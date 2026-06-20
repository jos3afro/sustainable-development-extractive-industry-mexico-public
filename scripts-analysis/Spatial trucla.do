* Run config.do first to set path globals
do "../config.do"

clear all

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

//We balance the panel (and we lose 159 obs)
sort cvegeo year
drop if  escoacum_head==.
drop if  gini==.
by cvegeo: egen nomissing = count(y) if (year==1990 | year==2000 | year==2010| year==2020)
keep if nomissing == 4
drop nomissing
table year

merge m:1 cvegeo using Mexico_Map

preserve
keep if year==2010
spmatrix create  contiguity Wcontig
spmatrix create  contiguity Wcontig, normalize(row) replace  //we make the weight matrix
spmatrix export Wcontig using Wcontig.txt
import delimited "$core\Wcontig.txt", delimiter(space) clear 
drop v1
drop in 1
save algo, replace
restore

spregdpd gini sexo_head edad_head hlengua_head escoacum_head, wmfile($core\algo.dta) nc(2393) model(sar) run(xtdhp) fe mfx(lin) lmspac lmhet
