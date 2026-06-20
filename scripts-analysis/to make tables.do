* Run config.do first to set path globals
do "../config.do"

python
import numpy as np
from sfi import Scalar
from texttable import Texttable
import latextable

titles = [""]
Average = ["Average effect"]
se_average = ['se']
p_average = ['p']
Effects = {}
se_effect = {}
p_effect={}
Placebos ={}
se_Placebos = {}
p_Placebos = {}
for i in range(0, 10) :
	Effects['t_%s' % i] = [(str('t+')+str(i))]
	Placebos['t_%s' % i] = [(str('t-')+str(i))]
	se_Placebos['t_%s' % i] = [(str('st-')+str(i))]
	se_effect['t_%s' % i] = [(str('st+')+str(i))]
	p_Placebos['t_%s' % i] = [(str('pt-')+str(i))]
	p_effect['t_%s' % i] = [(str('pt+')+str(i))]

end

 l_inc  gini enroll_rate l_gov escoacum 
scalar name = "enroll_rate"
did_multiplegt l_gov cvegeo year treat , robust_dynamic cluster(cvegeo) breps(50) dynamic(2) placebo(1) ///
			trends_lin(cvegeo) controls( $controls  )  
ereturn list

python	
print(Placebos)	
	##inserting the stata data
dependent = 'gini'  #change each time
titles += [str(dependent)] 
Average += [str(Scalar.getValue(' e(effect_average)'))]
se_average += [str(Scalar.getValue(' e(se_effect_average)'))]
stata:  scalar p_val = 2*normal(-abs(e(effect_average)/e(se_effect_average))) 
p_average += [str(Scalar.getValue(str('p_val')))] 

stata:  scalar  p_val0 =  2*normal(-abs(e(effect_0)/e(se_effect_0)))    
stata:  scalar  p_val1 =  2*normal(-abs(e(effect_1)/e(se_effect_1)))   
stata:  scalar  p_val2 =  2*normal(-abs(e(effect_2)/e(se_effect_2)))   

for i in range(0,3):
		algo1 = 'e(effect_'+str(i)+')'
		se_algo ='e(se_effect_'+str(i)+')'
		p_algo = 'p_val'+str(i)
		Effects[str('t_'+str(i))] += [str(Scalar.getValue(str(algo1)))]
		se_effect[str('t_'+str(i))] += [str(Scalar.getValue(str(se_algo)))]                      
		p_effect[str('t_'+str(i))] += [str(Scalar.getValue(str(p_algo)))] 

stata:  scalar p_val = 2*normal(-abs(e(placebo_1)/e(se_placebo_1)))  

Placebos['t_1'] += [str(Scalar.getValue(str(' e(placebo_'+str(1)+')')))]
se_Placebos['t_1'] += [str(Scalar.getValue(str(' e(se_placebo_'+str(1)+')')))]
p_Placebos['t_1'] += [str(Scalar.getValue(str('p_val')))]                      

end

python
table_1 = Texttable()
table_1.set_deco(Texttable.HEADER)
table_1.add_rows([ titles   , Average , se_average, p_average,  
                  Effects['t_0'], se_effect['t_0'], p_effect['t_0'],
                  Effects['t_1'], se_effect['t_1'], p_effect['t_1'],
                  Effects['t_2'], se_effect['t_2'], p_effect['t_2'],  
                  Placebos['t_1'], se_Placebos['t_1'], p_Placebos['t_1']
                     ])

print(latextable.draw_latex(table_1, caption="An example table.", label="table:example_table"))
end
	



