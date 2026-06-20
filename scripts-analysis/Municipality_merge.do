* Run config.do first to set path globals
do "../config.do"

**# Bookmark #1   Set up
clear all
set scheme tab2
use Mun90

foreach x in Mun00 Mun10 Mun20 {
	append using `x'
}

foreach x in sexo edad hlengua escoacum horas {
	rename  `x' `x'_head
}

//We add mexico covariates and school variables
sort cvegeo year
merge 1:1 cvegeo year using school_mexico, nogen

//We add other info on mexico as income of the gov
merge 1:1 cvegeo year using mex_covariate, 
drop if _merge==2
drop _merge
rename income income_gov
rename average av_inc_gov
label var av_inc_gov "Average decenial income of the goverment"

//We add population 
merge 1:1 cvegeo year using pop_mexico, 
drop if _merge==2
drop _merge

//Lets deflate the values (base is 2018) #source  https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarCuadro&idCuadro=CP154&locale=es

foreach x in ingresos income_gov av_inc_gov {
	replace `x' = `x'/(9.638214000000/100) if year==1990
	replace `x' = `x'/(48.307671000000/100) if year==2000
	replace `x' = `x'/(74.930954000000/100) if year==2010
	replace `x' = `x'/(109.271000000000/100) if year==2020
}

replace ingresos = ingresos /1000 if year ==1990

replace ingresos = ingresos /10 if year ==1990 | year==2000 //otherwise it does not make sense.... I think there was some rebalancing in the currency


//We balance the panel (and we lose 159 obs)
sort cvegeo year
by cvegeo: egen nomissing = count(y) if (year==1990 | year==2000 | year==2010| year==2020)
keep if nomissing == 4
drop nomissing
table year



// We transform income and goverment income to log 

gen l_inc = ln(ingresos)
gen gr_inc = l_inc - l_inc[_n-1] if cvegeo == cvegeo[_n-1]
gen l_gov = ln(income_gov)
gen gr_gov = l_gov - l_gov[_n-1] if cvegeo == cvegeo[_n-1]
gen gr_school = (enroll_rate - enroll_rate[_n-1])/enroll_rate[_n-1] if cvegeo == cvegeo[_n-1]
label var gr_school "Growth rate of school enrollment rate"
gen gr_gini = (gini - gini[_n-1])/gini[_n-1] if cvegeo == cvegeo[_n-1]

xtset cvegeo year



**#  Regressions baseline for municipality as treated

/*
BASE STAGGER FOR SANTANA CALLAWAY 
*/
preserve 
merge m:m cvegeo using  neighbors5
drop if _merge==2
		//We further remake start year and discovery so that it is in decades 
local timelag 0
gen start_treat = 1980 if start_year1<=1980 - `timelag' & start_year1!=.
replace start_treat = 1990 if start_year1<=1990 - `timelag' & start_year1!=. & start_treat==.
replace start_treat = 2000 if start_year1<=2000 - `timelag' & start_year1!=. & start_treat==.
replace start_treat = 2010 if start_year1<=2010 - `timelag' & start_year1!=. & start_treat==.
replace start_treat = 2020 if start_year1<=2020 - `timelag' & start_year1!=. & start_treat==.
replace start_treat = 0 if  start_treat==.

gen discovery_treat = 1980 if discovery<=1980 - `timelag' & discovery!=.
replace discovery_treat = 1990 if discovery<=1990 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 2000 if discovery<=2000 - `timelag'  & discovery!=. & discovery_treat==.
replace discovery_treat = 2010 if discovery<=2010 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 2020 if discovery<=2020 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 0 if  discovery_treat==.
replace start_year1 = 0 if start_year1==.
replace discovery = 0 if discovery == .
		
replace start_treat = 0 if cvegeo!= mun_location
replace discovery_treat = 0 if cvegeo!= mun_location

global controls population sexo_head edad_head hlengua_head escoacum_head agro_land

foreach x in  enroll_rate escoacum gini theis {
	csdid `x' $controls , ivar(cvegeo) time(year) gvar(start_treat)  method(dripw)  cluster() wboot(reps(1000) rseed(0510)) noyet agg(event) 
	estimate store event_`x'
	
	csdid `x' $controls , ivar(cvegeo) time(year) gvar(start_treat)  method(dripw)  cluster() wboot(reps(1000) rseed(0510)) noyet agg(group) 
	estimate store group_`x'
	
	event_plot event_`x', default_look graph_opt(xtitle("Periods since the event") ytitle("Average effect of discovery on `x'") ///
			title("Effect on `x'") xlabel() ) stub_lag(Tm#) stub_lead(Tp#) together	
	graph export "$results\Call_Santana\base`x'.png", as(png) name("Graph") replace
}

