# app.py
import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import gzip
import json
from io import BytesIO
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="Dashboard Fundos")

# ---------------------------
# Funções utilitárias
# ---------------------------
def limpar_cnpj(cnpj: str) -> str:
    if pd.isna(cnpj):
        return ""
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))
    return cnpj.zfill(14)

def limpar_data_para_api(d: pd.Timestamp) -> str:
    # Recebe pd.Timestamp ou string convertível
    try:
        ts = pd.to_datetime(d)
        return ts.strftime("%Y%m%d")
    except:
        return None

def to_number(x):
    """Converte strings numéricas com formatos BR (ex: '1.234.567,89') para float.
       Se já for numérico, retorna float(x)."""
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.number)):
        return float(x)
    s = str(x).strip()
    # remover caracteres que não sejam dígitos, ponto, vírgula, menos, ou expoente
    # tratar formatos como "1.234.567,89" -> "1234567.89"
    # primeiro, remover espaços
    s = s.replace(" ", "")
    # se houver ambos '.' e ',' assume formato BR
    if s.count(",") == 1 and s.count(".") >= 1:
        # ex: '1.234.567,89' -> remove pontos, troca vírgula por ponto
        s = s.replace(".", "").replace(",", ".")
    else:
        # se só vírgula e nenhuma ponto -> troca vírgula por ponto
        if s.count(",") == 1 and s.count(".") == 0:
            s = s.replace(",", ".")
        else:
            # remove milhares representados por espaços ou pontos
            s = s.replace(",", "")
    try:
        return float(s)
    except:
        return np.nan

def fmt_pct_port(x):
    try:
        return f"{x*100:.2f}%".replace(".", ",")
    except:
        return "-"

def fmt_br_money(v):
    try:
        return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "-"

# ---------------------------
# Sidebar / Inputs
# ---------------------------
st.sidebar.title("Parâmetros")
cnpj_input = st.sidebar.text_input("CNPJ do Fundo", value="10500884000105")
data_inicio = st.sidebar.date_input("Data inicial", value=pd.to_datetime("1900-01-01"))
data_fim = st.sidebar.date_input("Data final", value=pd.to_datetime("2099-01-01"))
botao_buscar = st.sidebar.button("Buscar dados")

# padronizar
cnpj = limpar_cnpj(cnpj_input)
data_ini_api = limpar_data_para_api(data_inicio)
data_fim_api = limpar_data_para_api(data_fim)

# Mostrar URL
url = f"https://www.okanebox.com.br/api/fundoinvestimento/hist/{cnpj}/{data_ini_api}/{data_fim_api}/"
st.sidebar.markdown("**URL usada:**")
st.sidebar.code(url)

# ---------------------------
# Buscar dados da API
# ---------------------------
if not botao_buscar:
    st.info("Preencha os parâmetros no menu lateral e clique em 'Buscar dados'.")
    st.stop()

try:
    req = urllib.request.Request(url)
    req.add_header("Accept-Encoding", "gzip")
    # se a API requer token, usuário pode editar abaixo. Mantive o header do exemplo.
    # req.add_header('Authorization', 'Bearer <seu-token-aqui>')
    response = urllib.request.urlopen(req, timeout=30)

    if response.info().get("Content-Encoding") == "gzip":
        buf = BytesIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        content_json = json.loads(f.read().decode("utf-8"))
    else:
        content_json = json.loads(response.read().decode("utf-8"))

    df = pd.DataFrame(content_json)
except Exception as e:
    st.error(f"Erro ao buscar dados da API: {e}")
    st.stop()

if df.empty:
    st.error("Dados retornados vazios.")
    st.stop()

# ---------------------------
# Tratamento e tipos
# ---------------------------
# Converter datas
if 'DT_COMPTC' in df.columns:
    df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'], dayfirst=True, errors='coerce')
else:
    st.error("Coluna 'DT_COMPTC' não encontrada no retorno da API.")
    st.stop()

