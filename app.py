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
                opacity=0.08,  # <<< AQUI VOCÊ ALTERA A OPACIDADE DA MARCA D'ÁGUA
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

# Opção para comparar com CDI
mostrar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)

# Botão de carregar dados
st.sidebar.markdown("---") # Separador visual
carregar_button = st.sidebar.button("🔄 Carregar Dados")

# Variáveis de cores
color_primary = "#1a5f3f"  # Verde escuro
color_secondary = "#2d8659" # Verde médio
color_cdi = "#f0b429"      # Amarelo/Ouro
color_danger = "#dc3545"   # Vermelho

# Formatação de números
def fmt_pct(value):
    return f"{value:.2%}"

def fmt_pct_port(value):
    return f"{value:.2%}"

def format_brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Inicializa session_state para controlar o carregamento e dados
if 'trigger_load' not in st.session_state:
    st.session_state['trigger_load'] = False
if 'df' not in st.session_state:
    st.session_state['df'] = pd.DataFrame()
if 'fund_info' not in st.session_state:
    st.session_state['fund_info'] = {}
if 'tem_cdi' not in st.session_state:
    st.session_state['tem_cdi'] = False
if 'cnpj_valido' not in st.session_state:
    st.session_state['cnpj_valido'] = False
if 'periodo_valido' not in st.session_state:
    st.session_state['periodo_valido'] = False