esttab event* , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab group* , se tex  star(* 0.10 ** 0.05 *** 0.01)



/*
FOR STAGGER DID of Chaisemartin and D'Haultfœuille
*/

		preserve 
		merge m:m cvegeo using  neighbors5
		drop if _merge==2
		//We further remake start year and discovery so that it is in decades 
		
		gen treat = mining1990
		gen treat_dis = discovery1990
		foreach n in 2000 2010 2020 {
			replace treat = mining`n' if year == `n'
			replace treat_dis = discovery`n' if year == `n'
		}
		replace treat = 0 if treat == .
		replace treat_dis = 0 if treat_dis == .
		
		replace treat = 0 if  cvegeo!= mun_location
		replace treat_dis = 0 if  cvegeo!= mun_location
		
		**One of the tests
		***replace treat = 1 if treat!=0
		***replace treat_dis = 1 if treat!=0		
		
		global controls population sexo_head edad_head hlengua_head escoacum_head agro_land
		
		foreach x in l_inc gr_inc gini enroll_rate l_gov gr_gov gr_school gr_gini escoacum {
			
			did_multiplegt gini cvegeo year treat , robust_dynamic cluster(cvegeo) breps(50) dynamic(2) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )  
			
			matrix betas = e(estimates) // storing the estimates for later
			matrix varianc = e(variances)
			
			event_plot betas#varianc,  plottype(scatter) stub_lag(Effect_#) stub_lead(Placebo_#) ///
			graph_opt(xtitle("Periods since the event") ytitle("Average causal effect") ///
			title("did Start of mine `x' at `i'") xlabel(-1(1)2) /// 
			xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8)))
			graph export "$results\Chaise_Haul\baseline`x'.png", as(png) name("Graph") replace

			did_multiplegt `x' cvegeo year treat_dis , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )
			
			**event_plot e(estimates)#e(variances), default_look ///
			**graph_opt(xtitle("Periods since the event") ytitle("Average causal effect") ///
			**title("did discovery `x' at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Chaise_Haul\disbaseline`x'.png", as(png) name("Graph") replace
		}
		restore
}



**#  Regressions based on buffers

/*
FOR STAGGER DID of Callaway and Sant'Anna
*/
foreach i in 5 10 15 20 25 30 50 75 {
		preserve 
		merge m:m cvegeo using  neighbors`i'
		drop if _merge==2
		//We further remake start year and discovery so that it is in decades 
		local timelag 0
		gen start_treat = 1980 if start_year1<=1980 - `timelag' & start_year1!=.
		replace start_treat = 1990 if start_year1<=1990 - `timelag' & start_year1!=. & start_treat==.
		replace start_treat = 2000 if start_year1<=2000 - `timelag' & start_year1!=. & start_treat==.
		replace start_treat = 2010 if start_year1<=2010 - `timelag' & start_year1!=. & start_treat==.
		replace start_treat = 2020 if start_year1<=2020 - `timelag' & start_year1!=. & start_treat==.
		replace start_treat = 0 if  start_treat==.

		gen discovery_treat = 1980 if discovery<=1980 - `timelag' & discovery!=.
		replace discovery_treat = 1990 if discovery<=1990 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 2000 if discovery<=2000 - `timelag'  & discovery!=. & discovery_treat==.
		replace discovery_treat = 2010 if discovery<=2010 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 2020 if discovery<=2020 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 0 if  discovery_treat==.
		replace start_year1 = 0 if start_year1==.
		replace discovery = 0 if discovery == .
		
		global controls population sexo_head edad_head hlengua_head escoacum_head agro_land
		
		foreach x in l_inc gr_inc gini enroll_rate l_gov gr_gov gr_school gr_gini escoacum {
			csdid `x' $controls , ivar(cvegeo) time(year) gvar(start_treat)  method(dripw)  cluster() wboot(reps(1000) rseed(0510)) noyet //Note that the command has cluster erros at the ivar level 
			estat all , estore(start`x'`i')
			estat event, estore(cs)
			event_plot cs, default_look graph_opt(xtitle("Periods since the event") ytitle("Average effect  on `x'") ///
			title("Effect of start on `x' at `i'") xlabel() ) stub_lag(Tm#) stub_lead(Tp#) together	
			graph export "$results\Call_Santana\startdid`x'`i'.png", as(png) name("Graph") replace

			csdid `x' $controls, ivar(cvegeo) time(year) gvar(discovery_treat)  method(dripw) cluster() wboot(reps(1000) rseed(0510)) noyet
			estat all , estore(dis`x'`i')
			estat event,  estore(cs)
			event_plot cs, default_look graph_opt(xtitle("Periods since the event") ytitle("Average effect of discovery on `x'") ///
			title("Effect of discovery `x' at `i'") xlabel() ) stub_lag(Tm#) stub_lead(Tp#) together	
			graph export "$results\Call_Santana\discoverydid`x'`i'.png", as(png) name("Graph") replace
		}
		restore
}




