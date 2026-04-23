"""
Trading Command Center - Working Version
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import json

# Must be first Streamlit command
st.set_page_config(page_title="Trading System", page_icon="🎯", layout="wide")

# ============================================================================
# SESSION STATE - Initialize everything first
# ============================================================================
if 'ticker' not in st.session_state:
    st.session_state.ticker = "AAPL"
if 'entry' not in st.session_state:
    st.session_state.entry = 180.00
if 'stop' not in st.session_state:
    st.session_state.stop = 175.00
if 'direction' not in st.session_state:
    st.session_state.direction = "LONG"
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = []
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# ============================================================================
# STYLING
# ============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 800;
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        height: 50px;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #f59e0b 100%);
    }
    .data-bar {
        background: #1e2a3a;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🎯 Trading Command Center</h1>', unsafe_allow_html=True)

# ============================================================================
# SHARED DATA BAR
# ============================================================================
st.markdown('<div class="data-bar">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.session_state.ticker = st.text_input("📈 Ticker", value=st.session_state.ticker).upper()
with col2:
    st.session_state.entry = st.number_input("💰 Entry", value=float(st.session_state.entry), step=0.01, format="%.2f")
with col3:
    st.session_state.stop = st.number_input("🛑 Stop", value=float(st.session_state.stop), step=0.01, format="%.2f")
with col4:
    st.session_state.direction = st.radio("📊 Dir", ["LONG", "SHORT"], horizontal=True, index=0 if st.session_state.direction=="LONG" else 1)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TABS
# ============================================================================
tab1, tab2, tab3 = st.tabs(["🔍 Scanner", "📈 Analyzer", "🎯 Exit Planner"])

# ----------------------------------------------------------------------------
# TAB 1: SCANNER
# ----------------------------------------------------------------------------
with tab1:
    st.header("🔍 Trading Scanner")
    
    watchlist = st.selectbox("Select Watchlist", ["Tech Giants", "Major ETFs", "Volatile Stocks"])
    
    watchlists = {
        "Tech Giants": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX", "ADBE", "CRM"],
        "Major ETFs": ["SPY", "QQQ", "IWM", "DIA", "TLT", "GLD", "SLV", "XLF", "XLK"],
        "Volatile Stocks": ["TSLA", "NVDA", "AMD", "PLTR", "COIN", "MARA", "RIOT", "GME", "AMC"]
    }
    
    tickers = watchlists[watchlist]
    st.info(f"📋 {len(tickers)} tickers ready to scan")
    
    scan_clicked = st.button("🔍 Run Scanner", key="scan_btn", use_container_width=True)
    
    if scan_clicked:
        results = []
        progress = st.progress(0, text="Starting scan...")
        
        for i, t in enumerate(tickers):
            progress.progress((i+1)/len(tickers), text=f"Scanning {t}... ({i+1}/{len(tickers)})")
            
            try:
                df = yf.download(t, period="1mo", progress=False)
                if not df.empty and len(df) > 20:
                    # Handle MultiIndex
                    if isinstance(df.columns, pd.MultiIndex):
                        close = df['Close'].iloc[:, 0] if df['Close'].ndim > 1 else df['Close']
                    else:
                        close = df['Close']
                    
                    price = float(close.iloc[-1])
                    prev = float(close.iloc[-2]) if len(close) > 1 else price
                    change = (price - prev) / prev * 100 if prev > 0 else 0
                    
                    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else price
                    
                    score = 5
                    if price > sma20: score += 2
                    if change > 0: score += 2
                    
                    results.append({
                        "Ticker": t, 
                        "Price": round(price, 2), 
                        "Change": round(change, 2), 
                        "Score": score
                    })
            except Exception as e:
                st.warning(f"{t}: {str(e)[:50]}")
        
        progress.empty()
        
        if results:
            st.session_state.scan_results = results
            st.success(f"✅ Found {len(results)} setups")
            
            df_results = pd.DataFrame(results).sort_values("Score", ascending=False)
            
            for _, row in df_results.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])
                with c1:
                    st.write(f"**{row['Ticker']}**")
                with c2:
                    st.write(f"${row['Price']:.2f}")
                with c3:
                    color = "#22c55e" if row['Change'] >= 0 else "#ef4444"
                    st.markdown(f"<span style='color:{color}'>{row['Change']:+.2f}%</span>", unsafe_allow_html=True)
                with c4:
                    score_color = "#22c55e" if row['Score'] >= 8 else ("#f59e0b" if row['Score'] >= 6 else "#ef4444")
                    st.markdown(f"<span style='color:{score_color}; font-weight:700;'>{row['Score']}/10</span>", unsafe_allow_html=True)
                with c5:
                    if st.button("📤", key=f"use_{row['Ticker']}_{_}"):
                        st.session_state.ticker = row['Ticker']
                        st.session_state.entry = row['Price']
                        st.rerun()
        else:
            st.warning("No setups found. Try a different watchlist.")
    else:
        if st.session_state.scan_results:
            st.info(f"Previous scan: {len(st.session_state.scan_results)} results. Click 'Run Scanner' to refresh.")
        else:
            st.info("👆 Click 'Run Scanner' to find trade setups")

# ----------------------------------------------------------------------------
# TAB 2: ENTRY ANALYZER
# ----------------------------------------------------------------------------
with tab2:
    st.header("📈 Entry Analyzer")
    st.markdown(f"**Current:** {st.session_state.ticker} @ ${st.session_state.entry:.2f}")
    
    analyze_clicked = st.button("🔍 Analyze Entry", key="analyze_btn", type="primary", use_container_width=True)
    
    if analyze_clicked:
        with st.spinner(f"Analyzing {st.session_state.ticker}..."):
            try:
                df = yf.download(st.session_state.ticker, period="3mo", progress=False)
                
                if df.empty:
                    st.error("No data found for this ticker")
                else:
                    # Handle MultiIndex
                    if isinstance(df.columns, pd.MultiIndex):
                        close = df['Close'].iloc[:, 0] if df['Close'].ndim > 1 else df['Close']
                        high = df['High'].iloc[:, 0] if df['High'].ndim > 1 else df['High']
                        low = df['Low'].iloc[:, 0] if df['Low'].ndim > 1 else df['Low']
                    else:
                        close = df['Close']
                        high = df['High']
                        low = df['Low']
                    
                    price = float(close.iloc[-1])
                    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else price
                    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else price
                    
                    # RSI
                    delta = close.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    rsi_val = float(rsi.iloc[-1]) if len(rsi) > 0 else 50
                    
                    # ATR
                    high_low = high - low
                    high_close = abs(high - close.shift())
                    low_close = abs(low - close.shift())
                    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                    atr = float(tr.rolling(14).mean().iloc[-1]) if len(tr) >= 14 else price * 0.02
                    
                    # Support/Resistance
                    support = float(low.tail(50).min()) if len(low) >= 50 else price * 0.95
                    resistance = float(high.tail(50).max()) if len(high) >= 50 else price * 1.05
                    
                    # Score
                    score = 50
                    reasons = []
                    warnings = []
                    
                    if st.session_state.direction == "LONG":
                        if price > sma20 > sma50:
                            score += 15
                            reasons.append("✅ Price above 20 & 50 SMA")
                        elif price > sma20:
                            score += 8
                            reasons.append("✅ Price above 20 SMA")
                        
                        if 30 < rsi_val < 70:
                            score += 10
                            reasons.append(f"✅ RSI {rsi_val:.1f} (neutral)")
                        elif 30 <= rsi_val <= 40:
                            score += 15
                            reasons.append(f"✅ RSI {rsi_val:.1f} (oversold - bounce potential)")
                        elif rsi_val > 70:
                            score -= 10
                            warnings.append(f"⚠️ RSI overbought ({rsi_val:.1f})")
                        
                        if price < support * 1.03:
                            score += 10
                            reasons.append(f"✅ Near support (${support:.2f})")
                        
                        suggested_stop = min(support * 0.99, price - atr * 1.5)
                    else:
                        if price < sma20 < sma50:
                            score += 15
                            reasons.append("✅ Price below 20 & 50 SMA")
                        elif price < sma20:
                            score += 8
                            reasons.append("✅ Price below 20 SMA")
                        
                        if rsi_val > 60:
                            score += 10
                            reasons.append(f"✅ RSI {rsi_val:.1f} (overbought)")
                        elif rsi_val > 70:
                            score += 15
                            reasons.append(f"✅ RSI {rsi_val:.1f} (extremely overbought)")
                        
                        if price > resistance * 0.97:
                            score += 10
                            reasons.append(f"✅ Near resistance (${resistance:.2f})")
                        
                        suggested_stop = max(resistance * 1.01, price + atr * 1.5)
                    
                    score = max(0, min(100, score))
                    
                    # Store results
                    st.session_state.analysis_done = True
                    st.session_state.analysis_result = {
                        "price": price,
                        "score": score,
                        "rsi": rsi_val,
                        "atr": atr,
                        "sma20": sma20,
                        "sma50": sma50,
                        "support": support,
                        "resistance": resistance,
                        "reasons": reasons,
                        "warnings": warnings,
                        "suggested_stop": suggested_stop
                    }
                    st.session_state.entry = price
                    st.session_state.stop = suggested_stop
                    
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display results if analysis was done
    if st.session_state.analysis_done and st.session_state.analysis_result:
        r = st.session_state.analysis_result
        
        if r['score'] >= 70:
            st.success(f"### ✅ STRONG {st.session_state.direction} — Score: {r['score']}/100")
        elif r['score'] >= 60:
            st.info(f"### 📈 {st.session_state.direction} — Score: {r['score']}/100")
        elif r['score'] >= 50:
            st.warning(f"### ⚠️ NEUTRAL — Score: {r['score']}/100")
        else:
            st.error(f"### ❌ AVOID — Score: {r['score']}/100")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Price", f"${r['price']:.2f}")
        col2.metric("RSI", f"{r['rsi']:.1f}")
        col3.metric("ATR", f"${r['atr']:.2f}")
        col4.metric("Stop", f"${r['suggested_stop']:.2f}")
        
        if r['reasons']:
            st.markdown("**✅ Confirming:**")
            for reason in r['reasons']:
                st.markdown(f"- {reason}")
        
        if r['warnings']:
            st.markdown("**⚠️ Warnings:**")
            for warning in r['warnings']:
                st.markdown(f"- {warning}")

# ----------------------------------------------------------------------------
# TAB 3: EXIT PLANNER
# ----------------------------------------------------------------------------
with tab3:
    st.header("🎯 Exit Planner")
    st.markdown(f"**Planning:** {st.session_state.ticker} {st.session_state.direction}")
    
    col1, col2 = st.columns(2)
    with col1:
        account = st.number_input("Account Size ($)", value=25000.0, step=1000.0, format="%.2f")
        risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    with col2:
        reward_ratio = st.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0, 0.5)
    
    entry = st.session_state.entry
    stop = st.session_state.stop
    
    risk_per_share = abs(entry - stop)
    reward_per_share = risk_per_share * reward_ratio
    
    if st.session_state.direction == "LONG":
        target = entry + reward_per_share
    else:
        target = entry - reward_per_share
    
    risk_amount = account * (risk_pct / 100)
    position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
    
    st.divider()
    st.markdown("### 📊 Position Plan")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Entry", f"${entry:.2f}")
        st.metric("Stop Loss", f"${stop:.2f}")
    with col2:
        st.metric("Target", f"${target:.2f}")
        st.metric("Risk/Share", f"${risk_per_share:.2f}")
    with col3:
        st.metric("Position Size", f"{position_size} shares")
        st.metric("Max Risk", f"${risk_amount:.2f}")
    
    rr_actual = reward_per_share / risk_per_share if risk_per_share > 0 else 0
    st.markdown(f"**Risk/Reward:** 1:{rr_actual:.2f}")
    
    if rr_actual >= 2:
        st.success("✅ Excellent R/R ratio")
    elif rr_actual >= 1.5:
        st.info("📈 Good R/R ratio")
    else:
        st.warning("⚠️ R/R ratio below 1.5")

# Footer
st.divider()
st.caption("🎯 Trading Command Center — Click the buttons to scan, analyze, and plan!")