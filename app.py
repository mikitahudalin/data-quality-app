import streamlit as st
import pandas as pd
from functions.data_functions import *


init_session()
config = get_config('columns.yaml')

def home_tab():


    st.write("""
    # DDCD Data Quality App 🕵️‍♂️
    """)

    collection = st.selectbox("**Enter collection you used:**", ['ddcd','test'])
   
    st.write('\n \n ')
    # st.write("Please, provide one or several task id(s). In case of several task_ids, separate them by comma.")
    task_ids = st.text_area("**Please, provide one or several task id(s):** \n \n  *In case of several task_ids, separate them by comma.*", "c63fbe36-0303-4fdf-b273-c93c73849546, 9f4e6d1d-ce83-4cc1-8087-5c7ba493bd27")
    st.write('\n \n ')
    
    # st.write('**Please provide type of the scraping.** \n \n ')
    scraping_type = st.selectbox('**Please provide type of the scraping:** \n \n  *"listing"* - in case products were scraped from a listing, \n \n  *"independent products"* - independendent product cards were scraped', ['listing','independent products'])
    if scraping_type == 'independent products':
        data_types_parsed = st.multiselect("**Provide data type(s) that were scraped:**", ['listings', 'content', 'reviews', 'qa'])
    else:
        data_types_parsed = None
    
    if scraping_type == 'listing' or (scraping_type == 'independent products' and data_types_parsed): 
        st.session_state['imp_col'], st.session_state['no_na_col'], st.session_state['no_dup_col'], st.session_state['rr_no_dup_col'], st.session_state['qa_no_dup_col'] = get_check_columns(config, scraping_type, data_types_parsed)

    if st.button("Get dataframe"):
        st.session_state['DataLoadButtonState'] = True
        
    if st.session_state['DataLoadButtonState']:
        st.write('''
                    ##### :grey[Please stay at this page for a few seconds untill the data is fully loaded :smile:]''')
        mongo_load(collection, task_ids)
        df = st.session_state['data']
        st.write('''
                 ##### :green[Data Loaded✔️]''')
        # st.dataframe(df,height=200)
        
        for task_id in st.session_state['task_ids_list']:
            st.write(f'''
                     ##### :orange[_________________ {task_id} _________________]
                     ''')
            st.write("Number of rows:", df.query('task_id == @task_id').shape[0])
            st.write("Number of columns:", df.query('task_id == @task_id').shape[1])
            st.write("Data types scraped:", df.query('task_id == @task_id').data_type.value_counts())

        #The reset of all pages
        st.session_state['ListingsButtonState'] = None
        st.session_state['ContentButtonState'] = None
        st.session_state['RRButtonState'] = None
        st.session_state['QAButtonState'] = None










                #######################################
                ########## QUALITY CHECKS #############
                #######################################



                ############## LISTINGS TAB ###########
                                        
