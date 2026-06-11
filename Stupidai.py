import streamlit as st
import pandas as pd

# Set up the dashboard layout
st.set_page_config(page_title="Universal Sales DSS", layout="wide")
st.title("📊 Universal Sales Decision Support System")

# 1. Universal Data Loader
@st.cache_data
def load_data(file_path):
    # Load the CSV
    df = pd.read_csv(file_path)
    # Strip whitespace from column names to prevent matching errors
    df.columns = df.columns.str.strip()
    return df

try:
    # Load the file
    df = load_data("sales_data.csv")
    
    # 2. Dynamic Column Classification
    # Identifies labels (text) and metrics (numbers) automatically
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    st.sidebar.header("Configuration")
    
    # User selects the identifier column (e.g., 'Product')
    selected_label = st.sidebar.selectbox("Select Item/Category Column", cat_cols)
    
    # User selects the months/metrics to analyze
    selected_metrics = st.sidebar.multiselect("Select Metric Columns", num_cols, default=num_cols)
    
    # 3. Calculation Logic
    # Calculate performance for each item based on selected columns
    df['Total_Performance'] = df[selected_metrics].sum(axis=1)
    
    st.subheader("Performance Overview")
    
    # Split UI into two sections
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### Data Preview")
        st.dataframe(df[[selected_label] + selected_metrics].head())
        
    with col2:
        st.write("### Sales Ranking")
        ranking = df.groupby(selected_label)['Total_Performance'].sum().sort_values(ascending=False)
        st.bar_chart(ranking)
    
    # 4. Actionable Decision Support
    st.subheader("Decision Support Engine")
    
    # Logic: Identify the best performer
    best_item = ranking.idxmax()
    st.success(f"**Top Performer:** '{best_item}' has the highest aggregate sales.")
    
    # Logic: Identify underperformers (below the average performance)
    avg_performance = ranking.mean()
    underperformers = ranking[ranking < avg_performance]
    
    if not underperformers.empty:
        st.warning(f"**Attention Needed:** The following items are performing below the average ({avg_performance:.0f}):")
        st.write(underperformers)
        st.info("Recommendation: Review marketing and supply for these items.")
    else:
        st.success("All items are performing above average.")

except FileNotFoundError:
    st.error("File 'sales_data.csv' not found. Please place it in the same directory as 'Stupidai.py'.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")