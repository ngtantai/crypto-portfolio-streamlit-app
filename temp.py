import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import time
import sqlite3
import os
import uuid

# Set page configuration
st.set_page_config(layout="wide")

# Add custom CSS for global font and metric styling
st.markdown("""
    <style>
        /* Default font for all elements */
        .st-emotion-cache-1jicfl2 {
            margin-top: -5rem;    
        }
        html, body, [class*="css"], [class*="st-"], .stMarkdown, .stDataFrame, input, button {
            font-family: 'Tahoma' !important;
        }
        
        /* Specific styling for metrics */
        .css-1wivap2, .css-1i3tcqk {
            font-family: 'Tahoma' !important;
        }
        [data-testid="stMain"] {
            margin-left: -5rem;  
        }
            
        [data-testid="stSidebarUserContent"] {
            margin-top: 4.75rem;
            text-align: center;
        }
        /* Metric spacing */
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
            letter-spacing: 2px !important;
        }
        
        /* Specific styling for buttons */
        .stButton button {
            font-family: 'Tahoma' !important;
            transition: all 0.3s ease-in-out;
            padding: 5px 15px;
            border-radius: 5px;
            border: 1px solid #888888;
            background-color: black;
        }
        
        /* Hover effect */
        .stButton button:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 10px rgba(0,0,0,0.2);
            background-color: #f0f0f0;
            opacity: 0.7;
            color: black;
            font-weight: bold;
        }
        
        /* Active/Click effect */
        .stButton button:active {
            transform: translateY(0px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border: 1px solid white;
            color: white;
        }
            
        button[kind="primary"] {
            margin-left: 0rem;
            margin-top: 1rem;
            height: 50px;
            width: 100%;
        }
            
        button[kind="secondary"] {
            margin-left: 0rem;
            margin-top: 1rem;
            height: 75px;
            width: 100%;
            border-radius: 10px;
        }
            
        /* DataFrame styling */
        .stDataFrame {
            width: 100% !important;
        }
        
        [data-testid="stDataFrame"] > div {
            width: 100% !important;
        }
        
        [data-testid="stDataFrame"] > div > iframe {
            width: 100% !important;
        }
        
        .dataframe thead th {
            font-size: 20px !important;
            font-family: 'Tahoma' !important;
            text-align: center !important;
            padding: 10px !important;
        }
        
        .dataframe tbody td {
            font-size: 26px !important;
            font-family: 'Tahoma' !important;
            text-align: center !important;
            padding: 10px !important;
        }

        /* Live update indicator */
        .live-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: #00ff00;
            border-radius: 50%;
            margin-right: 5px;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)


# Rate limiter class for API calls
class RateLimiter:
    def __init__(self, max_calls, time_window):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_call(self):
        now = datetime.now()
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < timedelta(seconds=self.time_window)]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False

# Create rate limiter instance
price_limiter = RateLimiter(max_calls=50, time_window=60)

# Database functions
def get_db_path():
    """Get the absolute path for the database file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'crypto_transactions.db')

def init_database():
    """Initialize SQLite database and create table if it doesn't exist"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             date TEXT, 
             asset TEXT,
             symbol TEXT,
             quantity REAL,
             purchase_price REAL,
             total_cash_invested REAL,
             current_price REAL,
             profit_loss REAL)
        ''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    finally:
        conn.close()

def save_transaction(transaction_data):
    """Save a new transaction to the database"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO transactions 
            (date, asset, symbol, quantity, purchase_price, total_cash_invested, current_price, profit_loss)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_data['Date'],
            transaction_data['Asset'],
            transaction_data['Symbol'],
            transaction_data['Quantity'],
            transaction_data['Purchase Price'],
            transaction_data['Total Cash Invested'],
            transaction_data['Current Price'],
            transaction_data['Profit/Loss']
        ))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error saving transaction: {e}")
    finally:
        conn.close()

def load_transactions():
    """Load all transactions from the database"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()
        
        if not df.empty:
            df = df.rename(columns={
                'profit_loss': 'Profit/Loss',
                'date': 'Date',
                'asset': 'Asset',
                'symbol': 'Symbol',
                'quantity': 'Quantity',
                'purchase_price': 'Purchase Price',
                'total_cash_invested': 'Total Cash Invested',
                'current_price': 'Current Price'
            })
        return df
    except sqlite3.Error as e:
        st.error(f"Error loading transactions: {e}")
        return pd.DataFrame(
            columns=['id', 'Date', 'Asset', 'Symbol', 'Quantity', 'Purchase Price', 
                    'Total Cash Invested', 'Current Price', 'Profit/Loss']
        )

def delete_transaction(transaction_id):
    """Delete a specific transaction from the database"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error deleting transaction: {e}")
        return False
    finally:
        conn.close()

