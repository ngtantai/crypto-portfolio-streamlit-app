# import streamlit as st
# import requests
# import pandas as pd
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import json
# import os

# # Function to fetch crypto data from CoinGecko with adaptive intervals
# def fetch_crypto_data(crypto_id, days=1):
#     url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    
#     # Use hourly data for 24h period, daily for longer periods
#     interval = 'hourly' if days <= 1 else 'daily'
    
#     params = {
#         'vs_currency': 'usd',
#         'days': days,
#         'interval': interval
#     }
    
#     try:
#         response = requests.get(url, params=params)
#         data = response.json()
        
#         # Create DataFrame with proper timestamp and price
#         df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
#         df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
#         if days <= 1:
#             # For 24h period: Resample to hourly frequency
#             df.set_index('timestamp', inplace=True)
#             df = df.resample('H').last()  # Get last price of each hour
#             df = df.dropna()
#         else:
#             # For longer periods: Resample to daily frequency
#             df.set_index('timestamp', inplace=True)
#             df = df.resample('D').last()  # Get last price of each day
#             df = df.dropna()
        
#         return df
#     except Exception as e:
#         st.error(f"Error fetching data for {crypto_id}: {str(e)}")
#         return None
    

    
# # Initialize session state for storing purchase prices
# if 'purchase_prices' not in st.session_state:
#     # Try to load saved purchase prices from file
#     if os.path.exists('purchase_prices.json'):
#         with open('purchase_prices.json', 'r') as f:
#             st.session_state.purchase_prices = json.load(f)
#     else:
#         st.session_state.purchase_prices = {}

# # Function to save purchase prices to file
# def save_purchase_prices():
#     with open('purchase_prices.json', 'w') as f:
#         json.dump(st.session_state.purchase_prices, f)

# # Function to update purchase price
# def update_purchase_price(crypto_name, price):
#     st.session_state.purchase_prices[crypto_name] = price
#     save_purchase_prices()

# # Page config
# st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# # App title
# st.title("Cryptocurrency Dashboard")

# # Function to fetch crypto data from CoinGecko
# def fetch_crypto_data(crypto_id, days=1):
#     url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
#     params = {
#         'vs_currency': 'usd',
#         'days': days,
#         'interval': 'daily' if days > 1 else 'hourly'
#     }
    
#     try:
#         response = requests.get(url, params=params)
#         data = response.json()
#         df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
#         df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#         return df
#     except Exception as e:
#         st.error(f"Error fetching data for {crypto_id}: {str(e)}")
#         return None

# # Function to get current price
# def get_current_price(crypto_id):
#     url = f"https://api.coingecko.com/api/v3/simple/price"
#     params = {
#         'ids': crypto_id,
#         'vs_currencies': 'usd',
#         'include_24hr_change': 'true'
#     }
    
#     try:
#         response = requests.get(url, params=params)
#         data = response.json()
#         return {
#             'price': data[crypto_id]['usd'],
#             'change_24h': data[crypto_id].get('usd_24h_change', 0)
#         }
#     except Exception as e:
#         st.error(f"Error fetching price for {crypto_id}: {str(e)}")
#         return None

# # Updated available cryptocurrencies
# crypto_list = {
#     "Bitcoin": "bitcoin",
#     "Ethereum": "ethereum",
#     "XRP": "ripple",
#     "MATIC (Polygon)": "matic-network",
#     "ARB (Arbitrum)": "arbitrum",
#     "APT (Aptos)": "aptos",
#     "INJ (Injective)": "injective-protocol",
#     "DOGE (Dogecoin)": "dogecoin",
#     "AVAX (Avalanche)": "avalanche-2",
#     "ZRO (LayerZero)": "layerzero",
#     "OP (Optimism)": "optimism",
#     "STRK (Starknet)": "starknet",
#     "RNDR (Render)": "render-token",
#     "FET (Fetch.ai)": "fetch-ai",
#     "SUI": "sui",
#     "MANTA": "manta-network",
#     "ZK (ZKSync)": "zksync"
# }








