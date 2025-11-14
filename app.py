# -*- coding: utf-8 -*-
import streamlit as st
import urllib.request
import gzip
import json
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
import numpy as np
import re
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Fundos de Investimentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado inspirado no estilo Copaiba Invest
st.markdown("""
<style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Variáveis de cor inspiradas no Copaiba */
    :root {
        --primary-color: #1a5f4f;
        --secondary-color: #2d8a6e;
        --accent-color: #3ab795;
        --dark-bg: #0a1f1a;
        --light-bg: #f8faf9;
        --text-dark: #1a1a1a;
        --text-light: #666666;
    }

    /* Estilo geral */
    .stApp {
        background-color: var(--light-bg);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--dark-bg) 100%);
        padding: 2rem 1rem;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Headers na sidebar */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
        font-weight: 600;
    }

    /* Inputs na sidebar - FONTE PRETA */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stDateInput input {
        background-color: white !important;
        color: #000000 !important;
        border: 2px solid var(--accent-color) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        font-weight: 500 !important;
    }

    /* Placeholder dos inputs */
    [data-testid="stSidebar"] input::placeholder {
        color: #666666 !important;
        opacity: 0.7 !important;
    }

    /* Labels dos inputs */
    [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }

    /* Botão principal */
    .stButton button {
        background: linear-gradient(135deg, var(--secondary-color) 0%, var(--accent-color) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(58, 183, 149, 0.3) !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(58, 183, 149, 0.4) !important;
    }

    /* Título principal */
    h1 {
        color: var(--primary-color) !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }

    /* Subtítulos */
    h2, h3 {
        color: var(--primary-color) !important;
        font-weight: 600 !important;
    }

    /* Cards de métricas */
    [data-testid="stMetricValue"] {
        color: var(--primary-color) !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-light) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        color: var(--text-dark);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border: 2px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-color: var(--primary-color) !important;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 8px !important;
        border-left: 4px solid var(--accent-color) !important;
    }

    /* Divisores */
    hr {
        border-color: var(--accent-color) !important;
        opacity: 0.3 !important;
    }

    /* Gráficos */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Success/Error messages */
    .stSuccess {
        background-color: rgba(58, 183, 149, 0.1) !important;
        color: var(--secondary-color) !important;
        border-left: 4px solid var(--accent-color) !important;
    }

    .stError {
        background-color: rgba(220, 53, 69, 0.1) !important;
        border-left: 4px solid #dc3545 !important;
    }

    /* Footer */
    footer {
        color: var(--text-light) !important;
        font-size: 0.85rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Função para limpar CNPJ (remove tudo que não é número)
def limpar_cnpj(cnpj):
    return re.sub(r'\D', '', cnpj)

# Função para converter data brasileira (DD/MM/AAAA) para formato API (YYYYMMDD)
def converter_data_brasileira(data_str):
    """
    Converte data do formato DD/MM/AAAA para YYYYMMDD
    """
    if not data_str:
        return None

    try:
        # Remove espaços e caracteres extras
        data_limpa = data_str.strip()

        # Tenta interpretar como DD/MM/AAAA
        dt = datetime.strptime(data_limpa, '%d/%m/%Y')
        return dt.strftime('%Y%m%d')
    except:
        try:
            # Tenta sem as barras
            data_limpa = re.sub(r'\D', '', data_str)
            if len(data_limpa) == 8:
                dt = datetime.strptime(data_limpa, '%d%m%Y')
                return dt.strftime('%Y%m%d')
        except:
            return None

    return None

# Sidebar com inputs do usuário
st.sidebar.header("⚙️ Configurações")
st.sidebar.markdown("---")

# Input de CNPJ (sem valor padrão)
cnpj_input = st.sidebar.text_input(
    "CNPJ do Fundo",
    value="",
    placeholder="Ex: 10.500.884/0001-05 o CNPJ com ou sem formatação"
)

# Inputs de data no formato brasileiro
st.sidebar.markdown("### 📅 Período de Análise")
col1_sidebar, col2_sidebar = st.sidebar.columns(2)

with col1_sidebar:
    data_inicial_input = st.text_input(
        "Data Inicial",
        value="",
        placeholder="DD/MM/AAAA",
        help="Ex: 01/01/2020",
        key="data_inicial"
    )

with col2_sidebar:
    data_final_input = st.text_input(
        "Data Final",
        value="",
        placeholder="DD/MM/AAAA",
        help="Ex: 31/12/2024",
        key="data_final"
    )

st.sidebar.markdown("---")

# Processar inputs
cnpj_limpo = limpar_cnpj(cnpj_input) if cnpj_input else ""
data_inicial_formatada = converter_data_brasileira(data_inicial_input) if data_inicial_input else None
data_final_formatada = converter_data_brasileira(data_final_input) if data_final_input else None

# Validação
cnpj_valido = False
datas_validas = False

if cnpj_input:
    if len(cnpj_limpo) != 14:
        st.sidebar.error("❌ CNPJ deve conter 14 dígitos")
    else:
        st.sidebar.success(f"✅ CNPJ: {cnpj_limpo}")
        cnpj_valido = True

if data_inicial_input and data_final_input:
    if not data_inicial_formatada or not data_final_formatada:
        st.sidebar.error("❌ Formato de data inválido. Use DD/MM/AAAA")
    else:
        st.sidebar.success(f"✅ Período: {data_inicial_input} a {data_final_input}")
        datas_validas = True

# Botão para carregar dados
carregar_button = st.sidebar.button("🔄 Carregar Dados", type="primary", use_container_width=True)

# Título principal
st.title("📊 Dashboard de Fundos de Investimentos")
st.markdown("**Análise completa e profissional de performance**")
st.markdown("---")

# Função para carregar dados
@st.cache_data
def carregar_dados(cnpj, data_ini, data_fim):
    url = f"https://www.okanebox.com.br/api/fundoinvestimento/hist/{cnpj}/{data_ini}/{data_fim}/"
    req = urllib.request.Request(url)
    req.add_header('Accept-Encoding', 'gzip')
    req.add_header('Authorization', 'Bearer caianfrancodecamargo@gmail.com')

    response = urllib.request.urlopen(req)

    if response.info().get('Content-Encoding') == 'gzip':
        buf = BytesIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        content_json = json.loads(f.read().decode("utf-8"))
    else:
        content = response.read().decode("utf-8")
        content_json = json.loads(content)

    df = pd.DataFrame(content_json)

    if 'DT_COMPTC' in df.columns:
        df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'])

    return df

# Função para formatar valores em BRL
def format_brl(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Função para formatar percentual
def fmt_pct_port(x):
    return f"{x*100:.2f}%".replace('.', ',')

# Verificar se deve carregar os dados
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False

if carregar_button:
    if not cnpj_input:
        st.warning("⚠️ Por favor, informe o CNPJ do fundo")
        st.stop()

    if not data_inicial_input or not data_final_input:
        st.warning("⚠️ Por favor, informe o período de análise")
        st.stop()

    if not cnpj_valido or not datas_validas:
        st.error("❌ Corrija os erros indicados na barra lateral antes de continuar")
        st.stop()

    st.session_state.dados_carregados = True
    st.session_state.cnpj = cnpj_limpo
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada

if not st.session_state.dados_carregados:
    st.info("👈 **Bem-vindo!** Configure os parâmetros na barra lateral e clique em 'Carregar Dados' para começar a análise.")

    # Instruções de uso
    with st.expander("📖 Como usar este dashboard"):
        st.markdown("""
        ### Passo a passo:

        1. **CNPJ do Fundo**: Digite o CNPJ do fundo que deseja analisar
           - Pode ser com ou sem formatação (ex: 10.500.884/0001-05 ou 10500884000105)

        2. **Período de Análise**: Informe as datas no formato brasileiro
           - Data Inicial: DD/MM/AAAA (ex: 01/01/2020)
           - Data Final: DD/MM/AAAA (ex: 31/12/2024)

        3. **Carregar Dados**: Clique no botão verde para iniciar a análise

        ### O que você verá:
        - 📈 Rentabilidade histórica e CAGR
        - 📉 Análise de risco (Drawdown, Volatilidade, VaR)
        - 💰 Evolução patrimonial e captação
        - 👥 Perfil de cotistas
        - 🎯 Retornos em janelas móveis
        """)

    st.stop()

try:
    with st.spinner('🔄 Carregando dados... Aguarde.'):
        df = carregar_dados(st.session_state.cnpj, st.session_state.data_ini, st.session_state.data_fim)

    # Preparação dos dados
    df = df.sort_values('DT_COMPTC')

    # Calcular métricas principais
    df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
    df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100
    df['Captacao_Liquida'] = df['CAPTC_DIA'] - df['RESG_DIA']
    df['Soma_Acumulada'] = df['Captacao_Liquida'].cumsum()
    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

    # Volatilidade
    vol_window = 21
    trading_days = 252
    df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()
    df['Volatilidade'] = df['VL_QUOTA'].pct_change().rolling(vol_window).std() * np.sqrt(trading_days) * 100
    vol_hist = round(df['Variacao_Perc'].std() * np.sqrt(trading_days) * 100, 2)

    # CAGR
    df_cagr = df.copy()
    end_value = df_cagr['VL_QUOTA'].iloc[-1]
    df_cagr['dias_uteis'] = df_cagr.index[-1] - df_cagr.index
    df_cagr = df_cagr[df_cagr['dias_uteis'] >= 252].copy()
    df_cagr['CAGR'] = ((end_value / df_cagr['VL_QUOTA']) ** (252 / df_cagr['dias_uteis'])) - 1
    df_cagr['CAGR'] = df_cagr['CAGR'] * 100
    mean_cagr = df_cagr['CAGR'].mean()

    # Retorno 21 dias para VaR
    df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
    df_plot = df.dropna(subset=['Retorno_21d']).copy()
    VaR_95 = np.percentile(df_plot['Retorno_21d'], 5)
    VaR_99 = np.percentile(df_plot['Retorno_21d'], 1)
    ES_95 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
    ES_99 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()

    # Cards com métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Patrimônio Líquido", format_brl(df['VL_PATRIM_LIQ'].iloc[-1]))

    with col2:
        st.metric("👥 Número de Cotistas", f"{int(df['NR_COTST'].iloc[-1]):,}".replace(',', '.'))

    with col3:
        st.metric("📈 CAGR Médio", f"{mean_cagr:.2f}%")

    with col4:
        st.metric("📊 Volatilidade Histórica", f"{vol_hist:.2f}%")

    st.markdown("---")

    # Tabs para organizar os gráficos
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Rentabilidade", 
        "📉 Risco", 
        "💰 Patrimônio", 
        "👥 Cotistas",
        "🎯 Janelas Móveis"
    ])

    with tab1:
        st.subheader("Rentabilidade Histórica")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['VL_QUOTA_NORM'],
            mode='lines+markers',
            line=dict(color='#2d8a6e', width=2),
            marker=dict(size=3),
            hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br><b>Rentabilidade:</b> %{y:.2f}%<extra></extra>'
        ))

        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade (%)",
            template="plotly_white",
            hovermode="closest",
            height=500
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("CAGR Anual por Dia de Aplicação")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=_COMPTC'],
            y=df_cagr['CAGR'],
            mode='lines',
            name='CAGR',
            line=dict(color='#2d8a6e'),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
        ))

        fig2.add_trace(go.Scatter(
            x=df_cagr['DT_COMPTC'],
            y=[mean_cagr] * len(df_cagr),
            mode='lines',
            line=dict(dash='dash', color='gray'),
            name=f'CAGR Médio ({mean_cagr:.2f}%)'
        ))

        fig2.update_layout(
            xaxis_title="Data",
            yaxis_title="CAGR (% a.a)",
            template="plotly_white",
            hovermode="closest",
            height=500
        )

        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Drawdown Histórico")

        fig3 = go.Figure(data=go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Drawdown'],
            mode='lines',
            name='Drawdown',
            line=dict(color='firebrick'),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
        ))

        fig3.add_hline(y=0, line_dash='dash', line_color='gray')

        fig3.update_layout(
            xaxis_title="Data",
            yaxis_title="Drawdown (%)",
            template="plotly_white",
            hovermode="closest",
            height=500
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"Volatilidade Móvel ({vol_window} dias úteis)")

        fig4 = go.Figure([
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Volatilidade'],
                mode='lines',
                name=f'Volatilidade {vol_window} dias',
                line=dict(color='#2d8a6e'),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
            ),
            go.Scatter(
                x=df['DT_COMPTC'],
                y=[vol_hist] * len(df),
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name=f'Vol. Histórica ({vol_hist:.2f}%)'
            )
        ])

        fig4.update_layout(
            xaxis_title="Data",
            yaxis_title="Volatilidade (% a.a.)",
            template="plotly_white",
            hovermode="closest",
            height=500
        )

        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Value at Risk (VaR) e Expected Shortfall (ES)")

        fig5 = go.Figure()

        fig5.add_trace(go.Scatter(
            x=df_plot['DT_COMPTC'],
            y=df_plot['Retorno_21d'] * 100,
            mode='lines',
            name='Rentabilidade móvel (1m)',
            line=dict(color='#2d8a6e', width=2),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade 21d: %{y:.2f}%<extra></extra>'
        ))

        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[VaR_95 * 100, VaR_95 * 100],
            mode='lines',
            name='VaR 95%',
            line=dict(dash='dot', color='orange')
        ))

        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[VaR_99 * 100, VaR_99 * 100],
            mode='lines',
            name='VaR 99%',
            line=dict(dash='dot', color='red')
        ))

        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[ES_95 * 100, ES_95 * 100],
            mode='lines',
            name='ES 95%',
            line=dict(dash='dash', color='orange')
        ))

        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[ES_99 * 100, ES_99 * 100],
            mode='lines',
            name='ES 99%',
            line=dict(dash='dash', color='red')
        ))

        fig5.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade (%)",
            template="plotly_white",
            hovermode="x unified",
            height=600
        )

        st.plotly_chart(fig5, use_container_width=True)

        st.info(f"""
        **Este gráfico mostra que, em um período de 1 mês:**

        • Há **99%** de confiança de que o fundo não cairá mais do que **{fmt_pct_port(VaR_99)} (VaR)**, 
        e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_99)} (ES)**.

        • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(VaR_95)} (VaR)**, 
        e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_95)} (ES)**.
        """)

    with tab3("Patrimônio e Captação Líquida")

        fig6 = go.Figure([
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Soma_Acumulada'],
                mode='lines',
                name='Captação Líquida',
                line=dict(color='#2d8a6e'),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Captação Líquida Acumulada: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['Soma_Acumulada']]
            ),
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_PATRIM_LIQ'],
                mode='lines',
                name='Patrimônio Líquido',
                line=dict(color='#3ab795'),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Líquido: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['VL_PATRIM_LIQ']]
            )
        ])

        fig6.update_layout(
            xaxis_title="Data",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="closest",
            height=500
        )

        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("Captação Líquida Mensal")

        df_monthly = df.groupby(pd.Grouper(key='DT_COMPTC', freq='M'))[['CAPTC_DIA', 'RESG_DIA']].sum()
        df_monthly['Captacao_Liquida'] = df_monthly['CAPTC_DIA'] - df_monthly['RESG_DIA']

        fig7 = go.Figure([
            go.Bar(
                x=df_monthly.index,
                y=df_monthly['Captacao_Liquida'],
                name='Captação Líquida Mensal',
                marker_color='#2d8a6e',
                hovertemplate='Mês: %{x|%b/%Y}<br>Captação Líquida: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df_monthly['Captacao_Liquida']]
            )
        ])

        fig7.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="closest",
            height=500
        )

        st.plotly_chart(fig7, use_container_width=True)

    with tab4:
        st.subheader("Patrimônio Médio e Nº de Cotistas")

        fig8 = go.Figure()

        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Patrimonio_Liq_Medio'],
            mode='lines',
            name='Patrimônio Médio por Cotista',
            line=dict(color='#2d8a6e'),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Médio: %{customdata}<extra></extra>',
            customdata=[format_brl(v) for v in df['Patrimonio_Liq_Medio']]
        ))

        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['NR_COTST'],
            mode='lines',
            name='Número de Cotistas',
            line=dict(color='#3ab795'),
            yaxis='y2',
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Nº de Cotistas: %{y}<extra></extra>'
        ))

        fig8.update_layout(
            xaxis_title="Data",
            yaxis=dict(title="Patrimônio Médio por Cotista (R$)"),
            yaxis2=dict(title="Número de Cotistas", overlaying="y", side="right"),
            template="plotly_white",
            hovermode="closest",
            height=500
        )

        st.plotly_chart(fig8, use_container_width=True)

    with tab5:
        st.subheader("Retornos em Janelas Móveis")

        janelas = {
            "12 meses (252 dias)": 252,
            "24 meses (504 dias)": 504,
            "36 meses (756 dias)": 756,
            "48 meses (1008 dias)": 1008,
            "60 meses (1260 dias)": 1260
        }

        df_returns = df.copy()

        for nome, dias in janelas.items():
            df_returns[nome] = df_returns['VL_QUOTA'] / df_returns['VL_QUOTA'].shift(dias) - 1

        janela_selecionada = st.selectbox("Selecione o período:", list(janelas.keys()))

        if not df_returns[janela_selecionada].dropna().empty:
            fig9 = go.Figure()

            fig9.add_trace(go.Scatter(
                x=df_returns['DT_COMPTC'],
                y=df_returns[janela_selecionada],
                mode='lines',
                name=f"Retorno — {janela_selecionada}",
                line=dict(width=2, color="#2d8a6e"),
                hovertemplate="Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
            ))

            fig9.update_layout(
                xaxis_title="Data",
                yaxis_title="Retorno (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                yaxis=dict(tickformat=".2%")
            )

            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning(f"Não há dados suficientes para calcular {janela_selecionada}.")

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("💡 Verifique sua conexão com a internet e se os dados informados estão corretos.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p style='margin: 0;'>Dashboard desenvolvido com ❤️ usando Streamlit e Plotly</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>© 2025 - Análise Profissional de Fundos de Investimento</p>
</div>
""", unsafe_allow_html=True)
