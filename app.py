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
from datetime import datetime, timedelta
import base64

# Importar biblioteca para obter dados do CDI
try:
    from bcb import sgs
    BCB_DISPONIVEL = True
except ImportError:
    BCB_DISPONIVEL = False
    st.warning("⚠️ Biblioteca 'python-bcb' não encontrada. Instale com: pip install python-bcb")

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Fundos de Investimentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para converter imagem local em base64
def get_image_base64(image_path):
    """Converte uma imagem local para base64 para uso no Plotly"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Caminho da logo
LOGO_PATH = "copaiba_logo.png"
logo_base64 = get_image_base64(LOGO_PATH)

# CSS customizado com espaçamentos reduzidos na sidebar
st.markdown("""
<style>
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

    /* Sidebar com padding reduzido */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #5a8a6f 0%, #4a7a5f 100%);
        padding: 1rem 0.8rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Logo na sidebar - espaçamento reduzido */
    [data-testid="stSidebar"] .sidebar-logo {
        text-align: center;
        padding: 0.5rem 0 0.8rem 0 !important;
        margin-bottom: 0.8rem !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }

    [data-testid="stSidebar"] .sidebar-logo img {
        max-width: 240px !important;
        height: auto;
        filter: brightness(1.05);
    }

    /* Labels dos inputs - espaçamento reduzido */
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.8rem !important;
        margin-bottom: 0.2rem !important;
        margin-top: 0 !important;
    }

    /* Reduzir espaçamento entre elementos */
    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 0.4rem !important;
    }

    /* Título "Período de Análise" com menos espaço */
    [data-testid="stSidebar"] h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
        font-size: 0.85rem !important;
    }

    /* Divisores com menos espaço */
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
    }

    /* INPUTS COM BORDA ELEGANTE */
    [data-testid="stSidebar"] input {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.6) !important;
        color: #000000 !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.3s ease !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stSidebar"] input::placeholder {
        color: #666666 !important;
        opacity: 0.8 !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] input:focus {
        color: #000000 !important;
        border-color: #8ba888 !important;
        box-shadow: 0 4px 12px rgba(139, 168, 136, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stSidebar"] input:hover {
        border-color: rgba(139, 168, 136, 0.5) !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12) !important;
    }

    /* BOTÃO COM DEGRADÊ - espaçamento reduzido */
    .stButton > button {
        background: linear-gradient(135deg, #6b9b7f 0%, #8ba888 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 3px 12px rgba(107, 155, 127, 0.3) !important;
        width: 100% !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-top: 0.5rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 16px rgba(107, 155, 127, 0.5) !important;
        background: linear-gradient(135deg, #8ba888 0%, #6b9b7f 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Mensagens de validação - espaçamento reduzido */
    [data-testid="stSidebar"] .stAlert {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 250, 0.98) 100%) !important;
        border-radius: 10px !important;
        padding: 0.5rem 0.7rem !important;
        margin: 0.3rem 0 !important;
        border-left: 3px solid #28a745 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        font-size: 0.8rem !important;
    }

    [data-testid="stSidebar"] .stAlert [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] .stAlert * {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stCheckbox {
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stSidebar"] .stCheckbox label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
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
        background: linear-gradient(135deg, #ffffff 0%, #f8f6f1 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #6b9b7f;
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #ffffff 0%, #f8f6f1 100%);
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
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(107, 155, 127, 0.1);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6b9b7f 0%, #8ba888 100%);
        color: white !important;
        box-shadow: 0 3px 10px rgba(107, 155, 127, 0.3);
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

    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f8f9fa;
    }

    ::-webkit-scrollbar-thumb {
        background: #6b9b7f;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #1a5f3f;
    }
</style>
""", unsafe_allow_html=True)

# Função para adicionar marca d'água GIGANTE e estilizar gráficos
def add_watermark_and_style(fig, logo_base64=None, x_range=None, x_autorange=True):
    """
    Adiciona marca d'água MUITO GRANDE cobrindo todo o gráfico e aplica estilo.
    Permite definir o range do eixo X.
    """
    if logo_base64:
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{logo_base64}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                sizex=1.75,  # 120% do tamanho do gráfico
                sizey=1.75,  # 120% do tamanho do gráfico
                xanchor="center",
                yanchor="middle",
                opacity=0.15,  # <<< OPACIDADE DA MARCA D'ÁGUA AJUSTADA PARA 0.15
                layer="below"
            )
        )

    # Estilização elegante
    fig.update_layout(
        plot_bgcolor='rgba(248, 246, 241, 0.5)',
        paper_bgcolor='white',
        font=dict(
            family="Inter, sans-serif",
            size=12,
            color="#2c2c2c"
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Inter, sans-serif",
            bordercolor="#6b9b7f"
        ),
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(color="#e0ddd5", width=2),
                fillcolor="rgba(0,0,0,0)"
            )
        ]
    )

    # Estilizar eixos
    x_axes_update_params = dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(224, 221, 213, 0.5)',
        showline=True,
        linewidth=2,
        linecolor='#e0ddd5',
        title_font=dict(size=13, color="#1a5f3f", family="Inter"),
        tickfont=dict(size=11, color="#6b9b7f")
    )

    if x_range is not None:
        x_axes_update_params['range'] = x_range
        x_axes_update_params['autorange'] = False # Se o range é definido, desativa o autorange
    else:
        x_axes_update_params['autorange'] = x_autorange # Usa o autorange padrão ou passado

    fig.update_xaxes(**x_axes_update_params)

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(224, 221, 213, 0.5)',
        showline=True,
        linewidth=2,
        linecolor='#e0ddd5',
        title_font=dict(size=13, color="#1a5f3f", family="Inter"),
        tickfont=dict(size=11, color="#6b9b7f")
    )

    return fig

# Função para limpar CNPJ
def limpar_cnpj(cnpj):
    if not cnpj:
        return ""
    return re.sub(r'\D', '', cnpj)

# Função para converter data brasileira para formato API
def formatar_data_api(data_str):
    if not data_str:
        return None
    data_limpa = re.sub(r'\D', '', data_str)
    if len(data_limpa) == 8:
        try:
            dia = data_limpa[:2]
            mes = data_limpa[2:4]
            ano = data_limpa[4:]
            datetime.strptime(f"{dia}/{mes}/{ano}", '%d/%m/%Y')
            return f"{ano}{mes}{dia}"
        except ValueError:
            return None
    return None

# FUNÇÃO PARA OBTER DADOS REAIS DO CDI - CORRIGIDA DEFINITIVAMENTE
@st.cache_data
def obter_dados_cdi_real(data_inicio: datetime, data_fim: datetime):
    """
    Obtém dados REAIS do CDI usando a biblioteca python-bcb
    Recalcula o acumulado APENAS com as taxas do período
    e normaliza para começar em 1.0.
    """
    if not BCB_DISPONIVEL:
        return pd.DataFrame()

    try:
        # Obter dados do CDI (série 12) - retorna apenas as taxas diárias
        cdi_diario = sgs.get({'cdi': 12}, start=data_inicio, end=data_fim)

        # Transformar o índice em coluna
        cdi_diario = cdi_diario.reset_index()

        # Alterar o nome da coluna
        cdi_diario = cdi_diario.rename(columns={'Date': 'DT_COMPTC'})

        # Calcular o fator diário
        cdi_diario['CDI_fator_diario'] = 1 + (cdi_diario['cdi'] / 100)

        # Calcular a cota do CDI normalizada para 1.0 no início do período
        cdi_diario['CDI_COTA'] = cdi_diario['CDI_fator_diario'].cumprod()
        if not cdi_diario.empty:
            cdi_diario['CDI_COTA'] = cdi_diario['CDI_COTA'] / cdi_diario['CDI_COTA'].iloc[0]

        cdi_diario['DT_COMPTC'] = pd.to_datetime(cdi_diario['DT_COMPTC'])
        cdi_diario = cdi_diario.set_index('DT_COMPTC').asfreq('D').fillna(method='ffill').reset_index()

        return cdi_diario[['DT_COMPTC', 'CDI_COTA']]
    except Exception as e:
        st.error(f"❌ Erro ao obter dados do CDI: {e}")
        return pd.DataFrame()

# FUNÇÃO PARA OBTER DADOS DO FUNDO DA CVM - REINTRODUZIDA
@st.cache_data(ttl=3600) # Cache por 1 hora
def obter_dados_fundo(cnpj: str, data_inicio: datetime, data_fim: datetime):
    """
    Obtém dados históricos de um fundo de investimento da CVM.
    """
    cnpj_limpo = limpar_cnpj(cnpj)
    if not cnpj_limpo:
        return pd.DataFrame(), "CNPJ inválido."

    ano_inicio = data_inicio.year
    ano_fim = data_fim.year

    all_data = []
    for ano in range(ano_inicio, ano_fim + 1):
        url = f"https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ano}.zip"
        try:
            with urllib.request.urlopen(url) as response:
                with gzip.open(BytesIO(response.read()), 'rt', encoding='latin-1') as f:
                    df_ano = pd.read_csv(f, sep=';')
                    all_data.append(df_ano)
        except Exception as e:
            st.warning(f"⚠️ Não foi possível carregar dados para o ano {ano}. Erro: {e}")
            continue

    if not all_data:
        return pd.DataFrame(), "Nenhum dado encontrado para o período e CNPJ especificados."

    df_full = pd.concat(all_data, ignore_index=True)

    # Filtrar pelo CNPJ
    df_fundo = df_full[df_full['CNPJ_FUNDO'] == cnpj_limpo].copy()

    if df_fundo.empty:
        return pd.DataFrame(), f"Nenhum dado encontrado para o CNPJ {cnpj_limpo} no período."

    # Conversão de tipos
    df_fundo['DT_COMPTC'] = pd.to_datetime(df_fundo['DT_COMPTC'])
    df_fundo['VL_QUOTA'] = pd.to_numeric(df_fundo['VL_QUOTA'], errors='coerce')
    df_fundo['VL_PATRIM_LIQ'] = pd.to_numeric(df_fundo['VL_PATRIM_LIQ'], errors='coerce')
    df_fundo['CAPTC_DIA'] = pd.to_numeric(df_fundo['CAPTC_DIA'], errors='coerce')
    df_fundo['RESG_DIA'] = pd.to_numeric(df_fundo['RESG_DIA'], errors='coerce')
    df_fundo['NR_COTST'] = pd.to_numeric(df_fundo['NR_COTST'], errors='coerce')

    # Filtrar pelo período selecionado
    df_fundo = df_fundo[(df_fundo['DT_COMPTC'] >= data_inicio) & (df_fundo['DT_COMPTC'] <= data_fim)]

    # Remover linhas com valores nulos importantes
    df_fundo.dropna(subset=['VL_QUOTA', 'VL_PATRIM_LIQ'], inplace=True)

    if df_fundo.empty:
        return pd.DataFrame(), f"Nenhum dado válido de cota ou patrimônio encontrado para o CNPJ {cnpj_limpo} no período."

    df_fundo = df_fundo.sort_values('DT_COMPTC').reset_index(drop=True)

    # Calcular retornos diários
    df_fundo['Retorno_Diario'] = df_fundo['VL_QUOTA'].pct_change()

    # Calcular Drawdown
    df_fundo['Pico'] = df_fundo['VL_QUOTA'].cummax()
    df_fundo['Drawdown'] = (df_fundo['VL_QUOTA'] / df_fundo['Pico'] - 1) * 100 # Em porcentagem

    # Calcular Patrimônio Líquido Médio por Cotista
    df_fundo['Patrimonio_Liq_Medio'] = df_fundo['VL_PATRIM_LIQ'] / df_fundo['NR_COTST']

    # Calcular Captação Líquida Acumulada
    df_fundo['Soma_Acumulada'] = (df_fundo['CAPTC_DIA'] - df_fundo['RESG_DIA']).cumsum()

    return df_fundo, None

# Funções de formatação
def format_brl(value):
    if pd.isna(value):
        return "N/A"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.2%}"

def fmt_pct_port(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}%"

# Cores
color_primary = "#1a5f3f"
color_secondary = "#2d8659"
color_accent = "#f0b429"
color_cdi = "#6c757d"
color_danger = "#dc3545"

# Sidebar para entrada de dados
st.sidebar.image(LOGO_PATH, use_column_width=True, output_format="PNG", caption="Copaíba Invest", clamp=True)
st.sidebar.markdown("<div class='sidebar-logo'></div>", unsafe_allow_html=True)

st.sidebar.title("Configurações do Dashboard")

cnpj_fundo = st.sidebar.text_input("CNPJ do Fundo (apenas números):", "31790006000108") # Exemplo: BTG Pactual Absoluto FIM
st.sidebar.markdown("---")

st.sidebar.markdown("#### Período de Análise")
data_fim_padrao = datetime.now() - timedelta(days=1)
data_inicio_padrao = data_fim_padrao - timedelta(days=5*365) # 5 anos

data_inicio = st.sidebar.date_input("Data de Início:", value=data_inicio_padrao)
data_fim = st.sidebar.date_input("Data de Fim:", value=data_fim_padrao)

comparar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)
st.sidebar.markdown("---")

# Converter datas para datetime para uso nas funções
data_inicio_dt = datetime.combine(data_inicio, datetime.min.time())
data_fim_dt = datetime.combine(data_fim, datetime.min.time())

# --- Carregar Dados ---
df, erro_fundo = obter_dados_fundo(cnpj_fundo, data_inicio_dt, data_fim_dt)

tem_cdi = False
if comparar_cdi:
    df_cdi = obter_dados_cdi_real(data_inicio_dt, data_fim_dt)
    if not df_cdi.empty:
        # Mesclar dados do fundo e CDI
        df = pd.merge(df, df_cdi, on='DT_COMPTC', how='left')
        df['CDI_COTA'] = df['CDI_COTA'].fillna(method='ffill')
        df['CDI_Retorno_Diario'] = df['CDI_COTA'].pct_change()
        tem_cdi = True
    else:
        st.warning("⚠️ Não foi possível carregar dados do CDI para o período selecionado. A comparação com CDI será desativada.")
        comparar_cdi = False

if erro_fundo:
    st.error(f"❌ Erro ao carregar os dados do fundo: {erro_fundo}")
    st.stop()

if df.empty:
    st.warning("⚠️ Nenhum dado disponível para o fundo e período selecionados. Ajuste o CNPJ ou o período.")
    st.stop()

# --- Cálculos de Métricas de Desempenho e Risco ---
trading_days_in_year = 252 # Aproximadamente 252 dias úteis no ano
num_dias_no_periodo = (df['DT_COMPTC'].iloc[-1] - df['DT_COMPTC'].iloc[0]).days

# Retorno Total do Fundo
retorno_total_fundo = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1

# CAGR (Anualizado) - Retorno total anualizado
if num_dias_no_periodo > 0:
    cagr_fundo = (1 + retorno_total_fundo) ** (trading_days_in_year / len(df)) - 1
else:
    cagr_fundo = np.nan

# Volatilidade Histórica Anualizada
if len(df['Retorno_Diario'].dropna()) > 1:
    volatilidade_historica_anualizada = df['Retorno_Diario'].std() * np.sqrt(trading_days_in_year)
else:
    volatilidade_historica_anualizada = np.nan

# Retorno Total do CDI
retorno_total_cdi = np.nan
if tem_cdi and not df['CDI_COTA'].dropna().empty:
    retorno_total_cdi = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0]) - 1

# Excesso de Retorno Anualizado (Rolling)
if tem_cdi and len(df) >= trading_days_in_year:
    df['Retorno_Diario_Fundo'] = df['VL_QUOTA'].pct_change()
    df['Retorno_Diario_CDI'] = df['CDI_COTA'].pct_change()

    # Retorno anualizado móvel (rolling)
    df['ROLLING_ANN_RETURN_FUND'] = (1 + df['Retorno_Diario_Fundo']).rolling(window=trading_days_in_year).apply(np.prod, raw=True) - 1
    df['ROLLING_ANN_RETURN_CDI'] = (1 + df['Retorno_Diario_CDI']).rolling(window=trading_days_in_year).apply(np.prod, raw=True) - 1

    df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'] = (df['ROLLING_ANN_RETURN_FUND'] - df['ROLLING_ANN_RETURN_CDI']) * 100
else:
    df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'] = np.nan


# --- Abas do Dashboard ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Desempenho", "📉 Risco", "💰 Patrimônio e Captação", "👥 Cotistas", "🎯 Janelas Móveis"
])

with tab1:
    st.subheader("📈 Desempenho Histórico")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df['DT_COMPTC'],
        y=df['VL_QUOTA'] / df['VL_QUOTA'].iloc[0],
        mode='lines',
        name='Fundo',
        line=dict(color=color_primary, width=2.5),
        hovertemplate='Data: %{x|%d/%m/%Y}<br>Cota Acumulada: %{y:.2f}<extra></extra>'
    ))

    if tem_cdi:
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['CDI_COTA'],
            mode='lines',
            name='CDI',
            line=dict(color=color_cdi, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>CDI Acumulado: %{y:.2f}<extra></extra>'
        ))

    fig1.update_layout(
        xaxis_title="Data",
        yaxis_title="Cota Acumulada (Base 1)",
        template="plotly_white",
        hovermode="x unified",
        height=500,
        font=dict(family="Inter, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 Métricas de Desempenho")
    col1_perf, col2_perf = st.columns(2)

    with col1_perf:
        st.metric("Retorno Total", fmt_pct(retorno_total_fundo))
        st.info("O retorno total do fundo no período selecionado. Indica o ganho ou perda percentual desde o início até o fim da análise.")
    with col2_perf:
        st.metric("CAGR (Anualizado)", fmt_pct(cagr_fundo))
        st.info("A Taxa de Crescimento Anual Composta. Representa a taxa média anual de crescimento do investimento ao longo do período, considerando o efeito dos juros compostos.")

    if tem_cdi:
        st.markdown("---")
        st.subheader("✨ Excesso de Retorno Anualizado (Rolling 252 dias)")
        if not df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'].dropna().empty:
            fig_excess_return = go.Figure()
            fig_excess_return.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'],
                mode='lines',
                name='Excesso de Retorno Anualizado',
                line=dict(color=color_accent, width=2.5),
                fill='tozeroy',
                fillcolor='rgba(240, 180, 41, 0.1)',
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Excesso de Retorno: %{y:.2f}%<extra></extra>'
            ))
            fig_excess_return.update_layout(
                xaxis_title="Data",
                yaxis_title="Excesso de Retorno Anualizado (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            fig_excess_return = add_watermark_and_style(fig_excess_return, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig_excess_return, use_container_width=True)
            st.info("Este gráfico mostra a diferença anualizada entre o retorno do fundo e o CDI, calculada em janelas móveis de 252 dias. Valores positivos indicam que o fundo superou o CDI nesse período móvel.")
        else:
            st.warning("⚠️ Não há dados suficientes (mínimo de 252 dias) para calcular o Excesso de Retorno Anualizado Rolling.")


with tab2:
    st.subheader("📉 Análise de Risco")

    # Cálculos de risco
    if not df.empty and len(df) > trading_days_in_year: # Mínimo de 1 ano de dados para métricas anualizadas
        # Retornos diários do fundo
        daily_returns_fund = df['Retorno_Diario'].dropna()
        num_obs = len(daily_returns_fund)

        # Retornos diários do CDI
        daily_returns_cdi = df['CDI_Retorno_Diario'].dropna() if tem_cdi else pd.Series([0.0] * num_obs)

        # Retorno anualizado do fundo (usando o CAGR calculado anteriormente)
        annualized_fund_return = cagr_fundo

        # Retorno anualizado do CDI
        annualized_cdi_return = np.nan
        if tem_cdi and not df['CDI_COTA'].dropna().empty and num_dias_no_periodo > 0:
            annualized_cdi_return = (1 + retorno_total_cdi) ** (trading_days_in_year / len(df_cdi)) - 1
        else:
            annualized_cdi_return = 0.0 # Se não tem CDI, taxa livre de risco é 0 para os cálculos

        # Volatilidade anualizada do fundo
        annualized_fund_volatility = daily_returns_fund.std() * np.sqrt(trading_days_in_year) if len(daily_returns_fund) > 1 else np.nan

        # Max Drawdown
        max_drawdown_value = df['Drawdown'].min() / 100 if not df['Drawdown'].empty else np.nan # Já está em % no df, converter para decimal

        # Ulcer Index
        if not df['Drawdown'].empty:
            squared_drawdowns = (df['Drawdown'] / 100)**2 # Drawdown já está em %, converter para decimal
            ulcer_index = np.sqrt(squared_drawdowns.mean()) if not squared_drawdowns.empty else np.nan
        else:
            ulcer_index = np.nan

        # Volatilidade de Baixa (Downside Volatility)
        downside_returns = daily_returns_fund[daily_returns_fund < 0]
        annualized_downside_volatility = downside_returns.std() * np.sqrt(trading_days_in_year) if len(downside_returns) > 1 else np.nan

        # Tracking Error
        tracking_error = np.nan
        if tem_cdi and len(daily_returns_fund) > 1 and len(daily_returns_cdi) > 1:
            excess_daily_returns = daily_returns_fund - daily_returns_cdi
            tracking_error = excess_daily_returns.std() * np.sqrt(trading_days_in_year)

        # Calcular a média dos 3 piores drawdowns para o Sterling Ratio
        avg_worst_drawdowns = np.nan
        if not df['Drawdown'].empty:
            # Pega os 3 menores (mais negativos) valores de drawdown em porcentagem
            worst_drawdowns_series = df['Drawdown'].nsmallest(3)
            if not worst_drawdowns_series.empty:
                avg_worst_drawdowns = worst_drawdowns_series.mean() / 100 # Converte para decimal

        # --- Ratios ---
        sharpe_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_fund_volatility if annualized_fund_volatility > 0 else np.nan
        sortino_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_downside_volatility if annualized_downside_volatility > 0 else np.nan
        calmar_ratio = (annualized_fund_return - annualized_cdi_return) / abs(max_drawdown_value) if max_drawdown_value != 0 else np.nan
        sterling_ratio = (annualized_fund_return - annualized_cdi_return) / abs(avg_worst_drawdowns) if avg_worst_drawdowns != 0 else np.nan
        martin_ratio = (annualized_fund_return - annualized_cdi_return) / ulcer_index if ulcer_index > 0 else np.nan
        information_ratio = (annualized_fund_return - annualized_cdi_return) / tracking_error if tracking_error > 0 else np.nan

        st.markdown("---")
        st.markdown("#### RISCO MEDIDO PELA VOLATILIDADE")
        col_vol1, col_vol2 = st.columns(2)
        with col_vol1:
            st.metric("Volatilidade Histórica Anualizada", fmt_pct(volatilidade_historica_anualizada))
            st.info("""
            **O que é:** Mede a dispersão dos retornos do fundo em relação à sua média, anualizada. Indica o grau de risco ou incerteza do fundo.
            **Interpretação Geral:**
            *   **Baixa (< 5%):** Geralmente associada a fundos de renda fixa conservadores.
            *   **Média (5% - 15%):** Comum em fundos multimercado ou de renda fixa mais arrojados.
            *   **Alta (> 15%):** Típica de fundos de ações ou com maior exposição a ativos voláteis.
            """)
        with col_vol2:
            st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if not pd.isna(sharpe_ratio) else "N/A")
            st.info("""
            **O que é:** Retorno excedente por unidade de risco (volatilidade total). Quanto maior, melhor o retorno ajustado ao risco.
            **Interpretação Geral:**
            *   **< 0:** O fundo rende menos que a taxa livre de risco (CDI), ou tem retorno negativo. Ruim.
            *   **0 - 0.5:** Retorno ajustado ao risco subótimo.
            *   **0.5 - 1.0:** Retorno ajustado ao risco razoável.
            *   **> 1.0:** Bom retorno ajustado ao risco.
            *   **> 2.0:** Muito bom, excelente retorno ajustado ao risco.
            """)

        col_sortino, col_info_ratio = st.columns(2)
        with col_sortino:
            st.metric("Sortino Ratio", f"{sortino_ratio:.2f}" if not pd.isna(sortino_ratio) else "N/A")
            st.info("""
            **O que é:** Similar ao Sharpe, mas considera apenas a volatilidade de baixa (risco de perdas). Quanto maior, melhor o retorno ajustado ao risco de queda.
            **Interpretação Geral:**
            *   **< 0:** O fundo rende menos que a taxa livre de risco (CDI), ou tem retorno negativo, considerando apenas as perdas. Ruim.
            *   **0 - 1.0:** Retorno ajustado ao risco de queda subótimo.
            *   **1.0 - 2.0:** Retorno ajustado ao risco de queda razoável.
            *   **> 2.0:** Bom retorno ajustado ao risco de queda.
            """)
        with col_info_ratio:
            st.metric("Information Ratio", f"{information_ratio:.2f}" if not pd.isna(information_ratio) else "N/A")
            st.info("""
            **O que é:** Mede a capacidade do gestor de gerar retornos excedentes (alfa) em relação a um benchmark (CDI), ajustado pelo risco (tracking error).
            **Interpretação Geral:**
            *   **< 0:** O gestor está adicionando valor negativo em relação ao benchmark.
            *   **0 - 0.4:** Desempenho razoável em relação ao benchmark.
            *   **0.4 - 0.6:** Bom desempenho em relação ao benchmark.
            *   **> 0.6:** Excelente desempenho em relação ao benchmark, indicando alta habilidade do gestor.
            """)

        st.markdown("---")
        st.markdown("#### RISCO MEDIDO PELO DRAWDOWN")
        col_dd1, col_dd2 = st.columns(2)
        with col_dd1:
            st.metric("Calmar Ratio", f"{calmar_ratio:.2f}" if not pd.isna(calmar_ratio) else "N/A")
            st.info("""
            **O que é:** Compara o retorno anualizado com o maior drawdown (perda máxima do pico ao vale). Quanto maior, melhor o retorno em relação à pior queda.
            **Interpretação Geral:**
            *   **< 0:** O fundo tem retorno negativo ou o retorno não compensa o drawdown. Ruim.
            *   **0 - 0.5:** Relação retorno/drawdown subótima.
            *   **0.5 - 1.0:** Relação retorno/drawdown razoável.
            *   **> 1.0:** Boa relação retorno/drawdown.
            """)
        with col_dd2:
            st.metric("Sterling Ratio", f"{sterling_ratio:.2f}" if not pd.isna(sterling_ratio) else "N/A")
            st.info("""
            **O que é:** Geralmente, compara o retorno anualizado com a **média dos piores drawdowns (nesta análise, os 3 piores)**. Um valor mais alto é preferível, indicando que o fundo gera bons retornos em relação às suas quedas mais severas.
            **Interpretação Geral:**
            *   **< 0:** O fundo tem retorno negativo ou o retorno não compensa a média dos piores drawdowns. Ruim.
            *   **0 - 0.5:** Relação retorno/média dos piores drawdowns subótima.
            *   **0.5 - 1.0:** Relação retorno/média dos piores drawdowns razoável.
            *   **> 1.0:** Boa relação retorno/média dos piores drawdowns.
            """)

        col_martin, col_ulcer = st.columns(2)
        with col_martin:
            st.metric("Martin Ratio", f"{martin_ratio:.2f}" if not pd.isna(martin_ratio) else "N/A")
            st.info("""
            **O que é:** Compara o retorno excedente com o Ulcer Index. É uma medida de retorno ajustado ao risco que penaliza fundos com drawdowns mais profundos e duradouros.
            **Interpretação Geral:**
            *   **< 0:** O fundo tem retorno negativo ou o retorno não compensa o risco medido pelo Ulcer Index. Ruim.
            *   **0 - 1.0:** Relação retorno/Ulcer Index subótima.
            *   **1.0 - 2.0:** Relação retorno/Ulcer Index razoável.
            *   **> 2.0:** Boa relação retorno/Ulcer Index.
            """)
        with col_ulcer:
            st.metric("Ulcer Index", f"{ulcer_index:.2f}" if not pd.isna(ulcer_index) else "N/A")
            st.info("""
            **O que é:** Mede a profundidade e a duração dos drawdowns. Quanto menor, menos "dor" o investidor sentiu com as quedas do fundo.
            **Interpretação Geral:**
            *   **< 0.05:** Muito baixo, indica grande estabilidade.
            *   **0.05 - 0.15:** Baixo a moderado, comum em fundos mais conservadores.
            *   **0.15 - 0.30:** Moderado a alto, pode ser visto em fundos multimercado.
            *   **> 0.30:** Alto, indica fundos com drawdowns frequentes ou severos.
            """)

        st.markdown("---")
        st.markdown("#### OUTRAS MÉTRICAS DE RISCO")
        col_treynor, _ = st.columns(2)
        with col_treynor:
            st.metric("Treynor Ratio", "N/A")
            st.info("""
            **O que é:** Mede o retorno excedente por unidade de risco sistemático (Beta).
            **Por que não está calculável aqui:** O cálculo do Treynor Ratio exige o Beta do fundo, que mede a sensibilidade do fundo aos movimentos de um índice de mercado (como o Ibovespa). Como não temos dados de um benchmark de mercado no momento, não é possível calcular o Beta e, consequentemente, o Treynor Ratio.
            """)

        st.markdown("---")
        st.info("""
        **Observação Importante sobre as Interpretações:**
        Os intervalos de valores e suas interpretações são diretrizes gerais baseadas em literatura financeira e prática de mercado. A avaliação de um fundo deve sempre considerar seu tipo (ações, multimercado, renda fixa), seu objetivo, o cenário econômico e o perfil de risco do investidor. Um valor "bom" para um fundo de ações pode ser "ruim" para um fundo de renda fixa, por exemplo.
        """)

    else:
        st.warning("⚠️ Não há dados suficientes (mínimo de 1 ano de dados) ou o CDI não está selecionado para calcular as Métricas de Risco-Retorno.")

    st.subheader("📊 VaR (Value at Risk) e ES (Expected Shortfall)")

    if len(df['Retorno_Diario'].dropna()) >= 21: # Mínimo de 21 dias para calcular VaR/ES de 1 mês
        # Calcular VaR e ES para 1 mês (21 dias úteis)
        retornos_21d = (1 + df['Retorno_Diario']).rolling(window=21).apply(np.prod, raw=True) - 1
        df_plot_var = pd.DataFrame({'DT_COMPTC': df['DT_COMPTC'], 'Retorno_21d': retornos_21d}).dropna()

        if not df_plot_var.empty:
            # VaR 95% e 99%
            VaR_95 = df_plot_var['Retorno_21d'].quantile(0.05)
            VaR_99 = df_plot_var['Retorno_21d'].quantile(0.01)

            # ES 95% e 99%
            ES_95 = df_plot_var['Retorno_21d'][df_plot_var['Retorno_21d'] <= VaR_95].mean()
            ES_99 = df_plot_var['Retorno_21d'][df_plot_var['Retorno_21d'] <= VaR_99].mean()

            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=df_plot_var['DT_COMPTC'],
                y=df_plot_var['Retorno_21d'] * 100,
                mode='lines',
                name='Rentabilidade móvel (1m)',
                line=dict(color=color_primary, width=2),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade 21d: %{y:.2f}%<extra></extra>'
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[VaR_95 * 100, VaR_95 * 100],
                mode='lines',
                name='VaR 95%',
                line=dict(dash='dot', color='orange', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[VaR_99 * 100, VaR_99 * 100],
                mode='lines',
                name='VaR 99%',
                line=dict(dash='dot', color='red', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[ES_95 * 100, ES_95 * 100],
                mode='lines',
                name='ES 95%',
                line=dict(dash='dash', color='orange', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[ES_99 * 100, ES_99 * 100],
                mode='lines',
                name='ES 99%',
                line=dict(dash='dash', color='red', width=2)
            ))

            fig5.update_layout(
                xaxis_title="Data",
                yaxis_title="Rentabilidade (%)",
                template="plotly_white",
                hovermode="x unified",
                height=600,
                font=dict(family="Inter, sans-serif")
            )
            # Ajusta o range do eixo X para os dados de df_plot_var
            fig5 = add_watermark_and_style(fig5, logo_base64, x_range=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig5, use_container_width=True)

            st.info(f"""
            **Este gráfico mostra que, em um período de 1 mês:**

            • Há **99%** de confiança de que o fundo não cairá mais do que **{fmt_pct_port(VaR_99)} (VaR)**,
            e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_99)} (ES)**.

            • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(VaR_95)} (VaR)**,
            e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_95)} (ES)**.
            """)
        else:
            st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias de retorno).")

    with tab3:
        st.subheader("💰 Patrimônio e Captação Líquida")

        fig6 = go.Figure([
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Soma_Acumulada'],
                mode='lines',
                name='Captação Líquida',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Captação Líquida Acumulada: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['Soma_Acumulada']]
            ),
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_PATRIM_LIQ'],
                mode='lines',
                name='Patrimônio Líquido',
                line=dict(color=color_secondary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Líquido: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['VL_PATRIM_LIQ']]
            )
        ])

        fig6.update_layout(
            xaxis_title="Data",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        # Ajusta o range do eixo X para os dados de df
        fig6 = add_watermark_and_style(fig6, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("📊 Captação Líquida Mensal")

        df_monthly = df.groupby(pd.Grouper(key='DT_COMPTC', freq='M'))[['CAPTC_DIA', 'RESG_DIA']].sum()
        df_monthly['Captacao_Liquida'] = df_monthly['CAPTC_DIA'] - df_monthly['RESG_DIA']

        colors = [color_primary if x >= 0 else color_danger for x in df_monthly['Captacao_Liquida']]

        fig7 = go.Figure([
            go.Bar(
                x=df_monthly.index,
                y=df_monthly['Captacao_Liquida'],
                name='Captação Líquida Mensal',
                marker_color=colors,
                hovertemplate='Mês: %{x|%b/%Y}<br>Captação Líquida: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df_monthly['Captacao_Liquida']]
            )
        ])

        fig7.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        # Ajusta o range do eixo X para os dados de df_monthly
        if not df_monthly.empty:
            fig7 = add_watermark_and_style(fig7, logo_base64, x_range=[df_monthly.index.min(), df_monthly.index.max()], x_autorange=False)
        else:
            fig7 = add_watermark_and_style(fig7, logo_base64) # Sem range específico se não houver dados
        st.plotly_chart(fig7, use_container_width=True)

    with tab4:
        st.subheader("👥 Patrimônio Médio e Nº de Cotistas")

        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Patrimonio_Liq_Medio'],
            mode='lines',
            name='Patrimônio Médio por Cotista',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Médio: %{customdata}<extra></extra>',
            customdata=[format_brl(v) for v in df['Patrimonio_Liq_Medio']]
        ))
        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['NR_COTST'],
            mode='lines',
            name='Número de Cotistas',
            line=dict(color=color_secondary, width=2.5),
            yaxis='y2',
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Nº de Cotistas: %{y}<extra></extra>'
        ))

        fig8.update_layout(
            xaxis_title="Data",
            yaxis=dict(title="Patrimônio Médio por Cotista (R$)"),
            yaxis2=dict(title="Número de Cotistas", overlaying="y", side="right"),
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        # Ajusta o range do eixo X para os dados de df
        fig8 = add_watermark_and_style(fig8, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig8, use_container_width=True)

    with tab5:
        st.subheader("🎯 Retornos em Janelas Móveis")

        janelas = {
            "12 meses (252 dias)": 252,
            "24 meses (504 dias)": 504,
            "36 meses (756 dias)": 756,
            "48 meses (1008 dias)": 1008,
            "60 meses (1260 dias)": 1260
        }

        df_returns = df.copy()
        for nome, dias in janelas.items():
            # Certifica-se de que há dados suficientes para a janela
            if len(df_returns) > dias:
                df_returns[f'FUNDO_{nome}'] = df_returns['VL_QUOTA'] / df_returns['VL_QUOTA'].shift(dias) - 1
                if tem_cdi:
                    df_returns[f'CDI_{nome}'] = df_returns['CDI_COTA'] / df_returns['CDI_COTA'].shift(dias) - 1
            else:
                df_returns[f'FUNDO_{nome}'] = np.nan
                if tem_cdi:
                    df_returns[f'CDI_{nome}'] = np.nan

        janela_selecionada = st.selectbox("Selecione o período:", list(janelas.keys()))

        if not df_returns[f'FUNDO_{janela_selecionada}'].dropna().empty:
            fig9 = go.Figure()

            # Retorno do Fundo
            fig9.add_trace(go.Scatter(
                x=df_returns['DT_COMPTC'],
                y=df_returns[f'FUNDO_{janela_selecionada}'],
                mode='lines',
                name=f"Retorno do Fundo — {janela_selecionada}",
                line=dict(width=2.5, color=color_primary),
                fill='tozeroy',
                fillcolor='rgba(26, 95, 63, 0.1)',
                hovertemplate="<b>Retorno do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
            ))

            # Retorno do CDI (se disponível)
            if tem_cdi:
                fig9.add_trace(go.Scatter(
                    x=df_returns['DT_COMPTC'],
                    y=df_returns[f'CDI_{janela_selecionada}'],
                    mode='lines',
                    name=f"Retorno do CDI — {janela_selecionada}",
                    line=dict(width=2.5, color=color_cdi),
                    hovertemplate="<b>Retorno do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                ))

            fig9.update_layout(
                xaxis_title="Data",
                yaxis_title=f"Retorno {janela_selecionada}",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                yaxis=dict(tickformat=".2%"),
                font=dict(family="Inter, sans-serif"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            # Ajusta o range do eixo X para os dados de df_returns
            df_plot_returns = df_returns.dropna(subset=[f'FUNDO_{janela_selecionada}']).copy()
            if not df_plot_returns.empty:
                fig9 = add_watermark_and_style(fig9, logo_base64, x_range=[df_plot_returns['DT_COMPTC'].min(), df_plot_returns['DT_COMPTC'].max()], x_autorange=False)
            else:
                fig9 = add_watermark_and_style(fig9, logo_base64) # Sem range específico se não houver dados
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada}.")

        # GRÁFICO: Consistência em Janelas Móveis
        st.subheader("📈 Consistência em Janelas Móveis")

        if tem_cdi:
            consistency_data = []
            for nome, dias in janelas.items():
                fund_col = f'FUNDO_{nome}'
                cdi_col = f'CDI_{nome}'

                if fund_col in df_returns.columns and cdi_col in df_returns.columns:
                    temp_df = df_returns[[fund_col, cdi_col]].dropna()

                    if not temp_df.empty:
                        outperformed_count = (temp_df[fund_col] > temp_df[cdi_col]).sum()
                        total_comparisons = len(temp_df)
                        consistency_percentage = (outperformed_count / total_comparisons) * 100 if total_comparisons > 0 else 0
                        consistency_data.append({'Janela': nome.split(' ')[0], 'Consistencia': consistency_percentage})
                    else:
                        consistency_data.append({'Janela': nome.split(' ')[0], 'Consistencia': np.nan})
                else:
                    consistency_data.append({'Janela': nome.split(' ')[0], 'Consistencia': np.nan})

            df_consistency = pd.DataFrame(consistency_data)
            df_consistency.dropna(subset=['Consistencia'], inplace=True)

            if not df_consistency.empty:
                fig_consistency = go.Figure()
                fig_consistency.add_trace(go.Bar(
                    x=df_consistency['Janela'],
                    y=df_consistency['Consistencia'],
                    marker_color=color_primary,
                    # Adiciona o texto nas barras
                    text=df_consistency['Consistencia'].apply(lambda x: f'{x:.2f}%'),
                    textposition='outside', # Posição do texto fora da barra
                    textfont=dict(color='black', size=12), # Cor e tamanho da fonte do texto
                    hovertemplate='<b>Janela:</b> %{x}<br><b>Consistência:</b> %{y:.2f}%<extra></extra>'
                ))

                fig_consistency.update_layout(
                    xaxis_title="Janela (meses)",
                    yaxis_title="Percentual de Superação do CDI (%)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Inter, sans-serif"),
                    yaxis=dict(range=[0, 110], ticksuffix="%") # Aumenta o range superior para dar mais espaço ao texto
                )
                fig_consistency = add_watermark_and_style(fig_consistency, logo_base64, x_autorange=True)
                st.plotly_chart(fig_consistency, use_container_width=True)
            else:
                st.warning("⚠️ Não há dados suficientes para calcular a Consistência em Janelas Móveis.")
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar a Consistência em Janelas Móveis.")

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("💡 Verifique se o CNPJ está correto e se há dados disponíveis para o período selecionado.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 2rem 0;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        <strong>Dashboard desenvolvido com Streamlit e Plotly</strong>
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem;'>
        Análise de Fundos de Investimentos • Copaíba Invest • 2025
    </p>
</div>
""", unsafe_allow_html=True)
