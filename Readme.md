
# 📊 E-Commerce Sales Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io)
[![SQL](https://img.shields.io/badge/SQL-Analytics-CC2927.svg)](https://en.wikipedia.org/wiki/SQL)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📌 Project Overview
This project is an end-to-end **E-Commerce Sales Analytics Dashboard** built using the public Brazilian Olist E-Commerce dataset. It analyzes sales performance, customer behavior, product category revenue, delivery efficiency, and regional order distribution using **Python, SQL, and Streamlit**.

The interactive dashboard enables businesses to monitor vital KPIs, uncover hidden trends, and make data-driven operational decisions through dynamic visualizations.

---

## 💼 Business Problem
E-commerce platforms generate massive transactional datasets daily. Without proper analytics, organizations struggle to identify:
* **Growth Vectors:** Revenue trends over time.
* **Product Performance:** High-performing vs. stagnant product categories.
* **Geographic Insights:** Customer distribution and regional demand.
* **Financial Metrics:** Average customer spending and payment preferences.
* **Operational Bottlenecks:** Delivery delays and state-wise efficiency logs.

This project bridges these gaps by delivering real-time, business-focused insights.

---

## 🛠️ Tech Stack & Tools
* **Data Processing:** Python, Pandas, NumPy
* **Data Visualization:** Plotly, Streamlit
* **Database Analysis:** SQL (Structured Queries for Deep Dives)
* **Environment & Version Control:** Jupyter Notebook, Git & GitHub

---

## 📊 Dataset Insights
* **Source:** [Brazilian E-Commerce Public Dataset by Olist (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
* **Core Tables Utilized:**
  * `olist_orders_dataset.csv` (Order status, timelines)
  * `olist_order_items_dataset.csv` (Price, freight, product associations)
  * `olist_products_dataset.csv` (Category names, dimensions)
  * `olist_customers_dataset.csv` (Customer location, zip codes)
  * `olist_order_payments_dataset.csv` (Payment types, installments)

---

## 🚀 Key Features
* **Interactive Controls:** Date range filters and Customer State selectors.
* **Executive KPI Cards:** 
  * Total Revenue ($R\$$) & Order Volume
  * Unique Customer Count
  * Average Order Value (AOV)
  * Late Delivery Rate ($\%$)
* **Advanced Visualizations:** Monthly revenue trends, Top product categories, and State-wise order distributions.
* **Granular Delivery Tracking:** Operational efficiency metrics and state-level summary tables.
* **SQL Deep Dive:** Pre-written production-grade business analysis queries.

---

## 📈 Key Business Findings
| Metric | Analysis Result |
| :--- | :--- |
| **Total Revenue** | **R$ 15M+** analyzed |
| **Delivered Orders** | **96K+** completed shipments |
| **Total Customers** | **93K+** unique buyers |
| **Logistics Health** | Late delivery rate stabilizes around **6–7%** |
| **Top Region** | **São Paulo (SP)** dominates order volume |
| **Top Categories** | Health & Beauty, Watches & Gifts, Bed/Table/Bath |

---

## 📂 Project Structure
```text
sales-analytics-project/
│
├── data/                         # Compressed dataset files
│   ├── olist_orders_dataset.csv
│   └── ...
├── notebooks/                    # Exploratory Data Analysis (EDA)
│   └── analysis_notebook.ipynb
├── sql/                          # Production-ready SQL scripts
│   └── business_queries.sql
├── dashboard/                    # Dashboard UI Mockups/Screenshots
│   ├── dashboard_overview.png
│   └── ...
├── app.py                        # Main Streamlit Application
├── requirements.txt              # Project Dependencies
├── .gitignore
└── README.md

```

---

## ⚙️ How to Run the Project

### 1. Clone the Repository

```bash
git clone <your-repository-link>
cd sales-analytics-project

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

### 3. Launch the Streamlit Dashboard

```bash
streamlit run app.py

```

---

## 🖼️ Dashboard Preview

### 1. Executive Overview

 <img width="1615" height="822" alt="image" src="https://github.com/user-attachments/assets/a250b955-7bc4-4086-a488-f92327bb762c" />


### 2. Revenue breakdown and category 

<img width="1637" height="517" alt="image" src="https://github.com/user-attachments/assets/63b73074-4d61-4a45-8049-3723800596eb" />


### 3. Logistics & Regional Summary

<img width="1604" height="777" alt="image" src="https://github.com/user-attachments/assets/5726d328-cd0c-4e9e-b7d9-55d022ca343a" />


---

## 🗄️ SQL Analysis

The repository contains optimized SQL scripts under `sql/business_queries.sql` designed to pull critical business metrics:

* Monthly Revenue & Growth Trends
* Top Categories by Financial Volume
* State-wise Revenue Concentration
* Distribution of Payment Methods & Installments
* Customer Lifetime Spending Rankings

> ⚠️ **Important Technical Note:** For revenue and delivery analysis, **order-level aggregation** was strictly applied to eliminate duplicate counting caused by multi-item orders.

---

## 🧠 Key Learnings

* Developed complex multi-table joins and data cleaning pipelines in **Pandas**.
* Mastered the distinction between **Order-level vs. Item-level aggregations** in business metrics.
* Designed and deployed clean, performant, and reactive web UIs using **Streamlit**.
* Documented enterprise-ready data project workflows from data acquisition to deployment.

---

## 🔮 Future Enhancements

* [ ] Integrate Time-Series Forecasting (Prophet/ARIMA) for sales predictions.
* [ ] Live deployment on Streamlit Cloud/AWS.
* [ ] Add RFM (Recency, Frequency, Monetary) Customer Segmentation analysis.
* [ ] Build a fully responsive, mobile-first CSS layout.

---

## 👩‍💻 Author

**Paramjeet Kaur**

*BCA Student | Aspiring Data Analyst*
