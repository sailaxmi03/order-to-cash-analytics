import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Order-to-Cash Analytics",
    page_icon="📊",
    layout="wide"
)

DATA_DIR = Path(__file__).parent / "data"

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    filenames = {
        "Accounts": "accounts.csv",
        "Quotes": "quotes.csv",
        "Orders": "orders.csv",
        "Shipments": "shipments.csv",
        "Invoices": "invoices.csv",
        "Payments": "payments.csv",
        "Disputes": "disputes.csv",
    }

    datasets = {}

    for name, filename in filenames.items():
        path = DATA_DIR / filename

        if path.exists():
            datasets[name] = pd.read_csv(path)

    return datasets


datasets = load_data()

# ---------------- HEADER ----------------
st.title("📊 Order-to-Cash Analytics Dashboard")
st.caption(
    "Monitor orders, invoices, payments, customer accounts, and disputes."
)

if not datasets:
    st.error("No CSV files found. Check your project's data folder.")
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.header("Dashboard Filters")

if "Accounts" in datasets and "region" in datasets["Accounts"].columns:
    regions = sorted(
        datasets["Accounts"]["region"].dropna().astype(str).unique()
    )

    selected_regions = st.sidebar.multiselect(
        "Select customer regions",
        regions,
        default=regions
    )
else:
    selected_regions = []

# ---------------- DATASETS ----------------
accounts = datasets.get("Accounts", pd.DataFrame()).copy()
quotes = datasets.get("Quotes", pd.DataFrame()).copy()
orders = datasets.get("Orders", pd.DataFrame()).copy()
shipments = datasets.get("Shipments", pd.DataFrame()).copy()
invoices = datasets.get("Invoices", pd.DataFrame()).copy()
payments = datasets.get("Payments", pd.DataFrame()).copy()
disputes = datasets.get("Disputes", pd.DataFrame()).copy()

# ---------------- REGION FILTERING ----------------

# Identify account IDs belonging to selected regions
if "region" in accounts.columns and "account_id" in accounts.columns:

    if selected_regions:
        accounts = accounts[
            accounts["region"].astype(str).isin(selected_regions)
        ].copy()

        selected_account_ids = set(
            accounts["account_id"].astype(str)
        )
    else:
        accounts = accounts.iloc[0:0].copy()
        selected_account_ids = set()

    # Filter quotes by account
    if "account_id" in quotes.columns:
        quotes = quotes[
            quotes["account_id"].astype(str).isin(
                selected_account_ids
            )
        ].copy()

    # Filter orders by account, when supported
    if "account_id" in orders.columns:
        orders = orders[
            orders["account_id"].astype(str).isin(
                selected_account_ids
            )
        ].copy()

    # Filter invoices through their related orders
    if "order_id" in invoices.columns and "order_id" in orders.columns:
        selected_order_ids = set(orders["order_id"].astype(str))

        invoices = invoices[
            invoices["order_id"].astype(str).isin(
                selected_order_ids
            )
        ].copy()

    # Filter payments through their related invoices
    if "invoice_id" in payments.columns and "invoice_id" in invoices.columns:
        selected_invoice_ids = set(
            invoices["invoice_id"].astype(str)
        )

        payments = payments[
            payments["invoice_id"].astype(str).isin(
                selected_invoice_ids
            )
        ].copy()

    # Filter shipments through their related orders
    if "order_id" in shipments.columns and "order_id" in orders.columns:
        selected_order_ids = set(orders["order_id"].astype(str))

        shipments = shipments[
            shipments["order_id"].astype(str).isin(
                selected_order_ids
            )
        ].copy()

    # Filter disputes through their related invoices
    if "invoice_id" in disputes.columns and "invoice_id" in invoices.columns:
        selected_invoice_ids = set(
            invoices["invoice_id"].astype(str)
        )

        disputes = disputes[
            disputes["invoice_id"].astype(str).isin(
                selected_invoice_ids
            )
        ].copy()

# ---------------- HELPER FUNCTIONS ----------------
def money(value):
    return f"{value:,.2f}"

def numeric_total(df, column):
    if column and column in df.columns:
        return pd.to_numeric(df[column], errors="coerce").fillna(0).sum()
    return 0.0

def find_column(df, candidates):
    for column in candidates:
        if column in df.columns:
            return column
    return None

