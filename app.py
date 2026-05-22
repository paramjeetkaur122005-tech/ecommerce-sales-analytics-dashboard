import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="E-Commerce Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        font-size: 42px !important;
        font-weight: 800 !important;
    }

    h2, h3 {
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 34px;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        font-size: 15px;
        font-weight: 600;
    }

    .insight-card {
        padding: 18px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 600;
        min-height: 90px;
    }

    .blue-card {
        background-color: rgba(37, 99, 235, 0.18);
        border-left: 6px solid #2563eb;
    }

    .green-card {
        background-color: rgba(22, 163, 74, 0.18);
        border-left: 6px solid #16a34a;
    }

    .yellow-card {
        background-color: rgba(202, 138, 4, 0.18);
        border-left: 6px solid #ca8a04;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def format_currency(value):
    """Format currency into readable K/M format."""
    if pd.isna(value):
        return "R$ 0"
    if value >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"R$ {value / 1_000:.2f}K"
    else:
        return f"R$ {value:.2f}"


def format_number(value):
    """Format large numbers with commas."""
    if pd.isna(value):
        return "0"
    return f"{int(value):,}"


# =========================================================
# DATA LOADING
# =========================================================
@st.cache_data
def load_data():
    possible_dirs = [
        Path.cwd() / "data",
        Path.cwd().parent / "data",
        Path.cwd().parent.parent / "data"
    ]

    data_dir = None

    for folder in possible_dirs:
        if (folder / "olist_orders_dataset.csv").exists():
            data_dir = folder
            break

    if data_dir is None:
        st.error("Data folder nahi mila. CSV files ko project ke data/ folder mein rakho.")
        st.stop()

    orders = pd.read_csv(data_dir / "olist_orders_dataset.csv")
    items = pd.read_csv(data_dir / "olist_order_items_dataset.csv")
    products = pd.read_csv(data_dir / "olist_products_dataset.csv")
    customers = pd.read_csv(data_dir / "olist_customers_dataset.csv")
    payments = pd.read_csv(data_dir / "olist_order_payments_dataset.csv")

    return orders, items, products, customers, payments


orders, items, products, customers, payments = load_data()

# =========================================================
# DATA PREPARATION
# =========================================================
@st.cache_data
def prepare_data(orders, items, products, customers, payments):

    orders = orders.copy()
    items = items.copy()
    products = products.copy()
    customers = customers.copy()
    payments = payments.copy()

    # Date conversion
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    orders["order_delivered_customer_date"] = pd.to_datetime(
        orders["order_delivered_customer_date"], errors="coerce"
    )
    orders["order_estimated_delivery_date"] = pd.to_datetime(
        orders["order_estimated_delivery_date"], errors="coerce"
    )

    # Delivered orders only
    delivered_orders = orders[orders["order_status"] == "delivered"].copy()

    # Payment aggregation at order level
    payment_order = payments.groupby("order_id", as_index=False).agg(
        total_payment=("payment_value", "sum")
    )

    # Order-level master table
    order_master = (
        delivered_orders
        .merge(customers, on="customer_id", how="left")
        .merge(payment_order, on="order_id", how="left")
    )

    order_master["total_payment"] = order_master["total_payment"].fillna(0)

    order_master["year_month"] = (
        order_master["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    order_master["year"] = order_master["order_purchase_timestamp"].dt.year
    order_master["month"] = order_master["order_purchase_timestamp"].dt.month

    # Delivery delay calculation
    order_master["delivery_delay_days"] = (
        order_master["order_delivered_customer_date"] -
        order_master["order_estimated_delivery_date"]
    ).dt.days

    order_master["delivery_status"] = np.where(
        order_master["delivery_delay_days"] > 0,
        "Late",
        "On Time"
    )

    # Item/Product level table
    item_product = items.merge(products, on="product_id", how="left")

    item_product = item_product.merge(
        delivered_orders[["order_id", "order_purchase_timestamp"]],
        on="order_id",
        how="inner"
    )

    item_product["year_month"] = (
        item_product["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    item_product["item_revenue"] = (
        item_product["price"].fillna(0) +
        item_product["freight_value"].fillna(0)
    )

    return order_master, item_product


order_master, item_product = prepare_data(
    orders, items, products, customers, payments
)

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.title("🔎 Dashboard Filters")

min_date = order_master["order_purchase_timestamp"].min().date()
max_date = order_master["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

states = sorted(order_master["customer_state"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select Customer State",
    options=states,
    default=states
)

# Date range handling
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filter order data
filtered_orders = order_master[
    (order_master["order_purchase_timestamp"].dt.date >= start_date) &
    (order_master["order_purchase_timestamp"].dt.date <= end_date) &
    (order_master["customer_state"].isin(selected_states))
].copy()

filtered_order_ids = filtered_orders["order_id"].unique()

# Filter item data based on selected orders
filtered_items = item_product[
    item_product["order_id"].isin(filtered_order_ids)
].copy()

# =========================================================
# HEADER
# =========================================================
st.title("📊 E-Commerce Sales Analytics Dashboard")

st.markdown("""
An interactive analytics dashboard built using the **Brazilian Olist E-Commerce dataset**.  
It analyzes **revenue trends, customer distribution, product category performance, average order value and delivery performance**.
""")

st.divider()

# =========================================================
# KPI CARDS
# =========================================================
total_revenue = filtered_orders["total_payment"].sum()
total_orders = filtered_orders["order_id"].nunique()
total_customers = filtered_orders["customer_unique_id"].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

valid_delivery_orders = filtered_orders.dropna(subset=["delivery_delay_days"])

late_delivery_rate = (
    (valid_delivery_orders["delivery_status"] == "Late").mean() * 100
    if len(valid_delivery_orders) > 0 else 0
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("💰 Total Revenue", format_currency(total_revenue))
col2.metric("📦 Total Orders", format_number(total_orders))
col3.metric("👥 Customers", format_number(total_customers))
col4.metric("🛒 Avg Order Value", f"R$ {avg_order_value:.2f}")
col5.metric("🚚 Late Delivery Rate", f"{late_delivery_rate:.2f}%")

st.divider()

# =========================================================
# ROW 1 CHARTS
# =========================================================
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📈 Monthly Revenue Trend")

    monthly_revenue = (
        filtered_orders
        .groupby("year_month", as_index=False)
        .agg(revenue=("total_payment", "sum"))
        .sort_values("year_month")
    )

    fig_monthly = px.line(
        monthly_revenue,
        x="year_month",
        y="revenue",
        markers=True,
        labels={
            "year_month": "Month",
            "revenue": "Revenue"
        },
        template="plotly_dark"
    )

    fig_monthly.update_traces(
        line=dict(width=3, color="#2563eb"),
        marker=dict(size=7)
    )

    fig_monthly.update_layout(
        height=430,
        xaxis_tickangle=-45,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig_monthly, use_container_width=True)

with right_col:
    st.subheader("🏆 Top 10 Product Categories by Revenue")

    category_revenue = (
        filtered_items
        .groupby("product_category_name", as_index=False)
        .agg(revenue=("item_revenue", "sum"))
        .dropna()
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    fig_category = px.bar(
        category_revenue,
        x="revenue",
        y="product_category_name",
        orientation="h",
        labels={
            "revenue": "Revenue",
            "product_category_name": "Product Category"
        },
        template="plotly_dark",
        color="revenue",
        color_continuous_scale="Greens"
    )

    fig_category.update_layout(
        height=430,
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig_category, use_container_width=True)

# =========================================================
# ROW 2 CHARTS
# =========================================================
left_col2, right_col2 = st.columns(2)

with left_col2:
    st.subheader("🌍 Top States by Orders")

    state_orders = (
        filtered_orders
        .groupby("customer_state", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            revenue=("total_payment", "sum")
        )
        .sort_values("orders", ascending=False)
        .head(10)
    )

    fig_states = px.bar(
        state_orders,
        x="customer_state",
        y="orders",
        color="revenue",
        labels={
            "customer_state": "State",
            "orders": "Orders",
            "revenue": "Revenue"
        },
        template="plotly_dark",
        color_continuous_scale="Oranges"
    )

    fig_states.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig_states, use_container_width=True)

with right_col2:
    st.subheader("🚚 Delivery Performance")

    delivery_summary = (
        valid_delivery_orders
        .groupby("delivery_status", as_index=False)
        .agg(orders=("order_id", "nunique"))
    )

    if len(delivery_summary) > 0:
        delivery_summary["percentage"] = (
            delivery_summary["orders"] /
            delivery_summary["orders"].sum() * 100
        ).round(2)

        delivery_summary["delivery_status"] = pd.Categorical(
            delivery_summary["delivery_status"],
            categories=["Late", "On Time"],
            ordered=True
        )

        delivery_summary = delivery_summary.sort_values("delivery_status")

        fig_delivery = px.bar(
            delivery_summary,
            x="delivery_status",
            y="orders",
            color="delivery_status",
            text="percentage",
            labels={
                "delivery_status": "Delivery Status",
                "orders": "Orders"
            },
            template="plotly_dark",
            color_discrete_map={
                "On Time": "#16a34a",
                "Late": "#dc2626"
            }
        )

        fig_delivery.update_traces(
            texttemplate="%{text}%",
            textposition="outside"
        )

        fig_delivery.update_layout(
            height=430,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig_delivery, use_container_width=True)
    else:
        st.warning("No delivery data available for selected filters.")

st.divider()

# =========================================================
# BUSINESS INSIGHTS
# =========================================================
st.subheader("📌 Business Insights")

insight_col1, insight_col2, insight_col3 = st.columns(3)

if len(monthly_revenue) > 0:
    best_month = monthly_revenue.sort_values(
        "revenue", ascending=False
    ).iloc[0]

    insight_col1.markdown(
        f"""
        <div class="insight-card blue-card">
            Best Revenue Month:<br>
            <span style="color:#60a5fa;">{best_month['year_month']}</span>
            with <span style="color:#60a5fa;">{format_currency(best_month['revenue'])}</span> revenue.
        </div>
        """,
        unsafe_allow_html=True
    )

if len(category_revenue) > 0:
    best_category = category_revenue.iloc[0]

    insight_col2.markdown(
        f"""
        <div class="insight-card green-card">
            Top Category:<br>
            <span style="color:#4ade80;">{best_category['product_category_name']}</span>
            generated <span style="color:#4ade80;">{format_currency(best_category['revenue'])}</span>.
        </div>
        """,
        unsafe_allow_html=True
    )

if len(state_orders) > 0:
    best_state = state_orders.iloc[0]

    insight_col3.markdown(
        f"""
        <div class="insight-card yellow-card">
            Highest Orders State:<br>
            <span style="color:#fde047;">{best_state['customer_state']}</span>
            with <span style="color:#fde047;">{format_number(best_state['orders'])}</span> orders.
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# =========================================================
# STATE LEVEL TABLE
# =========================================================
st.subheader("📄 State-Level Summary Table")

state_summary = (
    filtered_orders
    .groupby("customer_state", as_index=False)
    .agg(
        total_orders=("order_id", "nunique"),
        total_customers=("customer_unique_id", "nunique"),
        total_revenue=("total_payment", "sum"),
        avg_order_value=("total_payment", "mean")
    )
    .sort_values("total_revenue", ascending=False)
)

state_summary["total_revenue"] = state_summary["total_revenue"].round(2)
state_summary["avg_order_value"] = state_summary["avg_order_value"].round(2)

st.dataframe(
    state_summary,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# RAW DATA SAMPLE
# =========================================================
with st.expander("🔍 View Sample Order-Level Data"):
    sample_cols = [
        "order_id",
        "customer_state",
        "order_purchase_timestamp",
        "total_payment",
        "delivery_status",
        "delivery_delay_days"
    ]

    st.dataframe(
        filtered_orders[sample_cols].head(100),
        use_container_width=True,
        hide_index=True
    )
# =========================================================
# PROFESSIONAL PROJECT SUMMARY
# =========================================================
st.divider()

st.subheader("📘 Project Summary & Methodology")

# Summary metrics
summary_start_date = filtered_orders["order_purchase_timestamp"].min()
summary_end_date = filtered_orders["order_purchase_timestamp"].max()

summary_total_products = (
    filtered_items["product_id"].nunique()
    if "product_id" in filtered_items.columns else 0
)

late_orders_count = (
    valid_delivery_orders[valid_delivery_orders["delivery_status"] == "Late"]["order_id"].nunique()
    if len(valid_delivery_orders) > 0 else 0
)

on_time_orders_count = (
    valid_delivery_orders[valid_delivery_orders["delivery_status"] == "On Time"]["order_id"].nunique()
    if len(valid_delivery_orders) > 0 else 0
)

avg_late_delay = (
    valid_delivery_orders[valid_delivery_orders["delivery_status"] == "Late"]["delivery_delay_days"].mean()
    if late_orders_count > 0 else 0
)

if pd.isna(avg_late_delay):
    avg_late_delay = 0

# Best month, top category, top state safeguards
summary_best_month_text = "N/A"
summary_top_category_text = "N/A"
summary_top_state_text = "N/A"

if len(monthly_revenue) > 0:
    summary_best_month_row = monthly_revenue.sort_values("revenue", ascending=False).iloc[0]
    summary_best_month_text = f"{summary_best_month_row['year_month']} ({format_currency(summary_best_month_row['revenue'])})"

if len(category_revenue) > 0:
    summary_top_category_row = category_revenue.iloc[0]
    summary_top_category_text = f"{summary_top_category_row['product_category_name']} ({format_currency(summary_top_category_row['revenue'])})"

if len(state_orders) > 0:
    summary_top_state_row = state_orders.iloc[0]
    summary_top_state_text = f"{summary_top_state_row['customer_state']} ({format_number(summary_top_state_row['orders'])} orders)"


st.markdown(f"""
<div style="
    background-color: rgba(255,255,255,0.04);
    padding: 24px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.12);
    line-height: 1.7;
    font-size: 17px;
">

### 🎯 Business Objective

The objective of this project is to analyze an e-commerce business using transactional sales data and identify meaningful insights related to:

- Revenue performance over time  
- Best performing product categories  
- Customer and order distribution across states  
- Average order value  
- Delivery performance and late delivery rate  

This dashboard is designed for business teams to quickly monitor KPIs and identify areas where revenue, customer experience and delivery operations can be improved.

---

### 📊 Dataset Scope

The analysis uses the Brazilian Olist E-Commerce dataset and focuses only on successfully delivered orders to ensure that revenue and delivery metrics are reliable.

| Metric | Value |
|---|---:|
| Total Delivered Orders | {format_number(total_orders)} |
| Total Customers | {format_number(total_customers)} |
| Total Revenue | {format_currency(total_revenue)} |
| Average Order Value | R$ {avg_order_value:.2f} |
| Unique Products Sold | {format_number(summary_total_products)} |
| Late Delivery Rate | {late_delivery_rate:.2f}% |
| Selected Date Range | {summary_start_date.date() if pd.notna(summary_start_date) else 'N/A'} to {summary_end_date.date() if pd.notna(summary_end_date) else 'N/A'} |

---

### 🧠 Analytical Approach

The project follows a structured analytics workflow:

1. **Data Loading**  
   Multiple CSV files were loaded including orders, customers, payments, products and order items.

2. **Data Cleaning**  
   Date columns were converted into proper datetime format and only delivered orders were selected for business analysis.

3. **Data Modeling**  
   Payments were aggregated at the order level before joining with customer and order data.

4. **KPI Calculation**  
   Key metrics such as total revenue, total orders, total customers, average order value and late delivery rate were calculated.

5. **Visualization**  
   Interactive charts were created using Plotly and Streamlit to allow filtering by date range and customer state.

---

### ⚙️ Important Technical Decision

A key technical decision in this project was to calculate revenue and delivery metrics at the **order level** instead of directly using the merged item-level table.

This is important because one order can contain multiple products. If revenue or delivery metrics are calculated after merging orders with order items without aggregation, the same order can be counted multiple times.

Therefore:

- Revenue analysis uses aggregated payment value per order  
- Delivery performance uses one row per order  
- Product category analysis uses item-level data because category performance depends on products sold  

This avoids duplicate counting and makes the dashboard more accurate.

---

### 🔍 Key Business Insights

| Insight Area | Finding |
|---|---|
| Best Revenue Month | {summary_best_month_text} |
| Top Product Category | {summary_top_category_text} |
| Highest Order State | {summary_top_state_text} |
| On-Time Orders | {format_number(on_time_orders_count)} |
| Late Orders | {format_number(late_orders_count)} |
| Average Delay for Late Orders | {avg_late_delay:.1f} days |

---

### 💼 Business Interpretation

The dashboard shows that sales are highly concentrated in a few states and product categories.  
The highest order volume comes from specific regions, which indicates strong market demand in those locations.

The delivery performance section helps identify operational risk. Even though the majority of orders are delivered on time, the late delivery percentage can directly impact customer satisfaction and repeat purchase behavior.

From a business perspective, this dashboard can help teams:

- Track monthly revenue growth  
- Identify top revenue-generating product categories  
- Understand regional demand  
- Monitor delivery efficiency  
- Improve customer experience by reducing late deliveries  

---

### 🛠️ Tools & Technologies Used

- **Python** for data processing  
- **Pandas & NumPy** for data cleaning and analysis  
- **Plotly** for interactive visualizations  
- **Streamlit** for dashboard development  
- **SQL** for business query design  
- **Git/GitHub** for version control and project publishing  

---

### 🚀 Future Improvements

This project can be further improved by adding:

- Customer segmentation using RFM analysis  
- Churn or repeat-purchase prediction  
- Product recommendation analysis  
- Seller performance dashboard  
- Automated data pipeline using Airflow  
- Cloud deployment on Streamlit Cloud, AWS or Azure  

</div>
""", unsafe_allow_html=True)
