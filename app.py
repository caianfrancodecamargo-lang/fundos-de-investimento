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

# Cores
color_primary = '#1a5f3f'  # Verde escuro para o fundo
color_secondary = '#6b9b7f' # Verde médio para linhas secundárias
color_danger = '#dc3545'   # Vermelho para perdas
color_cdi = '#000000'      # Preto para o CDI
color_ibov = '#f0b429'     # Amarelo para o Ibovespa

# CSS customizado com fonte Montserrat
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

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

    /* Fundo geral com Montserrat */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Montserrat', sans-serif;
    }

    /* Sidebar com padding reduzido */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #5a8a6f 0%, #4a7a5f 100%);
        padding: 1rem 0.8rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-family: 'Montserrat', sans-serif;
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
        font-family: 'Montserrat', sans-serif;
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
        font-family: 'Montserrat', sans-serif;
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
        font-family: 'Montserrat', sans-serif;
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
        font-family: 'Montserrat', sans-serif;
    }

    /* Cards de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a5f3f; /* Tom esverdeado mais escuro */
        font-family: 'Montserrat', sans-serif;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #2d8659; /* Tom esverdeado mais claro */
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'Montserrat', sans-serif;
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
        font-family: 'Montserrat', sans-serif;
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
        font-family: 'Montserrat', sans-serif;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #1a5f3f;
        font-family: 'Montserrat', sans-serif;
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
                opacity=0.15,  # <<< OPACIDADE DA MARCA D'ÁGUA AUMENTADA PARA 0.15
                layer="below"
            )
        )

    # Estilização elegante
    fig.update_layout(
        plot_bgcolor='rgba(248, 246, 241, 0.5)',
        paper_bgcolor='white',
        font=dict(
            family="Montserrat, sans-serif",
            size=12,
            color="#2c2c2c"
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Montserrat, sans-serif",
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
        title_font=dict(size=13, color="#1a5f3f", family="Montserrat"),
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
        title_font=dict(size=13, color="#1a5f3f", family="Montserrat"),
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

# FUNÇÃO PARA OBTER DADOS REAIS DO CDI
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

# FUNÇÃO PARA OBTER DADOS DO IBOVESPA
@st.cache_data
def obter_dados_ibov(data_inicio: datetime, data_fim: datetime):
    """
    Obtém dados diários do Ibovespa usando yfinance (^BVSP),
    e retorna DataFrame com colunas:
    - DT_COMPTC (datetime)
    - IBOV (fechamento ajustado)
    """
    if not YF_DISPONIVEL:
        return pd.DataFrame()

    try:
        # yfinance considera 'end' como exclusivo, então somamos 1 dia
        start_date = data_inicio
        end_date = data_fim + pd.DateOffset(days=1)

        df_ibovespa = yf.download('^BVSP', start=start_date, end=end_date, progress=False)

        if df_ibovespa.empty:
            return pd.DataFrame()

        # Achata os cabeçalhos multi-nível, se existirem
        if isinstance(df_ibovespa.columns, pd.MultiIndex):
            df_ibovespa.columns = ['_'.join(col).strip() for col in df_ibovespa.columns.values]

        df_ibovespa = df_ibovespa.reset_index()

        # Lógica para identificar a coluna de fechamento, seja 'Close', 'Close_' ou 'Close_^BVSP'
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
        df_ibovespa = df_ibovespa[['DT_COMPTC', 'IBOV']].copy()
        df_ibovespa['DT_COMPTC'] = pd.to_datetime(df_ibovespa['DT_COMPTC'])
        df_ibovespa = df_ibovespa.sort_values('DT_COMPTC').reset_index(drop=True)

        return df_ibovespa

    except Exception as e:
        st.error(f"❌ Erro ao obter dados do Ibovespa: {str(e)}")
        return pd.DataFrame()

# Função para carregar dados do fundo
@st.cache_data
def carregar_dados_api(cnpj, data_ini_str, data_fim_str):
    dt_inicial = datetime.strptime(data_ini_str, '%Y%m%d')
    # Amplia o período inicial para garantir dados para ffill
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

# Funções de formatação
def format_brl(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_pct_port(x):
    return f"{x*100:.2f}%".replace('.', ',')

# Sidebar com logo
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

# Opções para mostrar CDI e Ibovespa
st.sidebar.markdown("#### Indicadores de Comparação")
mostrar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)
mostrar_ibov = st.sidebar.checkbox("Comparar com Ibovespa", value=False)

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
carregar_button = st.sidebar.button("Carregar Dados", type="primary", disabled=not (cnpj_valido and datas_validas))

# Título principal
st.markdown("<h1>Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
st.markdown("---")

# Verificar se deve carregar os dados
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
    4.  **Indicadores**: Marque as opções de comparação (CDI e/ou Ibovespa)
    5.  Clique em **Carregar Dados** para visualizar as análises

    ---

    ### 📊 Análises disponíveis:
    - Rentabilidade histórica e CAGR (com comparação ao CDI/Ibovespa)
    - Análise de risco (Drawdown, Volatilidade, VaR)
    - Evolução patrimonial e captação
    - Perfil de cotistas
    - Retornos em janelas móveis (com comparação aos benchmarks)
    """)

    st.stop()

try:
    with st.spinner('🔄 Carregando dados...'):
        # Converte as datas de input do usuário para objetos datetime
        dt_ini_user = datetime.strptime(st.session_state.data_ini, '%Y%m%d')
        dt_fim_user = datetime.strptime(st.session_state.data_fim, '%Y%m%d')

        # 1. BAIXAR DADOS DO FUNDO
        df_fundo_completo = carregar_dados_api(
            st.session_state.cnpj,
            st.session_state.data_ini,
            st.session_state.data_fim
        )
        df_fundo_completo = df_fundo_completo.sort_values('DT_COMPTC').reset_index(drop=True)

        # Filtrar apenas o período solicitado pelo usuário
        df = df_fundo_completo[(df_fundo_completo['DT_COMPTC'] >= dt_ini_user) & 
                              (df_fundo_completo['DT_COMPTC'] <= dt_fim_user)].copy()
        df = df.sort_values('DT_COMPTC').reset_index(drop=True)

        # 2. OBTER DADOS DO CDI
        df_cdi_raw = pd.DataFrame()
        tem_cdi = False
        if st.session_state.mostrar_cdi and BCB_DISPONIVEL:
            df_cdi_raw = obter_dados_cdi_real(dt_ini_user, dt_fim_user)
            if not df_cdi_raw.empty:
                tem_cdi = True

        # 3. OBTER DADOS DO IBOVESPA
        df_ibov_raw = pd.DataFrame()
        tem_ibov = False
        if st.session_state.mostrar_ibov and YF_DISPONIVEL:
            df_ibov_raw = obter_dados_ibov(dt_ini_user, dt_fim_user)
            if not df_ibov_raw.empty:
                tem_ibov = True

        # 4. COMBINAR TODOS OS DADOS
        df_final = df[['DT_COMPTC', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'CAPTC_DIA', 'RESG_DIA', 'NR_COTST']].copy()

        # Merge com CDI se disponível
        if tem_cdi and not df_cdi_raw.empty:
            df_final = df_final.merge(df_cdi_raw[['DT_COMPTC', 'VL_CDI_normalizado']], on='DT_COMPTC', how='left')
            df_final['CDI_COTA'] = df_final['VL_CDI_normalizado'].fillna(method='ffill')
        else:
            df_final['CDI_COTA'] = np.nan

        # Merge com Ibovespa se disponível
        if tem_ibov and not df_ibov_raw.empty:
            df_final = df_final.merge(df_ibov_raw[['DT_COMPTC', 'IBOV']], on='DT_COMPTC', how='left')
            # Normaliza o Ibovespa para começar em 1.0 no primeiro dia do fundo
            if not df_final.empty and 'IBOV' in df_final.columns:
                primeiro_ibov = df_final['IBOV'].dropna().iloc[0] if not df_final['IBOV'].dropna().empty else 1.0
                df_final['IBOV_COTA'] = df_final['IBOV'] / primeiro_ibov
                df_final['IBOV_COTA'] = df_final['IBOV_COTA'].fillna(method='ffill')
            else:
                df_final['IBOV_COTA'] = np.nan
        else:
            df_final['IBOV_COTA'] = np.nan

        # Garante que o DataFrame principal 'df' seja o df_final para os cálculos subsequentes
        df = df_final.copy()

        # Remove linhas onde VL_QUOTA é NaN (se houver)
        df.dropna(subset=['VL_QUOTA'], inplace=True)
        if df.empty:
            st.error("❌ Não há dados de cotas para o fundo no período selecionado.")
            st.stop()

        # Preenche NaNs nas colunas de patrimônio, captação e cotistas com 0 ou ffill
        df['VL_PATRIM_LIQ'] = df['VL_PATRIM_LIQ'].fillna(method='ffill').fillna(0)
        df['CAPTC_DIA'] = df['CAPTC_DIA'].fillna(0)
        df['RESG_DIA'] = df['RESG_DIA'].fillna(0)
        df['NR_COTST'] = df['NR_COTST'].fillna(method='ffill').fillna(0)

        # Cálculos de rentabilidade
        df['Rentabilidade'] = df['VL_QUOTA'].pct_change()
        df['Rentabilidade_Acumulada'] = df['VL_QUOTA'] / df['VL_QUOTA'].iloc[0] - 1

        # Cálculos para CDI e Ibovespa (se disponíveis)
        if tem_cdi and 'CDI_COTA' in df.columns:
            df['CDI_Rentabilidade'] = df['CDI_COTA'].pct_change()
            df['CDI_Rentabilidade_Acumulada'] = df['CDI_COTA'] / df['CDI_COTA'].iloc[0] - 1
        else:
            df['CDI_Rentabilidade'] = np.nan
            df['CDI_Rentabilidade_Acumulada'] = np.nan

        if tem_ibov and 'IBOV_COTA' in df.columns:
            df['IBOV_Rentabilidade'] = df['IBOV_COTA'].pct_change()
            df['IBOV_Rentabilidade_Acumulada'] = df['IBOV_COTA'] / df['IBOV_COTA'].iloc[0] - 1
        else:
            df['IBOV_Rentabilidade'] = np.nan
            df['IBOV_Rentabilidade_Acumulada'] = np.nan

        # Cálculo de CAGR (Annualized Growth Rate)
        num_dias = (df['DT_COMPTC'].iloc[-1] - df['DT_COMPTC'].iloc[0]).days
        if num_dias > 0:
            cagr_fundo = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0])**(252/num_dias) - 1
        else:
            cagr_fundo = np.nan

        cagr_cdi = np.nan
        if tem_cdi and 'CDI_COTA' in df.columns and num_dias > 0:
            cagr_cdi = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0])**(252/num_dias) - 1

        cagr_ibov = np.nan
        if tem_ibov and 'IBOV_COTA' in df.columns and num_dias > 0:
            cagr_ibov = (df['IBOV_COTA'].iloc[-1] / df['IBOV_COTA'].iloc[0])**(252/num_dias) - 1

        # Cálculo de Captação Líquida Acumulada
        df['Soma_Acumulada'] = (df['CAPTC_DIA'] - df['RESG_DIA']).cumsum()

        # Cálculo de Patrimônio Líquido Médio por Cotista
        df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']
        df['Patrimonio_Liq_Medio'].replace([np.inf, -np.inf], np.nan, inplace=True) # Remove inf

        # Tabs para organizar o dashboard
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Rentabilidade", "Risco e Métricas", "Patrimônio e Captação",
            "Cotistas", "Janelas Móveis"
        ])

    with tab1:
        st.subheader("Rentabilidade Histórica")

        fig1 = go.Figure()

        # Rentabilidade do Fundo
        # NOVO: Preenchimento condicional verde/vermelho
        fill_color_fundo = 'rgba(26, 95, 63, 0.1)' if df['Rentabilidade_Acumulada'].iloc[-1] >= 0 else 'rgba(220, 53, 69, 0.1)'
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Rentabilidade_Acumulada'],
            mode='lines',
            name='Fundo',
            line=dict(width=2.5, color=color_primary),
            fill='tozeroy',
            fillcolor=fill_color_fundo,
            hovertemplate="<b>Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2%}<extra></extra>"
        ))

        # Rentabilidade do CDI (se disponível)
        if tem_cdi:
            # NOVO: Preenchimento condicional verde/vermelho
            fill_color_cdi = 'rgba(26, 95, 63, 0.05)' if df['CDI_Rentabilidade_Acumulada'].iloc[-1] >= 0 else 'rgba(220, 53, 69, 0.05)'
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['CDI_Rentabilidade_Acumulada'],
                mode='lines',
                name='CDI',
                line=dict(width=2.5, color=color_cdi), # Cor preta
                fill='tozeroy',
                fillcolor=fill_color_cdi,
                hovertemplate="<b>CDI</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2%}<extra></extra>"
            ))

        # Rentabilidade do Ibovespa (se disponível)
        if tem_ibov:
            # NOVO: Preenchimento condicional verde/vermelho
            fill_color_ibov = 'rgba(26, 95, 63, 0.05)' if df['IBOV_Rentabilidade_Acumulada'].iloc[-1] >= 0 else 'rgba(220, 53, 69, 0.05)'
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['IBOV_Rentabilidade_Acumulada'],
                mode='lines',
                name='Ibovespa',
                line=dict(width=2.5, color=color_ibov), # Cor amarela
                fill='tozeroy',
                fillcolor=fill_color_ibov,
                hovertemplate="<b>Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2%}<extra></extra>"
            ))

        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade Acumulada",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            yaxis=dict(tickformat=".2%"),
            font=dict(family="Montserrat, sans-serif"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        # Ajusta o range do eixo X para os dados de df
        fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("CAGR (Compound Annual Growth Rate)")

        fig2 = go.Figure()
        cagr_names = ['Fundo']
        cagr_values = [cagr_fundo]
        cagr_colors = [color_primary]

        if tem_cdi:
            cagr_names.append('CDI')
            cagr_values.append(cagr_cdi)
            cagr_colors.append(color_cdi)

        if tem_ibov:
            cagr_names.append('Ibovespa')
            cagr_values.append(cagr_ibov)
            cagr_colors.append(color_ibov)

        fig2.add_trace(go.Bar(
            x=cagr_names,
            y=cagr_values,
            marker_color=cagr_colors,
            hovertemplate='<b>%{x}</b><br>CAGR: %{y:.2%}<extra></extra>',
            text=[f'{val:.2%}' for val in cagr_values], # Adiciona o texto nas barras
            textposition='outside', # Posição do texto fora da barra
            textfont=dict(color='black', size=12) # Cor e tamanho da fonte do texto
        ))

        fig2.update_layout(
            xaxis_title="Ativo",
            yaxis_title="CAGR Anualizado",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            yaxis=dict(tickformat=".2%", range=[min(0, min(cagr_values) * 1.1), max(cagr_values) * 1.1 + 0.05]), # Ajusta o range para o texto
            font=dict(family="Montserrat, sans-serif")
        )
        fig2 = add_watermark_and_style(fig2, logo_base64, x_autorange=True)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Análise de Risco e Métricas de Performance")

        # Validação para Métricas de Risco-Retorno
        if tem_cdi and tem_ibov:
            st.info("ℹ️ Para visualizar as Métricas de Risco-Retorno, selecione apenas um indicador de comparação (CDI ou Ibovespa) na barra lateral.")
            st.stop() # Interrompe a execução desta aba se ambos forem selecionados

        benchmark_name = ''
        benchmark_col_name = ''
        benchmark_rent_col = ''
        if tem_cdi:
            benchmark_name = 'CDI'
            benchmark_col_name = 'CDI_COTA'
            benchmark_rent_col = 'CDI_Rentabilidade'
        elif tem_ibov:
            benchmark_name = 'Ibovespa'
            benchmark_col_name = 'IBOV_COTA'
            benchmark_rent_col = 'IBOV_Rentabilidade'

        # Verifica se há dados suficientes para 1 ano (252 dias úteis)
        if len(df) >= 252 and (not tem_cdi or (tem_cdi and benchmark_col_name in df.columns and not df[benchmark_col_name].isnull().all())) and \
                           (not tem_ibov or (tem_ibov and benchmark_col_name in df.columns and not df[benchmark_col_name].isnull().all())):

            # Cálculos de Volatilidade (Anualizada)
            vol_fundo = df['Rentabilidade'].std() * np.sqrt(252)
            vol_cdi = df['CDI_Rentabilidade'].std() * np.sqrt(252) if tem_cdi else np.nan
            vol_ibov = df['IBOV_Rentabilidade'].std() * np.sqrt(252) if tem_ibov else np.nan

            # Cálculo de Drawdown
            roll_max = df['VL_QUOTA'].expanding(min_periods=1).max()
            daily_drawdown = df['VL_QUOTA'] / roll_max - 1.0
            max_drawdown = daily_drawdown.min()

            # Cálculo de VaR (Value at Risk) - 95% e 99%
            var_95 = df['Rentabilidade'].quantile(0.05)
            var_99 = df['Rentabilidade'].quantile(0.01)

            # Métricas de Risco-Retorno (se houver benchmark selecionado)
            sharpe_ratio = np.nan
            sortino_ratio = np.nan
            information_ratio = np.nan
            calmar_ratio = np.nan
            sterling_ratio = np.nan
            ulcer_index = np.nan
            martin_ratio = np.nan

            if benchmark_name:
                # Excesso de retorno anualizado
                excess_return_anualizado = cagr_fundo - (cagr_cdi if tem_cdi else cagr_ibov)

                # Sharpe Ratio
                if vol_fundo > 0:
                    sharpe_ratio = excess_return_anualizado / vol_fundo

                # Sortino Ratio
                downside_returns = df['Rentabilidade'][df['Rentabilidade'] < (df[benchmark_rent_col] if benchmark_rent_col in df.columns else 0)]
                downside_volatility = downside_returns.std() * np.sqrt(252)
                if downside_volatility > 0:
                    sortino_ratio = excess_return_anualizado / downside_volatility

                # Information Ratio
                if benchmark_rent_col in df.columns:
                    tracking_error = (df['Rentabilidade'] - df[benchmark_rent_col]).std() * np.sqrt(252)
                    if tracking_error > 0:
                        information_ratio = excess_return_anualizado / tracking_error

                # Calmar Ratio
                if max_drawdown < 0:
                    calmar_ratio = cagr_fundo / abs(max_drawdown)

                # Sterling Ratio (simplificado, usando max_drawdown)
                if max_drawdown < 0:
                    sterling_ratio = cagr_fundo / abs(max_drawdown)

                # Ulcer Index
                # Calculando o Ulcer Index
                if not daily_drawdown.empty:
                    squared_drawdown = (daily_drawdown**2).mean()
                    ulcer_index = np.sqrt(squared_drawdown)
                else:
                    ulcer_index = np.nan

                # Martin Ratio
                if not pd.isna(ulcer_index) and ulcer_index > 0:
                    martin_ratio = excess_return_anualizado / ulcer_index


            st.markdown("#### RISCO MEDIDO PELA VOLATILIDADE:")
            col_vol_1, col_vol_2 = st.columns(2)

            with col_vol_1:
                st.metric("Volatilidade Anualizada (Fundo)", f"{vol_fundo:.2%}" if not pd.isna(vol_fundo) else "N/A")
                st.info("""
                **Volatilidade Anualizada:** Mede a dispersão dos retornos do fundo em relação à sua média, anualizada. Um valor mais alto indica maior risco.
                *   **Interpretação Geral:**
                    *   **< 5%:** Baixa volatilidade, geralmente associada a renda fixa conservadora.
                    *   **5% - 15%:** Volatilidade moderada, comum em fundos multimercado ou renda fixa mais arrojada.
                    *   **> 15%:** Alta volatilidade, típica de fundos de ações ou mais agressivos.
                """)
            with col_vol_2:
                st.metric(f"Volatilidade Anualizada ({benchmark_name})", f"{vol_cdi:.2%}" if tem_cdi and not pd.isna(vol_cdi) else (f"{vol_ibov:.2%}" if tem_ibov and not pd.isna(vol_ibov) else "N/A"))
                st.info(f"""
                **Volatilidade Anualizada ({benchmark_name}):** Mede a dispersão dos retornos do {benchmark_name} em relação à sua média, anualizada.
                """)

            col_vol_3, col_vol_4 = st.columns(2)
            with col_vol_3:
                st.metric("VaR (95%)", f"{var_95:.2%}" if not pd.isna(var_95) else "N/A")
                st.info("""
                **Value at Risk (VaR) 95%:** Estima a perda máxima esperada do fundo em um determinado período (aqui, diário) com 95% de confiança. Ou seja, em 95% dos dias, a perda não deve exceder este valor.
                *   **Interpretação Geral:**
                    *   **-0.5% a 0%:** Risco de perda diária muito baixo.
                    *   **-1.5% a -0.5%:** Risco de perda diária moderado.
                    *   **< -1.5%:** Risco de perda diária mais elevado.
                """)
            with col_vol_4:
                st.metric("VaR (99%)", f"{var_99:.2%}" if not pd.isna(var_99) else "N/A")
                st.info("""
                **Value at Risk (VaR) 99%:** Estima a perda máxima esperada do fundo em um determinado período (aqui, diário) com 99% de confiança. É uma medida mais conservadora que o VaR 95%.
                *   **Interpretação Geral:**
                    *   **-1.0% a 0%:** Risco de perda diária muito baixo.
                    *   **-2.5% a -1.0%:** Risco de perda diária moderado.
                    *   **< -2.5%:** Risco de perda diária mais elevado.
                """)

            st.markdown("#### VOLATILIDADE HISTÓRICA (Janela Móvel de 21 dias)")

            # Cálculo da Volatilidade Móvel (21 dias úteis = 1 mês)
            df['Vol_Fundo_21d'] = df['Rentabilidade'].rolling(window=21).std() * np.sqrt(252)
            if tem_cdi:
                df['Vol_CDI_21d'] = df['CDI_Rentabilidade'].rolling(window=21).std() * np.sqrt(252)
            if tem_ibov:
                df['Vol_IBOV_21d'] = df['IBOV_Rentabilidade'].rolling(window=21).std() * np.sqrt(252)

            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Vol_Fundo_21d'],
                mode='lines',
                name='Volatilidade Fundo (21d)',
                line=dict(color=color_primary, width=2.5),
                fill='tozeroy', # NOVO: Preenchimento
                fillcolor='rgba(26, 95, 63, 0.1)', # NOVO: Cor do preenchimento
                hovertemplate="<b>Volatilidade Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2%}<extra></extra>"
            ))
            if tem_cdi:
                fig5.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['Vol_CDI_21d'],
                    mode='lines',
                    name='Volatilidade CDI (21d)',
                    line=dict(color=color_cdi, width=2.5), # Cor preta
                    fill='tozeroy', # NOVO: Preenchimento
                    fillcolor='rgba(0, 0, 0, 0.05)', # NOVO: Cor do preenchimento (preto mais claro)
                    hovertemplate="<b>Volatilidade CDI</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2%}<extra></extra>"
                ))
            if tem_ibov:
                fig5.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['Vol_IBOV_21d'],
                    mode='lines',
                    name='Volatilidade Ibovespa (21d)',
                    line=dict(color=color_ibov, width=2.5), # Cor amarela
                    fill='tozeroy', # NOVO: Preenchimento
                    fillcolor='rgba(240, 180, 41, 0.05)', # NOVO: Cor do preenchimento (amarelo mais claro)
                    hovertemplate="<b>Volatilidade Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2%}<extra></extra>"
                ))

            fig5.update_layout(
                xaxis_title="Data",
                yaxis_title="Volatilidade Anualizada",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                yaxis=dict(tickformat=".2%"),
                font=dict(family="Montserrat, sans-serif"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            # Ajusta o range do eixo X para os dados de df
            df_plot_vol = df.dropna(subset=['Vol_Fundo_21d']).copy()
            if not df_plot_vol.empty:
                fig5 = add_watermark_and_style(fig5, logo_base64, x_range=[df_plot_vol['DT_COMPTC'].min(), df_plot_vol['DT_COMPTC'].max()], x_autorange=False)
            else:
                fig5 = add_watermark_and_style(fig5, logo_base64) # Sem range específico se não houver dados
            st.plotly_chart(fig5, use_container_width=True)

            st.markdown("#### MÉTRICAS DE RETORNO AJUSTADO AO RISCO:")
            col_vol_1, col_vol_2 = st.columns(2)

            with col_vol_1:
                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if not pd.isna(sharpe_ratio) else "N/A")
                st.info(f"""
                **Sharpe Ratio:** Mede o excesso de retorno do fundo (acima do {benchmark_name}) por unidade de risco (volatilidade total). Quanto maior, melhor o retorno ajustado ao risco.
                *   **Interpretação Geral:**
                    *   **< 0.0:** O fundo não compensa o risco assumido.
                    *   **0.0 - 0.5:** Aceitável, mas com espaço para melhoria.
                    *   **0.5 - 1.0:** Bom, o fundo gera bom retorno para o risco.
                    *   **> 1.0:** Muito Bom, excelente retorno ajustado ao risco.
                """)
            with col_vol_2:
                st.metric("Sortino Ratio", f"{sortino_ratio:.2f}" if not pd.isna(sortino_ratio) else "N/A")
                st.info("""
                **Sortino Ratio:** Similar ao Sharpe, mas foca apenas na **volatilidade de baixa** (downside volatility). Ele mede o excesso de retorno por unidade de risco de queda. É útil para investidores que se preocupam mais com perdas do que com a volatilidade geral.
                *   **Interpretação Geral:**
                    *   **< 0.0:** Retorno não cobre o risco de queda.
                    *   **0.0 - 1.0:** Aceitável, o fundo gera retorno positivo para o risco de queda.
                    *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de perdas.
                """)

            col_vol_3, col_vol_4 = st.columns(2)
            with col_vol_3:
                st.metric("Information Ratio", f"{information_ratio:.2f}" if not pd.isna(information_ratio) else "N/A")
                st.info(f"""
                **Information Ratio:** Mede a capacidade do gestor de gerar retornos acima de um benchmark (aqui, o {benchmark_name}), ajustado pelo **tracking error** (risco de desvio em relação ao benchmark). Um valor alto indica que o gestor consistentemente superou o benchmark com um risco de desvio razoável.
                *   **Interpretação Geral:**
                    *   **< 0.0:** O fundo está consistentemente abaixo do benchmark.
                    *   **0.0 - 0.5:** Habilidade modesta em superar o benchmark.
                    *   **0.5 - 1.0:** Boa habilidade e consistência em superar o benchmark.
                    *   **> 1.0:** Excelente habilidade e forte superação consistente do benchmark.
                """)
            with col_vol_4:
                st.metric("Treynor Ratio", "Não Calculável" if not tem_ibov else "N/A") # Treynor precisa de Beta, que precisa de Ibovespa
                st.info("""
                **Treynor Ratio:** Mede o excesso de retorno por unidade de **risco sistemático (Beta)**. O Beta mede a sensibilidade do fundo aos movimentos do mercado.
                *   **Interpretação:** Um valor mais alto é preferível. É mais útil para comparar fundos com Betas semelhantes.
                *   **Observação:** *Não é possível calcular este índice sem dados de um índice de mercado (benchmark) para determinar o Beta do fundo.*
                """)

            st.markdown("#### RISCO MEDIDO PELO DRAWDOWN:")
            col_dd_1, col_dd_2 = st.columns(2)

            with col_dd_1:
                st.metric("Calmar Ratio", f"{calmar_ratio:.2f}" if not pd.isna(calmar_ratio) else "N/A")
                st.info("""
                **Calmar Ratio:** Mede o retorno ajustado ao risco, comparando o **CAGR** (retorno anualizado) do fundo com o seu **maior drawdown** (maior queda). Um valor mais alto indica que o fundo gerou bons retornos sem grandes perdas.
                *   **Interpretação Geral:**
                    *   **< 0.0:** Retorno negativo ou drawdown muito grande.
                    *   **0.0 - 0.5:** Aceitável, mas com espaço para melhoria.
                    *   **0.5 - 1.0:** Bom, o fundo gerencia bem o risco de drawdown.
                    *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de grandes quedas.
                """)
            with col_dd_2:
                st.metric("Sterling Ratio", f"{sterling_ratio:.2f}" if not pd.isna(sterling_ratio) else "N/A")
                st.info("""
                **Sterling Ratio:** Similar ao Calmar, avalia o retorno ajustado ao risco em relação ao drawdown. Geralmente, compara o retorno anualizado com a média dos piores drawdowns. *Nesta análise, para simplificar, utilizamos o maior drawdown como referência.* Um valor mais alto é preferível.
                *   **Interpretação Geral:**
                    *   **< 0.0:** Retorno negativo ou drawdown muito grande.
                    *   **0.0 - 0.5:** Aceitável, mas com espaço para melhoria.
                    *   **0.5 - 1.0:** Bom, o fundo gerencia bem o risco de drawdown.
                    *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de grandes quedas.
                """)

            col_dd_3, col_dd_4 = st.columns(2)
            with col_dd_3:
                st.metric("Ulcer Index", f"{ulcer_index:.2f}" if not pd.isna(ulcer_index) else "N/A")
                st.info("""
                **Ulcer Index:** Mede a profundidade e a duração dos drawdowns (quedas). Quanto menor o índice, menos dolorosas e mais curtas foram as quedas do fundo. É uma medida de risco que foca na "dor" do investidor.
                *   **Interpretação Geral:**
                    *   **< 1.0:** Baixo risco, fundo relativamente estável.
                    *   **1.0 - 2.0:** Risco moderado, com quedas mais frequentes ou profundas.
                    *   **> 2.0:** Alto risco, fundo com quedas significativas e/ou duradouras.
                """)
            with col_dd_4:
                st.metric("Martin Ratio", f"{martin_ratio:.2f}" if not pd.isna(martin_ratio) else "N/A")
                st.info(f"""
                **Martin Ratio:** Avalia o retorno ajustado ao risco dividindo o excesso de retorno anualizado (acima do {benchmark_name}) pelo **Ulcer Index**. Um valor mais alto indica um melhor desempenho em relação ao risco de drawdown.
                *   **Interpretação Geral:**
                    *   **< 0.0:** O fundo não compensa o risco de drawdown.
                    *   **0.0 - 1.0:** Aceitável, o fundo gera retorno positivo para o risco de drawdown.
                    *   **> 1.0:** Bom, o fundo entrega um bom retorno considerando a "dor" dos drawdowns.
                """)

            st.markdown("""
            ---
            **Observação Importante sobre as Interpretações:**
            Os intervalos e classificações acima são **diretrizes gerais** baseadas em práticas comuns do mercado financeiro e literaturas de investimento. A interpretação de qualquer métrica de risco-retorno deve sempre considerar o **contexto específico do fundo** (estratégia, classe de ativos, objetivo), as **condições de mercado** no período analisado e o **perfil de risco do investidor**. Não há um "número mágico" que sirva para todos os casos.
            """)

        elif not tem_cdi and not tem_ibov:
            st.info("ℹ️ Selecione um indicador de comparação (CDI ou Ibovespa) na barra lateral para visualizar as Métricas de Risco-Retorno.")
        else:
            st.warning(f"⚠️ Não há dados suficientes para calcular as Métricas de Risco-Retorno (mínimo de 1 ano de dados do fundo e do {benchmark_name}).")


    with tab3:
        st.subheader("Patrimônio e Captação Líquida")

        fig6 = go.Figure([
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Soma_Acumulada'],
                mode='lines',
                name='Captação Líquida',
                line=dict(color=color_primary, width=2.5),
                fill='tozeroy',
                fillcolor='rgba(26, 95, 63, 0.1)',
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Captação Líquida Acumulada: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['Soma_Acumulada']]
            ),
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_PATRIM_LIQ'],
                mode='lines',
                name='Patrimônio Líquido',
                line=dict(color=color_secondary, width=2.5),
                fill='tozeroy',
                fillcolor='rgba(45, 134, 89, 0.1)',
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
            font=dict(family="Montserrat, sans-serif")
        )
        # Ajusta o range do eixo X para os dados de df
        fig6 = add_watermark_and_style(fig6, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
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
                # REMOVIDO: text=df_monthly['Captacao_Liquida'].apply(lambda x: format_brl(x)),
                # REMOVIDO: textposition='outside',
                # REMOVIDO: textfont=dict(color='black', size=12)
            )
        ])

        fig7.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Montserrat, sans-serif"),
        )
        # Ajusta o range do eixo X para os dados de df_monthly
        if not df_monthly.empty:
            fig7 = add_watermark_and_style(fig7, logo_base64, x_range=[df_monthly.index.min(), df_monthly.index.max()], x_autorange=False)
        else:
            fig7 = add_watermark_and_style(fig7, logo_base64) # Sem range específico se não houver dados
        st.plotly_chart(fig7, use_container_width=True)

    with tab4:
        st.subheader("Patrimônio Médio e Nº de Cotistas")

        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Patrimonio_Liq_Medio'],
            mode='lines',
            name='Patrimônio Médio por Cotista',
            line=dict(color=color_primary, width=2.5),
            fill='tozeroy',
            fillcolor='rgba(26, 95, 63, 0.1)',
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
            fill='tozeroy',
            fillcolor='rgba(45, 134, 89, 0.1)',
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Nº de Cotistas: %{y}<extra></extra>'
        ))

        fig8.update_layout(
            xaxis_title="Data",
            yaxis=dict(title="Patrimônio Médio por Cotista (R$)"),
            yaxis2=dict(title="Número de Cotistas", overlaying="y", side="right"),
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Montserrat, sans-serif")
        )
        # Ajusta o range do eixo X para os dados de df
        fig8 = add_watermark_and_style(fig8, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
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
            # Certifica-se de que há dados suficientes para a janela
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

            # Retorno do Fundo
            # NOVO: Preenchimento condicional verde/vermelho
            fill_color_fundo_ret = 'rgba(26, 95, 63, 0.1)' if df_returns[f'FUNDO_{janela_selecionada}'].iloc[-1] >= 0 else 'rgba(220, 53, 69, 0.1)'
            fig9.add_trace(go.Scatter(
                x=df_returns['DT_COMPTC'],
                y=df_returns[f'FUNDO_{janela_selecionada}'],
                mode='lines',
                name=f"Retorno do Fundo — {janela_selecionada}",
                line=dict(width=2.5, color=color_primary),
                fill='tozeroy',
                fillcolor=fill_color_fundo_ret,
                hovertemplate="<b>Retorno do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
            ))

            # Retorno do CDI (se disponível)
            if tem_cdi:
                # NOVO: Preenchimento condicional verde/vermelho
                fill_color_cdi_ret = 'rgba(26, 95, 63, 0.05)' if df_returns[f'CDI_{janela_selecionada}'].iloc[-1] >= 0 else 'rgba(220, 53, 69, 0.05)'
                fig9.add_trace(go.Scatter(
                    x=df_returns['DT_COMPTC'],
                    y=df_returns[f'CDI_{janela_selecionada}'],
                    mode='lines',
                    name=f"Retorno do CDI — {janela_selecionada}",
                    line=dict(width=2.5, color=color_cdi), # Cor preta
                    fill='tozeroy',
                    fillcolor=fill_color_cdi_ret,
                    hovertemplate="<b>Retorno do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                ))

            # Retorno do Ibovespa (se disponível)
            if tem_ibov:
                # NOVO: Preenchimento condicional verde/vermelho
                fill_color_ibov_ret = 'rgba(26, 95, 63, 0.05)' if df_returns[f'IBOV_{janela_selecionada}'].iloc[-1] >= 0 else 'rgba(220, 53, 69, 0.05)'
                fig9.add_trace(go.Scatter(
                    x=df_returns['DT_COMPTC'],
                    y=df_returns[f'IBOV_{janela_selecionada}'],
                    mode='lines',
                    name=f"Retorno do Ibovespa — {janela_selecionada}",
                    line=dict(width=2.5, color=color_ibov), # Cor amarela
                    fill='tozeroy',
                    fillcolor=fill_color_ibov_ret,
                    hovertemplate="<b>Retorno do Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                ))

            fig9.update_layout(
                xaxis_title="Data",
                yaxis_title=f"Retorno {janela_selecionada}",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                yaxis=dict(tickformat=".2%"),
                font=dict(family="Montserrat, sans-serif"),
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
        st.subheader("Consistência em Janelas Móveis")

        if (tem_cdi and not tem_ibov) or (tem_ibov and not tem_cdi):
            consistency_data = []
            benchmark_prefix = ''
            benchmark_name_consistency = ''
            if tem_cdi:
                benchmark_prefix = 'CDI'
                benchmark_name_consistency = 'CDI'
            elif tem_ibov:
                benchmark_prefix = 'IBOV'
                benchmark_name_consistency = 'Ibovespa'

            for nome, dias in janelas.items():
                fund_col = f'FUNDO_{nome}'
                benchmark_col = f'{benchmark_prefix}_{nome}'

                if fund_col in df_returns.columns and benchmark_col in df_returns.columns:
                    temp_df = df_returns[[fund_col, benchmark_col]].dropna()

                    if not temp_df.empty:
                        outperformed_count = (temp_df[fund_col] > temp_df[benchmark_col]).sum()
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
                    hovertemplate=f'<b>Janela:</b> %{{x}}<br><b>Consistência vs {benchmark_name_consistency}:</b> %{{y:.2f}}%<extra></extra>'
                ))

                fig_consistency.update_layout(
                    xaxis_title="Janela (meses)",
                    yaxis_title=f"Percentual de Superação do {benchmark_name_consistency} (%)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Montserrat, sans-serif"),
                    yaxis=dict(range=[0, max(df_consistency['Consistencia']) * 1.1 + 5], ticksuffix="%") # Ajusta o range superior para dar mais espaço ao texto
                )
                fig_consistency = add_watermark_and_style(fig_consistency, logo_base64, x_autorange=True)
                st.plotly_chart(fig_consistency, use_container_width=True)
            else:
                st.warning(f"⚠️ Não há dados suficientes para calcular a Consistência em Janelas Móveis vs {benchmark_name_consistency}.")
        elif tem_cdi and tem_ibov:
            st.info("ℹ️ Para visualizar a Consistência em Janelas Móveis, selecione apenas um indicador de comparação (CDI ou Ibovespa) na barra lateral.")
        else:
            st.info("ℹ️ Selecione um indicador de comparação (CDI ou Ibovespa) na barra lateral para visualizar a Consistência em Janelas Móveis.")

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("💡 Verifique se o CNPJ está correto e se há dados disponíveis para o período selecionado.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 2rem 0;'>
    <p style='margin: 0; font-size: 0.9rem; font-family: "Montserrat", sans-serif;'>
        <strong>Dashboard desenvolvido com Streamlit e Plotly</strong>
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem; font-family: "Montserrat", sans-serif;'>
        Análise de Fundos de Investimentos • Copaíba Invest • 2025
    </p>
</div>
""", unsafe_allow_html=True)
