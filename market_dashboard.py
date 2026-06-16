import streamlit as st
import pandas as pd
from collections import Counter

def show_dashboard():
    st.set_page_config(page_title="Job Market Analysis", layout="wide")
    st.title("📊 Job Market Analysis")
    
    @st.cache_data
    def load_data():
        # EDA-la iruntha cleaning steps inga add panirukaen
        df = pd.read_csv("Job_Market_India_with_Skills.csv")
        df.columns = df.columns.str.lower().str.strip()
        return df

    df = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filter Dashboard")
    city_filter = st.sidebar.multiselect("Select City", sorted(df['city'].unique()))
    exp_filter = st.sidebar.multiselect("Select Experience Level", sorted(df['experience_level'].unique()))
    
    # Applying Filters
    if city_filter:
        df = df[df['city'].isin(city_filter)]
    if exp_filter:
        df = df[df['experience_level'].isin(exp_filter)]

    # --- TOP METRICS ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Openings", f"{len(df):,}")
    
    # EDA logic for top city
    top_city = df['city'].value_counts().idxmax() if not df.empty else "N/A"
    col2.metric("Top Hiring City", top_city)
    
    # Salary metric (Average)
    avg_sal = round(df['salary_inr'].mean(), 0) if not df.empty else 0
    col3.metric("Avg Salary (₹)", f"{avg_sal:,.0f}")
    
    # Remote jobs count
    remote_jobs = df['remote_option_flag'].sum() if 'remote_option_flag' in df.columns else 0
    col4.metric("Remote Jobs", remote_jobs)

    st.divider()

    # --- CHARTS SECTION 1: Companies & Location ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🏢 Top 10 Hiring Companies")
        # EDA-la iruntha logic: value_counts() head(10)
        top_comp = df['company_name'].value_counts().head(10)
        st.bar_chart(top_comp, color="#0077b6")
    
    with c2:
        st.subheader("📍 Job Demand by Location")
        # EDA-la top 10 locations paathom, adhey logic
        loc_demand = df['city'].value_counts().head(10)
        st.bar_chart(loc_demand, color="#ffb703")

    st.divider()

    # --- CHARTS SECTION 2: Salary & Experience ---
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("💰 Avg Salary by Experience (LPA)")
        # EDA Cell 23 logic: Groupby experience and get mean
        salary_exp = df.groupby('experience_level')['salary_inr'].mean().sort_values() / 100000
        st.area_chart(salary_exp)

    with c4:
        st.subheader("📈 Experience Level Demand")
        exp_dist = df['experience_level'].value_counts()
        st.bar_chart(exp_dist, color="#fb8500")

    # --- SKILLS ANALYSIS (Bottom Full Width) ---
    st.divider()
    st.subheader("🧠 Most Demanded Technical Skills")
    
    all_skills = []
    for skills in df['skills_required'].dropna():
        # EDA Cell 6 cleaning logic
        all_skills.extend([s.strip().lower() for s in skills.split(',')])
    
    if all_skills:
        skill_counts = Counter(all_skills).most_common(15)
        skill_df = pd.DataFrame(skill_counts, columns=['Skill', 'Demand'])
        st.bar_chart(skill_df.set_index('Skill'), color="#219ebc")
    else:
        st.write("No skills data available.")

# Call the function if running this file directly
if __name__ == "__main__":
    show_dashboard()