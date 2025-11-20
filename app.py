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

# NOVO: Importar biblioteca para obter dados do Ibovespa
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

# CSS customizado com espaçamentos reduzidos na sidebar e fonte Inter (mantido como estava)
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
       -color: rgba(139, 168, 136, 0.5) !important;
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
        ],
        # Padroniza a legenda para todos os gráficos
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
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
        # A memória do usuário indica "intervalos de 10 anos".
        # A biblioteca `bcb` já lida com o `start` e `end` diretamente,
        # mas para garantir que o cache seja eficiente para períodos maiores,
        # podemos buscar um período um pouco maior e depois filtrar.
        # No entanto, a chamada direta com `start` e `end` é a mais precisa para o período solicitado.
        # A lógica de "10 anos" pode ser mais relevante para o cache interno da função,
        # mas a chamada externa deve ser para o período exato.
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

# NOVO: FUNÇÃO PARA OBTER DADOS DO IBOVESPA
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
        end_date = data_fim + pd.DateOffset(days=1) # Ajuste para yfinance

        df_ibovespa = yf.download('^BVSP', start=start_date, end=end_date, progress=False)

        if df_ibovespa.empty:
            return pd.DataFrame()

        # NOVO: Achata os cabeçalhos multi-nível, se existirem
        # Isso garante que teremos apenas um nível de cabeçalho
        if isinstance(df_ibovespa.columns, pd.MultiIndex):
            df_ibovespa.columns = ['_'.join(col).strip() for col in df_ibovespa.columns.values]

        # Transforma o índice em coluna
        df_ibovespa = df_ibovespa.reset_index()

        # NOVO: Lógica para identificar a coluna de fechamento, seja 'Close', 'Close_' ou 'Close_^BVSP'
        close_col_options = ['Close', 'Close_', 'Close_^BVSP'] # Adicionado 'Close_'
        selected_close_col = None
        for col_option in close_col_options:
            if col_option in df_ibovespa.columns:
                selected_close_col = col_option
                break

        if selected_close_col is None:
            st.error("❌ Não foi possível encontrar a coluna de fechamento do Ibovespa ('Close', 'Close_' ou 'Close_^BVSP').")
            return pd.DataFrame()

        # Altera o nome da coluna para DT_COMPTC e usa a coluna de fechamento identificada
        df_ibovespa = df_ibovespa.rename(columns={'Date': 'DT_COMPTC', selected_close_col: 'IBOV'})

        # Garante tipo datetime
        df_ibovespa['DT_COMPTC'] = pd.to_datetime(df_ibovespa['DT_COMPTC'])

        # Mantém apenas as colunas relevantes
        df_ibovespa = df_ibovespa[['DT_COMPTC', 'IBOV']].copy()

        # Ordenar
        df_ibovespa = df_ibovespa.sort_values('DT_COMPTC').reset_index(drop=True)

        return df_ibovespa

    except Exception as e:
        st.error(f"❌ Erro ao obter dados do Ibovespa: {str(e)}")
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

