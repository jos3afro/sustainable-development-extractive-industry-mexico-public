* Run config.do first to set path globals
do "../config.do"

clear all

use NDVI

set scheme tab2
gen date = ym(year, month)
format date  %tm

gen cvegeo = real(CVEGEO)
drop CVEGEO
order cvegeo CVE_ENT date year month
//For some fucking reason I have duplicates

collapse (first) year month NDVI_sum NDVI_mean NDVI_median, by( cvegeo date)
gen quarter = 1 if month==1
replace quarter = 2 if month==3
replace quarter = 3 if month==6
replace quarter = 4 if month==9
gen date2 = yq(year, quarter)
format date2  %tq

/*
//This chunk takes like 5h to run
foreach i in 5  10 15 25 50 75 {
		preserve 
		merge m:m cvegeo using  neighbors`i'
		drop if _merge==2
		//We make treatments to start in january
		
		local timelag 0
		replace start_year1 = 0 if start_year1==.
		replace discovery = 0 if discovery == .
		gen treat_discovery = yq(discovery, 1)
		gen treat_start = yq(start_year1, 1)
		format treat_discovery treat_start  %tq
		
		global controls 
		
		csdid NDVI_mean $controls , ivar(cvegeo) time(date2) gvar(treat_start)  method(dripw)   //Note that the command has cluster erros at the ivar level 
		estat event,  estore(cs)
		event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on `x'") ///
		title("NDVI_mean for start of operation at `i'") ) stub_lag(Tp#) stub_lead(Tm#) together	
		graph export "$results\Environment\NDVI\startdid`i'.png", as(png) name("Graph") replace

		csdid NDVI_mean $controls, ivar(cvegeo) time(date2) gvar(treat_discovery)  method(dripw)
		estat event,  estore(cs)
		event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on `x'") ///
		title("NDVI_mean for discovery   at `i'") ) stub_lag(Tp#) stub_lead(Tm#) together	
		graph export "$results\Environment\NDVI\discoverydid`i'.png", as(png) name("Graph") replace
		
		restore
}
*/

//Baseline 

preserve
collapse (mean)   NDVI_sum NDVI_mean NDVI_median , by( cvegeo year)
merge m:m cvegeo using  neighbors5
drop if _merge==2
local timelag 0
drop _merge
merge m:1 cvegeo using Mun20,
replace coast = 0 if coast==.

replace start_year1 = 0 if start_year1==.
rename start_year1 treat_start
replace discovery = 0 if discovery == .
rename discovery treat_discovery
**BASE line only municipalities that have mining
replace treat_start = 0 if cvegeo!= mun_location
replace treat_discovery = 0 if cvegeo!= mun_location


global controls disttodf coast
csdid NDVI_mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
estimate store ndvi_event

csdid NDVI_mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
estimate store ndvi_group
estat all

event_plot ndvi_event ,  default_look stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on NDVI") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	   graph export "$results\Environment\NDVI\baseNDVI.png", as(png) name("Graph") replace

restore 
esttab ndvi_group , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab ndvi_event , se tex  star(* 0.10 ** 0.05 *** 0.01)


//For ROBUSTNESS BUFFERS 

foreach i in 5 10 15 25 50 75 {
		preserve  
		qui collapse (mean)   NDVI_sum NDVI_mean NDVI_median , by( cvegeo year)
		qui merge m:m cvegeo using  neighbors`i'
		qui drop if _merge==2
		//We make treatments to start in january
		
		local timelag 0
		qui replace start_year1 = 0 if start_year1==.
		qui rename start_year1 treat_start
		qui replace discovery = 0 if discovery == .
		qui rename discovery treat_discovery
		
		global controls 
		
		csdid NDVI_mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
		estimate store ndvi_event`i'

		csdid NDVI_mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
		estimate store ndvi_group`i'
		estat all 
		
		event_plot ndvi_event`i', stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on NDVI") xlabel( , nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

		graph export "$results\Environment\NDVI\robBUFFER`i'.png", as(png) name("Graph") replace

		restore
}

//Making the graph with the results 

