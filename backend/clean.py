import pandas as pd
from sqlalchemy import create_engine, text

# --- Category rules ---
# This is a dictionary where each key is a category name,
# and the value is a list of keywords to look for in the description.
# If a transaction description contains any of these keywords,
# it gets assigned that category.
CATEGORY_RULES = {
    "groceries":     ["woolworths", "checkers", "pick n pay", "spar", "food lover"],
    "eating out":    ["uber eats", "mr delivery", "restaurant", "café", "kfc", "mcdonalds"],
    "transport":     ["uber", "bolt", "fuel", "parking", "toll"],
    "entertainment": ["netflix", "spotify", "showmax", "steam", "cinema"],
    "utilities":     ["electricity", "water", "rates", "internet", "telkom"],
    "health":        ["gym", "pharmacy", "clicks", "dischem", "doctor"],
    "income":        ["salary", "deposit", "payment received"],
}

def categorise(description: str) -> str:
    """
    Takes a transaction description string and returns a category.
    If no keyword matches, returns "other".
    """
    # .lower() converts to lowercase so "WOOLWORTHS" matches "woolworths"
    desc = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in desc:
                return category
    return "other"

def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a raw transactions DataFrame and returns a cleaned version.
    """
    # 1. Drop any rows where critical fields are missing
    df = df.dropna(subset=["date", "amount", "description"])

    # 2. Remove duplicate rows (same date, description, and amount)
    df = df.drop_duplicates(subset=["date", "description", "amount"])

    # 3. Clean up description text — strip extra whitespace
    df["description"] = df["description"].str.strip()

    # 4. Make sure amount is a number (not a string)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # 5. Add a category column using our categorise function
    # .apply() runs the function once for every row in the column
    df["category"] = df["description"].apply(categorise)

    # 6. Add a month column — useful for grouping later (e.g. "2024-01")
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

    return df

# --- Run the cleaning pipeline ---
if __name__ == "__main__":
    engine = create_engine("sqlite:///data/finance.db")

    # Load raw transactions from the database
    df = pd.read_sql("SELECT * FROM transactions", engine)
    print(f"Loaded {len(df)} raw transactions")

    # Clean and categorise
    df_clean = clean_transactions(df)

    # Preview the result
    print("\nCleaned data preview:")
    print(df_clean[["date", "description", "amount", "category", "month"]].to_string())

    # Save cleaned data to a new table in the database
    df_clean.to_sql("transactions_clean", engine, if_exists="replace", index=False)
    print(f"\nSaved {len(df_clean)} cleaned transactions to 'transactions_clean' table")

    # Show category breakdown
    print("\nSpend by category:")
    summary = df_clean[df_clean["amount"] < 0].groupby("category")["amount"].sum()
    print(summary.sort_values())