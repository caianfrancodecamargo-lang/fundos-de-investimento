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

# NOVA FUNÇÃO: Converte data brasileira (DD/MM/AAAA) para string YYYYMMDD (para CVM API)
def parse_date_input_to_yyyymmdd_str(data_str):
    if not data_str:
        return None
    data_limpa = re.sub(r'\D', '', data_str)
    if len(data_limpa) == 8:
        try:
            dia = data_limpa[:2]
            mes = data_limpa[2:4]
            ano = data_limpa[4:]
            # Valida o formato DD/MM/AAAA
            datetime.strptime(f"{dia}/{mes}/{ano}", '%d/%m/%Y')
            return f"{ano}{mes}{dia}" # Retorna YYYYMMDD
        except ValueError:
            return None
    return None

# NOVA FUNÇÃO: Converte data brasileira (DD/MM/AAAA) para objeto datetime (para BCB SGS)
def parse_date_input_to_datetime_obj(data_str):
    if not data_str:
        return None
    data_limpa = re.sub(r'\D', '', data_str)
    if len(data_limpa) == 8:
        try:
            dia = data_limpa[:2]
            mes = data_limpa[2:4]
            ano = data_limpa[4:]
            return datetime.strptime(f"{dia}/{mes}/{ano}", '%d/%m/%Y')
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

        # Calcular o produto acumulado a partir do primeiro dia do período
        cdi_diario['VL_CDI_acum'] = cdi_diario['CDI_fator_diario'].cumprod()

        # NORMALIZAR para que o primeiro valor da série acumulada seja EXATAMENTE 1.0
        if not cdi_diario.empty:
            primeiro_valor_acum = cdi_diario['VL_CDI_acum'].iloc[0]
            cdi_diario['VL_CDI_normalizado'] = cdi_diario['VL_CDI_acum'] / primeiro_valor_acum
        else:
            cdi_diario['VL_CDI_normalizado'] = pd.Series(dtype='float64') # Garante que a coluna exista

        return cdi_diario

    except Exception as e:
        st.error(f"❌ Erro ao obter dados do CDI: {str(e)}")
        return pd.DataFrame()

# Sidebar com logo (SEM título "Configurações")
if logo_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" alt="Copaíba Invest"></div>',
        unsafe_allow_html=True
    )

# Input de CNPJ
cnpj_input = st.sidebar.text_input(
    "CNPJ do Fundo",
    value="",
    placeholder="00.000.000/0000-00",
    help="Digite o CNPJ com ou sem formatação"
)

# Inputs de data
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

# Opção para mostrar CDI
st.sidebar.markdown("#### 📈 Indicadores de Comparação")
mostrar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)

st.sidebar.markdown("---")

# Processar inputs
cnpj_limpo = limpar_cnpj(cnpj_input)
data_inicial_cvm_str = parse_date_input_to_yyyymmdd_str(data_inicial_input) # String YYYYMMDD para CVM
data_final_cvm_str = parse_date_input_to_yyyymmdd_str(data_final_input)     # String YYYYMMDD para CVM

start_date_dt = parse_date_input_to_datetime_obj(data_inicial_input) # Objeto datetime para BCB SGS
end_date_dt = parse_date_input_to_datetime_obj(data_final_input)     # Objeto datetime para BCB SGS

# Validação
cnpj_valido = False
datas_validas = False

if cnpj_input:
    if len(cnpj_limpo) != 14:
        st.sidebar.error("❌ CNPJ deve conter 14 dígitos")
    else:
        cnpj_valido = True

if data_inicial_input and data_final_input:
    if start_date_dt and end_date_dt: # Usar os objetos datetime para validação
        if start_date_dt <= end_date_dt:
            datas_validas = True
        else:
            st.sidebar.error("❌ Data inicial deve ser menor ou igual à data final.")
    else:
        st.sidebar.error("❌ Formato de data inválido. Use DD/MM/AAAA.")
else:
    st.sidebar.info("💡 Por favor, insira as datas inicial e final.")