# # Sidebar
# st.sidebar.header("Settings")

# # Time period selection
# time_periods = {
#     "24 Hours": 1,
#     "7 Days": 7,
#     "30 Days": 30,
#     "90 Days": 90,
#     "180 Days": 180,
#     "365 Days": 365
# }

# selected_period = st.sidebar.selectbox(
#     "Select Time Period",
#     list(time_periods.keys()),
#     index=2
# )

# # Add descriptions for new coins
# coin_descriptions = {
#     "XRP": "Digital payment protocol and cryptocurrency by Ripple Labs",
#     "ARB": "Layer 2 scaling solution using optimistic rollups",
#     "APT": "Layer 1 blockchain developed by former Meta (Facebook) employees",
#     "INJ": "Decentralized exchange protocol with cross-chain capabilities",
#     "AVAX": "High-performance, scalable blockchain platform",
#     "ZRO": "Omnichain interoperability protocol",
#     "OP": "Layer 2 scaling solution using optimistic rollups",
#     "STRK": "Decentralized Layer 2 scaling solution using STARK proofs",
#     "RNDR": "Decentralized GPU rendering network",
#     "FET": "Decentralized machine learning platform",
#     "SUI": "Layer 1 blockchain with high throughput",
#     "MANTA": "Privacy-preserving DeFi protocol",
#     "ZK": "Layer 2 scaling solution using zero-knowledge proofs"
# }

# # Add at the top of sidebar, before coin selection
# categories = {
#     "All": list(crypto_list.keys()),
#     "Layer 1": ["Bitcoin", "Ethereum", "AVAX (Avalanche)", "SUI", "APT (Aptos)", "XRP"],
#     "Layer 2": ["MATIC (Polygon)", "ARB (Arbitrum)", "OP (Optimism)", "STRK (Starknet)", "ZK (ZKSync)"],
#     "DeFi": ["INJ (Injective)", "MANTA"],
#     "Infrastructure": ["ZRO (LayerZero)", "RNDR (Render)", "FET (Fetch.ai)"],
#     "Meme": ["DOGE (Dogecoin)"]
# }

# selected_category = st.sidebar.radio(
#     "Filter by Category",
#     categories.keys()
# )

# # Update the multiselect options based on category
# available_cryptos = categories[selected_category]
# selected_cryptos = st.sidebar.multiselect(
#     "Select up to 5 cryptocurrencies",
#     available_cryptos,
#     default=["MATIC (Polygon)", "ZRO (LayerZero)"] if selected_category == "All" else [],
#     max_selections=5
# )

# # Add coin information section
# st.sidebar.markdown("---")
# st.sidebar.markdown("### Coin Information")
# selected_coin = st.sidebar.selectbox(
#     "Select a coin to learn more",
#     list(coin_descriptions.keys())
# )
# if selected_coin:
#     st.sidebar.info(coin_descriptions[selected_coin])

# # Update the Market Overview tab to show network info
# def get_network_info(crypto_name):
#     networks = {
#         "MATIC (Polygon)": "Ethereum Layer 2",
#         "ARB": "Ethereum Layer 2",
#         "OP": "Ethereum Layer 2",
#         "STRK": "Ethereum Layer 2",
#         "ZK": "Ethereum Layer 2",
#         "AVAX": "Layer 1",
#         "SUI": "Layer 1",
#         "XRP": "Layer 1",
#         "APT": "Layer 1"
#     }
#     return networks.get(crypto_name, "Information not available")

# if not selected_cryptos:
#     st.warning("Please select at least one cryptocurrency.")
#     st.stop()

# # Create tabs for different views
# tab1, tab2, tab3 = st.tabs(["Price Charts", "Market Overview", "Portfolio Tracker"])


