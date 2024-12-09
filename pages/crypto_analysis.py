import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from config import get_db_path
import sqlite3
# Page configuration
st.set_page_config(layout="wide", page_title="Crypto Analysis")

# Custom CSS
st.markdown("""
    <style>
        /* Import Poppins font */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Global styles */
        html, body, [class*="css"], [class*="st-"] {
            font-family: 'Poppins', sans-serif;
        }
        
        /* Header styling */
        .main-header {
            color: #FFD700;
            text-align: center;
            padding: 1rem 0;
            letter-spacing: 2px;
        }
        
        /* Card styling */
        .metric-card {
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Table styling */
        .dataframe {
            width: 100%;
            text-align: center;
        }
        
        .dataframe th {
            background-color: #2E2E2E;
            padding: 12px;
        }
        
        .dataframe td {
            padding: 10px;
        }
        
        /* Chart container */
        .chart-container {
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 1rem;
            margin-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Cache the coin list
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


@st.cache_data(ttl=300)
def get_historical_crypto_data(coin_id, days=365):
    """Fetch historical price data from CoinGecko with proper hourly granularity"""
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
        params = {
            'vs_currency': 'usd',
            'days': min(days, 90),  # Limit to 90 days for hourly data
            'interval': 'hourly'    # Always request hourly data for shorter periods
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Create DataFrame with timestamp as index
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'close'])
            df['volume'] = pd.DataFrame(data['total_volumes'])[1]
            df['market_cap'] = pd.DataFrame(data['market_caps'])[1]
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Sort index to ensure chronological order
            df = df.sort_index()
            
            # Calculate hourly price changes
            df['price_change'] = df['close'].pct_change()
            
            return df
            
        return None
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        return None




def create_price_chart(df, coin_name):
    """Create an interactive candlestick chart using Plotly"""
    # First create OHLC data
    ohlc_data = df['close'].resample('D').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).dropna()
    
    # Create volume and market cap daily data
    volume_data = df['volume'].resample('D').sum()
    market_cap_data = df['market_cap'].resample('D').last()
    
    fig = make_subplots(rows=3, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.05,
                       subplot_titles=('Price (USD)', 'Volume', 'Market Cap'),
                       row_heights=[0.6, 0.2, 0.2])

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=ohlc_data.index,
            open=ohlc_data['open'],
            high=ohlc_data['high'],
            low=ohlc_data['low'],
            close=ohlc_data['close'],
            name='Price'
        ),
        row=1, col=1
    )

    # Volume chart with colors matching price direction
    colors = ['red' if close < open else 'green' 
             for close, open in zip(ohlc_data['close'], ohlc_data['open'])]
    
    fig.add_trace(
        go.Bar(
            x=volume_data.index,
            y=volume_data,
            name='Volume',
            marker_color=colors,
            opacity=0.8
        ),
        row=2, col=1
    )

    # Market Cap chart
    fig.add_trace(
        go.Scatter(
            x=market_cap_data.index,
            y=market_cap_data,
            name='Market Cap',
            fill='tozeroy',
            line=dict(color='rgb(0,150,255)')
        ),
        row=3, col=1
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text=f'{coin_name} Price Chart',
            font=dict(size=24)
        ),
        height=800,
        template='plotly_dark',
        showlegend=False,
        yaxis_title='Price (USD)',
        yaxis2_title='Volume',
        yaxis3_title='Market Cap',
        xaxis_rangeslider_visible=False
    )

    # Update y-axes
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="Market Cap", row=3, col=1)

    # Update candlestick colors
    fig.update_traces(
        increasing_line_color='#00FF00',
        decreasing_line_color='#FF0000',
        selector=dict(type='candlestick')
    )

    return fig





def format_large_number(num):
    """Format large numbers with K, M, B, T suffixes"""
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T'][magnitude])



def create_calendar_view(df):
    """Create a calendar view of the data with months as rows and days as columns"""
    # Create copies of the timestamp for month and day
    df_copy = df.copy()
    
    # Use 'close' price instead of 'price' for calculations
    df_copy['month'] = df_copy.index.strftime('%Y-%m')
    df_copy['day'] = df_copy.index.day
    
    # Calculate daily price changes using close prices
    df_copy['price_change'] = df_copy['close'].pct_change()
    
    # Create pivot tables
    calendar_view = pd.pivot_table(
        df_copy,
        values='close',  # Use 'close' instead of 'price'
        index='month',
        columns='day',
        aggfunc='last'
    )
    
    changes_view = pd.pivot_table(
        df_copy,
        values='price_change',
        index='month',
        columns='day',
        aggfunc='last'
    )
    
    # Create style conditions
    def style_negative_positive(value):
        if pd.isna(value):
            return ''
            
        if isinstance(value, str):
            return ''
            
        # Determine color intensity based on value
        intensity = min(abs(value) * 5, 1.0)  # Cap at 100% intensity
        
        if value >= 0:
            color = f'background-color: rgba(0, 255, 0, {intensity})'
        else:
            color = f'background-color: rgba(255, 0, 0, {intensity})'
            
        return color

    # Format prices
    formatted_prices = calendar_view.round(2)
    
    # Apply styles and format numbers
    styled_calendar = formatted_prices.style\
        .map(style_negative_positive)\
        .format("${:,.2f}", na_rep="")
        
    # Format and style changes
    changes_formatted = changes_view.multiply(100).round(2)
    styled_changes = changes_formatted.style\
        .map(style_negative_positive)\
        .format("{:+.2f}%", na_rep="")
    
    return styled_calendar, styled_changes




def create_hourly_view(df):
    """Create an hourly view of the data with month-day as rows and hours as columns"""
    # Create a copy of the dataframe
    df_hourly = df.copy()
    
    # Create month-day and hour columns
    df_hourly['month_day'] = df_hourly.index.strftime('%Y-%m-%d')
    df_hourly['hour'] = df_hourly.index.hour
    
    # Calculate hourly price changes
    df_hourly['price_change'] = df_hourly['close'].pct_change()
    
    # Create list of all possible hours (0-23)
    all_hours = list(range(24))
    
    # Create pivot tables
    hourly_prices = pd.pivot_table(
        df_hourly,
        values='close',
        index='month_day',
        columns='hour',
        aggfunc='last'
    ).reindex(columns=all_hours)
    
    hourly_changes = pd.pivot_table(
        df_hourly,
        values='price_change',
        index='month_day',
        columns='hour',
        aggfunc='last'
    ).reindex(columns=all_hours)
    
    def style_changes(val):
        if pd.isna(val):
            return ''
        intensity = min(abs(val) * 5, 1.0)
        color = 'rgba(0, 255, 0, {})'.format(intensity) if val >= 0 else 'rgba(255, 0, 0, {})'.format(intensity)
        return f'background-color: {color}'
    
    # Format column headers to show hour in 24-hour format
    hourly_prices.columns = [f'{hour:02d}:00' for hour in hourly_prices.columns]
    hourly_changes.columns = [f'{hour:02d}:00' for hour in hourly_changes.columns]
    
    # Style the DataFrames
    styled_prices = hourly_prices.style\
        .format("${:,.2f}", na_rep="None")\
        .apply(lambda x: ['background-color: rgba(0,255,0,0.2)' if v >= 0 else 'background-color: rgba(255,0,0,0.2)' 
                         for v in x], axis=1)
    
    styled_changes = hourly_changes.style\
        .format("{:,.2f}%", na_rep="None")\
        .apply(lambda x: [style_changes(v) for v in x], axis=1)
    
    return styled_prices, styled_changes




def display_historical_data(df):
    """Display historical data in a formatted table"""
    # Create a copy of the dataframe for display
    display_df = df.copy()
    
    # Format the display dataframe
    display_df = pd.DataFrame({
        'Date': display_df.index,
        'Close Price': display_df['close'],
        'Volume': display_df['volume'],
        'Market Cap': display_df['market_cap']
    })

    # Format the columns
    display_df['Close Price'] = display_df['Close Price'].map('${:,.2f}'.format)
    display_df['Volume'] = display_df['Volume'].map(format_large_number)
    display_df['Market Cap'] = display_df['Market Cap'].map(format_large_number)
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    
    # Display the dataframe
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        height=400
    )

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

def load_transactions():
    """Load all transactions from the database"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Error loading transactions: {e}")
        return pd.DataFrame()
    
