import pandas as pd
from sqlalchemy import create_engine, text

# --- Load CSV ---
# pandas reads the CSV into a "DataFrame" — think of it as a smart spreadsheet in memory
df = pd.read_csv("data/transactions.csv")

# Convert the date column from plain text into actual date objects
# This lets us do date maths later (e.g. group by month)
df["date"] = pd.to_datetime(df["date"])

# Print the first 5 rows so we can see what we loaded
print("Loaded data:")
print(df.head())
print(f"\nTotal rows: {len(df)}")

# --- Connect to database ---
# SQLite stores everything in a single local file — perfect for development
# The file will be created automatically if it doesn't exist
engine = create_engine("sqlite:///data/finance.db")

# --- Write to database ---
# "replace" means: if the table already exists, wipe it and rewrite
# Useful while we're still building — we'll change this to "append" later
df.to_sql("transactions", engine, if_exists="replace", index=False)

print("\nData written to database successfully.")

# --- Verify it worked ---
# Read it back out to confirm
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM transactions"))
    count = result.scalar()
    print(f"Rows in database: {count}")