# Converter colunas numéricas possíveis
numeric_cols = ['VL_TOTAL', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'CAPTC_DIA', 'RESG_DIA', 'NR_COTST', 'VL_QUOTA_NORM']
for c in numeric_cols:
    if c in df.columns:
        df[c] = df[c].apply(to_number)

# ordenar
df = df.sort_values('DT_COMPTC').reset_index(drop=True)

# criar df_plot (sem NaNs nas colunas essenciais)
df_plot = df.copy()

# ---------------------------
# Função para criar layout padronizado Plotly
# ---------------------------
def configurar_layout(fig, titulo, height=650):
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b>", x=0.5),
        template="plotly_white",
        hoverlabel=dict(bgcolor="white", font_color="black"),
        hovermode="x unified",
        height=height,
        margin=dict(l=80, r=320, t=100, b=220),
        legend=dict(
            title=None,
            orientation="v",
            yanchor="top", y=1,
            xanchor="left", x=1.02,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='lightgray',
            borderwidth=1,
            font=dict(size=12)
        )
    )
    return fig

# ---------------------------
# 1) CAGR ANUAL POR DIA DE APLICAÇÃO
# ---------------------------
st.header("CAGR anualizado (base dias úteis)")

# calcular CAGR anualizado a partir de VL_QUOTA
# n_periods = número de observações com VL_QUOTA não-nulo - 1
vlq = df_plot['VL_QUOTA'].dropna()
if len(vlq) >= 2:
    start = vlq.iloc[0]
    end = vlq.iloc[-1]
    n_days = len(vlq) - 1  # número de períodos
    trading_days = 252
    # CAGR anualizado:
    try:
        cagr_ano = (end / start) ** (trading_days / n_days) - 1
    except Exception:
        cagr_ano = np.nan
else:
    cagr_ano = np.nan

col1, col2 = st.columns([3,1])
with col1:
    fig_cagr = go.Figure()
    fig_cagr.add_trace(go.Scatter(
        x=df_plot['DT_COMPTC'],
        y=(df_plot['VL_QUOTA'] / df_plot['VL_QUOTA'].iloc[0] - 1) * 100,
        mode='lines',
        line=dict(color='royalblue'),
        name='Crescimento acumulado'
    ))
    configurar_layout(fig_cagr, "Crescimento acumulado (base VL_QUOTA)", height=400)
    fig_cagr.update_yaxes(ticksuffix="%", tickformat=".2f")
    st.plotly_chart(fig_cagr, use_container_width=True)

with col2:
    st.metric("CAGR anualizado (a.a.)", fmt_pct_port(cagr_ano) if not pd.isna(cagr_ano) else "N/A")
    st.write("Período:")
    st.write(f"{df_plot['DT_COMPTC'].min().date()} → {df_plot['DT_COMPTC'].max().date()}")
    st.write(f"{len(vlq)} observações")

# ---------------------------
# 2) PATRIMÔNIO E CAPTAÇÃO LÍQUIDA
# ---------------------------
st.header("Patrimônio e Captação Líquida")

# garantir colunas
if 'CAPTC_DIA' in df_plot.columns and 'RESG_DIA' in df_plot.columns and 'VL_PATRIM_LIQ' in df_plot.columns:
    df_plot['Captacao_Liquida'] = df_plot['CAPTC_DIA'].fillna(0) - df_plot['RESG_DIA'].fillna(0)
    df_plot['Soma_Acumulada_Captacao'] = df_plot['Captacao_Liquida'].cumsum()

    fig_pl = go.Figure()
    fig_pl.add_trace(go.Scatter(
        x=df_plot['DT_COMPTC'],
        y=df_plot['Soma_Acumulada_Captacao'],
        mode='lines',
        name='Captação Líquida Acumulada',
        line=dict(color='darkgreen')
    ))
    fig_pl.add_trace(go.Scatter(
        x=df_plot['DT_COMPTC'],
        y=df_plot['VL_PATRIM_LIQ'],
        mode='lines',
        name='Patrimônio Líquido',
        line=dict(color='royalblue')
    ))
    configurar_layout(fig_pl, "Patrimônio e Captação Líquida", height=500)
    # ajustar hovertemplate para mostrar valores (usamos formatação simples)
    fig_pl.update_traces(hovertemplate=None)
    st.plotly_chart(fig_pl, use_container_width=True)
