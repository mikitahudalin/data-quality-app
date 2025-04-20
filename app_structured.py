
import streamlit as st

from functions.data_functions_structured import init_session, get_config
init_session()
get_config('columns.yaml')

from app_tabs.home_tab import home_tab
from app_tabs.listings_tab import listings_tab
from app_tabs.content_tab import content_tab
from app_tabs.rr_tab import rr_tab
from app_tabs.qa_tab import qa_tab


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