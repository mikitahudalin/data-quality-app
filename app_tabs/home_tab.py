import streamlit as st
import pandas as pd
from functions.data_functions_structured import mongo_load, get_check_columns

config = st.session_state['config']

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