def listings_tab():   
    st.write("""
    # Listings Quality Check 📃
    """)
    if st.session_state['task_ids_list']:
        #Selecting a task_id for verification when multiple options are provided
        if len(st.session_state['task_ids_list']) != 1:
            current_task_id =  st.radio("Choose task_id to run the check:",
                                            st.session_state['task_ids_list'])
        else:
            current_task_id = st.session_state['task_ids_list'][0]
    else:
        st.empty()

    if st.button("Check listings data"):
        st.session_state['ListingsButtonState'] = True
    
    if st.session_state['ListingsButtonState']:

        if st.session_state['data'] is not None and not st.session_state['data'].empty:
            df_lis = st.session_state['df_lis'].query('task_id == @current_task_id')
            # filtering only columns with some values 
            # to prevent columns from other task_ids migrated to othe task_id data
            nan_percentage = df_lis.isnull().mean()
            columns_to_drop = nan_percentage[nan_percentage == 1].index
            df_lis = df_lis.drop(columns=columns_to_drop)

            if df_lis.empty:
                st.write('''
                         # :grey[There is no listings data available for the selected task_id...]😞
                         ''')
            else:

            
                # Value counts aggregation
                st.write(f"""
                        #### Listings Summary: \n\n
                        (**:orange[{current_task_id}])**
                        """)

                col_val_counts = ['market', 'e_retailer', 'category', 'page']
                
                pres_col_val_counts = [col for col in col_val_counts if col in df_lis.columns]
                st.write(df_lis[pres_col_val_counts].value_counts())


                    #Missing important columns check
                st.write("""
                        ##### *Missing important columns check:*
                        """, 
                        missing_imp_col(df_lis, st.session_state['imp_col']))
                    
                # Not allowed null values check
                st.write("""
                        ##### *Not allowed NA values:* 
                        """)
                
                pres_col_na_check = [col for col in st.session_state['no_na_col'] if col in df_lis.columns]
                st.write(not_allowed_na(df_lis, pres_col_na_check))     

                
                #Null alert

                if len(analyze_na(df_lis, config).strip()) == 0:
                    st.write(':green[No columns have >10% of missing values]')
                else:
                    st.write(':orange[**Null values warning !!!**]')
                    st.write(analyze_na(df_lis, config))
                    
                #duplicates check
                st.write("""
                        ##### *Duplicated products:* \n
                        """, 
                        duplicates(df_lis, st.session_state['no_dup_col']))
                    
                if duplicates(df_lis, st.session_state['no_dup_col']) != ':green[No duplicates found.]':
                    st.write(df_lis[df_lis.product_link.duplicated(keep=False)]\
                            .sort_values(by='product_link'))
                        
        #### EXTRA TABLES
                #Not null summary 
                st.write(f'''
                        #### Non-Null Summary:
                         **(:orange[{current_task_id}])**:
                        ''')
                st.dataframe(get_df_info(df_lis))
                                        
                #descriptive statistics 
                st.write(f'''
                        #### Descriptive statistics: \n\n
                          **(:orange[{current_task_id}])**
                        ''',
                        df_lis.describe().loc[['count','mean','std', 'min','max']])
                
                # data types 
                st.write(f'''
                        #### Data types: \n\n
                         **(:orange[{current_task_id}])**:
                        ''')
                st.dataframe(get_columns_dtypes(df_lis, df_lis.columns),width=400)


                # Data overview
                st.write('''
                         #### Full Listings Data 
                         ''')

                st.dataframe(df_lis)
                    
               
        else:
            st.write('''
                     #### :grey[You need to load data first! 📥]
                     ''')
            st.session_state['ListingsButtonState'] = None


                                                            
                                                            
                                            ########## CONTENT TAB #############

