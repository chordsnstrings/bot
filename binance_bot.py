from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import math
import os

# HARDCODED API KEYS FOR INTERNAL USE
API_KEY = "QxJVB41f0kEbtpOP6b8v5M5W0Z1xb2Ud3S5fHVQe0c3JaVNalgENCGAkftRq24up"
API_SECRET = "6A4asBLA6pXRzpFPbWqLgRrfy0y52RPMvxNxfxFuSfynlGW4uOjHbuUYb5pNQhkG"

client = Client(API_KEY, API_SECRET)
client.FUTURES_URL = 'https://fapi.binance.com/fapi'

order_registry = {}

def get_precision(symbol):
    info = client.futures_exchange_info()
    for s in info['symbols']:
        if s['symbol'] == symbol:
            qty_precision = s['quantityPrecision']
            price_precision = s['pricePrecision']
            return qty_precision, price_precision
    return 3, 2

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def start_grid_bot(symbol, side, entry_price, grid_spacing, grid_size, quantity):
    try:
        side_enum = SIDE_BUY if side == "BUY" else SIDE_SELL
        open_orders = []
        qty_precision, price_precision = get_precision(symbol)

        for i in range(grid_size):
            spacing_pct = grid_spacing * i / 100
            if side == "BUY":
                price = entry_price * (1 - spacing_pct)
            else:
                price = entry_price * (1 + spacing_pct)

            price = round_down(price, price_precision)
            qty = round_down(quantity, qty_precision)

            order = client.futures_create_order(
                symbol=symbol,
                side=side_enum,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=qty,
                price=str(price)
            )
            open_orders.append(order)

        order_registry[(symbol, side)] = open_orders
        return {"status": "success"}

    except BinanceAPIException as e:
        return {"status": "error", "error": str(e)}

def cancel_grid_orders(symbol, side):
    try:
        orders = order_registry.get((symbol, side), [])
        for o in orders:
            try:
                client.futures_cancel_order(symbol=symbol, orderId=o['orderId'])
            except BinanceAPIException:
                pass
        order_registry[(symbol, side)] = []
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_open_grid_orders(symbol, side):
    try:
        side_enum = SIDE_BUY if side == "BUY" else SIDE_SELL
        all_orders = client.futures_get_open_orders(symbol=symbol)
        filtered = [
            {"orderId": o["orderId"], "price": o["price"], "qty": o["origQty"]}
            for o in all_orders if o["side"] == side_enum
        ]
        return filtered
    except Exception as e:
        return []

def get_grid_pnl(symbol, side):
    try:
        positions = client.futures_account()['positions']
        for p in positions:
            if p['symbol'] == symbol and float(p['positionAmt']) != 0:
                pnl = float(p['unrealizedProfit'])
                return {"status": "success", "pnl": pnl}
        return {"status": "success", "pnl": 0.0}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_wallet_balance():
    try:
        balances = client.futures_account_balance()
        pnl_map = {}
        for p in client.futures_account()['positions']:
            if float(p['positionAmt']) != 0:
                pnl_map[p['symbol']] = float(p['unrealizedProfit'])
        result = {}
        for b in balances:
            if float(b['balance']) > 0:
                result[b['asset']] = {
                    'balance': float(b['balance']),
                    'unrealizedPnL': pnl_map.get(b['asset'], 0.0)
                }
        return result
    except Exception as e:
        return {}