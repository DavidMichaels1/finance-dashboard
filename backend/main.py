from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import pandas as pd
from analytics import monthly_totals, spending_by_category, month_on_month_change, load_clean_data

# --- Create the FastAPI app ---
# Think of this as the "main hub" that all your API routes attach to
app = FastAPI()

# --- CORS setup ---
# CORS (Cross-Origin Resource Sharing) allows your React frontend
# to talk to this API even though they run on different ports.
# Without this, the browser would block the requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's default port
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database connection ---
engine = create_engine("sqlite:///../data/finance.db")

# --- Routes ---
# Each @app.get() defines a URL endpoint.
# When React calls that URL, the function below it runs and returns data.

@app.get("/")
def root():
    """Health check — confirms the API is running."""
    return {"status": "ok", "message": "Finance Dashboard API"}

@app.get("/transactions")
def get_transactions():
    """Returns all cleaned transactions."""
    df = load_clean_data(engine)
    # .to_dict("records") converts the DataFrame into a list of dictionaries
    # e.g. [{"date": "2024-01-03", "amount": -850.0, ...}, ...]
    # This is the JSON format React expects
    return df.to_dict("records")

@app.get("/summary/monthly")
def get_monthly_summary():
    """Returns total income, spending, and net per month."""
    df = load_clean_data(engine)
    return monthly_totals(df).to_dict("records")

@app.get("/summary/categories")
def get_category_summary():
    """Returns spending broken down by category and month."""
    df = load_clean_data(engine)
    return spending_by_category(df).to_dict("records")

@app.get("/summary/trends")
def get_trends():
    """Returns month-on-month spending change."""
    df = load_clean_data(engine)
    return month_on_month_change(df).to_dict("records")