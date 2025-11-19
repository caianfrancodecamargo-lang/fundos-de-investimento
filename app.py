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
import yfinance as yf # <<< ADICIONADO: Importar yfinance para dados do Ibovespa

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
                opacity=0.15,  # <<< OPACIDADE DA MARCA D'ÁGUA AUMENTADA PARA 0.15
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
        # Aumenta o período de busca para 10 anos antes da data inicial para garantir dados
        # mesmo que o período solicitado seja curto, e depois filtra.
        # No entanto, a biblioteca `bcb` já lida com o `start` e `end` diretamente.
        # A memória do usuário indica "intervalos de 10 anos", mas a função `sgs.get`
        # já busca no intervalo exato. Vou manter a busca direta e garantir que
        # o período de 10 anos seja considerado na lógica de cache ou na chamada,
        # se necessário. Por enquanto, a chamada direta é a mais eficiente.
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

# <<< ADICIONADO: NOVA FUNÇÃO PARA OBTER DADOS DO IBOVESPA >>>
@st.cache_data
def obter_dados_ibovespa(data_inicio: datetime, data_fim: datetime):
    """
    Obtém dados históricos do Ibovespa (^BVSP) usando yfinance e os normaliza.
    Garante que as colunas sejam de nível único e usa 'Close' como fonte.
    """
    ticker_ibovespa = "^BVSP"
    try:
        # Adiciona um dia à data final para garantir que o último dia seja incluído
        # yfinance é exclusivo no 'end' date. Usar auto_adjust=True para simplificar as colunas.
        dados_ibovespa = yf.download(ticker_ibovespa, start=data_inicio, end=data_fim + timedelta(days=1), progress=False, auto_adjust=True)

        if not dados_ibovespa.empty:
            # Resetar o índice para transformar 'Date' em coluna
            dados_ibovespa = dados_ibovespa.reset_index()

            # Renomear 'Date' para 'DT_COMPTC' e 'Close' para 'IBOV_Close'
            # Com auto_adjust=True, 'Close' já é o preço ajustado.
            dados_ibovespa = dados_ibovespa.rename(columns={'Date': 'DT_COMPTC', 'Close': 'IBOV_Close'})

            # Selecionar apenas as colunas necessárias
            dados_ibovespa = dados_ibovespa[['DT_COMPTC', 'IBOV_Close']]

            # Normalizar para que o primeiro valor da série seja 1.0
            if not dados_ibovespa.empty:
                primeiro_valor_ibov = dados_ibovespa['IBOV_Close'].iloc[0]
                dados_ibovespa['VL_IBOV_normalizado'] = dados_ibovespa['IBOV_Close'] / primeiro_valor_ibov
            else:
                dados_ibovespa['VL_IBOV_normalizado'] = pd.Series(dtype='float64') # Garante que a coluna exista

            return dados_ibovespa
        else:
            st.warning(f"⚠️ Nenhum dado encontrado para o Ibovespa ({ticker_ibovespa}) no período especificado.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao obter dados do Ibovespa: {str(e)}")
        return pd.DataFrame()
# <<< FIM DA FUNÇÃO IBOVESPA >>>

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

# Opção para mostrar CDI e IBOVESPA
st.sidebar.markdown("#### Indicadores de Comparação")
mostrar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)
mostrar_ibovespa = st.sidebar.checkbox("Comparar com Ibovespa", value=False) # Novo checkbox para Ibovespa

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

# Função para carregar dados
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

# Verificar se deve carregar os dados
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False

