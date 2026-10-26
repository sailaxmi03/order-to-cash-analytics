Order-to-Cash Analytics Dashboard

Project Overview

An interactive analytics dashboard built using Python and Streamlit to analyze the Order-to-Cash (O2C) business process. It helps users explore orders, invoices, payments, shipments, and disputes through visualizations and key business insights.

Features

- Interactive regional filters
- Order value analysis by region
- Order status distribution
- Payment analysis
- Invoice status tracking
- Business insights through charts and metrics
- Synthetic datasets for demonstration

Technologies Used

- Python
- Pandas
- Streamlit
- Plotly
- CSV

Project Structure

order-to-cash-analytics/
├── data/
│   ├── accounts.csv
│   ├── disputes.csv
│   ├── invoices.csv
│   ├── orders.csv
│   ├── payments.csv
│   ├── quotes.csv
│   └── shipments.csv
├── app.py
├── generate_data.py
├── validate_data.py
├── README.md
└── .gitignore

How to Run the Project

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/order-to-cash-analytics.git
cd order-to-cash-analytics

Replace "YOUR_USERNAME" with your GitHub username.

2. Install the dependencies

python -m pip install streamlit pandas plotly

3. Run the dashboard

python -m streamlit run app.py

Data

This project uses synthetic sample data for demonstration and learning purposes.

Author

Sai Laxmi