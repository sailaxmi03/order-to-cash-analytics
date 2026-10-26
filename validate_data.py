import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")


def validate_data():
    print("\n===== ORDER-TO-CASH DATA VALIDATION =====\n")

    # Load datasets
    accounts = pd.read_csv(DATA_DIR / "accounts.csv")
    quotes = pd.read_csv(DATA_DIR / "quotes.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv")
    shipments = pd.read_csv(DATA_DIR / "shipments.csv")
    invoices = pd.read_csv(DATA_DIR / "invoices.csv")
    payments = pd.read_csv(DATA_DIR / "payments.csv")
    disputes = pd.read_csv(DATA_DIR / "disputes.csv")

    # 1. Check primary-key uniqueness
    datasets = {
        "Accounts": (accounts, "account_id"),
        "Quotes": (quotes, "quote_id"),
        "Orders": (orders, "order_id"),
        "Shipments": (shipments, "shipment_id"),
        "Invoices": (invoices, "invoice_id"),
        "Payments": (payments, "payment_id"),
        "Disputes": (disputes, "dispute_id"),
    }

    print("1. PRIMARY KEY VALIDATION")

    for name, (df, key) in datasets.items():
        duplicate_count = df[key].duplicated().sum()

        if duplicate_count == 0:
            print(f"PASS: {name} IDs are unique")
        else:
            print(f"FAIL: {name} has {duplicate_count} duplicate IDs")

    # 2. Check foreign-key relationships
    print("\n2. RELATIONSHIP VALIDATION")

    checks = [
        (
            "Quotes -> Accounts",
            quotes["account_id"],
            accounts["account_id"],
        ),
        (
            "Orders -> Quotes",
            orders["quote_id"],
            quotes["quote_id"],
        ),
        (
            "Shipments -> Orders",
            shipments["order_id"],
            orders["order_id"],
        ),
        (
            "Invoices -> Orders",
            invoices["order_id"],
            orders["order_id"],
        ),
        (
            "Payments -> Invoices",
            payments["invoice_id"],
            invoices["invoice_id"],
        ),
        (
            "Disputes -> Invoices",
            disputes["invoice_id"],
            invoices["invoice_id"],
        ),
    ]

    for name, child_ids, parent_ids in checks:
        missing = (~child_ids.isin(parent_ids)).sum()

        if missing == 0:
            print(f"PASS: {name}")
        else:
            print(f"FAIL: {name} has {missing} invalid references")

    # 3. Check financial amounts
    print("\n3. FINANCIAL VALIDATION")

    if (invoices["invoice_amount"] >= 0).all():
        print("PASS: Invoice amounts are non-negative")
    else:
        print("FAIL: Negative invoice amounts found")

    if (payments["payment_amount"] >= 0).all():
        print("PASS: Payment amounts are non-negative")
    else:
        print("FAIL: Negative payment amounts found")

    # 4. Check date consistency
    print("\n4. DATE VALIDATION")

    invoices["due_date"] = pd.to_datetime(invoices["due_date"])

    if invoices["due_date"].notna().all():
        print("PASS: All invoices have valid due dates")
    else:
        print("FAIL: Missing invoice due dates found")

    # 5. Summary
    print("\n5. DATASET SUMMARY")

    for name, (df, _) in datasets.items():
        print(f"{name}: {len(df)} rows")

    print("\nValidation completed.")


if __name__ == "__main__":
    validate_data()