# with tab1:
#     # Create a Plotly figure
#     fig = go.Figure()
    
#     # Add data for each selected cryptocurrency
#     for crypto_name in selected_cryptos:
#         crypto_id = crypto_list[crypto_name]
#         with st.spinner(f'Loading {crypto_name} data...'):
#             df = fetch_crypto_data(crypto_id, time_periods[selected_period])
#             if df is not None:
#                 fig.add_trace(
#                     go.Scatter(
#                         x=df.index,
#                         y=df['price'],
#                         name=crypto_name,
#                         mode='lines+markers+text',  # Add text mode
#                         marker=dict(
#                             size=6,
#                             line=dict(
#                                 width=1,
#                                 color='white'
#                             )
#                         ),
#                         text=[f"${price:,.2f}" for price in df['price']],
#                         textposition='top center',
#                         textfont=dict(
#                             size=10,
#                             color='black'
#                         ),
#                         hovertemplate=(
#                             f"<b>{crypto_name}</b><br>" +
#                             "Date: %{x|%Y-%m-%d}<br>" +
#                             "Price: $%{y:,.2f}<br>" +
#                             "<extra></extra>"
#                         )
#                     )
#                 )
    
#     # Update layout with light yellow background
#     fig.update_layout(
#         title={
#             'text': "Cryptocurrency Daily Closing Prices",
#             'y': 0.95,
#             'x': 0.5,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': dict(
#                 color='black',
#                 weight='bold',
#                 size=20
#             )
#         },
#         xaxis=dict(
#             title="Date",
#             showgrid=True,
#             gridwidth=1,
#             gridcolor='rgba(128, 128, 128, 0.2)',  # Softer grid lines
#             title_font=dict(
#                 color='black',
#                 weight='bold',
#                 size=14
#             ),
#             tickfont=dict(
#                 color='black',
#                 weight='bold',
#                 size=12
#             ),
#             tickformat='%Y-%m-%d',
#             dtick='D1'
#         ),
#         yaxis=dict(
#             title="Price (USD)",
#             showgrid=True,
#             gridwidth=1,
#             gridcolor='rgba(128, 128, 128, 0.2)',  # Softer grid lines
#             title_font=dict(
#                 color='black',
#                 weight='bold',
#                 size=14
#             ),
#             tickfont=dict(
#                 color='black',
#                 weight='bold',
#                 size=12
#             ),
#             tickprefix='$',
#             tickformat=',.2f'
#         ),
#         height=600,
#         hovermode='x unified',
#         legend=dict(
#             yanchor="top",
#             y=0.99,
#             xanchor="left",
#             x=0.01,
#             bgcolor='rgba(255, 255, 240, 0.8)',  # Light yellow legend background
#             font=dict(
#                 color='black',
#                 weight='bold',
#                 size=12
#             ),
#             bordercolor='rgba(0,0,0,0.2)',
#             borderwidth=1
#         ),
#         plot_bgcolor='rgba(255, 255, 224, 0.5)',  # Light yellow plot background
#         paper_bgcolor='rgba(255, 255, 240, 0.8)',  # Light yellow paper background
#         margin=dict(t=100)
#     )

#     # Add range selector buttons with matching style
#     fig.update_xaxes(
#         rangeslider_visible=False,
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=7, label="1W", step="day", stepmode="backward"),
#                 dict(count=1, label="1M", step="month", stepmode="backward"),
#                 dict(count=3, label="3M", step="month", stepmode="backward"),
#                 dict(count=6, label="6M", step="month", stepmode="backward"),
#                 dict(count=1, label="1Y", step="year", stepmode="backward"),
#                 dict(step="all", label="All")
#             ]),
#             font=dict(color="black", weight="bold"),
#             bgcolor='rgba(255, 255, 224, 0.8)',  # Light yellow button background
#             bordercolor='rgba(0,0,0,0.2)',
#             borderwidth=1,
#             x=0,
#             y=1,
#             yanchor='bottom'
#         )
#     )

