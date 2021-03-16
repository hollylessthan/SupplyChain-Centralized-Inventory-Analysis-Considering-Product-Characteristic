#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pip install openpyxl

#----------------
# Read data
#----------------

#The data file contains daily demands for one year in four different regional distribution center for three
#different products. 

demand = pd.read_excel("product_demand.xlsx", sheet_name = ['Product1', 'Product2', 'Product3'], engine="openpyxl")

product1 = demand['Product1'][:365]
product2 = demand['Product2'][:365]
product3 = demand['Product3'][:365]

#----------------
# Assumption
#----------------
#Consider a periodic review policy with review interval 6 days and lead time 5 days. 
#The cycle service level is 95%. The unit holding cost is $0.15 per unit per day.

#For the regional distribution centers, the inbound transportation cost is $0.09 per 
#unit and the outbound transportation cost is $0.10 per unit. 

#In the national distributional center case, the inbound transportation cost becomes
#$0.05 per unit and the outbound transportation cost becomes $0.24 per unit. 
#----------------

review_interval = 6
lead_time = 5
cycle_service_level = 0.95
unit_hold_cost = 0.15 #per day

#regional distribution centers
inbound_t = 0.09 
outbound_t = 0.10

#national distribution centers
inbound_nt = 0.05
outbound_nt = 0.24


#----------------
# Inventory Analysis Function based on Periodic Review Policy
#----------------

#Eleven-data demand for regional distribution centers
def eleven_day_demand_r(data):
    cols = {0:'Region1', 1:'Region2', 2:'Region3', 3:'Region4'}
    region_array = np.array([np.arange(len(data)-10), 
                             np.arange(len(data)-10), 
                             np.arange(len(data)-10), 
                             np.arange(len(data)-10)])
    demand_11 = pd.DataFrame(region_array).T.rename(columns=cols)
    
    for col in data.columns:
        demand_r = []
        for i in range(len(data)-10):
            demand_r.append(data[col][i:i+11].sum())
        demand_11[col] = demand_r
    return(demand_11)


#Eleven-data demand for national distribution centers
def eleven_day_demand_n(data):
    cols = {0:'National'}
    national_array = np.array([np.arange(len(data)-10)])
    demand_11 = pd.DataFrame(national_array).T.rename(columns=cols)
    
    for col in data.columns:
        demand_r = []
        for i in range(len(data)-10):
            demand_r.append(data[col][i:i+11].sum())
        demand_11[col] = demand_r
    return(demand_11)

#Inventory Calculation
def ans_cal(product1, cycle_service_level, review_interval, unit_hold_cost, inbound_t, outbound_t, regional=True):
    
    p1_ans = pd.DataFrame({'avg_1day_d':product1.mean()}).reset_index()
    
    if regional == True:
        product1_11day_demand = eleven_day_demand_r(product1)
    else:
        product1_11day_demand = eleven_day_demand_n(product1)
        
    avg_11_demand = pd.DataFrame({'avg_11day_d':product1_11day_demand.mean()}).reset_index()
    p1_ans = p1_ans.merge(avg_11_demand, how='left', on='index')

    # 1) OUL
    OUL = product1_11day_demand.quantile([cycle_service_level]).T.rename(columns={0.95: 'OUL'}).reset_index()
    p1_ans = p1_ans.merge(OUL, how='left', on='index')

    # 2) Average order quantity
    p1_ans['avg_order_q'] = p1_ans['avg_1day_d'] * review_interval

    # 3) Average Cycle stock
    p1_ans['avg_cycle_stock'] = p1_ans['avg_order_q'] / 2

    # 4) Average Safety Stock
    p1_ans['avg_safety_stock'] = p1_ans['OUL'] - p1_ans['avg_11day_d']

    # 5) Average Inventory
    p1_ans['avg_inventory'] = p1_ans['avg_cycle_stock'] + p1_ans['avg_safety_stock']

    # 6) Daily Average Inventory holding cost
    p1_ans['daily_inv_hold_c'] = p1_ans['avg_inventory'] * unit_hold_cost

    # 7) Daily Average transportation cost (sum of inbound and outbound)
    p1_ans['daily_transport_c'] = p1_ans['avg_1day_d'] * (inbound_t + outbound_t)

    # 8) The sum of Daily Average Inventory holding cost and Daily Average transportation cost
    p1_ans['hold_trans_total'] = p1_ans['daily_inv_hold_c'] + p1_ans['daily_transport_c']
    
    return(p1_ans)


#----------------
# Inventory Analysis for Product 1: Regional Distribution Centers
#----------------
#Visualize the daily demand distribution for four regions
f, axes = plt.subplots(2, 2, figsize=(7, 7), sharex=True)
sns.histplot(product1['Region1'], color="skyblue", ax=axes[0, 0])
sns.histplot(product1['Region2'], color="olive", ax=axes[0, 1])
sns.histplot(product1['Region3'], color="gold", ax=axes[1, 0])
sns.histplot(product1['Region4'], color="teal", ax=axes[1, 1])
plt.show()

#Average Inventory and costs across four regions
p1_regional = ans_cal(product1 = product1, 
                      cycle_service_level = cycle_service_level, 
                      review_interval = review_interval, 
                      unit_hold_cost = unit_hold_cost, 
                      inbound_t = inbound_t, 
                      outbound_t = outbound_t)

p1_regional = p1_regional.append(p1_regional.agg(['sum']))
p1_regional.loc['sum', 'index'] = 'Total'
p1_regional