event_plot ndvi_event5 ndvi_event10 ndvi_event15 ndvi_event25, stub_lag(Tp#) stub_lead(Tm#)  plottype(scatter) ciplottype(rcap)  together ///
			perturb(-0.325(0.13)0.325) trimlead(2) trimlag(18) noautolegend ///
			graph_opt(xlabel(-2(6)18) xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8)) graphregion(color(white)) bgcolor(white) ylabel(, angle(horizontal)) ///
			xtitle("Years since the event") ytitle("Average causal effect on NDVI") ///
			legend(order(1 "5 km" 3 "10 km " 5 "15 km" 7 "25 km") rows(1) region(style(none)))) 

graph export "$results\Environment\NDVI\robBUFFER.png", as(png) name("Graph") replace

//For discovery

//Baseline 

preserve
qui collapse (mean)   NDVI_sum NDVI_mean NDVI_median , by( cvegeo year)
qui merge m:m cvegeo using  neighbors5
qui drop if _merge==2
local timelag 0
replace start_year1 = 0 if start_year1==.
rename start_year1 treat_start
replace discovery = 0 if discovery == .
rename discovery treat_discovery
**BASE line only municipalities that have mining
replace treat_start = 0 if cvegeo!= mun_location
replace treat_discovery = 0 if cvegeo!= mun_location
//drop if treat_discovery!=0 & treat_start==0 //variation in which we omit those municipalities that do not have operating mine


global controls 
csdid NDVI_mean $controls , ivar(cvegeo)  time(year) gvar(treat_discovery)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
estimate store ndvi_disevent

csdid NDVI_mean $controls , ivar(cvegeo)  time(year) gvar(treat_discovery)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
estimate store ndvi_disgroup
estat all

event_plot ndvi_disevent ,   stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on NDVI") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	   graph export "$results\Environment\NDVI\discoveryNDVI.png", as(png) name("Graph") replace

restore 
esttab ndvi_disgroup , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab ndvi_disevent , se tex  star(* 0.10 ** 0.05 *** 0.01)


