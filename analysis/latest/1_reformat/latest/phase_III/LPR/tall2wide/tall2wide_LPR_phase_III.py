#!/usr/bin/env python
# coding: utf-8

# In[15]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os, random, time

import warnings
warnings.filterwarnings('ignore')

# In[5]:


starting_dir = os.getcwd()
print (starting_dir)

# ### Reformat LPR behavioral data

# In[7]:


#mac
#complete_input_file_path= '/Users/kimd999/research/projects/toxicity/per_each_data/phase_III/input/behavior/LPR/tall/Tanguay_Phase_3_zf_LPR_data_PNNL_2021MAR23_full_w_240_timepoints.csv'

#constance
complete_input_file_path= '/people/kimd999/tox/phase_III/LPR/input/Tanguay_Phase_3_zf_LPR_data_PNNL_2021MAR23_full_w_240_timepoints.csv'

df_behav = pd.read_csv(complete_input_file_path, header = 0)
display(len(np.unique(df_behav['chemical.id'])))
df_behav = df_behav.rename({'variable': 'timepoint'}, axis=1)
display(df_behav.head())

# In[9]:


# Keep only relevant columns
columns_to_keep = ['chemical.id', 'conc', 'plate.id', 'well', 'timepoint', 'value']
df_select = df_behav.loc[:,columns_to_keep]
df_select.head()

# In[10]:


display("chemical_id_count:"+str(len(np.unique(df_select['chemical.id']))))

# In[6]:


#behav_all_data_select = behav_all_data_select.dropna(subset=['chemical.id'])
### no row is dropped for this phase III data

#display("chemical_id_count:"+str(len(np.unique(behav_all_data_select['chemical.id']))))

# ### Transpose time points

# In[17]:


start_time = time.time()

df_reformatted = pd.DataFrame()
    
len_group_timepoint = []
    
#full_devel = "full"
full_devel = "devel"


chemical_id_from_here = np.unique(df_behav['chemical.id'])

if (full_devel == "devel"):
    choose_this_number = min(len(chemical_id_from_here), 1)
    randomly_chosen = random.sample(set(chemical_id_from_here), choose_this_number)
    chemical_id_from_here = []
    for i in range(len(randomly_chosen)):
        chemical_id_from_here.append(randomly_chosen[i])

total_number_of_chemicals_to_processed = len(chemical_id_from_here)
number_of_chemicals_processed = 0

    
for chemical_index in chemical_id_from_here:
    df_per_chemical = df_select.loc[df_behav['chemical.id'] == chemical_index,:]
    print("chemical_index:" + str(chemical_index))
    
    print("len(df_per_chemical):" + str(len(df_per_chemical)))
    
    
    # Append chemical_plate_well as a unique identifier
    df_per_chemical.insert(0, 'chemical_plate_well', df_per_chemical.loc[:,['chemical.id','plate.id', 'well']].apply(lambda x: '_'.join(x.map(str)), axis = 1))
    
    #output_filename = str(chemical_index) + ".csv"
    #behav_data_chemical.to_csv(output_filename,index=False)
    
    for cpw in np.unique(df_per_chemical.chemical_plate_well):
        df_per_cpw = df_per_chemical.loc[df_per_chemical.chemical_plate_well == cpw,:]

        df_per_cpw_grouped = df_per_cpw.groupby(['chemical.id', 'plate.id', 'well'])
        for name, group in df_per_cpw_grouped:
            
            #display("group.timepoint", group.timepoint.head())
            #len_group_timepoint.append(str(len(group.timepoint)))
            len_group_timepoint.append(str(len(np.unique(group.timepoint))))
            df_to_add = pd.DataFrame(
                    {
                    'chemical.id': np.unique(df_per_cpw['chemical.id']),
                    'plate.id': np.unique(df_per_cpw['plate.id']),
                    'well': np.unique(df_per_cpw['well']),
                    'chemical_plate_well': np.unique(df_per_cpw['chemical_plate_well']),
                    'conc': np.unique(df_per_cpw['conc'])
                    })
            #display("before concat:", df_to_add.head())
            
            # Append additonal columns corresponding to time points
            for time_point in np.arange(len(group.timepoint)):
                time_point = 't'+ str(time_point)
                #print ("\nend_point:"+str(end_point))
                #print ("pd.DataFrame({end_point: per_cpw.value[per_cpw.timepoint == end_point]}):"\
                #   +str(pd.DataFrame({end_point: per_cpw.value[per_cpw.timepoint == end_point]})))
                #print ("pd.DataFrame({end_point: per_cpw.value[per_cpw.timepoint == end_point].values}):"\
                #   +str(pd.DataFrame({end_point: per_cpw.value[per_cpw.timepoint == end_point].values})))
                df_to_add = pd.concat([df_to_add, pd.DataFrame({timepoint: df_per_cpw.value[df_per_cpw.timepoint == time_point].values})],axis = 1)
            #display("after concat:", temp.head())

            df_reformatted = pd.concat([df_reformatted, df_to_add])
            
    number_of_chemicals_processed += 1
    print_this = str(number_of_chemicals_processed) + " chemicals processed out of " + str(total_number_of_chemicals_to_processed)
    print(print_this)

end_time = time.time()
time_took = str(round((end_time-start_time), 1)) + " seconds"
print ("Done, it took:"+str(time_took)) 
# took 1.1 minutes for 1 chemical

# In[ ]:


# ds = pd.Series({"Column": len_group_variable})
# plt.figure(figsize=(8,4))
# sns.countplot(x="Column", data=ds)
# plt.show()

# In[18]:


display(df_reformatted)

# In[21]:


reformatted_data_filename = str(complete_input_file_path[:-4]) + "_wide_" + str(full_devel) + ".csv"
print ("reformatted_data_filename:" + str(reformatted_data_filename))
df_reformatted.to_csv(reformatted_data_filename,index=False)

# In[ ]:


#display(len(np.unique(reformatted_w_240_endpoints['chemical.id'])))
#display(len(np.unique(reformatted_w_non_240_endpoints['chemical.id'])))

# In[ ]:


'''reformatted_w_non_240_endpoints_155 = reformatted_w_non_240_endpoints[reformatted_w_non_240_endpoints['chemical.id']==155]

display(reformatted_w_non_240_endpoints_155.head())
display(reformatted_w_non_240_endpoints_155.tail())

output_filename = str(complete_input_file_path[:-4]) + "_155_chemical_id.csv"
print ("output_filename:"+str(output_filename))
reformatted_w_non_240_endpoints_155.to_csv(output_filename, index=False)'''

# In[ ]:


'''reformatted_w_non_240_endpoints_163 = reformatted_w_non_240_endpoints[reformatted_w_non_240_endpoints['chemical.id']==163]

display(reformatted_w_non_240_endpoints_163.head())
display(reformatted_w_non_240_endpoints_163.tail())

output_filename = str(complete_input_file_path[:-4]) + "_163_chemical_id.csv"
print ("output_filename:"+str(output_filename))
reformatted_w_non_240_endpoints_163.to_csv(output_filename, index=False)'''
