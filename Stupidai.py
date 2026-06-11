import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# 1. Page Configuration
st.set_page_config(page_title="Professional DSS", layout="wide")
st.title("🎯 Advanced Decision Support System")

# Helper function to remove date/ID-looking columns from default categorical selections
def filter_good_categories(df, cat_list):
    good_cats = []
    for col in cat_list:
        col_lower = col.lower()
        if 'date' in col_lower or 'time' in col_lower or 'id' in col_lower or 'no' in col_lower:
            continue
        if df[col].nunique() > 25:
            continue
        good_cats.append(col)
    return good_cats if good_cats else cat_list

# 2. Data Loading Engine
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df

# 3. Sidebar: Data & Weighting Controls
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your sales CSV", type=["csv"])

try:
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        df = load_data("SMARTPHONE RETAIL OUTLET SALE DATA.csv")

    st.sidebar.header("2. Analysis Configuration")
    all_cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Filter categories so 'Date' isn't auto-selected
    clean_cat_cols = filter_good_categories(df, all_cat_cols)
    group_col = st.sidebar.selectbox("Select Category to Group By", clean_cat_cols)
    
    # Auto-default metrics
    default_metrics = [m for m in ['Amount', 'Price', 'Quantity'] if m in num_cols]
    if not default_metrics:
        default_metrics = num_cols[:1]
        
    metrics = st.sidebar.multiselect("Select Metrics to Weigh", num_cols, default=default_metrics)

    if metrics:
        # 4. Accuracy Engine: Normalization
        scaler = MinMaxScaler()
        df_norm = df.copy()
        df_norm[metrics] = scaler.fit_transform(df[metrics])

        st.sidebar.subheader("Adjust Metric Weights")
        weights = {m: st.sidebar.slider(f"Weight: {m}", 0.0, 1.0, 0.5) for m in metrics}

        # 5. Calculation
        df_norm['Score'] = df_norm[metrics].multiply(pd.Series(weights), axis=1).sum(axis=1)
        results = df_norm.groupby(group_col)['Score'].mean().sort_values(ascending=False)

        # 6. Clean UI Display
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write(f"### 🏆 Performance Score: {group_col}")
            st.dataframe(results.to_frame(name='Decision Score').style.format("{:.2f}"))
        with col2:
            st.write("### 📊 Performance Visualization")
            st.bar_chart(results)

        # 7. Actionable Business Logic (Green vs Red + Price Recommendations)
        st.markdown("---")
        st.subheader("💡 Business Action Center")
        
        avg_score = results.mean()
        
        for item, score in results.items():
            # Calculate the percentage difference relative to the average
            percentage_diff = ((score - avg_score) / avg_score) * 100
            
            if score >= avg_score:
                # GREEN STATUS
                st.success(
                    f"🟢 **{item}** is in the **GREEN** (+{percentage_diff:.1f}% above average). "
                    f"Performance is strong. Strategy recommendation: Maintain regular stock and current pricing structure."
                )
            else:
                # RED STATUS
                abs_diff_pct = abs(percentage_diff)
                
                # Dynamic pricing strategy adjustment rule based on severity
                if abs_diff_pct > 30:
                    suggested_price_hike = "10% to 15%"
                elif abs_diff_pct > 15:
                    suggested_price_hike = "5% to 10%"
                else:
                    suggested_price_hike = "2% to 5%"
                    
                st.error(
                    f"🔴 **{item}** is in the **RED** ({percentage_diff:.1f}% below average). "
                    f"Performance is weak. **Action Needed:** To cover costs and recover profit margins, consider "
                    f"increasing the price of items in this category by **{suggested_price_hike}** while scaling back underperforming stock."
                )

except Exception as e:
    st.error(f"Data Error: {e}")
    st.info("Please ensure your CSV contains clean rows and columns.")