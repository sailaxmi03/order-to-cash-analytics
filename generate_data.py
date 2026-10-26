import pandas as pd
import random 
import numpy as np
from pathlib import Path

# Fixed seed makes the data reproducible
SEED = 20261022
rng = np.random.default_rng(SEED)

# Create output folder
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Generate master data
def generate_data():
    accounts = pd.DataFrame({
        "account_id": [f"ACC-{i:06d}" for i in range(1, 501)],
        "account_name": [f"Customer {i}" for i in range(1, 501)],
        "region": rng.choice(
            ["North", "South", "East", "West"], 500
        ),
    })

    quotes = pd.DataFrame({
        "quote_id": [f"QTE-2026-{i:06d}" for i in range(1, 1001)],
        "account_id": rng.choice(accounts["account_id"], 1000),
        "quote_amount": rng.integers(1000, 100000, 1000),
        "status": rng.choice(
            ["Accepted", "Rejected", "Pending"], 1000,
            p=[0.60, 0.25, 0.15]
        ),
    })

    orders = quotes[quotes["status"] == "Accepted"].copy()
    orders = orders.reset_index(drop=True)
    orders["order_id"] = [
        f"SO-2026-{i:06d}" for i in range(1, len(orders) + 1)
    ]
    orders["order_amount"] = orders["quote_amount"]
    orders["order_status"] = rng.choice(
    ["Open", "Completed", "Cancelled", "Processing"],
    size = len(orders),
    p=[0.40, 0.35, 0.10, 0.15],
    
)

    shipments = pd.DataFrame({
        "shipment_id": [
            f"SHP-2026-{i:06d}" for i in range(1, len(orders) + 1)
        ],
        "order_id": orders["order_id"],
        "shipped_quantity": rng.integers(1, 101, len(orders)),
        "shipment_status": rng.choice(
            ["Shipped", "Partial", "Pending"], len(orders)
        ),
    })

    invoices = pd.DataFrame({
        "invoice_id": [
            f"INV-2026-{i:06d}" for i in range(1, 801)
        ],
        "order_id": rng.choice(orders["order_id"], 800),
        "invoice_amount": rng.integers(1000, 100000, 800),
        "paid_amount": 0,
        "invoice_status": "Unpaid",
    })

    invoices["due_date"] = (
        pd.Timestamp("2026-10-26")
        + pd.to_timedelta(rng.integers(-60, 31, 800), unit="D")
    )

    invoices["days_overdue"] = (
        pd.Timestamp("2026-10-26") - invoices["due_date"]
    ).dt.days.clip(lower=0)

    invoices["outstanding_amount"] = invoices["invoice_amount"]

    payments = pd.DataFrame({
        "payment_id": [
            f"PAY-2026-{i:06d}" for i in range(1, 1501)
        ],
        "invoice_id": rng.choice(invoices["invoice_id"], 1500),
        "payment_amount": rng.integers(100, 50000, 1500),
        "payment_status": "Recorded",
    })

    disputes = pd.DataFrame({
        "dispute_id": [
            f"DSP-2026-{i:06d}" for i in range(1, 101)
        ],
        "invoice_id": rng.choice(invoices["invoice_id"], 100),
        "dispute_reason": rng.choice(
            ["Short Payment", "Incorrect Amount", "Duplicate Invoice"],
            100
        ),
        "dispute_status": rng.choice(
            ["Open", "Under Review", "Resolved"], 100
        ),
    })

    # Export CSV files
    datasets = {
        "accounts": accounts,
        "quotes": quotes,
        "orders": orders,
        "shipments": shipments,
        "invoices": invoices,
        "payments": payments,
        "disputes": disputes,
    }

    for name, df in datasets.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
        print(f"Created {name}.csv: {len(df)} rows")

    print("\nData generation completed!")

if __name__ == "__main__":
    generate_data()