import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import time
import sqlite3
import os
import uuid
import numpy as np
import re

from datetime import datetime, timedelta
# import plotly.graph_objs as go

from crypto_logo_helper import get_crypto_logo

from config import get_db_path

def get_db_path():
    """Get the absolute path for the database file"""
    return get_db_path()

# Set page configuration
st.set_page_config(layout="wide", page_title="Crypto Portfolio")


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
            padding-left:4rem;
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
            margin-top: 0.5rem;
            text-align: center;
            letter-spacing: 0.1rem;
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
            
        /* button[kind="secondary"] */
        /* Select elements with 'st-key-reset_button' in their class */
        .stElementContainer.element-container.st-key-reset_button 
            .stButton button {
                margin-left: 4rem;
                margin-top: 0rem;
                padding: 0.5rem;
                padding-top: 2rem;
                padding-bottom: 2rem;
                width: 50%;
                heigth: 65%;
                border-radius: 10px;
                background-color: #e59866;
        }

            
        .stElementContainer.element-container.st-key-clear_transactions
            .stButton button {
                margin-left: -6rem;
                margin-top: 0rem;
                padding: 0.5rem;
                padding-top: 2rem;
                padding-bottom: 2rem;
                width: 70%;
                heigth: 65%;
                border-radius: 10px;
        }
            
            
        .stElementContainer.element-container.st-key-calculate_new_balance
            .stButton button {
                margin-left: 10rem;
                margin-top: 1rem;
                padding: 0.1rem;
                padding-top: 1rem;
                padding-bottom: 1rem;
                width: 30%;
                heigth: 45%;
                border-radius: 10px;
                background-color: #2980b9;
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
        
        /* Checkbox */
        [data-baseweb="checkbox"] {
            padding: 1rem;
            border: 1px dotted green;
            border-radius: 5px;
        }

        /* Live update indicator */
        .live-indicator {
            display: inline-block;
            width: 1rem;
            height: 1rem;
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

        [data-testid="stFullScreenFrame"]{
            margin-left: 1rem;
            margin-top: 0.25rem;
        }

        .stPlotlyChart {
            padding: 0;
            margin-left: -1rem;
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


# First, add these new database functions after the existing database functions:
# Update the update_transaction function to handle the date:
def update_transaction(transaction_id, updated_data):
    """Update an existing transaction in the database"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create a mapping for column names
        column_mapping = {
            'Date': 'date',
            'Quantity': 'quantity',
            'Purchase Price': 'purchase_price',
            'Total Cash Invested': 'total_cash_invested',
            'Current Price': 'current_price',
            'Profit/Loss': 'profit_loss'
        }
        
        # Prepare the update query and parameters
        update_fields = []
        params = []
        for key, value in updated_data.items():
            if key in column_mapping:
                update_fields.append(f"{column_mapping[key]} = ?")
                params.append(value)
        
        params.append(transaction_id)  # Add transaction_id for WHERE clause
        
        update_query = f"""
            UPDATE transactions 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """
        
        c.execute(update_query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error updating transaction: {e}")
        return False
    finally:
        conn.close()



def get_transaction(transaction_id):
    """Retrieve a specific transaction from the database"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        result = c.fetchone()
        if result:
            # Convert to dictionary
            columns = ['id', 'Date', 'Asset', 'Symbol', 'Quantity', 
                      'Purchase Price', 'Total Cash Invested', 'Current Price', 'Profit/Loss']
            return dict(zip(columns, result))
        return None
    except sqlite3.Error as e:
        st.error(f"Error retrieving transaction: {e}")
        return None
    finally:
        conn.close()


def calculate_profit_withdrawal_options(transactions_df, coin_selected):
    """Calculate withdrawal options based on profit"""
    # Get all transactions for selected coin
    coin_transactions = transactions_df[transactions_df['Asset'] == coin_selected].copy()
    if coin_transactions.empty:
        return None
    
    # Calculate current total profit/loss
    total_quantity = coin_transactions['Quantity'].sum()
    total_invested = coin_transactions['Total Cash Invested'].sum()
    current_price = st.session_state.current_prices.get(coin_transactions.iloc[0]['Symbol'])
    
    if not current_price:
        return None
        
    current_value = total_quantity * current_price
    total_profit = current_value - total_invested
    
    # Calculate reference targets (10% to 50% of profit)
    percentages = [10, 20, 30, 40, 50]
    reference_targets = {
        f"{p}%": {
            'percentage': p,
            'amount': (total_profit * p / 100),
            'coins': (total_profit * p / 100) / current_price
        } for p in percentages
    }
    
    return {
        'total_profit': total_profit,
        'current_price': current_price,
        'total_quantity': total_quantity,
        'total_invested': total_invested,
        'reference_targets': reference_targets,
        'current_value': current_value
    }


# Session state management
def init_session_state():
    """Initialize all required session state variables"""
    if 'chart_days' not in st.session_state:
        st.session_state.chart_days = '30'  # Default to 30 days

    if 'db_initialized' not in st.session_state:
        init_database()
        st.session_state.db_initialized = True
    
    if 'transactions' not in st.session_state:
        st.session_state.transactions = load_transactions()
    
    if 'current_prices' not in st.session_state:
        st.session_state.current_prices = {}
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()

    if 'editing_transaction' not in st.session_state:
        st.session_state.editing_transaction = None
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

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
        <div style='padding: 1rem; border-radius: 5px; background-color: rgba(0,255,0,0.1); 
        margin-bottom: 20px; display: flex; align-items: center;'>
            <div class='live-indicator'></div>
            <span style='color: #00ff00; margin-left: 5px;'>Live updates active</span>
        </div>
    """, unsafe_allow_html=True)

def format_currency(value): 
    """Format currency values with commas and 2 decimal places"""
    if value / 1000 >= 1:
        return "${:,.0f}".format(value)
    elif re.findall(r'^\d\.', str(value)):
        return "${:,.4f}".format(value)
    else:
         return "${:,.2f}".format(value)
    
# def format_purchase_price(value):
#     """Format currency values with commas and 2 decimal places"""
#     if '.' in str(value):
#         return "${:,.2f}".format(value)
#     return "${:,.0f}".format(value)



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
def process_transaction(selected_coin, quantity, total_investment, purchase_price, coin_id, current_price, input_method, transaction_date):
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
        'Date': transaction_date.strftime('%Y-%m-%d %H:%M'),
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

def create_percentage_bar(value):
    """
    Create a simple percentage bar
    Args:
        value (float): Percentage value (-100 to 100)
    """
    # Ensure value is between -100 and 100
    value = max(-100, min(100, value))
    
    # Determine color based on positive/negative value
    color = '#00ff00' if value >= 0 else '#ff0000'
    
    # Use absolute value for width
    width = abs(value)
    
    return f"""
        <div style="
            width: 100%;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 2px;
            margin-top: 0.35rem;
        ">
            <div style="
                width: {width}%;
                height: 35px;
                background-color: {color};
                border-radius: 3px;
                transition: width 500ms ease-in-out;
            ">
            </div>
        </div>
    """


# Add days selection in the sidebar
def add_chart_settings_to_sidebar():
    st.sidebar.markdown("### Chart Settings")
    
    # Days selection
    days_options = {
        '7': '7 Days',
        '30': '30 Days',
        '90': '90 Days',
        '180': '180 Days',
        '360': '360 Days'
    }
    selected_days = st.sidebar.selectbox(
        "Price History Range",
        options=list(days_options.keys()),
        format_func=lambda x: days_options[x],
        key="chart_days"
    )
    
    # Chart type selection
    chart_types = ['Candlestick', 'Line']
    selected_type = st.sidebar.selectbox(
        "Chart Type",
        options=chart_types,
        key="chart_type"
    )
    
    return selected_days, selected_type

# Update price history function to include OHLC data for candlesticks
def get_coin_price_history(coin_id, days='30'):
    """Fetch price history with OHLC data"""
    try:
        # For candlestick data
        ohlc_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
        # For line chart data
        line_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        
        headers = {
            'accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
        
        if st.session_state.chart_type == 'Candlestick':
            response = requests.get(
                ohlc_url,
                params={'vs_currency': 'usd', 'days': days},
                headers=headers
            )
        else:
            response = requests.get(
                line_url,
                params={'vs_currency': 'usd', 'days': days, 'interval': 'daily'},
                headers=headers
            )
        
        if response.status_code == 200:
            data = response.json()
            
            if st.session_state.chart_type == 'Candlestick':
                # OHLC data format
                dates = [datetime.fromtimestamp(candle[0]/1000) for candle in data]
                ohlc = [[candle[1], candle[2], candle[3], candle[4]] for candle in data]
                return dates, ohlc
            else:
                # Line chart format
                prices = data['prices']
                dates = [datetime.fromtimestamp(price[0]/1000) for price in prices]
                values = [price[1] for price in prices]
                return dates, values
            
        print(f"Failed to fetch price history: Status {response.status_code}")
        return None, None
    except Exception as e:
        print(f"Error fetching price history: {e}")
        return None, None

def create_sparkline(dates, prices, current_price, purchase_price):
    """Create a sparkline chart with weekly interval lines and price annotations"""
    if not dates or not prices:
        return None
    
    fig = go.Figure()
    
    # Helper function to find price at specific date
    def get_price_at_date(target_date):
        for i, date in enumerate(dates):
            if date.date() == target_date.date():
                return prices[i] if isinstance(prices[0], (int, float)) else prices[i][3]
        return None
    
    # Add the price data based on chart type
    if st.session_state.chart_type == 'Candlestick':
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=[p[0] for p in prices],
                high=[p[1] for p in prices],
                low=[p[2] for p in prices],
                close=[p[3] for p in prices],
                increasing=dict(line=dict(color='#00ff00')),
                decreasing=dict(line=dict(color='#ff0000')),
                showlegend=False
            )
        )
    else:
        # Line chart with daily color changes
        for i in range(1, len(dates)):
            color = '#00ff00' if prices[i] >= prices[i-1] else '#ff0000'
            fig.add_trace(
                go.Scatter(
                    x=dates[i-1:i+1],
                    y=prices[i-1:i+1] if isinstance(prices[0], (int, float)) else [p[3] for p in prices[i-1:i+1]],
                    mode='lines',
                    line=dict(color=color, width=1.5),
                    hoverinfo='y',
                    showlegend=False
                )
            )
    
    # Add weekly interval lines and annotations
    start_date = min(dates)
    end_date = max(dates)
    current_date = start_date
    while current_date <= end_date:
        # Only add line and annotation if it's the start of a week (Monday)
        if current_date.weekday() == 0:
            # Add vertical line
            fig.add_vline(
                x=current_date,
                line_width=1,
                line_dash="dot",
                line_color="rgba(255, 255, 255, 0.1)"
            )
            
            # Get price at this date
            price = get_price_at_date(current_date)
            if price is not None:
                # Add price annotation
                fig.add_annotation(
                    x=current_date,
                    y=price,
                    text=f"${price:,.2f}",
                    showarrow=False,
                    font=dict(
                        size=8,
                        color="rgba(255, 255, 255, 0.5)"
                    ),
                    yshift=10  # Slight shift above the line
                )
        
        current_date += timedelta(days=1)
    
    # Update layout for minimal appearance
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),  # Added top margin for annotations
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=45,  # Increased height slightly for annotations
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            visible=False,
            range=[start_date, end_date]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            visible=False
        ),
        hovermode='x unified'
    )
    
    return fig





def main():
    # In your main app layout, add the days selector to sidebar
    # Add this near the top of your main section
    selected_days, selected_type = add_chart_settings_to_sidebar()



    # Initialize database if not exists
    if 'db_initialized' not in st.session_state:
        init_database()
        st.session_state.db_initialized = True

    st.title('Crypto Investment Portfolio'.upper())
    st.markdown("<h3 style='color: yellow; font-family:Poppins; letter-spacing: 0.1rem;'>Track cryptocurrency trades with live price updates from CoinGecko</h3>", unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    
    
    # Sidebar setup
    st.sidebar.title('Add New Transaction')
    
    enable_live_space, live_update_space, empty_space= st.columns([1.8,1.5,6.8])
    # # Live update toggle
    # with transaction_space:
        
    with enable_live_space:
        auto_refresh = st.checkbox('Enable Live Price Updates', value=True)

    with live_update_space:
        if auto_refresh:
            display_live_indicator()

    

    # Create placeholders for dynamic content
    main_placeholder = st.empty()
    # Example usage:
    # Basic usage with label
    # st.markdown(
    #     create_advanced_percentage_bar(65, label="Progress"), 
    #     unsafe_allow_html=True
    # )
    while True:
        try:
            with main_placeholder.container():
                # Add date and time pickers in sidebar
                transaction_date = st.sidebar.date_input(
                    "Transaction Date",
                    value=datetime.now().date(),
                    key="new_transaction_date"
                )
                transaction_time = st.sidebar.time_input(
                    "Transaction Time",
                    value=datetime.now().time(),
                    key="new_transaction_time"
                )

                # Combine date and time when processing transaction
                transaction_datetime = datetime.combine(transaction_date, transaction_time)

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
                

                # Update the Add Transaction button section
                if st.sidebar.button('Add Transaction', type="primary"):
                    if selected_coin and purchase_price > 0 and current_price:
                        if process_transaction(
                            selected_coin, 
                            quantity, 
                            total_investment, 
                            purchase_price, 
                            coin_id, 
                            current_price, 
                            input_method,
                            transaction_datetime  # Pass the combined datetime
                        ):
                            st.sidebar.success('Transaction added successfully!')
                    else:
                        st.sidebar.error('Please fill in all required fields')
                
                # Display Transactions
                left_col, right_col = st.columns([0.01, 9.5])
                
                with right_col:
                    # Edit Transaction Form
                    if st.session_state.edit_mode and st.session_state.editing_transaction:
                        transaction = get_transaction(st.session_state.editing_transaction)
                        if transaction:
                            st.markdown("### Edit Transaction")
                            
                            # Use columns for the form
                            edit_cols = st.columns([2, 2, 2, 2, 2, 1.5, 1.5])
                            
                            # Add separate date and time pickers
                            with edit_cols[0]:
                                # Convert stored date string to datetime object
                                current_datetime = datetime.strptime(transaction['Date'], '%Y-%m-%d %H:%M')
                                new_date = st.date_input(
                                    'Transaction Date',
                                    value=current_datetime.date(),
                                    key='edit_date'
                                )
                            
                            with edit_cols[1]:
                                new_time = st.time_input(
                                    'Transaction Time',
                                    value=current_datetime.time(),
                                    key='edit_time'
                                )
                            
                            with edit_cols[2]:
                                new_quantity = st.number_input(
                                    'New Quantity',
                                    value=float(transaction['Quantity']),
                                    min_value=0.0,
                                    step=0.01,
                                    key='edit_quantity'
                                )
                            
                            with edit_cols[3]:
                                new_purchase_price = st.number_input(
                                    'New Purchase Price ($)',
                                    value=float(transaction['Purchase Price']),
                                    min_value=0.0,
                                    step=0.01,
                                    key='edit_purchase_price'
                                )
                            
                            with edit_cols[4]:
                                new_total_invested = st.number_input(
                                    'New Total Investment ($)',
                                    value=float(transaction['Total Cash Invested']),
                                    min_value=0.0,
                                    step=0.01,
                                    key='edit_total_invested'
                                )
                            
                            with edit_cols[5]:
                                if st.button('Save Changes', type='primary', key='save_edit'):
                                    # Combine date and time
                                    new_datetime = datetime.combine(new_date, new_time)
                                    
                                    # Calculate new values
                                    new_profit_loss = calculate_profit_loss(
                                        new_quantity,
                                        new_purchase_price,
                                        transaction['Current Price']
                                    )
                                    
                                    # Update transaction
                                    updated_data = {
                                        'Date': new_datetime.strftime('%Y-%m-%d %H:%M'),
                                        'Quantity': new_quantity,
                                        'Purchase Price': new_purchase_price,
                                        'Total Cash Invested': new_total_invested,
                                        'Profit/Loss': new_profit_loss
                                    }
                                    
                                    if update_transaction(st.session_state.editing_transaction, updated_data):
                                        st.success('Transaction updated successfully!')
                                        st.session_state.edit_mode = False
                                        st.session_state.editing_transaction = None
                                        st.session_state.transactions = load_transactions()
                                        st.rerun()
                            
                            with edit_cols[6]:
                                if st.button('Cancel', type='secondary', key='cancel_edit'):
                                    st.session_state.edit_mode = False
                                    st.session_state.editing_transaction = None
                                    st.rerun()
                            
                            st.markdown("<hr>", unsafe_allow_html=True)
                    
                    
                    if not st.session_state.transactions.empty:
                        # Update current prices if auto-refresh is enabled
                        if auto_refresh and should_update_prices():
                            update_current_prices()
                        
                        left_header_space, right_header_space, right_space = st.columns([0.1,3,6.9])
                        with left_header_space:
                            st.markdown("<div style='margin-left: -1.25rem;'>✨</div>", unsafe_allow_html=True)
                        with right_header_space:
                            st.header('Transaction Records')
                        
                        
                        # Create headers
                        col_headers = st.columns([2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1])
                        headers = ['Purchase Date', 'Logo', 'Asset', 'Quantity', 'Invested Cash', 
                                 'Purchase Price', 'Current Price', 'Chart', 'Profit/Loss', "% Yield", "Performance"]
                        
                        for col, header in zip(col_headers[:-1], headers):
                            with col:
                                # if header == '':
                                #     st.markdown(f"""
                                #     <div style='background-color:transparent;color:yellow;
                                #     font-weight:bold;font-family:Tahoma;padding-top:0.25rem;padding-bottom:0.5rem;padding-left:0.1rem;
                                #     padding-right:0.1rem;height: 4rem;box-shadow: rgba(50, 50, 93, 0.25) 0px 30px 60px -12px inset, rgba(0, 0, 0, 0.3) 0px 18px 36px -18px inset;
                                #     border: 0rem solid #0085ca; border-radius: 0.25rem;letter-spacing:0.1rem;
                                #     text-align:center;font-size:1rem;margin-right: 0rem;opacity: 0.8;'>
                                #     {header}
                                #     </div>
                                # """, unsafe_allow_html=True)
                                # else:
                                st.markdown(f"""
                                    <div style='background-color:#1965e1;color:yellow;
                                    font-weight:bold;font-family:Tahoma;padding-top:0.25rem;padding-bottom:0.5rem;padding-left:0.1rem;
                                    padding-right:0.1rem;height: 4rem;box-shadow: rgba(50, 50, 93, 0.25) 0px 30px 60px -12px inset, rgba(0, 0, 0, 0.3) 0px 18px 36px -18px inset;
                                    border: 0.1rem solid #0085ca; border-radius: 0.25rem;letter-spacing:0.1rem;
                                    text-align:center;font-size:1rem;margin-right: 0rem;opacity: 0.8;'>
                                    {header}
                                    </div>
                                """, unsafe_allow_html=True)

                        # Display transactions
                        for index, row in st.session_state.transactions.iterrows():
                            cols = st.columns([2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1])
                            if index == 0:
                                margin_value = 1
                            elif index == len(st.session_state.transactions) - 1:
                                margin_value = 0
                            else:
                                margin_value = 0

                            # positive_impact = st.empty()
                            current_price = st.session_state.current_prices.get(row['Symbol']) or get_current_price(row['Symbol'])
                            profit_loss = calculate_profit_loss(row['Quantity'], 
                                                                      row['Purchase Price'], 
                                                                      current_price)
                            performance_rate = profit_loss * 100 / row['Total Cash Invested']
                            # Continue with the display of transaction details...
                            # Display transaction details
                            with cols[0]:  # Date
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;margin-left:-0.5rem;padding-left: 2rem;font-size:15px;text-align:left;
                                    border-left:0.5rem solid #0085ca;padding-top:8px;letter-spacing:1px;opacity: 0.8;'>
                                    {row['Date']}</p>
                                """, unsafe_allow_html=True)
                            
                            # with cols[1]:  # Asset
                            #     st.markdown(f"""
                            #         <p style='margin-top:{margin_value}rem;font-size:15px;text-align:center;opacity: 1;
                            #         padding-top:.75rem;letter-spacing:0.5px;'>{row['Asset']}</p>
                            #     """, unsafe_allow_html=True)

                            with cols[1]:
                                logo_path = get_crypto_logo(row['Asset'])
                                if logo_path and os.path.exists(logo_path):
                                    if index == 0:
                                        st.write('')
                                        # st.write('')
                                    st.image(logo_path, width=40)
                                else:
                                    st.write("")  # Empty space for alignment
                            with cols[2]:
                                # row['Asset'] = re.sub("\s\(.*\)", "", row['Asset'])
                                if index == 0:
                                    st.markdown(f"""
                                    <div style='padding-top: 0rem; margin-top: 1.75rem;text-align: left;margin-left: 0.5rem;'>
                                        <span style='font-size:16px;opacity:0.8;
                                        letter-spacing:0.5px;'>{row['Asset']}</span>
                                    </div>
                                """, unsafe_allow_html=True)
                                else:                          
                                    # margin_top_value = '2rem' if len(row['Asset']) >= 15 else '2rem'
                                    st.markdown(f"""
                                        <div style='padding-top: 0rem; margin-top: 0.65rem; margin-bottom: 0.5rem;text-align: left;margin-left: 0.5rem;'>
                                            <span style='font-size:15px;opacity:0.8; white-space: nowrap;
                                            letter-spacing:0.5px;'>{row['Asset']}</span>
                                        </div>
                                    """, unsafe_allow_html=True)

                                
                            
                            with cols[3]:  # Quantity
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;font-size:16px;text-align:center;opacity: 0.8;
                                    padding-top:0.8rem;letter-spacing:1px;'>{row['Quantity']:.3f}</p>
                                """, unsafe_allow_html=True)
                            
                            with cols[4]:  # Total Cash Invested
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;text-align:right;font-size:20px;padding-right: 1rem;opacity: 0.8;\
                                    box-shadow: white 0px 10px 10px -25px inset, white 0px 18px 36px -29px inset;border: 0.5px solid white;border-radius: 5px;
                                    padding-top:0.5rem;padding-bottom:0.5rem;letter-spacing:1px;'>{format_round_currency(row['Total Cash Invested'])}</p>
                                """, unsafe_allow_html=True)
                            
                            with cols[5]:  # Purchase Price
                                purchase_price = row['Purchase Price']
                                st.markdown(f"""
                                    <p style='margin-top:{margin_value}rem;text-align:right;font-size:20px;padding-right: 1rem;opacity: 0.7;
                                    padding-top:0.5rem;letter-spacing:1px;'>{format_currency(row['Purchase Price'])}</p>
                                """, unsafe_allow_html=True)
                            
                            with cols[6]:  # Current Price
                                current_price = st.session_state.current_prices.get(row['Symbol']) or get_current_price(row['Symbol'])
                                if current_price:
                                    color = '#0fe6d2' if current_price >= row['Purchase Price'] else '#dd3342'
                                    st.markdown(f"""
                                        <p style='margin-top:{margin_value}rem;text-align:right;font-size:20px;padding-top:0.6rem;padding-right: 1rem;
                                        color:{color};letter-spacing:1.5px;'>
                                        {format_currency(current_price)}</p>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<p style='margin-top:{margin_value}rem;'>Price unavailable</p>", 
                                              unsafe_allow_html=True)
                            
                            with cols[7]:
                                try:
                                    if index == 0:
                                        st.write('')
                                    if 'Symbol' in row:
                                        dates, prices = get_coin_price_history(
                                            row['Symbol'].lower(), 
                                            days=st.session_state.chart_days
                                        )
                                        if dates and prices:
                                            current_price = st.session_state.current_prices.get(row['Symbol'])
                                            fig = create_sparkline(
                                                dates, 
                                                prices, 
                                                current_price, 
                                                row['Purchase Price']
                                            )
                                            if fig:
                                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{index}")
                                            else:
                                                st.write("No data")
                                        else:
                                            st.write("No data")
                                except Exception as e:
                                    st.write(f"Chart error: {e}")


                            with cols[8]:  # Profit/Loss
                                if current_price:
                                    profit_loss = calculate_profit_loss(row['Quantity'], 
                                                                      row['Purchase Price'], 
                                                                      current_price)
                                    color = '#00ff00' if profit_loss > 0 else '#c80c20'
                                    background_color = "#075f00" if profit_loss > 0 else '#ec124e'
                                    st.markdown(f"""
                                        <p style='margin-top:{margin_value}rem;margin-left:0.15rem;text-align:right;font-size:20px;font-weight:400;padding-right: 0.5rem;padding-top:0.5rem;padding-bottom:0.5rem;\
                                                border-radius: 5px; border: 0.5px solid {background_color}; width: 100%; font-weight: 500;box-shadow: {background_color} 0px 10px 10px -29px inset, {background_color} 0px 18px 36px -28px inset;
                                        color:{color};letter-spacing:2px;background-color:transparent;'>
                                        {format_currency(profit_loss)}</p>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<p style='margin-top:{margin_value}rem;'>-</p>", 
                                              unsafe_allow_html=True)
                            with cols[9]: # % Yield
                                if current_price:
                                    # import numpy as np
                                    profit_loss = calculate_profit_loss(row['Quantity'], 
                                                                      row['Purchase Price'], 
                                                                      current_price)
                                    performance_rate = profit_loss * 100 / row['Total Cash Invested']
                                    positive_impact = performance_rate
                                    color = '#00ff00' if profit_loss > 0 else '#c80c20'
                                    background_color = "#075f00" if profit_loss > 0 else '#ec124e'
                                    # icon = '📈' if profit_loss > 0 else '📉'

                                    st.markdown(f"""
                                        <p style='margin-top:{margin_value}rem;text-align:right;font-size:20px;font-weight:500;padding-right: 0.5rem;padding-top:0.5rem;padding-bottom:0.5rem;\
                                                border-radius: 5px; border: 0.5px solid {background_color}; box-shadow: {background_color} 0px 10px 10px -29px inset, {background_color} 0px 18px 36px -29px inset;
                                        color:{color};letter-spacing:2px;background-color: transparent;'>
                                        {np.round(performance_rate,2)}%</p>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<p style='margin-top:{margin_value}rem;'>-</p>", 
                                              unsafe_allow_html=True)
                            
                            with cols[10]:  # Performance column
                                if current_price:
                                    if index == 0:
                                        st.write("")
                                    profit_loss = calculate_profit_loss(row['Quantity'], 
                                                                    row['Purchase Price'], 
                                                                    current_price)
                                    performance_rate = profit_loss * 100 / row['Total Cash Invested']
                                    st.markdown(create_percentage_bar(performance_rate), unsafe_allow_html=True)

                            with cols[11]:  # Edit/Delete Buttons
                                if index == 0:
                                    st.write('')
                                st.markdown(f"""<style>
                                            .stElementContainer.element-container.st-key-edit_{row['id']}
                                                {{
                                                    margin-top: -1.1rem;
                                                    margin-left: -0.5rem;
                                                    padding: .9rem;
                                                    padding-top: 0.4rem;
                                                    padding-bottom: 0.4rem;
                                                    border-radius: 5px;
                                            }}                                  
                                </style>""", unsafe_allow_html=True)
                                # st.write('<div style="margin-top: -2rem;"></div>', unsafe_allow_html=True)
                                if st.button('✏️', key=f"edit_{row['id']}"):
                                    st.session_state.editing_transaction = row['id']
                                    st.session_state.edit_mode = True
                                    st.rerun()

                            with cols[12]:
                                if index == 0:
                                    st.write('')
                                st.markdown(f"""<style>
                                            .stElementContainer.element-container.st-key-delete_{row['id']}
                                                {{
                                                    margin-top: -1.1rem;
                                                    margin-left: -1.25rem;
                                                    padding: .9rem;
                                                    padding-top: 0.4rem;
                                                    padding-bottom: 0.4rem;
                                                    border-radius: 5px;
                                            }}                                  
                                </style>""", unsafe_allow_html=True)
                                if st.button('🗑️', key=f"delete_{row['id']}"):
                                    if delete_transaction(row['id']):
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
                        # st.markdown("<hr style='margin-top:2rem;margin-bottom:2rem;border:1px solid #2d3436;'>",
                        #           unsafe_allow_html=True)
                        
                        left_button_space, col1, col2, right_button_space = st.columns([4,3,3,4])
                        with col1:
                            if st.button('Refresh Prices', key="reset_button", type="secondary"):
                                st.rerun()
                        
                        with col2:
                            if st.button('Clear All Transactions', type="secondary", key="clear_transactions"):
                                clear_transactions()
                                st.session_state.transactions = load_transactions()
                                st.success('All transactions cleared!')


            # Add this to your main app
            st.markdown("<hr>", unsafe_allow_html=True)
            st.header("New Balance if Withdrawal")

            if not st.session_state.transactions.empty:
                unique_coins = st.session_state.transactions['Asset'].unique()
                
                col1, col2 = st.columns([3, 7])
                
                with col1:
                    selected_coin = st.selectbox(
                        "Select Coin to Withdraw",
                        options=unique_coins,
                        key="withdrawal_coin"
                    )
                    
                    profit_data = calculate_profit_withdrawal_options(
                        st.session_state.transactions,
                        selected_coin
                    )
                    
                    if profit_data and profit_data['total_profit'] > 0:
                        # Show total profit
                        st.metric(
                            "Total Profit Available",
                            f"${profit_data['total_profit']:,.2f}",
                            help="Current profit for selected coin"
                        )
                        
                        # Reference targets
                        st.markdown("### Reference Targets")
                        ref_cols = st.columns(5)
                        for i, (label, data) in enumerate(profit_data['reference_targets'].items()):
                            with ref_cols[i]:
                                st.markdown(f"""
                                    <div style='text-align: center; border: 1px solid rgba(255,255,255,0.1); 
                                    padding: 5px; border-radius: 5px;'>
                                        <div style='font-size: 0.8em; color: rgba(255,255,255,0.6);'>{label}</div>
                                        <div style='font-size: 0.9em;'>${data['amount']:,.2f}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # Custom withdrawal input
                        st.markdown("### Custom Withdrawal")
                        withdrawal_amount = st.number_input(
                            "Enter withdrawal amount ($)",
                            min_value=0.0,
                            max_value=float(profit_data['total_profit']),
                            value=0.0,
                            step=100.0,
                            key="custom_withdrawal"
                        )
                        
                        # Show percentage of profit
                        if withdrawal_amount > 0:
                            withdrawal_percentage = (withdrawal_amount / profit_data['total_profit']) * 100
                            withdrawal_coins = withdrawal_amount / profit_data['current_price']
                            st.markdown(f"""
                                <div style='margin-top: 10px;'>
                                    <span style='color: rgba(255,255,255,0.6);'>This represents:</span><br/>
                                    • {withdrawal_percentage:.1f}% of your profit<br/>
                                    • {withdrawal_coins:.4f} coins
                                </div>
                            """, unsafe_allow_html=True)
                        

                        
                        if st.button("Calculate New Balance", type="secondary", key="calculate_new_balance"):
                            if withdrawal_amount > 0:
                                with col2:
                                    withdrawal_coins = withdrawal_amount / profit_data['current_price']
                                    st.markdown("### Impact Analysis")
                                    
                                    # Holdings
                                    st.markdown("#### Holdings")
                                    cols = st.columns(2)
                                    with cols[0]:
                                        st.metric(
                                            "Original Quantity",
                                            f"{profit_data['total_quantity']:.4f}"
                                        )
                                    with cols[1]:
                                        new_quantity = profit_data['total_quantity'] - withdrawal_coins
                                        st.metric(
                                            "New Quantity",
                                            f"{new_quantity:.4f}",
                                            delta=f"-{withdrawal_coins:.4f}"
                                        )
                                    
                                    # Investment Values
                                    st.markdown("#### Investment")
                                    withdrawal_ratio = withdrawal_coins / profit_data['total_quantity']
                                    new_invested = profit_data['total_invested'] * (1 - withdrawal_ratio)
                                    
                                    cols = st.columns(2)
                                    with cols[0]:
                                        st.metric(
                                            "Original Investment",
                                            f"${profit_data['total_invested']:,.2f}"
                                        )
                                    with cols[1]:
                                        st.metric(
                                            "New Investment",
                                            f"${new_invested:,.2f}",
                                            delta=f"-${profit_data['total_invested'] - new_invested:,.2f}"
                                        )
                                    
                                    # Market Value & P/L
                                    st.markdown("#### Market Value & P/L")
                                    new_market_value = new_quantity * profit_data['current_price']
                                    new_profit_loss = new_market_value - new_invested
                                    
                                    cols = st.columns(2)
                                    with cols[0]:
                                        st.metric(
                                            "Market Value",
                                            f"${profit_data['current_value']:,.2f}"
                                        )
                                    with cols[1]:
                                        st.metric(
                                            "New Market Value",
                                            f"${new_market_value:,.2f}",
                                            delta=f"-{withdrawal_amount:,.2f}"
                                        )
                                    
                                    pl_color = "normal" if new_profit_loss >= 0 else "inverse"
                                    st.metric(
                                        "New Profit/Loss",
                                        f"${new_profit_loss:,.2f}",
                                        delta=f"${new_profit_loss:,.2f}",
                                        delta_color=pl_color
                                    )
                    else:
                        st.warning("No profit available for withdrawal on this coin")
            else:
                st.info("No transactions available. Add some transactions to use this feature.")


            if auto_refresh:
                time.sleep(60)  # Wait for 60 second before next update
                st.rerun()
            else:
                break
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            time.sleep(15)
            continue

if __name__ == "__main__":
    main()