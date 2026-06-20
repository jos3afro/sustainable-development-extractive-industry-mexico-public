* Run config.do first to set path globals
do "../config.do"

///Only for emergencies

import delimited "$core\neighbors5.csv", clear

save neighbors5, replace

import delimited "$core\neighbors10.csv", clear

save neighbors10, replace

import delimited "$core\neighbors15.csv", clear

save neighbors15, replace

import delimited "$core\neighbors20.csv", clear

save neighbors20, replace

import delimited "$core\neighbors25.csv", clear

save neighbors25, replace

import delimited "$core\neighbors30.csv", clear

save neighbors30, replace

import delimited "$core\neighbors40.csv", clear

save neighbors40, replace

import delimited "$core\neighbors50.csv", clear

save neighbors50, replace

import delimited "$core\neighbors75.csv", clear

save neighbors75, replace

import delimited "$core\neighbors100.csv", clear

save neighbors100, replace


//Only for emergencies of school 
import delimited "$censo1990\school90.csv", clear 
drop v1 ent mun asiste count_ppl
save school90, replace

import delimited "$censo2000\school00.csv", clear 
drop v1 ent mun 
save school00, replace

import delimited "$censo2010\school10.csv", clear 
drop v1 ent mun 
save school10, replace

import delimited "$censo2020\school20.csv", clear 
drop v1 ent mun 
save school20, replace

use school90, clear 
foreach x in school00 school10 school20 {
	append using `x'
}

sort cvegeo year 
save school_mexico, replace

//Only for emergencies population
import delimited "$censo1990\pop90.csv", clear 
drop v1 ent mun 
save pop90, replace

import delimited "$censo2000\pop00.csv", clear 
drop v1 ent mun 
save pop00, replace

import delimited "$censo2010\pop10.csv", clear 
drop v1 ent mun 
save pop10, replace

import delimited "$censo2020\pop20.csv", clear 
drop v1 ent mun 
save pop20, replace

use pop90, clear 
merge 1:1 cvegeo using pop20, nogen

foreach x in pop00 pop10 pop20 {
	append using `x'
}
rename pobtot population
label var population "Population "

rename pea PEA
label var PEA "Poblacion Economicamente Activa"

label var pdesocup "Poblacion desocupada"

rename psinder pop_nohealth
label var pop_nohealth "Population without any health coverage"

gen unemployment = pdesocup / PEA
label var unemployment "Unemployment rate (desocupados/PEA)"

gen nohealth_coverage = pop_nohealth / population
label var nohealth_coverage "% of population without any health coverage"

sort cvegeo year 
save pop_mexico, replace


//For others
import delimited "$core\mex_info.csv", clear 
rename average90 average1990
rename average00 average2000
rename average10 average2010
rename average20 average2020
reshape long income average, i( cvegeo area agricultural human_settle agro_land human_land) j(year)
drop v1 cve_ent cve_mun nomgeo  coast capital dfmexico disttodf dist_capital perimeter x y
sort cvegeo year
save mex_covariate, replace


//For ndvi
foreach year in 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 {
	foreach month in 01 03 06 09 {
		capture import excel "$ndvi\A`year'_`month'.xlsx", sheet("A`year'_`month'") firstrow clear
		capture drop DFMexico Capital Coast NOMGEO CVE_MUN
		capture rename A`year'sum NDVI_sum
		capture label var NDVI_sum "Sum over the municipality of NDVI pixel values"
		capture rename A`year'mean NDVI_mean
		capture label var NDVI_mean "Mean over the municipality of NDVI pixel values"
		capture rename A`year'median NDVI_median
		capture label var NDVI_median "Median over the municipality of NDVI pixel values"
		capture gen year = `year'
		capture gen month = `month'
		capture save NDVI`year'`month'

	}
}

use NDVI200001, clear
foreach x in NDVI200001   NDVI200003   NDVI200006   NDVI200009   NDVI200101   NDVI200103   NDVI200106   NDVI200109   NDVI200201   NDVI200203   NDVI200206   NDVI200209   NDVI200301   NDVI200303   NDVI200306   NDVI200309   NDVI200401   NDVI200403   NDVI200406   NDVI200409   NDVI200501   NDVI200503   NDVI200506   NDVI200509   NDVI200601   NDVI200603   NDVI200606   NDVI200609   NDVI200701   NDVI200703   NDVI200706   NDVI200709   NDVI200801   NDVI200803   NDVI200806   NDVI200809   NDVI200901   NDVI200903   NDVI200906   NDVI200909   NDVI201001   NDVI201003   NDVI201006   NDVI201009   NDVI201101   NDVI201103   NDVI201106   NDVI201109   NDVI201201   NDVI201203   NDVI201206   NDVI201209   NDVI201301   NDVI201303   NDVI201306   NDVI201309   NDVI201401   NDVI201403   NDVI201406   NDVI201409   NDVI201501   NDVI201503   NDVI201506   NDVI201509   NDVI201601   NDVI201603   NDVI201606   NDVI201609   NDVI201701   NDVI201703   NDVI201706   NDVI201709   NDVI201801   NDVI201803   NDVI201806   NDVI201809   NDVI201901   NDVI201903   NDVI201906   NDVI201909   NDVI202001   NDVI202003   NDVI202006   NDVI202009  {
	append using `x'
}

save NDVI, replace


//For rings
import delimited "$core\ring25.csv", clear

save ring25, replace

import delimited "$core\ring50.csv", clear

save ring50, replace
