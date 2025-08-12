import streamlit as st
import pandas as pd

from functions.frontend_functions import task_id_multi_check, run_check


def qa_tab():
    st.write("""
    # Q&A Quality Check ❔
    """)
    current_task_id = task_id_multi_check()
    dtype = 'Q&A'
    run_check(dtype = dtype,current_task_id = current_task_id)