# Lógica de carregamento de dados
if carregar_button or st.session_state['trigger_load']:
    st.session_state['trigger_load'] = False # Reseta o trigger

    cnpj_limpo = limpar_cnpj(cnpj_input)
    if not cnpj_limpo or len(cnpj_limpo) != 14:
        st.sidebar.error("❌ CNPJ inválido. Digite 14 dígitos.")
        st.session_state['cnpj_valido'] = False
        st.stop()
    else:
        st.session_state['cnpj_valido'] = True

    data_inicial_api = formatar_data_api(data_inicial_input)
    data_final_api = formatar_data_api(data_final_input)

    if not data_inicial_api or not data_final_api:
        st.sidebar.error("❌ Datas inválidas. Use o formato DD/MM/AAAA.")
        st.session_state['periodo_valido'] = False
        st.stop()
    else:
        dt_ini_user = datetime.strptime(data_inicial_api, '%Y%m%d')
        dt_fim_user = datetime.strptime(data_final_api, '%Y%m%d')
        if dt_ini_user >= dt_fim_user:
            st.sidebar.error("❌ Data inicial deve ser anterior à data final.")
            st.session_state['periodo_valido'] = False
            st.stop()
        st.session_state['periodo_valido'] = True

    if st.session_state['cnpj_valido'] and st.session_state['periodo_valido']:
        with st.spinner("Carregando dados do fundo e CDI..."):
            try:
                # --- 1. Carregar dados do Fundo (período ampliado para ffill) ---
                # Ajusta a data inicial para 10 anos antes para garantir dados para ffill e janelas móveis
                data_inicio_fundo_ampliado = dt_ini_user - timedelta(days=10*365)
                url_fundo = f"https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{data_inicio_fundo_ampliado.year:04d}{data_inicio_fundo_ampliado.month:02d}.csv.gz"

                df_fundo_completo = pd.DataFrame()
                current_year = data_inicio_fundo_ampliado.year
                end_year = dt_fim_user.year

                for year in range(current_year, end_year + 1):
                    for month in range(1, 13):
                        # Se o ano atual for o ano de início e o mês for anterior ao mês de início, pula
                        if year == current_year and month < data_inicio_fundo_ampliado.month:
                            continue
                        # Se o ano atual for o ano final e o mês for posterior ao mês final, pula
                        if year == end_year and month > dt_fim_user.month:
                            continue

                        url_mes = f"https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{year:04d}{month:02d}.csv.gz"
                        try:
                            with urllib.request.urlopen(url_mes) as response:
                                with gzip.open(BytesIO(response.read()), 'rt', encoding='latin1') as file:
                                    df_temp = pd.read_csv(file, sep=';')
                                    df_fundo_completo = pd.concat([df_fundo_completo, df_temp], ignore_index=True)
                        except urllib.error.HTTPError as e:
                            if e.code == 404:
                                # st.warning(f"⚠️ Dados não encontrados para {year}/{month}. Pulando.")
                                pass # Silenciosamente pula meses sem dados
                            else:
                                raise e # Re-lança outros erros HTTP
                        except Exception as e:
                            st.error(f"❌ Erro ao carregar dados do fundo para {year}/{month}: {str(e)}")
                            st.stop()

                if df_fundo_completo.empty:
                    st.error("❌ Não foi possível carregar dados do fundo para o período selecionado.")
                    st.session_state['df'] = pd.DataFrame()
                    st.stop()

                df_fundo_completo['DT_COMPTC'] = pd.to_datetime(df_fundo_completo['DT_COMPTC'])
                df_fundo_completo = df_fundo_completo[df_fundo_completo['CNPJ_FUNDO'] == cnpj_limpo].copy()

                if df_fundo_completo.empty:
                    st.error(f"❌ CNPJ {cnpj_input} não encontrado ou sem dados para o período ampliado.")
                    st.session_state['df'] = pd.DataFrame()
                    st.stop()

                # Ordenar e remover duplicatas
                df_fundo_completo = df_fundo_completo.sort_values('DT_COMPTC').drop_duplicates(subset=['DT_COMPTC']).reset_index(drop=True)

                # Armazenar informações do fundo
                st.session_state['fund_info'] = {
                    'DENOM_SOCIAL': df_fundo_completo['DENOM_SOCIAL'].iloc[0] if not df_fundo_completo.empty else "Fundo Desconhecido",
                    'DT_REG_CVM': df_fundo_completo['DT_REG_CVM'].iloc[0] if not df_fundo_completo.empty else "N/A"
                }

                # --- 2. Carregar dados do CDI (período exato do usuário) ---
                df_cdi_raw = obter_dados_cdi_real(dt_ini_user, dt_fim_user)
                st.session_state['tem_cdi'] = not df_cdi_raw.empty and mostrar_cdi

                # --- 3. Combinar dados (base CDI) ---
                if st.session_state['tem_cdi']:
                    # Usar as datas do CDI como base
                    df_final = df_cdi_raw[['DT_COMPTC', 'VL_CDI_normalizado']].copy()
                    df_final = df_final.rename(columns={'VL_CDI_normalizado': 'CDI_COTA'})

                    # Mesclar dados do fundo
                    df_final = pd.merge(df_final, df_fundo_completo[['DT_COMPTC', 'VL_QUOTA', 'CAPTC_DIA', 'RESG_DIA', 'NR_COTST', 'VL_PATRIM_LIQ']],
                                        on='DT_COMPTC', how='left')

                    # Preencher dados do fundo para datas do CDI onde não há cota
                    df_final['VL_QUOTA'] = df_final['VL_QUOTA'].ffill()
                    df_final['CAPTC_DIA'] = df_final['CAPTC_DIA'].fillna(0)
                    df_final['RESG_DIA'] = df_final['RESG_DIA'].fillna(0)
                    df_final['NR_COTST'] = df_final['NR_COTST'].ffill()
                    df_final['VL_PATRIM_LIQ'] = df_final['VL_PATRIM_LIQ'].ffill()

                    # Remover linhas onde VL_QUOTA ainda é NaN (fundo não existia ou não tinha dados)
                    df_final = df_final.dropna(subset=['VL_QUOTA']).reset_index(drop=True)

                    if df_final.empty:
                        st.error("❌ Não há dados do fundo disponíveis para o período selecionado, mesmo após preenchimento com CDI.")
                        st.session_state['df'] = pd.DataFrame()
                        st.stop()

                    # Filtrar para o período exato do usuário (após ffill)
                    df_final = df_final[(df_final['DT_COMPTC'] >= dt_ini_user) & (df_final['DT_COMPTC'] <= dt_fim_user)].reset_index(drop=True)

                    if df_final.empty:
                        st.error("❌ Não há dados do fundo disponíveis para o período selecionado após o filtro final.")
                        st.session_state['df'] = pd.DataFrame()
                        st.stop()

                    # Normalizar cotas do fundo para começar em 1.0 no início do período do usuário
                    primeira_cota_fundo = df_final['VL_QUOTA'].iloc[0]
                    df_final['VL_QUOTA_NORM'] = df_final['VL_QUOTA'] / primeira_cota_fundo

                    # Normalizar CDI para começar em 1.0 no início do período do usuário
                    primeira_cota_cdi = df_final['CDI_COTA'].iloc[0]
                    df_final['CDI_NORM'] = df_final['CDI_COTA'] / primeira_cota_cdi

                    st.session_state['df'] = df_final
                else:
                    # Se não for para comparar com CDI, usar apenas dados do fundo
                    df_final = df_fundo_completo[(df_fundo_completo['DT_COMPTC'] >= dt_ini_user) & (df_fundo_completo['DT_COMPTC'] <= dt_fim_user)].copy()
                    df_final = df_final.sort_values('DT_COMPTC').drop_duplicates(subset=['DT_COMPTC']).reset_index(drop=True)

                    if df_final.empty:
                        st.error("❌ Não há dados do fundo disponíveis para o período selecionado.")
                        st.session_state['df'] = pd.DataFrame()
                        st.stop()

                    primeira_cota_fundo = df_final['VL_QUOTA'].iloc[0]
                    df_final['VL_QUOTA_NORM'] = df_final['VL_QUOTA'] / primeira_cota_fundo
                    df_final['CDI_COTA'] = np.nan # Garante que a coluna exista, mas vazia
                    df_final['CDI_NORM'] = np.nan # Garante que a coluna exista, mas vazia
                    st.session_state['df'] = df_final

            except Exception as e:
                st.error(f"❌ Erro ao carregar os dados: {str(e)}")
                st.info("💡 Verifique se o CNPJ está correto e se há dados disponíveis para o período selecionado.")
                st.session_state['df'] = pd.DataFrame() # Limpa o dataframe em caso de erro
                st.stop()