def content_tab():
    st.write("""
    # Content Quality Check 📖
    """)
    if st.session_state['task_ids_list']:
        #Selecting a task_id for verification when multiple options are provided
        if len(st.session_state['task_ids_list']) != 1:
            current_task_id =  st.radio("Choose task_id to run the check:",
                                            st.session_state['task_ids_list'])
        else:
            current_task_id = st.session_state['task_ids_list'][0]
    else:
        st.empty()

    if st.button("Check content data"):
        st.session_state['ContentButtonState'] = True

    if st.session_state['ContentButtonState']:

        if st.session_state['data'] is not None and not st.session_state['data'].empty:
            df_con = st.session_state['df_con'].query('task_id == @current_task_id')
            # filtering only columns with some values 
            # to prevent columns from other task_ids migrated to othe task_id data
            nan_percentage = df_con.isnull().mean()
            columns_to_drop = nan_percentage[nan_percentage == 1].index
            df_con = df_con.drop(columns=columns_to_drop)

            if df_con.empty:
                    st.write('''
                             # :grey[There is no content data available for the selected task_id...]😞
                             ''')
            else: 

                #Value counts aggregation               
                st.write(f"""
                        #### Content Summary:
                         **(:orange[{current_task_id}])**
                        """) 
                
                
                col_val_counts = ['market', 'e_retailer', 'category', 'page']
                
                pres_col_val_counts = [col for col in col_val_counts if col in df_con.columns]
                st.write(df_con[pres_col_val_counts].value_counts())


                # Missing important columns check
                st.write("""
                        ##### *Missing important columns:*
                        """, 
                        missing_imp_col(df_con, st.session_state['imp_col']))
                

                # Not allowed null values check
                st.write("""
                        ##### *Not allowed NA values:*
                        """)
                
                pres_col_na_check = [col for col in st.session_state['no_na_col'] if col in df_con.columns]
                st.write(not_allowed_na(df_con, pres_col_na_check)) 

                        # not_allowed_na(df_con, st.session_state['no_na_col']))
                #Null alert
                if len(analyze_na(df_con, config).strip()) == 0:
                    st.write(':green[No columns have >10% of missing values]')
                else:
                    st.write(':orange[**Null values warning !!!**]')
                    st.write(analyze_na(df_con, config))

                # Duplicates check            
                st.write("""
                        ##### *Duplicated products:*
                        """, 
                        duplicates(df_con, st.session_state['no_dup_col']))
                
                if duplicates(df_con, st.session_state['no_dup_col']) != ':green[No duplicates found.]':
                    st.write(df_con[df_con.product_link.duplicated(keep=False)]\
                            .sort_values(by='product_link'))
                    
                # Non-null summary
                st.write(f'''
                         #### Non-Null Summary :
                         **(:orange[{current_task_id}])**
                         ''')
                st.dataframe(get_df_info(df_con))
                #particular columns null check
                con_col_check_list = st.multiselect("Select columns for the check:",
                                                    df_con.columns, ['title', 'description', 'bullet_points'])
                st.write('"✅" - not null values;')
                st.write('"⬜️" - null values.')
                st.write((~df_con[con_col_check_list].isnull()).value_counts())

                if df_con[con_col_check_list].isnull().any(axis=1).any():
                    con_col_check_item = st.selectbox("Choose column to view records containing NA values within it:",
                                                    df_con.columns)           
                    st.write(df_con[df_con[con_col_check_item].isnull()])

                # Descriptive statistics
                st.write(f'''
                         #### Descriptive statistics:
                         **(:orange[{current_task_id}])**
                         ''',
                        df_con.describe().loc[['count','mean','std', 'min','max']])
                

                # Data types 
                st.write(f'''
                         #### Data types:
                          **(:orange[{current_task_id}])**
                         ''')
                st.dataframe(get_columns_dtypes(df_con, df_con.columns), width=400)

                # Data Overview
                st.write('''
                         #### Full Content Data 
                         ''')

                st.dataframe(df_con)
        else:
            st.write('''
                     #### :grey[You need to load data first! 📥]
                     ''')
            st.session_state['ContentButtonState'] = None


                                                
                                                
                                                ##################### RR TAB ########################

