import streamlit as st
import pandas as pd

from functions.frontend_functions import task_id_multi_check, run_check


def rr_tab():
    st.write("""
    # Reviews Quality Check 🗨️
    """)
    current_task_id = task_id_multi_check()
    dtype = 'Reviews'
    run_check(dtype = dtype,current_task_id = current_task_id)