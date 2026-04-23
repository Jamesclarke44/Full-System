"""
Trading Command Center - Full Scanner Restored
All 14 watchlists + Scan ALL option
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import json

st.set_page_config(page_title="Trading System", page_icon="🎯", layout="wide")

# ============================================================================
# SESSION STATE
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
# FULL WATCHLISTS (Same as original Test.py)
# ============================================================================
DEFAULT_WATCHLISTS = {
    "Major ETFs": [
        "SPY", "QQQ", "IWM", "DIA", "TLT", "GLD", "SLV", "USO", "XLF", "XLK",
        "XLV", "XLI", "XLE", "XLP", "XLY", "XLU", "XLB", "XME", "XRT", "XHB",
        "SMH", "SOXX", "IBB", "XBI", "ARKK"
    ],
    "Tech Giants": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX", "ADBE", "CRM",
        "ORCL", "IBM", "CSCO", "INTC", "AMD", "QCOM", "TXN", "AVGO", "MU", "AMAT",
        "LRCX", "KLAC", "SNPS", "CDNS", "ADSK", "NOW", "WDAY", "TEAM", "DDOG", "CRWD"
    ],
    "Semiconductors": [
        "NVDA", "AMD", "INTC", "AVGO", "TXN", "QCOM", "MU", "AMAT", "LRCX", "KLAC",
        "ASML", "TSM", "ADI", "MCHP", "ON", "STM", "NXPI", "MPWR", "MRVL", "SWKS",
        "QRVO", "TER", "ENTG", "ACLS", "FORM", "COHR", "IPGP", "LSCC", "SIMO", "SLAB"
    ],
    "Financials": [
        "JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "SCHW", "AXP", "V",
        "MA", "PYPL", "SQ", "COIN", "BX", "KKR", "APO", "ARES", "CG", "TPG",
        "BEN", "TROW", "STT", "BK", "NTRS", "AMP", "RJF", "SF", "EVR", "LAZ"
    ],
    "Healthcare": [
        "JNJ", "PFE", "MRK", "ABBV", "LLY", "TMO", "DHR", "ABT", "BMY", "AMGN",
        "GILD", "BIIB", "REGN", "VRTX", "MRNA", "ISRG", "EW", "BSX", "SYK", "ZBH",
        "HCA", "UHS", "CI", "UNH", "CVS", "ANTM", "HUM", "CNC", "MOH", "ALGN"
    ],
    "Consumer": [
        "WMT", "AMZN", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "COST", "TJX",
        "ROST", "BURL", "DG", "DLTR", "FIVE", "ULTA", "LULU", "DECK", "CROX", "YETI",
        "PG", "KO", "PEP", "CL", "EL", "CLX", "CHD", "KMB", "HSY", "MDLZ"
    ],
    "Energy": [
        "XOM", "CVX", "COP", "SLB", "EOG", "PXD", "OXY", "MPC", "VLO", "PSX",
        "HAL", "BKR", "FANG", "DVN", "MRO", "APA", "HES", "CTRA", "EQT", "RRC",
        "WMB", "KMI", "OKE", "ENB", "EPD", "ET", "MMP", "PAA", "SUN", "LNG"
    ],
    "High Volume": [
        "AAPL", "TSLA", "NVDA", "AMD", "AMZN", "META", "MSFT", "GOOGL", "NFLX", "PLTR",
        "SOFI", "RIVN", "LCID", "MARA", "RIOT", "COIN", "GME", "AMC", "TQQQ", "SQQQ",
        "SOXL", "SOXS", "SPY", "QQQ", "IWM", "TLT", "HYG", "LQD", "NVDA", "AAPL"
    ],
    "Swing Trading": [
        "AAPL", "MSFT", "NVDA", "TSLA", "META", "AMZN", "GOOGL", "AMD", "NFLX", "CRM",
        "ADBE", "NOW", "SNOW", "DDOG", "CRWD", "ZS", "NET", "MDB", "PLTR", "SOFI",
        "UBER", "LYFT", "ABNB", "SHOP", "SQ", "PYPL", "COIN", "RBLX", "U", "PATH"
    ],
    "Volatile": [
        "TSLA", "NVDA", "AMD", "PLTR", "COIN", "RIVN", "LCID", "MARA", "RIOT", "GME",
        "AMC", "MSTR", "AI", "UPST", "AFRM", "HOOD", "W", "CHWY", "CVNA", "WOLF",
        "ENPH", "SEDG", "FSLR", "SPWR", "RUN", "NOVA", "MAXN", "ARRY", "SHLS", "STEM"
    ],
    "AI & Software": [
        "MSFT", "GOOGL", "META", "NVDA", "ADBE", "CRM", "NOW", "SNOW", "PLTR", "AI",
        "PATH", "U", "TEAM", "WDAY", "ZM", "DOCU", "CRWD", "ZS", "NET", "DDOG",
        "MDB", "ESTC", "SPLK", "DT", "FROG", "GTLB", "CFLT", "BRZE", "PD", "ASAN"
    ],
    "Crypto-Related": [
        "COIN", "MARA", "RIOT", "MSTR", "SQ", "PYPL", "HOOD", "CLSK", "HUT", "BITF",
        "BTBT", "WULF", "IREN", "CIFR", "SDIG", "ARBK", "CORZ", "DGHI", "BTCM", "MIGI"
    ],
    "Dividend Aristocrats": [
        "JNJ", "PG", "KO", "PEP", "WMT", "MCD", "MMM", "CAT", "DE", "LOW",
        "HD", "TGT", "CL", "CLX", "KMB", "BEN", "TROW", "ABBV", "ABT", "CVX",
        "XOM", "O", "SPG", "PLD", "AVB", "EQR", "ESS", "MAA", "UDR", "CPT"
    ],
    "Small Cap Growth": [
        "SMCI", "CELH", "ELF", "WING", "TXG", "PGNY", "FND", "W", "CHWY", "CVNA",
        "UPST", "AFRM", "SOFI", "HOOD", "RKLB", "ASTS", "IONQ", "QBTS", "RGTI", "QUBT",
        "ACHR", "JOBY", "EVTL", "BLDE", "LILM", "EH", "PL", "MVST", "SLDP", "QS"
    ]
}

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
# TAB 1: SCANNER (FULL VERSION)
# ----------------------------------------------------------------------------
with tab1:
    st.header("🔍 Trading Scanner")
    
    watchlist_option = st.selectbox("Select Watchlist", list(DEFAULT_WATCHLISTS.keys()) + ["Custom"])
    
    scan_all = st.checkbox("🔍 Scan ALL Watchlists Combined (400+ tickers)", value=False)
    
    if scan_all:
        all_tickers = set()
        for name, tlist in DEFAULT_WATCHLISTS.items():
            all_tickers.update(tlist)
        tickers = list(all_tickers)
        st.success(f"🎯 Scanning ALL {len(tickers)} tickers across all watchlists!")
    elif watchlist_option == "Custom":
        custom_tickers = st.text_area("Enter tickers (comma separated)", value="AAPL, MSFT, NVDA, TSLA", height=80)
        tickers = [t.strip().upper() for t in custom_tickers.replace(',', ' ').split() if t.strip()]
    else:
        tickers = DEFAULT_WATCHLISTS[watchlist_option]
        st.info(f"📋 {len(tickers)} tickers in {watchlist_option}")
    
    scan_clicked = st.button("🔍 Run Scanner", key="scan_btn", use_container_width=True)
    
    if scan_clicked:
        results = []
        progress = st.progress(0, text="Starting scan...")
        
        for i, t in enumerate(tickers):
            progress.progress((i+1)/len(tickers), text=f"Scanning {t}... ({i+1}/{len(tickers)})")
            
            try:
                df = yf.download(t, period="1mo", progress=False)
                if not df.empty and len(df) > 20:
                    if isinstance(df.columns, pd.MultiIndex):
                        close = df['Close'].iloc[:, 0] if df['Close'].ndim > 1 else df['Close']
                        volume = df['Volume'].iloc[:, 0] if df['Volume'].ndim > 1 else df['Volume']
                    else:
                        close = df['Close']
                        volume = df['Volume']
                    
                    price = float(close.iloc[-1])
                    prev = float(close.iloc[-2]) if len(close) > 1 else price
                    change = (price - prev) / prev * 100 if prev > 0 else 0
                    
                    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else price
                    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else price
                    
                    avg_volume = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else 0
                    current_volume = float(volume.iloc[-1])
                    vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                    
                    # RSI
                    delta = close.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    rsi_val = float(rsi.iloc[-1]) if len(rsi) > 0 else 50
                    
                    # ATR %
                    high = df['High'].iloc[:, 0] if isinstance(df['High'], pd.DataFrame) else df['High']
                    low = df['Low'].iloc[:, 0] if isinstance(df['Low'], pd.DataFrame) else df['Low']
                    atr_val = float((high - low).tail(14).mean()) if len(df) >= 14 else price * 0.02
                    atr_pct = (atr_val / price) * 100
                    
                    # Trend
                    if price > sma20 > sma50:
                        trend = "Strong Up"
                    elif price > sma20:
                        trend = "Up"
                    elif price < sma20 < sma50:
                        trend = "Strong Down"
                    elif price < sma20:
                        trend = "Down"
                    else:
                        trend = "Neutral"
                    
                    # Score
                    score = 5
                    if price > sma20: score += 1
                    if price > sma50: score += 1
                    if change > 0: score += 1
                    if vol_ratio > 1.2: score += 1
                    if 30 < rsi_val < 70: score += 1
                    
                    results.append({
                        "Ticker": t, 
                        "Price": round(price, 2), 
                        "Change": round(change, 2),
                        "Vol Ratio": round(vol_ratio, 2),
                        "ATR %": round(atr_pct, 2),
                        "RSI": round(rsi_val, 1),
                        "Trend": trend,
                        "Score": score
                    })
            except Exception as e:
                pass
        
        progress.empty()
        
        if results:
            st.session_state.scan_results = results
            st.success(f"✅ Found {len(results)} setups out of {len(tickers)} tickers")
            
            df_results = pd.DataFrame(results).sort_values("Score", ascending=False)
            
            st.dataframe(
                df_results.style.format({
                    'Price': '${:.2f}',
                    'Change': '{:+.2f}%',
                    'Vol Ratio': '{:.2f}x',
                    'ATR %': '{:.2f}%',
                    'RSI': '{:.1f}'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            st.divider()
            st.subheader("📤 Quick Load")
            
            # Quick load buttons in columns
            cols = st.columns(5)
            for i, (_, row) in enumerate(df_results.head(10).iterrows()):
                with cols[i % 5]:
                    if st.button(f"📤 {row['Ticker']}", key=f"quick_{row['Ticker']}_{i}", use_container_width=True):
                        st.session_state.ticker = row['Ticker']
                        st.session_state.entry = row['Price']
                        st.success(f"Loaded {row['Ticker']}!")
                        st.rerun()
        else:
            st.warning("No setups found. Try relaxing filters or a different watchlist.")

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
                    st.error("No data found")
                else:
                    if isinstance(df.columns, pd.MultiIndex):
                        close = df['Close'].iloc[:, 0] if df['Close'].ndim > 1 else df['Close']
                        high = df['High'].iloc[:, 0] if df['High'].ndim > 1 else df['High']
                        low = df['Low'].iloc[:, 0] if df['Low'].ndim > 1 else df['Low']
                        volume = df['Volume'].iloc[:, 0] if df['Volume'].ndim > 1 else df['Volume']
                    else:
                        close = df['Close']
                        high = df['High']
                        low = df['Low']
                        volume = df['Volume']
                    
                    price = float(close.iloc[-1])
                    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else price
                    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else price
                    ema9 = float(close.ewm(span=9, adjust=False).mean().iloc[-1])
                    ema21 = float(close.ewm(span=21, adjust=False).mean().iloc[-1])
                    
                    # RSI
                    delta = close.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain / loss
                    rsi_val = float((100 - (100 / (1 + rs))).iloc[-1]) if len(delta) >= 14 else 50
                    
                    # MACD
                    ema12 = close.ewm(span=12, adjust=False).mean()
                    ema26 = close.ewm(span=26, adjust=False).mean()
                    macd = ema12 - ema26
                    signal = macd.ewm(span=9, adjust=False).mean()
                    hist = macd - signal
                    hist_val = float(hist.iloc[-1])
                    hist_prev = float(hist.iloc[-2]) if len(hist) > 1 else 0
                    
                    # ATR
                    high_low = high - low
                    high_close = abs(high - close.shift())
                    low_close = abs(low - close.shift())
                    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                    atr = float(tr.rolling(14).mean().iloc[-1]) if len(tr) >= 14 else price * 0.02
                    atr_pct = (atr / price) * 100
                    
                    # Volume
                    avg_volume = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else 0
                    current_volume = float(volume.iloc[-1])
                    vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                    
                    # Support/Resistance
                    support = float(low.tail(50).min()) if len(low) >= 50 else price * 0.95
                    resistance = float(high.tail(50).max()) if len(high) >= 50 else price * 1.05
                    dist_support = (price - support) / price * 100
                    dist_resistance = (resistance - price) / price * 100
                    
                    # Market Regime (ADX)
                    plus_dm = high.diff()
                    minus_dm = low.diff().abs() * -1
                    plus_dm[plus_dm < 0] = 0
                    minus_dm[minus_dm > 0] = 0
                    minus_dm = minus_dm.abs()
                    atr_14 = tr.rolling(14).mean()
                    plus_di = 100 * (plus_dm.rolling(14).mean() / atr_14)
                    minus_di = 100 * (minus_dm.rolling(14).mean() / atr_14)
                    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
                    adx = float(dx.rolling(14).mean().iloc[-1]) if len(dx) >= 28 else 20
                    
                    if adx > 25:
                        regime = "Strong Trending"
                    elif adx > 20:
                        regime = "Trending"
                    else:
                        regime = "Choppy/Ranging"
                    
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
                        
                        if ema9 > ema21:
                            score += 10
                            reasons.append("✅ 9 EMA above 21 EMA")
                        
                        if hist_val > 0 and hist_val > hist_prev:
                            score += 15
                            reasons.append("✅ MACD histogram positive and increasing")
                        elif hist_val > 0:
                            score += 8
                            reasons.append("✅ MACD histogram positive")
                        
                        if 30 <= rsi_val <= 70:
                            score += 10
                            reasons.append(f"✅ RSI {rsi_val:.1f} (neutral)")
                        elif 30 <= rsi_val < 40:
                            score += 15
                            reasons.append(f"✅ RSI {rsi_val:.1f} (oversold)")
                        elif rsi_val > 70:
                            score -= 10
                            warnings.append(f"⚠️ RSI overbought ({rsi_val:.1f})")
                        
                        if dist_support < 3:
                            score += 15
                            reasons.append(f"✅ Near support ({dist_support:.1f}% away)")
                        elif dist_support < 5:
                            score += 10
                            reasons.append(f"✅ Close to support ({dist_support:.1f}% away)")
                        
                        suggested_stop = min(support * 0.99, price - atr * 1.5)
                    else:
                        if price < sma20 < sma50:
                            score += 15
                            reasons.append("✅ Price below 20 & 50 SMA")
                        elif price < sma20:
                            score += 8
                            reasons.append("✅ Price below 20 SMA")
                        
                        if ema9 < ema21:
                            score += 10
                            reasons.append("✅ 9 EMA below 21 EMA")
                        
                        if rsi_val > 60:
                            score += 15
                            reasons.append(f"✅ RSI {rsi_val:.1f} (overbought)")
                        
                        if dist_resistance < 3:
                            score += 15
                            reasons.append(f"✅ Near resistance ({dist_resistance:.1f}% away)")
                        
                        suggested_stop = max(resistance * 1.01, price + atr * 1.5)
                    
                    if vol_ratio > 1.5:
                        score += 10
                        reasons.append(f"✅ High volume ({vol_ratio:.1f}x)")
                    elif vol_ratio > 1.2:
                        score += 5
                        reasons.append(f"✅ Above avg volume ({vol_ratio:.1f}x)")
                    
                    if regime == "Strong Trending":
                        score += 15
                        reasons.append("✅ Strong trending market")
                    elif regime == "Trending":
                        score += 8
                        reasons.append("✅ Trending market")
                    elif regime == "Choppy/Ranging":
                        score -= 10
                        warnings.append("⚠️ Choppy market - reduce expectations")
                    
                    score = max(0, min(100, score))
                    
                    st.session_state.analysis_done = True
                    st.session_state.analysis_result = {
                        "price": price, "score": score, "rsi": rsi_val, "atr": atr,
                        "atr_pct": atr_pct, "sma20": sma20, "sma50": sma50,
                        "support": support, "resistance": resistance,
                        "dist_support": dist_support, "dist_resistance": dist_resistance,
                        "reasons": reasons, "warnings": warnings,
                        "suggested_stop": suggested_stop, "regime": regime,
                        "vol_ratio": vol_ratio, "macd_hist": hist_val
                    }
                    st.session_state.entry = price
                    st.session_state.stop = suggested_stop
                    
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.session_state.analysis_done and st.session_state.analysis_result:
        r = st.session_state.analysis_result
        
        if r['score'] >= 75:
            st.success(f"### ✅ STRONG {st.session_state.direction} — Score: {r['score']}/100")
        elif r['score'] >= 60:
            st.info(f"### 📈 {st.session_state.direction} — Score: {r['score']}/100")
        elif r['score'] >= 40:
            st.warning(f"### ⚠️ NEUTRAL — Score: {r['score']}/100")
        else:
            st.error(f"### ❌ AVOID — Score: {r['score']}/100")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Price", f"${r['price']:.2f}")
        col2.metric("RSI", f"{r['rsi']:.1f}")
        col3.metric("ATR", f"${r['atr']:.2f} ({r['atr_pct']:.2f}%)")
        col4.metric("Volume", f"{r['vol_ratio']:.2f}x")
        col5.metric("Regime", r['regime'])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Support", f"${r['support']:.2f}")
        col2.metric("Resistance", f"${r['resistance']:.2f}")
        col3.metric("20 SMA", f"${r['sma20']:.2f}")
        col4.metric("50 SMA", f"${r['sma50']:.2f}")
        
        if r['reasons']:
            st.markdown("**✅ Confirming Factors:**")
            for reason in r['reasons']:
                st.markdown(f"- {reason}")
        
        if r['warnings']:
            st.markdown("**⚠️ Warning Signs:**")
            for warning in r['warnings']:
                st.markdown(f"- {warning}")
        
        st.success(f"🎯 Suggested Stop Loss: **${r['suggested_stop']:.2f}**")

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

st.divider()
st.caption("🎯 Trading Command Center — Full Scanner Restored!")