import streamlit as st
import pandas as pd

# 1. Setup the dashboard layout
st.set_page_config(page_title="Universal Sales DSS", layout="wide")
st.title("📊 Universal Sales Decision Support System")

# 2. Universal Data Loader
@st.cache_data
def load_data(file_path):
    # Load the CSV
    df = pd.read_csv(file_path)
    # Strip whitespace from column names to prevent errors
    df.columns = df.columns.str.strip()
    return df

# 3. Sidebar for File Upload (Enables Global Use)
st.sidebar.header("Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload your sales CSV", type=["csv"])

try:
    if uploaded_file is not None:
        # Use uploaded file
        df = load_data(uploaded_file)
    else:
        # Fallback to local file if no upload
        df = load_data("sales_data.csv")
    
    # 4. Dynamic Column Classification
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    st.sidebar.header("Configuration")
    selected_label = st.sidebar.selectbox("Select Item/Category Column", cat_cols)
    selected_metrics = st.sidebar.multiselect("Select Metric Columns", num_cols, default=num_cols)
    
    # 5. Calculation Logic
    df['Total_Performance'] = df[selected_metrics].sum(axis=1)
    
    st.subheader("Performance Overview")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### Data Preview")
        st.dataframe(df[[selected_label] + selected_metrics].head())
        
    with col2:
        st.write("### Sales Ranking")
        ranking = df.groupby(selected_label)['Total_Performance'].sum().sort_values(ascending=False)
        st.bar_chart(ranking)
    
    # 6. Actionable Decision Support
    st.subheader("Decision Support Engine")
    best_item = ranking.idxmax()
    st.success(f"**Top Performer:** '{best_item}' has the highest aggregate sales.")
    
    avg_performance = ranking.mean()
    underperformers = ranking[ranking < avg_performance]
    
    if not underperformers.empty:
        st.warning(f"**Attention Needed:** The following items are performing below the average ({avg_performance:.0f}):")
        st.write(underperformers)
        st.info("Recommendation: Review marketing and supply for these items.")
    else:
        st.success("All items are performing above average.")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Please ensure your CSV is formatted with column headers.")