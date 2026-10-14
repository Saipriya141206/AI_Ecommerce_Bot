from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "orders.csv"


def get_order_status(order_id: str):
    if not order_id:
        return {"found": False, "message": "Please enter a valid order ID such as ORD1001."}

    orders = pd.read_csv(DATA_PATH)
    match = orders[orders["order_id"].str.lower() == order_id.lower()]

    if match.empty:
        return {
            "found": False,
            "message": f"Sorry, I could not find an order with ID {order_id}.",
        }

    row = match.iloc[0]
    return {
        "found": True,
        "order_id": row["order_id"],
        "customer": row["customer"],
        "product": row["product"],
        "status": row["status"],
        "expected_delivery": row["expected_delivery"],
    }
