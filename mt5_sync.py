import MetaTrader5 as mt5
import requests
import time
from datetime import datetime, timedelta

# ==========================================
# CONFIGURATION
# ==========================================

# Supabase Settings
SUPABASE_URL = SUPABASE_URL = "https://nkcbwkhntnwcwkqnlpah.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5rY2J3a2hudG53Y3drcW5scGFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYyMDczMDAsImV4cCI6MjA5MTc4MzMwMH0.mVGgdlrYar6nuUngCWok2Kd5F4X5IE6b2KcAgWQtrK0"
SUPABASE_TABLE = "trades"

# MT5 Settings (Optional: Leave empty if MT5 is already open and logged in)
MT5_LOGIN = None      # e.g., 12345678
MT5_PASSWORD = None   # e.g., "your_password"
MT5_SERVER = None     # e.g., "Broker-Server"

# How many days back to check for trades on each run
DAYS_TO_FETCH = 7

# ==========================================

def fetch_and_send_trades():
    # 1. Initialize MT5 connection
    if not mt5.initialize():
        print("MT5 initialization failed. Ensure MetaTrader 5 is installed and running.")
        return

    # Optional: Login if credentials are provided
    if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
        authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
        if not authorized:
            print(f"MT5 login failed, error code: {mt5.last_error()}")
            return

    # 2. Fetch Deals (Trades)
    now = datetime.now()
    from_date = now - timedelta(days=DAYS_TO_FETCH)
    
    deals = mt5.history_deals_get(from_date, now)
    if deals is None:
        print("No deals found or failed to fetch history.")
        return

    formatted_trades = []
    
    # 3. Process Deals
    for deal in deals:
        # We only care about DEAL_ENTRY_OUT (which represents a closed trade/exit)
        if deal.entry == mt5.DEAL_ENTRY_OUT:
            
            trade_data = {
                "position_id": deal.position_id, # Use this as Primary Key in Supabase
                "symbol": deal.symbol,
                "exit_price": deal.price,
                "profit": deal.profit,
                "time": datetime.fromtimestamp(deal.time).isoformat(),
            }
            
            # To get the entry price, we must find the DEAL_ENTRY_IN for the same position
            position_deals = mt5.history_deals_get(position=deal.position_id)
            if position_deals:
                for p_deal in position_deals:
                    if p_deal.entry == mt5.DEAL_ENTRY_IN:
                        trade_data["entry_price"] = p_deal.price
                        break
            
            # Fallback if entry price wasn't found
            if "entry_price" not in trade_data:
                trade_data["entry_price"] = 0.0

            formatted_trades.append(trade_data)

    if not formatted_trades:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No closed trades found in the last {DAYS_TO_FETCH} days.")
        return

    # 4. Send to Supabase
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        # Prefer resolution=merge-duplicates ensures we don't insert the same trade twice
        # (Requires 'position_id' to be set as a Primary Key or Unique constraint in Supabase)
        "Prefer": "resolution=merge-duplicates" 
    }

    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    
    try:
        response = requests.post(url, json=formatted_trades, headers=headers)
        if response.status_code in [200, 201]:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Successfully synced {len(formatted_trades)} trades to Supabase.")
        else:
            print(f"Failed to send data to Supabase: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")

def main():
    print("Starting MT5 to Supabase sync script...")
    print("Press Ctrl+C to stop.")
    
    while True:
        fetch_and_send_trades()
        # Wait 60 seconds before running again
        time.sleep(60)

if __name__ == "__main__":
    main()