if carregar_button and cnpj_valido and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpj = cnpj_limpo
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada
    st.session_state.mostrar_cdi = mostrar_cdi # Salva o estado do checkbox
    st.session_state.mostrar_ibovespa = mostrar_ibovespa # Salva o estado do checkbox do Ibovespa

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

    ### 📊 Análises disponíveis:
    - Rentabilidade histórica e CAGR (com comparação ao CDI e Ibovespa)
    - Análise de risco (Drawdown, Volatilidade, VaR)
    - Evolução patrimonial e captação
    - Perfil de cotistas
    - Retornos em janelas móveis (com comparação ao CDI e Ibovespa)
    """)

    st.stop()

try:
    with st.spinner('🔄 Carregando dados...'):
        # Converte as datas de input do usuário para objetos datetime
        dt_ini_user = datetime.strptime(st.session_state.data_ini, '%Y%m%d')
        dt_fim_user = datetime.strptime(st.session_state.data_fim, '%Y%m%d')

        # 1. BAIXAR DADOS DO FUNDO (período ampliado para ffill)
        df_fundo_completo = carregar_dados_api(
            st.session_state.cnpj,
            st.session_state.data_ini,
            st.session_state.data_fim
        )
        df_fundo_completo = df_fundo_completo.sort_values('DT_COMPTC').reset_index(drop=True)

        # 2. OBTER DADOS DO CDI para o período EXATO solicitado pelo usuário
        df_cdi_raw = pd.DataFrame()
        if st.session_state.mostrar_cdi and BCB_DISPONIVEL:
            df_cdi_raw = obter_dados_cdi_real(dt_ini_user, dt_fim_user)
            if not df_cdi_raw.empty:
                df_cdi_raw = df_cdi_raw.sort_values('DT_COMPTC').reset_index(drop=True)

        # 3. OBTER DADOS DO IBOVESPA para o período EXATO solicitado pelo usuário
        df_ibov_raw = pd.DataFrame()
        if st.session_state.mostrar_ibovespa:
            df_ibov_raw = obter_dados_ibovespa(dt_ini_user, dt_fim_user)
            if not df_ibov_raw.empty:
                df_ibov_raw = df_ibov_raw.sort_values('DT_COMPTC').reset_index(drop=True)

        # 4. COMBINAR FUNDO, CDI E IBOVESPA
        # Criar um DataFrame de datas completo para garantir que todos os benchmarks e o fundo
        # sejam alinhados corretamente.
        all_dates = pd.Series(dtype='datetime64[ns]')
        if not df_fundo_completo.empty:
            all_dates = pd.concat([all_dates, df_fundo_completo['DT_COMPTC']])
        if not df_cdi_raw.empty:
            all_dates = pd.concat([all_dates, df_cdi_raw['DT_COMPTC']])
        if not df_ibov_raw.empty:
            all_dates = pd.concat([all_dates, df_ibov_raw['DT_COMPTC']])

        all_dates = all_dates.drop_duplicates().sort_values().reset_index(drop=True)
        df_final = pd.DataFrame({'DT_COMPTC': all_dates})

        # Merge com fundo
        df_final = pd.merge(df_final, df_fundo_completo, on='DT_COMPTC', how='left')

        # Merge com CDI se disponível
        if not df_cdi_raw.empty:
            df_final = pd.merge(df_final, df_cdi_raw[['DT_COMPTC', 'cdi', 'VL_CDI_normalizado']], on='DT_COMPTC', how='left')
        else:
            df_final.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado'] if col in df_final.columns], errors='ignore', inplace=True)

        # Merge com Ibovespa se disponível
        if not df_ibov_raw.empty:
            df_final = pd.merge(df_final, df_ibov_raw[['DT_COMPTC', 'IBOV_Close', 'VL_IBOV_normalizado']], on='DT_COMPTC', how='left')
        else:
            df_final.drop(columns=[col for col in ['IBOV_Close', 'VL_IBOV_normalizado'] if col in df_final.columns], errors='ignore', inplace=True)

        # Garante que o dataframe esteja ordenado por data
        df_final = df_final.sort_values('DT_COMPTC').reset_index(drop=True)

        # 5. Preencher valores ausentes para colunas do fundo e benchmarks com o último valor válido (forward-fill)
        fund_cols_to_ffill = ['VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST', 'CAPTC_DIA', 'RESG_DIA']
        for col in fund_cols_to_ffill:
            if col in df_final.columns:
                df_final[col] = df_final[col].ffill()

        if 'VL_CDI_normalizado' in df_final.columns:
            df_final['VL_CDI_normalizado'] = df_final['VL_CDI_normalizado'].ffill()
            if 'cdi' in df_final.columns: # Preenche o 'cdi' diário também, se necessário
                df_final['cdi'] = df_final['cdi'].ffill()

        if 'VL_IBOV_normalizado' in df_final.columns:
            df_final['VL_IBOV_normalizado'] = df_final['VL_IBOV_normalizado'].ffill()
            if 'IBOV_Close' in df_final.columns: # Preenche o 'IBOV_Close' também
                df_final['IBOV_Close'] = df_final['IBOV_Close'].ffill()

        # 6. Remover linhas onde VL_QUOTA ainda é NaN (fundo não existia ou não tinha dados mesmo após ffill)
        df_final.dropna(subset=['VL_QUOTA'], inplace=True)

        # 7. Filtrar o dataframe combinado para o período EXATO solicitado pelo usuário
        df = df_final[(df_final['DT_COMPTC'] >= dt_ini_user) & (df_final['DT_COMPTC'] <= dt_fim_user)].copy()

        # Verifica se o dataframe final está vazio após todas as operações
        if df.empty:
            st.error("❌ Não há dados disponíveis para o fundo no período selecionado após a combinação com os benchmarks ou o fundo não possui dados suficientes.")
            st.stop()

        # <<< ADICIONADO: Definir trading_days_in_period aqui >>>
        trading_days_in_year = 252 # Número de dias úteis em um ano para anualização
        num_days_in_period = (df['DT_COMPTC'].iloc[-1] - df['DT_COMPTC'].iloc[0]).days
        # Corrigido: trading_days_in_period deve ser o número de dias *úteis* no período
        # Uma aproximação é len(df) - 1, se df contiver apenas dias úteis.
        trading_days_in_period = len(df) - 1 if len(df) > 1 else 1 # Garante que não seja zero

        # 8. Re-normalizar a cota do fundo para começar em 1.0 (0% de rentabilidade) na primeira data do 'df' final
        primeira_cota_fundo = df['VL_QUOTA'].iloc[0]
        df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota_fundo) - 1) * 100

        # Processa e re-normaliza os dados do CDI para o 'df' final
        tem_cdi = False
        if st.session_state.mostrar_cdi and 'VL_CDI_normalizado' in df.columns and not df['VL_CDI_normalizado'].empty:
            # Re-normaliza o CDI para começar em 1.0 na primeira data do 'df' final
            first_cdi_normalized_value_in_period = df['VL_CDI_normalizado'].iloc[0]
            df['CDI_COTA'] = df['VL_CDI_normalizado'] / first_cdi_normalized_value_in_period
            df['CDI_NORM'] = (df['CDI_COTA'] - 1) * 100
            tem_cdi = True
        else:
            # Garante que colunas CDI sejam removidas se não forem solicitadas ou não estiverem disponíveis
            df.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado', 'CDI_COTA', 'CDI_NORM'] if col in df.columns], errors='ignore', inplace=True)

        # Processa e re-normaliza os dados do Ibovespa para o 'df' final
        tem_ibovespa = False
        if st.session_state.mostrar_ibovespa and 'VL_IBOV_normalizado' in df.columns and not df['VL_IBOV_normalizado'].empty:
            # Re-normaliza o Ibovespa para começar em 1.0 na primeira data do 'df' final
            first_ibov_normalized_value_in_period = df['VL_IBOV_normalizado'].iloc[0]
            df['IBOV_COTA'] = df['VL_IBOV_normalizado'] / first_ibov_normalized_value_in_period
            df['IBOV_NORM'] = (df['IBOV_COTA'] - 1) * 100
            tem_ibovespa = True
        else:
            # Garante que colunas Ibovespa sejam removidas se não forem solicitadas ou não estiverem disponíveis
            df.drop(columns=[col for col in ['IBOV_Close', 'VL_IBOV_normalizado', 'IBOV_COTA', 'IBOV_NORM'] if col in df.columns], errors='ignore', inplace=True)

    # 3. CALCULAR MÉTRICAS (agora usando o 'df' combinado e normalizado)
    df = df.sort_values('DT_COMPTC').reset_index(drop=True)

    # Métricas do fundo
    df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
    df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100
    df['Captacao_Liquida'] = df['CAPTC_DIA'] - df['RESG_DIA']
    df['Soma_Acumulada'] = df['Captacao_Liquida'].cumsum()
    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

    vol_window = 21
    df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()
    df['Volatilidade'] = df['Variacao_Perc'].rolling(vol_window).std() * np.sqrt(trading_days_in_year) * 100
    vol_hist = round(df['Variacao_Perc'].std() * np.sqrt(trading_days_in_year) * 100, 2)

    # CAGR - Cálculo conforme sua especificação: última cota fixa, cota inicial variável
    df['CAGR_Fundo'] = np.nan
    if tem_cdi:
        df['CAGR_CDI'] = np.nan
    if tem_ibovespa:
        df['CAGR_IBOV'] = np.nan

    if not df.empty and len(df) > trading_days_in_year:
        end_value_fundo = df['VL_QUOTA'].iloc[-1]
        if tem_cdi:
            end_value_cdi = df['CDI_COTA'].iloc[-1]
        if tem_ibovespa:
            end_value_ibov = df['IBOV_COTA'].iloc[-1]

        # O loop vai até o índice que é 'trading_days_in_year' antes do último.
        # Isso garante que o último ponto plotado corresponda a 252 dias.
        for i in range(len(df) - trading_days_in_year):
            start_value_fundo = df['VL_QUOTA'].iloc[i]
            cagr_fundo_calc = ((end_value_fundo / start_value_fundo)**(trading_days_in_year / (len(df) - 1 - i)) - 1) * 100
            df.loc[i + trading_days_in_year, 'CAGR_Fundo'] = cagr_fundo_calc

            if tem_cdi:
                start_value_cdi = df['CDI_COTA'].iloc[i]
                cagr_cdi_calc = ((end_value_cdi / start_value_cdi)**(trading_days_in_year / (len(df) - 1 - i)) - 1) * 100
                df.loc[i + trading_days_in_year, 'CAGR_CDI'] = cagr_cdi_calc

            if tem_ibovespa:
                start_value_ibov = df['IBOV_COTA'].iloc[i]
                cagr_ibov_calc = ((end_value_ibov / start_value_ibov)**(trading_days_in_year / (len(df) - 1 - i)) - 1) * 100
                df.loc[i + trading_days_in_year, 'CAGR_IBOV'] = cagr_ibov_calc

    # Calcula o CAGR médio para o período total de análise
    mean_cagr = df['CAGR_Fundo'].dropna().mean() if not df['CAGR_Fundo'].dropna().empty else np.nan

    # Excesso de Retorno Anualizado
    df['EXCESSO_RETORNO_ANUALIZADO_CDI'] = np.nan
    df['EXCESSO_RETORNO_ANUALIZADO_IBOV'] = np.nan

    if tem_cdi:
        df['EXCESSO_RETORNO_ANUALIZADO_CDI'] = df['CAGR_Fundo'] - df['CAGR_CDI']
    if tem_ibovespa:
        df['EXCESSO_RETORNO_ANUALIZADO_IBOV'] = df['CAGR_Fundo'] - df['CAGR_IBOV']

    # VaR (Value at Risk)
    # VaR Histórico (95% e 99%)
    var_95 = df['Variacao_Perc'].quantile(0.05) * 100 if not df['Variacao_Perc'].empty else np.nan
    var_99 = df['Variacao_Perc'].quantile(0.01) * 100 if not df['Variacao_Perc'].empty else np.nan

    # Cores para os gráficos
    color_primary = '#1a5f3f' # Verde escuro
    color_secondary = '#2d8659' # Verde médio
    color_accent = '#f0b429' # Amarelo
    color_cdi = '#007bff' # Azul para CDI
    color_ibovespa = '#dc3545' # Vermelho para Ibovespa
    color_danger = '#dc3545' # Vermelho para captação negativa

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Rentabilidade", "Risco", "Patrimônio e Captação", "Cotistas", "Janelas Móveis"])

    with tab1:
        st.subheader("Rentabilidade Histórica")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['VL_QUOTA_NORM'],
            mode='lines',
            name='Fundo',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
        ))

        if tem_cdi:
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['CDI_NORM'],
                mode='lines',
                name='CDI',
                line=dict(color=color_cdi, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
            ))

        if tem_ibovespa:
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['IBOV_NORM'],
                mode='lines',
                name='Ibovespa',
                line=dict(color=color_ibovespa, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
            ))

        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade Acumulada (%)",
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
        # Ajusta o range do eixo X para os dados de df
        fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("CAGR Anual")

        df_plot_cagr = df.dropna(subset=['CAGR_Fundo']).copy()

        if not df_plot_cagr.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_plot_cagr['DT_COMPTC'],
                y=df_plot_cagr['CAGR_Fundo'],
                mode='lines',
                name='Fundo',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR Fundo: %{y:.2f}%<extra></extra>'
            ))
            if tem_cdi:
                fig2.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=df_plot_cagr['CAGR_CDI'],
                    mode='lines',
                    name='CDI',
                    line=dict(color=color_cdi, width=2.5),
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR CDI: %{y:.2f}%<extra></extra>'
                ))
            if tem_ibovespa:
                fig2.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=df_plot_cagr['CAGR_IBOV'],
                    mode='lines',
                    name='Ibovespa',
                    line=dict(color=color_ibovespa, width=2.5),
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR Ibovespa: %{y:.2f}%<extra></extra>'
                ))

            fig2.update_layout(
                xaxis_title="Data",
                yaxis_title="CAGR Anual (%)",
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
            # Ajusta o range do eixo X para os dados de df_plot_cagr
            fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df_plot_cagr['DT_COMPTC'].min(), df_plot_cagr['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("⚠️ Não há dados suficientes para calcular o CAGR Anual (mínimo de 1 ano de dados).")

        st.subheader("Excesso de Retorno Anualizado")

        df_plot_excesso = df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO_CDI', 'EXCESSO_RETORNO_ANUALIZADO_IBOV'], how='all').copy()

        if not df_plot_excesso.empty:
            fig_excesso_retorno = go.Figure()

            if tem_cdi:
                fig_excesso_retorno.add_trace(go.Scatter(
                    x=df_plot_excesso['DT_COMPTC'],
                    y=df_plot_excesso['EXCESSO_RETORNO_ANUALIZADO_CDI'],
                    mode='lines',
                    name='Fundo vs CDI',
                    line=dict(color=color_primary, width=2.5),
                    fill='tozeroy',
                    fillcolor='rgba(26, 95, 63, 0.1)',
                    hovertemplate="Data: %{x|%d/%m/%Y}<br>Excesso vs CDI: %{y:.2f}%<extra></extra>"
                ))
            if tem_ibovespa:
                fig_excesso_retorno.add_trace(go.Scatter(
                    x=df_plot_excesso['DT_COMPTC'],
                    y=df_plot_excesso['EXCESSO_RETORNO_ANUALIZADO_IBOV'],
                    mode='lines',
                    name='Fundo vs Ibovespa',
                    line=dict(color=color_ibovespa, width=2.5, dash='dot'), # Linha pontilhada para diferenciar
                    fill='tozeroy',
                    fillcolor='rgba(220, 53, 69, 0.1)',
                    hovertemplate="Data: %{x|%d/%m/%Y}<br>Excesso vs Ibovespa: %{y:.2f}%<extra></extra>"
                ))

            fig_excesso_retorno.update_layout(
                xaxis_title="Data",
                yaxis_title="Excesso de Retorno Anualizado (%)",
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
            # Ajusta o range do eixo X para os dados de df_plot_excesso
            fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64, x_range=[df_plot_excesso['DT_COMPTC'].min(), df_plot_excesso['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig_excesso_retorno, use_container_width=True)
        else:
            st.warning("⚠️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado (mínimo de 1 ano de dados e benchmark selecionado).")

    with tab2: # Aba de Risco
        st.subheader("Análise de Risco")

        col_risk_1, col_risk_2, col_risk_3 = st.columns(3)
        with col_risk_1:
            st.metric("Volatilidade Histórica", f"{vol_hist:.2f}%" if not pd.isna(vol_hist) else "N/A")
        with col_risk_2:
            st.metric("VaR 95% (Diário)", f"{var_95:.2f}%" if not pd.isna(var_95) else "N/A")
        with col_risk_3:
            st.metric("VaR 99% (Diário)", f"{var_99:.2f}%" if not pd.isna(var_99) else "N/A")

        st.markdown("---")

        # Gráfico de Volatilidade
        st.subheader("Volatilidade Anualizada (Janela Móvel de 21 dias)")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Volatilidade'],
            mode='lines',
            name='Volatilidade Fundo',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
        ))
        fig_vol.update_layout(
            xaxis_title="Data",
            yaxis_title="Volatilidade Anualizada (%)",
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
        fig_vol = add_watermark_and_style(fig_vol, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig_vol, use_container_width=True)

        # <<< MOVIDO PARA A ABA DE RISCO >>>
        st.subheader("Drawdown Histórico")
        fig_drawdown = go.Figure()
        fig_drawdown.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Drawdown'],
            mode='lines',
            name='Drawdown Fundo',
            line=dict(color=color_danger, width=2.5),
            fill='tozeroy',
            fillcolor='rgba(220, 53, 69, 0.1)',
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
        ))
        fig_drawdown.update_layout(
            xaxis_title="Data",
            yaxis_title="Drawdown (%)",
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
        fig_drawdown = add_watermark_and_style(fig_drawdown, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig_drawdown, use_container_width=True)
        # <<< FIM DO GRÁFICO DE DRAWDOWN MOVIDO >>>

        st.markdown("---")
        st.subheader("Métricas de Risco-Retorno")

        # Inicializa as variáveis para evitar NameError
        annualized_fund_return = np.nan
        annualized_fund_volatility = np.nan
        annualized_downside_volatility = np.nan
        max_drawdown_value = np.nan
        ulcer_index = np.nan

        # Calcula o retorno anualizado do fundo para o período
        if not df['VL_QUOTA'].empty and len(df) > 1:
            total_fund_return = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1
            annualized_fund_return = (1 + total_fund_return)**(trading_days_in_year / trading_days_in_period) - 1 if trading_days_in_period > 0 else 0

        # Volatilidade anualizada do fundo
        annualized_fund_volatility = df['Variacao_Perc'].std() * np.sqrt(trading_days_in_year) if not df['Variacao_Perc'].empty else np.nan

        # Max Drawdown (já calculada como df['Drawdown'].min(), convertida para decimal)
        max_drawdown_value = df['Drawdown'].min() / 100 if not df['Drawdown'].empty else np.nan

        # CAGR do fundo (já calculada como mean_cagr, convertida para decimal)
        cagr_fund_decimal = mean_cagr / 100 if not pd.isna(mean_cagr) else np.nan

        # Ulcer Index
        drawdown_series = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1)
        squared_drawdowns = drawdown_series**2
        if not squared_drawdowns.empty and squared_drawdowns.mean() > 0:
            ulcer_index = np.sqrt(squared_drawdowns.mean())
        else:
            ulcer_index = np.nan

        # Downside Volatility
        downside_returns = df['Variacao_Perc'][df['Variacao_Perc'] < 0]
        if not downside_returns.empty:
            annualized_downside_volatility = downside_returns.std() * np.sqrt(trading_days_in_year)
        else:
            annualized_downside_volatility = np.nan

        # Inicializa as métricas para CDI e Ibovespa
        sharpe_ratio_cdi, sortino_ratio_cdi, information_ratio_cdi = np.nan, np.nan, np.nan
        calmar_ratio_cdi, sterling_ratio_cdi, martin_ratio_cdi = np.nan, np.nan, np.nan
        sharpe_ratio_ibov, sortino_ratio_ibov, information_ratio_ibov = np.nan, np.nan, np.nan

        # --- Cálculos para CDI ---
        if tem_cdi and 'cdi' in df.columns and 'CDI_COTA' in df.columns:
            total_cdi_return = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0]) - 1
            annualized_cdi_return = (1 + total_cdi_return)**(trading_days_in_year / trading_days_in_period) - 1 if trading_days_in_period > 0 else 0

            # Tracking Error vs CDI
            df['Variacao_Perc_CDI'] = df['cdi'] / 100 # Taxa diária do CDI
            excess_daily_returns_cdi = df['Variacao_Perc'] - df['Variacao_Perc_CDI']
            tracking_error_cdi = excess_daily_returns_cdi.std() * np.sqrt(trading_days_in_year) if not excess_daily_returns_cdi.empty else np.nan

            if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(max_drawdown_value) and max_drawdown_value != 0:
                calmar_ratio_cdi = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value)
                sterling_ratio_cdi = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value) # Simplificado para Max Drawdown

            if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(ulcer_index) and ulcer_index != 0:
                martin_ratio_cdi = (cagr_fund_decimal - annualized_cdi_return) / ulcer_index

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0:
                sharpe_ratio_cdi = (annualized_fund_return - annualized_cdi_return) / annualized_fund_volatility

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0:
                sortino_ratio_cdi = (annualized_fund_return - annualized_cdi_return) / annualized_downside_volatility

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(tracking_error_cdi) and tracking_error_cdi != 0:
                information_ratio_cdi = (annualized_fund_return - annualized_cdi_return) / tracking_error_cdi

        # --- Cálculos para Ibovespa ---
        if tem_ibovespa and 'IBOV_Close' in df.columns and 'IBOV_COTA' in df.columns:
            # Volatilidade anualizada do Ibovespa (para o Sharpe/Sortino do Ibovespa)
            df['Variacao_Perc_IBOV'] = df['IBOV_Close'].pct_change()
            annualized_ibov_volatility = df['Variacao_Perc_IBOV'].std() * np.sqrt(trading_days_in_year) if not df['Variacao_Perc_IBOV'].empty else np.nan

            total_ibov_return = (df['IBOV_COTA'].iloc[-1] / df['IBOV_COTA'].iloc[0]) - 1
            annualized_ibov_return = (1 + total_ibov_return)**(trading_days_in_year / trading_days_in_period) - 1 if trading_days_in_period > 0 else 0

            # Tracking Error vs Ibovespa
            excess_daily_returns_ibov = df['Variacao_Perc'] - df['Variacao_Perc_IBOV']
            tracking_error_ibov = excess_daily_returns_ibov.std() * np.sqrt(trading_days_in_year) if not excess_daily_returns_ibov.empty else np.nan

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_ibov_return) and not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0:
                sharpe_ratio_ibov = (annualized_fund_return - annualized_ibov_return) / annualized_fund_volatility

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_ibov_return) and not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0:
                sortino_ratio_ibov = (annualized_fund_return - annualized_ibov_return) / annualized_downside_volatility

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_ibov_return) and not pd.isna(tracking_error_ibov) and tracking_error_ibov != 0:
                information_ratio_ibov = (annualized_fund_return - annualized_ibov_return) / tracking_error_ibov

        # --- Exibição dos Cards e Explicações ---
        if tem_cdi or tem_ibovespa:
            st.markdown("#### RISCO MEDIDO PELA VOLATILIDADE:")

            # Criar um DataFrame para as métricas de risco-retorno
            metrics_data = {
                "Métrica": ["Sharpe Ratio", "Sortino Ratio", "Information Ratio", "Treynor Ratio"],
                "Fundo vs CDI": [
                    f"{sharpe_ratio_cdi:.2f}" if not pd.isna(sharpe_ratio_cdi) else "N/A",
                    f"{sortino_ratio_cdi:.2f}" if not pd.isna(sortino_ratio_cdi) else "N/A",
                    f"{information_ratio_cdi:.2f}" if not pd.isna(information_ratio_cdi) else "N/A",
                    "Não Calculável (Beta)"
                ]
            }
            if tem_ibovespa:
                metrics_data["Fundo vs Ibovespa"] = [
                    f"{sharpe_ratio_ibov:.2f}" if not pd.isna(sharpe_ratio_ibov) else "N/A",
                    f"{sortino_ratio_ibov:.2f}" if not pd.isna(sortino_ratio_ibov) else "N/A",
                    f"{information_ratio_ibov:.2f}" if not pd.isna(information_ratio_ibov) else "N/A",
                    "Não Calculável (Beta)"
                ]

            df_metrics_vol = pd.DataFrame(metrics_data)
            st.table(df_metrics_vol) # Exibe como tabela

            st.info("""
            **Sharpe Ratio:** Mede o excesso de retorno do fundo (acima do benchmark) por unidade de **volatilidade total** (risco). Quanto maior o Sharpe, melhor o retorno para o nível de risco assumido.
            *   **Interpretação Geral:**
                *   **< 1.0:** Subótimo, o retorno não compensa adequadamente o risco.
                *   **1.0 - 1.99:** Bom, o fundo gera um bom retorno para o risco.
                *   **2.0 - 2.99:** Muito Bom, excelente retorno ajustado ao risco.
                *   **≥ 3.0:** Excepcional, performance muito consistente.
            """)
            st.info("""
            **Sortino Ratio:** Similar ao Sharpe, mas foca apenas na **volatilidade de baixa** (downside volatility). Ele mede o excesso de retorno por unidade de risco de queda. É útil para investidores que se preocupam mais com perdas do que com a volatilidade geral.
            *   **Interpretação Geral:**
                *   **< 0.0:** Retorno não cobre o risco de queda.
                *   **0.0 - 1.0:** Aceitável, o fundo gera retorno positivo para o risco de queda.
                *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de perdas.
            """)
            st.info("""
            **Information Ratio:** Mede a capacidade do gestor de gerar retornos acima de um benchmark (aqui, o CDI ou Ibovespa), ajustado pelo **tracking error** (risco de desvio em relação ao benchmark). Um valor alto indica que o gestor consistentemente superou o benchmark com um risco de desvio razoável.
            *   **Interpretação Geral:**
                *   **< 0.0:** O fundo está consistentemente abaixo do benchmark.
                *   **0.0 - 0.5:** Habilidade modesta em superar o benchmark.
                *   **0.5 - 1.0:** Boa habilidade e consistência em superar o benchmark.
                *   **> 1.0:** Excelente habilidade e forte superação consistente do benchmark.
            """)
            st.info("""
            **Treynor Ratio:** Mede o excesso de retorno por unidade de **risco sistemático (Beta)**. O Beta mede a sensibilidade do fundo aos movimentos do mercado.
            *   **Interpretação:** Um valor mais alto é preferível. É mais útil para comparar fundos com Betas semelhantes.
            *   **Observação:** *Não é possível calcular este índice sem dados de um índice de mercado (benchmark) para determinar o Beta do fundo. Para o Ibovespa, seria necessário calcular o Beta do fundo em relação ao Ibovespa.*
            """)

            st.markdown("#### RISCO MEDIDO PELO DRAWDOWN:")

            metrics_data_dd = {
                "Métrica": ["Calmar Ratio", "Sterling Ratio", "Ulcer Index", "Martin Ratio"],
                "Fundo vs CDI": [
                    f"{calmar_ratio_cdi:.2f}" if not pd.isna(calmar_ratio_cdi) else "N/A",
                    f"{sterling_ratio_cdi:.2f}" if not pd.isna(sterling_ratio_cdi) else "N/A",
                    f"{ulcer_index:.2f}" if not pd.isna(ulcer_index) else "N/A",
                    f"{martin_ratio_cdi:.2f}" if not pd.isna(martin_ratio_cdi) else "N/A"
                ]
            }
            # Adiciona coluna para Ibovespa se selecionado
            if tem_ibovespa:
                metrics_data_dd["Fundo vs Ibovespa"] = [
                    "N/A", # Calmar Ratio vs Ibovespa - Requer CAGR vs Ibovespa
                    "N/A", # Sterling Ratio vs Ibovespa - Requer CAGR vs Ibovespa
                    f"{ulcer_index:.2f}" if not pd.isna(ulcer_index) else "N/A", # Ulcer Index é do fundo, não muda com benchmark
                    "N/A" # Martin Ratio vs Ibovespa - Requer CAGR vs Ibovespa
                ]
            df_metrics_dd = pd.DataFrame(metrics_data_dd)
            st.table(df_metrics_dd) # Exibe como tabela

            st.info("""
            **Calmar Ratio:** Mede o retorno ajustado ao risco, comparando o **CAGR** (retorno anualizado) do fundo com o seu **maior drawdown** (maior queda). Um valor mais alto indica que o fundo gerou bons retornos sem grandes perdas.
            *   **Interpretação Geral:**
                *   **< 0.0:** Retorno negativo ou drawdown muito grande.
                *   **0.0 - 0.5:** Aceitável, mas com espaço para melhoria.
                *   **0.5 - 1.0:** Bom, o fundo gerencia bem o risco de drawdown.
                *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de grandes quedas.
            """)
            st.info("""
            **Sterling Ratio:** Similar ao Calmar, avalia o retorno ajustado ao risco em relação ao drawdown. Geralmente, compara o retorno anualizado com a média dos piores drawdowns. *Nesta análise, para simplificar, utilizamos o maior drawdown como referência.* Um valor mais alto é preferível.
            *   **Interpretação Geral:**
                *   **< 0.0:** Retorno negativo ou drawdown muito grande.
                *   **0.0 - 0.5:** Aceitável, mas com espaço para melhoria.
                *   **0.5 - 1.0:** Bom, o fundo gerencia bem o risco de drawdown.
                *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de grandes quedas.
            """)
            st.info("""
            **Ulcer Index:** Mede a profundidade e a duração dos drawdowns (quedas). Quanto menor o índice, menos dolorosas e mais curtas foram as quedas do fundo. É uma medida de risco que foca na "dor" do investidor.
            *   **Interpretação Geral:**
                *   **< 1.0:** Baixo risco, fundo relativamente estável.
                *   **1.0 - 2.0:** Risco moderado, com quedas mais frequentes ou profundas.
                *   **> 2.0:** Alto risco, fundo com quedas significativas e/ou duradouras.
            """)
            st.info("""
            **Martin Ratio:** Avalia o retorno ajustado ao risco dividindo o excesso de retorno anualizado (acima do CDI) pelo **Ulcer Index**. Um valor mais alto indica um melhor desempenho em relação ao risco de drawdown.
            *   **Interpretação Geral:**
                *   **< 0.0:** O fundo não compensa o risco de drawdown.
                *   **0.0 - 1.0:** Aceitável, o fundo gera retorno positivo para o risco de drawdown.
                *   **0.5 - 1.0:** Bom, o fundo entrega um bom retorno considerando a "dor" dos drawdowns.
                *   **> 1.0:** Muito Bom, excelente retorno em relação à "dor" dos drawdowns.
            """)

            st.markdown("""
            ---
            **Observação Importante sobre as Interpretações:**
            Os intervalos e classificações acima são **diretrizes gerais** baseadas em práticas comuns do mercado financeiro e literaturas de investimento. A interpretação de qualquer métrica de risco-retorno deve sempre considerar o **contexto específico do fundo** (estratégia, classe de ativos, objetivo), as **condições de mercado** no período analisado e o **perfil de risco do investidor**. Não há um "número mágico" que sirva para todos os casos.
            """)

        elif not tem_cdi and not tem_ibovespa:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' e/ou 'Comparar com Ibovespa' na barra lateral para visualizar as Métricas de Risco-Retorno.")
        else:
            st.warning("⚠️ Não há dados suficientes para calcular as Métricas de Risco-Retorno (mínimo de 1 ano de dados).")

    with tab3:
        st.subheader("Patrimônio e Captação Líquida")

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
                # Adiciona o texto nas barras
                text=df_monthly['Captacao_Liquida'].apply(lambda x: format_brl(x)),
                textposition='outside', # Posição do texto fora da barra
                textfont=dict(color='black', size=12), # Cor e tamanho da fonte do texto
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
            font=dict(family="Inter, sans-serif"),
            yaxis=dict(tickformat="$,.0f", range=[df_monthly['Captacao_Liquida'].min() * 1.2, df_monthly['Captacao_Liquida'].max() * 1.2]) # Ajusta o range para o texto
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
                if tem_cdi:
                    df_returns[f'CDI_{nome}'] = df_returns['CDI_COTA'] / df_returns['CDI_COTA'].shift(dias) - 1
                if tem_ibovespa: # Novo para Ibovespa
                    df_returns[f'IBOV_{nome}'] = df_returns['IBOV_COTA'] / df_returns['IBOV_COTA'].shift(dias) - 1
            else:
                df_returns[f'FUNDO_{nome}'] = np.nan
                if tem_cdi:
                    df_returns[f'CDI_{nome}'] = np.nan
                if tem_ibovespa:
                    df_returns[f'IBOV_{nome}'] = np.nan

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

            # Retorno do Ibovespa (se disponível)
            if tem_ibovespa:
                fig9.add_trace(go.Scatter(
                    x=df_returns['DT_COMPTC'],
                    y=df_returns[f'IBOV_{janela_selecionada}'],
                    mode='lines',
                    name=f"Retorno do Ibovespa — {janela_selecionada}",
                    line=dict(width=2.5, color=color_ibovespa),
                    hovertemplate="<b>Retorno do Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
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
        st.subheader("Consistência em Janelas Móveis")

        if tem_cdi or tem_ibovespa:
            consistency_data = []
            for nome, dias in janelas.items():
                fund_col = f'FUNDO_{nome}'
                cdi_col = f'CDI_{nome}'
                ibov_col = f'IBOV_{nome}' # Nova coluna para Ibovespa

                if fund_col in df_returns.columns:
                    temp_df = df_returns[[fund_col]].dropna()
                    if not temp_df.empty:
                        if tem_cdi and cdi_col in df_returns.columns:
                            temp_df_cdi = df_returns[[fund_col, cdi_col]].dropna()
                            outperformed_cdi_count = (temp_df_cdi[fund_col] > temp_df_cdi[cdi_col]).sum()
                            total_comparisons_cdi = len(temp_df_cdi)
                            consistency_cdi_percentage = (outperformed_cdi_count / total_comparisons_cdi) * 100 if total_comparisons_cdi > 0 else np.nan
                        else:
                            consistency_cdi_percentage = np.nan

                        if tem_ibovespa and ibov_col in df_returns.columns:
                            temp_df_ibov = df_returns[[fund_col, ibov_col]].dropna()
                            outperformed_ibov_count = (temp_df_ibov[fund_col] > temp_df_ibov[ibov_col]).sum()
                            total_comparisons_ibov = len(temp_df_ibov)
                            consistency_ibov_percentage = (outperformed_ibov_count / total_comparisons_ibov) * 100 if total_comparisons_ibov > 0 else np.nan
                        else:
                            consistency_ibov_percentage = np.nan

                        consistency_data.append({
                            'Janela': nome.split(' ')[0],
                            'Consistencia vs CDI': consistency_cdi_percentage,
                            'Consistencia vs Ibovespa': consistency_ibov_percentage
                        })
                    else:
                        consistency_data.append({
                            'Janela': nome.split(' ')[0],
                            'Consistencia vs CDI': np.nan,
                            'Consistencia vs Ibovespa': np.nan
                        })
                else:
                    consistency_data.append({
                        'Janela': nome.split(' ')[0],
                        'Consistencia vs CDI': np.nan,
                        'Consistencia vs Ibovespa': np.nan
                    })

            df_consistency = pd.DataFrame(consistency_data)
            df_consistency.dropna(subset=['Consistencia vs CDI', 'Consistencia vs Ibovespa'], how='all', inplace=True)

            if not df_consistency.empty:
                fig_consistency = go.Figure()

                if tem_cdi:
                    fig_consistency.add_trace(go.Bar(
                        x=df_consistency['Janela'],
                        y=df_consistency['Consistencia vs CDI'],
                        name='vs CDI',
                        marker_color=color_primary,
                        text=df_consistency['Consistencia vs CDI'].apply(lambda x: f'{x:.2f}%' if not pd.isna(x) else ''),
                        textposition='outside',
                        textfont=dict(color='black', size=12),
                        hovertemplate='<b>Janela:</b> %{x}<br><b>Consistência vs CDI:</b> %{y:.2f}%<extra></extra>'
                    ))
                if tem_ibovespa:
                    fig_consistency.add_trace(go.Bar(
                        x=df_consistency['Janela'],
                        y=df_consistency['Consistencia vs Ibovespa'],
                        name='vs Ibovespa',
                        marker_color=color_ibovespa,
                        text=df_consistency['Consistencia vs Ibovespa'].apply(lambda x: f'{x:.2f}%' if not pd.isna(x) else ''),
                        textposition='outside',
                        textfont=dict(color='black', size=12),
                        hovertemplate='<b>Janela:</b> %{x}<br><b>Consistência vs Ibovespa:</b> %{y:.2f}%<extra></extra>'
                    ))

                fig_consistency.update_layout(
                    xaxis_title="Janela (meses)",
                    yaxis_title="Percentual de Superação do Benchmark (%)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Inter, sans-serif"),
                    yaxis=dict(range=[0, 110], ticksuffix="%"), # Aumenta o range superior para dar mais espaço ao texto
                    barmode='group', # Para barras lado a lado
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                fig_consistency = add_watermark_and_style(fig_consistency, logo_base64, x_autorange=True)
                st.plotly_chart(fig_consistency, use_container_width=True)
            else:
                st.warning("⚠️ Não há dados suficientes para calcular a Consistência em Janelas Móveis.")
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' e/ou 'Comparar com Ibovespa' na barra lateral para visualizar a Consistência em Janelas Móveis.")

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