invoice_amount_col = find_column(
    invoices, ["invoice_amount", "amount", "total_amount", "invoice_total"]
)

payment_amount_col = find_column(
    payments, ["payment_amount", "amount", "paid_amount"]
)

invoice_status_col = find_column(
    invoices, ["status", "invoice_status", "payment_status"]
)

# ---------------- KPI METRICS ----------------
st.subheader("Business Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Customer Accounts", f"{len(accounts):,}")
c2.metric("Total Orders", f"{len(orders):,}")
c3.metric("Total Invoices", f"{len(invoices):,}")
c4.metric("Total Disputes", f"{len(disputes):,}")

c5, c6, c7 = st.columns(3)

invoice_total = numeric_total(invoices, invoice_amount_col)
payment_total = numeric_total(payments, payment_amount_col)

average_invoice = (
    invoice_total / len(invoices)
    if len(invoices) > 0
    else 0.0
)

# Identify successful payment records where status is available
payment_status_col = find_column(
    payments,
    ["payment_status", "status"]
)

if payment_status_col:
    successful_statuses = [
        "recorded",
        "paid",
        "successful",
        "completed",
        "settled"
    ]

    successful_payments = payments[
        payments[payment_status_col]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(successful_statuses)
    ].copy()

    collected_amount = numeric_total(
        successful_payments,
        payment_amount_col
    )
else:
    collected_amount = payment_total

collection_rate = (
    collected_amount / invoice_total * 100
    if invoice_total > 0
    else 0.0
)

c5.metric("Invoice Value", money(invoice_total))
c6.metric("Payment Value", money(payment_total))
c7.metric("Average Invoice Value", money(average_invoice))

c8, c9 = st.columns(2)

c8.metric(
    "Recorded Collection Value",
    money(collected_amount)
)

c9.metric(
    "Collection Rate",
    f"{collection_rate:.2f}%"
)


st.caption(
    "Financial values use the amount columns available in your generated CSV files. "
    "Confirm the currency and payment-to-invoice relationships before interpreting them."
)

st.divider()

# ---------------- CHARTS ----------------
st.subheader("📈 Business Insights")

left, right = st.columns(2)

with left:
    st.markdown("#### Orders by Region")

    if "region" in accounts.columns:
        region_counts = (
            accounts.groupby("region")
            .size()
            .reset_index(name="Customer Accounts")
        )

        fig = px.bar(
            region_counts,
            x="region",
            y="Customer Accounts",
            labels={"region": "Region"},
            color="region",
            title="Customer Accounts by Region"
        )

        st.plotly_chart(fig, width="stretch")
    else:
        st.info("A region column is not available in the accounts dataset.")

with right:
    st.markdown("#### Invoice Amount Distribution")

    if invoice_amount_col:
        chart_data = invoices.copy()
        chart_data[invoice_amount_col] = pd.to_numeric(
            chart_data[invoice_amount_col], errors="coerce"
        )
        chart_data = chart_data.dropna(subset=[invoice_amount_col])

        if not chart_data.empty:
            fig = px.histogram(
                chart_data,
                x=invoice_amount_col,
                nbins=20,
                title="Distribution of Invoice Amounts",
                labels={invoice_amount_col: "Invoice Amount"}
            )

            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No valid invoice amounts are available.")
    else:
        st.info("No recognizable invoice amount column was found.")
# ---------------- ORDER ANALYSIS ----------------
st.divider()
st.subheader("📦 Order Analysis")