def rr_tab():
    st.write("""
    # Reviews Quality Check 🗨️
    """)

    #Selecting a task_id for verification when multiple options are provided
    if st.session_state['task_ids_list']:
        #Selecting a task_id for verification when multiple options are provided
        if len(st.session_state['task_ids_list']) != 1:
            current_task_id =  st.radio("Choose task_id to run the check:",
                                            st.session_state['task_ids_list'])
        else:
            current_task_id = st.session_state['task_ids_list'][0]
    else:
        st.empty()

    if st.button("Check reviews data"):
        st.session_state['RRButtonState'] = True

    if st.session_state['RRButtonState']:
        
        
        if st.session_state['data'] is not None and not st.session_state['data'].empty:
            df_rr = st.session_state['df_rr'].query('task_id == @current_task_id')
            # filtering only columns with some values 
            # to prevent columns from other task_ids migrated to othe task_id data
            nan_percentage = df_rr.isnull().mean()
            columns_to_drop = nan_percentage[nan_percentage == 1].index
            df_rr = df_rr.drop(columns=columns_to_drop)

            if df_rr.empty:
                st.write('''
                             # :grey[There is no reviews data available for the selected task_id...]😞
                             ''')
            else:
                st.write(f"""
                        #### R&R Summary:
                        **(:orange[{current_task_id}])**
                        """)
                #filtering only columns with some values
                nan_percentage = df_rr.isnull().mean()
                columns_to_drop = nan_percentage[nan_percentage == 1].index
                col_val_counts = ['market', 'e_retailer', 'category', 'page']
                
                pres_col_val_counts = [col for col in col_val_counts if col in df_rr.columns]
                st.write(df_rr[pres_col_val_counts].value_counts())


                # st.write(df_rr[['market', 'e_retailer', 'category', 'page']].value_counts())
                

                # Missing important columns check
                st.write("""
                        ##### *Missing important columns check:*\n
                        """, 
                        missing_imp_col(df_rr, st.session_state['imp_col']))
                

                #Not allowed NA check
                st.write("""
                        ##### *Not allowed NA values:*
                        """)
                pres_col_na_check = [col for col in st.session_state['no_na_col'] if col in df_rr.columns]
                st.write(not_allowed_na(df_rr, pres_col_na_check))     

                #Null alert
                if len(analyze_na(df_rr, config).strip()) == 0:
                    st.write(':green[No columns have >10% of missing values]')
                else:
                    st.write(':orange[**Null values warning !!!**]')
                    st.write(analyze_na(df_rr, config))

                # Duplicates
                st.write("""
                        ##### *Duplicated reviews:* \n
                        """, 
                        duplicates(df_rr, st.session_state['rr_no_dup_col']))         
                if duplicates(df_rr, st.session_state['rr_no_dup_col']) != ':green[No duplicates found.]':
                    st.write(df_rr[df_rr.review_id.duplicated(keep=False)]\
                            .sort_values(by='review_id'))
                
                #Non null summary
                st.write(f'''
                         #### Non-Null Summary:
                         **(:orange[{current_task_id}])**
                         ''')
                st.dataframe(get_df_info(df_rr))
                # particular columns null values check
                rr_col_check_list = st.multiselect("Particular columns check for nulls:",
                                    df_rr.columns, ['review_rating','content'])
                st.write('"✅" - not null values;')
                st.write('"⬜️" - null values.')
                st.write((~df_rr[rr_col_check_list].isnull()).value_counts())

                if df_rr[rr_col_check_list].isnull().any(axis=1).any():
                    rr_col_check_item = st.selectbox("Choose column to view records containing NA values within it:",
                                                        df_rr.columns)
                    if df_rr[df_rr[rr_col_check_item].isnull()].empty:
                        st.write('No null values were found in this column.')
                    else:      
                        st.write(df_rr[df_rr[rr_col_check_item].isnull()])

                #Descriptive stats
                st.write(f'''
                         #### Descriptive statistics:
                         **(:orange[{current_task_id}])**
                         ''',
                        df_rr.describe().loc[['count','mean','std', 'min','max']])
                

                #Data types
                st.write(f'''
                         #### Data types:
                         **(:orange[{current_task_id}])**
                         ''')
                st.dataframe(get_columns_dtypes(df_rr, df_rr.columns), width=400)

                # Data overview
                st.write('''
                         #### Full R&R Data 
                         ''')

                st.dataframe(df_rr)

        else:
            st.write('''
                     #### :grey[You need to load data first! 📥]
                     ''')
            st.session_state['RRButtonState'] = None



                                                    
                                                    
                     ################### QA TAB #######################

