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
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stTextArea label { /* Adicionado stTextArea */
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.8rem !important;
        margin-bottom: 0.2rem !important;
        margin-top: 0 !important;
    }

    /* Reduzir espaçamento entre elementos */
    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stTextArea { /* Adicionado stTextArea */
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
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea { /* Adicionado textarea */
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

    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder { /* Adicionado textarea */
        color: #666666 !important;
        opacity: 0.8 !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus { /* Adicionado textarea */
        color: #000000 !important;
        border-color: #8ba888 !important;
        box-shadow: 0 4px 12px rgba(139, 168, 136, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stSidebar"] input:hover,
    [data-testid="stSidebar"] textarea:hover { /* Adicionado textarea */
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

# Sidebar com logo (SEM título "Configurações")
if logo_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" alt="Copaíba Invest"></div>',
        unsafe_allow_html=True
    )

# Input de CNPJ (agora text_area para múltiplos)
cnpj_input_raw = st.sidebar.text_area(
    "CNPJs dos Fundos (separados por vírgula ou nova linha)",
    value="",
    placeholder="00.000.000/0000-00, 11.111.111/1111-11",
    help="Digite um ou mais CNPJs com ou sem formatação"
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

# Opção para mostrar CDI
st.sidebar.markdown("#### Indicadores de Comparação")
mostrar_cdi = st.sidebar.checkbox("Comparar com CDI", value=True)

st.sidebar.markdown("---")

# Processar inputs de CNPJ
cnpjs_list_raw = [c.strip() for c in re.split(r'[,;\n]+', cnpj_input_raw) if c.strip()]
cnpjs_list = [limpar_cnpj(c) for c in cnpjs_list_raw]
cnpjs_list = [c for c in cnpjs_list if len(c) == 14] # Filtra apenas CNPJs válidos

# Validação
cnpj_valido = False
if cnpjs_list_raw:
    if not cnpjs_list:
        st.sidebar.error("❌ Nenhum CNPJ válido encontrado. Verifique a formatação (14 dígitos).")
    else:
        st.sidebar.success(f"✅ CNPJs válidos: {len(cnpjs_list)}")
        cnpj_valido = True

datas_validas = False
data_inicial_formatada = formatar_data_api(data_inicial_input)
data_final_formatada = formatar_data_api(data_final_input)

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

# Função para carregar dados da API
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
    if pd.isna(valor):
        return "N/A"
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_pct_port(x):
    if pd.isna(x):
        return "N/A"
    return f"{x*100:.2f}%".replace('.', ',')

# NOVO: Função para processar dados e calcular métricas para um único fundo
def process_single_fund_data(cnpj, data_ini_str, data_fim_str, mostrar_cdi, dt_ini_user, dt_fim_user):
    fund_metrics = {}
    df_fundo_completo = carregar_dados_api(cnpj, data_ini_str, data_fim_str)
    df_fundo_completo = df_fundo_completo.sort_values('DT_COMPTC').reset_index(drop=True)

    df_cdi_raw = pd.DataFrame()
    if mostrar_cdi and BCB_DISPONIVEL:
        df_cdi_raw = obter_dados_cdi_real(dt_ini_user, dt_fim_user)
        if not df_cdi_raw.empty:
            df_cdi_raw = df_cdi_raw.sort_values('DT_COMPTC').reset_index(drop=True)

    if not df_cdi_raw.empty:
        df_final = df_cdi_raw[['DT_COMPTC', 'cdi', 'VL_CDI_normalizado']].copy()
        df_final = df_final.merge(df_fundo_completo, on='DT_COMPTC', how='left')
    else:
        df_final = df_fundo_completo.copy()
        df_final.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado'] if col in df_final.columns], errors='ignore', inplace=True)

    df_final = df_final.sort_values('DT_COMPTC').reset_index(drop=True)

    fund_cols_to_ffill = ['VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST', 'CAPTC_DIA', 'RESG_DIA']
    for col in fund_cols_to_ffill:
        if col in df_final.columns:
            df_final[col] = df_final[col].ffill()

    df_final.dropna(subset=['VL_QUOTA'], inplace=True)

    df = df_final[(df_final['DT_COMPTC'] >= dt_ini_user) & (df_final['DT_COMPTC'] <= dt_fim_user)].copy()

    if df.empty:
        return pd.DataFrame(), fund_metrics # Retorna dataframe vazio e métricas vazias

    primeira_cota_fundo = df['VL_QUOTA'].iloc[0]
    df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota_fundo) - 1) * 100

    tem_cdi = False
    if mostrar_cdi and 'VL_CDI_normalizado' in df.columns:
        first_cdi_normalized_value_in_period = df['VL_CDI_normalizado'].iloc[0]
        df['CDI_COTA'] = df['VL_CDI_normalizado'] / first_cdi_normalized_value_in_period
        df['CDI_NORM'] = (df['CDI_COTA'] - 1) * 100
        tem_cdi = True
    else:
        df.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado', 'CDI_COTA', 'CDI_NORM'] if col in df.columns], errors='ignore', inplace=True)

    df = df.sort_values('DT_COMPTC').reset_index(drop=True)

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

    if not df.empty and len(df) > trading_days_in_year:
        end_value_fundo = df['VL_QUOTA'].iloc[-1]
        if tem_cdi:
            end_value_cdi = df['CDI_COTA'].iloc[-1]

        for i in range(len(df) - trading_days_in_year):
            initial_value_fundo = df['VL_QUOTA'].iloc[i]
            num_intervals = (len(df) - 1) - i

            if initial_value_fundo > 0 and num_intervals > 0:
                df.loc[i, 'CAGR_Fundo'] = ((end_value_fundo / initial_value_fundo) ** (trading_days_in_year / num_intervals) - 1) * 100

            if tem_cdi and 'CDI_COTA' in df.columns:
                initial_value_cdi = df['CDI_COTA'].iloc[i]
                if initial_value_cdi > 0 and num_intervals > 0:
                    df.loc[i, 'CAGR_CDI'] = ((end_value_cdi / initial_value_cdi) ** (trading_days_in_year / num_intervals) - 1) * 100

    mean_cagr = df['CAGR_Fundo'].mean() if 'CAGR_Fundo' in df.columns else 0
    if pd.isna(mean_cagr):
        mean_cagr = 0

    df['EXCESSO_RETORNO_ANUALIZADO'] = np.nan
    if tem_cdi and 'CAGR_Fundo' in df.columns and 'CAGR_CDI' in df.columns:
        valid_excess_return_indices = df.dropna(subset=['CAGR_Fundo', 'CAGR_CDI']).index
        if not valid_excess_return_indices.empty:
            df.loc[valid_excess_return_indices, 'EXCESSO_RETORNO_ANUALIZADO'] = (
                (1 + df.loc[valid_excess_return_indices, 'CAGR_Fundo'] / 100) /
                (1 + df.loc[valid_excess_return_indices, 'CAGR_CDI'] / 100) - 1
            ) * 100

    df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
    df_plot_var = df.dropna(subset=['Retorno_21d']).copy()
    VaR_95, VaR_99, ES_95, ES_99 = 0, 0, 0, 0
    if not df_plot_var.empty:
        VaR_95 = np.percentile(df_plot_var['Retorno_21d'], 5)
        VaR_99 = np.percentile(df_plot_var['Retorno_21d'], 1)
        ES_95 = df_plot_var.loc[df_plot_var['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
        ES_99 = df_plot_var.loc[df_plot_var['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()

    # --- Cálculos dos Novos Indicadores ---
    calmar_ratio, sterling_ratio, ulcer_index, martin_ratio, sharpe_ratio, sortino_ratio, information_ratio = [np.nan] * 7

    if tem_cdi and not df.empty and len(df) > trading_days_in_year:
        total_fund_return = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1
        total_cdi_return = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0]) - 1

        num_days_in_period = len(df)
        if num_days_in_period > 0:
            annualized_fund_return = (1 + total_fund_return)**(trading_days_in_year / num_days_in_period) - 1
            annualized_cdi_return = (1 + total_cdi_return)**(trading_days_in_year / num_days_in_period) - 1
        else:
            annualized_fund_return = 0
            annualized_cdi_return = 0

        annualized_fund_volatility = vol_hist / 100 if vol_hist else np.nan
        max_drawdown_value = df['Drawdown'].min() / 100 if not df['Drawdown'].empty else np.nan
        cagr_fund_decimal = mean_cagr / 100 if mean_cagr else np.nan

        drawdown_series = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1)
        squared_drawdowns = drawdown_series**2
        if not squared_drawdowns.empty and squared_drawdowns.mean() > 0:
            ulcer_index = np.sqrt(squared_drawdowns.mean())
        else:
            ulcer_index = np.nan

        downside_returns = df['Variacao_Perc'][df['Variacao_Perc'] < 0]
        if not downside_returns.empty:
            annualized_downside_volatility = downside_returns.std() * np.sqrt(trading_days_in_year)
        else:
            annualized_downside_volatility = np.nan

        if 'cdi' in df.columns and not df['Variacao_Perc'].empty:
            excess_daily_returns = df['Variacao_Perc'] - (df['cdi'] / 100)
            if not excess_daily_returns.empty:
                tracking_error = excess_daily_returns.std() * np.sqrt(trading_days_in_year)
            else:
                tracking_error = np.nan
        else:
            tracking_error = np.nan

        if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(max_drawdown_value) and max_drawdown_value != 0:
            calmar_ratio = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value)
            sterling_ratio = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value)

        if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(ulcer_index) and ulcer_index != 0:
            martin_ratio = (cagr_fund_decimal - annualized_cdi_return) / ulcer_index

        if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0:
            sharpe_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_fund_volatility

        if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0:
            sortino_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_downside_volatility

        if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(tracking_error) and tracking_error != 0:
            information_ratio = (annualized_fund_return - annualized_cdi_return) / tracking_error

    fund_metrics = {
        'Patrimônio Líquido': df['VL_PATRIM_LIQ'].iloc[-1],
        'Rentabilidade Acumulada': df['VL_QUOTA_NORM'].iloc[-1] / 100,
        'CAGR Médio': mean_cagr / 100,
        'Max Drawdown': df['Drawdown'].min() / 100,
        'Vol. Histórica': vol_hist / 100,
        'Sharpe Ratio': sharpe_ratio,
        'Sortino Ratio': sortino_ratio,
        'Information Ratio': information_ratio,
        'Calmar Ratio': calmar_ratio,
        'Sterling Ratio': sterling_ratio,
        'Ulcer Index': ulcer_index,
        'Martin Ratio': martin_ratio,
        'VaR 95%': VaR_95,
        'VaR 99%': VaR_99,
        'ES 95%': ES_95,
        'ES 99%': ES_99,
        'Tem CDI': tem_cdi,
        'Dados VaR Suficientes': not df_plot_var.empty,
        'Dados CAGR Suficientes': not df.empty and len(df) > trading_days_in_year
    }

    return df, fund_metrics

# Verificar se deve carregar os dados
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
    st.session_state.processed_funds_dfs = {}
    st.session_state.fund_metrics_summary = {}
    st.session_state.cnpjs_list = []
    st.session_state.data_ini = None
    st.session_state.data_fim = None
    st.session_state.mostrar_cdi = False

if carregar_button and cnpj_valido and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpjs_list = cnpjs_list
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada
    st.session_state.mostrar_cdi = mostrar_cdi

    st.session_state.processed_funds_dfs = {}
    st.session_state.fund_metrics_summary = {}

    dt_ini_user = datetime.strptime(st.session_state.data_ini, '%Y%m%d')
    dt_fim_user = datetime.strptime(st.session_state.data_fim, '%Y%m%d')

    with st.spinner('🔄 Carregando e processando dados dos fundos...'):
        for cnpj in st.session_state.cnpjs_list:
            df_fund, metrics_fund = process_single_fund_data(
                cnpj,
                st.session_state.data_ini,
                st.session_state.data_fim,
                st.session_state.mostrar_cdi,
                dt_ini_user,
                dt_fim_user
            )
            if not df_fund.empty:
                st.session_state.processed_funds_dfs[cnpj] = df_fund
                st.session_state.fund_metrics_summary[cnpj] = metrics_fund
            else:
                st.warning(f"⚠️ Não foi possível carregar dados para o CNPJ {cnpj} no período selecionado.")

if not st.session_state.dados_carregados or not st.session_state.processed_funds_dfs:
    st.info("👈 Preencha os campos na barra lateral e clique em 'Carregar Dados' para começar a análise.")

    st.markdown("""
    ### 📋 Como usar:

    1.  **CNPJs dos Fundos**: Digite um ou mais CNPJs (separados por vírgula ou nova linha)
    2.  **Data Inicial**: Digite a data inicial no formato DD/MM/AAAA
    3.  **Data Final**: Digite a data final no formato DD/MM/AAAA
    4.  **Indicadores**: Marque a opção "Comparar com CDI" se desejar
    5.  Clique em **Carregar Dados** para visualizar as análises

    ---

    ### 📊 Análises disponíveis:
    - Rentabilidade histórica e CAGR (com comparação ao CDI)
    - Análise de risco (Drawdown, Volatilidade, VaR)
    - Evolução patrimonial e captação
    - Perfil de cotistas
    - Retornos em janelas móveis (com comparação ao CDI)
    """)

    st.stop()

# Cores
color_primary = '#1a5f3f'  # Verde escuro para o fundo
color_secondary = '#6b9b7f'
color_danger = '#dc3545'
color_cdi = '#f0b429'  # Amarelo para o CDI

# Exibir cards de métricas no topo APENAS se for um único fundo
if len(st.session_state.cnpjs_list) == 1:
    cnpj_unico = st.session_state.cnpjs_list[0]
    metrics = st.session_state.fund_metrics_summary.get(cnpj_unico, {})
    df = st.session_state.processed_funds_dfs.get(cnpj_unico)

    if df is not None and not df.empty:
        st.markdown(f"<h2>Análise Detalhada do Fundo: {cnpj_unico}</h2>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Patrimônio Líquido", format_brl(metrics.get('Patrimônio Líquido')))
        with col2:
            st.metric("Rentabilidade Acumulada", fmt_pct_port(metrics.get('Rentabilidade Acumulada')))
        with col3:
            st.metric("CAGR Médio", fmt_pct_port(metrics.get('CAGR Médio')))
        with col4:
            st.metric("Max Drawdown", fmt_pct_port(metrics.get('Max Drawdown')))
        with col5:
            st.metric("Vol. Histórica", fmt_pct_port(metrics.get('Vol. Histórica')))
    else:
        st.error(f"❌ Não foi possível exibir as métricas de topo para o CNPJ {cnpj_unico}.")
        st.stop() # Parar aqui se não houver dados para o único fundo

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Rentabilidade", "Risco", "Patrimônio e Captação",
        "Cotistas", "Janelas Móveis"
    ])

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

        if metrics.get('Tem CDI'):
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
        fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig1, use_container_width=True)

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
                y=[metrics.get('CAGR Médio') * 100] * len(df_plot_cagr),
                mode='lines',
                line=dict(dash='dash', color=color_secondary, width=2),
                name=f'CAGR Médio ({metrics.get("CAGR Médio")*100:.2f}%)'
            ))

            if metrics.get('Tem CDI') and 'CAGR_CDI' in df_plot_cagr.columns:
                fig2.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=df_plot_cagr['CAGR_CDI'],
                    mode='lines',
                    name='CAGR do CDI',
                    line=dict(color=color_cdi, width=2.5),
                    hovertemplate='<b>CAGR do CDI</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
                ))
        else:
            st.warning("⚠️ Não há dados suficientes para calcular o CAGR (mínimo de 1 ano de dados).")

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
        if not df_plot_cagr.empty:
            fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df_plot_cagr['DT_COMPTC'].min(), df_plot_cagr['DT_COMPTC'].max()], x_autorange=False)
        else:
            fig2 = add_watermark_and_style(fig2, logo_base64)
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Excesso de Retorno Anualizado")

        if metrics.get('Tem CDI') and not df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO']).empty:
            fig_excesso_retorno = go.Figure()

            fig_excesso_retorno.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['EXCESSO_RETORNO_ANUALIZADO'],
                mode='lines',
                name='Excesso de Retorno Anualizado',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='<b>Excesso de Retorno</b><br>Data: %{x|%d/%m/%Y}<br>Excesso: %{y:.2f}%<extra></extra>'
            ))

            fig_excesso_retorno.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

            fig_excesso_retorno.update_layout(
                xaxis_title="Data",
                yaxis_title="Excesso de Retorno (% a.a)",
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
            df_plot_excess = df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO']).copy()
            if not df_plot_excess.empty:
                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64, x_range=[df_plot_excess['DT_COMPTC'].min(), df_plot_excess['DT_COMPTC'].max()], x_autorange=False)
            else:
                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64)
            st.plotly_chart(fig_excesso_retorno, use_container_width=True)
        elif st.session_state.mostrar_cdi:
            st.warning("⚠️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado (verifique se há dados de CDI e CAGR para o período).")
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar o Excesso de Retorno Anualizado.")

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

        fig3.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

        fig3.update_layout(
            xaxis_title="Data",
            yaxis_title="Drawdown (%)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        fig3 = add_watermark_and_style(fig3, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"Volatilidade Móvel ({vol_window} dias úteis)")

        fig4 = go.Figure()

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
            y=[metrics.get('Vol. Histórica') * 100] * len(df),
            mode='lines',
            line=dict(dash='dash', color=color_secondary, width=2),
            name=f'Vol. Histórica ({metrics.get("Vol. Histórica")*100:.2f}%)'
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
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Value at Risk (VaR) e Expected Shortfall (ES)")

        if metrics.get('Dados VaR Suficientes'):
            df_plot_var = df.dropna(subset=['Retorno_21d']).copy()
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
                y=[metrics.get('VaR 95%') * 100, metrics.get('VaR 95%') * 100],
                mode='lines',
                name='VaR 95%',
                line=dict(dash='dot', color='orange', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[metrics.get('VaR 99%') * 100, metrics.get('VaR 99%') * 100],
                mode='lines',
                name='VaR 99%',
                line=dict(dash='dot', color='red', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[metrics.get('ES 95%') * 100, metrics.get('ES 95%') * 100],
                mode='lines',
                name='ES 95%',
                line=dict(dash='dash', color='orange', width=2)
            ))
            fig5.add_trace(go.Scatter(
                x=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()],
                y=[metrics.get('ES 99%') * 100, metrics.get('ES 99%') * 100],
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
            fig5 = add_watermark_and_style(fig5, logo_base64, x_range=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig5, use_container_width=True)

            st.info(f"""
            **Este gráfico mostra que, em um período de 1 mês:**

            • Há **99%** de confiança de que o fundo não cairá mais do que **{fmt_pct_port(metrics.get('VaR 99%'))} (VaR)**,
            e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(metrics.get('ES 99%'))} (ES)**.

            • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(metrics.get('VaR 95%'))} (VaR)**,
            e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(metrics.get('ES 95%'))} (ES)**.
            """)
        else:
            st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias de retorno).")

        st.subheader("Métricas de Risco-Retorno")

        if metrics.get('Tem CDI') and metrics.get('Dados CAGR Suficientes'):
            st.markdown("#### RISCO MEDIDO PELA VOLATILIDADE:")
            col_vol_1, col_vol_2 = st.columns(2)

            with col_vol_1:
                st.metric("Sharpe Ratio", f"{metrics.get('Sharpe Ratio'):.2f}" if not pd.isna(metrics.get('Sharpe Ratio')) else "N/A")
                st.info("""
                **Sharpe Ratio:** Mede o excesso de retorno do fundo (acima do CDI) por unidade de **volatilidade total** (risco). Quanto maior o Sharpe, melhor o retorno para o nível de risco assumido.
                *   **Interpretação Geral:**
                    *   **< 1.0:** Subótimo, o retorno não compensa adequadamente o risco.
                    *   **1.0 - 1.99:** Bom, o fundo gera um bom retorno para o risco.
                    *   **2.0 - 2.99:** Muito Bom, excelente retorno ajustado ao risco.
                    *   **≥ 3.0:** Excepcional, performance muito consistente.
                """)
            with col_vol_2:
                st.metric("Sortino Ratio", f"{metrics.get('Sortino Ratio'):.2f}" if not pd.isna(metrics.get('Sortino Ratio')) else "N/A")
                st.info("""
                **Sortino Ratio:** Similar ao Sharpe, mas foca apenas na **volatilidade de baixa** (downside volatility). Ele mede o excesso de retorno por unidade de risco de queda. É útil para investidores que se preocupam mais com perdas do que com a volatilidade geral.
                *   **Interpretação Geral:**
                    *   **< 0.0:** Retorno não cobre o risco de queda.
                    *   **0.0 - 1.0:** Aceitável, o fundo gera retorno positivo para o risco de queda.
                    *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de perdas.
                """)

            col_vol_3, col_vol_4 = st.columns(2)
            with col_vol_3:
                st.metric("Information Ratio", f"{metrics.get('Information Ratio'):.2f}" if not pd.isna(metrics.get('Information Ratio')) else "N/A")
                st.info("""
                **Information Ratio:** Mede a capacidade do gestor de gerar retornos acima de um benchmark (aqui, o CDI), ajustado pelo **tracking error** (risco de desvio em relação ao benchmark). Um valor alto indica que o gestor consistentemente superou o benchmark com um risco de desvio razoável.
                *   **Interpretação Geral:**
                    *   **< 0.0:** O fundo está consistentemente abaixo do benchmark.
                    *   **0.0 - 0.5:** Habilidade modesta em superar o benchmark.
                    *   **0.5 - 1.0:** Boa habilidade e consistência em superar o benchmark.
                    *   **> 1.0:** Excelente habilidade e forte superação consistente do benchmark.
                """)
            with col_vol_4:
                st.metric("Treynor Ratio", "Não Calculável" if not metrics.get('Tem CDI') else "N/A")
                st.info("""
                **Treynor Ratio:** Mede o excesso de retorno por unidade de **risco sistemático (Beta)**. O Beta mede a sensibilidade do fundo aos movimentos do mercado.
                *   **Interpretação:** Um valor mais alto é preferível. É mais útil para comparar fundos com Betas semelhantes.
                *   **Observação:** *Não é possível calcular este índice sem dados de um índice de mercado (benchmark) para determinar o Beta do fundo.*
                """)

            st.markdown("#### RISCO MEDIDO PELO DRAWDOWN:")
            col_dd_1, col_dd_2 = st.columns(2)

            with col_dd_1:
                st.metric("Calmar Ratio", f"{metrics.get('Calmar Ratio'):.2f}" if not pd.isna(metrics.get('Calmar Ratio')) else "N/A")
                st.info("""
                **Calmar Ratio:** Mede o retorno ajustado ao risco, comparando o **CAGR** (retorno anualizado) do fundo com o seu **maior drawdown** (maior queda). Um valor mais alto indica que o fundo gerou bons retornos sem grandes perdas.
                *   **Interpretação Geral:**
                    *   **< 0.0:** Retorno negativo ou drawdown muito grande.
                    *   **0.0 - 0.5:** Aceitável, mas com espaço para melhoria.
                    *   **0.5 - 1.0:** Bom, o fundo gerencia bem o risco de drawdown.
                    *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de grandes quedas.
                """)
            with col_dd_2:
                st.metric("Sterling Ratio", f"{metrics.get('Sterling Ratio'):.2f}" if not pd.isna(metrics.get('Sterling Ratio')) else "N/A")
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
                st.metric("Ulcer Index", f"{metrics.get('Ulcer Index'):.2f}" if not pd.isna(metrics.get('Ulcer Index')) else "N/A")
                st.info("""
                **Ulcer Index:** Mede a profundidade e a duração dos drawdowns (quedas). Quanto menor o índice, menos dolorosas e mais curtas foram as quedas do fundo. É uma medida de risco que foca na "dor" do investidor.
                *   **Interpretação Geral:**
                    *   **< 1.0:** Baixo risco, fundo relativamente estável.
                    *   **1.0 - 2.0:** Risco moderado, com quedas mais frequentes ou profundas.
                    *   **> 2.0:** Alto risco, fundo com quedas significativas e/ou duradouras.
                """)
            with col_dd_4:
                st.metric("Martin Ratio", f"{metrics.get('Martin Ratio'):.2f}" if not pd.isna(metrics.get('Martin Ratio')) else "N/A")
                st.info("""
                **Martin Ratio:** Avalia o retorno ajustado ao risco dividindo o excesso de retorno anualizado (acima do CDI) pelo **Ulcer Index**. Um valor mais alto indica um melhor desempenho em relação ao risco de drawdown.
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

        elif not metrics.get('Tem CDI'):
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar as Métricas de Risco-Retorno.")
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
                text=df_monthly['Captacao_Liquida'].apply(format_brl), # Adiciona texto nas barras
                textposition='outside',
                textfont=dict(color='black', size=10)
            )
        ])

        fig7.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif"),
            yaxis=dict(range=[df_monthly['Captacao_Liquida'].min() * 1.2, df_monthly['Captacao_Liquida'].max() * 1.2]) # Ajusta range para texto
        )
        if not df_monthly.empty:
            fig7 = add_watermark_and_style(fig7, logo_base64, x_range=[df_monthly.index.min(), df_monthly.index.max()], x_autorange=False)
        else:
            fig7 = add_watermark_and_style(fig7, logo_base64)
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
            if len(df_returns) > dias:
                df_returns[f'FUNDO_{nome}'] = df_returns['VL_QUOTA'] / df_returns['VL_QUOTA'].shift(dias) - 1
                if metrics.get('Tem CDI'):
                    df_returns[f'CDI_{nome}'] = df_returns['CDI_COTA'] / df_returns['CDI_COTA'].shift(dias) - 1
            else:
                df_returns[f'FUNDO_{nome}'] = np.nan
                if metrics.get('Tem CDI'):
                    df_returns[f'CDI_{nome}'] = np.nan

        janela_selecionada = st.selectbox("Selecione o período:", list(janelas.keys()))

        if not df_returns[f'FUNDO_{janela_selecionada}'].dropna().empty:
            fig9 = go.Figure()

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

            if metrics.get('Tem CDI'):
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
            df_plot_returns = df_returns.dropna(subset=[f'FUNDO_{janela_selecionada}']).copy()
            if not df_plot_returns.empty:
                fig9 = add_watermark_and_style(fig9, logo_base64, x_range=[df_plot_returns['DT_COMPTC'].min(), df_plot_returns['DT_COMPTC'].max()], x_autorange=False)
            else:
                fig9 = add_watermark_and_style(fig9, logo_base64)
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada}.")

        st.subheader("Consistência em Janelas Móveis")

        if metrics.get('Tem CDI'):
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
                    text=df_consistency['Consistencia'].apply(lambda x: f'{x:.2f}%'),
                    textposition='outside',
                    textfont=dict(color='black', size=12),
                    hovertemplate='<b>Janela:</b> %{x}<br><b>Consistência:</b> %{y:.2f}%<extra></extra>'
                ))

                fig_consistency.update_layout(
                    xaxis_title="Janela (meses)",
                    yaxis_title="Percentual de Superação do CDI (%)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Inter, sans-serif"),
                    yaxis=dict(range=[0, 110], ticksuffix="%")
                )
                fig_consistency = add_watermark_and_style(fig_consistency, logo_base64, x_autorange=True)
                st.plotly_chart(fig_consistency, use_container_width=True)
            else:
                st.warning("⚠️ Não há dados suficientes para calcular a Consistência em Janelas Móveis.")
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar a Consistência em Janelas Móveis.")

# Se múltiplos fundos forem selecionados, exibir a tabela de métricas de risco-retorno
elif len(st.session_state.cnpjs_list) > 1:
    st.markdown("<h2>Comparativo de Fundos</h2>", unsafe_allow_html=True)
    st.warning("⚠️ Para análise detalhada e gráficos individuais, selecione apenas um CNPJ.")

    if st.session_state.fund_metrics_summary:
        # Coletar métricas para a tabela
        table_data = {}
        metric_names = [
            'Sharpe Ratio', 'Sortino Ratio', 'Information Ratio',
            'Calmar Ratio', 'Sterling Ratio', 'Ulcer Index', 'Martin Ratio'
        ]

        for metric in metric_names:
            table_data[metric] = {
                cnpj: st.session_state.fund_metrics_summary[cnpj].get(metric)
                for cnpj in st.session_state.cnpjs_list
                if cnpj in st.session_state.fund_metrics_summary
            }

        df_metrics_table = pd.DataFrame(table_data).T
        df_metrics_table.index.name = "Métrica"

        # Formatar os valores da tabela
        def format_metric_value(value):
            if pd.isna(value):
                return "N/A"
            return f"{value:.2f}".replace('.', ',')

        st.subheader("Métricas de Risco-Retorno Comparativas")
        st.dataframe(df_metrics_table.applymap(format_metric_value), use_container_width=True)

        # Explicações das métricas em um expander
        with st.expander("Clique para ver as explicações das Métricas de Risco-Retorno"):
            st.markdown("#### RISCO MEDIDO PELA VOLATILIDADE:")
            st.info("""
            **Sharpe Ratio:** Mede o excesso de retorno do fundo (acima do CDI) por unidade de **volatilidade total** (risco). Quanto maior o Sharpe, melhor o retorno para o nível de risco assumido.
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
            **Information Ratio:** Mede a capacidade do gestor de gerar retornos acima de um benchmark (aqui, o CDI), ajustado pelo **tracking error** (risco de desvio em relação ao benchmark). Um valor alto indica que o gestor consistentemente superou o benchmark com um risco de desvio razoável.
            *   **Interpretação Geral:**
                *   **< 0.0:** O fundo está consistentemente abaixo do benchmark.
                *   **0.0 - 0.5:** Habilidade modesta em superar o benchmark.
                *   **0.5 - 1.0:** Boa habilidade e consistência em superar o benchmark.
                *   **> 1.0:** Excelente habilidade e forte superação consistente do benchmark.
            """)
            st.info("""
            **Treynor Ratio:** Mede o excesso de retorno por unidade de **risco sistemático (Beta)**. O Beta mede a sensibilidade do fundo aos movimentos do mercado.
            *   **Interpretação:** Um valor mais alto é preferível. É mais útil para comparar fundos com Betas semelhantes.
            *   **Observação:** *Não é possível calcular este índice sem dados de um índice de mercado (benchmark) para determinar o Beta do fundo.*
            """)

            st.markdown("#### RISCO MEDIDO PELO DRAWDOWN:")
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
                *   **> 1.0:** Bom, o fundo entrega um bom retorno considerando a "dor" dos drawdowns.
            """)
    else:
        st.warning("⚠️ Não há dados disponíveis para nenhum dos fundos selecionados para comparação.")

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
