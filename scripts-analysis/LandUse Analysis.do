* Run config.do first to set path globals
do "../config.do"

/*
#########################################   Land Use  ########################

*/

clear all

import excel "$landuse\LandUse_2001_2020.xlsx", sheet("Sheet1") firstrow clear

order CVEGEO year * 

rename CVEGEO cvegeo 
label var LandUse_mean "Mean of urban area cover (Pixels) of municipality"
label var LandUse_sum "Sum of urban area cover (Pixels) of municipality"

xtset cvegeo year

/*

*/

//Baseline 

*preserve
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
csdid LandUse_sum $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
estimate store lu_sum
estat all

csdid LandUse_mean $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event)
estimate store lu_mean
estat all

event_plot lu_sum ,  default_look stub_lag(Tp#) stub_lead(Tm#) together 

event_plot lu_sum ,  default_look stub_lag(Tp#) stub_lead(Tm#) together 


/*
#########################################   NDVI without land use  ########################

*/
import excel "$landuse\NDVI_noUrban2001-2020.xlsx", sheet("Sheet1") firstrow clear

rename CVEGEO cvegeo 
xtset cvegeo year

*preserve
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

esttab  ndvi_event , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab  ndvi_group , se tex  star(* 0.10 ** 0.05 *** 0.01)

event_plot ndvi_event ,  default_look stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Years since the event") ytitle("Average effect on NDVI") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(0, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	   graph export "$results\Environment\NDVI\noUrbanLand.png", as(png) name("Graph") replace
