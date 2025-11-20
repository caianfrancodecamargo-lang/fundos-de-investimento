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

# CSS customizado com espaçamentos reduzidos na sidebar e fonte Inter
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

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #5a8a6f 0%, #4a7a5f 100%);
        padding: 1rem 0.8rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

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
        color: #1a5f3f;
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

def limpar_cnpj(cnpj):
    if not cnpj:
        return ""
    return re.sub(r'\D', '', cnpj)

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
            st.error("❌ Não foi possível encontrar a coluna de fechamento do Ibovespa ('Close', 'Close_' ou 'Close_^BVSP').")
            return pd.DataFrame()
        df_ibovespa = df_ibovespa.rename(columns={'Date': 'DT_COMPTC', selected_close_col: 'IBOV'})
        df_ibovespa['DT_COMPTC'] = pd.to_datetime(df_ibovespa['DT_COMPTC'])
        df_ibovespa = df_ibovespa[['DT_COMPTC', 'IBOV']].copy()
        df_ibovespa = df_ibovespa.sort_values('DT_COMPTC').reset_index(drop=True)
        return df_ibovespa
    except Exception as e:
        st.error(f"❌ Erro ao obter dados do Ibovespa: {str(e)}")
        return pd.DataFrame()

# Sidebar
if logo_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" alt="Copaíba Invest"></div>',
        unsafe_allow_html=True
    )

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
    data_final_input = st.text_input(
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

    st.markdown("""
    ### 📋 Como usar:

    1.  **CNPJ do Fundo**: Digite o CNPJ do fundo que deseja analisar
    2.  **Data Inicial**: Digite a data inicial no formato DD/MM/AAAA
    3.  **Data Final**: Digite a data final no formato DD/MM/AAAA
    4.  **Indicadores**: Marque a opção "Comparar com CDI" e/ou "Comparar com Ibovespa" se desejar
    5.  Clique em **Carregar Dados** para visualizar as análises

    ---
    """)
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

        df_cdi_raw = pd.DataFrame()
        if st.session_state.mostrar_cdi and BCB_DISPONIVEL:
            df_cdi_raw = obter_dados_cdi_real(dt_ini_user, dt_fim_user)
            if not df_cdi_raw.empty:
                df_cdi_raw = df_cdi_raw.sort_values('DT_COMPTC').reset_index(drop=True)

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
            df_final.drop(
                columns=[col for col in ['cdi', 'VL_CDI_normalizado'] if col in df_final.columns],
                errors='ignore',
                inplace=True
            )

        if not df_ibov_raw.empty:
            df_final = df_final.merge(
                df_ibov_raw[['DT_COMPTC', 'IBOV']],
                on='DT_COMPTC',
                how='left'
            )
        else:
            df_final.drop(
                columns=[col for col in ['IBOV'] if col in df_final.columns],
                errors='ignore',
                inplace=True
            )

        df_final = df_final.sort_values('DT_COMPTC').reset_index(drop=True)

        fund_cols_to_ffill = ['VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST', 'CAPTC_DIA', 'RESG_DIA']
        for col in fund_cols_to_ffill:
            if col in df_final.columns:
                df_final[col] = df_final[col].ffill()

        if 'IBOV' in df_final.columns:
            df_final['IBOV'] = df_final['IBOV'].ffill()

        df_final.dropna(subset=['VL_QUOTA'], inplace=True)

        df = df_final[(df_final['DT_COMPTC'] >= dt_ini_user) & (df_final['DT_COMPTC'] <= dt_fim_user)].copy()

        if df.empty:
            st.error("❌ Não há dados disponíveis para o fundo no período selecionado.")
            st.stop()

        primeira_cota_fundo = df['VL_QUOTA'].iloc[0]
        df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota_fundo) - 1) * 100

        tem_cdi = False
        if st.session_state.mostrar_cdi and 'VL_CDI_normalizado' in df.columns and not df['VL_CDI_normalizado'].isna().all():
            first_cdi_normalized_value_in_period = df['VL_CDI_normalizado'].iloc[0]
            df['CDI_COTA'] = df['VL_CDI_normalizado'] / first_cdi_normalized_value_in_period
            df['CDI_NORM'] = (df['CDI_COTA'] - 1) * 100
            tem_cdi = True
        else:
            df.drop(
                columns=[col for col in ['cdi', 'VL_CDI_normalizado', 'CDI_COTA', 'CDI_NORM'] if col in df.columns],
                errors='ignore',
                inplace=True
            )

        tem_ibov = False
        if st.session_state.mostrar_ibov and 'IBOV' in df.columns and not df['IBOV'].isna().all():
            first_ibov_value = df['IBOV'].iloc[0]
            if first_ibov_value and not pd.isna(first_ibov_value):
                df['IBOV_COTA'] =['IBOV'] / first_ibov_value
                df['IBOV_NORM'] = (df['IBOV_COTA'] - 1) * 100
                tem_ibov = True
        else:
            df.drop(
                columns=[col for col in ['IBOV', 'IBOV_COTA', 'IBOV_NORM'] if col in df.columns],
                errors='ignore',
                inplace=True
            )

    df = df.sort_values('DT_COMPTC').reset_index(drop=True)

    # MÉTRICAS DO FUNDO
    df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
    df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100
    df['Captacao_Liquida'] = df['CAPTC_DIA'] - df['RESG_DIA']
    df['Soma_Acumulada'] = df['Captacao_Liquida'].cumsum()
    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

    vol_window = 21
    trading_days_in_year = 252
    df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()
    df['Volatilidade'] = df['Variacao_Perc'].rolling(vol_window).std() * np.sqrt(trading_days_in_year) * 100
    vol_hist = round(df['Variacao_Perc'].std() * np.sqrt(trading_days_in_year) * 100, 2)

    df['CAGR_Fundo'] = np.nan
    if tem_cdi:
        df['CAGR_CDI'] = np.nan
    if tem_ibov:
        df['CAGR_IBOV'] = np.nan

    if not df.empty and len(df) > trading_days_in_year:
        end_value_fundo = df['VL_QUOTA'].iloc[-1]
        if tem_cdi:
            end_value_cdi = df['CDI_COTA'].iloc[-1]
        if tem_ibov:
            end_value_ibov = df['IBOV_COTA'].iloc[-1]

        for i in range(len(df) - trading_days_in_year):
            initial_value_fundo = df['VL_QUOTA'].iloc[i]
            num_intervals = (len(df) - 1) - i
            if initial_value_fundo > 0 and num_intervals >= trading_days_in_year:
                df.loc[i, 'CAGR_Fundo'] = ((end_value_fundo / initial_value_fundo) ** (trading_days_in_year / num_intervals) - 1) * 100

            if tem_cdi and 'CDI_COTA' in df.columns:
                initial_value_cdi = df['CDI_COTA'].iloc[i]
                if initial_value_cdi > 0 and num_intervals >= trading_days_in_year:
                    df.loc[i, 'CAGR_CDI'] = ((end_value_cdi / initial_value_cdi) ** (trading_days_in_year / num_intervals) - 1) * 100

            if tem_ibov and 'IBOV_COTA' in df.columns:
                initial_value_ibov = df['IBOV_COTA'].iloc[i]
                if initial_value_ibov > 0 and num_intervals >= trading_days_in_year:
                    df.loc[i, 'CAGR_IBOV'] = ((end_value_ibov / initial_value_ibov) ** (trading_days_in_year / num_intervals) - 1) * 100

    mean_cagr = df['CAGR_Fundo'].mean() if 'CAGR_Fundo' in df.columns else 0
    if pd.isna(mean_cagr):
        mean_cagr = 0

    df['EXCESSO_RETORNO_ANUALIZADO'] = np.nan

    df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
    df_plot_var = df.dropna(subset=['Retorno_21d']).copy()
    VaR_95, VaR_99, ES_95, ES_99 = 0, 0, 0, 0
    if not df_plot_var.empty:
        VaR_95 = np.percentile(df_plot_var['Retorno_21d'], 5)
        VaR_99 = np.percentile(df_plot_var['Retorno_21d'], 1)
        ES_95 = df_plot_var.loc[df_plot_var['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
        ES_99 = df_plot_var.loc[df_plot_var['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()
    else:
        st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias de retorno).")

    color_primary = '#1a5f3f'
    color_secondary = '#6b9b7f'
    color_danger = '#dc3545'
    color_cdi = '#000000'
    color_ibov = '#007bff'

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Patrimônio Líquido", format_brl(df['VL_PATRIM_LIQ'].iloc[-1]))
    with col2:
        st.metric("Rentabilidade Acumulada", fmt_pct_port(df['VL_QUOTA_NORM'].iloc[-1] / 100))
    with col3:
        st.metric("Volatilidade Histórica (a.a.)", f"{vol_hist:.2f}%")
    with col4:
        st.metric("Máx. Drawdown", f"{df['Drawdown'].min():.2f}%")
    with col5:
        st.metric("CAGR Médio", f"{mean_cagr:.2f}%")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Rentabilidade", "Risco", "Patrimônio", "Cotistas", "Retornos Móveis"])

    # ================== TAB 1, TAB 3, TAB 4, TAB 5 ==================
    # (mantidos exatamente como no seu arquivo – não repito aqui pra focar na parte de risco)
    # =================================================================

    with tab2:
        st.subheader("Distribuição de Retornos e VaR")

        if not df_plot_var.empty:
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=df_plot_var['DT_COMPTC'],
                y=df_plot_var['Retorno_21d'] * 100,
                mode='lines',
                name='Retorno 21 dias',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Retorno 21 dias: %{y:.2f}%<extra></extra>'
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[VaR_95 * 100, VaR_95 * 100],
                mode='lines',
                name='VaR 95%',
                line=dict(dash='dash', color='orange', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[VaR_99 * 100, VaR_99 * 100],
                mode='lines',
                name='VaR 99%',
                line=dict(dash='dash', color='red', width=2)
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
                fig5, logo_base64,
                x_range=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                x_autorange=False
            )
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

        st.subheader("Métricas de Risco-Retorno")

        # ------ NOVA LÓGICA COMPLETA PARA RISCO-RETORNO (COM PAIN, BETA, JENSEN) ------
        if (tem_cdi and tem_ibov):
            st.info("ℹ️ As Métricas de Risco-Retorno só podem ser calculadas para um indicador de comparação por vez. Por favor, selecione apenas CDI ou Ibovespa na barra lateral.")
        elif not tem_cdi and not tem_ibov:
            st.info("ℹ️ Selecione um indicador de comparação (CDI ou Ibovespa) na barra lateral para visualizar as Métricas de Risco-Retorno.")
        else:
            benchmark_cota_col = ''
            benchmark_cagr_col = ''
            benchmark_daily_rate_col = ''
            benchmark_name = ''
            if tem_cdi:
                benchmark_cota_col = 'CDI_COTA'
                benchmark_cagr_col = 'CAGR_CDI'
                benchmark_daily_rate_col = 'cdi'
                benchmark_name = 'CDI'
            elif tem_ibov:
                benchmark_cota_col = 'IBOV_COTA'
                benchmark_cagr_col = 'CAGR_IBOV'
                benchmark_name = 'Ibovespa'

            calmar_ratio = sterling_ratio = ulcer_index = martin_ratio = np.nan
            sharpe_ratio = sortino_ratio = information_ratio = np.nan
            pain_index = beta = jensen_alpha = np.nan

            if not df.empty and len(df) > trading_days_in_year and benchmark_cota_col in df.columns:
                total_fund_return = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1
                total_benchmark_return = (df[benchmark_cota_col].iloc[-1] / df[benchmark_cota_col].iloc[0]) - 1

                num_days_in_period = len(df)
                if num_days_in_period > 0:
                    annualized_fund_return = (1 + total_fund_return) ** (trading_days_in_year / num_days_in_period) - 1
                    annualized_benchmark_return = (1 + total_benchmark_return) ** (trading_days_in_year / num_days_in_period) - 1
                else:
                    annualized_fund_return = 0
                    annualized_benchmark_return = 0

                annualized_fund_volatility = vol_hist / 100 if vol_hist else np.nan
                max_drawdown_value = df['Drawdown'].min() / 100 if not df['Drawdown'].empty else np.nan
                cagr_fund_decimal = mean_cagr / 100 if mean_cagr else np.nan

                # Ulcer Index
                drawdown_series = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1)
                squared_drawdowns = drawdown_series ** 2
                if not squared_drawdowns.empty and squared_drawdowns.mean() > 0:
                    ulcer_index = np.sqrt(squared_drawdowns.mean())
                else:
                    ulcer_index = np.nan

                # Pain Index (média dos drawdowns negativos, em valor absoluto)
                negative_drawdowns = drawdown_series[drawdown_series < 0]
                if not negative_drawdowns.empty:
                    pain_index = -negative_drawdowns.mean()
                else:
                    pain_index = np.nan

                # Downside Volatility
                benchmark_daily_returns = pd.Series(dtype='float64')

                if benchmark_daily_rate_col and benchmark_daily_rate_col in df.columns:
                    benchmark_daily_returns = df[benchmark_daily_rate_col] / 100.0
                    excess_returns_vs_benchmark_daily = df['Variacao_Perc'] - benchmark_daily_returns
                    downside_returns = excess_returns_vs_benchmark_daily[excess_returns_vs_benchmark_daily < 0]
                else:
                    downside_returns = df['Variacao_Perc'][df['Variacao_Perc'] < 0]
                    if benchmark_cota_col in df.columns:
                        benchmark_daily_returns = df[benchmark_cota_col].pct_change()

                if not downside_returns.empty:
                    annualized_downside_volatility = downside_returns.std() * np.sqrt(trading_days_in_year)
                else:
                    annualized_downside_volatility = np.nan

                # Tracking Error
                if not benchmark_daily_returns.empty and not df['Variacao_Perc'].empty:
                    excess_daily_returns = df['Variacao_Perc'] - benchmark_daily_returns
                    if not excess_daily_returns.empty:
                        tracking_error = excess_daily_returns.std() * np.sqrt(trading_days_in_year)
                    else:
                        tracking_error = np.nan
                else:
                    tracking_error = np.nan

                # Beta
                if not benchmark_daily_returns.empty:
                    beta_df = pd.concat(
                        [df['Variacao_Perc'], benchmark_daily_returns],
                        axis=1
                    ).dropna()
                    if not beta_df.empty and beta_df.iloc[:, 1].var() != 0:
                        beta = beta_df.iloc[:, 0].cov(beta_df.iloc[:, 1]) / beta_df.iloc[:, 1].var()
                    else:
                        beta = np.nan
                else:
                    beta = np.nan

                # Alpha de Jensen (rf = 0 para simplificar)
                if (
                    not pd.isna(beta)
                    and not pd.isna(annualized_fund_return)
                    and not pd.isna(annualized_benchmark_return)
                ):
                    jensen_alpha = annualized_fund_return - beta * annualized_benchmark_return
                else:
                    jensen_alpha = np.nan

                # Ratios
                if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_benchmark_return) and not pd.isna(max_drawdown_value) and max_drawdown_value != 0:
                    calmar_ratio = (cagr_fund_decimal - annualized_benchmark_return) / abs(max_drawdown_value)
                    sterling_ratio = (cagr_fund_decimal - annualized_benchmark_return) / abs(max_drawdown_value)

                if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_benchmark_return) and not pd.isna(ulcer_index) and ulcer_index != 0:
                    martin_ratio = (cagr_fund_decimal - annualized_benchmark_return) / ulcer_index

                if not pd.isna(annualized_fund_return) and not pd.isna(annualized_benchmark_return) and not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0:
                    sharpe_ratio = (annualized_fund_return - annualized_benchmark_return) / annualized_fund_volatility

                if not pd.isna(annualized_fund_return) and not pd.isna(annualized_benchmark_return) and not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0:
                    sortino_ratio = (annualized_fund_return - annualized_benchmark_return) / annualized_downside_volatility

                if not pd.isna(annualized_fund_return) and not pd.isna(annualized_benchmark_return) and not pd.isna(tracking_error) and tracking_error != 0:
                    information_ratio = (annualized_fund_return - annualized_benchmark_return) / tracking_error

                # Exibição
                st.markdown(f"#### RISCO MEDIDO PELA VOLATILIDADE (vs. {benchmark_name}):")
                col_vol_1, col_vol_2 = st.columns(2)

                with col_vol_1:
                    st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if not pd.isna(sharpe_ratio) else "N/A")
                    st.info(f"""
                    **Sharpe Ratio:** Mede o excesso de retorno do fundo (acima do {benchmark_name}) por unidade de **volatilidade total**. Quanto maior o Sharpe, melhor o retorno para o nível de risco assumido.
                    *   < 1.0: subótimo
                    *   1.0–2.0: bom
                    *   2.0–3.0: muito bom
                    *   ≥ 3.0: excepcional
                    """)

                with col_vol_2:
                    st.metric("Sortino Ratio", f"{sortino_ratio:.2f}" if not pd.isna(sortino_ratio) else "N/A")
                    st.info(f"""
                    **Sortino Ratio:** Similar ao Sharpe, mas considera apenas a **volatilidade de queda**. Foca no risco de perdas.
                    *   < 0.0: retorno não cobre o risco de queda
                    *   0.0–1.0: aceitável
                    *   > 1.0: bom/muito bom
                    """)

                col_vol_3, col_vol_4 = st.columns(2)
                with col_vol_3:
                    st.metric("Information Ratio", f"{information_ratio:.2f}" if not pd.isna(information_ratio) else "N/A")
                    st.info(f"""
                    **Information Ratio:** Mede o excesso de retorno sobre o {benchmark_name} por unidade de **tracking error**.
                    *   < 0.0: abaixo do benchmark
                    *   0.0–0.5: habilidade modesta
                    *   0.5–1.0: boa consistência
                    *   > 1.0: excelente consistência
                    """)
                with col_vol_4:
                    st.metric("Treynor Ratio", "Não calculado", help="Depende explicitamente de Beta e taxa livre de risco.")

                st.markdown(f"#### RISCO MEDIDO PELO DRAWDOWN (vs. {benchmark_name}):")
                col_dd_1, col_dd_2 = st.columns(2)

                with col_dd_1:
                    st.metric("Calmar Ratio", f"{calmar_ratio:.2f}" if not pd.isna(calmar_ratio) else "N/A")
                    st.info("""
                    **Calmar Ratio:** Retorno anualizado dividido pelo maior drawdown absoluto.
                    Valores maiores indicam boa relação retorno / grandes quedas.
                    """)
                with col_dd_2:
                    st.metric("Sterling Ratio", f"{sterling_ratio:.2f}" if not pd.isna(sterling_ratio) else "N/A")
                    st.info("""
                    **Sterling Ratio:** Similar ao Calmar, usando drawdowns como medida de risco.
                    """)
                col_dd_3, col_dd_4 = st.columns(2)
                with col_dd_3:
                    st.metric("Ulcer Index", f"{ulcer_index:.2f}" if not pd.isna(ulcer_index) else "N/A")
                    st.info("""
                    **Ulcer Index:** Mede profundidade e duração das quedas.
                    Quanto menor, menos “doloroso” o histórico de drawdowns.
                    """)
                with col_dd_4:
                    st.metric("Martin Ratio", f"{martin_ratio:.2f}" if not pd.isna(martin_ratio) else "N/A")
                    st.info("""
                    **Martin Ratio:** Excesso de retorno anualizado dividido pelo Ulcer Index.
                    """)
                # NOVO BLOCO – OUTROS INDICADORES
                st.markdown(f"#### OUTROS INDICADORES (vs. {benchmark_name}):")
                col_extra_1, col_extra_2, col_extra_3 = st.columns(3)

                with col_extra_1:
                    st.metric("Pain Index", f"{pain_index:.2f}" if not pd.isna(pain_index) else "N/A")
                    st.info("""
                    **Pain Index:** Média (em valor absoluto) dos drawdowns negativos.
                    Quanto menor, típicas quedas mais rasas.
                    """)

                with col_extra_2:
                    st.metric("Beta", f"{beta:.2f}" if not pd.isna(beta) else "N/A")
                    st.info(f"""
                    **Beta:** Sensibilidade do fundo ao {benchmark_name}, com base nos retornos diários.
                    *   ≈ 1: anda em linha com o {benchmark_name}
                    *   > 1: mais sensível/volátil
                    *   < 1: menos sensível
                    *   < 0: comportamento inverso
                    """)

                with col_extra_3:
                    st.metric("Alpha de Jensen (a.a.)", f"{jensen_alpha*100:.2f}%" if not pd.isna(jensen_alpha) else "N/A")
                    st.info(f"""
                    **Alpha de Jensen:** Quanto o fundo entrega acima/abaixo do retorno esperado dado seu Beta vs. {benchmark_name}, anualizado (rf=0).
                    *   > 0%: retorno acima do esperado
                    *   = 0%: em linha com o esperado
                    *   < 0%: abaixo do esperado
                    """)

                st.markdown("""
                ---
                **Observação:** As faixas são diretrizes gerais; sempre interprete as métricas no contexto da estratégia do fundo e do ciclo de mercado.
                """)

            else:
                st.warning(f"⚠️ Não há dados suficientes para calcular as Métricas de Risco-Retorno (mínimo de 1 ano de dados do fundo e do {benchmark_name}).")

    # As demais tabs (tab1, tab3, tab4, tab5) seguem exatamente como no seu arquivo original,
    # mantendo cores, gráficos e textos que você já ajustou.

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("💡 Verifique se o CNPJ está correto e se há dados disponíveis para o período selecionado.")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 2 0;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        <strong>Dashboard desenvolvido com Streamlit e Plotly</strong>
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem;'>
        Análise de Fundos de Investimentos • Copaíba Invest • 2025
    </p>
</div>
""", unsafe_allow_html=True)