else:
    st.warning("Dados insuficientes para Patrimônio/Captação (colunas CAPTC_DIA, RESG_DIA ou VL_PATRIM_LIQ ausentes).")

# ---------------------------
# 3) CAPTAÇÃO LÍQUIDA MENSAL
# ---------------------------
st.header("Captação Líquida Mensal")

if 'CAPTC_DIA' in df_plot.columns and 'RESG_DIA' in df_plot.columns:
    df_monthly = df_plot.set_index('DT_COMPTC').resample('M')[['CAPTC_DIA', 'RESG_DIA']].sum()
    df_monthly['Captacao_Liquida'] = df_monthly['CAPTC_DIA'] - df_monthly['RESG_DIA']

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_monthly.index,
        y=df_monthly['Captacao_Liquida'],
        name='Captação Líquida Mensal'
    ))
    configurar_layout(fig_bar, "Captação Líquida Mensal", height=450)
    fig_bar.update_yaxes(tickformat=",.2f")
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Dados insuficientes para Captação mensal (colunas CAPTC_DIA/RESG_DIA ausentes).")

# ---------------------------
# 4) PATRIMÔNIO MÉDIO POR COTISTA e Nº COTISTAS
# ---------------------------
st.header("Patrimônio Médio por Cotista e Nº de Cotistas")
if 'VL_PATRIM_LIQ' in df_plot.columns and 'NR_COTST' in df_plot.columns:
    df_plot['Patrimonio_Liq_Medio'] = df_plot['VL_PATRIM_LIQ'] / df_plot['NR_COTST'].replace(0, np.nan)
    fig_pc = go.Figure()
    fig_pc.add_trace(go.Scatter(
        x=df_plot['DT_COMPTC'],
        y=df_plot['Patrimonio_Liq_Medio'],
        mode='lines',
        name='Patrimônio Médio por Cotista',
        line=dict(color='royalblue')
    ))
    fig_pc.add_trace(go.Scatter(
        x=df_plot['DT_COMPTC'],
        y=df_plot['NR_COTST'],
        mode='lines',
        name='Nº de Cotistas',
        yaxis='y2',
        line=dict(color='gray')
    ))
    # layout com eixo secundário
    fig_pc.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=500,
        margin=dict(l=80, r=320, t=100, b=220),
        yaxis=dict(title="Patrimônio Médio (R$)"),
        yaxis2=dict(title="Nº Cotistas", overlaying="y", side="right")
    )
    st.plotly_chart(fig_pc, use_container_width=True)
else:
    st.warning("Dados insuficientes para Patrimônio médio / Nº cotistas (colunas ausentes).")

# ---------------------------
# 5) RENTABILIDADE MÓVEL (1M) + VaR + ES + caixas explicativas
# ---------------------------
st.header("Rentabilidade móvel (21 dias), VaR e Expected Shortfall")

