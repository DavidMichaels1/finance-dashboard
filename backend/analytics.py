import pandas as pd
from sqlalchemy import create_engine

def load_clean_data(engine):
    """Load the cleaned transactions table into a DataFrame."""
    return pd.read_sql("SELECT * FROM transactions_clean", engine)

def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns total spending and income per month.
    We split debits (spending) and credits (income) separately.
    """
    # Filter to debits only (negative amounts = money going out)
    spending = (
        df[df["amount"] < 0]
        .groupby("month")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "total_spent"})
    )

    # Filter to credits only (positive amounts = money coming in)
    income = (
        df[df["amount"] > 0]
        .groupby("month")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "total_income"})
    )

    # Merge the two together on the month column
    summary = pd.merge(spending, income, on="month", how="outer").fillna(0)

    # Calculate net (income - spending)
    # abs() converts negative spending to positive for easier reading
    summary["net"] = summary["total_income"] + summary["total_spent"]

    return summary

def spending_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns spending broken down by category and month.
    This powers the category chart on the dashboard.
    """
    return (
        df[df["amount"] < 0]
        .groupby(["month", "category"])["amount"]
        .sum()
        .abs()  # Convert to positive numbers for easier charting
        .reset_index()
        .rename(columns={"amount": "spent"})
        .sort_values(["month", "spent"], ascending=[True, False])
    )

def month_on_month_change(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the percentage change in total spending month over month.
    Useful for spotting trends.
    """
    totals = monthly_totals(df)[["month", "total_spent"]].copy()
    totals["total_spent"] = totals["total_spent"].abs()

    # .pct_change() calculates the % difference from the previous row
    totals["change_pct"] = totals["total_spent"].pct_change() * 100
    totals["change_pct"] = totals["change_pct"].round(1)

    return totals

# --- Run analytics and print results ---
if __name__ == "__main__":
    engine = create_engine("sqlite:///data/finance.db")
    df = load_clean_data(engine)

    print("=== Monthly totals ===")
    print(monthly_totals(df).to_string(index=False))

    print("\n=== Spending by category ===")
    print(spending_by_category(df).to_string(index=False))

    print("\n=== Month-on-month change ===")
    print(month_on_month_change(df).to_string(index=False))