# Connect orders with customer accounts to analyze regional performance
if (
    "account_id" in orders.columns
    and "account_id" in accounts.columns
    and "region" in accounts.columns
):
    regional_orders = orders.merge(
        accounts[["account_id", "region"]],
        on="account_id",
        how="inner"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Order Value by Region")

        if "order_amount" in regional_orders.columns:
            regional_orders["order_amount"] = pd.to_numeric(
                regional_orders["order_amount"],
                errors="coerce"
            )

            order_values = (
                regional_orders.groupby("region", as_index=False)
                ["order_amount"]
                .sum()
            )

            fig = px.bar(
                order_values,
                x="region",
                y="order_amount",
                color="region",
                title="Total Order Value by Region",
                labels={
                    "region": "Customer Region",
                    "order_amount": "Total Order Value"
                }
            )

            st.plotly_chart(fig, width="stretch")
        else:
            st.info("The order_amount column was not found.")

    with col2:
            st.markdown("### Order Status Analysis")

            if "order_status" in orders.columns:
                status_counts = (
                    orders["order_status"]
                    .fillna("Unknown")
                    .astype(str)
                    .str.strip()
                    .value_counts()
                    .rename_axis("Order Status")
                    .reset_index(name="Number of Orders")
                )

                fig = px.pie(
                    status_counts,
                    names="Order Status",
                    values="Number of Orders",
                    title="Orders by Status",
                    hole=0.45
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("The order status column was not found.")
        
else:
    st.info(
        "Regional order analysis requires account_id in both datasets "
        "and region in the accounts dataset."
    )
# ---------------- PAYMENT ANALYSIS ----------------
st.divider()
st.subheader("💰 Payment Analysis")

left, right = st.columns(2)

with left:
    st.markdown("#### Payment Amounts")

    if payment_amount_col:
        payment_data = payments.copy()
        payment_data[payment_amount_col] = pd.to_numeric(
            payment_data[payment_amount_col], errors="coerce"
        )

        fig = px.histogram(
            payment_data.dropna(subset=[payment_amount_col]),
            x=payment_amount_col,
            nbins=20,
            title="Distribution of Payment Amounts"
        )

        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No recognizable payment amount column was found.")

with right:
    st.markdown("#### Invoice Status")

    if invoice_status_col:
        status_data = (
            invoices[invoice_status_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Invoices")
        )

        fig = px.pie(
            status_data,
            names="Status",
            values="Invoices",
            title="Invoices by Status",
            hole=0.4
        )

        st.plotly_chart(fig, width="stretch")
    else:
        st.info(
            "No invoice status column was found. "
            "Check your invoices.csv column names."
        )

# ---------------- OVERDUE INVOICE ANALYSIS ----------------
st.divider()
st.subheader("⏰ Overdue Invoice Analysis")

due_date_col = find_column(invoices, ["due_date"])
paid_date_col = find_column(
    invoices, ["paid_date", "payment_date", "date_paid"]
)
invoice_date_col = find_column(
    invoices, ["invoice_date", "issue_date", "created_at"]
)

if due_date_col:
    overdue_data = invoices.copy()

    overdue_data[due_date_col] = pd.to_datetime(
        overdue_data[due_date_col], errors="coerce"
    )

    today = pd.Timestamp.now().normalize()

    overdue_mask = overdue_data[due_date_col] < today

    if paid_date_col:
        overdue_data[paid_date_col] = pd.to_datetime(
            overdue_data[paid_date_col], errors="coerce"
        )
        overdue_mask &= overdue_data[paid_date_col].isna()
    elif invoice_status_col:
        status = (
            overdue_data[invoice_status_col]
            .fillna("")
            .astype(str)
            .str.lower()
        )
        overdue_mask &= ~status.isin(
            ["paid", "complete", "completed", "settled"]
        )
    else:
        st.caption(
            "Without a payment date or invoice status, overdue invoices "
            "cannot be reliably distinguished from invoices already paid."
        )

    overdue_data = overdue_data[overdue_mask].copy()

    st.metric("Potential Overdue Invoices", f"{len(overdue_data):,}")

    if invoice_amount_col:
        overdue_total = numeric_total(overdue_data, invoice_amount_col)
        st.metric("Potential Overdue Value", money(overdue_total))

    if not overdue_data.empty:
        st.dataframe(overdue_data, width="stretch")
    else:
        st.success("No overdue invoices matched the available data.")
else:
    st.info("The invoices dataset does not contain a due_date column.")

# ---------------- DATA EXPLORER ----------------
st.divider()
st.subheader("🔎 Explore Your Data")

selected_dataset = st.selectbox(
    "Choose a dataset",
    list(datasets.keys())
)

selected_df = datasets[selected_dataset]

if selected_dataset == "Accounts" and "region" in selected_df.columns:
    if selected_regions:
        selected_df = selected_df[
            selected_df["region"].astype(str).isin(selected_regions)
        ]

search_text = st.text_input("Search the selected dataset")

if search_text:
    mask = selected_df.astype(str).apply(
        lambda column: column.str.contains(
            search_text, case=False, na=False
        )
    ).any(axis=1)

    selected_df = selected_df[mask]

st.write(f"Showing {len(selected_df):,} rows")
st.dataframe(selected_df, width="stretch", hide_index=True)

st.download_button(
    label="⬇️ Download Selected Dataset",
    data=selected_df.to_csv(index=False),
    file_name=f"{selected_dataset.lower()}.csv",
    mime="text/csv"
)

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "Order-to-Cash Analytics | Built with Python, Pandas, Plotly, and Streamlit"
)
# ---------------- ADVANCED FINANCIAL ANALYSIS ----------------
st.divider()
st.header("📊 Advanced Financial Analysis")

# Prepare invoice data
invoice_analysis = invoices.copy()

if "due_date" in invoice_analysis.columns:
    invoice_analysis["due_date"] = pd.to_datetime(
        invoice_analysis["due_date"], errors="coerce"
    )

    invoice_analysis["invoice_month"] = (
        invoice_analysis["due_date"].dt.to_period("M").astype(str)
    )

    monthly_invoices = (
        invoice_analysis.dropna(subset=["due_date"])
        .groupby("invoice_month", as_index=False)["invoice_amount"]
        .sum()
    )

    st.subheader("📈 Monthly Invoice Trends")

    if not monthly_invoices.empty:
        fig = px.line(
            monthly_invoices,
            x="invoice_month",
            y="invoice_amount",
            markers=True,
            title="Invoice Amount by Month",
            labels={
                "invoice_month": "Month",
                "invoice_amount": "Invoice Amount"
            }
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No valid invoice dates available.")

# Payment collection analysis
st.subheader("💰 Payment Collection Analysis")

payment_analysis = payments.copy()

if "payment_status" in payment_analysis.columns:
    payment_analysis["payment_status"] = (
        payment_analysis["payment_status"].astype(str).str.strip()
    )

    payment_summary = (
        payment_analysis.groupby("payment_status", as_index=False)
        ["payment_amount"].sum()
    )

    fig = px.bar(
        payment_summary,
        x="payment_status",
        y="payment_amount",
        color="payment_status",
        title="Payment Amount by Status",
        labels={
            "payment_status": "Payment Status",
            "payment_amount": "Payment Amount"
        }
    )

    st.plotly_chart(fig, width="stretch")

# ---------------- OUTSTANDING INVOICE ANALYSIS ----------------
# ---------------- INVOICE AGING ANALYSIS ----------------
st.divider()
st.subheader("📅 Invoice Aging Analysis")

if "due_date" in invoices.columns:

    aging_data = invoices.copy()

    aging_data["due_date"] = pd.to_datetime(
        aging_data["due_date"],
        errors="coerce"
    )

    today = pd.Timestamp.now().normalize()

    # Identify unpaid invoices
    if "invoice_status" in aging_data.columns:
        unpaid_mask = (
            ~aging_data["invoice_status"]
            .fillna("")
            .astype(str)
            .str.lower()
            .isin(["paid", "completed", "settled"])
        )
    else:
        unpaid_mask = pd.Series(
            True,
            index=aging_data.index
        )

    # Calculate days overdue
    aging_data["days_overdue_calculated"] = (
        today - aging_data["due_date"]
    ).dt.days

    overdue_data = aging_data[
        unpaid_mask
        & (aging_data["days_overdue_calculated"] > 0)
    ].copy()

    overdue_data["Aging Category"] = pd.cut(
        overdue_data["days_overdue_calculated"],
        bins=[0, 30, 60, 90, float("inf")],
        labels=["0–30 days", "31–60 days", "61–90 days", "90+ days"],
        include_lowest=True
    )

    st.metric(
        "Overdue Invoices",
        f"{len(overdue_data):,}"
    )

    if not overdue_data.empty:

        aging_summary = (
            overdue_data.groupby(
                "Aging Category",
                observed=False
            )
            .size()
            .reset_index(name="Invoice Count")
        )

        fig = px.bar(
            aging_summary,
            x="Aging Category",
            y="Invoice Count",
            color="Aging Category",
            title="Overdue Invoices by Aging Category"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

        st.dataframe(
            overdue_data,
            width="stretch",
            hide_index=True
        )

    else:
        st.success("No overdue invoices found.")

else:
    st.info(
        "The invoices dataset does not contain a due_date column."
    )