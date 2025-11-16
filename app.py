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

    [data-testid="stSidebar"] .stTextInput label {
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

# Função para adicionar marca d'água e estilizar gráficos
def add_watermark_and_style(fig, logo_base64=None):
    """Adiciona marca d'água e estilização aos gráficos"""
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
                opacity=0.08,  # <<< AQUI VOCÊ ALTERA A OPACIDADE DA MARCA D'ÁGUA
                layer="below"
            )
        )

    fig.update_layout(
        plot_bgcolor='rgba(248, 246, 241, 0.5)',
        paper_bgcolor='white',
        font=dict(family="Inter, sans-serif", size=12, color="#2c2c2c"),
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

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(224, 221, 213, 0.5)',
        showline=True,
        linewidth=2,
        linecolor='#e0ddd5',
        title_font=dict(size=13, color="#1a5f3f", family="Inter"),
        tickfont=dict(size=11, color="#6b9b7f")
    )

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

# FUNÇÃO PARA OBTER DADOS REAIS DO CDI (AGORA COM SUPORTE A PERÍODOS MAIORES QUE 10 ANOS)
@st.cache_data
def obter_dados_cdi_real(data_inicio_str, data_fim_str):
    """
    Obtém dados REAIS do CDI usando a biblioteca python-bcb,
    dividindo a requisição em blocos de 10 anos para contornar limites da API.
    Normaliza o VL_CDI para começar em 1.0 no primeiro dia do período.
    """
    if not BCB_DISPONIVEL:
        st.error("❌ Biblioteca 'python-bcb' não está instalada. Instale com: pip install python-bcb")
        return pd.DataFrame()

    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y%m%d')
        data_fim = datetime.strptime(data_fim_str, '%Y%m%d')

        all_cdi_dfs = []
        current_start = data_inicio

        # Loop para buscar dados em blocos de 10 anos (limite da API)
        while current_start <= data_fim:
            current_end = min(current_start + timedelta(days=10*365 - 1), data_fim) 

            st.info(f"Buscando CDI de {current_start.strftime('%d/%m/%Y')} a {current_end.strftime('%d/%m/%Y')}...")

            cdi_chunk = sgs.get({'cdi': 12}, start=current_start, end=current_end)

            if not cdi_chunk.empty:
                all_cdi_dfs.append(cdi_chunk)

            current_start = current_end + timedelta(days=1)

        if not all_cdi_dfs:
            return pd.DataFrame()

        # Concatenar todos os chunks e remover duplicatas (se houver)
        cdi_diario = pd.concat(all_cdi_dfs).drop_duplicates().sort_index()

        # Transformar o índice em coluna
        cdi_diario = cdi_diario.reset_index()

        # Alterar o nome da coluna
        cdi_diario = cdi_diario.rename(columns={'Date': 'DT_COMPTC'})

        # Garantir que DT_COMPTC é datetime
        cdi_diario['DT_COMPTC'] = pd.to_datetime(cdi_diario['DT_COMPTC'])

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

