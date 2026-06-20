* Run config.do first to set path globals
do "../config.do"

clear all

cd "$core"
set scheme tab2
use Census90, clear

sort id_viv

foreach x in Census00 Census10 Census20 {
	append using `x', force
}

foreach x in sexo edad hlengua escoacum horas {
	rename  `x' `x'_head
}

replace ingresos = ingreso if year ==1990 | year==2000

foreach x in ingresos {
	replace `x' = `x'/(9.638214000000/100) if year==1990
	replace `x' = `x'/(48.307671000000/100) if year==2000
	replace `x' = `x'/(74.930954000000/100) if year==2010
	replace `x' = `x'/(109.271000000000/100) if year==2020
}
replace ingresos = ingresos /1000 if year ==1990

replace ingresos = ingresos /10 if year ==1990 | year==2000 //otherwise it does not make sense.... I think there was some rebalancing in the currency

gen l_inc = ln(ingresos)
sort cvegeo year

/*   ********************************************************************************************************************************
BASELINE 
* ********************************************************************************************************************************/ 
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

gen discovery_treat = 1980 if discovery<= 1980 - `timelag' & discovery!=.
replace discovery_treat = 1990 if discovery<=1990 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 2000 if discovery<=2000 - `timelag'  & discovery!=. & discovery_treat==.
replace discovery_treat = 2010 if discovery<=2010 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 2020 if discovery<=2020 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 0 if  discovery_treat==.
replace start_year1 = 0 if start_year1==.
replace discovery = 0 if discovery == .

replace start_treat = 0 if cvegeo!= mun_location
replace discovery = 0 if cvegeo!= mun_location

global controls  sexo_head edad_head hlengua_head escoacum_head 

csdid l_inc $controls , time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
estimate store base_event

csdid l_inc $controls , time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
estimate store base_group

event_plot base_event, stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on income") xlabel(-20(10)20 , nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

graph export "$results\Income\base.png", as(png) name("Graph") replace

esttab base_event , se tex 
	   
/*
Robustness buffers
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

		gen discovery_treat = 1980 if discovery<= 1980 - `timelag' & discovery!=.
		replace discovery_treat = 1990 if discovery<=1990 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 2000 if discovery<=2000 - `timelag'  & discovery!=. & discovery_treat==.
		replace discovery_treat = 2010 if discovery<=2010 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 2020 if discovery<=2020 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 0 if  discovery_treat==.
		replace start_year1 = 0 if start_year1==.
		replace discovery = 0 if discovery == .
		
		global controls  sexo_head edad_head hlengua_head escoacum_head 
		

			csdid l_inc $controls , time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
			estimate store event_`i'
			
			csdid l_inc $controls , time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
			estimate store group_`i'

			*event_plot base_event, stub_lag(Tp#) stub_lead(Tm#) together ///
			*	graph_opt(xtitle("Years since the event") ytitle("Average effect on income") xlabel(-20(10)20 , nogrid) ylabel(, angle(horizontal))  ///
			*	xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
			*graph export "$results\Income\robBUFFER`i'.png", as(png) name("Graph") replace
		restore
}

esttab group* using group_algo.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace
esttab event* using event_algo.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace


event_plot event_5 event_10 event_15 event_25 event_50 event_75, stub_lag(Tp#) stub_lead(Tm#)  plottype(scatter) ciplottype(rcap)  together ///
			perturb(-1.5(1)1.5) trimlead() trimlag() noautolegend ///
			graph_opt(xlabel(-20(10)20) xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8)) graphregion(color(white)) bgcolor(white) ylabel(, angle(horizontal)) ///
			xtitle("Years since the event") ytitle("Average causal effect on Income") ///
			legend(order(1 "5 km" 3 "10 km " 5 "15 km" 7 "25 km" 9 "50 km" 11 "75 km") rows(1) region(style(none)))) ///
			lag_opt1( color("70 111 157")) lag_ci_opt1(color("70 111 157")) ///
			lag_opt2( color("237 68 74")) lag_ci_opt2(color("237 68 74")) ///
			lag_opt3( color("145 179 215")) lag_ci_opt3(color("145 179 215")) ///
			lag_opt4( color("254 181 162")) lag_ci_opt4(color("254 181 162")) ///
			lag_opt5( color("56 150 196")) lag_ci_opt5(color("56 150 196")) ///
			lag_opt6( color("157 118 96")) lag_ci_opt6(color("157 118 96")) 

graph export "$results\Income\robBUFFER.png", as(png) name("Graph") replace

/*
Robustness  DISCOVERY 
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

gen discovery_treat = 1980 if discovery<= 1980 - `timelag' & discovery!=.
replace discovery_treat = 1990 if discovery<=1990 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 2000 if discovery<=2000 - `timelag'  & discovery!=. & discovery_treat==.
replace discovery_treat = 2010 if discovery<=2010 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 2020 if discovery<=2020 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 0 if  discovery_treat==.
replace start_year1 = 0 if start_year1==.
replace discovery_treat = 0 if discovery_treat == .

replace start_treat = 0 if cvegeo!= mun_location
replace discovery_treat = 0 if cvegeo!= mun_location


global controls  sexo_head edad_head hlengua_head escoacum_head 

csdid l_inc $controls , time(year) gvar(discovery_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
estimate store dis_event
			
csdid l_inc $controls , time(year) gvar(discovery_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
estimate store dis_group

esttab dis_event using group_discovery.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace
esttab dis_group using event_discovery.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace

event_plot dis_event, stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on income") xlabel(-20(10)20 , nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
graph export "$results\Income\robDiscovery.png", as(png) name("Graph") replace



/*
Robustness  ENTROPY BALANCE  
*/


