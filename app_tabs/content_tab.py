import streamlit as st
import pandas as pd
# from functions.data_functions import *
from functions.frontend_functions import task_id_multi_check, run_check


def content_tab():
    st.write("""
    # Content Quality Check 📖
    """)
    current_task_id = task_id_multi_check()
    dtype = 'Content'
    run_check(dtype = dtype,current_task_id = current_task_id)