#     # Add subtle box shadow to the chart
#     fig.update_layout(
#         shapes=[
#             dict(
#                 type='rect',
#                 xref='paper',
#                 yref='paper',
#                 x0=0,
#                 y0=0,
#                 x1=1,
#                 y1=1,
#                 line=dict(
#                     color='rgba(0,0,0,0.1)',
#                     width=1,
#                 ),
#                 fillcolor='rgba(0,0,0,0)',
#                 layer='below'
#             )
#         ]
#     )

#     # Make hover text bold and black with light yellow background
#     fig.update_traces(
#         hoverlabel=dict(
#             font=dict(
#                 color='black',
#                 weight='bold',
#                 size=12
#             ),
#             bgcolor='rgba(255, 255, 224, 0.95)'  # Light yellow hover background
#         )
#     )
    
#     # Display the plot
#     st.plotly_chart(fig, use_container_width=True)





# # Update the function definition to accept all the required parameters
# def update_purchase_price(crypto_name, purchase_price, holdings, invested_amount, platform):
#     try:
#         st.session_state.purchase_prices[crypto_name] = {
#             'price': float(purchase_price),
#             'holdings': float(holdings),
#             'invested_amount': float(invested_amount),
#             'platform': platform,
#             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }
#         save_purchase_prices()
#         return True
#     except Exception as e:
#         st.error(f"Error saving data: {str(e)}")
#         return False



# with tab2:
#     # Add educational information at the top
#     with st.expander("📚 Understanding Holdings and Position Tracking"):
#         st.markdown("""
#         ### What are Holdings?
#         Holdings refer to the quantity of cryptocurrency you own. It's a crucial metric for portfolio management:
        
#         - **Definition**: The actual amount of coins/tokens you possess
#         - **Example**: If you own 0.5 BTC, your Bitcoin holdings are 0.5
        
#         ### Why Holdings are Important:
#         1. **Position Value Calculation**:
#            - Total Value = Current Price × Holdings
#            - Example: If BTC price is $50,000 and you hold 0.5 BTC
#            - Position Value = $50,000 × 0.5 = $25,000

#         2. **Profit/Loss Tracking**:
#            - P&L = (Current Price - Purchase Price) × Holdings
#            - Example: If you bought at $40,000 and current price is $50,000
#            - Per coin profit = $50,000 - $40,000 = $10,000
#            - Total profit = $10,000 × 0.5 = $5,000

#         3. **Portfolio Management**:
#            - Track exposure to different cryptocurrencies
#            - Manage risk through position sizing
#            - Monitor portfolio diversification
#         """)

#     st.subheader("Market Overview & Position Tracker")
    
#     # Initialize the current_prices dictionary
#     current_prices = {}
    
#     # Available trading platforms
#     platforms = ["Coinbase", "Bybit"]
    
#     # Function to safely get saved data
#     def get_saved_data(crypto_name):
#         saved_data = st.session_state.purchase_prices.get(crypto_name, {})
#         if isinstance(saved_data, dict):
#             return {
#                 'price': saved_data.get('price', 0.0),
#                 'holdings': saved_data.get('holdings', 0.0),
#                 'invested_amount': saved_data.get('invested_amount', 0.0),
#                 'platform': saved_data.get('platform', platforms[0])
#             }
#         else:
#             return {
#                 'price': float(saved_data) if saved_data else 0.0,
#                 'holdings': 0.0,
#                 'invested_amount': 0.0,
#                 'platform': platforms[0]
#             }

#     # Create columns for metrics
#     for crypto_name in selected_cryptos:
#         st.markdown("---")
#         col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 1.5])
        
#         crypto_id = crypto_list[crypto_name]
#         data = get_current_price(crypto_id)
        
#         if data:
#             current_price = data['price']
#             current_prices[crypto_name] = current_price
            
