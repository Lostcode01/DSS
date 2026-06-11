import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# 1. Page Configuration
st.set_page_config(page_title="Professional DSS", layout="wide")
st.title("🎯 Advanced Decision Support System")

# 2. Data Loading Engine
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df

# 3. Sidebar: Data & Weighting Controls
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your sales CSV", type=["csv"])

# Load data (default fallback if no file uploaded)
try:
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        df = load_data("SMARTPHONE RETAIL OUTLET SALE DATA.csv")

    st.sidebar.header("2. Analysis Configuration")
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    num_cols = df.select_dtypes(include=['number']).columns.tolist()

    group_col = st.sidebar.selectbox("Select Category to Group By", cat_cols)
    metrics = st.sidebar.multiselect("Select Metrics to Weigh", num_cols, default=num_cols[:1])

    if metrics:
        # 4. Accuracy Engine: Normalization
        # This scales values 0-1 so 'Amount' doesn't overpower 'Quantity'
        scaler = MinMaxScaler()
        df_norm = df.copy()
        df_norm[metrics] = scaler.fit_transform(df[metrics])

        st.sidebar.subheader("Adjust Metric Weights")
        weights = {m: st.sidebar.slider(f"Weight: {m}", 0.0, 1.0, 0.5) for m in metrics}

        # 5. Calculation
        df_norm['Score'] = df_norm[metrics].multiply(pd.Series(weights), axis=1).sum(axis=1)
        results = df_norm.groupby(group_col)['Score'].mean().sort_values(ascending=False)

        # 6. Display Results
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("### Recommended Ranking")
            st.dataframe(results)
        with col2:
            st.write("### Performance Visualization")
            st.bar_chart(results)

        # 7. Strategic Advice
        st.success(f"**Top Recommendation:** '{results.idxmax()}' is the optimal choice based on your selected weights.")
        
        avg_score = results.mean()
        underperformers = results[results < avg_score]
        if not underperformers.empty:
            st.warning("Items requiring attention (below average score):")
            st.write(underperformers.index.tolist())

except Exception as e:
    st.error(f"Data Error: {e}")
    st.info("Please ensure your CSV contains numeric columns for analysis.")