if 'VL_QUOTA' in df_plot.columns:
    # retorno acumulado 21 dias
    df_plot['Retorno_21d'] = df_plot['VL_QUOTA'].pct_change(21)
    df_var = df_plot.dropna(subset=['Retorno_21d']).copy()
    if df_var.empty:
        st.warning("Dados insuficientes para cálculo de Retorno 21d / VaR / ES")
    else:
        # VaR e ES (históricos)
        nivel95 = 0.95
        nivel99 = 0.99
        VaR_95 = -np.percentile(df_var['Retorno_21d'], 100*(1-nivel95))
        VaR_99 = -np.percentile(df_var['Retorno_21d'], 100*(1-nivel99))
        ES_95 = -df_var[df_var['Retorno_21d'] < -VaR_95]['Retorno_21d'].mean()
        ES_99 = -df_var[df_var['Retorno_21d'] < -VaR_99]['Retorno_21d'].mean()

        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(
            x=df_var['DT_COMPTC'],
            y=df_var['Retorno_21d'],
            mode='lines',
            name='Rentabilidade 21d',
            line=dict(color='royalblue'),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Retorno 21d: %{y:.2%}<extra></extra>'
        ))
        # linhas VaR/ES (negativas, plotamos como -VaR? já calculados como positivos)
        fig_v.add_trace(go.Scatter(x=df_var['DT_COMPTC'], y=[-VaR_95]*len(df_var),
                                   mode='lines', name=f'VaR 95% ({fmt_pct_port(VaR_95)})',
                                   line=dict(dash='dash', color='red')))
        fig_v.add_trace(go.Scatter(x=df_var['DT_COMPTC'], y=[-VaR_99]*len(df_var),
                                   mode='lines', name=f'VaR 99% ({fmt_pct_port(VaR_99)})',
                                   line=dict(dash='dot', color='darkred')))
        fig_v.add_trace(go.Scatter(x=df_var['DT_COMPTC'], y=[-ES_95]*len(df_var),
                                   mode='lines', name=f'ES 95% ({fmt_pct_port(ES_95)})',
                                   line=dict(dash='dash', color='orange')))
        fig_v.add_trace(go.Scatter(x=df_var['DT_COMPTC'], y=[-ES_99]*len(df_var),
                                   mode='lines', name=f'ES 99% ({fmt_pct_port(ES_99)})',
                                   line=dict(dash='dot', color='darkorange')))

        configurar_layout(fig_v, "Retorno 21d, VaR e ES", height=550)
        # formatar eixo y em %
        fig_v.update_yaxes(tickformat=".2%")

        # texto explicativo (painel)
        texto_v = (
            f"Este gráfico indica que, em um período de 21 dias:<br>"
            f"• <b>99%</b> de confiança de que o fundo não cairá mais que <b>{fmt_pct_port(VaR_99)}</b>, "
            f"com perda média esperada de <b>{fmt_pct_port(ES_99)}</b> nesses casos.<br>"
            f"• <b>95%</b> de confiança de que a queda não será superior a <b>{fmt_pct_port(VaR_95)}</b>, "
            f"com perda média esperada de <b>{fmt_pct_port(ES_95)}</b> nesses casos."
        )

        fig_v.add_annotation(
            xref="paper", yref="paper", x=0.5, y=-0.28,
            text=texto_v, showarrow=False, align="center", xanchor="center",
            font=dict(size=13), width=1000, bgcolor="rgba(255,255,255,0.95)",
            bordercolor='lightgray', borderwidth=1, borderpad=10
        )

        # caixa com exemplo em R$ (10k)
        invest = 10000
        valor99 = fmt_br_money(VaR_99 * invest)
        valor95 = fmt_br_money(VaR_95 * invest)
        texto_r = (
            f"<b>Ao alocar {fmt_br_money(invest)}</b> no fundo, podemos esperar:<br><br>"
            f"• Uma queda, no pior dos casos (VaR 99%), de <b>{valor99}</b> uma vez a cada <b>8,33 anos (100 meses)</b>.<br>"
            f"• Uma queda, no pior dos casos (VaR 95%), de <b>{valor95}</b> uma vez a cada <b>1,67 anos (20 meses)</b>."
        )
        fig_v.add_annotation(
            xref="paper", yref="paper", x=0.5, y=-0.48,
            text=texto_r, showarrow=False, align="center", xanchor="center",
            font=dict(size=13), width=1000, bgcolor="rgba(255,255,255,0.95)",
            bordercolor='lightgray', borderwidth=1, borderpad=10
        )

        st.plotly_chart(fig_v, use_container_width=True)