#             # Column 1: Display current price and 24h change
#             with col1:
#                 st.metric(
#                     label=f"{crypto_name} Current Price",
#                     value=f"${current_price:,.4f}",
#                     delta=f"{data['change_24h']:.2f}%",
#                     delta_color="normal" if data['change_24h'] >= 0 else "inverse"
#                 )
            
#             # Get saved data using the safe function
#             saved_data = get_saved_data(crypto_name)
#             saved_price = saved_data['price']
#             saved_holdings = saved_data['holdings']
#             saved_investment = saved_data['invested_amount']
#             saved_platform = saved_data['platform']
            
#             # Column 2: Input field for purchase price
#             with col2:
#                 new_price = st.number_input(
#                     f"Purchase Price ($)",
#                     min_value=0.0,
#                     value=float(saved_price),
#                     format="%.4f",
#                     key=f"purchase_price_{crypto_name}" 
#                 )
            
#             # Column 3: Input fields for holdings and investment with calculation option
#             with col3:
#                 calc_method = st.radio(
#                     "Holdings Input Method",
#                     ["Calculate from Investment", "Manual"],
#                     key=f"calc_method_{crypto_name}",
#                     horizontal=True,
#                     label_visibility="collapsed"
#                 )
                
#                 invested_amount = st.number_input(
#                     f"Investment ($)",
#                     min_value=0.0,
#                     value=float(saved_investment),
#                     format="%.2f",
#                     key=f"investment_{crypto_name}"
#                 )
                
#                 if calc_method == "Manual":
#                     holdings = st.number_input(
#                         f"Holdings",
#                         min_value=0.0,
#                         value=float(saved_holdings),
#                         format="%.4f",
#                         key=f"holdings_{crypto_name}"
#                     )
#                 else:
#                     # Calculate holdings from investment amount
#                     if new_price > 0:
#                         holdings = invested_amount / new_price
#                         st.markdown(f"""
#                         <div style='margin-top: 1em;'>
#                             <div style='font-size: 0.8em; color: gray;'>Calculated Holdings:</div>
#                             <div style='font-size: 1.1em; font-weight: bold;'>{holdings:,.4f}</div>
#                         </div>
#                         """, unsafe_allow_html=True)
#                     else:
#                         holdings = 0
#                         st.warning("Enter purchase price to calculate holdings")

#             # Column 4: Platform selection
#             with col4:
#                 platform = st.selectbox(
#                     "Platform",
#                     options=platforms,
#                     index=platforms.index(saved_platform) if saved_platform in platforms else 0,
#                     key=f"platform_{crypto_name}"
#                 )
                
#                 if st.button(f"Save", key=f"save_{crypto_name}"):
#                     update_purchase_price(crypto_name, new_price, holdings, invested_amount, platform)
#                     st.success("Position saved!")
            
#             # Column 5: P&L Display
#             with col5:
#                 if new_price > 0 and holdings > 0:
#                     current_value = current_price * holdings
#                     pl_amount = current_value - invested_amount
#                     pl_percentage = (pl_amount / invested_amount * 100) if invested_amount > 0 else 0
#                     pl_color = "green" if pl_amount >= 0 else "red"
                    
#                     st.markdown("##### P&L")
#                     st.markdown(f"""
#                     <div style='color: {pl_color}'>
#                         <strong>Amount:</strong> ${pl_amount:,.2f}<br>
#                         <strong>Percentage:</strong> {pl_percentage:.2f}%
#                     </div>
#                     """, unsafe_allow_html=True)
                    
#                     st.markdown(f"""
#                     <div style='margin-top: 10px;'>
#                         <strong>Position Value:</strong><br>
#                         ${current_value:,.2f}
#                     </div>
#                     <div style='margin-top: 10px; font-size: 0.8em;'>
#                         <strong>Platform:</strong> {platform}<br>
#                         <strong>Investment:</strong> ${invested_amount:,.2f}
#                     </div>
#                     """, unsafe_allow_html=True)

