* config.do — run this at the top of every .do file
* It sets a global macro $root that replaces hardcoded paths.
*
* Usage in .do files:
*   do config.do          (from repo root)
*   use "$root/Core/Census90", clear
*   cd "$root/Core"

* Detect root automatically as the directory containing this file
global root "`c(pwd)'"

* Sub-path globals for convenience
global censo1990  "$root/Censo1990"
global censo2000  "$root/Censo2000"
global censo2010  "$root/Censo2010"
global censo2020  "$root/Censo2020"
global core       "$root/Core"
global results    "$root/Results"
global ndvi       "$root/NDVI"
global landuse    "$root/LandUse"

display "Root set to: $root"
