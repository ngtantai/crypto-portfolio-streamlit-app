import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import time
import sqlite3
import os
import uuid
import numpy as np

# Set page configuration
st.set_page_config(layout="wide")

# Add custom CSS for global font and metric styling
st.markdown("""
    <style>
        /* Import Poppins font from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
            
        /* Import Bungee font from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Bungee&display=swap');
            
        /* Default font for all elements */
        .st-emotion-cache-1jicfl2 {
            margin-top: -5rem;    
        }
        html, body, [class*="css"], [class*="st-"], .stMarkdown, .stDataFrame, input, button {
            font-family: 'Poppins' !important;
            font-weight: bold;
        }
        
        /* Specific styling for metrics */
        .css-1wivap2, .css-1i3tcqk {
            font-family: 'Poppins' !important;
        }
            
        [data-testid="stMainBlockContainer"] {
            padding-left:6rem;
            padding-right:6rem;
        }
        [data-testid="stMain"] {
            margin-left: 0rem;  
            padding:0;
        }

        [data-testid="column"] {
            gap: 0px !important;
            padding: 0px !important;
        }
            
        [data-testid="stSidebarUserContent"] {
            margin-top: 4.5rem;
            text-align: center;
        }
        /* Metric spacing */
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
            letter-spacing: 2px !important;
            
        }
            
        [data-testid="stMetricValue"] {
            color: #00ff00;
            font-weight: light;
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
            margin-top: 0rem;
            padding: 0.75rem;
            width: 100%;
            heigth: 65%;
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
            
        h2 {
            margin-top: -2rem;
            font-size: 36px;
            margin-left: -0.5rem;
        }
            
        .background-image {
            width: 100%;
            height: 100%;
            background-image: url('icons8-profit-32.png');
            background-size: cover;
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
    st.markdown("""
        <div style='padding: 10px; border-radius: 5px; background-color: rgba(0,255,0,0.1); 
        margin-bottom: 20px; display: flex; align-items: center;'>
            <div class='live-indicator'></div>
            <span style='color: #00ff00; margin-left: 5px;'>Live updates active</span>
        </div>
    """, unsafe_allow_html=True)

def format_currency(value):
    """Format currency values with commas and 2 decimal places"""
    if value / 1000 >= 1:
        return "${:,.0f}".format(value)
    else:
        return "${:,.2f}".format(value)


def format_percentage(value):
    """Format currency values with commas and 2 decimal places"""
    return "%".format(value)


def format_round_currency(value):
    """Format currency values with commas and 2 decimal places"""
    return "${:,.0f}".format(value)

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


def main():
    st.title('Crypto Investment Portfolio'.upper())
    st.write('Track cryptocurrency trades with live price updates from CoinGecko')
    
    # Initialize session state
    init_session_state()
    
    
    
    # Sidebar setup
    st.sidebar.title('Add New Transaction')
    
    enable_live_space, live_update_space, empty_space= st.columns([3,2.5,4])
    # # Live update toggle
    # with transaction_space:
        
    with enable_live_space:
        auto_refresh = st.checkbox('Enable Live Price Updates', value=True)

    with live_update_space:
        if auto_refresh:
            display_live_indicator()

    

    # Create placeholders for dynamic content
    main_placeholder = st.empty()
    
    while True:
        try:
            with main_placeholder.container():
                # Input section in sidebar
                input_method = st.sidebar.selectbox(
                    "Choose input method:",
                    ['Enter Quantity', 'Enter Total Investment']
                )
                
                selected_coin = st.sidebar.selectbox(
                    'Select Cryptocurrency', 
                    options=[""] + list(fetch_available_coins().keys())
                )
                
                current_price = None
                if selected_coin:
                    coin_id = fetch_available_coins()[selected_coin]
                    current_price = st.session_state.current_prices.get(coin_id) or get_current_price(coin_id)
                
                purchase_price = st.sidebar.number_input('Purchase Price ($)', min_value=0.0, step=0.01)
                
                quantity = 0.0
                total_investment = 0.0
                
                if input_method == 'Enter Quantity':
                    quantity = st.sidebar.number_input('Quantity', min_value=0.0, step=0.01)
                    if quantity > 0 and purchase_price > 0:
                        total_investment = calculate_total_investment(quantity, purchase_price)
                        st.sidebar.write(f"Total Cash Invested: {format_currency(total_investment)}")
                else:
                    total_investment = st.sidebar.number_input('Total Cash Invested ($)', min_value=0.0, step=0.01)
                    if total_investment > 0 and purchase_price > 0:
                        quantity = calculate_quantity(total_investment, purchase_price)
                        st.sidebar.write(f"Quantity: {quantity:.8f}")
                
                if selected_coin and current_price:
                    st.sidebar.write(f"Current Price: {format_currency(current_price)}")
                    if quantity > 0:
                        current_value = quantity * current_price
                        st.sidebar.write(f"Current Value: {format_currency(current_value)}")
                
                # Add Transaction Button
                if st.sidebar.button('Add Transaction', type="primary"):
                    if selected_coin and purchase_price > 0 and current_price:
                        if process_transaction(selected_coin, quantity, total_investment, 
                                            purchase_price, coin_id, current_price, input_method):
                            st.sidebar.success('Transaction added successfully!')
                    else:
                        st.sidebar.error('Please fill in all required fields')
                
                # Display Transactions
                left_col, right_col = st.columns([0.01, 9.5])
                
                with right_col:
                    
                    
                    if not st.session_state.transactions.empty:
                        # Update current prices if auto-refresh is enabled
                        if auto_refresh and should_update_prices():
                            update_current_prices()
                        
                        left_header_space, right_header_space, right_space = st.columns([0.1,3,6.9])
                        with left_header_space:
                            st.markdown("<div style='margin-left: -1.25rem;'>🟦</div>", unsafe_allow_html=True)
                        with right_header_space:
                            st.header('Transactions')
                        
                        
                        # Create headers
                        col_headers = st.columns([2, 2, 2, 2, 2, 2, 2, 2, 1])
                        headers = ['Purchase Date', 'Asset', 'Quantity', 'Invested Cash', 
                                 'Purchase Price', 'Current Price', 'Profit/Loss', "% Yield"]
                        
                        for col, header in zip(col_headers[:-1], headers):
                            with col:
                                st.markdown(f"""
                                    <div style='background-color:#1965e1;color:white;
                                    font-weight:bold;font-family:Tahoma;padding-top:0.5rem;padding-bottom:0.5rem;padding-left:0.5rem;
                                    padding-right:0.5rem;height: 4rem;box-shadow: rgba(50, 50, 93, 0.25) 0px 30px 60px -12px inset, rgba(0, 0, 0, 0.3) 0px 18px 36px -18px inset;
                                    border: 0.1rem solid #0085ca; border-radius: 0.25rem;letter-spacing:0.1rem;
                                    text-align:center;font-size:0.75rem;margin-right: 0rem;opacity: 0.8;'>
                                    {header}
                                    </div>
                                """, unsafe_allow_html=True)

                        # Display transactions
                        for index, row in st.session_state.transactions.iterrows():
                            cols = st.columns([2, 2, 2, 2, 2, 2, 2, 2, 1])
                            if index == 0:
                                margin_value = 1
                            elif index == len(st.session_state.transactions) - 1:
                                margin_value = 0
                            else:
                                margin_value = 0
                            # Continue with the display of transaction details...
                            # Display transaction details
                            with cols[0]:  # Date
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;margin-left: -0.5rem;padding-left: 1rem;font-size:14px;text-align:center;
                                    border-left:5px solid #0085ca;padding-top:8px;letter-spacing:1px;opacity: 0.8;'>
                                    {row['Date']}</p>
                                """, unsafe_allow_html=True)
                            
                            with cols[1]:  # Asset
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;font-size:18px;text-align:center;opacity: 0.8;
                                    padding-top:7px;letter-spacing:1px;'>{row['Asset']}</p>
                                """, unsafe_allow_html=True)
                            
                            with cols[2]:  # Quantity
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;font-size:14px;text-align:center;opacity: 0.8;
                                    padding-top:0.9rem;letter-spacing:1px;'>{row['Quantity']:.3f}</p>
                                """, unsafe_allow_html=True)
                            
                            with cols[3]:  # Total Cash Invested
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;text-align:right;font-size:20px;padding-right: 2rem;opacity: 0.8;
                                    padding-top:0.75rem;letter-spacing:1px;'>{format_round_currency(row['Total Cash Invested'])}</p>
                                """, unsafe_allow_html=True)
                            
                            with cols[4]:  # Purchase Price
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;text-align:right;font-size:20px;padding-right: 2rem;opacity: 0.8;
                                    padding-top:0.75rem;letter-spacing:1px;'>{format_currency(row['Purchase Price'])}</p>
                                """, unsafe_allow_html=True)
                            
                            with cols[5]:  # Current Price
                                current_price = st.session_state.current_prices.get(row['Symbol']) or get_current_price(row['Symbol'])
                                if current_price:
                                    color = '#0fe6d2' if current_price >= row['Purchase Price'] else '#dd3342'
                                    st.markdown(f"""
                                        <p style='margin-top:{margin_value}rem;text-align:right;font-size:20px;padding-top:0.6rem;padding-right: 2rem;
                                        color:{color};letter-spacing:1.5px;'>
                                        {format_currency(current_price)}</p>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<p style='margin-top:{margin_value}rem;'>Price unavailable</p>", 
                                              unsafe_allow_html=True)
                            
                            with cols[6]:  # Profit/Loss
                                if current_price:
                                    profit_loss = calculate_profit_loss(row['Quantity'], 
                                                                      row['Purchase Price'], 
                                                                      current_price)
                                    color = '#00ff00' if profit_loss > 0 else '#c80c20'
                                    background_color = "#075f00" if profit_loss > 0 else '#ec124e'
                                    st.markdown(f"""
                                        <p style='margin-top:{margin_value}rem;margin-left:0.15rem;text-align:right;font-size:20px;font-weight:400;padding-right: 0.5rem;padding-top:0.5rem;padding-bottom:0.5rem;\
                                                border-radius: 5px; border: 1.5px solid green; width: 100%; font-weight: 500;box-shadow: green 0px 10px 10px -15px inset, green 0px 18px 36px -18px inset;
                                        color:{color};letter-spacing:2px;background-color:transparent;'>
                                        {format_currency(profit_loss)}</p>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<p style='margin-top:{margin_value}rem;'>-</p>", 
                                              unsafe_allow_html=True)
                            with cols[7]:
                                if current_price:
                                    # import numpy as np
                                    profit_loss = calculate_profit_loss(row['Quantity'], 
                                                                      row['Purchase Price'], 
                                                                      current_price)
                                    performance_rate = profit_loss * 100 / row['Total Cash Invested']
                                    color = '#00ff00' if profit_loss > 0 else '#c80c20'
                                    # icon = '📈' if profit_loss > 0 else '📉'
                                    background_color = "#075f00" if profit_loss > 0 else '#ec124e'
                                    st.markdown(f"""
                                        <p style='margin-top:{margin_value}rem;text-align:right;font-size:20px;font-weight:500;padding-right: 0.5rem;padding-top:0.5rem;padding-bottom:0.5rem;\
                                                border-radius: 5px; border: 1.5px solid green; box-shadow: green 0px 10px 10px -15px inset, green 0px 18px 36px -18px inset;
                                        color:{color};letter-spacing:2px;background-color: transparent;'>
                                        {np.round(performance_rate,2)}%</p>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<p style='margin-top:{margin_value}rem;'>-</p>", 
                                              unsafe_allow_html=True)
                            
                            with cols[8]:  # Delete Button
                                if index == 0:
                                    st.markdown("<div style='margin-top:0rem;'></div>", unsafe_allow_html=True)
                                # unique_id = str(uuid.uuid4())
                                if st.button('🗑️', key=f"delete_{row['id']}"):
                                    if delete_transaction(int(row['id'])):
                                        st.success("Transaction deleted!")
                                        st.session_state.transactions = load_transactions()
                                        st.rerun()
                            
                            # Separator lines
                            if index == len(st.session_state.transactions) - 1:
                                st.markdown(f"""
                                    <hr style='margin-top:{margin_value}rem;margin-bottom:0rem;
                                    border:0.1px solid transparent;box-shadow:0px 20px 40px yellow;'>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <hr style='margin-top:{0}rem;margin-bottom:0rem;border: 0.25px dash white;'>
                                """, unsafe_allow_html=True)
                        
                        # Calculate and display summary statistics
                        st.write("")
                        st.write("")
                        left_space, col1, middle_space, col2, col3, col4, right_space = st.columns([1,10,5,10,10,10, 1])
                        
                        # st.markdown('<div style=""></div>', unsafe_allow_html=True)
                        # st.markdown('<div style=""></div>', unsafe_allow_html=True)
                        with col1:
                            total_investment = st.session_state.transactions['Total Cash Invested'].sum()
                            
                            # st.markdown('<div class="total-cash-invested" >', unsafe_allow_html=True)
                            # st.metric(
                            #     label="Total Cash Invested",
                            #     value=format_currency(total_investment),
                            #     delta=total_investment,
                            #     delta_color="off"
                            # )

                            # st.markdown('</div>', unsafe_allow_html=True)
                            # Instead of using st.metric, use custom HTML
                            st.markdown(f"""
                                <div style='padding: 0rem; letter-spacing: 2px;margin-top:0.1rem;opacity:0.7;'>
                                    <p style='color: white; font-size: 14px; margin-bottom: 0.5rem; '>Total Cash Invested</p>
                                    <p style='font-size: 2rem; margin-top:-0.5rem;font-size: 36px; font-weight: 700;'>{format_currency(total_investment)}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            actual_cash_yield = sum(
                                calculate_profit_loss(
                                    row['Quantity'],
                                    row['Purchase Price'],
                                    st.session_state.current_prices.get(row['Symbol']) or row['Current Price']
                                ) + row['Total Cash Invested']
                                for _, row in st.session_state.transactions.iterrows()
                            )
                            
                            actual_profit_loss = actual_cash_yield - total_investment
                            perc_yield = actual_profit_loss / total_investment
                            if perc_yield > 0.3:
                                emoji = "🎉"*4 + "✈️"*4
                            elif perc_yield > 0.2:
                                emoji = "🎉 😍 🚀 ✈️"
                            elif perc_yield > 0.15:
                                emoji = "🎉 😍 🚀"
                            elif perc_yield > 0.1:
                                emoji = "🎉 😍"
                            elif perc_yield > 0.05:
                                emoji = "🎉"
                            else:
                                emoji = "💥"
                            st.metric(
                                label="Actual Cash Yield",
                                value=format_currency(actual_cash_yield),
                                delta=emoji
                            )
                        
                        with col3:
                            total_profit_loss = sum(
                                calculate_profit_loss(
                                    row['Quantity'],
                                    row['Purchase Price'],
                                    st.session_state.current_prices.get(row['Symbol']) or row['Current Price']
                                )
                                for _, row in st.session_state.transactions.iterrows()
                            )
                            
                            formatted_profit_loss = format_currency(abs(total_profit_loss))
                            if total_profit_loss < 0:
                                formatted_profit_loss = f"-{formatted_profit_loss}"
                                color = "inverse"
                            else:
                                color = "normal"
                            
                            st.metric(
                                label="Total Profit/Loss",
                                value=formatted_profit_loss,
                                delta=formatted_profit_loss,
                                delta_color=color
                            )

                        with col4:
                            if total_investment and total_profit_loss:
                                actual_percentage_yield = total_profit_loss * 100 / total_investment
                                formatted_perc_yield= np.round(actual_percentage_yield,2)
                                if total_profit_loss < 0:
                                    formatted_perc_yield = f"{formatted_perc_yield} %"
                                    color = "inverse"
                                else:
                                    formatted_perc_yield = f"{formatted_perc_yield} %"
                                    color = "normal"
                                
                                st.metric(
                                    label="Actual % Yield",
                                    value=formatted_perc_yield,
                                    delta=formatted_perc_yield,
                                    delta_color=color
                                )
                            else:
                                st.metric(
                                    label="Actual % Yield",
                                    value=0,
                                    delta='normal'
                                )
                        

                        st.write("")
                        # Asset summary
                        st.markdown("""
                            <hr style='margin-top:1.5rem;margin-bottom:1.5rem;
                            border:0.5px solid transparent;box-shadow:0px -30px 40px yellow;'>
                        """, unsafe_allow_html=True)
                        
                        st.subheader('Profit/Loss by Asset')
                        asset_summary = pd.DataFrame()
                        if not st.session_state.transactions.empty:
                            summary_data = []
                            for asset in st.session_state.transactions['Asset'].unique():
                                asset_transactions = st.session_state.transactions[
                                    st.session_state.transactions['Asset'] == asset
                                ]
                                
                                total_invested = asset_transactions['Total Cash Invested'].sum()
                                profit_loss = sum(
                                    calculate_profit_loss(
                                        row['Quantity'],
                                        row['Purchase Price'],
                                        st.session_state.current_prices.get(row['Symbol']) or row['Current Price']
                                    )
                                    for _, row in asset_transactions.iterrows()
                                )
                                actual_yield = total_invested + profit_loss
                                
                                summary_data.append({
                                    'Asset': asset,
                                    'Total Cash Invested': total_invested,
                                    'Profit/Loss': profit_loss,
                                    'Actual Cash Yield': actual_yield
                                })
                            
                            asset_summary = pd.DataFrame(summary_data)
                        
                        if not asset_summary.empty:
                            st.dataframe(
                                asset_summary,
                                column_config={
                                    'Total Cash Invested': st.column_config.NumberColumn(
                                        'Total Cash Invested',
                                        help='Total amount invested',
                                        format="$%.2f",
                                    ),
                                    'Profit/Loss': st.column_config.NumberColumn(
                                        'Profit/Loss',
                                        help='Current profit or loss',
                                        format="$%.2f",
                                    ),
                                    'Actual Cash Yield': st.column_config.NumberColumn(
                                        'Actual Cash Yield',
                                        help='The Actual Return Cash yielded from investment',
                                        format="$%.2f",
                                    ),
                                },
                                hide_index=True,
                                use_container_width=True
                            )
                        
                        # Control buttons
                        st.markdown("<hr style='margin-top:2rem;margin-bottom:2rem;border:1px solid #2d3436;'>",
                                  unsafe_allow_html=True)
                        
                        left_button_space, col1, col2, right_button_space = st.columns([2,3,3,2])
                        with col1:
                            if st.button('Refresh Prices', key="reset_button", type="secondary"):
                                st.rerun()
                        
                        with col2:
                            if st.button('Clear All Transactions', type="secondary"):
                                clear_transactions()
                                st.session_state.transactions = load_transactions()
                                st.success('All transactions cleared!')


            if auto_refresh:
                time.sleep(15)  # Wait for 1 second before next update
                st.rerun()
            else:
                break
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()