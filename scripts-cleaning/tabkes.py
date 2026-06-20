# -*- coding: utf-8 -*-
"""
Created on Wed May  3 11:33:47 2023

@author: Jos3
"""

###Making a latex table output for stata

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
    Placebos['t_%s' % i] = [(str('t+')+str(i))]
    se_Placebos['t_%s' % i] = [(str('st+')+str(i))]
    se_effect['t_%s' % i] = [(str('st+')+str(i))]
    p_Placebos['t_%s' % i] = [(str('pt+')+str(i))]
    p_effect['t_%s' % i] = [(str('pt+')+str(i))]
    
##inserting the stata data
dependent = 'gini' #change each time
titles += [str(dependent)] 
Average += [str(Scalar.getValue(' e(effect_average)'))]
se_average += [str(Scalar.getValue(' e(se_effect_average)'))]
stata:  scalar p_val  2*normal(-abs(e(effect_average)/e(se_effect_average))) 
p_average += [str(Scalar.getValue(str('p_val')))] 

for i in range(0,3):
    Effects[t_i] += [str(Scalar.getValue(str(' e(effect_'+str(i)+')')))]
    se_effect[t_i] += [str(Scalar.getValue(str(' e(se_effect_'+str(i)+')')))]
    stata:  scalar p_val  2*normal(-abs(e(effect_i)/e(se_effect_i)))                      
    p_effect[t_i] += [str(Scalar.getValue(str('p_val')))] 

for i in range(1,2):
    Placebos[t_i] += [str(Scalar.getValue(str(' e(placebo_'+str(i)+')')))]
    se_Placebos[t_i] += [str(Scalar.getValue(str(' e(se_placebo_'+str(i)+')')))]
    stata:  scalar p_val  2*normal(-abs(e(placebo_i)/e(se_placebo_i)))                      
    p_Placebos[t_i] += [str(Scalar.getValue(str('p_val')))]                      


table_1 = Texttable()
table_1.set_deco(Texttable.HEADER)
table_1.set_cols_align(["l", "c", "c"])

table_1.add_rows([ titles   , Average , se_average, p_average,  
                  Effects[t_0], se_effect[t_0], p_effect[t_0],
                  Effects[t_1], se_effect[t_1], p_effect[t_1],
                  Effects[t_2], se_effect[t_2], p_effect[t_2],  
                  Placebos[t_1], se_Placebos[t_1], p_Placebos[t_1]
                     ])
print('-- Example 1: Basic --')
print('Texttable Output:')
print(table_1.draw())
print('\nLatextable Output:')
print(latextable.draw_latex(table_1, caption="An example table.", label="table:example_table"))