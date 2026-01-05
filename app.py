import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE SETUP
st.set_page_config(page_title="Coffee Sales Dashboard", layout="wide")

@st.cache_data
def load_data():
    # Load the data
    df = pd.read_csv('Cleaned_data.csv')
    
    # 1. Fix Dates
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # 2. Fix Column Names (Stripping spaces just in case)
    df.columns = df.columns.str.strip()
    
    # 3. Create Total Sales Column
    # Using 'Unit Price_y' from your specific CSV structure
    df['Total Sales'] = df['Quantity'] * df['Unit Price_y']
    
    return df

try:
    df = load_data()

    # SIDEBAR FILTERS
    st.sidebar.header("Filter Here:")
    country = st.sidebar.multiselect(
        "Select Country:",
        options=df["Country_y"].unique(),
        default=df["Country_y"].unique()
    )

    coffee = st.sidebar.multiselect(
        "Select Coffee Type:",
        options=df["Coffee Type_y"].unique(),
        default=df["Coffee Type_y"].unique()
    )

    df_selection = df.query(
        "Country_y == @country & `Coffee Type_y` == @coffee"
    )

    # MAIN DASHBOARD
    st.title("☕ Coffee Sales Dashboard")
    st.markdown("##")

    # KPIs
    sales = float(df_selection["Total Sales"].sum())
    profit = float(df_selection["Profit"].sum())
    qty = int(df_selection["Quantity"].sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${sales:,.2f}")
    col2.metric("Total Profit", f"${profit:,.2f}")
    col3.metric("Items Sold", f"{qty:,}")

    st.markdown("---")

    # BAR CHART: Sales by Coffee Type
    # Fixed: Selecting only numeric column for the sum
    sales_by_coffee = df_selection.groupby("Coffee Type_y")[["Total Sales"]].sum().sort_values(by="Total Sales")
    
    fig_coffee = px.bar(
        sales_by_coffee,
        x="Total Sales",
        y=sales_by_coffee.index,
        orientation="h",
        title="<b>Sales by Coffee Type</b>",
        color_discrete_sequence=["#6F4E37"],
        template="plotly_white",
    )
    
    # LINE CHART: Sales Trend
    sales_trend = df_selection.set_index("Order Date").resample("M")[["Total Sales"]].sum().reset_index()
    fig_trend = px.line(sales_trend, x="Order Date", y="Total Sales", title="<b>Monthly Sales Trend</b>")

    left, right = st.columns(2)
    left.plotly_chart(fig_coffee, use_container_width=True)
    right.plotly_chart(fig_trend, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")