# Verifica se há dados carregados para exibir o dashboard
if st.session_state['df'].empty:
    if st.session_state['cnpj_valido'] and st.session_state['periodo_valido']:
        st.info("Aguardando o carregamento dos dados. Por favor, clique em 'Carregar Dados'.")
    else:
        st.info("Por favor, insira o CNPJ do fundo e o período de análise na barra lateral e clique em 'Carregar Dados'.")
    st.stop()

# Se chegamos aqui, significa que st.session_state['df'] não está vazio e os dados foram carregados com sucesso.
df = st.session_state['df'].copy()
fund_info = st.session_state['fund_info']
tem_cdi = st.session_state['tem_cdi']

# --- Cálculos de Métricas ---
if not df.empty:
    # Retornos diários
    df['Retorno_Fundo'] = df['VL_QUOTA_NORM'].pct_change()
    if tem_cdi:
        df['Retorno_CDI'] = df['CDI_NORM'].pct_change()

    # Rentabilidade Histórica
    rentabilidade_fundo = (df['VL_QUOTA_NORM'].iloc[-1] / df['VL_QUOTA_NORM'].iloc[0]) - 1
    rentabilidade_cdi = (df['CDI_NORM'].iloc[-1] / df['CDI_NORM'].iloc[0]) - 1 if tem_cdi else 0

    # Volatilidade
    trading_days_in_year = 252
    vol_window = 21 # Janela para volatilidade móvel (aprox. 1 mês)
    if len(df) >= vol_window:
        df['Volatilidade'] = df['Retorno_Fundo'].rolling(window=vol_window).std() * np.sqrt(trading_days_in_year) * 100
        vol_hist = df['Retorno_Fundo'].std() * np.sqrt(trading_days_in_year) * 100
    else:
        df['Volatilidade'] = np.nan
        vol_hist = np.nan

    # Drawdown
    df['Peak'] = df['VL_QUOTA_NORM'].cummax()
    df['Drawdown'] = (df['VL_QUOTA_NORM'] / df['Peak'] - 1) * 100
    max_drawdown = df['Drawdown'].min()

    # VaR e ES (para retornos mensais - 21 dias úteis)
    VaR_95, VaR_99, ES_95, ES_99 = 0, 0, 0, 0 # Inicializa com 0
    if len(df) >= 21:
        df['Retorno_21d'] = df['VL_QUOTA_NORM'].pct_change(periods=21)
        returns_21d = df['Retorno_21d'].dropna()
        if not returns_21d.empty:
            VaR_95 = returns_21d.quantile(0.05)
            VaR_99 = returns_21d.quantile(0.01)
            ES_95 = returns_21d[returns_21d <= VaR_95].mean()
            ES_99 = returns_21d[returns_21d <= VaR_99].mean()
    else:
        st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias de retorno).")

    # Patrimônio Líquido Médio por Cotista
    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']
    df['Soma_Acumulada'] = (df['CAPTC_DIA'] - df['RESG_DIA']).cumsum()

    # CAGR Anual por Dia de Aplicação (do início ao fim)
    df['CAGR_Fundo'] = np.nan
    df['CAGR_CDI'] = np.nan

    # Última cota disponível no dataframe
    end_value_fundo = df['VL_QUOTA_NORM'].iloc[-1]
    end_value_cdi = df['CDI_NORM'].iloc[-1] if tem_cdi else np.nan

    # Calcula o CAGR para cada ponto 'i' até a última data
    # O loop vai até len(df) - trading_days_in_year para garantir que o último ponto plotado
    # tenha exatamente trading_days_in_year (252) dias úteis até o final.
    for i in range(len(df) - trading_days_in_year):
        initial_value_fundo = df['VL_QUOTA_NORM'].iloc[i]
        num_datas = len(df) - 1 - i # Número de intervalos (dias úteis) entre i e o final

        if num_datas >= trading_days_in_year: # Garante que há pelo menos 252 dias para anualizar
            cagr_fundo = ((end_value_fundo / initial_value_fundo) ** (trading_days_in_year / num_datas)) - 1
            df.loc[i, 'CAGR_Fundo'] = cagr_fundo * 100 # Em porcentagem

            if tem_cdi:
                initial_value_cdi = df['CDI_NORM'].iloc[i]
                cagr_cdi = ((end_value_cdi / initial_value_cdi) ** (trading_days_in_year / num_datas)) - 1
                df.loc[i, 'CAGR_CDI'] = cagr_cdi * 100 # Em porcentagem

    mean_cagr = df['CAGR_Fundo'].mean() if not df['CAGR_Fundo'].dropna().empty else 0

    # Excesso de Retorno Anualizado
    if tem_cdi:
        # Converte para fator de retorno antes da divisão
        df['EXCESSO_RETORNO_ANUALIZADO'] = ((1 + df['CAGR_Fundo']/100) / (1 + df['CAGR_CDI']/100) - 1) * 100
    else:
        df['EXCESSO_RETORNO_ANUALIZADO'] = np.nan