#     # Platform Summary section
#     # In the Platform Summary section, update the DataFrame creation:
#     if current_prices:  # Only show summary if we have prices
#         st.markdown("---")
#         st.subheader("Summary by Platform")
        
#         # Calculate totals by platform
#         platform_summary = {}
#         for platform in platforms:
#             platform_summary[platform] = {
#                 'investment': 0,
#                 'current_value': 0,
#                 'pl_amount': 0
#             }
        
#         # Create data list with proper dictionary structure
#         data_list = []
        
#         for crypto_name, position in st.session_state.purchase_prices.items():
#             if isinstance(position, dict) and crypto_name in current_prices:
#                 platform = position.get('platform')
#                 if platform in platform_summary:
#                     investment = position.get('invested_amount', 0)
#                     holdings = position.get('holdings', 0)
#                     current_value = current_prices[crypto_name] * holdings
#                     pl_amount = current_value - investment
                    
#                     platform_summary[platform]['investment'] += investment
#                     platform_summary[platform]['current_value'] += current_value
#                     platform_summary[platform]['pl_amount'] += pl_amount
                    
#                     # Add to data list for DataFrame
#                     data_list.append({
#                         'Cryptocurrency': crypto_name,
#                         'Platform': platform,
#                         'Holdings': f"{holdings:,.4f}",
#                         'Purchase Price': f"${position.get('price', 0):,.4f}",
#                         'Current Price': f"${current_prices[crypto_name]:,.4f}",
#                         'Investment': f"${investment:,.2f}",
#                         'Current Value': f"${current_value:,.2f}",
#                         'P&L': f"${pl_amount:,.2f}",
#                         'Last Updated': position.get('timestamp', 'N/A')
#                     })
        
#         # Create DataFrame with explicit index
#         if data_list:
#             df = pd.DataFrame(data_list, index=range(len(data_list)))
#             st.markdown("##### Detailed Portfolio Breakdown")
#             st.dataframe(df, use_container_width=True)

#         # Display platform summaries
#         cols = st.columns(len(platforms))
#         for idx, (platform, data) in enumerate(platform_summary.items()):
#             with cols[idx]:
#                 st.markdown(f"##### {platform}")
#                 investment = data['investment']
#                 current_value = data['current_value']
#                 pl_amount = data['pl_amount']
#                 pl_percentage = (pl_amount / investment * 100) if investment > 0 else 0
                
#                 st.metric(
#                     label="Total Investment",
#                     value=f"${investment:,.2f}"
#                 )
#                 st.metric(
#                     label="Current Value",
#                     value=f"${current_value:,.2f}"
#                 )
#                 st.metric(
#                     label="P&L",
#                     value=f"${pl_amount:,.2f}",
#                     delta=f"{pl_percentage:.2f}%",
#                     delta_color="normal" if pl_amount >= 0 else "inverse"
#                 )



# with tab3:
#     st.subheader("Portfolio Summary")

#     # In the Platform Summary section, update the DataFrame creation:
#     if current_prices:  # Only show summary if we have prices
#         st.markdown("---")
#         st.subheader("Summary by Platform")
        
#         # Calculate totals by platform
#         platform_summary = {}
#         for platform in platforms:
#             platform_summary[platform] = {
#                 'investment': 0,
#                 'current_value': 0,
#                 'pl_amount': 0
#             }
        
#         # Create data list with proper dictionary structure
#         data_list = []
        
#         for crypto_name, position in st.session_state.purchase_prices.items():
#             if isinstance(position, dict) and crypto_name in current_prices:
#                 platform = position.get('platform')
#                 if platform in platform_summary:
#                     investment = position.get('invested_amount', 0)
#                     holdings = position.get('holdings', 0)
#                     current_value = current_prices[crypto_name] * holdings
#                     pl_amount = current_value - investment
                    
