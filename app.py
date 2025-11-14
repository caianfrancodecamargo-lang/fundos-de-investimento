import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import gzip
import json
from io import BytesIO
import plotly.graph_objects as go

# -----------------------------------------------------------
# 🔧 FUNÇÕES AUXILIARES
# -----------------------------------------------------------

def limpar_cnpj(cnpj):
    """Remove . / - e garante 14 dígitos."""
    cnpj = ''.join(filter(str.isdigit, cnpj))
    return cnpj.zfill(14)

def limpar_data(data):
    """Converte YYYY-MM-DD para formato YYYYMMDD."""
    try:
        return pd.to_datetime(data).strftime("%Y%m%d")
    except:
        return None

def format_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# -----------------------------------------------------------
# 🎛️ INTERFACE STREAMLIT
# -----------------------------------------------------------

st.title("📊 Dashboard de Fundos de Investimento – Caian Franco")

st.markdown("### Informe os parâmetros para buscar os dados:")

cnpj_input = st.text_input("CNPJ do Fundo:", "10500884000105")
data_ini_input = st.date_input("Data inicial:", value=pd.to_datetime("1900-01-01"))
data_fim_input = st.date_input("Data final:", value=pd.to_datetime("2099-01-01"))

cnpj = limpar_cnpj(cnpj_input)
data_ini = limpar_data(data_ini_input)
data_fim = limpar_data(data_fim_input)

if not cnpj or not data_ini or not data_fim:
    st.error("Erro no formato de CNPJ ou datas.")
    st.stop()

url = f"https://www.okanebox.com.br/api/fundoinvestimento/hist/{cnpj}/{data_ini}/{data_fim}/"

st.write("🔗 **URL usada na consulta:**")
st.code(url)

# -----------------------------------------------------------
# 📥 BUSCAR OS DADOS
# -----------------------------------------------------------

try:
    req = urllib.request.Request(url)
    req.add_header("Accept-Encoding", "gzip")
    req.add_header('Authorization', 'Bearer caianfrancodecamargo@gmail.com')

    response = urllib.request.urlopen(req)

    if response.info().get("Content-Encoding") == "gzip":
        buf = BytesIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        content_json = json.loads(f.read().decode("utf-8"))
    else:
        content_json = json.loads(response.read().decode("utf-8"))

    df = pd.DataFrame(content_json)

except Exception as e:
    st.error(f"Erro ao acessar os dados da API: {e}")
    st.stop()

# -----------------------------------------------------------
# 🧹 TRATAMENTO DOS DADOS
# -----------------------------------------------------------

df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'])

# -----------------------------------------------------------
# 📈 GRÁFICO — RENTABILIDADE NORMALIZADA
# -----------------------------------------------------------

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['DT_COMPTC'],
    y=df['VL_QUOTA_NORM'],
    mode='lines',
    line=dict(color='royalblue', width=2),
    hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
))

fig.update_layout(
    title="<b>Rentabilidade Histórica Normalizada</b>",
    title_x=0.5,
    xaxis_title="Data",
    yaxis_title="Rentabilidade (%)",
    template="plotly_white",
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------
# 📉 GRÁFICO — DRAWDOWN
# -----------------------------------------------------------

df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100

fig_dd = go.Figure()
fig_dd.add_trace(go.Scatter(
    x=df['DT_COMPTC'],
    y=df['Drawdown'],
    mode='lines',
    line=dict(color='firebrick'),
))

fig_dd.update_layout(
    title="<b>Drawdown Histórico</b>",
    title_x=0.5,
    xaxis_title="Data",
    yaxis_title="Drawdown (%)",
    template="plotly_white",
    height=450
)

st.plotly_chart(fig_dd, use_container_width=True)

# -----------------------------------------------------------
# 📊 VOLATILIDADE
# -----------------------------------------------------------

vol_window = 21
trading_days = 252

df['Volatilidade'] = df['VL_QUOTA'].pct_change().rolling(vol_window).std() * np.sqrt(trading_days) * 100

fig_vol = go.Figure()
fig_vol.add_trace(go.Scatter(
    x=df['DT_COMPTC'],
    y=df['Volatilidade'],
    mode='lines',
    line=dict(color='royalblue'),
))

fig_vol.update_layout(
    title=f"<b>Volatilidade Móvel ({vol_window} dias)</b>",
    title_x=0.5,
    xaxis_title="Data",
    yaxis_title="Volatilidade (% a.a.)",
    template="plotly_white",
    height=450
)

st.plotly_chart(fig_vol, use_container_width=True)

# -----------------------------------------------------------
# ✔️ FINALIZAÇÃO
# -----------------------------------------------------------

st.success("Dashboard carregado com sucesso!")
