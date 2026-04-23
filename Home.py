"""
Home.py - Trading Command Center Dashboard
"""

import streamlit as st

st.set_page_config(
    page_title="Trading Command Center",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }
    .step-card {
        background: #1e2a3a;
        border-radius: 20px;
        padding: 30px;
        margin: 10px;
        border: 1px solid #334155;
        transition: transform 0.2s;
        height: 100%;
    }
    .step-card:hover {
        transform: translateY(-5px);
        border-color: #667eea;
    }
    .step-number {
        background: #667eea;
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .data-bar {
        background: #0f172a;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #334155;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🎯 Trading Command Center</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 1.2rem; margin-bottom: 40px;">Find → Analyze → Execute — All in one place</p>', unsafe_allow_html=True)

# Initialize shared session state
if 'shared_ticker' not in st.session_state:
    st.session_state.shared_ticker = "AAPL"
if 'shared_entry' not in st.session_state:
    st.session_state.shared_entry = 180.00
if 'shared_stop' not in st.session_state:
    st.session_state.shared_stop = 175.00
if 'shared_direction' not in st.session_state:
    st.session_state.shared_direction = "LONG"
if 'shared_score' not in st.session_state:
    st.session_state.shared_score = 0
if 'shared_support' not in st.session_state:
    st.session_state.shared_support = 175.00
if 'shared_resistance' not in st.session_state:
    st.session_state.shared_resistance = 190.00
if 'shared_atr' not in st.session_state:
    st.session_state.shared_atr = 3.50

# Shared data bar
st.markdown("### 💾 Shared Trade Data")
st.markdown('<div class="data-bar">', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.session_state.shared_ticker = st.text_input("📈 Ticker", value=st.session_state.shared_ticker).upper()
with col2:
    st.session_state.shared_entry = st.number_input("💰 Entry Price", value=st.session_state.shared_entry, step=0.01, format="%.2f")
with col3:
    st.session_state.shared_stop = st.number_input("🛑 Stop Loss", value=st.session_state.shared_stop, step=0.01, format="%.2f")
with col4:
    st.session_state.shared_direction = st.radio("📊 Direction", ["LONG", "SHORT"], horizontal=True)
with col5:
    st.metric("Entry Score", f"{st.session_state.shared_score}/100")

st.markdown('</div>', unsafe_allow_html=True)
st.caption("Data entered here is shared across Scanner, Entry Analyzer, and Exit Planner")

st.divider()

# Workflow cards
st.markdown("### 📋 Workflow")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">1</div>
        <h2 style="color: white;">🔍 Scanner</h2>
        <p style="color: #94a3b8; min-height: 80px;">Scan 400+ tickers across multiple watchlists. Find high-probability setups ranked by technical score.</p>
        <p style="color: #667eea;">➡️ Select "Scanner" from sidebar</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">2</div>
        <h2 style="color: white;">📈 Entry Analyzer</h2>
        <p style="color: #94a3b8; min-height: 80px;">Confirm entry signals with comprehensive technical analysis. Get confidence score and suggested stops.</p>
        <p style="color: #667eea;">➡️ Select "Entry Analyzer" from sidebar</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">3</div>
        <h2 style="color: white;">🎯 Exit Planner</h2>
        <p style="color: #94a3b8; min-height: 80px;">Calculate position size, stop losses, and take profit levels. Export complete trade plans.</p>
        <p style="color: #667eea;">➡️ Select "Exit Planner" from sidebar</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Quick start
st.markdown("### 🚀 Quick Start")
st.markdown("""
1. **Start with Scanner** (sidebar → Scanner) — Select a watchlist and run scan
2. **Pick a high-scoring ticker** — Look for score 8+ (green)
3. **Go to Entry Analyzer** — Click "Use This Ticker" to confirm signal
4. **If score 60+** — Go to Exit Planner
5. **Calculate position size** — Enter account size and risk %
6. **Execute with confidence** — You have a complete plan
""")

# Current status
st.divider()
st.markdown("### 📊 Current Trade Status")
status_col1, status_col2, status_col3, status_col4 = st.columns(4)
with status_col1:
    st.metric("Ticker", st.session_state.shared_ticker)
with status_col2:
    st.metric("Direction", st.session_state.shared_direction)
with status_col3:
    risk_distance = abs(st.session_state.shared_entry - st.session_state.shared_stop)
    risk_pct = (risk_distance / st.session_state.shared_entry) * 100
    st.metric("Risk Distance", f"${risk_distance:.2f} ({risk_pct:.2f}%)")
with status_col4:
    if st.session_state.shared_score >= 60:
        st.success("✅ Ready to Trade")
    elif st.session_state.shared_score >= 40:
        st.warning("⚠️ Review Carefully")
    else:
        st.error("❌ Not Ready")

st.divider()
st.caption("🎯 Trading Command Center — Complete trading system at your fingertips")