# Opção para mostrar CDI e Ibovespa
st.sidebar.markdown("#### Indicadores de Comparação")
mostrar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)
mostrar_ibov = st.sidebar.checkbox("Comparar com Ibovespa", value=False) # NOVO

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
    st.session_state.mostrar_ibov = mostrar_ibov # NOVO: Salva o estado do checkbox do Ibovespa

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

        # 2a. OBTER DADOS DO CDI para o período EXATO solicitado pelo usuário
        df_cdi_raw = pd.DataFrame()
        if st.session_state.mostrar_cdi and BCB_DISPONIVEL:
            df_cdi_raw = obter_dados_cdi_real(dt_ini_user, dt_fim_user)
            if not df_cdi_raw.empty:
                df_cdi_raw = df_cdi_raw.sort_values('DT_COMPTC').reset_index(drop=True)

        # 2b. NOVO: OBTER DADOS DO IBOVESPA para o período EXATO solicitado pelo usuário
        df_ibov_raw = pd.DataFrame()
        if st.session_state.mostrar_ibov and YF_DISPONIVEL:
            df_ibov_raw = obter_dados_ibov(dt_ini_user, dt_fim_user)
            if not df_ibov_raw.empty:
                df_ibov_raw = df_ibov_raw.sort_values('DT_COMPTC').reset_index(drop=True)

        # 3. COMBINAR FUNDO, CDI E IBOVESPA
        # Começa com o dataframe do fundo
        df_final = df_fundo_completo.copy()

        # Adiciona CDI se disponível
        if not df_cdi_raw.empty:
            df_final = df_final.merge(df_cdi_raw[['DT_COMPTC', 'cdi', 'VL_CDI_normalizado']], on='DT_COMPTC', how='left')
        else:
            df_final.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado'] if col in df_final.columns], errors='ignore', inplace=True)

        # Adiciona Ibovespa se disponível
        if not df_ibov_raw.empty:
            df_final = df_final.merge(df_ibov_raw[['DT_COMPTC', 'IBOV']], on='DT_COMPTC', how='left')
        else:
            df_final.drop(columns=[col for col in ['IBOV'] if col in df_final.columns], errors='ignore', inplace=True)

        # Garante que o dataframe esteja ordenado por data
        df_final = df_final.sort_values('DT_COMPTC').reset_index(drop=True)

        # 4. Preencher valores ausentes para colunas do fundo com o último valor válido (forward-fill)
        fund_cols_to_ffill = ['VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST', 'CAPTC_DIA', 'RESG_DIA']
        for col in fund_cols_to_ffill:
            if col in df_final.columns:
                df_final[col] = df_final[col].ffill()

        # NOVO: ffill do Ibovespa para manter série contínua nos dias úteis do fundo
        if 'IBOV' in df_final.columns:
            df_final['IBOV'] = df_final['IBOV'].ffill()

        # 5. Remover linhas onde VL_QUOTA ainda é NaN (fundo não existia ou não tinha dados mesmo após ffill)
        df_final.dropna(subset=['VL_QUOTA'], inplace=True)

        # 6. Filtrar o dataframe combinado para o período EXATO solicitado pelo usuário
        df = df_final[(df_final['DT_COMPTC'] >= dt_ini_user) & (df_final['DT_COMPTC'] <= dt_fim_user)].copy()

        # Verifica se o dataframe final está vazio após todas as operações
        if df.empty:
            st.error("❌ Não há dados disponíveis para o fundo no período selecionado após a combinação com os indicadores ou o fundo não possui dados suficientes.")
            st.stop()

        # 7. Re-normalizar a cota do fundo para começar em 1.0 (0% de rentabilidade) na primeira data do 'df' final
        primeira_cota_fundo = df['VL_QUOTA'].iloc[0]
        df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota_fundo) - 1) * 100

        # Processa e re-normaliza os dados do CDI para o 'df' final
        tem_cdi = False
        if st.session_state.mostrar_cdi and 'VL_CDI_normalizado' in df.columns and not df['VL_CDI_normalizado'].isna().all():
            first_cdi_normalized_value_in_period = df['VL_CDI_normalizado'].iloc[0]
            df['CDI_COTA'] = df['VL_CDI_normalizado'] / first_cdi_normalized_value_in_period
            df['CDI_NORM'] = (df['CDI_COTA'] - 1) * 100
            tem_cdi = True
        else:
            df.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado', 'CDI_COTA', 'CDI_NORM'] if col in df.columns], errors='ignore', inplace=True)

        # NOVO: Processa e re-normaliza os dados do Ibovespa
        tem_ibov = False
        if st.session_state.mostrar_ibov and 'IBOV' in df.columns and not df['IBOV'].isna().all():
            primeira_cota_ibov = df['IBOV'].iloc[0]
            df['IBOV_COTA'] = df['IBOV'] / primeira_cota_ibov
            df['IBOV_NORM'] = (df['IBOV_COTA'] - 1) * 100
            tem_ibov = True
        else:
            df.drop(columns=[col for col in ['IBOV', 'IBOV_COTA', 'IBOV_NORM'] if col in df.columns], errors='ignore', inplace=True)

        # A partir daqui segue o restante do seu código original

        # TRADING DAYS POR ANO
        trading_days_in_year = 252

        # Cálculo de Drawdown do Fundo
        df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
        df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100

        # Cálculo de rentabilidade diária do fundo
        df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()

        # Volatilidade móvel
        vol_window = 21
        df['Volatilidade'] = df['Variacao_Perc'].rolling(window=vol_window).std() * np.sqrt(trading_days_in_year) * 100
        vol_hist = df['Variacao_Perc'].std() * np.sqrt(trading_days_in_year) * 100 if not df['Variacao_Perc'].empty else 0

        # Cálculo de CAGR diário do fundo (para cada data considerando 252 dias úteis antes)
        df['CAGR_Fundo'] = np.nan
        for i in range(len(df)):
            if i >= trading_days_in_year - 1:
                initial_value = df['VL_QUOTA'].iloc[i - (trading_days_in_year - 1)]
                end_value = df['VL_QUOTA'].iloc[i]
                if initial_value > 0:
                    df.loc[i, 'CAGR_Fundo'] = ((end_value / initial_value) ** (trading_days_in_year / trading_days_in_year) - 1) * 100

        # Se houver CDI, calcula CAGR do CDI
        if tem_cdi and 'CDI_COTA' in df.columns:
            df['CAGR_CDI'] = np.nan
            for i in range(len(df)):
                if i >= trading_days_in_year - 1:
                    initial_value_cdi = df['CDI_COTA'].iloc[i - (trading_days_in_year - 1)]
                    if initial_value_cdi > 0:
                        end_value_cdi = df['CDI_COTA'].iloc[i]
                        df.loc[i, 'CAGR_CDI'] = ((end_value_cdi / initial_value_cdi) ** (trading_days_in_year / trading_days_in_year) - 1) * 100

        # Se houver Ibovespa, calcula CAGR do Ibovespa
        if tem_ibov and 'IBOV_COTA' in df.columns:
            df['CAGR_IBOV'] = np.nan
            for i in range(len(df)):
                if i >= trading_days_in_year - 1:
                    initial_value_ibov = df['IBOV_COTA'].iloc[i - (trading_days_in_year - 1)]
                    if initial_value_ibov > 0:
                        end_value_ibov = df['IBOV_COTA'].iloc[i]
                        df.loc[i, 'CAGR_IBOV'] = ((end_value_ibov / initial_value_ibov) ** (trading_days_in_year / trading_days_in_year) - 1) * 100

        # Calcular CAGR médio para o card de métricas (baseado na nova coluna CAGR_Fundo)
        mean_cagr = df['CAGR_Fundo'].mean() if 'CAGR_Fundo' in df.columns else 0
        if pd.isna(mean_cagr):
            mean_cagr = 0

        # Excesso de Retorno Anualizado (definido depois, na seção de risco-retorno, com o benchmark escolhido)

        # VaR
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

        # Cores (mantidas)
        color_primary = '#1a5f3f'
        color_secondary = '#6b9b7f'
        color_danger = '#dc3545'
        color_cdi = '#000000'
        color_ibov = '#007bff'

        # Cards de métricas principais
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Patrimônio Líquido", format_brl(df['VL_PATRIM_LIQ'].iloc[-1]))
        with col2:
            st.metric("Rentabilidade Acumulada", fmt_pct_port(df['VL_QUOTA_NORM'].iloc[-1] / 100))
        with col3:
            st.metric("CAGR Médio", fmt_pct_port(mean_cagr / 100))
        with col4:
            st.metric("Max Drawdown", fmt_pct_port(df['Drawdown'].min() / 100))
        with col5:
            st.metric("Vol. Histórica", fmt_pct_port(vol_hist/100))

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Rentabilidade", "Risco", "Patrimônio e Captação",
            "Cotistas", "Janelas Móveis"
        ])

        # -------------------------------- TAB 1 --------------------------------
        with tab1:
            st.subheader("Rentabilidade Histórica")

            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_QUOTA_NORM'],
                mode='lines',
                name='Fundo',
                line=dict(color=color_primary, width=2.5),
                fill='tozeroy',
                fillcolor='rgba(26, 95, 63, 0.1)',
                hovertemplate='<b>Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
            ))

            if tem_cdi:
                fig1.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['CDI_NORM'],
                    mode='lines',
                    name='CDI',
                    line=dict(color=color_cdi, width=2.5),
                    hovertemplate='<b>CDI</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
                ))

            if tem_ibov:
                fig1.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['IBOV_NORM'],
                    mode='lines',
                    name='Ibovespa',
                    line=dict(color=color_ibov, width=2.5),
                    hovertemplate='<b>Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
                ))

            fig1.update_layout(
                xaxis_title="Data",
                yaxis_title="Rentabilidade (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig1, use_containerwidth=True)

            st.subheader("CAGR Anual por Dia de Aplicação")

            fig2 = go.Figure()
            df_plot_cagr = df.dropna(subset=['CAGR_Fundo']).copy()

            if not df_plot_cagr.empty:
                fig2.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=df_plot_cagr['CAGR_Fundo'],
                    mode='lines',
                    name='CAGR do Fundo',
                    line=dict(color=color_primary, width=2.5),
                    hovertemplate='<b>CAGR do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
                ))

                fig2.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=[mean_cagr] * len(df_plot_cagr),
                    mode='lines',
                    line=dict(dash='dash', color=color_secondary, width=2),
                    name=f'CAGR Médio ({mean_cagr:.2f}%)'
                ))

                if tem_cdi and 'CAGR_CDI' in df_plot_cagr.columns:
                    fig2.add_trace(go.Scatter(
                        x=df_plot_cagr['DT_COMPTC'],
                        y=df_plot_cagr['CAGR_CDI'],
                        mode='lines',
                        name='CAGR do CDI',
                        line=dict(color=color_cdi, width=2.5),
                        hovertemplate='<b>CAGR do CDI</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
                    ))

                if tem_ibov and 'CAGR_IBOV' in df_plot_cagr.columns:
                    fig2.add_trace(go.Scatter(
                        x=df_plot_cagr['DT_COMPTC'],
                        y=df_plot_cagr['CAGR_IBOV'],
                        mode='lines',
                        name='CAGR do Ibovespa',
                        line=dict(color=color_ibov, width=2.5),
                        hovertemplate='<b>CAGR do Ibovespa</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
                    ))
            else:
                st.warning("⚠️ Não há dados suficientes para calcular o CAGR (mínimo de 1 ano de dados).")

            fig2.update_layout(
                xaxis_title="Data",
                yaxis_title="CAGR (% a.a)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            if not df_plot_cagr.empty:
                fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df_plot_cagr['DT_COMPTC'].min(), df_plot_cagr['DT_COMPTC'].max()], x_autorange=False)
            else:
                fig2 = add_watermark_and_style(fig2, logo_base64)
            st.plotly_chart(fig2, use_containerwidth=True)

            # Excesso de Retorno Anualizado
            st.subheader("Excesso de Retorno Anualizado")

            df['EXCESSO_RETORNO_ANUALIZADO'] = np.nan

            if (tem_cdi and not tem_ibov) or (tem_ibov and not tem_cdi):
                benchmark_cagr_col = ''
                benchmark_name = ''
                if tem_cdi:
                    benchmark_cagr_col = 'CAGR_CDI'
                    benchmark_name = 'CDI'
                elif tem_ibov:
                    benchmark_cagr_col = 'CAGR_IBOV'
                    benchmark_name = 'Ibovespa'

                if benchmark_cagr_col and benchmark_cagr_col in df.columns and not df.dropna(subset=['CAGR_Fundo', benchmark_cagr_col]).empty:
                    valid_idx = df.dropna(subset=['CAGR_Fundo', benchmark_cagr_col]).index
                    if not valid_idx.empty:
                        df.loc[valid_idx, 'EXCESSO_RETORNO_ANUALIZADO'] = (
                            (1 + df.loc[valid_idx, 'CAGR_Fundo'] / 100) /
                            (1 + df.loc[valid_idx, benchmark_cagr_col] / 100) - 1
                        ) * 100

                    fig_excesso_retorno = go.Figure()
                    fig_excesso_retorno.add_trace(go.Scatter(
                        x=df['DT_COMPTC'],
                        y=df['EXCESSO_RETORNO_ANUALIZADO'],
                        mode='lines',
                        name=f'Excesso de Retorno Anualizado vs {benchmark_name}',
                        line=dict(color=color_primary, width=2.5),
                        fill='tozeroy',
                        fillcolor='rgba(26, 95, 63, 0.1)',
                        hovertemplate=f'<b>Excesso de Retorno vs {benchmark_name}</b><br>Data: %{{x|%d/%m/%Y}}<br>Excesso: %{{y:.2f}}%<extra></extra>'
                    ))
                    fig_excesso_retorno.add_hline(y=0, line_dash='dash', line_color='gray', linewidth=1)

                    fig_excesso_retorno.update_layout(
                        xaxis_title="Data",
                        yaxis_title="Excesso de Retorno (% a.a)",
                        template="plotly_white",
                        hovermode="x unified",
                        height=500,
                        font=dict(family="Inter, sans-serif")
                    )
                    df_plot_excess = df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO']).copy()
                    if not df_plot_excess.empty:
                        fig_excesso_retorno = add_watermark_and_style(
                            fig_excesso_retorno,
                            logo_base64,
                            x_range=[df_plot_excess['DT_COMPTC'].min(), df_plot_excess['DT_COMPTC'].max()],
                            x_autorange=False
                        )
                    else:
                        fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64)
                    st.plotly_chart(fig_excesso_retorno, use_containerwidth=True)
                else:
                    st.warning(f"⚠️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado (verifique se há dados de {benchmark_name} e CAGR para o período).")
            elif tem_cdi and tem_ibov:
                st.info("ℹ️ Para visualizar o Excesso de Retorno Anualizado, selecione apenas um indicador de comparação (CDI ou Ibovespa) na barra lateral.")
            else:
                st.info("ℹ️ Selecione um indicador de comparação (CDI ou Ibovespa) na barra lateral para visualizar o Excesso de Retorno Anualizado.")

        # ------------------------------ TAB 2 (Risco) --------------------------
        with tab2:
            st.subheader("Drawdown Histórico")

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Drawdown'],
                mode='lines',
                name='Drawdown do Fundo',
                line=dict(color=color_danger, width=2.5),
                fill='tozeroy',
                fillcolor='rgba(220, 53, 69, 0.1)',
                hovertemplate='<b>Drawdown do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ))
            fig3.add_hline(y=0, line_dash='dash', line_color='gray',width=1)
            fig3.update_layout(
                xaxis_title="Data",
                yaxis_title="Drawdown (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            fig3 = add_watermark_and_style(fig3, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig3, use_containerwidth=True)

            st.subheader(f"Volatilidade Móvel ({vol_window} dias úteis)")

            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Volatilidade'],
                mode='lines',
                name=f'Volatilidade do Fundo ({vol_window} dias)',
                line=dict(color=color_primary, width=2.5),
                fill='tozeroy',
                fillcolor='rgba(26, 95, 63, 0.1)',
                hovertemplate='<b>Volatilidade do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
            ))
            fig4_trace(go.Scatter(
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
            fig4 = add_watermark_and_style(fig4, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig4, use_containerwidth=True)

            st.subheader("Value at Risk (VaR) e Expected Shortfall (ES)")

            if not df_plot_var.empty:
                fig5 = go.Figure()
                fig5.add_trace(go.Scatter(
                    x=df_plot_var['DT_COMPTC'],
                    y=df_plot_var['Retorno_21d'] * 100,
                    mode='lines',
                    name='Rentabilidade móvel (1m)',
                    line=dict(color=color_primary, width=2),
                    fill='tozeroy',
                    fillcolor='rgba(26, 95, 63, 0.1)',
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade 21d: %{y:.2f}%<extra></extra>'
                ))
                fig5.add_trace(go.Scatter(
                    x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                    y=[VaR_95 * 100, VaR_95 * 100],
                    mode='lines',
                    name='Va 95%',
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
                    fig5, logo_base64,
                    x_range=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                    x_autorange=False
                )
                st.plotly_chart(fig5, use_containerwidth=True)

                st.info(f"""
                **Este gráfico mostra que, em um período de 1 mês:**

                • Há **99%** de confiança de que fundo não cairá mais do que **{fmt_pct_port(VaR_99)} (VaR)**,
                e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_99)} (ES)**.

                • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(VaR_95)} (VaR)**,
                e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES95)} (ES)**.
                """)
            else:
                st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias de retorno).")

            # ----------------- MÉTRICAS DE RISCO-RETORNO (COM NOVOS INDICADORES) -----------------
            st.subheader("Métricas de Risco-Retorno")

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

                    # Pain Index: média absoluta dos drawdowns negativos
                    negative_drawdowns = drawdown_series[drawdown_series < 0]
                    if not negative_drawdowns.empty:
                        pain_index = -negative_drawdowns.mean()
                    else:
                        pain_index = np.nan

                    # Downside Volatility & tracking error: precisamos de retornos diários do benchmark
                    benchmark_daily_returns = pd.Series(dtype='float64')

                    if tem_cdi and (benchmark_daily_rate_col in df.columns):
                        # CDI: df['cdi'] já está em taxa diária %
                        benchmark_daily_returns = df[benchmark_daily_rate_col] / 100.0
                    elif tem_ibov and (benchmark_cota_col in df.columns):
                        # Ibovespa: retorno diário de preço
                        benchmark_daily_returns = df[benchmark_cota_col].pct_change()

                    # Downside returns: excesso do fundo vs benchmark abaixo de zero
                    if not benchmark_daily_returns.empty:
                        excess_returns_vs_benchmark_daily = df['Variacao_Perc'] - benchmark_daily_returns
                        downside_returns = excess_returns_vs_benchmark_daily[excess_returns_vs_benchmark_daily < 0]
                    else:
                        downside_returns = df['Variacao_Perc'][df['Variacao_Perc'] < 0]

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

                    # Ratios baseados em drawdown
                    if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_benchmark_return) and not pd.isna(max_drawdown_value) and max_drawdown_value != 0:
                        calmar_ratio = (cagr_fund_decimal - annualized_benchmark_return) / abs(max_drawdown_value)
                        sterling_ratio = (cagr_fund_decimal - annualized_benchmark_return) / abs(max_drawdown_value)

                    # Martin
                    if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_benchmark_return) and not pd.isna(ulcer_index) and ulcer_index != 0:
                        martin_ratio = (cagr_fund_decimal - annualized_benchmark_return) / ulcer_index

                    # Sharpe
                    if not pd.isna(annualized_fund_return) and not pd.isna(annualized_benchmark_return) and not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0:
                        sharpe_ratio = (annualized_fund_return - annualized_benchmark_return) / annualized_fund_volatility

                    # Sortino
                    if not pd.isna(annualized_fund_return) and not pd.isna(annualized_benchmark_return) and not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0:
                        sortino_ratio = (annualized_fund_return - annualized_benchmark_return) / annualized_downside_volatility

                    # Information
                    if not pd.isna(annualized_fund_return) and not pd.isna(annualized_benchmark_return) and not pd.isna(tracking_error) and tracking_error != 0:
                        information_ratio = (annualized_fund_return - annualized_benchmark_return) / tracking_error

                    # --------- Exibição dos cards / explicações ---------
                    st.markdown(f"#### RISCO MEDIDO PELA VOLATILIDADE (vs. {benchmark_name}):")
                    col_vol_1, col_vol_2 = st.columns(2)

                    with col_vol_1:
                        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if not pd.isna(sharpe_ratio) else "N/A")
                        st.info(f"""
                        **Sharpe Ratio:** Mede o excesso de retorno do fundo (acima do {benchmark_name}) por unidade de **volatilidade total** (risco). Quanto maior, melhor.
                        *   < 1.0: subótimo
                        *   1.0–2.0: bom
                        *   2.0–3.0: muito bom
                        *   ≥ 3.0: excepcional
                        """)

                    with col_vol_2:
                        st.metric("Sortino Ratio", f"{sortino_ratio:.2f}" if not pd.isna(sortino_ratio) else "N/A")
                        st.info(f"""
                        **Sortino Ratio:** Similar ao Sharpe, mas foca apenas na **volatilidade de queda** (downside). Indica retorno por unidade de risco de perda.
                        *   < 0.0: retorno não cobre o risco de queda
                        *   0.0–1.0: aceitável
                        *   > 1.0: bom / muito bom
                        """)

                    col_vol_3, col_vol_4 = st.columns(2)
                    with col_vol_3:
                        st.metric("Information Ratio", f"{information_ratio:.2f}" if not pd.isna(information_ratio) else "N/A")
                        st.info(f"""
                        **Information Ratio:** Excesso de retorno sobre o {benchmark_name} por unidade de **tracking error**.
                        *   < 0.0: abaixo do benchmark
                        *   0.0–0.5: habilidade modesta
                        *   0.5–1.0: boa consistência
                        *   > 1.0: excelente consistência
                        """)
                    with col_vol_4:
                        st.metric("Treynor Ratio", "Não calculado", help="Depende explicitamente de Beta e taxa livre de risco. Aqui usamos Beta só para o Alpha de Jensen.")

                    st.markdown(f"#### RISCO MEDIDO PELO DRAWDOWN (vs. {benchmark_name}):")
                    col_dd_1, col_dd_2 = st.columns(2)

                    with col_dd_1:
                        st.metric("Calmar Ratio", f"{calmar_ratio:.2f}" if not pd.isna(calmar_ratio) else "N/A")
                        st.info("""
                        **Calmar Ratio:** Retorno anualizado acima do benchmark dividido pelo maior drawdown absoluto.
                        Quanto maior, melhor a relação retorno / grandes quedas.
                        """)

                    with col_dd_2:
                        st.metric("Sterling Ratio", f"{sterling_ratio:.2f}" if not pd.isna(sterling_ratio) else "N/A")
                        st.info("""
                        **Sterling Ratio:** Similar ao Calmar; aqui usamos o maior drawdown como aproximação do risco de cauda.
                        """)

                    col_dd_3, col_dd_4 = st.columns(2)
                    with col_dd_3:
                        st.metric("Ulcer Index", f"{ulcer_index:.2f}" if not pd.isna(ulcer_index) else "N/A")
                        st.info("""
                        **Ulcer Index:** Mede profundidade e duração das quedas (drawdowns).
                        Quanto menor, menos “doloroso” o histórico do fundo.
                        """)
                    with col_dd_4:
                        st.metric("Martin Ratio", f"{martin_ratio:.2f}" if not pd.isna(martin_ratio) else "N/A")
                        st.info("""
                        **Martin Ratio:** Excesso de retorno anualizado dividido pelo Ulcer Index.
                        Indica retorno obtido por unidade de “dor” em drawdowns.
                        """)

                    # --------- NOVO BLOCO: PAIN, BETA, ALPHA DE JENSEN ---------
                    st.markdown(f"#### OUTROS INDICADORES (vs. {benchmark_name}):")
                    col_extra_1, col_extra_2, col_extra_3 = st.columns(3)

                    with col_extra_1:
                        st.metric("Pain Index", f"{pain_index:.2f}" if not pd.isna(pain_index) else "N/A")
                        st.info("""
                        **Pain Index:** Média (em valor absoluto) dos drawdowns negativos.
                        Quanto menor, mais rasas tendem a ser as quedas típicas do fundo.
                        """)

                    with col_extra_2:
                        st.metric("Beta", f"{beta:.2f}" if not pd.isna(beta) else "N/A")
                        st.info(f"""
                        **Beta:** Sensibilidade do fundo em relação ao {benchmark_name}, usando retornos diários.
                        *   ≈ 1: anda em linha com o {benchmark_name}
                        *   > 1: mais sensível / mais volátil
                        *   < 1: menos sensível
                        *   < 0: comportamento inverso
                        """)

                    with col_extra_3:
                        st.metric("Alpha de Jensen (a.a.)", f"{jensen_alpha*100:.2f}%" if not pd.isna(jensen_alpha) else "N/A")
                        st.info(f"""
                        **Alpha de Jensen:** Retorno anualizado do fundo **menos** o retorno esperado dado seu Beta vs. {benchmark_name}, assumindo taxa livre de risco = 0.
                        *   > 0%: entregou retorno acima do esperado para o risco sistemático
                        *   = 0%: em linha com o esperado
                        *   < 0%: abaixo do esperado para o risco assumido
                        """)

                    st.markdown("""
                    ---
                    **Observação:** As faixas de “bom/ruim” são diretrizes gerais de literatura; sempre interprete as métricas no contexto da estratégia, horizonte e ciclo de mercado.
                    """)
                else:
                    st.warning(f"⚠️ Não há dados suficientes para calcular as Métricas de Risco-Retorno (mínimo de 1 ano de dados do fundo e do {benchmark_name}).")

    with tab3:
        st.subheader("Patrimônio e Captação Líquida")

        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Soma_Acumulada'],
            mode='lines',
            name='Captação Líquida',
            line=dict(color=color_primary, width=2.5), # Cor primária
            fill='tozeroy', # Adicionado preenchimento
            fillcolor='rgba(26, 95, 63, 0.1)', # Cor de preenchimento
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Captação Líquida Acumulada: %{customdata}<extra></extra>',
            customdata=[format_brl(v) for v in df['Soma_Acumulada']]
        ))
        fig6.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['VL_PATRIM_LIQ'],
            mode='lines',
            name='Patrimônio Líquido',
            line=dict(color=color_secondary, width=2.5), # Cor secundária
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
        # Ajusta o range do eixo X para os dados de df
        fig6 = add_watermark_and_style(fig6, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig6, use_containerwidth=True)

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
                # Removido text e textposition para não exibir valores nas barras (conforme memória do usuário)
            )
        ])

        fig7.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            # Ajusta o range para evitar cortar barras, mas sem texto
            yaxis=dict(range=[df_monthly['Captacao_Liquida'].min() * 1.1, df_monthly['Captacao_Liquida'].max() * 1.1])
        )
        # Ajusta o range do eixo X para os dados de df_monthly
        if not df_monthly.empty:
            fig7 = add_watermark_and_style(fig7, logo_base64, x_range=[df_monthly.index.min(), df_monthly.index.max()], x_autorange=False)
        else:
            fig7 = add_watermark_and_style(fig7, logo_base64) # Sem range específico se não houver dados
        st.plotly_chart(fig7, use_containerwidth=True)

    with tab4:
        st.subheader("Patrimônio Médio e Nº de Cotistas")

        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Patrimonio_Liq_Medio'],
            mode='lines',
            name='Patrimônio Médio por Cotista',
            line=dict(color=color_primary, width=2.5), # Cor primária
            fill='tozeroy', # Adicionado preenchimento
            fillcolor='rgba(26, 95, 63, 0.1)', # Cor de preenchimento
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Médio: %{customdata}<extra></extra>',
            customdata=[format_brl(v) for v in df['Patrimonio_Liq_Medio']]
        ))
        fig8.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['NR_COTST'],
            mode='lines',
            name='Número de Cotistas',
            line=dict(color=color_secondary, width=2.5), # Cor secundária
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
        st.plotly_chart(fig8, use_containerwidth=True)

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
                if tem_cdi and 'CDI_COTA' in df_returns.columns: # NOVO: Verifica se a coluna existe
                    df_returns[f'CDI_{nome}'] = df_returns['CDI_COTA'] / df_returns['CDI_COTA'].shift(dias) - 1
                if tem_ibov and 'IBOV_COTA' in df_returns.columns: # NOVO
                    df_returns[f'IBOV_{nome}'] = df_returns['IBOV_COTA'] / df_returns['IBOV_COTA'].shift(dias) - 1
            else:
                df_returns[f'FUNDO_{nome}'] = np.nan
                if tem_cdi:
                    df_returns[f'CDI_{nome}'] = np.nan
                if tem_ibov: # NOVO
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

            # NOVO: Retorno do Ibovespa (se disponível)
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
            # Ajusta o range do eixo X para os dados de df_returns
            df_plot_returns = df_returns.dropna(subset=[f'FUNDO_{janela_selecionada}']).copy()
            if not df_plot_returns.empty:
                fig9 = add_watermark_and_style(fig9, logo_base64, x_range=[df_plot_returns['DT_COMPTC'].min(), df_plot_returns['DT_COMPTC'].max()], x_autorange=False)
            else:
                fig9 = add_watermark_and_style(fig9, logo_base64) # Sem range específico se não houver dados
            st.plotly_chart(fig9, use_containerwidth=True)
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
                    # Removido text e textposition para não exibir valores nas barras (conforme memória do usuário)
                    hovertemplate=f'<b>Janela:</b> %{{x}}<br><b>Consistência vs {benchmark_name_consistency}:</b> %{{y:.2f}}%<extra></extra>'
                ))

                fig_consistency.update_layout(
                    xaxis_title="Janela (meses)",
                    yaxis_title=f"Percentual de Superação do {benchmark_name_consistency} (%)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Inter, sans-serif"),
                    yaxis=dict(range=[0, 100], ticksuffix="%") # Ajusta o range para 0-100%
                )
                fig_consistency = add_watermark_and_style(fig_consistency, logo_base64, x_autorange=True)
                st.plotly_chart(fig_consistency, use_containerwidth=True)
            else:
                st.warning(f"⚠️ Não há dados suficientes para calcular a Consistência em Janelas Móveis vs {benchmark_name_consistency}.")
        elif tem_cdi and tem_ibov:
            st.info("ℹ️ Para visualizar a Consistência em Janelas Móveis, selecione apenas um indicador de comparação (CDI ou Ibovespa) na barra lateral.")
        else:
            st.info("ℹ️ Selecione um indicador de comparação (CDI ou Ibovespa) na barra lateral para visualizar a Consistência em Janelas Móveis.")

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("💡 Verifique se o CNPJ está correto e se há dados disponíveis para o período selecionado.")

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