# FUNÇÃO PARA COMBINAR FUNDO E CDI (CDI AGORA É A TABELA PRINCIPAL)
def processar_dados_com_cdi(df_fundo_raw, data_inicial_usuario_str, data_final_usuario_str, incluir_cdi=False):
    """
    Processa os dados do fundo e opcionalmente adiciona o CDI REAL,
    usando as datas do CDI como base principal.
    """

    # 1. Obter CDI para o período COMPLETO do usuário (será a base)
    df_cdi_base = obter_dados_cdi_real(data_inicial_usuario_str, data_final_usuario_str)

    if df_cdi_base.empty:
        st.warning("Não foi possível obter dados do CDI para o período selecionado.")
        # Se não há CDI, apenas processa o fundo
        df = df_fundo_raw.copy()
        # Verificar se df_fundo_raw não está vazio antes de acessar iloc[0]
        if not df.empty and 'VL_QUOTA' in df.columns and not df['VL_QUOTA'].isnull().all():
            primeira_cota = df['VL_QUOTA'].iloc[0]
            df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota) - 1) * 100
        else:
            df['VL_QUOTA_NORM'] = 0.0 # Se não há dados do fundo, a rentabilidade é 0
        return df

    # 2. Mesclar dados do fundo com a base do CDI (CDI é a tabela principal)
    # Usamos 'left' merge aqui porque df_cdi_base é a tabela da esquerda (principal)
    df_merged = df_cdi_base.merge(
        df_fundo_raw, 
        on='DT_COMPTC', 
        how='left',
        suffixes=('_cdi', '_fundo') # Adiciona sufixos para evitar conflitos de nomes se houver
    )

    # Garantir que o DataFrame esteja ordenado por data
    df_merged = df_merged.sort_values('DT_COMPTC').reset_index(drop=True)

    # 3. Preencher valores ausentes para as colunas do fundo
    # VL_QUOTA e VL_PATRIM_LIQ: ffill para preencher para frente, bfill para preencher para trás
    # Isso lida com casos onde o fundo começa depois do CDI ou tem lacunas
    df_merged['VL_QUOTA'].fillna(method='ffill', inplace=True)
    df_merged['VL_QUOTA'].fillna(method='bfill', inplace=True) # Para NaNs no início se o fundo começa depois

    df_merged['VL_PATRIM_LIQ'].fillna(method='ffill', inplace=True)
    df_merged['VL_PATRIM_LIQ'].fillna(method='bfill', inplace=True) # Para NaNs no início

    # NR_COTST, CAPTC_DIA, RESG_DIA: preencher com 0 se não houver dados
    df_merged['NR_COTST'].fillna(0, inplace=True)
    df_merged['CAPTC_DIA'].fillna(0, inplace=True)
    df_merged['RESG_DIA'].fillna(0, inplace=True)

    # 4. Normalizar dados do fundo (agora que NaNs foram tratados)
    # Encontrar a primeira cota válida para normalização
    first_valid_quota_idx = df_merged['VL_QUOTA'].first_valid_index()
    if first_valid_quota_idx is not None and not pd.isna(df_merged.loc[first_valid_quota_idx, 'VL_QUOTA']):
        primeira_cota = df_merged.loc[first_valid_quota_idx, 'VL_QUOTA']
        df_merged['VL_QUOTA_NORM'] = ((df_merged['VL_QUOTA'] / primeira_cota) - 1) * 100
        # Preencher NaNs antes do início do fundo com 0 na rentabilidade normalizada
        df_merged['VL_QUOTA_NORM'].fillna(0, inplace=True)
    else:
        # Se não há dados válidos para o fundo no período, a rentabilidade é 0
        df_merged['VL_QUOTA_NORM'] = 0.0
        st.warning("⚠️ Não há dados válidos para o fundo no período selecionado. Gráficos do fundo podem estar vazios.")

    # 5. Normalizar CDI (se for para incluir)
    if incluir_cdi:
        # CDI_COTA é agora o valor acumulado normalizado, começando em 1.0
        df_merged['CDI_COTA'] = df_merged['VL_CDI_normalizado']
        # CDI_NORM será a rentabilidade percentual, começando em 0.00%
        df_merged['CDI_NORM'] = (df_merged['CDI_COTA'] - 1) * 100
    else:
        # Se não incluir CDI, garantir que as colunas não existam ou sejam NaN
        df_merged['CDI_COTA'] = np.nan
        df_merged['CDI_NORM'] = np.nan
        df_merged['cdi'] = np.nan # Taxa diária do CDI

    return df_merged

# Sidebar
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
carregar_button = st.sidebar.button("🔄 Carregar Dados", type="primary", disabled=not (cnpj_valido and datas_validas))