def clear_transactions():
    """Clear all transactions from the database"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM transactions")
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error clearing transactions: {e}")
    finally:
        conn.close()

# Session state management
def init_session_state():
    """Initialize all required session state variables"""
    if 'db_initialized' not in st.session_state:
        init_database()
        st.session_state.db_initialized = True
    
    if 'transactions' not in st.session_state:
        st.session_state.transactions = load_transactions()
    
    if 'current_prices' not in st.session_state:
        st.session_state.current_prices = {}
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()

# Price update function
def update_current_prices():
    """Update current prices for all cryptocurrencies in transactions"""
    if 'transactions' in st.session_state and not st.session_state.transactions.empty:
        for _, row in st.session_state.transactions.iterrows():
            try:
                current_price = get_current_price(row['Symbol'])
                if current_price:
                    st.session_state.current_prices[row['Symbol']] = current_price
            except Exception as e:
                st.error(f"Error updating price for {row['Symbol']}: {e}")


# API Functions
@st.cache_data(ttl=3600)
def fetch_available_coins():
    """Fetch list of available cryptocurrencies from CoinGecko"""
    try:
        response = requests.get('https://api.coingecko.com/api/v3/coins/list')
        if response.status_code == 200:
            coins = response.json()
            return {f"{coin['name']} ({coin['symbol'].upper()})": coin['id'] for coin in coins}
        return {}
    except Exception as e:
        st.error(f"Error fetching coin list: {e}")
        return {}

def get_current_price(coin_id):
    """Get current price with rate limiting and caching"""
    # Use cached price if rate limit is reached
    if not price_limiter.can_call():
        return st.session_state.current_prices.get(coin_id)
    
    try:
        response = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': coin_id, 'vs_currencies': 'usd'},
            timeout=5  # Add timeout to prevent hanging
        )
        if response.status_code == 200:
            price = response.json()[coin_id]['usd']
            st.session_state.current_prices[coin_id] = price
            return price
        return st.session_state.current_prices.get(coin_id)
    except Exception as e:
        st.error(f"Error fetching price: {e}")
        return st.session_state.current_prices.get(coin_id)

# Calculation Functions
def calculate_profit_loss(quantity, purchase_price, current_price):
    """Calculate profit/loss for a single transaction"""
    return (current_price - purchase_price) * quantity

def calculate_quantity(total_investment, purchase_price):
    """Calculate quantity based on total investment and purchase price"""
    return total_investment / purchase_price if purchase_price > 0 else 0

def calculate_total_investment(quantity, purchase_price):
    """Calculate total investment based on quantity and purchase price"""
    return quantity * purchase_price

# Display Functions
def display_live_indicator():
    """Display a live update indicator in the sidebar"""
    st.sidebar.markdown("""
        <div style='padding: 10px; border-radius: 5px; background-color: rgba(0,255,0,0.1); 
        margin-bottom: 20px; display: flex; align-items: center;'>
            <div class='live-indicator'></div>
            <span style='color: #00ff00; margin-left: 5px;'>Live updates active</span>
        </div>
    """, unsafe_allow_html=True)

def format_currency(value):
    """Format currency values with commas and 2 decimal places"""
    return "${:,.2f}".format(value)

def should_update_prices():
    """Check if it's time to update prices based on refresh interval"""
    current_time = time.time()
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = current_time
        return True
    
    # Update every second
    if current_time - st.session_state.last_refresh >= 1:
        st.session_state.last_refresh = current_time
        return True
    return False

# Transaction Management
def process_transaction(selected_coin, quantity, total_investment, purchase_price, coin_id, current_price, input_method):
    """Process and validate a new transaction"""
    if input_method == 'Enter Quantity' and quantity > 0:
        total_investment = calculate_total_investment(quantity, purchase_price)
    elif input_method == 'Enter Total Investment' and total_investment > 0:
        quantity = calculate_quantity(total_investment, purchase_price)
    else:
        st.error('Please enter valid quantity or investment amount')
        return False

    profit_loss = calculate_profit_loss(quantity, purchase_price, current_price)
    
    transaction_data = {
        'Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'Asset': selected_coin,
        'Symbol': coin_id,
        'Quantity': quantity,
        'Purchase Price': purchase_price,
        'Total Cash Invested': total_investment,
        'Current Price': current_price,
        'Profit/Loss': profit_loss
    }
    
    save_transaction(transaction_data)
    st.session_state.transactions = load_transactions()
    return True