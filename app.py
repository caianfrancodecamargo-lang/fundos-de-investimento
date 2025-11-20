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

# Importar biblioteca para obter dados do Ibovespa
try:
    import yfinance as yf
    YF_DISPONIVEL = True
except ImportError:
    YF_DISPONIVEL = False
    st.warning("⚠️ Biblioteca 'yfinance' não encontrada. Instale com: pip install yfinance")

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

# CSS customizado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary-color: #1a5f3f;
        --secondary-color: #2d8659;
        --accent-color: #f0b429;
        --dark-bg: #0f1419;
        --light-bg: #f8f9fa;
        --text-dark: #1a1a1a;
        --text-light: #ffffff;
    }

    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar mais clara, esverdeada */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #88b89a 0%, #6da882 100%);
        padding: 1rem 0.8rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .sidebar-logo {
        text-align: center;
        padding: 0.5rem 0 0.8rem 0 !important;
        margin-bottom: 0.8rem !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }

    .sidebar-logo img {
        max-width: 240px !important;
        height: auto;
        filter: brightness(1.05);
    }

    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.8rem !important;
        margin-bottom: 0.2rem !important;
        margin-top: 0 !important;
    }

    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 0.4rem !important;
    }

    [data-testid="stSidebar"] h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
    }

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

    h1 {
        color: #1a5f3f;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
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
        padding: 1.0rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #6b9b7f;
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

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

    h2, h3 {
        color:1a5f3f;
        font-weight: 600;
    }

    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #1a5f3f;
    }

    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #1a5f3f, transparent);
    }

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

# Função para adicionar marca d'água e estilizar gráficos
def add_watermark_and_style(fig, logo_base64=None, x_range=None, x_autorange=True):
    if logo_base64:
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{logo_base64}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                sizex=1.75,
                sizey=1.75,
                xanchor="center",
                yanchor="middle",
                opacity=0.15,
                layer="below"
            )
        )

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
        ],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

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
        x_axes_update_params['autorange'] = False
    else:
        x_axes_update_params['autorange'] = x_autorange

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

# Obter dados CDI (real)
@st.cache_data
def obter_dados_cdi_real(data_inicio: datetime, data_fim: datetime):
    if not BCB_DISPONIVEL:
        return pd.DataFrame()
    try:
        cdi_diario = sgs.get({'cdi': 12}, start=data_inicio, end=data_fim)
        cdi_diario = cdi_diario.reset_index()
        cdi_diario = cdi_diario.rename(columns={'Date': 'DT_COMPTC'})
        cdi_diario['CDI_fator_diario'] = 1 + (cdi_diario['cdi'] / 100)
        cdi_diario['VL_CDI_acum'] = cdi_diario['CDI_fator_diario'].cumprod()
        if not cdi_diario.empty:
            primeiro_valor_acum = cdi_diario['VL_CDI_acum'].iloc[0]
            cdi_diario['VL_CDI_normalizado'] = cdi_diario['VL_CDI_acum'] / primeiro_valor_acum
        else:
            cdi_diario['VL_CDI_normalizado'] = pd.Series(dtype='float64')
        return cdi_diario
    except Exception as e:
        st.error(f"❌ Erro ao obter dados do CDI: {str(e)}")
        return pd.DataFrame()

# Obter dados Ibovespa
@st.cache_data
def obter_dados_ibov(data_inicio: datetime, data_fim: datetime):
    if not YF_DISPONIVEL:
        return pd.DataFrame()
    try:
        start_date = data_inicio
        end_date = data_fim + pd.DateOffset(days=1)
        df_ibovespa = yf.download('^BVSP', start=start_date, end=end_date, progress=False)
        if df_ibovespa.empty:
            return pd.DataFrame()
        if isinstance(df_ibovespa.columns, pd.MultiIndex):
            df_ibovespa.columns = ['_'.join(col).strip() for col in df_ibovespa.columns.values]
        df_ibovespa = df_ibovespa.reset_index()
        close_col_options = ['Close', 'Close_', 'Close_^BVSP']
        selected_close_col = None
 for col_option in close_col_options:
            if col_option in df_ibovespa.columns:
                selected_close_col = col_option
                break
        if selected_close_col is None:
            st.error("❌ Não foi possível encontrar a coluna de fechamento do Ibovespa.")
            return pd.DataFrame()
        df_ibovespa = df_ibovespa.rename(columns={'Date': 'DT_COMPTC', selected_close_col: 'IBOV'})
        df_ibovespa['DT_COMPTC'] = pd.to_datetime(df_ibovespa['DT_COMPTC'])
        df_ibovespa = df_ibovespa[['DT_COMPTC', 'IBOV']].copy()
        df_ibovespa = df_ibovespa.sort_values('DT_COMPTC').reset_index(drop=True)
        return df_ibovespa
    except Exception as e:
        st.error(f"❌ Erro ao obter dados do Ibovespa: {str(e)}")
        return pd.DataFrame()