def main():
    # Initialize database if not exists
    if 'db_initialized' not in st.session_state:
        init_database()
        st.session_state.db_initialized = True
    st.title("🔍 Cryptocurrency Analysis Dashboard")
    st.markdown("<p class='main-header'>Analyze historical cryptocurrency data and trends</p>", 
                unsafe_allow_html=True)

    # Sidebar controls
    st.sidebar.title("Analysis Controls")
    
    # Coin selection
    coins = fetch_available_coins()
    selected_coin = st.sidebar.selectbox(
        "Select Cryptocurrency",
        options=[""] + list(coins.keys())
    )
    
    # Time period selection
    time_periods = {
        '7 days': 7,
        '30 days': 30,
        '90 days': 90,
        '180 days': 180,
        '1 year': 365,
        'Max': 'max'
    }
    selected_period = st.sidebar.selectbox(
        "Select Time Period",
        options=list(time_periods.keys())
    )

    if selected_coin and selected_period:
        # Modify the time period selection to warn about data limitations
        if time_periods[selected_period] > 90:
            st.warning("""
                Note: Hourly price data is only available for the last 90 days.
                For longer periods, only daily data (00:00 UTC) will be shown.
            """)

        coin_id = coins[selected_coin]
        days = time_periods[selected_period]
        
        with st.spinner('Fetching historical data...'):
            days = time_periods[selected_period]
            if days > 90:
                st.warning("Hourly data is only available for periods up to 90 days. Please select a shorter time range for detailed hourly analysis.")
                days = 90  # Limit to 90 days for hourly data
            
            df = get_historical_crypto_data(coin_id, days)
            
            if df is not None:
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    current_price = df['close'].iloc[-1]
                    price_change = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
                    st.metric(
                        "Current Price",
                        f"${current_price:,.2f}",
                        f"{price_change:+.2f}%"
                    )
                
                with col2:
                    current_volume = df['volume'].iloc[-1]
                    volume_change = ((current_volume - df['volume'].iloc[-2]) / df['volume'].iloc[-2]) * 100
                    st.metric(
                        "24h Volume",
                        format_large_number(current_volume),
                        f"{volume_change:+.2f}%"
                    )
                
                with col3:
                    current_mcap = df['market_cap'].iloc[-1]
                    mcap_change = ((current_mcap - df['market_cap'].iloc[-2]) / df['market_cap'].iloc[-2]) * 100
                    st.metric(
                        "Market Cap",
                        format_large_number(current_mcap),
                        f"{mcap_change:+.2f}%"
                    )

                # Display chart
                # st.plotly_chart(create_price_chart(df, selected_coin), use_container_width=True)


                # Display chart
                st.plotly_chart(create_price_chart(df, selected_coin), use_container_width=True)

                # After displaying the first dataframe, add:
                st.subheader("Monthly Calendar View")
                
                # Create tabs for different views
                price_tab, change_tab = st.tabs(["Price Values", "Price Changes (%)"])
                
                # Get calendar views
                calendar_prices, calendar_changes = create_calendar_view(df)
                
                with price_tab:
                    st.markdown("### Daily Closing Prices")
                    st.dataframe(
                        calendar_prices,
                        use_container_width=True,
                        height=400
                    )
                
                with change_tab:
                    st.markdown("### Daily Price Changes (%)")
                    st.dataframe(
                        calendar_changes,
                        use_container_width=True,
                        height=400
                    )

                # Add description of the views
                st.markdown("""
                **Calendar View Guide:**
                - Price Values tab shows closing prices for each day
                - Price Changes tab shows daily percentage changes
                - Empty cells indicate no data for that day
                - Green indicates positive change, Red indicates negative change
                """)


                # Hourly view section
                st.subheader("Hourly Price Analysis")
                hourly_price_tab, hourly_change_tab = st.tabs(["Hourly Prices", "Hourly Changes (%)"])
                
                try:
                    hourly_prices, hourly_changes = create_hourly_view(df)
                    
                    with hourly_price_tab:
                        st.markdown("### Hourly Closing Prices")
                        st.dataframe(hourly_prices, use_container_width=True, height=600)
                    
                    with hourly_change_tab:
                        st.markdown("### Hourly Price Changes (%)")
                        st.dataframe(hourly_changes, use_container_width=True, height=600)
                        
                except Exception as e:
                    st.warning("Unable to generate hourly view. This might be due to limited data points.")
                    st.error(f"Error details: {str(e)}")

                
                # Display data table
                if df is not None:
                    st.subheader("Historical Data")
                    display_historical_data(df)

                # Add download button
                csv = df.to_csv()
                st.download_button(
                    label="Download Data as CSV",
                    data=csv,
                    file_name=f'{selected_coin}_historical_data.csv',
                    mime='text/csv',
                )
    else:
        st.info("Please select a cryptocurrency and time period to begin analysis.")

if __name__ == "__main__":
    main()