def qa_tab():
    st.write("""
    # Q&A Quality Check ❔
    """)
    if st.session_state['task_ids_list']:
        #Selecting a task_id for verification when multiple options are provided
        if len(st.session_state['task_ids_list']) != 1:
            current_task_id =  st.radio("Choose task_id to run the check:",
                                            st.session_state['task_ids_list'])
        else:
            current_task_id = st.session_state['task_ids_list'][0]
    else:
        st.empty()

    if st.button("Check Q&A data"):
        st.session_state['QAButtonState'] = True

    if st.session_state['QAButtonState']:
        if st.session_state['data'] is not None and not st.session_state['data'].empty:
            df_qa = st.session_state['df_qa'].query('task_id == @current_task_id')
            # filtering only columns with some values 
            # to prevent columns from other task_ids migrated to othe task_id data
            nan_percentage = df_qa.isnull().mean()
            columns_to_drop = nan_percentage[nan_percentage == 1].index
            df_qa = df_qa.drop(columns=columns_to_drop)

            if df_qa.empty:
                st.write('''
                        # :grey[There is no Q&A data available for the selected task_id...]😞
                        ''')
            else:    

                # Value counts aggregation      
                st.write(f"""
                        #### Q&A Summary:
                         **(:orange[{current_task_id}])**
                        """) 
                
                col_val_counts = ['market', 'e_retailer', 'category', 'page']
                
                pres_col_val_counts = [col for col in col_val_counts if col in df_qa.columns]
                st.write(df_qa[pres_col_val_counts].value_counts())
                
                #Missing important columns 
                st.write("""
                        ##### *Missing important columns check:*
                        """, 
                        missing_imp_col(df_qa, st.session_state['imp_col']))
                
                #Not allowed NA values
                st.write("""
                        ##### *Not allowed NA values:* 
                        """)
                pres_col_na_check = [col for col in st.session_state['no_na_col'] if col in df_qa.columns]
                st.write(not_allowed_na(df_qa, pres_col_na_check))     

                # #Null alert
                if len(analyze_na(df_qa, config).strip()) == 0:
                    st.write(':green[No columns have >10% of missing values]')
                else:
                    st.write(':orange[**Null values warning !!!**]')
                    st.write(analyze_na(df_qa, config))
            
                # Duplicates check
                st.write(f"""
                        ##### *Duplicated QA:* \n
                        """, 
                        duplicates(df_qa, st.session_state['qa_no_dup_col']))
                            
                if duplicates(df_qa, st.session_state['qa_no_dup_col']) != ':green[No duplicates found.]':
                    st.write(df_qa[df_qa.qa_id.duplicated(keep=False)]\
                            .sort_values(by='qa_id'))

                # Non null summary
                st.write(f'''
                         #### Non-Null Summary:
                         **(:orange[{current_task_id}])**
                         ''') 
                st.dataframe(get_df_info(df_qa[['questions','answers','qa_date','qa_id','votes']]))
                # particular null values check
                qa_col_check_list = ['questions','answers','qa_date','qa_id','votes']
                st.write('"✅" - not null values;')
                st.write('"⬜️" - null values.')
                st.write((~df_qa[qa_col_check_list].isnull()).value_counts())
                qa_col_check_item = st.selectbox("Choose column to view records containing NA values within it:",
                                                    qa_col_check_list)
                
                if not df_qa[df_qa[qa_col_check_item].isnull()].empty:
                    st.write(df_qa[df_qa[qa_col_check_item].isnull()])
                else:
                    st.write('No null values were found for this field.') 

                # Descriptive stats 
                st.write(f'''
                         #### Descriptive statistics:
                         **(:orange[{current_task_id}])**
                         ''',                   
                        df_qa.describe().loc[['count','mean','std', 'min','max']])
                

                # Data types
                st.write(f"""
                         #### Data types:
                         **(:orange[{current_task_id}])**
                         """)
                st.dataframe(get_columns_dtypes(df_qa, df_qa.columns), width=400)

                # Data overview
                st.write('''
                         #### Full Q&A Data 
                         ''')

                st.dataframe(df_qa)

        else:
            st.write('''
                     #### :grey[You need to load data first! 📥]
                     ''')
            st.session_state['QAButtonState'] = None




############################################################################################################################################    

# Main function to run the app
def main():
    # Tabs
    tabs = [
            "Home", 
            "Listings Quality Check", "Content Quality Check",
            "Reviews Quality Check",  "Q&A Quality Check"      
            ]
    st.sidebar.markdown("<h1  color: #fc2a61;'>Navigation</h1>", unsafe_allow_html=True)
    selected_tab = st.sidebar.radio("",options=tabs)

    # display the selected tab content
    if selected_tab == "Home":
        home_tab()
    elif selected_tab == "Listings Quality Check":
        listings_tab()
    elif selected_tab == "Content Quality Check":
        content_tab()
    elif selected_tab == "Reviews Quality Check":
        rr_tab()
    elif selected_tab == "Q&A Quality Check":
        qa_tab()

# Runs the app
if __name__ == "__main__":
    main()