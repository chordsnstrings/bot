import streamlit as st
from binance_bot import (
    start_grid_bot, cancel_grid_orders, get_open_grid_orders,
    get_grid_pnl, get_all_symbols, calculate_entry_grid_params
)

st.set_page_config(page_title="Binance Grid Bot", layout="centered")
st.title("📈 Binance Futures Grid Trading Bot")

# --- INPUTS ---
st.subheader("Step 1: Auto Parameters")
with st.form("auto_params"):
    capital = st.number_input("Capital (USDT)", value=100.0)
    leverage = st.number_input("Leverage", value=20)
    range_pct = st.number_input("Grid Range %", value=30)
    submitted_auto = st.form_submit_button("Auto Calculate")

# Load symbols once
symbols = get_all_symbols()

st.subheader("Step 2: Bot Parameters")
with st.form("bot_params"):
    symbol = st.selectbox("Trading Pair", options=symbols)
    side = st.selectbox("Grid Direction", ["BUY", "SELL"])
    entry_price = st.number_input("Entry Price")
    grid_spacing = st.number_input("Grid Spacing (%)")
    grid_size = st.number_input("Grid Size (No. of Orders)", step=1, format="%d")
    quantity = st.number_input("Quantity per Order")
    submit_bot = st.form_submit_button("Create Bot")

if submitted_auto:
    current_price, spacing, size, qty = calculate_entry_grid_params(
        capital, leverage, range_pct, side="BUY", symbol="BTCUSDT"
    )
    st.success(f"Auto: Entry {current_price:.2f}, Spacing {spacing:.2f}%, Size {size}, Qty {qty}")

if submit_bot:
    result = start_grid_bot(symbol, side, entry_price, grid_spacing, int(grid_size), quantity)
    if result["status"] == "success":
        st.success("Grid Bot started")
    else:
        st.error(result.get("error", "Unknown Error"))

# --- OPEN ORDERS ---
st.subheader("📊 Active Grid Orders")
symbol_sel = st.selectbox("View Orders For Symbol", options=symbols, key="symbol_sel")
side_sel = st.selectbox("Side", ["BUY", "SELL"], key="side_sel")

if st.button("Cancel All Orders"):
    result = cancel_grid_orders(symbol_sel, side_sel)
    if result["status"] == "success":
        st.success("Orders cancelled")
    else:
        st.error("Cancel failed")

orders = get_open_grid_orders(symbol_sel, side_sel)
if orders:
    st.table(orders)
else:
    st.info("No open orders found.")

# --- PNL ---
st.subheader("💹 PnL Tracker")
if st.button("Refresh PnL"):
    result = get_grid_pnl(symbol_sel, side_sel)
    if result["status"] == "success":
        st.metric("Estimated PnL", f"{result['pnl']:.2f} USDT")
    else:
        st.error("Unable to fetch PnL")