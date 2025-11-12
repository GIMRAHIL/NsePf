# portfolio_nselib.py
import streamlit as st
import pandas as pd
from nselib import capital_market
from datetime import datetime

st.set_page_config(page_title="NSE Portfolio Tracker", layout="wide")
st.title("📊 NSE Portfolio Tracker (using nselib)")

# Sidebar portfolio input
st.sidebar.header("Portfolio")
portfolio_text = st.sidebar.text_area(
    "Enter your holdings (symbol,shares,cost):",
    "RELIANCE,10,2400\nTCS,5,3500\nINFY,8,1400",
    height=100
)

date_str = st.sidebar.text_input("Bhavcopy Date (dd-mm-yyyy):", datetime.now().strftime("%d-%m-%Y"))

def parse_portfolio(text):
    rows = []
    for line in text.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 2:
            rows.append({
                "symbol": parts[0].upper(),
                "shares": float(parts[1]),
                "cost": float(parts[2]) if len(parts) > 2 else None
            })
    return pd.DataFrame(rows)

df_portfolio = parse_portfolio(portfolio_text)

if st.sidebar.button("Fetch NSE Data"):
    try:
        bhav = capital_market.bhav_copy_with_delivery(date_str)
        bhav = bhav[["SYMBOL", "CLOSE_PRICE", "DELIV_QTY", "DELIV_PER"]].rename(columns={
            "SYMBOL": "symbol",
            "CLOSE_PRICE": "last_price",
            "DELIV_QTY": "delivery_qty",
            "DELIV_PER": "delivery_per"
        })
        merged = pd.merge(df_portfolio, bhav, on="symbol", how="left")
        merged["market_value"] = merged["last_price"] * merged["shares"]
        merged["p_l"] = (merged["last_price"] - merged["cost"]) * merged["shares"]
        merged["p_l_pct"] = (merged["p_l"] / (merged["cost"] * merged["shares"])) * 100

        st.subheader("Portfolio Summary")
        st.dataframe(merged)

        total_mv = merged["market_value"].sum()
        total_cost = (merged["cost"] * merged["shares"]).sum()
        total_pl = total_mv - total_cost
        st.markdown(f"**Total Portfolio Value:** ₹{total_mv:,.2f}")
        st.markdown(f"**Total Profit/Loss:** ₹{total_pl:,.2f} ({(total_pl/total_cost*100):.2f}%)")

        # Export CSV
        csv_data = merged.to_csv(index=False)
        st.download_button("Download Portfolio CSV", csv_data, "portfolio_summary.csv", "text/csv")

    except Exception as e:
        st.error(f"Error fetching NSE data: {e}")