# Título principal
st.markdown("<h1>📊 Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
st.markdown("---")

# Função para carregar dados do fundo
@st.cache_data
def carregar_dados_api(cnpj, data_ini, data_fim):
    """
    Carrega dados do fundo. O período é ampliado para garantir que
    todas as datas relevantes para o CDI sejam cobertas, mesmo que o fundo
    comece depois ou termine antes do período do CDI.
    """
    # Ampliar o período inicial para garantir que pegamos dados suficientes para ffill/bfill
    dt_inicial_solicitada = datetime.strptime(data_ini, '%Y%m%d')
    dt_ampliada = dt_inicial_solicitada - timedelta(days=365 * 10) # 10 anos antes para ter bastante histórico
    data_ini_ampliada = dt_ampliada.strftime('%Y%m%d')

    url = f"https://www.okanebox.com.br/api/fundoinvestimento/hist/{cnpj}/{data_ini_ampliada}/{data_fim}/"
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

if not st.session_state.dados_carregados:
    st.info("👈 Preencha os campos na barra lateral e clique em 'Carregar Dados' para começar a análise.")
    st.markdown("""
    ### 📋 Como usar:
    1. **CNPJ do Fundo**: Digite o CNPJ do fundo que deseja analisar
    2. **Data Inicial**: Digite a data inicial no formato DD/MM/AAAA
    3. **Data Final**: Digite a data final no formato DD/MM/AAAA
    4. **Indicadores**: Selecione os indicadores para comparação
    5. Clique em **Carregar Dados** para visualizar as análises
    """)
    st.stop()

try:
    with st.spinner('🔄 Carregando dados...'):
        # 1. BAIXAR DADOS DO FUNDO (período ampliado para garantir cobertura)
        df_fundo_raw = carregar_dados_api(
            st.session_state.cnpj,
            st.session_state.data_ini, # Passa a data inicial do usuário
            st.session_state.data_fim
        )

        # 2. PROCESSAR DADOS (CDI É A BASE PRINCIPAL)
        # A função ajustar_periodo_analise não é mais necessária aqui
        df = processar_dados_com_cdi(
            df_fundo_raw, 
            data_inicial_usuario_str=st.session_state.data_ini,
            data_final_usuario_str=st.session_state.data_fim,
            incluir_cdi=st.session_state.mostrar_cdi
        )

    # 3. CALCULAR MÉTRICAS
    # df já está ordenado por DT_COMPTC dentro de processar_dados_com_cdi

    # Verificar se há dados válidos para o fundo para calcular métricas
    if 'VL_QUOTA' not in df.columns or df['VL_QUOTA'].isnull().all():
        st.error("❌ Não foi possível obter dados válidos para o fundo no período selecionado. Verifique o CNPJ e as datas.")
        st.stop()

    # Métricas do fundo
    df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
    df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100
    df['Captacao_Liquida'] = df['CAPTC_DIA'] - df['RESG_DIA']
    df['Soma_Acumulada'] = df['Captacao_Liquida'].cumsum()
    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

    vol_window = 21
    trading_days = 252
    df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()
    df['Volatilidade'] = df['Variacao_Perc'].rolling(vol_window).std() * np.sqrt(trading_days) * 100
    vol_hist = round(df['Variacao_Perc'].std() * np.sqrt(trading_days) * 100, 2)

    # Métricas do CDI (se disponível)
    tem_cdi = st.session_state.mostrar_cdi and 'CDI_NORM' in df.columns and not df['CDI_NORM'].isnull().all()
    if tem_cdi:
        # Drawdown do CDI
        df['CDI_Max'] = df['VL_CDI_normalizado'].cummax() # Usar VL_CDI_normalizado
        df['CDI_Drawdown'] = (df['VL_CDI_normalizado'] / df['CDI_Max'] - 1) * 100

        # Volatilidade do CDI
        df['CDI_Variacao'] = df['CDI_COTA'].pct_change()
        df['CDI_Volatilidade'] = df['CDI_Variacao'].rolling(vol_window).std() * np.sqrt(trading_days) * 100
        cdi_vol_hist = round(df['CDI_Variacao'].std() * np.sqrt(trading_days) * 100, 2)

    # CAGR
    df_cagr = df.copy()

    # CORREÇÃO: Definir DT_COMPTC como índice para calcular dias_uteis corretamente
    df_cagr = df_cagr.set_index('DT_COMPTC')

    # Filtrar df_cagr para garantir que VL_QUOTA não seja NaN no início do período de cálculo
    first_valid_cagr_idx = df_cagr['VL_QUOTA'].first_valid_index()
    if first_valid_cagr_idx is not None:
        df_cagr = df_cagr.loc[first_valid_cagr_idx:].copy()

    end_value = df_cagr['VL_QUOTA'].iloc[-1]
    # Agora df_cagr.index é um DatetimeIndex, então .days funciona
    df_cagr['dias_uteis'] = (df_cagr.index[-1] - df_cagr.index).map(lambda x: x.days) 
    df_cagr = df_cagr[df_cagr['dias_uteis'] >= 252].copy() # Filtrar para ter pelo menos 1 ano de dados

    if not df_cagr.empty:
        # CAGR do Fundo
        df_cagr['CAGR'] = ((end_value / df_cagr['VL_QUOTA']) ** (252 / df_cagr['dias_uteis'])) - 1
        df_cagr['CAGR'] = df_cagr['CAGR'] * 100
        mean_cagr = df_cagr['CAGR'].mean()

        # CAGR do CDI (se disponível)
        if tem_cdi and 'CDI_COTA' in df_cagr.columns and not df_cagr['CDI_COTA'].isnull().all():
            end_value_cdi = df_cagr['CDI_COTA'].iloc[-1]
            df_cagr['CAGR_CDI'] = ((end_value_cdi / df_cagr['CDI_COTA']) ** (252 / df_cagr['dias_uteis'])) - 1
            df_cagr['CAGR_CDI'] = df_cagr['CAGR_CDI'] * 100
    else:
        mean_cagr = 0
        st.warning("⚠️ Não há dados suficientes para calcular o CAGR (mínimo de 252 dias úteis).")


    # VaR
    df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
    df_plot = df.dropna(subset=['Retorno_21d']).copy()
    if not df_plot.empty:
        VaR_95 = np.percentile(df_plot['Retorno_21d'], 5)
        VaR_99 = np.percentile(df_plot['Retorno_21d'], 1)
        ES_95 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
        ES_99 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()
    else:
        VaR_95, VaR_99, ES_95, ES_99 = 0, 0, 0, 0
        st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias úteis).")


    # Cores
    color_primary = '#1a5f3f'  # Verde escuro para o fundo
    color_secondary = '#6b9b7f'
    color_danger = '#dc3545'
    color_cdi = '#f0b429'  # Amarelo para o CDI

    # Cards de métricas
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

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Rentabilidade",
        "📉 Risco",
        "💰 Patrimônio",
        "👥 Cotistas",
        "🎯 Janelas Móveis"
    ])

    with tab1:
        st.subheader("📈 Rentabilidade Histórica")

        fig1 = go.Figure()

        # Linha do Fundo
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

        # Linha do CDI (se selecionado)
        if tem_cdi:
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['CDI_NORM'],
                mode='lines',
                name='CDI',
                line=dict(color=color_cdi, width=2.5),
                hovertemplate='<b>CDI</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
            ))

        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade (%)",
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

        fig1 = add_watermark_and_style(fig1, logo_base64)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 CAGR Anual por Dia de Aplicação")

        fig2 = go.Figure()

        if not df_cagr.empty:
            # CAGR do Fundo
            fig2.add_trace(go.Scatter(
                x=df_cagr.index, # Usar o índice que agora é DT_COMPTC
                y=df_cagr['CAGR'],
                mode='lines',
                name='CAGR do Fundo',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='<b>CAGR do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
            ))

            fig2.add_trace(go.Scatter(
                x=df_cagr.index, # Usar o índice que agora é DT_COMPTC
                y=[mean_cagr] * len(df_cagr),
                mode='lines',
                line=dict(dash='dash', color=color_secondary, width=2),
                name=f'CAGR Médio ({mean_cagr:.2f}%)'
            ))

            # CAGR do CDI (se disponível)
            if tem_cdi and 'CAGR_CDI' in df_cagr.columns:
                fig2.add_trace(go.Scatter(
                    x=df_cagr.index, # Usar o índice que agora é DT_COMPTC
                    y=df_cagr['CAGR_CDI'],
                    mode='lines',
                    name='CAGR do CDI',
                    line=dict(color=color_cdi, width=2.5),
                    hovertemplate='<b>CAGR do CDI</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
                ))

        fig2.update_layout(
            xaxis_title="Data",
            yaxis_title="CAGR (% a.a)",
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

        fig2 = add_watermark_and_style(fig2, logo_base64)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("📉 Drawdown Histórico")

        fig3 = go.Figure()

        # Drawdown do Fundo
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

        # Drawdown do CDI (se disponível)
        if tem_cdi:
            fig3.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['CDI_Drawdown'],
                mode='lines',
                name='Drawdown do CDI',
                line=dict(color=color_cdi, width=2.5),
                hovertemplate='<b>Drawdown do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ))

        fig3.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

        fig3.update_layout(
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

        fig3 = add_watermark_and_style(fig3, logo_base64)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"📊 Volatilidade Móvel ({vol_window} dias úteis)")

        fig4 = go.Figure()

        # Volatilidade do Fundo
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

        # Volatilidade do CDI (se disponível)
        if tem_cdi:
            fig4.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['CDI_Volatilidade'],
                mode='lines',
                name=f'Volatilidade do CDI ({vol_window} dias)',
                line=dict(color=color_cdi, width=2.5),
                hovertemplate='<b>Volatilidade do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
            ))

            fig4.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=[cdi_vol_hist] * len(df),
                mode='lines',
                line=dict(dash='dot', color=color_cdi, width=1.5),
                name=f'CDI Vol. Histórica ({cdi_vol_hist:.2f}%)'
            ))

        fig4.update_layout(
            xaxis_title="Data",
            yaxis_title="Volatilidade (% a.a.)",
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

        fig4 = add_watermark_and_style(fig4, logo_base64)
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("⚠️ Value at Risk (VaR) e Expected Shortfall (ES)")

        if not df_plot.empty:
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=df_plot['DT_COMPTC'],
                y=df_plot['Retorno_21d'] * 100,
                mode='lines',
                name='Rentabilidade móvel (1m)',
                line=dict(color=color_primary, width=2),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade 21d: %{y:.2f}%<extra></extra>'
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
                y=[VaR_95 * 100, VaR_95 * 100],
                mode='lines',
                name='VaR 95%',
                line=dict(dash='dot', color='orange', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
                y=[VaR_99 * 100, VaR_99 * 100],
                mode='lines',
                name='VaR 99%',
                line=dict(dash='dot', color='red', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
                y=[ES_95 * 100, ES_95 * 100],
                mode='lines',
                name='ES 95%',
                line=dict(dash='dash', color='orange', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
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

            fig5 = add_watermark_and_style(fig5, logo_base64)
            st.plotly_chart(fig5, use_container_width=True)

            st.info(f"""
            **Este gráfico mostra que, em um período de 1 mês:**

            • Há **99%** de confiança de que o fundo não cairá mais do que **{fmt_pct_port(VaR_99)} (VaR)**,
            e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_99)} (ES)**.

            • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(VaR_95)} (VaR)**,
            e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_95)} (ES)**.
            """)

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

        fig6 = add_watermark_and_style(fig6, logo_base64)
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

        fig7 = add_watermark_and_style(fig7, logo_base64)
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

        fig8 = add_watermark_and_style(fig8, logo_base64)
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
            df_returns[f'FUNDO_{nome}'] = df_returns['VL_QUOTA'] / df_returns['VL_QUOTA'].shift(dias) - 1
            if tem_cdi:
                df_returns[f'CDI_{nome}'] = df_returns['CDI_COTA'] / df_returns['CDI_COTA'].shift(dias) - 1

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

            fig9 = add_watermark_and_style(fig9, logo_base64)
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada}.")

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
