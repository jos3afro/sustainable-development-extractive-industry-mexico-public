* Run config.do first to set path globals
do "../config.do"

///Cleaning of the water data 

import delimited "$root\mapa\Calidad agua - With municipalities.csv", stringcols(15 16 17)  //data with the municipalities
sort clavesitio
save  idAgua, replace

//data with info 
import delimited "$root\mapa\Calidad de agua - Results.csv"  

/* 
Im planning to use 3measures : oxigeno disuelto (od)  demanda bioquimica de oxigneo (bdo) y metales en el agua (mercurio)


DBO_TOT	Demanda Bioquímica de Oxígeno Total


OD_%	Oxígeno Disuelto_%	% Saturación
OD_mg/L	Oxígeno Disuelto	mg/L


AS_TOT	Arsénico Total
CD_TOT	Cadmio Total
CR_TOT	Cromo Total
HG_TOT	Mercurio Total
NI_TOT	Níquel Total
PB_TOT	Plomo Total
CN_TOT	Cianuros Totales
CU_TOT	Cobre Total
ZN_TOT	Zinc Total


HENCE WE NEED TO CLEAN AND DESTRING THOSE 
*/

//For dissolved oxygen (od)
replace od_ = "10" if od_ == "<10"
replace od_ = "150" if od_ == ">150"
destring od_, replace
label var od_ "Dissolved oxigen %"

//for total Biochemical Oxygen Demand
replace dbo_tot = "2" if dbo_tot == "<2"
replace dbo_tot = "300" if dbo_tot == ">300"
destring dbo_tot, replace
label var dbo_tot "Total Biochemical Oxygen Demand"

//for metals


replace as_tot = "0.0015" if as_tot == "<0.0015" 
replace as_tot = "0.01" if as_tot == "<0.01"
replace as_tot = "5" if as_tot == "<5"

replace cd_tot = "0.001301" if cd_tot == "<0.001301" 
replace cd_tot = "0.00130148" if cd_tot == "<0.00130148"
replace cd_tot = "0.003" if cd_tot == "<0.003"

replace cr_tot = "0.0012" if cr_tot == "<0.0012" 
replace cr_tot = "0.005" if cr_tot == "<0.005"

replace hg_tot = "0.000201289" if hg_tot == "<0.000201289" 
replace hg_tot = "0.0002013" if hg_tot == "<0.0002013"
replace hg_tot = "0.0005" if hg_tot == "<0.0005"

replace ni_tot = "0.00042" if ni_tot == "<0.00042" 
replace ni_tot = "0.001" if ni_tot == "<0.001"

replace pb_tot = "0.00154" if pb_tot == "<0.00154" 
replace pb_tot = "0.005" if pb_tot == "<0.005"

replace cn_tot = "0.001" if cn_tot == "<0.001" 

foreach x in 2 3 4 5 6 7 8 {
	replace cn_tot = "0.0`x'" if cn_tot == "<0.0`x'"
}

foreach x in 0.0003 0.0015 0.02 {
	replace cu_tot = "`x'" if cu_tot == "<`x'"
}

foreach x in 0.00284 0.01 0.05 {
	replace zn_tot = "`x'" if zn_tot == "<`x'"
}