//we create weights using entropy balance
ebalance treatment sexo_head edad_head escoacum_head  year, gen(weights)

csdid l_inc disttodf coast [iweight= weights ] , time(year) gvar(start_treat)  method(dripw )  noyet wboot(reps(1000) rseed(0510))  agg(event)
estimate store event_entropy

esttab event_entropy   se tex  star(* 0.10 ** 0.05 *** 0.01) replace

/*
Robustness  long term wealth
*/


foreach years in 1990 2000 2010 2020 {
	
	summarize index_score if year==`years' 
	scalar mean_income = r(mean)
	scalar sd_income = r(sd)

	generate index`years' = (index_score - mean_income) / sd_income if  year==`years'
}

gen index_z = index1990

foreach years in  2000 2010 2020 {
	replace index_z = index`years' if year ==`years'
}

csdid wealth_index $controls , time(year) gvar(discovery_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
estimate store event_wealth

esttab event_wealth ,  se tex  star(* 0.10 ** 0.05 *** 0.01) replace

//it could also be 
csdid index_z $controls , time(year) gvar(discovery_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
estimate store z_index


/*
Robustness  CHAISE
 
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
		
		**One of the tests
		replace treat = 1 if treat!=0
		replace treat_dis = 1 if treat!=0
		
	**only municipalities that have mining
replace treat = 0 if cvegeo!= mun_location
replace treat_dis = 0 if cvegeo!= mun_location
		
global controls  sexo_head edad_head hlengua_head escoacum_head 

did_multiplegt l_inc cvegeo year treat , robust_dynamic cluster(cvegeo) breps(100) dynamic(2) placebo(1) seed(0510)  controls( $controls  )  trends_lin(cvegeo)

di 		"effect_average  & "     e(effect_average)  " & se & " e(se_effect_average) " &  t_stat  & "   e(effect_average)/e(se_effect_average)  " &  p &  "   2*normal(-abs(e(effect_average)/e(se_effect_average) )) " \\"
		 
forvalues i = 0/2 {
	scalar t_stat = e(effect_`i')/e(se_effect_`i')
	scalar p_val = 2*normal(-abs(t_stat))
	di "effect_`i'  & "     e(effect_`i')  " & se & " e(se_effect_`i') " &  t_stat & "   t_stat  " &  p & "   p_val " \\"
}
forvalues i = 0/1 {
	scalar t_stat = e(placebo_`i')/e(se_placebo_`i')
	scalar p_val = 2*normal(-abs(t_stat))
	di "placebo_`i'  & "     e(placebo_`i')  " & se & " e(se_placebo_`i') " &  t_stat & "   t_stat  " &  p & "   p_val " \\"
}


event_plot e(estimates)#e(variances), stub_lag(Effect_#) stub_lead(Placebo_#)  together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on income") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

graph export "$results\Income\robChaise1.png", as(png) name("Graph") replace


/*   ********************************************************************************************************************************

DISCUSSION  SIZE AND TYPE OF MINE
 
* ********************************************************************************************************************************/ 
preserve
merge m:m cvegeo using  neighborsROB
drop if _merge==2
//We further remake start year and discovery so that it is in decades 

foreach x in  major moderate precious etm { //giant
	 qui gen filter_`x' = start_`x' if start_`x'<= start_year1 | start_year1==.
	 qui gen excluded_`x'= 1 if start_year1!=.
	 qui replace excluded_`x'= 0 if filter_`x' !=.
	 qui replace excluded_`x' = 0 if excluded_`x'==.
	
	 qui local timelag 0
	 qui gen start_treat = 1980 if filter_`x'<=1980 - `timelag' & filter_`x'!=.
	 qui replace start_treat = 1990 if filter_`x'<=1990 - `timelag' & filter_`x'!=. & start_treat==.
	 qui replace start_treat = 2000 if filter_`x'<=2000 - `timelag' & filter_`x'!=. & start_treat==.
	 qui replace start_treat = 2010 if filter_`x'<=2010 - `timelag' & filter_`x'!=. & start_treat==.
	 qui replace start_treat = 2020 if filter_`x'<=2020 - `timelag' & filter_`x'!=. & start_treat==.
	 qui replace start_treat = 0 if  start_treat==.
	
	qui replace start_treat = 0 if cvegeo!= mun_location

	qui global controls  sexo_head edad_head hlengua_head escoacum_head 

	csdid l_inc $controls if excluded_`x'==0, time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
	estimate store `x'_event

	csdid l_inc $controls if excluded_`x'==0, time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
	estimate store `x'_group

	event_plot `x'_event, stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on income") xlabel(-20(10)20 , nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

	graph export "$results\Income\`x'.png", as(png) name("Graph") replace

	esttab `x'_event using event_`x'.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace
	esttab `x'_group using group_`x'.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace
	drop start_treat
}



gen filter_giant = start_giant if start_giant<= start_year1 | start_year1==.

gen excluded = 1 if start_year1!=.
replace excluded = 0 if filter_giant!=.
replace excluded = 0 if excluded==.

local timelag 0
gen start_treat = 1980 if filter_giant<=1980 - `timelag' & filter_giant!=.
replace start_treat = 1990 if filter_giant<=1990 - `timelag' & filter_giant!=. & start_treat==.
replace start_treat = 2000 if filter_giant<=2000 - `timelag' & filter_giant!=. & start_treat==.
replace start_treat = 2010 if filter_giant<=2010 - `timelag' & filter_giant!=. & start_treat==.
replace start_treat = 2020 if filter_giant<=2020 - `timelag' & filter_giant!=. & start_treat==.
replace start_treat = 0 if  start_treat==.

replace start_treat = 0 if cvegeo!= mun_location

global controls  sexo_head edad_head hlengua_head escoacum_head 

csdid l_inc $controls if excluded==0, time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
estimate store giant_event

csdid l_inc $controls if excluded==0, time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
estimate store giant_group

event_plot giant_event, stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on income") xlabel(-20(10)20 , nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  

graph export "$results\Income\Giant.png", as(png) name("Graph") replace

esttab giant_event using event_giant.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace
esttab giant_group using group_giant.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace


/// DISCUSSION LEVEL OF INCOME AFFECTED
gquantiles algo = ingresos , xtile nquantiles(5) by( cvegeo year )

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

gen discovery_treat = 1980 if discovery<= 1980 - `timelag' & discovery!=.
replace discovery_treat = 1990 if discovery<=1990 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 2000 if discovery<=2000 - `timelag'  & discovery!=. & discovery_treat==.
replace discovery_treat = 2010 if discovery<=2010 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 2020 if discovery<=2020 - `timelag' & discovery!=. & discovery_treat==.
replace discovery_treat = 0 if  discovery_treat==.
replace start_year1 = 0 if start_year1==.
replace discovery = 0 if discovery == .

replace start_treat = 0 if cvegeo!= mun_location
replace discovery = 0 if cvegeo!= mun_location

global controls  sexo_head edad_head hlengua_head escoacum_head 

foreach i in 1 2 3 4 5 {
	csdid l_inc $controls if algo==`i', time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
	estimate store base_event`i'
	
	csdid l_inc $controls if algo==`i', time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
	estimate store base_group`i'
	
	esttab base_event`i' using Quantile`i'_event.tex , se tex  star(* 0.10 ** 0.05 *** 0.01) replace
	esttab base_group`i' using Quantile`i'_group.tex , se tex  star(* 0.10 ** 0.05 *** 0.01) replace
}



event_plot base_event1 base_event2 base_event3 base_event4 base_event5, stub_lag(Tp#) stub_lead(Tm#)  plottype(scatter) ciplottype(rcap)  together ///
			perturb(-0.325(0.13)0.325) trimlead(10) trimlag() noautolegend ///
			graph_opt(xlabel(-10(10)20) xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8)) graphregion(color(white)) bgcolor(white) ylabel(, angle(horizontal)) ///
			xtitle("Years since the event") ytitle("Average causal effect on Income") ///
			legend(order(1 "Lowest" 3 "Lower" 5 "Middle" 7 "Higher" 9 "Highest") rows(1) region(style(none)))) ///
			lag_opt1( color("70 111 157")) lag_ci_opt1(color("70 111 157")) ///
			lag_opt2( color("56 150 196")) lag_ci_opt2(color("56 150 196")) ///
			lag_opt3( color("145 179 215")) lag_ci_opt3(color("145 179 215")) ///
			lag_opt4( color("254 181 162")) lag_ci_opt4(color("254 181 162")) ///
			lag_opt5( color("237 68 74")) lag_ci_opt5(color("237 68 74"))
			
graph export "$results\Income\quintile.png", as(png) name("Graph") replace



////////////////////////////////     TEST TO CHANGE BASELINE AND INCLUDE DISCOVERY IN THE BASELINE  //////////////////////////////////////////////////////////////////
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

		gen discovery_treat = 1980 if discovery<= 1980 - `timelag' & discovery!=.
		replace discovery_treat = 1990 if discovery<=1990 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 2000 if discovery<=2000 - `timelag'  & discovery!=. & discovery_treat==.
		replace discovery_treat = 2010 if discovery<=2010 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 2020 if discovery<=2020 - `timelag' & discovery!=. & discovery_treat==.
		replace discovery_treat = 0 if  discovery_treat==.
		replace start_year1 = 0 if start_year1==.
		replace discovery = 0 if discovery == .
		
		global controls  sexo_head edad_head hlengua_head escoacum_head 
		

			csdid l_inc $controls , time(year) gvar(discovery_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
			estimate store event_`i'
			
			csdid l_inc $controls , time(year) gvar(discovery_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group)
			estimate store group_`i'


	restore
}

esttab  event_* using disBUFFERSinc_event.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace
esttab  group_* using disBUFFERSinc_group.tex, se tex  star(* 0.10 ** 0.05 *** 0.01) replace


event_plot event_5 event_10 event_25 event_50 event_75 , stub_lag(Tp#) stub_lead(Tm#)  plottype(scatter) ciplottype(rcap)  together ///
			perturb(-0.325(0.13)0.325) trimlead(10) trimlag() noautolegend ///
			graph_opt(xlabel(-10(10)20) xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8)) graphregion(color(white)) bgcolor(white) ylabel(, angle(horizontal)) ///
			xtitle("Years since the event") ytitle("Average causal effect on Income") ///
			legend(order(1 "5" 3 "10" 5 "25" 7 "50" 9 "75") rows(1) region(style(none)))) ///
			lag_opt1( color("70 111 157")) lag_ci_opt1(color("70 111 157")) ///
			lag_opt2( color("56 150 196")) lag_ci_opt2(color("56 150 196")) ///
			lag_opt3( color("145 179 215")) lag_ci_opt3(color("145 179 215")) ///
			lag_opt4( color("254 181 162")) lag_ci_opt4(color("254 181 162")) ///
			lag_opt5( color("237 68 74")) lag_ci_opt5(color("237 68 74"))
















///////////////////////////////////////////////////////////////////////// OLD STUFFS //////////////////////////////////////////////////////////////////////////////


/*
			csdid l_inc $controls,  time(year) gvar(discovery_treat)  method(dripw) 
			estat all , estore(dis`i')
			estat event,estore(cs)
			
			event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on income") ///
			title("Effect on income at `i'") xlabel(-20(10)20)) stub_lag(Tp#) stub_lead(Tm#) together	
			graph export "$results\Income\Sant_discovery`i'.png", as(png) name("Graph") replace
*/


/*
FOR STAGGER DID of Chaisemartin and D'Haultfœuille  //note that is not exactly the same as it is the effect of at municipality made based on household data 
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
		
		**A test for only municipalities that have mining
		**replace treat = 0 if cvegeo!= mun_location
		**replace treat_dis = 0 if cvegeo!= mun_location
		
		global controls  sexo_head edad_head hlengua_head escoacum_head 
		

			did_multiplegt l_inc cvegeo year treat , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )  
			
			event_plot e(estimates)#e(variances), default_look ///
			graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
			title("Effect of start on income  at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Income\Chaise_start`i'.png", as(png) name("Graph") replace

			did_multiplegt l_inc cvegeo year treat_dis , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )
			
			event_plot e(estimates)#e(variances), default_look ///
			graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
			title("Effect of discovery on income  at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Income\Chaise_discovery`i'.png", as(png) name("Graph") replace

		restore
}


/*
FOR STAGGER DID of Callaway and Sant'Anna
*/
foreach i in 25 50 {
		preserve 
		merge m:m cvegeo using  ring`i'
		drop if _merge==2
		drop if cvegeo ==mun_location
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
		
		global controls  sexo_head edad_head hlengua_head escoacum_head 
		

			csdid l_inc $controls , time(year) gvar(start_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet  //Note that the command has cluster erros at the ivar level 
			estat all
			estat event,  estore(cs)
			event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on income") ///
			title("Effect on income at `i'") xlabel()) stub_lag(Tp#) stub_lead(Tm#) together	
			graph export "$results\Income\Sant_start`i'ring.png", as(png) name("Graph") replace

			csdid l_inc $controls,  time(year) gvar(discovery_treat)  method(dripw) wboot(reps(1000) rseed(0510)) noyet 
			estat all
			estat event,  estore(cs)
			event_plot cs, default_look graph_opt(xtitle("Years since the event") ytitle("Average effect on income") ///
			title("Effect on income at `i'") xlabel()) stub_lag(Tp#) stub_lead(Tm#) together	
			graph export "$results\Income\Sant_discovery`i'ring.png", as(png) name("Graph") replace
		
	restore
}

/*
FOR STAGGER DID of Chaisemartin and D'Haultfœuille  //note that is not exactly the same as it is the effect of at municipality made based on household data 
*/
foreach i in  25  50  {
		preserve 
		merge m:m cvegeo using  ring`i'
		drop if _merge==2
		drop if cvegeo ==mun_location
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
		
		
		
		global controls  sexo_head edad_head hlengua_head escoacum_head 
		

			did_multiplegt l_inc cvegeo year treat , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )  
			
			event_plot e(estimates)#e(variances), default_look ///
			graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
			title("Effect of start on income  at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Income\Chaise_start`i'ring.png", as(png) name("Graph") replace

			did_multiplegt l_inc cvegeo year treat_dis , robust_dynamic cluster(cvegeo) breps(50) dynamic(1) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )
			
			event_plot e(estimates)#e(variances), default_look ///
			graph_opt(xtitle("Years since the event") ytitle("Average causal effect") ///
			title("Effect of discovery on income  at `i'") xlabel(-1(1)1)) stub_lag(Effect_#) stub_lead(Placebo_#) together
			graph export "$results\Income\Chaise_discovery`i'ring.png", as(png) name("Graph") replace

		restore
}