# --- Título Principal ---
st.title(f"Dashboard de Análise de Fundos")
st.markdown(f"<h2 style='text-align: center; color: {color_primary};'>{fund_info['DENOM_SOCIAL']}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #6c757d;'>CNPJ: {cnpj_input} | Início: {fund_info['DT_REG_CVM']}</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Cards de Métricas ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Rentabilidade Histórica", value=fmt_pct(rentabilidade_fundo))
with col2:
    if tem_cdi:
        st.metric(label="Rentabilidade CDI", value=fmt_pct(rentabilidade_cdi))
    else:
        st.metric(label="Rentabilidade CDI", value="N/A")
with col3:
    st.metric(label="Volatilidade Histórica", value=f"{vol_hist:.2f}% a.a.")
with col4:
    st.metric(label="Max Drawdown", value=f"{max_drawdown:.2f}%")

st.markdown("---")

# --- Tabs de Gráficos ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Rentabilidade e CAGR",
    "📉 Risco",
    "💰 Patrimônio e Captação",
    "👥 Cotistas",
    "🎯 Retornos em Janelas Móveis"
])

if not df.empty:
    with tab1:
        st.subheader("📈 Rentabilidade Acumulada")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['VL_QUOTA_NORM'],
            mode='lines',
            name='Fundo',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Fundo: %{y:.2f}<extra></extra>'
        ))
        if tem_cdi:
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['CDI_NORM'],
                mode='lines',
                name='CDI',
                line=dict(color=color_cdi, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>CDI: %{y:.2f}<extra></extra>'
            ))

        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Cota Normalizada (Base 1)",
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

        st.subheader("📊 CAGR Anual por Dia de Aplicação")

        df_plot_cagr = df.dropna(subset=['CAGR_Fundo']).copy()

        if not df_plot_cagr.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_plot_cagr['DT_COMPTC'],
                y=df_plot_cagr['CAGR_Fundo'],
                mode='lines',
                name='CAGR Fundo',
                line=dict(width=2.5, color=color_primary),
                fill='tozeroy',
                fillcolor='rgba(26, 95, 63, 0.1)',
                hovertemplate='<b>CAGR Fundo</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
            ))
            if tem_cdi:
                fig2.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=df_plot_cagr['CAGR_CDI'],
                    mode='lines',
                    name='CAGR CDI',
                    line=dict(width=2.5, color=color_cdi),
                    hovertemplate='<b>CAGR CDI</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
                ))
            # Linha de referência para o CAGR médio
            fig2.add_hline(y=mean_cagr, line_dash='dash', line_color='gray', line_width=1,
                           annotation_text=f"CAGR Médio: {mean_cagr:.2f}%",
                           annotation_position="bottom right",
                           annotation_font_color="gray")

            fig2.update_layout(
                xaxis_title="Data",
                yaxis_title="CAGR Anual (% a.a.)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                yaxis=dict(tickformat=".2f%"),
                font=dict(family="Inter, sans-serif"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df_plot_cagr['DT_COMPTC'].min(), df_plot_cagr['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("⚠️ Não há dados suficientes para calcular o CAGR Anual por Dia de Aplicação (mínimo de 252 dias úteis).")

        st.subheader("📊 Excesso de Retorno Anualizado (vs. CDI)")

        df_plot_excess = df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO']).copy()

        if tem_cdi and not df_plot_excess.empty:
            fig_excesso_retorno = go.Figure()
            fig_excesso_retorno.add_trace(go.Scatter(
                x=df_plot_excess['DT_COMPTC'],
                y=df_plot_excess['EXCESSO_RETORNO_ANUALIZADO'],
                mode='lines',
                name='Excesso de Retorno Anualizado',
                line=dict(width=2.5, color=color_primary), # Cor principal do fundo
                fill='tozeroy',
                fillcolor='rgba(26, 95, 63, 0.1)',
                hovertemplate='<b>Excesso de Retorno</b><br>Data: %{x|%d/%m/%Y}<br>Excesso: %{y:.2f}%<extra></extra>'
            ))
            # Linha de referência em 0%
            fig_excesso_retorno.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

            fig_excesso_retorno.update_layout(
                xaxis_title="Data",
                yaxis_title="Excesso de Retorno (% a.a.)",
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
            if not df_plot_excess.empty:
                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64, x_range=[df_plot_excess['DT_COMPTC'].min(), df_plot_excess['DT_COMPTC'].max()], x_autorange=False)
            else:
                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64)
            st.plotly_chart(fig_excesso_retorno, use_container_width=True)
        elif tem_cdi:
            st.warning("⚠️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado (verifique se há dados de CDI e CAGR para o período).")
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar o Excesso de Retorno Anualizado.")


    with tab2:
        st.subheader("📉 Drawdown Histórico")

        fig3 = go.Figure()

        # Drawdown do Fundo (APENAS - SEM CDI)
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

        fig3.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

        fig3.update_layout(
            xaxis_title="Data",
            yaxis_title="Drawdown (%)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        # Ajusta o range do eixo X para os dados de df
        fig3 = add_watermark_and_style(fig3, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"📊 Volatilidade Móvel ({vol_window} dias úteis)")

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

        df_plot_var = df.dropna(subset=['Retorno_21d']).copy()
        if not df_plot_var.empty:
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
                    line=dict(color=color_cdi, width=2.5),
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

        # --- NOVO GRÁFICO: Consistência em Janelas Móveis ---
        st.markdown("---") # Separador visual
        st.subheader("📈 Consistência em Janelas Móveis")

        if tem_cdi:
            consistency_data = []
            for nome, dias in janelas.items():
                fund_returns_window = df_returns[f'FUNDO_{nome}']
                cdi_returns_window = df_returns[f'CDI_{nome}']

                # Filtra para apenas onde ambos têm dados
                valid_comparisons = (fund_returns_window.notna()) & (cdi_returns_window.notna())

                if valid_comparisons.sum() > 0:
                    outperformed_count = (fund_returns_window[valid_comparisons] > cdi_returns_window[valid_comparisons]).sum()
                    total_comparisons = valid_comparisons.sum()
                    consistency_percentage = (outperformed_count / total_comparisons) * 100
                    consistency_data.append({'Janela': nome, 'Consistencia': consistency_percentage})
                else:
                    consistency_data.append({'Janela': nome, 'Consistencia': np.nan})

            df_consistency = pd.DataFrame(consistency_data).dropna(subset=['Consistencia'])

            if not df_consistency.empty:
                fig_consistency = go.Figure()
                fig_consistency.add_trace(go.Bar(
                    x=df_consistency['Janela'],
                    y=df_consistency['Consistencia'],
                    marker_color=color_primary,
                    hovertemplate='<b>Janela:</b> %{x}<br><b>Consistência:</b> %{y:.2f}%<extra></extra>'
                ))

                fig_consistency.update_layout(
                    xaxis_title="Janela Analisada",
                    yaxis_title="Frequência de Superação do CDI (%)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    yaxis=dict(tickformat=".2f%"), # Formata como porcentagem com 2 casas decimais
                    font=dict(family="Inter, sans-serif")
                )
                fig_consistency = add_watermark_and_style(fig_consistency, logo_base64)
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
