import streamlit as st
import pandas as pd
from functions.data_functions_structured import (
                                            not_allowed_na,
                                            missing_imp_col,
                                            analyze_na,
                                            duplicates,
                                            get_df_info,
                                            get_columns_dtypes
                                            )

config = st.session_state['config']

def task_id_multi_check():
    if st.session_state['DataLoadButtonState']:
        if st.session_state['task_ids_list']:
            #Selecting a task_id for verification when multiple options are provided
            if len(st.session_state['task_ids_list']) != 1:
                current_task_id =  st.radio("Choose task_id to run the check:",
                                                st.session_state['task_ids_list'])
            else:
                current_task_id = st.session_state['task_ids_list'][0]
    else:
        current_task_id = None
    return current_task_id

def run_check(dtype, current_task_id, df = st.session_state['data']):

    if st.button(f"Check {dtype} data"):
        st.session_state[f'{dtype}ButtonState'] = True
    if st.session_state[f'{dtype}ButtonState']:
        if st.session_state['DataLoadButtonState'] and current_task_id != None:
            df_dtype = st.session_state[f'{dtype}']
            if df_dtype.empty:
                st.write(f'''
                        # :grey[{dtype} data not found for the selected task_id...]😞
                        ''')
            else:

                # filtering only columns with some values 
                # to prevent columns from other task_ids migrated to othe task_id data
                df_dtype = st.session_state[f'{dtype}'].query('task_id == @current_task_id')
                nan_percentage = df_dtype.isnull().mean()
                columns_to_drop = nan_percentage[nan_percentage == 1].index
                df_dtype = df_dtype.drop(columns=columns_to_drop)


                if dtype == 'Listings':
                    no_dup_col = st.session_state['no_dup_col']
                    present_columns_to_be_checked = df_dtype.columns
                elif dtype == 'Content':
                    no_dup_col = st.session_state['no_dup_col']
                    columns_to_be_checked = df_dtype.columns
                    null_check_default_list = config['Content']['null_check_default_list']

                    present_columns_to_be_checked = [col for col in columns_to_be_checked if col in df_dtype.columns]
                    present_null_check_default_list = [col for col in null_check_default_list if col in df_dtype.columns]
                elif dtype == 'Reviews':
                    no_dup_col = st.session_state['rr_no_dup_col']
                    columns_to_be_checked = config['Reviews']['columns_to_be_checked'] 
                    null_check_default_list = config['Reviews']['null_check_default_list'] 

                    present_columns_to_be_checked = [col for col in columns_to_be_checked if col in df_dtype.columns]
                    present_null_check_default_list = [col for col in null_check_default_list if col in df_dtype.columns] 
                elif dtype == 'Q&A':
                    no_dup_col = st.session_state['qa_no_dup_col']
                    columns_to_be_checked = config['Q&A']['columns_to_be_checked'] 
                    null_check_default_list = config['Q&A']['null_check_default_list']

                    present_columns_to_be_checked = [col for col in columns_to_be_checked if col in df_dtype.columns]
                    present_null_check_default_list = [col for col in null_check_default_list if col in df_dtype.columns]  




                if df_dtype.empty:
                    st.write(f'''
                            # :grey[{dtype} data not found for the selected task_id...]😞
                            ''')
                else:

                    
                    # Value counts aggregation
                    st.write(f"""
                            #### {dtype} Summary: \n\n
                            (**:orange[{current_task_id}])**
                                """)

                    col_val_counts = ['market', 'e_retailer', 'category', 'page']
                            
                    pres_col_val_counts = [col for col in col_val_counts if col in df_dtype.columns]
                    st.write(df_dtype[pres_col_val_counts].value_counts())


                            #Missing important columns check
                    st.write("""
                                ##### *Missing important columns check:*
                                """, 
                                missing_imp_col(df_dtype, st.session_state['imp_col']))
                                
                        # Not allowed null values check
                    st.write("""
                                ##### *Not allowed NA values:* 
                                """)
                            
                    pres_col_na_check = [col for col in st.session_state['no_na_col'] if col in df_dtype.columns]
                    st.write(not_allowed_na(df_dtype, pres_col_na_check))     
                            
                    #Null alert

                    if len(analyze_na(df_dtype[present_columns_to_be_checked], st.session_state['config']).strip()) == 0:
                        st.write(':green[No columns have >10% of missing values]')
                    else:
                        st.write(':orange[**Null values warning !!!**]')
                        st.write(analyze_na(df_dtype[present_columns_to_be_checked], st.session_state['config']))




                        #duplicates check
                    if no_dup_col[0] in df_dtype:
                        st.write("""
                                    ##### *Duplicated items:* \n
                                    """, 
                                    duplicates(df_dtype, no_dup_col))
                                
                        if duplicates(df_dtype, no_dup_col) != ':green[No duplicates found.]':
                            st.write(df_dtype[df_dtype[no_dup_col].duplicated(keep=False)]\
                                    .sort_values(by='product_link'))
                    else:
                        st.write("""
                                ##### *Duplicated items:* \n
                                """, f":red[Column{no_dup_col} is not found in the dataset. Can not check duplicated items!]")
                                    
                    #### EXTRA TABLES
                            #Not null summary 
                    st.write(f'''
                                #### Non-Null Summary:
                                **(:orange[{current_task_id}])**:
                                ''')
                    st.dataframe(get_df_info(df_dtype[present_columns_to_be_checked]))


                    if dtype != 'Listings':
                                #particular columns null check
                        col_check_list = st.multiselect("Select columns for the check:",
                                                        present_columns_to_be_checked, present_null_check_default_list)
                        st.write('"✅" - not null values;')
                        st.write('"⬜️" - null values.')
                        st.write((~df_dtype[col_check_list].isnull()).value_counts())

                        if df_dtype[col_check_list].isnull().any(axis=1).any():
                            col_check_item = st.selectbox("Choose column to view records containing NA values within it:",
                                                            present_columns_to_be_checked)           
                            st.write(df_dtype[df_dtype[col_check_item].isnull()])
            
                        #descriptive statistics 
                    st.write(f'''
                                #### Descriptive statistics: \n\n
                                **(:orange[{current_task_id}])**
                                ''',
                                df_dtype[present_columns_to_be_checked].describe().loc[['count','mean','std', 'min','max']])
                            
                        # data types 
                    st.write(f'''
                                #### Data types: \n\n
                                **(:orange[{current_task_id}])**:
                                ''')
                    st.dataframe(get_columns_dtypes(df_dtype, present_columns_to_be_checked),width=400)


                        # Data overview
                    st.write(f'''
                                #### Full {dtype} Data 
                                ''')

                    st.dataframe(df_dtype)
                            
                
        else:
            st.write('''
                #### :grey[You need to load data first! 📥]
                    ''')
            st.session_state[f'{dtype}ButtonState'] = None