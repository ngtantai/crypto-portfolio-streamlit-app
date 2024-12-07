import streamlit as st

st.set_page_config(layout="wide", page_title="Crypto Dashboard")

# Custom CSS for the home page
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
        
        .welcome-text {
            font-size: 1.2rem;
            text-align: center;
            max-width: 800px;
            margin: 2rem auto;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

# Main content
st.title("🚀 Crypto Dashboard")
st.markdown("<p class='main-header'>Welcome to Your Crypto Dashboard</p>", unsafe_allow_html=True)

st.markdown("""
<div class='welcome-text'>
    This dashboard provides comprehensive cryptocurrency analysis and portfolio management tools. 
    Use the sidebar menu to navigate between different features:

    • Portfolio Management: Track your crypto investments and monitor performance
    • Market Analysis: Analyze historical data and trends for any cryptocurrency
</div>
""", unsafe_allow_html=True)

# Feature descriptions
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Portfolio Management")
    st.write("""
    - Track your cryptocurrency investments
    - Monitor real-time performance
    - View profit/loss analysis
    - Manage multiple transactions
    - Live price updates
    """)

with col2:
    st.markdown("### 📈 Market Analysis")
    st.write("""
    - Historical price data visualization
    - Technical analysis tools
    - Price change patterns
    - Volume analysis
    - Market trends
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Select a page from the sidebar to get started!
</div>
""", unsafe_allow_html=True)