# Cores
color_primary = "#1a5f3f"
color_secondary = "#2d8659"
color_accent = "#f0b429"
color_cdi = "#8ba888"
color_danger = "#dc3545"

# Formatação para BRL
def format_brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Formatação para porcentagem
def fmt_pct(value):
    return f"{value:.2%}"

def fmt_pct_port(value):
    return f"{value:.2%}".replace(".", ",")

# Lógica principal do dashboard
if cnpj_valido and datas_validas:
    try:
        # Obter dados do CDI
        if mostrar_cdi:
            cdi_df = obter_dados_cdi_real(start_date_dt, end_date_dt) # Passa objetos datetime
            if cdi_df.empty:
                st.warning("⚠️ Não foi possível obter dados do CDI para o período selecionado.")
                tem_cdi = False
            else:
                tem_cdi = True
        else:
            tem_cdi = False
            cdi_df = pd.DataFrame() # Garante que cdi_df sempre exista

        # Obter dados do fundo
        df = obter_dados_fundo(cnpj_limpo, data_inicial_cvm_str, data_final_cvm_str) # Passa strings YYYYMMDD

        if df.empty:
            st.warning("⚠️ Não foi possível obter dados do fundo para o CNPJ e período selecionados.")
            st.stop()

        # Merge com CDI se disponível
        if tem_cdi and not cdi_df.empty:
            df = pd.merge(df, cdi_df[['DT_COMPTC', 'VL_CDI_normalizado']], on='DT_COMPTC', how='left')
            df['CDI_COTA'] = df['VL_CDI_normalizado']
            # Preencher NaNs no CDI_COTA com o valor anterior para manter a série contínua
            df['CDI_COTA'] = df['CDI_COTA'].ffill()
            # Se ainda houver NaN no início, preencher com 1.0 (valor inicial normalizado)
            df['CDI_COTA'] = df['CDI_COTA'].bfill().fillna(1.0)
        elif tem_cdi and cdi_df.empty: # Se a flag tem_cdi é True mas o df está vazio
            st.warning("⚠️ Dados do CDI não puderam ser carregados. Análises comparativas serão limitadas.")
            tem_cdi = False

        # Cálculos adicionais
        df['Retorno_Diario_Fundo'] = df['VL_QUOTA'].pct_change()
        df['Drawdown'] = (df['VL_QUOTA'] / df['VL_QUOTA'].cummax() - 1) * 100 # Em porcentagem

        # Calcular Captação Líquida Acumulada
        df['Soma_Acumulada'] = (df['CAPTC_DIA'] - df['RESG_DIA']).cumsum()

        # Calcular Patrimônio Líquido Médio por Cotista
        df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']
        df['Patrimonio_Liq_Medio'] = df['Patrimonio_Liq_Medio'].replace([np.inf, -np.inf], np.nan).fillna(0) # Trata divisão por zero cotistas

        # Número de dias úteis no ano para anualização
        trading_days_in_year = 252

        # Calcular retornos diários
        df['Retorno_Diario_Fundo'] = df['VL_QUOTA'].pct_change()
        if tem_cdi:
            df['Retorno_Diario_CDI'] = df['CDI_COTA'].pct_change()

        # Calcular o excesso de retorno anualizado (rolling 252 dias)
        if tem_cdi and len(df) >= trading_days_in_year:
            # Retorno anualizado móvel do fundo
            df['ROLLING_ANN_RETURN_FUND'] = (1 + df['Retorno_Diario_Fundo']).rolling(window=trading_days_in_year).apply(lambda x: x.prod() - 1, raw=False)
            # Retorno anualizado móvel do CDI
            df['ROLLING_ANN_RETURN_CDI'] = (1 + df['Retorno_Diario_CDI']).rolling(window=trading_days_in_year).apply(lambda x: x.prod() - 1, raw=False)
            # Excesso de retorno anualizado móvel
            df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'] = (df['ROLLING_ANN_RETURN_FUND'] - df['ROLLING_ANN_RETURN_CDI']) * 100
        else:
            df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'] = np.nan # Garante que a coluna exista

        # Título do Dashboard
        st.title(f"Dashboard de Análise de Fundos de Investimentos")
        st.subheader(f"Fundo: {df['DENOM_SOCIAL'].iloc[-1]} (CNPJ: {cnpj_input})")

        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Visão Geral",
            "📉 Risco",
            "💰 Patrimônio e Captação",
            "👥 Cotistas",
            "🎯 Janelas Móveis"
        ])

        with tab1:
            st.subheader("📈 Performance Histórica")

            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_QUOTA'] / df['VL_QUOTA'].iloc[0],
                mode='lines',
                name='Fundo',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Valor da Cota: %{customdata}<extra></extra>',
                customdata=[f"{v:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in df['VL_QUOTA']]
            ))

            if tem_cdi:
                fig1.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['CDI_COTA'],
                    mode='lines',
                    name='CDI',
                    line=dict(color=color_cdi, width=2.5),
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>CDI Acumulado: %{customdata}<extra></extra>',
                    customdata=[f"{v:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in df['CDI_COTA']]
                ))

            fig1.update_layout(
                xaxis_title="Data",
                yaxis_title="Performance Relativa (Base 1)",
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

            # Métricas de Retorno
            st.subheader("Sumário de Retornos")
            col_ret1, col_ret2, col_ret3 = st.columns(3)

            # Cálculo do Retorno Total
            total_return_fund = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1
            with col_ret1:
                st.metric("Retorno Total do Fundo", fmt_pct(total_return_fund))

            # Cálculo do CAGR (Retorno Anualizado)
            if not df.empty and len(df) > 1:
                num_years = (df['DT_COMPTC'].iloc[-1] - df['DT_COMPTC'].iloc[0]).days / trading_days_in_year
                if num_years > 0:
                    cagr_fund = ((1 + total_return_fund) ** (1 / num_years)) - 1
                else:
                    cagr_fund = 0
            else:
                cagr_fund = 0

            with col_ret2:
                st.metric("CAGR (Anualizado)", fmt_pct(cagr_fund))

            if tem_cdi:
                total_return_cdi = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0]) - 1
                num_years_cdi = (df['DT_COMPTC'].iloc[-1] - df['DT_COMPTC'].iloc[0]).days / trading_days_in_year
                if num_years_cdi > 0:
                    cagr_cdi = ((1 + total_return_cdi) ** (1 / num_years_cdi)) - 1
                else:
                    cagr_cdi = 0
                with col_ret3:
                    st.metric("CAGR do CDI (Anualizado)", fmt_pct(cagr_cdi))
            else:
                with col_ret3:
                    st.info("Selecione o CDI para ver o CAGR comparativo.")

            st.subheader("📊 Excesso de Retorno Anualizado (Rolling 12 meses)")
            if tem_cdi and len(df) >= trading_days_in_year:
                fig_excess_return = go.Figure()
                fig_excess_return.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'],
                    mode='lines',
                    name='Excesso de Retorno Anualizado',
                    line=dict(color=color_primary, width=2.5),
                    fill='tozeroy',
                    fillcolor='rgba(26, 95, 63, 0.1)',
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>Excesso de Retorno: %{y:.2f}%<extra></extra>'
                ))
                fig_excess_return.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Excesso de Retorno (% a.a.)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Inter, sans-serif")
                )
                fig_excess_return = add_watermark_and_style(fig_excess_return, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
                st.plotly_chart(fig_excess_return, use_container_width=True)
            elif tem_cdi and len(df) < trading_days_in_year:
                st.warning(f"⚠️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado (mínimo de {trading_days_in_year} dias de dados).")
            else:
                st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar o Excesso de Retorno Anualizado.")


            st.subheader("📉 Drawdown Histórico")
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Drawdown'],
                mode='lines',
                name='Drawdown',
                line=dict(color=color_danger, width=2.5),
                fill='tozeroy',
                fillcolor='rgba(220, 53, 69, 0.1)',
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ))
            fig2.update_layout(
                xaxis_title="Data",
                yaxis_title="Drawdown (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig2, use_container_width=True)

            # Métricas de Drawdown
            st.subheader("Sumário de Drawdowns")
            col_dd1, col_dd2 = st.columns(2)

            max_drawdown_value = df['Drawdown'].min() if not df['Drawdown'].empty else 0
            with col_dd1:
                st.metric("Max Drawdown", fmt_pct(max_drawdown_value / 100))

            # Cálculo do tempo de recuperação (se houver drawdown)
            if max_drawdown_value < 0:
                peak_date = df['DT_COMPTC'][df['VL_QUOTA'].idxmax()]
                trough_date = df['DT_COMPTC'][df['Drawdown'].idxmin()]
                recovery_df = df[df['DT_COMPTC'] >= trough_date]
                if not recovery_df.empty:
                    recovery_date_idx = (recovery_df['VL_QUOTA'] >= df['VL_QUOTA'].max()).idxmax()
                    if recovery_date_idx:
                        recovery_date = recovery_df['DT_COMPTC'][recovery_date_idx]
                        recovery_time = (recovery_date - trough_date).days
                        with col_dd2:
                            st.metric("Tempo de Recuperação (dias)", f"{recovery_time} dias")
                    else:
                        with col_dd2:
                            st.metric("Tempo de Recuperação (dias)", "Em andamento")
                else:
                    with col_dd2:
                        st.metric("Tempo de Recuperação (dias)", "N/A")
            else:
                with col_dd2:
                    st.metric("Tempo de Recuperação (dias)", "N/A")

        with tab2:
            st.subheader("📊 Métricas de Risco-Retorno")

            if tem_cdi and not df.empty and len(df) >= trading_days_in_year:
                # Retornos anualizados para o período total
                total_return_fund = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1
                total_return_cdi = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0]) - 1
                num_years_total = (df['DT_COMPTC'].iloc[-1] - df['DT_COMPTC'].iloc[0]).days / trading_days_in_year

                if num_years_total > 0:
                    annualized_return_fund = ((1 + total_return_fund) ** (1 / num_years_total)) - 1
                    annualized_return_cdi = ((1 + total_return_cdi) ** (1 / num_years_total)) - 1
                else:
                    annualized_return_fund = 0
                    annualized_return_cdi = 0

                # Volatilidade Anualizada
                annualized_fund_volatility = df['Retorno_Diario_Fundo'].std() * np.sqrt(trading_days_in_year) if not df['Retorno_Diario_Fundo'].empty else 0
                annualized_cdi_volatility = df['Retorno_Diario_CDI'].std() * np.sqrt(trading_days_in_year) if not df['Retorno_Diario_CDI'].empty else 0

                # Max Drawdown (já calculado em %)
                max_drawdown_value_abs = abs(max_drawdown_value / 100) # Converte para decimal positivo

                # Volatilidade de Baixa (Downside Volatility)
                negative_returns = df['Retorno_Diario_Fundo'][df['Retorno_Diario_Fundo'] < 0]
                annualized_downside_volatility = negative_returns.std() * np.sqrt(trading_days_in_year) if not negative_returns.empty else 0

                # Ulcer Index
                if not df['Drawdown'].empty:
                    # Drawdown já está em % negativo, precisamos do valor absoluto para o cálculo
                    drawdowns_for_ulcer = df['Drawdown'].apply(lambda x: abs(x / 100) if x < 0 else 0)
                    squared_drawdowns = drawdowns_for_ulcer ** 2
                    ulcer_index = np.sqrt(squared_drawdowns.mean()) if not squared_drawdowns.empty else np.nan
                else:
                    ulcer_index = np.nan

                # Tracking Error
                if tem_cdi and not df['Retorno_Diario_CDI'].empty:
                    excess_daily_returns = df['Retorno_Diario_Fundo'] - df['Retorno_Diario_CDI']
                    tracking_error = excess_daily_returns.std() * np.sqrt(trading_days_in_year) if not excess_daily_returns.empty else 0
                else:
                    tracking_error = 0

                # Cálculo dos 3 piores drawdowns para Sterling Ratio
                negative_drawdowns = df['Drawdown'][df['Drawdown'] < 0]
                if not negative_drawdowns.empty:
                    # Pega os 3 menores (mais negativos) valores de drawdown e calcula a média
                    worst_drawdowns_series = negative_drawdowns.nsmallest(3)
                    avg_worst_drawdowns = abs(worst_drawdowns_series.mean() / 100) # Converte para decimal positivo
                else:
                    avg_worst_drawdowns = np.nan

                # --- Cálculo dos Ratios ---
                # Sharpe Ratio
                if annualized_fund_volatility > 0:
                    sharpe_ratio = (annualized_return_fund - annualized_return_cdi) / annualized_fund_volatility
                else:
                    sharpe_ratio = np.nan

                # Sortino Ratio
                if annualized_downside_volatility > 0:
                    sortino_ratio = (annualized_return_fund - annualized_return_cdi) / annualized_downside_volatility
                else:
                    sortino_ratio = np.nan

                # Calmar Ratio
                if max_drawdown_value_abs > 0:
                    calmar_ratio = (annualized_return_fund - annualized_return_cdi) / max_drawdown_value_abs
                else:
                    calmar_ratio = np.nan

                # Sterling Ratio (usando a média dos 3 piores drawdowns)
                if avg_worst_drawdowns > 0:
                    sterling_ratio = (annualized_return_fund - annualized_return_cdi) / avg_worst_drawdowns
                else:
                    sterling_ratio = np.nan

                # Martin Ratio
                if ulcer_index > 0:
                    martin_ratio = (annualized_return_fund - annualized_return_cdi) / ulcer_index
                else:
                    martin_ratio = np.nan

                # Information Ratio
                if tracking_error > 0:
                    information_ratio = (annualized_return_fund - annualized_return_cdi) / tracking_error
                else:
                    information_ratio = np.nan

                # --- Exibição dos Cards ---
                st.markdown("#### Risco Medido pela Volatilidade")
                col_vol1, col_vol2, col_vol3 = st.columns(3)

                with col_vol1:
                    st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if not np.isnan(sharpe_ratio) else "N/A")
                    st.info("""
                        **O que é:** Mede o retorno excedente por unidade de risco total (volatilidade).
                        **Interpretação Geral:**
                        *   **< 0:** Retorno inferior à taxa livre de risco. Subótimo.
                        *   **0 - 1:** Retorno excedente baixo para o risco assumido. Pode ser melhor.
                        *   **1 - 2:** Bom retorno para o risco. Aceitável.
                        *   **> 2:** Muito bom retorno para o risco. Excelente.
                    """)
                with col_vol2:
                    st.metric("Sortino Ratio", f"{sortino_ratio:.2f}" if not np.isnan(sortino_ratio) else "N/A")
                    st.info("""
                        **O que é:** Similar ao Sharpe, mas foca apenas no risco de queda (volatilidade de retornos negativos).
                        **Interpretação Geral:**
                        *   **< 0:** Retorno inferior à taxa livre de risco, considerando apenas o risco de queda. Subótimo.
                        *   **0 - 1:** Retorno excedente baixo para o risco de queda. Pode ser melhor.
                        *   **1 - 2:** Bom retorno para o risco de queda. Aceitável.
                        *   **> 2:** Muito bom retorno para o risco de queda. Excelente.
                    """)
                with col_vol3:
                    st.metric("Information Ratio", f"{information_ratio:.2f}" if not np.isnan(information_ratio) else "N/A")
                    st.info("""
                        **O que é:** Mede a capacidade do gestor de gerar retornos acima de um benchmark (CDI) por unidade de risco ativo (Tracking Error).
                        **Interpretação Geral:**
                        *   **< 0:** O fundo está performando pior que o benchmark. Fraco.
                        *   **0 - 0.5:** O fundo está gerando algum excesso de retorno, mas com volatilidade significativa. Mediano.
                        *   **0.5 - 1.0:** Boa performance em relação ao benchmark. Bom.
                        *   **> 1.0:** Excelente performance em relação ao benchmark. Muito bom.
                    """)

                st.markdown("#### Risco Medido pelo Drawdown")
                col_dd_ratio1, col_dd_ratio2, col_dd_ratio3 = st.columns(3)

                with col_dd_ratio1:
                    st.metric("Calmar Ratio", f"{calmar_ratio:.2f}" if not np.isnan(calmar_ratio) else "N/A")
                    st.info("""
                        **O que é:** Compara o retorno anualizado com o maior drawdown (perda máxima do pico ao vale).
                        **Interpretação Geral:**
                        *   **< 0:** O fundo teve um retorno anualizado negativo ou um drawdown muito grande em relação ao retorno. Subótimo.
                        *   **0 - 0.5:** Retorno baixo em relação ao maior drawdown. Fraco.
                        *   **0.5 - 1.0:** Retorno razoável para o maior drawdown. Aceitável.
                        *   **> 1.0:** Bom retorno em relação ao maior drawdown. Excelente.
                    """)
                with col_dd_ratio2:
                    st.metric("Sterling Ratio", f"{sterling_ratio:.2f}" if not np.isnan(sterling_ratio) else "N/A")
                    st.info("""
                        **O que é:** Geralmente, compara o retorno anualizado com a **média dos piores drawdowns (nesta análise, a média dos 3 piores)**. Um valor mais alto é preferível.
                        **Interpretação Geral:**
                        *   **< 0:** Retorno anualizado negativo ou média dos piores drawdowns muito grande. Subótimo.
                        *   **0 - 0.5:** Retorno baixo em relação à média dos piores drawdowns. Fraco.
                        *   **0.5 - 1.0:** Retorno razoável para a média dos piores drawdowns. Aceitável.
                        *   **> 1.0:** Bom retorno em relação à média dos piores drawdowns. Excelente.
                    """)
                with col_dd_ratio3:
                    st.metric("Martin Ratio", f"{martin_ratio:.2f}" if not np.isnan(martin_ratio) else "N/A")
                    st.info("""
                        **O que é:** Compara o retorno excedente com o Ulcer Index, que mede a profundidade e duração dos drawdowns.
                        **Interpretação Geral:**
                        *   **< 0:** Retorno inferior à taxa livre de risco ou Ulcer Index muito alto. Subótimo.
                        *   **0 - 0.5:** Retorno baixo em relação à "dor" dos drawdowns. Fraco.
                        *   **0.5 - 1.0:** Retorno razoável para a "dor" dos drawdowns. Aceitável.
                        *   **> 1.0:** Bom retorno em relação à "dor" dos drawdowns. Excelente.
                    """)

                st.markdown("#### Outras Métricas")
                col_other1, col_other2 = st.columns(2)

                with col_other1:
                    st.metric("Ulcer Index", f"{ulcer_index:.2f}" if not np.isnan(ulcer_index) else "N/A")
                    st.info("""
                        **O que é:** Mede a "dor" ou severidade dos drawdowns, considerando tanto a profundidade quanto a duração. Quanto menor, melhor.
                        **Interpretação Geral:**
                        *   **> 1.0:** Indica drawdowns frequentes e/ou profundos. Alto risco de "dor".
                        *   **0.5 - 1.0:** Nível moderado de "dor" de drawdown.
                        *   **< 0.5:** Baixo nível de "dor" de drawdown. Bom.
                    """)
                with col_other2:
                    st.metric("Treynor Ratio", "Não Calculável")
                    st.info("""
                        **O que é:** Mede o retorno excedente por unidade de risco sistemático (Beta).
                        **Por que não é calculável aqui:** Requer o cálculo do Beta do fundo, que mede sua sensibilidade aos movimentos de um índice de mercado (ex: Ibovespa). Como não temos dados de um benchmark de mercado no momento, não é possível calcular o Beta e, consequentemente, o Treynor Ratio.
                    """)

                st.markdown("""
                ---
                **Observação Importante sobre as Interpretações:**
                Os intervalos e classificações acima são **diretrizes gerais** baseadas em práticas comuns do mercado financeiro e literaturas de investimento. A interpretação de qualquer métrica de risco-retorno deve sempre considerar o **contexto específico do fundo** (estratégia, classe de ativos, objetivo), as **condições de mercado** no período analisado e o **perfil de risco do investidor**. Não há um "número mágico" que sirva para todos os casos.
                """)

            elif not tem_cdi:
                st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar as Métricas de Risco-Retorno.")
            else:
                st.warning("⚠️ Não há dados suficientes para calcular as Métricas de Risco-Retorno (mínimo de 1 ano de dados).")

            st.subheader("📊 Volatilidade (Rolling 12 meses)")

            # Volatilidade (rolling)
            vol_window = 21 # 1 mês
            df['Volatilidade'] = df['Retorno_Diario_Fundo'].rolling(window=vol_window).std() * np.sqrt(trading_days_in_year) * 100
            vol_hist = df['Retorno_Diario_Fundo'].std() * np.sqrt(trading_days_in_year) * 100 # Volatilidade Histórica Anualizada

            fig4 = go.Figure()
            # Volatilidade do Fundo (APENAS - SEM CDI)
            fig4.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Volatilidade'],
                mode='lines',
                name=f'Volatilidade do Fundo ({vol_window} dias)',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='<b>Volatilidade do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
            ))

            fig4.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=[vol_hist] * len(df),
                mode='lines',
                line=dict(dash='dash', color=color_secondary, width=2),
                name=f'Vol. Histórica ({vol_hist:.2f}%)'
            ))

            fig4.update_layout(
                xaxis_title="Data",
                yaxis_title="Volatilidade (% a.a.)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            # Ajusta o range do eixo X para os dados de df
            fig4 = add_watermark_and_style(fig4, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig4, use_container_width=True)

            st.subheader("⚠️ Value at Risk (VaR) e Expected Shortfall (ES)")

            # Cálculo do VaR e ES
            if not df['Retorno_Diario_Fundo'].dropna().empty and len(df['Retorno_Diario_Fundo'].dropna()) >= vol_window:
                df_plot_var = df.copy()
                df_plot_var['Retorno_21d'] = (1 + df_plot_var['Retorno_Diario_Fundo']).rolling(window=vol_window).apply(lambda x: x.prod() - 1, raw=False)

                # Calcular VaR e ES para o período total
                daily_returns_series = df['Retorno_Diario_Fundo'].dropna()
                if not daily_returns_series.empty:
                    VaR_95 = daily_returns_series.quantile(0.05) * np.sqrt(vol_window) # VaR 1 mês
                    VaR_99 = daily_returns_series.quantile(0.01) * np.sqrt(vol_window) # VaR 1 mês

                    # Expected Shortfall (ES)
                    es_95_returns = daily_returns_series[daily_returns_series <= daily_returns_series.quantile(0.05)]
                    ES_95 = es_95_returns.mean() * np.sqrt(vol_window) if not es_95_returns.empty else np.nan

                    es_99_returns = daily_returns_series[daily_returns_series <= daily_returns_series.quantile(0.01)]
                    ES_99 = es_99_returns.mean() * np.sqrt(vol_window) if not es_99_returns.empty else np.nan
                else:
                    VaR_95, VaR_99, ES_95, ES_99 = np.nan, np.nan, np.nan, np.nan
            else:
                df_plot_var = pd.DataFrame() # Garante que df_plot_var esteja vazio
                VaR_95, VaR_99, ES_95, ES_99 = np.nan, np.nan, np.nan, np.nan


            if not df_plot_var.empty and not np.isnan(VaR_95):
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
                    fig9 = add_watermark_and_style(fig9, logo_base64)
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