#                     platform_summary[platform]['investment'] += investment
#                     platform_summary[platform]['current_value'] += current_value
#                     platform_summary[platform]['pl_amount'] += pl_amount
                    
#                     # Add to data list for DataFrame
#                     data_list.append({
#                         'Cryptocurrency': crypto_name,
#                         'Platform': platform,
#                         'Holdings': f"{holdings:,.4f}",
#                         'Purchase Price': f"${position.get('price', 0):,.4f}",
#                         'Current Price': f"${current_prices[crypto_name]:,.4f}",
#                         'Investment': f"${investment:,.2f}",
#                         'Current Value': f"${current_value:,.2f}",
#                         'P&L': f"${pl_amount:,.2f}",
#                         'Last Updated': position.get('timestamp', 'N/A')
#                     })
        
#         # Create DataFrame with explicit index
#         if data_list:
#             df = pd.DataFrame(data_list, index=range(len(data_list)))
#             st.markdown("##### Detailed Portfolio Breakdown")
#             st.dataframe(df, use_container_width=True)

#         # Display platform summaries
#         cols = st.columns(len(platforms))
#         for idx, (platform, data) in enumerate(platform_summary.items()):
#             with cols[idx]:
#                 st.markdown(f"##### {platform}")
#                 investment = data['investment']
#                 current_value = data['current_value']
#                 pl_amount = data['pl_amount']
#                 pl_percentage = (pl_amount / investment * 100) if investment > 0 else 0
                
#                 st.metric(
#                     label="Total Investment",
#                     value=f"${investment:,.2f}"
#                 )
#                 st.metric(
#                     label="Current Value",
#                     value=f"${current_value:,.2f}"
#                 )
#                 st.metric(
#                     label="P&L",
#                     value=f"${pl_amount:,.2f}",
#                     delta=f"{pl_percentage:.2f}%",
#                     delta_color="normal" if pl_amount >= 0 else "inverse"
#                 )
    
#     # # Create a summary table of all tracked investments
#     # if st.session_state.purchase_prices:
#     #     data = []
#     # for crypto_name, position in st.session_state.purchase_prices.items():
#     #     if isinstance(position, dict) and crypto_name in selected_cryptos:  # Only include selected cryptos
#     #         # Get current price
#     #         current_price = current_prices.get(crypto_name, 0)
#     #         holdings = position.get('holdings', 0)
#     #         purchase_price = position.get('price', 0)
#     #         platform = position.get('platform', 'Unknown')  # Default to 'Unknown' if not found
            
#     #         # Calculate values
#     #         investment = purchase_price * holdings
#     #         current_value = current_price * holdings
#     #         pl_amount = current_value - investment
#     #         pl_percentage = (pl_amount / investment * 100) if investment > 0 else 0
            
#     #         data.append({
#     #             "Cryptocurrency": crypto_name,
#     #             "Platform": platform,
#     #             "Holdings": f"{holdings:,.4f}",
#     #             "Purchase Price": f"${purchase_price:,.4f}",
#     #             "Current Price": f"${current_price:,.4f}",
#     #             "Investment": f"${investment:,.2f}",
#     #             "Current Value": f"${current_value:,.2f}",
#     #             "P&L": f"${pl_amount:,.2f} ({pl_percentage:.2f}%)",
#     #             "Last Updated": position.get('timestamp', 'N/A')
#     #         })
#     #         st.write(data)
#             # data = [
#             #     {
#             #         "Cryptocurrency": crypto_name
#             #         # "Platform": platform,
#             #         # "Holdings": holdings,
#             #         # "Purchase Price": purchase_price,
#             #         # "Current Price": current_price,
#             #         # "Investment": investment,
#             #         # "Current Value": current_value,
#             #         # "P&L": pl_amount,
#             #         # "P&L %": pl_percentage,
#             #         # "Last Updated": position.get('timestamp', 'N/A')
#             #     }
#             # ]
    