/*
FOR STAGGER DID of Chaisemartin and D'Haultfœuille
*/
foreach i in 5 10 15 20 25 30 50 75 {
		preserve 
		merge m:m cvegeo using  neighbors`i'
		drop if _merge==2
		//We further remake start year and discovery so that it is in decades 
		
		gen treat = mining1990
		gen treat_dis = discovery1990
		foreach n in 2000 2010 2020 {
			replace treat = mining`n' if year == `n'
			replace treat_dis = discovery`n' if year == `n'
		}
		replace treat = 0 if treat == .
		replace treat_dis = 0 if treat_dis == .
		
		**One of the tests
		***replace treat = 1 if treat!=0
		***replace treat_dis = 1 if treat!=0
		
		
		
		global controls population sexo_head edad_head hlengua_head escoacum_head agro_land
		
		foreach x in l_inc gr_inc gini enroll_rate l_gov gr_gov gr_school gr_gini escoacum {
			did_multiplegt `x' cvegeo year treat , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )  
			
			**event_plot e(estimates)#e(variances), default_look ///
			**graph_opt(xtitle("Periods since the event") ytitle("Average causal effect") ///
			**title("did Start of mine `x' at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Chaise_Haul\startdid`x'`i'.png", as(png) name("Graph") replace

			did_multiplegt `x' cvegeo year treat_dis , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )
			
			**event_plot e(estimates)#e(variances), default_look ///
			**graph_opt(xtitle("Periods since the event") ytitle("Average causal effect") ///
			**title("did discovery `x' at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Chaise_Haul\discoverydid`x'`i'.png", as(png) name("Graph") replace
		}
		restore
}

**# Regressions based on rings

/* ***********************************

FOR RINGS 

**************************************/

foreach i in 25 50 {
		preserve 
		merge m:m cvegeo using  ring`i'
		drop if _merge==2
		//We further remake start year and discovery so that it is in decades 
		local timelag 0
		gen start_treat = 1980 if start_year1<=1980 - `timelag' & start_year1!=.
		replace start_treat = 1990 if start_year1<=1990 - `timelag' & start_year1!=. & start_treat==.
		replace start_treat = 2000 if start_year1<=2000 - `timelag' & start_year1!=. & start_treat==.
		replace start_treat = 2010 if start_year1<=2010 - `timelag' & start_year1!=. & start_treat==.
		replace start_treat = 2020 if start_year1<=2020 - `timelag' & start_year1!=. & start_treat==.
		replace start_treat = 0 if  start_treat==.

		gen discovery_treat = 1980 if discovery<=1980 - `timelag' & discovery!=.
		replace discovery_treat = 1990 if discovery<=1990 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 2000 if discovery<=2000 - `timelag'  & discovery!=. & discovery_treat==.
		replace discovery_treat = 2010 if discovery<=2010 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 2020 if discovery<=2020 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 0 if  discovery_treat==.
		replace start_year1 = 0 if start_year1==.
		replace discovery = 0 if discovery == .
		
		global controls population sexo_head edad_head hlengua_head escoacum_head agro_land
		
		foreach x in l_inc gr_inc gini enroll_rate l_gov gr_gov gr_school gr_gini escoacum {
			csdid `x' $controls , ivar(cvegeo) time(year) gvar(start_treat)  method(dripw)  cluster() wboot(reps(1000) rseed(0510)) noyet //Note that the command has cluster erros at the ivar level 
			estat event, window() estore(cs)
			event_plot cs, default_look graph_opt(xtitle("Periods since the event") ytitle("Average effect  on `x'") ///
			title("Effect of start on `x' at `i'") xlabel() ) stub_lag(Tm#) stub_lead(Tp#) together	
			graph export "$results\Call_Santana\startdid`x'ring`i'.png", as(png) name("Graph") replace

			csdid `x' $controls, ivar(cvegeo) time(year) gvar(discovery_treat)  method(dripw) cluster() wboot(reps(1000) rseed(0510)) noyet
			estat event,  estore(cs)
			event_plot cs, default_look graph_opt(xtitle("Periods since the event") ytitle("Average effect of discovery on `x'") ///
			title("Effect of discovery `x' at `i'") xlabel() ) stub_lag(Tm#) stub_lead(Tp#) together	
			graph export "$results\Call_Santana\discoverydid`x'ring`i'.png", as(png) name("Graph") replace
		}
		restore
}



/*
FOR STAGGER DID of Chaisemartin and D'Haultfœuille
*/
foreach i in  25  50  {
		preserve 
		merge m:m cvegeo using  ring`i'
		drop if _merge==2
		//We further remake start year and discovery so that it is in decades 
		
		gen treat = mining1990
		gen treat_dis = discovery1990
		foreach n in 2000 2010 2020 {
			replace treat = mining`n' if year == `n'
			replace treat_dis = discovery`n' if year == `n'
		}
		replace treat = 0 if treat == .
		replace treat_dis = 0 if treat_dis == .
		
		**One of the tests
		***replace treat = 1 if treat!=0
		***replace treat_dis = 1 if treat!=0
		
		
		
		global controls population sexo_head edad_head hlengua_head escoacum_head agro_land
		
		foreach x in l_inc gr_inc gini enroll_rate l_gov gr_gov gr_school gr_gini escoacum {
			did_multiplegt `x' cvegeo year treat , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )  
			
			**event_plot e(estimates)#e(variances), default_look ///
			**graph_opt(xtitle("Periods since the event") ytitle("Average causal effect") ///
			**title("did Start of mine `x' at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Chaise_Haul\startdidring`x'`i'.png", as(png) name("Graph") replace

			did_multiplegt `x' cvegeo year treat_dis , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )
			
			**event_plot e(estimates)#e(variances), default_look ///
			**graph_opt(xtitle("Periods since the event") ytitle("Average causal effect") ///
			**title("did discovery `x' at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Chaise_Haul\discoverydidring`x'`i'.png", as(png) name("Graph") replace
		}
		restore
}



foreach i in 5 10 15 20 25 30 50 75 {
		preserve 
		merge m:m cvegeo using  neighbors`i'
		drop if _merge==2
		
		gen minex = 1 if no_mines!=.
		replace minex = 0 if minex==.
		replace minex =0 if start_year1<=1989  
		psmatch2 minex escoacum hlengua totpers coast disttodf if year==1990 , neighbor(5)
		**I need to pass the weights for the rest of years 
		replace _weight = _weight[_n-1] if cvegeo==cvegeo[_n-1] & _weight==.
		gen start_treat = 1980 if start_year1<=1980 & start_year1!=.
		replace start_treat = 1990 if start_year1<=1990 & start_year1!=. & start_treat==.
		replace start_treat = 2000 if start_year1<=2000 & start_year1!=. & start_treat==.
		replace start_treat = 2010 if start_year1<=2010 & start_year1!=. & start_treat==.
		replace start_treat = 2020 if start_year1<=2020 & start_year1!=. & start_treat==.
		replace start_treat = 0 if  start_treat==.
		
		gen discovery_treat = 1980 if discovery<=1980 & discovery!=.
		replace discovery_treat = 1990 if discovery<=1990 & discovery!=. & discovery_treat==.
		replace discovery_treat = 2000 if discovery<=2000 & discovery!=. & discovery_treat==.
		replace discovery_treat = 2010 if discovery<=2010 & discovery!=. & discovery_treat==.
		replace discovery_treat = 2020 if discovery<=2020 & discovery!=. & discovery_treat==.
		replace discovery_treat = 0 if  discovery_treat==.
		replace start_year1 = 0 if start_year1==.
		replace discovery = 0 if discovery == .
		global primary _copper _gold _graphite _ironore _lithium _manganese _molybdenum _silver _tungsten _zinc
		
		foreach x in $primary {
			rename primary_metal`x' pm`x'
		}
		
		global dummies size_giant size_major size_moderate contain_precious contain_etm contain_other operating exploration feasibility closed stalled other_status pm_copper pm_gold pm_graphite pm_ironore pm_lithium pm_manganese pm_molybdenum pm_silver pm_tungsten pm_zinc
		foreach x in $dummies {
			quietly replace `x' = `x'*1 if start_treat==year //To modify when using discovery or start 
			quietly replace `x' = 0 if start_treat>year
			quietly replace `x' = 0 if 	`x' ==.
		}
		
		global size size_giant size_major size_moderate
		global primary pm_copper pm_gold pm_graphite pm_ironore pm_lithium pm_manganese pm_molybdenum pm_silver pm_tungsten pm_zinc
		global status operating exploration feasibility closed stalled
		global controls sexo_head edad_head hlengua_head escoacum_head agro_land 
		
		foreach x in l_inc gr_inc gini enroll_rate l_gov escoacum {
			
				quietly reg `x'  $size   i.cve_ent i.year cve_ent#year if start_treat!=1980  [aweight= _weight ],  cluster( cve_ent )
				estimates store size`x'`i'
				
				quietly reg `x'  $primary   i.cve_ent i.year cve_ent#year if start_treat!=1980  [aweight= _weight ],  cluster( cve_ent )
				estimates store primary`x'`i'
				
				quietly reg `x'  $status   i.cve_ent i.year cve_ent#year if start_treat!=1980  [aweight= _weight ],  cluster( cve_ent )
				estimates store status`x'`i'
	
			}
		
		restore 
}

foreach x in l_inc gr_inc gini enroll_rate l_gov escoacum {

		coefplot size`x'5  size`x'10  size`x'15  size`x'20    , keep(size*)  xline(0) levels(95 90) title(Effect on `x' Reg-cluster start_) 
		graph export "$results\didFE\start_size`x'a.png", as(png) name("Graph") replace
		
		coefplot primary`x'5  primary`x'10  primary`x'15  primary`x'20  , keep(pm*)  xline(0) levels(95 90) title(Effect on `x' Reg-cluster start_) 
		graph export "$results\didFE\start_primary`x'a.png", as(png) name("Graph") replace
		
		coefplot status`x'5  status`x'10  status`x'15  status`x'20 , keep(operating exploration feasibility closed stalled)  xline(0) levels(95 90) title(Effect on `x' Reg-cluster start_) 
		graph export "$results\didFE\start_status`x'a.png", as(png) name("Graph") replace

		coefplot size`x'25  size`x'30  size`x'50  size`x'75  , keep(size*)  xline(0) levels(95 90) title(Effect on `x' Reg-cluster) 
		graph export "$results\didFE\start_size`x'b.png", as(png) name("Graph") replace
		
		coefplot primary`x'25  primary`x'30  primary`x'50  primary`x'75, keep(pm*)  xline(0) levels(95 90) title(Effect on `x' Reg-cluster) 
		graph export "$results\didFE\start_primary`x'b.png", as(png) name("Graph") replace
		
		coefplot status`x'25  status`x'30  status`x'50  status`x'75 , keep(operating exploration feasibility closed stalled)  xline(0) levels(95 90) title(Effect on `x' Reg-cluster start_) 
		graph export "$results\didFE\start_status`x'b.png", as(png) name("Graph") replace
}

*/