else:
    st.warning("Coluna VL_QUOTA ausente; não é possível calcular VaR/ES.")

# ---------------------------
# 6) RETORNO EM JANELA MÓVEL (dropdown 12-60 meses)
# ---------------------------
st.header("Retorno em janela móvel — selecione a janela")

# janelas
janelas = {
    "12 meses (252 dias)": 252,
    "24 meses (504 dias)": 504,
    "36 meses (756 dias)": 756,
    "48 meses (1008 dias)": 1008,
    "60 meses (1260 dias)": 1260
}
# calcular retornos por janela
df_returns = df.copy()
if 'VL_QUOTA' in df_returns.columns:
    for nome, dias in janelas.items():
        df_returns[nome] = df_returns['VL_QUOTA'] / df_returns['VL_QUOTA'].shift(dias) - 1

    # dropdown via selectbox (mais simples no Streamlit)
    janela_selecionada = st.selectbox("Escolha a janela", list(janelas.keys()), index=0)

    dias = janelas[janela_selecionada]
    serie = df_returns[janela_selecionada].dropna()

    if serie.empty:
        st.warning(f"Dados insuficientes para a janela selecionada ({janela_selecionada}).")
    else:
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(
            x=df_returns['DT_COMPTC'],
            y=df_returns[janela_selecionada],
            mode='lines',
            line=dict(color='royalblue'),
            name=f"Retorno {janela_selecionada}"
        ))
        configurar_layout(fig_r, f"Retorno Acumulado — {janela_selecionada}", height=600)
        fig_r.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig_r, use_container_width=True)
else:
    st.warning("VL_QUOTA ausente; não é possível calcular retornos por janela.")

# ---------------------------
# Outros gráficos que já havia (normalizada, drawdown, volatilidade)
# ---------------------------
st.header("Outros indicadores")

cols = st.columns(3)
with cols[0]:
    st.subheader("Rentabilidade Normalizada")
    if 'VL_QUOTA_NORM' in df_plot.columns:
        fig_norm = go.Figure()
        fig_norm.add_trace(go.Scatter(
            x=df_plot['DT_COMPTC'],
            y=df_plot['VL_QUOTA_NORM'],
            mode='lines',
            line=dict(color='royalblue')
        ))
        configurar_layout(fig_norm, "Rentabilidade Normalizada", height=350)
        st.plotly_chart(fig_norm, use_container_width=True)
    else:
        st.write("VL_QUOTA_NORM ausente")

with cols[1]:
    st.subheader("Drawdown")
    if 'VL_QUOTA' in df_plot.columns:
        df_plot['Max_VL_QUOTA'] = df_plot['VL_QUOTA'].cummax()
        df_plot['Drawdown'] = (df_plot['VL_QUOTA'] / df_plot['Max_VL_QUOTA'] - 1) * 100
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(x=df_plot['DT_COMPTC'], y=df_plot['Drawdown'], mode='lines', line=dict(color='firebrick')))
        configurar_layout(fig_dd, "Drawdown", height=350)
        st.plotly_chart(fig_dd, use_container_width=True)
    else:
        st.write("VL_QUOTA ausente")

with cols[2]:
    st.subheader("Volatilidade (21 dias, a.a.)")
    if 'VL_QUOTA' in df_plot.columns:
        vol_window = 21
        df_plot['Volatilidade'] = df_plot['VL_QUOTA'].pct_change().rolling(vol_window).std() * np.sqrt(252) * 100
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=df_plot['DT_COMPTC'], y=df_plot['Volatilidade'], mode='lines', line=dict(color='royalblue')))
        configurar_layout(fig_vol, f"Volatilidade {vol_window} dias", height=350)
        fig_vol.update_yaxes(tickformat=".2f")
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.write("VL_QUOTA ausente")

st.success("Dashboard carregado com sucesso!")
