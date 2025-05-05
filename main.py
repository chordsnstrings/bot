import streamlit as st
from binance_bot import start_grid_bot, cancel_grid_orders, get_open_grid_orders, get_grid_pnl, get_wallet_balance

st.set_page_config(page_title="Grid Trading Bot", layout="wide")
st.title("Binance Futures Grid Bot")

symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT"]
sides = ["BUY", "SELL"]

# Sidebar inputs
with st.sidebar:
    st.header("Bot Configuration")
    symbol = st.selectbox("Symbol", symbols)
    side = st.selectbox("Side", sides)
    entry_price = st.number_input("Entry Price", min_value=0.0, value=25000.0, step=0.1)
    grid_spacing = st.number_input("Grid Spacing (%)", min_value=0.01, value=0.5, step=0.01)
    grid_size = st.number_input("Grid Size (Number of Orders)", min_value=1, value=10, step=1)
    quantity = st.number_input("Quantity per Order", min_value=0.0, value=0.001, step=0.0001)

    if st.button("Start Grid Bot"):
        result = start_grid_bot(symbol, side, entry_price, grid_spacing, grid_size, quantity)
        if result["status"] == "success":
            st.success("Grid Bot Started. Orders placed.")
        else:
            st.error(f"Error: {result['error']}")

    if st.button("Cancel Grid Orders"):
        result = cancel_grid_orders(symbol, side)
        if result["status"] == "success":
            st.success("Orders cancelled successfully.")
        else:
            st.error("Failed to cancel orders.")

    if st.button("Refresh Wallet"):
        balances = get_wallet_balance()
        for asset, info in balances.items():
            st.write(f"{asset}: {info['balance']} (Unrealized PnL: {info['unrealizedPnL']})")

# Main content
st.subheader(f"Active Grid Orders: {symbol} - {side}")
open_orders = get_open_grid_orders(symbol, side)
if open_orders:
    st.table(open_orders)
else:
    st.info("No active grid orders.")

if st.button("Calculate PnL"):
    result = get_grid_pnl(symbol, side)
    if result["status"] == "success":
        pnl = result["pnl"]
        st.success(f"Grid PnL for {symbol} {side}: {pnl:.2f} USDT")
    else:
        st.error("Failed to calculate PnL")