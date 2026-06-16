import streamlit as st

import career_recommendation

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Job Market Analysis",
    page_icon="📊",
    layout="wide"
)                                                  

# Navigation Sidebar
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Market Dashboard", "Career Recommendation"])

if page == "Home":
    st.title("📊 Job Market Analysis")
    st.markdown("""
    Welcome to the **Next-Gen Career Portal**. 
    Use the sidebar to navigate through our tools:
    
    * **Market Dashboard**: Real-time insights into hiring trends across India.
    * **Career Recommendation**: Upload your profile and let AI find your best match.
    """)
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800", use_column_width=True)

elif page == "Market Dashboard":
    # This imports and runs the dashboard logic
    import market_dashboard
    market_dashboard.show_dashboard()

elif page == "Career Recommendation":
    # This imports and runs the recommendation logic
    import career_recommendation
    career_recommendation.show_recommendation()
    