import pandas as pd
from pymongo import MongoClient
import streamlit as st
import io
import yaml

from dotenv import load_dotenv
import os
load_dotenv()

def init_session():
        #config
    if 'config' not in st.session_state:
        st.session_state['config'] = None

        # full dataframe 
    if 'data' not in st.session_state:
        st.session_state['data'] = None
    if 'df_lis' not in st.session_state:
        st.session_state['df_lis'] = None
    if 'df_con' not in st.session_state:
        st.session_state['df_con'] = None
    if 'df_rr' not in st.session_state:
        st.session_state['df_rr'] = None
    if 'df_qa' not in st.session_state:
        st.session_state['df_qa'] = None

        # buttons states
    if 'DataLoadButtonState' not in st.session_state:
        st.session_state['DataLoadButtonState'] = None
    if 'ListingsButtonState' not in st.session_state:
        st.session_state['ListingsButtonState'] = None
    if 'ContentButtonState' not in st.session_state:
        st.session_state['ContentButtonState'] = None
    if 'ReviewsButtonState' not in st.session_state:
        st.session_state['ReviewsButtonState'] = None
    if 'QAButtonState' not in st.session_state:
        st.session_state['QAButtonState'] = None

        # columns lists
    if 'imp_col' not in st.session_state:
        st.session_state['imp_col'] = None
    if 'no_na_col' not in st.session_state:
        st.session_state['no_na_col'] = None
    if 'no_dup_col' not in st.session_state:
        st.session_state['no_dup_col'] = None
    if 'rr_no_dup_col' not in st.session_state:
        st.session_state['rr_no_dup_col'] = None
    if 'qa_no_dup_col' not in st.session_state:
        st.session_state['qa_no_dup_col'] = None
    
        #data required for the application to function correctly
    if 'task_ids_list' not in st.session_state:
        st.session_state['task_ids_list'] = None

def mongo_load(collection, task_ids):
    task_id_list = [task_id.strip() for task_id in task_ids.split(',') ]
    st.session_state['task_ids_list'] = task_id_list
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["crawlab"]
    if task_id_list:
        st.session_state['data'] = pd.DataFrame(db[collection].find({"task_id": {"$in": task_id_list}}))
        st.session_state['df_lis'] = pd.DataFrame(db[collection].find({"task_id": {"$in": task_id_list},
                                                                        "data_type": 'listings'}))
        st.session_state['df_con'] = pd.DataFrame(db[collection].find({"task_id": {"$in": task_id_list},
                                                                        "data_type": 'content'}))
        st.session_state['df_rr'] = pd.DataFrame(db[collection].find({"task_id": {"$in": task_id_list},
                                                                        "data_type": 'reviews'}))
        st.session_state['df_qa'] = pd.DataFrame(db[collection].find({"task_id": {"$in": task_id_list},
                                                                        "data_type": 'qa'}))
        

def get_config(config_path='columns.yaml'):
    with open(config_path, 'r') as stream:
        st.session_state['config'] = yaml.safe_load(stream)
    return st.session_state['config']

def get_columns(config):
    listing_columns_list = config['get_listings']['columns_list']
    content_columns_list = config['get_content']['columns_list']
    rr_columns_list = config['get_rr']['columns_list']
    return listing_columns_list, content_columns_list, rr_columns_list

def get_check_columns(config, scraping_type, data_types_parsed=None):
    if scraping_type == 'listing':
        imp_col = config['listing']['important_columns']
        no_na_col = config['listing']['no_na_columns']
        no_dup_col = config['listing']['no_duplicate_columns']
    elif scraping_type == 'independent products':
        if 'content' in data_types_parsed:
            imp_col = config['independent_products']['important_columns_with_content']
        else:
            imp_col = config['independent_products']['important_columns_without_content']
        no_na_col = config['independent_products']['no_na_columns']
        no_dup_col = config['independent_products']['no_duplicate_columns']
    else:
        raise ValueError("Invalid scraping type")
    
    rr_no_dup = ['review_id']
    qa_no_dup = ['qa_id']

    return imp_col, no_na_col, no_dup_col, rr_no_dup, qa_no_dup


###### QC FUNCTIONS #########

def missing_imp_col(df, imp_col):
    missing_imp_columns = [col for col in imp_col if col not in df.columns]
    if missing_imp_columns:
        warning_message = " **{}** - :red[the following important columns are missing]".format(', '.join(missing_imp_columns))
        return warning_message
    else:
        return ":green[No important columns are missing.]"

def not_allowed_na(df, no_na_col):
    columns_with_na = df[no_na_col].columns[df[no_na_col].isna().any()].tolist()
    if columns_with_na:
        warning_message = '**{}** - :red[the following columns labeled as "no NA" have missing values.] '.format(', '.join(columns_with_na))
        return warning_message
    else:
        return ':green[No columns labeled as "no NA" contain any null values.]'

def duplicates(df, no_dup_col):
    duplicates = df[no_dup_col].duplicated().any()
    if duplicates:
        warning_message = ':red[Duplicates found in columns with no duplicates allowed!!!]'
        return warning_message
    else:
        return ':green[No duplicates found.]'
    
def get_df_info(df):
    return pd.DataFrame(df.count()).reset_index().rename(columns={'index':'Column',0:'Non-null-Count'}).sort_values(by='Non-null-Count', ascending=True)


def get_columns_dtypes(df, col_names):
    col_dtypes={}
    for col in col_names:
        dtypes_present = df[col].apply(type).unique()
        dtypes_present_str = [str(dtype) for dtype in dtypes_present]
        col_dtypes[col] = dtypes_present_str
    
    for key, value in col_dtypes.items():
        # If the value is a list, join its elements into a single string
        if isinstance(value, list):
            col_dtypes[key] = ', '.join(map(str, value))

    # Convert the modified dictionary to a DataFrame
    df = pd.DataFrame.from_dict(col_dtypes, orient='index', columns=['Value'])
    return df

def analyze_na(df, config):
    na_percentage_1st_level = config['null_alert']['1_st_level']
    na_percentage_2nd_level = config['null_alert']['2_nd_level']
    
    result_strings_1st_level = []
    result_strings_2nd_level = []

    # missing value thresholds
    for column in df.columns:
        missing_percentage = df[column].isna().mean() * 100
        if missing_percentage > na_percentage_2nd_level:
            result_strings_2nd_level.append(f"**{column}** \t-\t:red[has {missing_percentage:.2f}% NA]")
        elif missing_percentage > na_percentage_1st_level:
            result_strings_1st_level.append(f"**{column}** \t-\t:orange[has {missing_percentage:.2f}% NA]") 

    return  '\n\n'.join(result_strings_2nd_level) +'\n\n'+ '\n\n'.join(result_strings_1st_level)


