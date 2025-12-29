import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ===============================
# CONFIGURAÇÃO GERAL
# ===============================
st.set_page_config(
    page_title="AgroMarket Intelligence",
    layout="wide"
)

# ===============================
# HEADER
# ===============================
st.markdown(
    """
    <h1 style="color:#2ecc71;margin-bottom:0">
        AgroMarket Intelligence
    </h1>
    <p style="color:gray;margin-top:5px">
        Monitoramento inteligente de ativos do Agronegócio
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("Configurações")

dias = st.sidebar.slider(
    "Período de análise (dias)",
    min_value=30,
    max_value=365,
    value=180
)

ativos_agro = {
    "JBS (Brasil)": "JBSS3.SA",
    "SLC Agrícola": "SLCE3.SA",
    "Rumo Logística": "RAIL3.SA",
    "Klabin": "KLBN11.SA",
    "BRF": "BRFS3.SA",
    "Deere (BDR)": "DEEC34.SA",
    "Bunge (BDR)": "BUNG34.SA",
    "Mosaic (BDR)": "MOSC34.SA"
}

ativo_selecionado = st.sidebar.selectbox(
    "Selecione um ativo do Agronegócio",
    list(ativos_agro.keys())
)

ticker = ativos_agro[ativo_selecionado]

# ===============================
# DOWNLOAD DOS DADOS
# ===============================
@st.cache_data
def carregar_dados(ticker, dias):
    fim = datetime.today()
    inicio = fim - timedelta(days=dias)
    df = yf.download(ticker, start=inicio, end=fim)
    return df

df = carregar_dados(ticker, dias)

# ===============================
# VALIDAÇÃO
# ===============================
if df.empty:
    st.error("Não foi possível carregar dados para este ativo.")
    st.stop()

# ===============================
# MÉDIAS MÓVEIS
# ===============================
df["MM21"] = df["Close"].rolling(21).mean()
df["MM50"] = df["Close"].rolling(50).mean()

# ===============================
# SINAL SIMPLES
# ===============================
ultimo = df.iloc[-1]

if ultimo["Close"] > ultimo["MM21"] > ultimo["MM50"]:
    sinal = "🟢 Tendência de Alta"
    cor = "#2ecc71"
elif ultimo["Close"] < ultimo["MM21"] < ultimo["MM50"]:
    sinal = "🔴 Tendência de Baixa"
    cor = "#e74c3c"
else:
    sinal = "🟡 Atenção / Lateral"
    cor = "#f1c40f"

# ===============================
# RESUMO
# ===============================
col1, col2, col3 = st.columns(3)

col1.metric(
    "Preço Atual",
    f"R$ {ultimo['Close']:.2f}"
)

col2.metric(
    "Variação do Dia",
    f"{ultimo['Close'] - ultimo['Open']:.2f}"
)

col3.markdown(
    f"""
    <div style="padding:15px;border-radius:8px;background:{cor};color:black;font-weight:bold;text-align:center">
        {sinal}
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
# GRÁFICO
# ===============================
fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Preço"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MM21"],
        line=dict(color="blue", width=1),
        name="MM21"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MM50"],
        line=dict(color="orange", width=1),
        name="MM50"
    )
)

fig.update_layout(
    height=600,
    xaxis_rangeslider_visible=False,
    title=f"Gráfico do ativo: {ativo_selecionado}",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# ===============================
# CTA
# ===============================
st.markdown("---")

st.markdown(
    """
    ### 📲 Quer receber alertas automáticos no WhatsApp?
    Monitoramento diário, sinais objetivos e linguagem simples para o produtor rural.
    
    **Entre em contato:**  
    **(62) 99975-5774**
    """
)

# ===============================
# RODAPÉ
# ===============================
st.markdown(
    """
    <hr>
    <center>
    <small>
    AgroMarket Intelligence • Sistema de monitoramento automatizado para o Agronegócio
    </small>
    </center>
    """,
    unsafe_allow_html=True
)