foreach x in as_tot cd_tot cr_tot hg_tot ni_tot pb_tot cn_tot cu_tot zn_tot {
	destring `x', replace
}

label var as_tot "Arsénico Total"
label var cd_tot "Cadmio Total"
label var cr_tot "Cromo Total"
label var hg_tot "Mercurio Total"
label var ni_tot "Níquel Total"
label var pb_tot "Plomo Total"
label var cn_tot "Cianuros Totales"
label var cu_tot "Cobre Total"
label var zn_tot "Zinc Total"

keep  clavesitio clavemonitoreo nombredelsitio tipocuerpodeagua fecharealización año od_ dbo_tot transparencia as_tot cd_tot cr_tot hg_tot ni_tot pb_tot cn_tot cu_tot zn_tot temp_amb temp_agua
sort clavesitio
merge m:1 clavesitio using idAgua
drop if _merge==1  //those locations are sea or didnt match to any municipalities

order cvegeo cve_ent cve_mun clavesitio año dbo_tot od_ as_tot cd_tot cr_tot hg_tot ni_tot pb_tot cn_tot cu_tot zn_tot temp_amb temp_agua latitud longitud
keep cvegeo cve_ent cve_mun clavesitio año dbo_tot od_ as_tot cd_tot cr_tot hg_tot ni_tot pb_tot cn_tot cu_tot zn_tot temp_amb temp_agua latitud longitud  nombredelsitio tipocuerpodeagua fecharealización transparencia cuenca claveacuífero acuífero  cuerpodeagua tipodecuerpodeagua subtipocuerpoagua 
rename año year
destring cvegeo, replace
save DataAgua, replace

///FOR THE ANALYSIS 
use DataAgua, replace

sort cvegeo year
collapse (mean) dbo_tot od_ as_tot cd_tot cr_tot hg_tot ni_tot pb_tot cn_tot cu_tot zn_tot temp_amb temp_agua (max) dbo_tot_max =  dbo_tot	od__max =  od_	as_tot_max =  as_tot	cd_tot_max =  cd_tot	cr_tot_max =  cr_tot	hg_tot_max =  hg_tot	ni_tot_max =  ni_tot	pb_tot_max =  pb_tot	cn_tot_max =  cn_tot	cu_tot_max =  cu_tot	zn_tot_max =  zn_tot	temp_amb_max =  temp_amb	temp_agua_max =  temp_agua , by(cvegeo year)

merge m:1 cvegeo using Mun20, force
drop if _merge==2
drop _merge

//By doing this we have around 900 municipalities with data
merge m:m cvegeo using  neighbors5
drop if _merge==2
replace start_year1 = 0 if start_year1==.
rename start_year1 treat_start
replace discovery = 0 if discovery == .
rename discovery treat_discovery
**BASE line only municipalities that have mining
replace treat_start = 0 if cvegeo!= mun_location
replace treat_discovery = 0 if cvegeo!= mun_location

//A small correction 
replace temp_amb = 31.2 if temp_amb ==312

global controls  disttodf  temp_amb

foreach x in  dbo_tot od_ hg_tot  dbo_tot_max od__max hg_tot_max {
	csdid `x' $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
	estimate store event`x'
	
	csdid `x' $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group) 
	estimate store group`x'
}

esttab event* , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab group* , se tex  star(* 0.10 ** 0.05 *** 0.01)

foreach x in  dbo_tot od_ hg_tot  dbo_tot_max od__max hg_tot_max {

	event_plot event`x',   stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on `x'") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	graph export "$results\Environment\Water\base`x'.png", as(png) name("Graph") replace
}



foreach x in  as_tot cd_tot cr_tot  ni_tot pb_tot cn_tot cu_tot zn_tot   {
	csdid `x' $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
	estimate store ZZevent`x'
	
	
	csdid `x' $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group) 
	estimate store ZZgroup`x'
}

esttab ZZevent* , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab ZZgroup* , se tex  star(* 0.10 ** 0.05 *** 0.01)




foreach x in  as_tot_max cd_tot_max cr_tot_max  ni_tot_max pb_tot_max cn_tot_max cu_tot_max zn_tot_max   {
	csdid `x' $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
	estimate store MAXZevent`x'
	
	
	csdid `x' $controls , ivar(cvegeo)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group) 
	estimate store MAXZgroup`x'
}

esttab MAXZevent* , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab MAXZgroup* , se tex  star(* 0.10 ** 0.05 *** 0.01)

foreach x in  as_tot cd_tot cr_tot  ni_tot pb_tot cn_tot cu_tot zn_tot {

	event_plot ZZevent`x',   stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on `x'") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	graph export "$results\Environment\Water\base`x'.png", as(png) name("Graph") replace
}

foreach x in  as_tot_max cd_tot_max cr_tot_max  ni_tot_max pb_tot_max cn_tot_max cu_tot_max zn_tot_max  {

	event_plot MAXZevent`x',   stub_lag(Tp#) stub_lead(Tm#) together ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on `x'") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	graph export "$results\Environment\Water\base`x'.png", as(png) name("Graph") replace
}

/*

TEST BASED ONLY ON BODIES OF WATER

*/

import delimited "$core\water10km.csv"
merge 1:m  clavesitio using DataAgua

encode clavesitio , generate (idwater)
sort idwater year

collapse (mean) dbo_tot od_ as_tot cd_tot cr_tot hg_tot ni_tot pb_tot cn_tot cu_tot zn_tot temp_amb temp_agua no_mines  primary_metal_copper primary_metal_gold primary_metal_graphite primary_metal_ironore primary_metal_lithium primary_metal_manganese primary_metal_molybdenum primary_metal_silver primary_metal_tungsten primary_metal_zinc size_giant size_major size_moderate contain_precious contain_etm contain_other operating exploration feasibility closed stalled other_status  start_year2 close_year1 close_year2 mining1990 mining2000 mining2010 mining2020 discovery1990 discovery2000 discovery2010 discovery2020 (max) dbo_tot_max =  dbo_tot	od__max =  od_	as_tot_max =  as_tot	cd_tot_max =  cd_tot	cr_tot_max =  cr_tot	hg_tot_max =  hg_tot	ni_tot_max =  ni_tot	pb_tot_max =  pb_tot	cn_tot_max =  cn_tot	cu_tot_max =  cu_tot	zn_tot_max =  zn_tot	temp_amb_max =  temp_amb	temp_agua_max =  temp_agua  (min) mun_location start_year1 discovery 	od__min =  od_ , by(idwater year)

replace start_year1 = 0 if start_year1==.
rename start_year1 treat_start
replace discovery = 0 if discovery == .
rename discovery treat_discovery



//A small correction 
replace temp_amb = 31.2 if temp_amb ==312

global controls   temp_amb

foreach x in    hg_tot  as_tot cr_tot {
	csdid `x' $controls , ivar(idwater)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
	estimate store event`x'
	
	csdid `x' $controls , ivar(idwater)  time(year) gvar(treat_start)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group) 
	estimate store group`x'
}

esttab event* , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab group* , se tex  star(* 0.10 ** 0.05 *** 0.01)



event_plot eventas_tot,   stub_lag(Tp#) stub_lead(Tm#) together trimlead(3) ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on level of Asernic in water") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	graph export "$results\Environment\Water\ringAS.png", as(png) name("Graph") replace

event_plot eventhg_tot,   stub_lag(Tp#) stub_lead(Tm#) together trimlead(3) ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on level of Mercury in water") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	graph export "$results\Environment\Water\ringHG.png", as(png) name("Graph") replace
	
event_plot eventcr_tot,   stub_lag(Tp#) stub_lead(Tm#) together trimlead(3) ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on level of Chromium in water") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	graph export "$results\Environment\Water\ringCR.png", as(png) name("Graph") replace	
	

foreach x in    hg_tot  as_tot cr_tot {
	csdid `x' $controls , ivar(idwater)  time(year) gvar(treat_discovery)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(event) 
	estimate store disevent`x'
	
	csdid `x' $controls , ivar(idwater)  time(year) gvar(treat_discovery)  method(dripw) wboot(reps(1000) rseed(0510)) noyet agg(group) 
	estimate store disgroup`x'
}

esttab disevent* , se tex  star(* 0.10 ** 0.05 *** 0.01)
esttab disgroup* , se tex  star(* 0.10 ** 0.05 *** 0.01)

event_plot diseventas_tot,   stub_lag(Tp#) stub_lead(Tm#) together trimlead(3) ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on level of Asernic in water") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none)) 

	   	graph export "$results\Environment\Water\ringASdis.png", as(png) name("Graph") replace
	   
event_plot diseventhg_tot,   stub_lag(Tp#) stub_lead(Tm#) together trimlead(3) ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on level of Mercury in water") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	     graph export "$results\Environment\Water\ringHGdis.png", as(png) name("Graph") replace
	   
event_plot diseventcr_tot,   stub_lag(Tp#) stub_lead(Tm#) together trimlead(3) ///
       graph_opt(xtitle("Periods since the event") ytitle("Average effect on level of Chromium in water") xlabel(, nogrid) ylabel(, angle(horizontal))  ///
	   xline(-0.5, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8) ) graphregion(color(white)) bgcolor(white))   lag_opt(color("56 150 196"))  lag_ci_opt(fcolor("56 150 196%45" "56 150 196%45") lwidth(none none))  
	   
	   	graph export "$results\Environment\Water\ringCRdis.png", as(png) name("Graph") replace	

