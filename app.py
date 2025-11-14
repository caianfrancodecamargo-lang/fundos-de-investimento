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

# CSS customizado inspirado no site Copaíba Invest
st.markdown("""
<style>
    /* Importar fonte similar */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Variáveis de cores inspiradas no Copaíba */
    :root {
        --primary-color: #1a5f3f;
        --secondary-color: #2d8659;
        --accent-color: #f0b429;
        --dark-bg: #0f1419;
        --light-bg: #f8f9fa;
        --text-dark: #1a1a1a;
        --text-light: #ffffff;
    }

    /* Fundo geral */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a5f3f 0%, #0f3d28 100%);
        padding: 2rem 1rem;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    /* INPUTS COM FONTE PRETA */
    [data-testid="stSidebar"] input {
        background-color: #ffffff !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
        color: #000000 !important;  /* ← FONTE PRETA */
        border-radius: 8px;
        padding: 0.5rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] input::placeholder {
        color: #666666 !important;  /* ← PLACEHOLDER CINZA */
        opacity: 0.7 !important;
    }

    /* Garantir que o texto digitado seja preto */
    [data-testid="stSidebar"] input:focus {
        color: #000000 !important;
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 2px rgba(240, 180, 41, 0.2) !important;
    }

    /* Botão principal */
    .stButton > button {
        background: linear-gradient(135deg, #f0b429 0%, #d99b1f 100%);
        color: #1a1a1a;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(240, 180, 41, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(240, 180, 41, 0.4);
        background: linear-gradient(135deg, #d99b1f 0%, #f0b429 100%);
    }

    /* Título principal */
    h1 {
        color: #1a5f3f;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Cards de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a5f3f;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="metric-container"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1a5f3f;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #6c757d;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1a5f3f 0%, #2d8659 100%);
        color: white !important;
    }

    /* Subtítulos */
    h2, h3 {
        color: #1a5f3f;
        font-weight: 600;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #1a5f3f;
    }

    /* Divisor */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #1a5f3f, transparent);
    }

    /* Mensagens de sucesso/erro na sidebar */
    [data-testid="stSidebar"] .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Função para limpar CNPJ (remove tudo que não é número)
def limpar_cnpj(cnpj):
    if not cnpj:
        return ""
    return re.sub(r'\D', '', cnpj)

# Função para converter data brasileira (DD/MM/AAAA) para formato API (AAAAMMDD)
def formatar_data_api(data_str):
    """
    Converte data do formato brasileiro DD/MM/AAAA para AAAAMMDD
    Aceita formatos: DD/MM/AAAA, DD-MM-AAAA, DD.MM.AAAA ou DDMMAAAA
    """
    if not data_str:
        return None

    # Remove caracteres não numéricos
    data_limpa = re.sub(r'\D', '', data_str)

    # Verifica se tem 8 dígitos
    if len(data_limpa) == 8:
        try:
            # Assume formato brasileiro DDMMAAAA
            dia = data_limpa[:2]
            mes = data_limpa[2:4]
            ano = data_limpa[4:]

            # Valida a data
            datetime.strptime(f"{dia}/{mes}/{ano}", '%d/%m/%Y')

            # Retorna no formato AAAAMMDD
            return f"{ano}{mes}{dia}"
        except ValueError:
            return None

    return None

# Sidebar com inputs do usuário
st.sidebar.markdown("### ⚙️ Configurações")
st.sidebar.markdown("---")

# Input de CNPJ (vazio por padrão)
cnpj_input = st.sidebar.text_input(
    "CNPJ do Fundo",
    value="",
    placeholder="00.000.000/0000-00",
    help="Digite o CNPJ com ou sem formatação"
)

# Inputs de data (vazios por padrão)
st.sidebar.markdown("#### 📅 Período de Análise")
col1_sidebar, col2_sidebar = st.sidebar.columns(2)

with col1_sidebar:
    data_inicial_input = st.text_input(
        "Data Inicial",
        value="",
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        key="data_inicial"
    )

with col2_sidebar:
    data_final_input = st.text_input(
        "Data Final",
        value="",
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        key="data_final"
    )

st.sidebar.markdown("---")

# Processar inputs
cnpj_limpo = limpar_cnpj(cnpj_input)
data_inicial_formatada = formatar_data_api(data_inicial_input)
data_final_formatada = formatar_data_api(data_final_input)

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
        # Converte para exibição
        try:
            dt_ini = datetime.strptime(data_inicial_formatada, '%Y%m%d')
            dt_fim = datetime.strptime(data_final_formatada, '%Y%m%d')

            if dt_ini > dt_fim:
                st.sidebar.error("❌ Data inicial deve ser anterior à data final")
            else:
                st.sidebar.success(f"✅ Período: {dt_ini.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}")
                datas_validas = True
        except:
            st.sidebar.error("❌ Erro ao processar datas")

# Botão para carregar dados
carregar_button = st.sidebar.button("🔄 Carregar Dados", type="primary", disabled=not (cnpj_valido and datas_validas))

# Título principal
st.markdown("<h1>📊 Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
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

if carregar_button and cnpj_valido and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpj = cnpj_limpo
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada

if not st.session_state.dados_carregados:
    st.info("👈 Preencha os campos na barra lateral e clique em 'Carregar Dados' para começar a análise.")

    # Instruções de uso
    st.markdown("""
    ### 📋 Como usar:

    1. **CNPJ do Fundo**: Digite o CNPJ do fundo que deseja analisar (com ou sem formatação)
    2. **Data Inicial**: Digite a data inicial no formato DD/MM/AAAA (ex: 01/01/2020)
    3. **Data Final**: Digite a data final no formato DD/MM/AAAA (ex: 31/12/2024)
    4. Clique em **Carregar Dados** para visualizar as análises

    ---

    ### 📊 Análises disponíveis:
    - Rentabilidade histórica e CAGR
    - Análise de risco (Drawdown, Volatilidade, VaR)
    - Evolução patrimonial e captação
    - Perfil de cotistas
    - Retornos em janelas móveis
    """)

    st.stop()

try:
    with st.spinner('🔄 Carregando dados...'):
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

    # Configuração de cores para os gráficos
    color_primary = '#1a5f3f'
    color_secondary = '#f0b429'
    color_danger = '#dc3545'

    with tab1:
        st.subheader("📈 Rentabilidade Histórica")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['VL_QUOTA_NORM'],
            mode='lines',
            line=dict(color=color_primary, width=2.5),
            fill='tozeroy',
            fillcolor=f'rgba(26, 95, 63, 0.1)',
            hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br><b>Rentabilidade:</b> %{y:.2f}%<extra></extra>'
        ))

        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade (%)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 CAGR Anual por Dia de Aplicação")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_cagr['DT_COMPTC'],
            y=df_cagr['CAGR'],
            mode='lines',
            name='CAGR',
            line=dict(color=color_primary))