# Sidebar logo
if logo_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" alt="Copaíba Invest"></div>',
        unsafe_allow_html=True
    )

# Inputs sidebar
cnpj_input = st.sidebar.text_input(
    "CNPJ do Fundo",
    value="",
    placeholder="00.000.000/0000-00",
    help="Digite o CNPJ com ou sem formatação"
)

st.sidebar.markdown("#### Período de Análise")
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
    data_input = st.text_input(
        "Data Final",
        value="",
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        key="data_final"
    )

st.sidebar.markdown("#### Indicadores de Comparação")
mostrar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)
mostrar_ibov = st.sidebar.checkbox("Comparar com Ibovespa", value=False)

st.sidebar.markdown("---")

# Processar inputs
cnpj_limpo = limpar_cnpj(cnpj_input)
data_inicial_formatada = formatar_data_api(data_inicial_input)
data_final_formatada = formatar_data_api(data_final_input)

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

carregar_button = st.sidebar.button("Carregar Dados", type="primary", disabled=not (cnpj_valido and datas_validas))

st.markdown("<h1>Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
st.markdown("---")

# Carregar dados API
@st.cache_data
def carregar_dados_api(cnpj, data_ini_str, data_fim_str):
    dt_inicial = datetime.strptime(data_ini_str, '%Y%m%d')
    dt_ampliada = dt_inicial - timedelta(days=60)
    data_ini_ampliada_str = dt_ampliada.strftime('%Y%m%d')

    url = f"https://www.okanebox.com.br/api/fundoinvestimento/hist/{cnpj}/{data_ini_ampliada_str}/{data_fim_str}/"
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

def format_brl(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_pct_port(x):
    return f"{x*100:.2f}%".replace('.', ',')

if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False

if carregar_button and cnpj_valido and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpj = cnpj_limpo
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada
    st.session_state.mostrar_cdi = mostrar_cdi
    st.session_state.mostrar_ibov = mostrar_ibov

if not st.session_state.dados_carregados:
    st.info("👈 Preencha os campos na barra lateral e clique em 'Carregar Dados' para começar a análise.")
    st.stop()

try:
    with st.spinner('🔄 Carregando dados...'):
        dt_ini_user = datetime.strptime(st.session_state.data_ini, '%Y%m%d')
        dt_fim_user = datetime.strptime(st.session_state.data_fim, '%Y%m%d')

        df_fundo_completo = carregar_dados_api(
            st.session_state.cnpj,
            st.session_state.data_ini,
            st.session_state.data_fim
        )
        df_fundo_completo = df_fundo_completo.sort_values('DT_COMPTC').reset_index(drop=True)

        # CDI
        df_cdi_raw = pd.DataFrame()
        if st.session_state.mostrar_cdi and BCB_DISPONIVEL:
            df_cdi_raw = obter_dados_cdi_real(dt_ini_user, dt_fim_user)
            if not df_cdi_raw.empty:
                df_cdi_raw = df_cdi_raw.sort_values('DT_COMPTC').reset_index(drop=True)

        #ovespa
        df_ibov_raw = pd.DataFrame()
        if st.session_state.mostrar_ibov and YF_DISPONIVEL:
            df_ibov_raw = obter_dados_ibov(dt_ini_user, dt_fim_user)
            if not df_ibov_raw.empty:
                df_ibov_raw = df_ibov_raw.sort_values('DT_COMPTC').reset_index(drop=True)

        df_final = df_fundo_completo.copy()

        if not df_cdi_raw.empty:
            df_final = df_final.merge(
                df_cdi_raw[['DT_COMPTC', 'cdi', 'VL_CDI_normalizado']],
                on='DT_COMPTC',
                how='left'
            )
        else:
            df_final.drop(columns=[c for c in ['cdi', 'VL_CDI_normalizado'] if c in df_final.columns],
                          errors='ignore', inplace=True)

        if not df_ibov_raw.empty:
            df_final = df_final.merge(
                df_ibov_raw[['DT_COMPTC', 'IBOV']],
                on='DT_COMPTC',
                how='left'
            )
        else:
            df_final.drop(columns=[c for c in ['IBOV'] if c in df_final.columns],
                          errors='ignore', inplace=True)

        df_final = df_final.sort_values('DT_COMPTC').reset_index(drop=True)

        for col in ['VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST', 'CAPTC_DIA', 'RESG_DIA']:
            if col in df_final.columns:
                df_final[col] = df_final[col].ffill()

        if 'IBOV' in df_final.columns:
            df_final['IBOV'] = df_final['IBOV'].ffill()

        df_final.dropna(subset=['VL_QUOTA'], inplace=True)

        df = df_final[(df_final['DT_COMPTC'] >= dt_ini_user) & (df_final['DT_COMPTC'] <= dt_fim_user)].copy()
        if df.empty:
            st.error("❌ Não há dados disponíveis para o fundo no período selecionado.")
            st.stop()

        # Cores
        color_primary = "#1a5f3f"
        color_secondary = "#2d8659"
        color_danger = "#b02a37"
        color_cdi = "#000000"      # CDI preto
        color_ibov = "#f0c74b"     # Ibov amarelo suave

        # Normalizar fundo
        primeira_cota_fundo = df['VL_QUOTA'].iloc[0]
        df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota_fundo) - 1) * 100

        tem_cdi = False
        tem_ibov = False

        if st.session_state.mostrar_cdi and 'VL_CDI_normalizado' in df.columns and not df['VL_CDI_normalizado'].isna().all():
            first_cdi_norm = df['VL_CDI_normalizado'].iloc[0]
            df['CDI_COTA'] = df['VL_CDI_normalizado'] / first_cdi_norm
            df['CDI_NORM'] = (df['CDI_COTA'] - 1) * 100
            tem_cdi = True

        if st.session_state.mostrar_ibov and 'IBOV' in df.columns and not df['IBOV'].isna().all():
            first_ibov = df['IBOV'].iloc[0]
            df['IBOV_COTA'] = df['IBOV'] / first_ibov
            df['IBOV_NORM'] = (df['IBOV_COTA'] - 1) * 100
            tem_ibov = True

        # Retornos diários
        df['RET_FUNDO'] = df['VL_QUOTA'].pct_change()
        if tem_cdi and 'CDI_COTA' in df.columns:
            df['RET_CDI'] = df['CDI_COTA'].pct_change()
        if tem_ibov and 'IBOV_COTA' in df.columns:
            df['RET_IBOV'] = df['IBOV_COTA'].pct_change()

        df['ACUM_FUNDO'] = (1 + df['RET_FUNDO'].fillna(0)).cumprod()
        if tem_cdi and 'RET_CDI' in df.columns:
            df['ACUM_CDI'] = (1 + df['RET_CDI'].fillna(0)).cumprod()
        if tem_ibov and 'RET_IBOV' in df.columns:
            df['ACUM_IBOV'] = (1 + df['RET_IBOV'].fillna(0)).cumprod()

        n_dias = df['RET_FUNDO'].dropna().shape[0]
        if n_dias > 0:
            retorno_total_fundo = df['ACUM_FUNDO'].iloc[-1] - 1
        else:
            retorno_total_fundo = 0.0

        cagr_fundo = (retorno_total_fundo / n_dias * 252) * 100 if n_dias > 0 else 0.0
        vol_hist = df['RET_FUNDO'].std() * np.sqrt(252) * 100 if n_dias > 1 else 0.0
        max_drawdown = ((df['ACUM_FUNDO'] / df['ACUM_FUNDO'].cummax()) - 1).min() * 100 if n_dias > 1 else 0.0

        if tem_cdi and 'ACUM_CDI' in df.columns:
            retorno_total_cdi = df['ACUM_CDI'].iloc[-1] - 1
            cagr_cdi = (retorno_total_cdi / n_dias * 252) * 100 if n_dias > 0 else 0.0
        else:
            cagr_cdi = np.nan

        if tem_ibov and 'ACUM_IBOV' in df.columns:
            retorno_total_ibov = df['ACUM_IBOV'].iloc[-1] - 1
            cagr_ibov = (retorno_total_ibov / n_dias * 252) * 100 if n_dias > 0 else 0.0
        else:
            cagr_ibov = np.nan

        # Drawdown série
        df['CUMMAX_FUNDO'] = df['ACUM_FUNDO'].cummax()
        df['Drawdown'] = (df['ACUM_FUNDO'] / df['CUMMAX_FUNDO'] - 1) * 100

        # Captação acumulada
        if 'CAPTC_DIA' in df.columns and 'RESG_DIA' in df.columns:
            df['CAPTACAO_LIQUIDA_DIA'] = df['CAPTC_DIA'] - df['RESG_DIA']
            df['Soma_Acumulada'] = df['CAPTACAO_LIQUIDA_DIA'].cumsum()
        else:
            df['Soma_Acumulada'] = 0.0

        # Patrimônio médio por cotista
        if 'VL_PATRIM_LIQ' in df.columns and 'NR_COTST' in df.columns:
            df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST'].replace(0, np.nan)
        else:
            df['Patrimonio_Liq_Medio'] = np.nan

        # VaR e ES
        rolling_window_var = 21
        df['RET_21D_FUNDO'] = df['RET_FUNDO'].rolling(rolling_window_var).sum()
        df_var_calc = df['RET_21D_FUNDO'].dropna()
        if not df_var_calc.empty:
            VaR_95 = df_var_calc.quantile(0.05)
            VaR_99 = df_var_calc.quantile(0.01)
            ES_95 = df_var_calc[df_var_calc <= VaR_95].mean()
            ES_99 = df_var_calc[df_var_calc <= VaR_99].mean()
            df_plot_var = df.dropna(subset=['RET_21D_FUNDO']).copy()
        else:
            VaR_95 = VaR_99 = ES_95 = ES_99 = np.nan
            df_plot_var = pd.DataFrame()

        # Vol móvel
        vol_window = 63
        df['Volatilidade'] = df['RET_FUNDO'].rolling(vol_window).std() * np.sqrt(252) * 100

        # ====== MÉTRICAS SUPERIORES ======
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            st.metric("PL Atual", format_brl(df['VL_PATRIM_LIQ'].iloc[-1]) if 'VL_PATRIM_LIQ' in df.columns else "N/A")
        with col_m2:
            st.metric("Retorno Acumulado", f"{retorno_total_fundo*100:.2f}%")
        with col_m3:
            # PL médio 12 meses
            dt_limite_12m = df['DT_COMPTC'].max() - pd.DateOffset(days=365)
            df_12m = df[df['DT_COMPTC'] >= dt_limite_12m]
            if not df_12m.empty and 'VL_PATRIM_LIQ' in df_12m.columns:
                pl_medio_12m = df_12m['VL_PATRIM_LIQ'].mean()
                st.metric("PL Médio 12 meses", format_brl(pl_medio_12m))
            else:
                st.metric("PL Médio 12 meses", "N/A")
        with col_m4:
            st.metric("Cotistas Atuais", f"{int(df['NR_COTST'].iloc[-1])}" if 'NR_COTST' in df.columns else "N/A")

        st.markdown("---")

        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Rentabilidade",
            "Risco",
            "Patrimônio e Captação",
            "Cotistas",
            "Janelas Móveis"
        ])

        # ===== TAB 1 - RENTABILIDADE =====
        with tab1:
            st.subheader("Rentabilidade Histórica")

            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_QUOTA_NORM'],
                mode='lines',
                name='Fundo',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Retorno Fundo: %{y:.2f}%<extra></extra>'
            ))

            if tem_cdi:
                fig1.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['CDI_NORM'],
                    mode='lines',
                    name='CDI',
                    line=dict(color=color_cdi, width=2.0),
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>Retorno CDI: %{y:.2f}%<extra></extra>'
                ))

            if tem_ibov:
                fig1.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['IBOV_NORM'],
                    mode='lines',
                    name='Ibovespa',
                    line=dict(color=color_ibov, width=2.0),
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>Retorno Ibovespa: %{y:.2f}%<extra></extra>'
                ))

            fig1.update_layout(
                xaxis_title="Data",
                yaxis_title="Retorno Acumulado (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            fig1 = add_watermark_and_style(
                fig1,
                logo_base64,
                x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()],
                x_autorange=False
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Excesso de Retorno Anualizado
            st.subheader("Excesso de Retorno Anualizado (Fundo vs Benchmark)")

            df['CAGR_Fundo'] = ((df['ACUM_FUNDO'] - 1) / np.arange(1, len(df) + 1) * 252) * 100
            if tem_cdi and 'ACUM_CDI' in df.columns:
                df['CAGR_CDI'] = ((df['ACUM_CDI'] - 1) / np.arange(1, len(df) + 1) * 252) * 100
            if tem_ibov and 'ACUM_IBOV' in df.columns:
                df['CAGR_IBOV'] = ((df['ACUM_IBOV'] - 1) / np.arange(1, len(df) + 1) * 252) * 100

            df['EXCESSO_RETORNO_ANUALIZADO_CDI'] = np.nan
            df['EXCESSO_RETORNO_ANUALIZADO_IBOV'] = np.nan

            if tem_cdi and 'CAGR_CDI' in df.columns:
                valid_idx_cdi = df.dropna(subset=['CAGR_Fundo', 'CAGR_CDI']).index
                df.loc[valid_idx_cdi, 'EXCESSO_RETORNO_ANUALIZADO_CDI'] = (
                    (1 + df.loc[valid_idx_cdi, 'CAGR_Fundo'] / 100) /
                    (1 + df.loc[valid_idx_cdi, 'CAGR_CDI'] / 100) - 1
                ) * 100

            if tem_ibov and 'CAGR_IBOV' in df.columns:
                valid_idx_ibov = df.dropna(subset=['CAGR_Fundo', 'CAGR_IBOV']).index
                df.loc[valid_idx_ibov, 'EXCESSO_RETORNO_ANUALIZADO_IBOV'] = (
                    (1 + df.loc[valid_idx_ibov, 'CAGR_Fundo'] / 100) /
                    (1 + df.loc[valid_idx_ibov, 'CAGR_IBOV'] / 100) - 1
                ) * 100

            if (tem_cdi and not df['EXCESSO_RETORNO_ANUALIZADO_CDI'].dropna().empty) or \
               (tem_ibov and not df['EXCESSO_RETORNO_ANUALIZADO_IBOV'].dropna().empty):

                fig_excesso = go.Figure()

                if tem_cdi and not df['EXCESSO_RETORNO_ANUALIZADO_CDI'].dropna().empty:
                    fig_excesso.add_trace(go.Scatter(
                        x=df['DT_COMPTC'],
                        y=df['EXCESSO_RETORNO_ANUALIZADO_CDI'],
                        mode='lines',
                        name='Excesso vs CDI',
                        line=dict(color=color_cdi, width=2.5),
                        hovertemplate='<b>Excesso vs CDI</b><br>Data: %{x|%d/%m/%Y}<br>Excesso: %{y:.2f}%<extra></extra>'
                    ))

                if tem_ibov and not df['EXCESSO_RETORNO_ANUALIZADO_IBOV'].dropna().empty:
                    fig_excesso.add_trace(go.Scatter(
                        x=df['DT_COMPTC'],
                        y=df['EXCESSO_RETORNO_ANUALIZADO_IBOV'],
                        mode='lines',
                        name='Excesso vs Ibovespa',
                        line=dict(color=color_ibov, width=2.5),
                        hovertemplate='<b>Excesso vs Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Excesso: %{y:.2f}%<extra></extra>'
                    ))

                fig_excesso.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

                fig_excesso.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Excesso de Retorno (% a.a.)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Inter, sans-serif")
                )

                df_plot_excess = df.dropna(
                    subset=['EXCESSO_RETORNO_ANUALIZADO_CDI', 'EXCESSO_RETORNO_ANUALIZADO_IBOV'],
                    how='all'
                ).copy()
                if not df_plot_excess.empty:
                    fig_excesso = add_watermark_and_style(
                        fig_excesso,
                        logo_base64,
                        x_range=[df_plot_excess['DT_COMPTC'].min(), df_plot_excess['DT_COMPTC'].max()],
                        x_autorange=False
                    )
                else:
                    fig_excesso = add_watermark_and_style(fig_excesso, logo_base64)

                st.plotly_chart(fig_excesso, use_container_width=True)
            else:
                st.info("ℹ️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado.")

        # ===== TAB 2 - RISCO =====
        with tab2:
            st.subheader("Drawdown Histórico")

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Drawdown'],
                mode='lines',
                name='Drawdown do Fundo',
                line=dict(color=color_danger, width=2.5),
                hovertemplate='<b>Drawdown do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ))

            if tem_cdi and 'CDI_COTA' in df.columns:
                cdi_cummax = df['CDI_COTA'].cummax()
                df['Drawdown_CDI'] = (df['CDI_COTA'] / cdi_cummax - 1) * 100
                fig3.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['Drawdown_CDI'],
                    mode='lines',
                    name='Drawdown CDI',
                    line=dict(color=color_cdi, width=2.0),
                    hovertemplate='<b>Drawdown CDI</b><br>Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
                ))

            if tem_ibov and 'IBOV_COTA' in df.columns:
                ibov_cummax = df['IBOV_COTA'].cummax()
                df['Drawdown_IBOV'] = (df['IBOV_COTA'] / ibov_cummax - 1) * 100
                fig3.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['Drawdown_IBOV'],
                    mode='lines',
                    name='Drawdown Ibovespa',
                    line=dict(color=color_ibov, width=2.0),
                    hovertemplate='<b>Drawdown Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
                ))

            fig3.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

            fig3.update_layout(
                xaxis_title="Data",
                yaxis_title="Drawdown (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            fig3 = add_watermark_and_style(
                fig3,
                logo_base64,
                x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()],
                x_autorange=False
            )
            st.plotly_chart(fig3, use_container_width=True)

            st.subheader(f"Volatilidade Móvel ({vol_window} dias úteis)")

            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Volatilidade'],
                mode='lines',
                name=f'Volatilidade do Fundo ({vol_window} dias)',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='<b>Vol Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
            ))

            if tem_ibov and 'IBOV_COTA' in df.columns:
                ibov_ret = df['IBOV_COTA'].pct_change()
                df['Vol_IBOV'] = ibov_ret.rolling(vol_window).std() * np.sqrt(252) * 100
                fig4.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['Vol_IBOV'],
                    mode='lines',
                    name=f'Vol Ibovespa ({vol_window} dias)',
                    line=dict(color=color_ibov, width=2.0),
                    hovertemplate='<b>Vol Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
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
            fig4 = add_watermark_and_style(
                fig4,
                logo_base64,
                x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()],
                x_autorange=False
            )
            st.plotly_chart(fig4, use_container_width=True)

            st.subheader("Value at Risk (VaR) e Expected Shortfall (ES)")

            if not df_plot_var.empty:
                fig5 = go.Figure()
                fig5.add_trace(go.Scatter(
                    x=df_plot_var['DT_COMPTC'],
                    y=df_plot_var['RET_21D_FUNDO'] * 100,
                    mode='lines',
                    name='Rentabilidade 21d',
                    line=dict(color=color_primary, width=2),
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>Retorno 21d: %{y:.2f}%<extra></extra>'
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
                fig5 = add_watermark_and_style(
                    fig5,
                    logo_base64,
                    x_range=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                    x_autorange=False
                )
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias).")

        # ===== TAB 3 - PATRIMÔNIO E CAPTAÇÃO =====
        with tab3:
            st.subheader("Patrimônio e Captação Líquida")

            fig6 = go.Figure()
            fig6.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Soma_Acumulada'],
                mode='lines',
                name='Captação Líquida Acumulada',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Captação Líquida Acum.: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['Soma_Acumulada']]
            ))
            fig6.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_PATRIM_LIQ'],
                mode='lines',
                name='Patrimônio Líquido',
                line=dict(color=color_secondary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Líquido: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['VL_PATRIM_LIQ']]
            ))

            fig6.update_layout(
                xaxis_title="Data",
                yaxis_title="Valor (R$)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            fig6 = add_watermark_and_style(
                fig6,
                logo_base64,
                x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()],
                x_autorange=False
            )
            st.plotly_chart(fig6, use_container_width=True)

            st.subheader("Captação Líquida Mensal")

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
                    customdata=[format_brl(v) for v in df_monthly['Captacao_Liquida']],
                    text=[format_brl(v) for v in df_monthly['Captacao_Liquida']],
                    textposition='outside'
                )
            ])

            if not df_monthly.empty:
                y_min = df_monthly['Captacao_Liquida'].min()
                y_max = df_monthly['Captacao_Liquida'].max()
                if y_min == y_max:
                    y_min *= 0.9
                    y_max *= 1.1
            else:
                y_min, y_max = 0, 1

            fig7.update_layout(
                xaxis_title="Mês",
                yaxis_title="Valor (R$)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif"),
                yaxis=dict(range=[y_min, y_max])
            )

            if not df_monthly.empty:
                fig7 = add_watermark_and_style(
                    fig7,
                    logo_base64,
                    x_range=[df_monthly.index.min(), df_monthly.index.max()],
                    x_autorange=False
                )
            else:
                fig7 = add_watermark_and_style(fig7, logo_base64)

            st.plotly_chart(fig7, use_container_width=True)

        # ===== TAB 4 - COTISTAS =====
        with tab4:
            st.subheader("Patrimônio Médio e Nº de Cotistas")

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
            fig8 = add_watermark_and_style(
                fig8,
                logo_base64,
                x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()],
                x_autorange=False
            )
            st.plotly_chart(fig8, use_container_width=True)

        # ===== TAB 5 - JANELAS MÓVEIS =====
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
                if len(df_returns) > dias:
                    df_returns[f'FUNDO_{nome}'] = df_returns['VL_QUOTA'] / df_returns['VL_QUOTA'].shift(dias) - 1
                    if tem_cdi and 'CDI_COTA' in df_returns.columns:
                        df_returns[f'CDI_{nome}'] = df_returns['CDI_COTA'] / df_returns['CDI_COTA'].shift(dias) - 1
                    if tem_ibov and 'IBOV_COTA' in df_returns.columns:
                        df_returns[f'IBOV_{nome}'] = df_returns['IBOV_COTA'] / df_returns['IBOV_COTA'].shift(dias) - 1
                else:
                    df_returns[f'FUNDO_{nome}'] = np.nan
                    if tem_cdi:
                        df_returns[f'CDI_{nome}'] = np.nan
                    if tem_ibov:
                        df_returns[f'IBOV_{nome}'] = np.nan

            janela_selecionada = st.selectbox("Selecione o período:", list(janelas.keys()))

            if not df_returns[f'FUNDO_{janela_selecionada}'].dropna().empty:
                fig9 = go.Figure()
                fig9.add_trace(go.Scatter(
                    x=df_returns['DT_COMPTC'],
                    y=df_returns[f'FUNDO_{janela_selecionada}'],
                    mode='lines',
                    name=f"Retorno do Fundo — {janela_selecionada}",
                    line=dict(width=2.5, color=color_primary),
                    hovertemplate="<b>Retorno do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                ))

                if tem_cdi:
                    fig9.add_trace(go.Scatter(
                        x=df_returns['DT_COMPTC'],
                        y=df_returns[f'CDI_{janela_selecionada}'],
                        mode='lines',
                        name=f"Retorno do CDI — {janela_selecionada}",
                        line=dict(width=2.5, color=color_cdi),
                        hovertemplate="<b>Retorno do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                    ))

                if tem_ibov:
                    fig9.add_trace(go.Scatter(
                        x=df_returns['DT_COMPTC'],
                        y=df_returns[f'IBOV_{janela_selecionada}'],
                        mode='lines',
                        name=f"Retorno do Ibovespa — {janela_selecionada}",
                        line=dict(width=2.5, color=color_ibov),
                        hovertemplate="<b>Retorno do Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                    ))

                fig9.update_layout(
                    xaxis_title="Data",
                    yaxis_title=f"Retorno {janela_selecionada}",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    yaxis=dict(tickformat=".2%"),
                    font=dict(family="Inter, sans-serif")
                )

                df_plot_returns = df_returns.dropna(subset=[f'FUNDO_{janela_selecionada}']).copy()
                if not df_plot_returns.empty:
                    fig9 = add_watermark_and_style(
                        fig9,
                        logo_base64,
                        x_range=[df_plot_returns['DT_COMPTC'].min(), df_plot_returns['DT_COMPTC'].max()],
                        x_autorange=False
                    )
                else:
                    fig9 = add_watermark_and_style(fig9, logo_base64)

                st.plotly_chart(fig9, use_container_width=True)
            else:
                st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada}.")

            st.subheader("Consistência em Janelas Móveis")

            consistency_data = []
            for nome, dias in janelas.items():
                fund_col = f'FUNDO_{nome}'
                linha = {'Janela': nome.split(' ')[0]}

                if tem_cdi:
                    bench_cdi = f'CDI_{nome}'
                    if fund in df_returns.columns and bench_cdi in df_returns.columns:
                        tmp = df_returns[[fund_col, bench_cdi]].dropna()
                        if not tmp.empty:
                            out = (tmp[fund_col] > tmp[bench_cdi]).sum()
                            total = len(tmp)
                            linha['Consistencia_CDI'] = (out / total) * 100 if total > 0 else np.nan
                        else:
                            linha['Consistencia_CDI'] = np.nan
                    else:
                        linha['Consistencia_CDI'] = np.nan

                if tem_ibov:
                    bench_ibov = f'IBOV_{nome}'
                    if fund_col in df_returns.columns and bench_ibov in df_returns.columns:
                        tmp = df_returns[[fund_col, bench_ibov]].dropna()
                        if not tmp.empty:
                            out = (tmp[fund_col] > tmp[bench_ibov]).sum()
                            total = len(tmp)
                            linha['Consistencia_IBOV'] = (out / total) * 100 if total > 0 else np.nan
                       :
                            linha['Consistencia_IBOV'] = np.nan
                    else:
                        linha['Consistencia_IBOV'] = np.nan

                consistency_data.append(linha)

            df_consistency = pd.DataFrame(consistency_data)

            has_cdi_cons = tem_cdi and 'Consistencia_CDI' in df_consistency.columns and not df_consistency['Consistencia_CDI'].dropna().empty
            has_ibov_cons = tem_ibov and 'Consistencia_IBOV' in df_consistency.columns and not df_consistency['Consistencia_IBOV'].dropna().empty

            if has_cdi_cons or has_ibov_cons:
                fig_consistency = go.Figure()

                if has_cdi_cons:
                    fig_consistency.add_trace(go.Bar(
                        x=df_consistency['Janela'],
                        y=df_consistency['Consistencia_CDI'],
                        name='Consistência vs CDI',
                        marker_color=color_cdi,
                        text=[f"{v:.2f}%" if not pd.isna(v) else "" for v in df_consistency['Consistencia_CDI']],
                        textposition='outside',
                        hovertemplate='Janela: %{x}<br>Consistência vs CDI: %{y:.2f}%<extra></extra>'
                    ))

                if has_ibov_cons:
                    fig_consistency.add_trace(go.Bar(
                        x=df_consistency['Janela'],
                        y=df_consistency['Consistencia_IBOV'],
                        name='Consistência vs Ibovespa',
                        marker_color=color_ibov,
                        text=[f"{v:.2f}%" if not pd.isna(v) else "" for v in df_consistency['Consistencia_IBOV']],
                        textposition='outside',
                        hovertemplate='Janela: %{x}<br>Consistência vs Ibovespa: %{y:.2f}%<extra></extra>'
                    ))

                fig_consistency.update_layout(
                    xaxis_title="Janela (meses)",
                    yaxis_title="Percentual de Superação (%)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Inter, sans-serif"),
                    yaxis=dict(range=[0, 100], ticksuffix="%")
                )
                fig_consistency = add_watermark_and_style(fig_consistency, logo_base64, x_autorange=True)
                st.plotly_chart(fig_consistency, use_container_width=True)
            else:
                st.warning("⚠️ Não há dados suficientes para calcular a Consistência em Janelas Móveis.")

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