#     # if data:
#     #     # Create DataFrame for display
#     #     df = pd.DataFrame(data)
#     #     # df = pd.DataFrame(data, columns=[
#     #     #     "Cryptocurrency", "Platform", "Holdings", "Purchase Price", "Current Price",
#     #     #     "Investment", "Current Value", "P&L", "P&L %", "Last Updated"
#     #     # ], dtype={
#     #     #     "Holdings": float, "Purchase Price": float, "Current Price": float,
#     #     #     "Investment": float, "Current Value": float, "P&L": float, "P&L %": str
#     #     # })
#     #     st.markdown("##### Detailed Portfolio Breakdown")
#     #     st.dataframe(df, use_container_width=True)

#     #     # Platform Summary
#     #     st.markdown("---")
#     #     st.subheader("Summary by Platform")
        
#     #     # Calculate totals by platform
#     #     platform_summary = {}
#     #     for entry in data:
#     #         platform = entry['Platform']
#     #         if platform not in platform_summary:
#     #             platform_summary[platform] = {
#     #                 'investment': 0,
#     #                 'current_value': 0,
#     #                 'pl_amount': 0
#     #             }
            
#     #         # Strip currency symbols and convert to float
#     #         investment = float(entry['Investment'].replace('$', '').replace(',', ''))
#     #         current_value = float(entry['Current Value'].replace('$', '').replace(',', ''))
#     #         pl_amount = current_value - investment
            
#     #         platform_summary[platform]['investment'] += investment
#     #         platform_summary[platform]['current_value'] += current_value
#     #         platform_summary[platform]['pl_amount'] += pl_amount
        
#     #     # Display platform summaries
#     #     cols = st.columns(len(platform_summary))
#     #     for idx, (platform, data) in enumerate(platform_summary.items()):
#     #         with cols[idx]:
#     #             st.markdown(f"##### {platform}")
#     #             investment = data['investment']
#     #             current_value = data['current_value']
#     #             pl_amount = data['pl_amount']
#     #             pl_percentage = (pl_amount / investment * 100) if investment > 0 else 0
                
#     #             st.metric(
#     #                 label="Total Investment",
#     #                 value=f"${investment:,.2f}"
#     #             )
#     #             st.metric(
#     #                 label="Current Value",
#     #                 value=f"${current_value:,.2f}"
#     #             )
#     #             st.metric(
#     #                 label="P&L",
#     #                 value=f"${pl_amount:,.2f}",
#     #                 delta=f"{pl_percentage:.2f}%",
#     #                 delta_color="normal" if pl_amount >= 0 else "inverse"
#     #             )
#     # else:
#     #     st.info("No positions saved yet. Add your purchase prices in the Market Overview tab to track your portfolio.")

# # Add clear data button in sidebar
# if st.sidebar.button("Clear All Saved Data"):
#     st.session_state.purchase_prices = {}
#     if os.path.exists('purchase_prices.json'):
#         os.remove('purchase_prices.json')
#     st.sidebar.success("All saved data cleared!")

# # Add information about POL and LayerZero
# st.subheader("Additional Information")
# st.info("""
# - POL (formerly MATIC): Polygon's token that powers the Polygon network, a scaling solution that aims to provide multiple tools to improve the speed and reduce the costs and complexities of transactions on blockchain networks.
# - LayerZero (ZRO): An omnichain interoperability protocol designed to enable lightweight cross-chain communication, powering the future of cross-chain applications.
# """)

# # Add rate limit warning
# st.sidebar.warning("""
# Note: This app uses the CoinGecko free API which has rate limits.
# If you see errors, please wait a few seconds and try again.
# """)

# # Footer with last updated timestamp
# st.markdown("---")
# st.markdown("""
# Data provided by CoinGecko API | Last updated: {}
# """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))