event_plot ndvi_disevent ,   stub_lag(Tp#) stub_lead(Tm#) together trimlead(10) ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on NDVI") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	   graph export "$results\Environment\NDVI\discoveryNDVItrim.png", as(png) name("Graph") replace

//For ROBUSTNESS chaise martin 
preserve 
collapse (mean)   NDVI_sum NDVI_mean NDVI_median , by( cvegeo year)
merge m:m cvegeo using  neighbors5
drop if _merge==2

		
gen treat_discovery = 1 if discovery <= year
replace treat_discovery = 0 if  treat_discovery==.
		
gen treat_start = 1 if start_year1 <= year
replace treat_start = 0 if  treat_start==.
		
replace treat_start = 0 if cvegeo!= mun_location
replace treat_discovery = 0 if cvegeo!= mun_location

global controls 
				
did_multiplegt NDVI_mean cvegeo year treat_start , robust_dynamic cluster(cvegeo) breps(100) dynamic(18) placebo(10) trends_lin(cvegeo) seed(0510) ///
		 controls( $controls  )  

di 		"effect_average  & "     e(effect_average)  " & se & " e(se_effect_average) " &  t_stat  & "   e(effect_average)/e(se_effect_average)  " &  p &  "   2*normal(-abs(e(effect_average)/e(se_effect_average) )) " \\"
		 
forvalues i = 0/18 {
	scalar t_stat = e(effect_`i')/e(se_effect_`i')
	scalar p_val = 2*normal(-abs(t_stat))
	di "effect_`i'  & "     e(effect_`i')  " & se & " e(se_effect_`i') " &  t_stat & "   t_stat  " &  p & "   p_val " \\"
}
forvalues i = 0/10 {
	scalar t_stat = e(placebo_`i')/e(se_placebo_`i')
	scalar p_val = 2*normal(-abs(t_stat))
	di "placebo_`i'  & "     e(placebo_`i')  " & se & " e(se_placebo_`i') " &  t_stat & "   t_stat  " &  p & "   p_val " \\"
}

event_plot e(estimates)#e(variances), together stub_lag(Effect_#) stub_lead(Placebo_#) ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on NDVI") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

graph export "$results\Environment\NDVI\robCHAISE2.png", as(png) name("Graph") replace	   

restore

////FOR DISCUSSION BASED ON PARTICULAR SIZE OR TYPE OF MINE
preserve
qui collapse (mean)   NDVI_sum NDVI_mean NDVI_median , by( cvegeo year)
merge m:m cvegeo using  neighborsROB
drop if _merge==2
//We further remake start year and discovery so that it is in decades 

foreach x in giant major moderate precious etm {
	 qui gen filter_`x' = start_`x' if start_`x'<= start_year1 | start_year1==.
	 qui gen excluded_`x'= 1 if start_year1!=.
	 qui replace excluded_`x'= 0 if filter_`x' !=.
	 qui replace excluded_`x' = 0 if excluded_`x'==.
	
	qui gen treat_start = filter_`x'
	qui replace treat_start= 0 if  treat_start==.
	qui replace treat_start = 0 if cvegeo!= mun_location

	global controls 
	csdid NDVI_mean $controls if excluded_`x'==0, ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
	estimate store ndvi`x'_event 

	csdid NDVI_mean $controls if excluded_`x'==0, ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
	estimate store ndvi`x'_group
	estat all

	event_plot ndvi`x'_event  ,   stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on NDVI") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	   graph export "$results\Environment\NDVI\NDVI`x'.png", as(png) name("Graph") replace

 
	esttab ndvi`x'_event using ndvi`x'_event.tex , se tex  star(* 0.10 ** 0.05 *** 0.01)
	esttab ndvi`x'_group using ndvi`x'_group.tex , se tex  star(* 0.10 ** 0.05 *** 0.01)

	drop treat_start
} 

/*
TO GRAPH PARALLEL TRENDS WITHOUT ANYTHING
preserve
drop if treat_start!=0 & treat_start<2000
separate NDVI_mean, by( treat_start)
collapse(mean) NDVI*, by( treat_start year)
graph twoway line NDVI_mean0 NDVI_mean2005 NDVI_mean2002 NDVI_mean2010 year, sort
restore

*/



/* THIS CHUNK WILL BE USED EVENTUALLY FOR DISCOVERY RESULTS D:
			
		csdid NDVI_mean $controls, ivar(cvegeo) time(year) gvar(treat_discovery)  method(dripw) wboot(reps(1000) rseed(0510)) noyet 
		estat all
		estat event,  estore(cs)
		event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on `x'") ///
		title("NDVI_mean for discovery   at `i'") ) stub_lag(Tp#) stub_lead(Tm#) together	
		graph export "$results\Environment\NDVI\discoverydid`i'.png", as(png) name("Graph") replace
		
		restore

		*/
/*
FOR STAGGER DID of Chaisemartin and D'Haultfœuille
*/
foreach i in 5 { //10 15  25  50 75 {
		preserve 
		collapse (mean)   NDVI_sum NDVI_mean NDVI_median , by( cvegeo year)
		merge m:m cvegeo using  neighbors`i'
		drop if _merge==2

		
		gen treat_discovery = 1 if discovery <= year
		replace treat_discovery = 0 if  treat_discovery==.
		
		gen treat_start = 1 if start_year1 <= year
		replace treat_start = 0 if  treat_start==.
		
		**A test for only municipalities that have mining
		replace treat_start = 0 if cvegeo!= mun_location
		replace treat_discovery = 0 if cvegeo!= mun_location

		global controls 
				
		did_multiplegt NDVI_mean cvegeo year treat_start , robust_dynamic cluster(cvegeo) breps(50) dynamic(10) placebo(10) ///
		trends_lin(cvegeo) controls( $controls  )  
			
		event_plot e(estimates)#e(variances), default_look ///
		graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
		title("NDVI Start of mine at `i'") ) stub_lag(Effect_#) stub_lead(Placebo_#) together
		graph export "$results\Environment\NDVI\chaise_startdid`i'.png", as(png) name("Graph") replace

		did_multiplegt NDVI_mean cvegeo year treat_discovery , robust_dynamic cluster(cvegeo) breps(50) dynamic(10) placebo(10) ///
		trends_lin(cvegeo) controls( $controls  )
			
		event_plot e(estimates)#e(variances), default_look ///
		graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
		title("NDVI discovery at `i'")) stub_lag(Effect_#) stub_lead(Placebo_#) together
		graph export "$results\Environment\NDVI\chaise_discoverydid`i'.png", as(png) name("Graph") replace
		
		restore
}

/************************************************************************************************

FOR THE RINGS,  ndvi
*************************************************************************************************/


//For yearly
foreach i in 25 50  {
		preserve  
		collapse (mean)   NDVI_sum NDVI_mean NDVI_median , by( cvegeo year)
		merge m:m cvegeo using  ring`i'
		drop if _merge==2
		//We make treatments to start in january
		
		local timelag 0
		replace start_year1 = 0 if start_year1==.
		rename start_year1 treat_start
		replace discovery = 0 if discovery == .
		rename discovery treat_discovery
		
		**A test for only municipalities that have mining OR to exclude the origin mun
		replace treat_start = 0 if cvegeo== mun_location
		replace treat_discovery = 0 if cvegeo== mun_location
		
		global controls 
		
		csdid NDVI_mean $controls , ivar(cvegeo) time(year) gvar(treat_start)  method(dripw)  wboot(reps(1000) rseed(0510)) noyet  //Note that the command has cluster erros at the ivar level 
		estat all
		estat event,  estore(cs)
		event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on `x'") ///
		title("NDVI_mean for start of operation at `i'") ) stub_lag(Tp#) stub_lead(Tm#) together	
		graph export "$results\Environment\NDVI\startdid`i'ring.png", as(png) name("Graph") replace

		csdid NDVI_mean $controls, ivar(cvegeo) time(year) gvar(treat_discovery)  method(dripw)
		estat all
		estat event,  estore(cs)
		event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on `x'") ///
		title("NDVI_mean for discovery   at `i'") ) stub_lag(Tp#) stub_lead(Tm#) together	
		graph export "$results\Environment\NDVI\discoverydid`i'ring.png", as(png) name("Graph") replace
		
		restore
}

/*
FOR STAGGER DID of Chaisemartin and D'Haultfœuille
*/
foreach i in 25 50 {
		preserve 
		collapse (mean)   NDVI_sum NDVI_mean NDVI_median , by( cvegeo year)
		merge m:m cvegeo using  ring`i'
		drop if _merge==2

		
		gen treat_discovery = 1 if discovery <= year
		replace treat_discovery = 0 if  treat_discovery==.
		
		gen treat_start = 1 if start_year1 <= year
		replace treat_start = 0 if  treat_start==.
		
		**A test for only municipalities that have mining
		replace treat_start = 0 if cvegeo== mun_location
		replace treat_discovery = 0 if cvegeo== mun_location

		global controls 
				
		did_multiplegt NDVI_mean cvegeo year treat_start , robust_dynamic cluster(cvegeo) breps(50) dynamic(10) placebo(10) ///
		trends_lin(cvegeo) controls( $controls  )  
			
		event_plot e(estimates)#e(variances), default_look ///
		graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
		title("NDVI Start of mine at `i'") ) stub_lag(Effect_#) stub_lead(Placebo_#) together
		graph export "$results\Environment\NDVI\chaise_startdid`i'ring.png", as(png) name("Graph") replace

		did_multiplegt NDVI_mean cvegeo year treat_discovery , robust_dynamic cluster(cvegeo) breps(50) dynamic(10) placebo(10) ///
		trends_lin(cvegeo) controls( $controls  )
			
		event_plot e(estimates)#e(variances), default_look ///
		graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
		title("NDVI discovery at `i'")) stub_lag(Effect_#) stub_lead(Placebo_#) together
		graph export "$results\Environment\NDVI\chaise_discoverydid`i'ring.png", as(png) name("Graph") replace
		
		restore
}



//For yearly
foreach i in 25 50 {
		preserve  

		merge m:m cvegeo using  ring`i'
		drop if _merge==2
		//We make treatments to start in january
		
		local timelag 0
		replace start_year1 = 0 if start_year1==.
		rename start_year1 treat_start
		replace discovery = 0 if discovery == .
		rename discovery treat_discovery
		
		**A test for only municipalities that have mining
		replace treat_start = 0 if cvegeo== mun_location
		replace treat_discovery = 0 if cvegeo== mun_location
		
		global controls 
		
		capture csdid mean_xco2 $controls , ivar(cvegeo) time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510))  //Note that the command has cluster erros at the ivar level 
		estat all
		capture estat event,  estore(cs)
		capture event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on `x'") ///
		title("Effect of Start on CO2 concentration at `i'") ) stub_lag(Tp#) stub_lead(Tm#) together	
		capture graph export "$results\Environment\CO2\startdid`i'ring.png", as(png) name("Graph") replace

		capture csdid mean_xco2 $controls, ivar(cvegeo) time(year) gvar(treat_discovery)  method(dripw) wboot(reps(1000) rseed(0510))
		estat all
		capture estat event,  estore(cs)
		capture event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on `x'") ///
		title("Effect of Discovery on CO2 concentration at `i'") ) stub_lag(Tp#) stub_lead(Tm#) together	
		capture graph export "$results\Environment\CO2\discoverydid`i'ring.png", as(png) name("Graph") replace
		
		restore
}

foreach i in  25  50  {
		preserve 
		merge m:m cvegeo using  ring`i'
		drop if _merge==2

		
		gen treat_discovery = 1 if discovery <= year
		replace treat_discovery = 0 if  treat_discovery==.
		
		gen treat_start = 1 if start_year1 <= year
		replace treat_start = 0 if  treat_start==.
		
		**A test for only municipalities that have mining
		replace treat_start = 0 if cvegeo== mun_location
		replace treat_discovery = 0 if cvegeo== mun_location

		global controls 
				
		capture did_multiplegt mean_xco2 cvegeo year treat_start , robust_dynamic cluster(cvegeo) breps(50) dynamic(4) placebo(3) ///
		trends_lin(cvegeo) controls( $controls  )  
			
		capture event_plot e(estimates)#e(variances), default_look ///
		graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
		title("Effect of Start on CO2 concentration at `i'") ) stub_lag(Effect_#) stub_lead(Placebo_#) together
		capture graph export "$results\Environment\CO2\chaise_startdid`i'ring.png", as(png) name("Graph") replace

		graph drop _all 
		capture did_multiplegt mean_xco2 cvegeo year treat_discovery , robust_dynamic cluster(cvegeo) breps(50) dynamic(2) placebo(2) ///
		trends_lin(cvegeo) controls( $controls  )
			
		capture event_plot e(estimates)#e(variances), default_look ///
		graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
		title("Effect of Discovery on CO2 concentration at `i'")) stub_lag(Effect_#) stub_lead(Placebo_#) together
		capture graph export "$results\Environment\CO2\chaise_discoverydid`i'ring.png", as(png) name("Graph") replace
		
		restore
}

*/

**** FOR NEW CO2  ---> NASA data


set scheme tab2
clear
import delimited "$core\CO2data.csv", 

**To make an evolution of CO2 graph
/*
preserve
sort year
collapse co2sum co2mean co2median , by(year)
line co2sum year, ytitle("CO2 Emissions") xtitle("Year")
graph export "$results\Descriptive Statistics\CO2evolution.png", as(png) name("Graph") replace
restore
*/
//For regression

//Fetching some controls 
sort cvegeo year
merge m:1 cvegeo using Mun20 , nogen
drop sexo edad hlengua hespanol escoacum horas cve_ocup sit_trab vacacion servmed totpers ingresos wealth_index wealth_index2 gini theis ratio90_10 mining tipohog_1 tipohog_2 tipohog_3 tipohog_4 tipohog_5 tipohog_6 sit_trab_1 sit_trab_2 sit_trab_3 sit_trab_4 sit_trab_5 index_score index_score2 

preserve

use mex_covariate, clear
tempfile f
sort cvegeo year
collapse area agro_land human_land income average, by(cvegeo)
save `f'
restore
merge m:1 cvegeo using `f', nogen
foreach x in coast capital dfmexico {
	replace `x' = 0 if `x'==.
}


***For baseline
preserve
merge m:m cvegeo using  neighbors5

		
replace start_year1 = 0 if start_year1==.
rename start_year1 treat_start
replace discovery = 0 if discovery == .
rename discovery treat_discovery
**BASE line only municipalities that have mining
replace treat_start = 0 if cvegeo!= mun_location
replace treat_discovery = 0 if cvegeo!= mun_location


global controls coast capital dfmexico disttodf agro_land human_land

csdid co2mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
estimate store co2_event

csdid co2mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
estimate store co2_group
estat all

esttab co2_event using CO2nasa_event.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace
esttab co2_group using CO2nasa_group.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace

event_plot co2_event ,   stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on CO2 Emissions") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

graph export "$results\Environment\CO2\baseCO2nasa.png", as(png) name("Graph") replace


***** For discovery --> nothing is significant

csdid co2mean $controls , ivar(cvegeo)  time(year) gvar(treat_discovery)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
estimate store co2dis_event

csdid co2mean $controls , ivar(cvegeo)  time(year) gvar(treat_discovery)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
estimate store co2dis_group
estat all


event_plot co2dis_event ,   stub_lag(Tp#) stub_lead(Tm#) together trimlead(10) ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on CO2 Emissions") xlabel(-10(5)20, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

graph export "$results\Environment\CO2\discoveryCO2nasa.png", as(png) name("Graph") replace




****For robustness buffer --> bigger effect in 50km and 75km which is not really consistent with the rest of the results.... FUCK ME 
restore 
foreach i in 5 10 15 25 50 75 {
		preserve  
		qui merge m:m cvegeo using  neighbors`i'
		qui drop if _merge==2
		//We make treatments to start in january
		
		qui replace start_year1 = 0 if start_year1==.
		qui rename start_year1 treat_start
		qui replace discovery = 0 if discovery == .
		qui rename discovery treat_discovery
		
		global controls coast capital dfmexico disttodf agro_land human_land
		
		csdid co2mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
		estimate store co2_event`i'

		csdid co2mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
		estimate store co2_group`i'
		estat all 
		
		event_plot co2_event`i', stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on CO2 Emissions") xlabel( , nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

		graph export "$results\Environment\CO2\robBUFFER`i'.png", as(png) name("Graph") replace

		restore
}

event_plot co2_event5 co2_event10 co2_event25 co2_event50 co2_event75, stub_lag(Tp#) stub_lead(Tm#)  plottype(scatter) ciplottype(rcap)  together ///
			perturb(-0.325(0.13)0.325) trimlead(10) trimlag() noautolegend ///
			graph_opt(xlabel(-10(10)20) xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8)) graphregion(color(white)) bgcolor(white) ylabel(, angle(horizontal)) ///
			xtitle("Years since the event") ytitle("Average causal effect on Income") ///
			legend(order(1 "5km" 3 "10km" 5 "25km" 7 "50km" 9 "75km") rows(1) region(style(none)))) ///
			lag_opt1( color("70 111 157")) lag_ci_opt1(color("70 111 157")) ///
			lag_opt2( color("56 150 196")) lag_ci_opt2(color("56 150 196")) ///
			lag_opt3( color("145 179 215")) lag_ci_opt3(color("145 179 215")) ///
			lag_opt4( color("254 181 162")) lag_ci_opt4(color("254 181 162")) ///
			lag_opt5( color("237 68 74")) lag_ci_opt5(color("237 68 74"))	   
	   
graph export "$results\Environment\CO2\robBUFFERS.png", as(png) name("Graph") replace	   

***With the ring cest encore pire !!!! 
import delimited "$core\CO2ring_dataWithMinex.csv"
encode idstata, gen(idstata2)
gen start_treat = start_year1
replace start_treat = 0 if start_treat==.
replace start_treat=0 if ring==2 | ring==3
global controls exploration feasibility closed stalled other_status operating
csdid co2mean $controls , ivar( idstata2 )  time(year) gvar( start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
event_plot  ,  default_look stub_lag(Tp#) stub_lead(Tm#) together
replace start_treat = . if ringid==2
csdid co2mean $controls , ivar( idstata2 )  time(year) gvar( start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
event_plot  ,  default_look stub_lag(Tp#) stub_lead(Tm#) together


	   