#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Import Libraries and Files
import numpy as np
import pandas as pd
import matplotlib as plt
import matplotlib.pyplot as plt

file = "/Users/juliarivera/Desktop/itmgt25/transaction-data-adhoc-analysis.json"


df_1 = pd.read_json(file)
df_1


# In[2]:


# Pivot Table (Sales per month, sale value per item per month)


# In[3]:


#Clean data
import string
df_p = df_1.copy()
df_p_2 = df_p.transaction_items.str.split(";")
df_p = df_p.assign(transaction_items=df_p_2)
df_p = df_p[df_p["transaction_items"].apply(len)==1]
df_p['transaction_items'] = [','.join(map(str, l)) for l in df_p['transaction_items']]
df_p['quantities'] = df_p["transaction_items"].str[-5:]
df_p['quantities'] = df_p["quantities"].str.strip(',)(x')
df_p["quantities"] = df_p["quantities"].astype(int)
df_p["transaction_items"] = df_p["transaction_items"].str[:-5]

df_p


# In[4]:


items = df_p[["transaction_items", "quantities", "transaction_value"]]
items = items.drop_duplicates(subset = "transaction_items", keep = "first")
index = list(items["transaction_items"].values)
items = items['transaction_value'] / items['quantities']
items.index = index
items


# In[5]:


df_2 = df_1.assign(transaction_items=df_1.transaction_items.str.split(";")).explode('transaction_items').reset_index(drop=True)
df_2['quantities'] = df_2["transaction_items"].str[-5:]
df_2['quantities'] = df_2["quantities"].str.strip(',)(x')
df_2["quantities"] = df_2["quantities"].astype(int)
df_2["transaction_items"] = df_2["transaction_items"].str[:-5]
df_2["Total Sales"] = df_2["quantities"] * df_2["transaction_items"].apply(lambda x: items.loc[x])
df_2["Month"] = df_2["transaction_date"].str[6:7]
df_2


# In[6]:


#Pivot Table - by transaction and month
df_pivot = df_2[['Total Sales','quantities']].groupby([df_2.transaction_items, df_2.Month]).agg(sum)
df_pivot


# In[ ]:


df_pivot_2 = df_pivot.reset_index()

df_pivot_2


# In[7]:


import sys
get_ipython().system('{sys.executable} -m pip install seaborn')


# In[8]:



ax = df_pivot.unstack(level=0).plot(kind='bar', subplots=True, rot=0, figsize=(20, 50), layout=(15, 1))


# In[9]:


#Data Frame for Graphs

df_g1 = df_2[['Total Sales','quantities']].groupby([df_2.transaction_items]).agg(sum)
df_g1 = df_g1.reset_index()

df_g1


# In[10]:




y_pos = np.arange(len(df_g1['Total Sales']))

plt.bar(y_pos, df_g1['Total Sales'], align='center', alpha=0.5)
plt.xticks(y_pos,df_g1['transaction_items'])
plt.ylabel('Total Sales')
plt.title('Total Sales by Object Type')
plt.rcParams["figure.figsize"] = (100,50)
plt.rcParams.update({'font.size': 25})
plt.show()


# In[11]:



y_pos = np.arange(len(df_g1['quantities']))

plt.bar(y_pos, df_g1['quantities'], align='center', alpha=0.5)
plt.xticks(y_pos,df_g1['transaction_items'])
plt.ylabel('Quantities')
plt.title('Quantities by Object Type')
plt.rcParams["figure.figsize"] = (50,50)
plt.rcParams.update({'font.size': 25})
plt.show()



# In[12]:


df_g2 = df_2[['Total Sales','quantities']].groupby([df_2.Month]).agg(sum).reset_index()

y_pos = np.arange(len(df_g2['Total Sales']))

plt.bar(y_pos, df_g2['Total Sales'], align='center', alpha=0.5)
plt.xticks(y_pos,df_g2['Month'])
plt.ylabel('Total Sales')
plt.title('Total Sales by Month')
plt.rcParams["figure.figsize"] = (50,50)
plt.rcParams.update({'font.size': 50})
plt.show()



# In[13]:


y_pos = np.arange(len(df_g2['quantities']))

plt.bar(y_pos, df_g2['quantities'], align='center', alpha=0.5)
plt.xticks(y_pos,df_g2['Month'])
plt.ylabel('Quantities')
plt.title('Quantity by Month')
plt.rcParams["figure.figsize"] = (50,50)
plt.rcParams.update({'font.size': 25})
plt.show()




# In[14]:


df_2.pivot_table(index=["Month"], columns='transaction_items', values='Total Sales', aggfunc='sum').plot(kind='line',lw=5,fontsize=30).legend(loc='best',bbox_to_anchor=(1.0, 0.5))


# In[26]:


df_g3 = df_2.pivot_table(index=["Month"], columns='transaction_items', values='quantities', aggfunc='sum')
df_g3.plot(kind='line',lw=5,fontsize=30).legend(loc='best',bbox_to_anchor=(1.0, 0.5))


# In[16]:



df_cust = df_2[['name']].groupby([df_2.Month]).nunique()
df_cust = df_2[['name']].groupby([df_2.Month]).nunique()
df_cust_1 = df_2[['quantities']].groupby([df_2.name, df_2.Month]).agg(sum)
#df_cust_1 = df_cust_1.reset_index()
#df_cust_1 = df_cust_1.set_index("Month","name")
df_cust_1
new_index = pd.MultiIndex.from_product(df_cust_1.index.levels)
new_df = df_cust_1.reindex(new_index)
new_df = new_df.fillna(0).astype(int)


# In[17]:


#new_df = new_df.reset_index()
#new_df = new_df.set_index("Month","name")
engaged = df_2[['name']].groupby([df_2.Month]).nunique()

new_df


# In[18]:


new_df['Exists'] = new_df['quantities'].apply(lambda x: True if x >0 else False)


# In[19]:


new_df_2 = new_df.unstack(['name'])
new_df_2 = new_df_2['Exists']
new_df_2.index = new_df_2.index.map(int)
new_df_2


# In[20]:


new_df_2.info()


# In[21]:


repeaters = new_df_2.apply(lambda x: [0 if i==1 else (1 if x[i-1] and x[i] else 0)for i in x.index]).transpose().sum()
inactives = new_df_2.apply(lambda x: [0 if i==1 else ((1 if x[i]==0 else 0) if any(x[:i]) else 0) for i in x.index]).transpose().sum()
engaged = new_df_2.apply(lambda x: [1 if all(x[:i]) else 0 for i in x.index]).transpose().sum()


# In[22]:


print(repeaters)


# In[23]:


print(inactives)


# In[24]:


print(engaged)


# In[25]:


table_for_customers = pd.DataFrame({
    'repeater': repeaters,
    'inactive': inactives,
    'engaged' : engaged
    })

table_for_customers=table_for_customers.transpose()

table_for_customers

