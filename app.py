# ============================================================
# AGROMARKET INTELLIGENCE
# Monitoramento Inteligente do Agronegócio
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
from datetime import datetime, timedelta
import json
import time
import plotly.graph_objects as go

# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================

st.set_page_config(
    page_title="AgroMarket Intelligence",
    layout="wide"
)

FINNHUB_API_KEY = "d4uouchr01qnm7pnasq0d4uouchr01qnm7pnasqg"
NEWS_API_KEY = "ec7100fa90ef4e3f9a69a914050dd736"
BRAPI_API_TOKEN = "iExnKM1xcbQcYL3cNPhPQ3"

PROJECT_NAME = "AgroMarket Intelligence"
WHATSAPP = "(62) 99975-5774"

# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
# 🌱 {PROJECT_NAME}
### Monitoramento Inteligente do Agronegócio  
📲 **Contato:** {WHATSAPP}
---
""")

# ============================================================
# CLASSE PRINCIPAL – MOTOR COMPLETO (Claude)
# ============================================================

class AdvancedNewsTracker:

    def __init__(self):
        self.params = {
            'stop_loss': 0.03,
            'take_profit': 0.15,
            'min_score': 20,
            'hold_period': 5,
            'earnings_window': 45,
            'dividend_window': 30,
            'earnings_0_3': 60,
            'earnings_4_7': 55,
            'earnings_8_14': 50,
            'earnings_15_30': 45,
            'earnings_31_45': 35,
            'dividend_0_1': 50,
            'dividend_2_5': 45,
            'dividend_6_10': 40,
            'dividend_11_20': 35,
            'dividend_21_30': 30,
        }

        self.trusted_sources = [
            'reuters','bloomberg','wsj','financial times','cnbc',
            'marketwatch','seeking alpha','benzinga','barrons',
            'yahoo finance','sec','investor relations'
        ]

        self.ticker_map = self.get_bdr_mapping()

    # --------------------------------------------------------
    def get_bdr_mapping(self):
        mapping = {}
        try:
            url = f"https://brapi.dev/api/quote/list?token={BRAPI_API_TOKEN}"
            r = requests.get(url, timeout=20)
            data = r.json().get("stocks", [])
            for s in data:
                if s["stock"].endswith(("34","35")):
                    mapping[s["stock"][:-2]] = s["stock"]
        except:
            pass
        return mapping

    # --------------------------------------------------------
    def get_news(self, ticker):
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
        try:
            r = requests.get(url, timeout=10)
            return r.json() if r.status_code == 200 else []
        except:
            return []

    # --------------------------------------------------------
    def get_yahoo_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            cal = stock.calendar
            return {
                "news": stock.news if hasattr(stock,"news") else [],
                "earnings": cal,
                "ex_div": info.get("exDividendDate"),
                "yield": info.get("dividendYield")
            }
        except:
            return {}

    # --------------------------------------------------------
    def analyze_ticker(self, ticker):
        score = 0
        events = []

        news = self.get_news(ticker)
        yahoo = self.get_yahoo_data(ticker)

        for n in news[:5]:
            title = n.get("headline","").lower()
            if any(x in title for x in ["earnings","results"]):
                score += 30
                events.append("Earnings anunciado")
            if any(x in title for x in ["guidance","outlook"]):
                score += 30
                events.append("Guidance anunciado")
            if any(x in title for x in ["merger","acquisition"]):
                score += 30
                events.append("Fusão/Aquisição")

        if yahoo.get("ex_div"):
            score += 20
            events.append("Dividendo identificado")

        if score >= self.params["min_score"]:
            return {
                "Ticker": ticker,
                "BDR": self.ticker_map.get(ticker,"N/A"),
                "Score": score,
                "Eventos": ", ".join(set(events))
            }

        return None

    # --------------------------------------------------------
    def scan(self, tickers):
        results = []
        for t in tickers:
            res = self.analyze_ticker(t)
            if res:
                results.append(res)
            time.sleep(0.3)
        return pd.DataFrame(results)

# ============================================================
# LISTA DE ATIVOS AGRO
# ============================================================

AGRO_TICKERS = [
    "AAPL","MSFT","DE","MOS","BG","ADM","TSM","NKE",
    "JBS","SLCE3","SUZB3","SMTO3"
]

# ============================================================
# EXECUÇÃO
# ============================================================

st.sidebar.header("⚙️ Parâmetros")
min_score = st.sidebar.slider("Score mínimo", 20, 80, 20)

tracker = AdvancedNewsTracker()

if st.button("🔍 Executar Monitoramento"):
    with st.spinner("Analisando ativos do agronegócio..."):
        df = tracker.scan(AGRO_TICKERS)

    if df.empty:
        st.warning("Nenhuma oportunidade encontrada.")
    else:
        st.success(f"{len(df)} oportunidades identificadas")
        st.dataframe(df.sort_values("Score", ascending=False), use_container_width=True)