#----------------
# Inventory Analysis for Product 1: National Distribution Center
#----------------

product1_N = product1.copy()
product1_N['National'] = product1_N.sum(axis=1)
product1_N.head()

p1_n = product1_N[['National']]

p1_national = ans_cal(product1 = p1_n,
                      cycle_service_level = cycle_service_level, 
                      review_interval = review_interval, 
                      unit_hold_cost = unit_hold_cost, 
                      inbound_t = inbound_nt, 
                      outbound_t = outbound_nt,
                      regional = False)
p1_national


#----------------
# Inventory Analysis for Product 2: Regional Distribution Centers
#----------------

#Visualize the daily demand distribution for four regions

f, axes = plt.subplots(2, 2, figsize=(7, 7), sharex=True)
sns.histplot(product2['Region1'], color="skyblue", ax=axes[0, 0])
sns.histplot(product2['Region2'], color="olive", ax=axes[0, 1])
sns.histplot(product2['Region3'], color="gold", ax=axes[1, 0])
sns.histplot(product2['Region4'], color="teal", ax=axes[1, 1])
plt.show()

#Average Inventory and costs across four regions
p2_regional = ans_cal(product1 = product2,
                      cycle_service_level = cycle_service_level, 
                      review_interval = review_interval, 
                      unit_hold_cost = unit_hold_cost, 
                      inbound_t = inbound_t, 
                      outbound_t = outbound_t)

p2_regional = p2_regional.append(p2_regional.agg(['sum']))
p2_regional.loc['sum', 'index'] = 'Total'
p2_regional


#----------------
# Inventory Analysis for Product 2: National Distribution Center
#----------------

product2_N = product2.copy()
product2_N['National'] = product2_N.sum(axis=1)
product2_N.head()

p2_n = product2_N[['National']]

p2_national = ans_cal(product1 = p2_n,
                      cycle_service_level = cycle_service_level, 
                      review_interval = review_interval, 
                      unit_hold_cost = unit_hold_cost, 
                      inbound_t = inbound_nt, 
                      outbound_t = outbound_nt,
                      regional = False)
p2_national                                                                                                   


#----------------
# Inventory Analysis for Product 3: Regional Distribution Centers
#----------------

#Visualize the daily demand distribution for four regions
f, axes = plt.subplots(2, 2, figsize=(7, 7), sharex=True)
sns.histplot(product3['Region1'], color="skyblue", ax=axes[0, 0])
sns.histplot(product3['Region2'], color="olive", ax=axes[0, 1])
sns.histplot(product3['Region3'], color="gold", ax=axes[1, 0])
sns.histplot(product3['Region4'], color="teal", ax=axes[1, 1])
plt.show()

#Average Inventory and costs across four regions
p3_regional = ans_cal(product1 = product3,
                      cycle_service_level = cycle_service_level, 
                      review_interval = review_interval, 
                      unit_hold_cost = unit_hold_cost, 
                      inbound_t = inbound_t, 
                      outbound_t = outbound_t)

p3_regional = p3_regional.append(p3_regional.agg(['sum']))
p3_regional.loc['sum', 'index'] = 'Total'
p3_regional

#----------------
# Inventory Analysis for Product 2: National Distribution Center
#----------------

product3_N = product3.copy()
product3_N['National'] = product3_N.sum(axis=1)
product3_N.head()

p3_n = product3_N[['National']]

p3_national = ans_cal(product1 = p3_n, 
                      cycle_service_level = cycle_service_level, 
                      review_interval = review_interval, 
                      unit_hold_cost = unit_hold_cost, 
                      inbound_t = inbound_nt, 
                      outbound_t = outbound_nt, 
                      regional=False)
p3_national                                                                                                   

#----------------
# Summarize the total costs for 3 Products
#----------------
pd.DataFrame({"Regional": [p1_regional.loc['sum','hold_trans_total'], 
                           p2_regional.loc['sum','hold_trans_total'], 
                           p3_regional.loc['sum','hold_trans_total']],
              "National": [p1_national.loc[0, 'hold_trans_total'], 
                           p2_national.loc[0, 'hold_trans_total'], 
                           p3_national.loc[0, 'hold_trans_total']]}, 
             index = ['Product1', 'Product2', 'Product3'])


# For product 2, I will recommend a national distribution center because its holding and transportation costs are lower than those of regional distribution centers. However, for product 1 and product 3, I will recommend regional distribution centers because their total holding and transportation costs are lower than the national distribution centers.


#----------------
#In some cases, the national distribution center is better, but in other
#cases, the regional distribution center is better.
#Reason behind it
#----------------
# The national distribution center brings a lower cost in some cases but higher in others is due to 2 factors:

#1. Demand correlation for each regional center
product1.corr()
product2.corr()
product3.corr()

#The demands in 4 regional centers for Product 3 are correlated in some extent.

# 2. Coefficient of Variation for each regional center
product1.std()/product1.mean()
product2.std()/product2.mean()
product3.std()/product3.mean()

# The CV is higher in product 2 and product 3


#For product 1, its CVs is very low for each region, suggesting that it is better to keep regional distribution center
#because this can help it minimize the transportation cost.

#For product 2, its regional correlation is low, and it has a high CV, meaning that it would better centralize 
#its warehouse to reduce the inventory cost.

#For product 3, its regional correlation is too high. Although it has high CVs, it would still be better to 
#keep regional distribution center.


