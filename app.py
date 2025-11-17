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
import plotly.express as px # Importar para cores automáticas

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
    [data-testid="stSidebar"] .stTextArea label,
    [data-testid="stSidebar"] .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 0.8rem !important;
        margin-bottom: 0.2rem !important;
        margin-top: 0 !important;
    }

    /* Reduzir espaçamento entre elementos */
    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stTextArea,
    [data-testid="stSidebar"] .stSelectbox {
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
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
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
    [data-testid="stSidebar"] textarea::placeholder {
        color: #666666 !important;
        opacity: 0.8 !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:focus {
        color: #000000 !important;
        border-color: #8ba888 !important;
        box-shadow: 0 4px 12px rgba(139, 168, 136, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stSidebar"] input:hover,
    [data-testid="stSidebar"] textarea:hover,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {
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
def limpar_cnpj(cnpj_str):
    if not cnpj_str:
        return []
    # Divide a string por vírgulas ou quebras de linha, remove espaços e filtra vazios
    cnpjs = [re.sub(r'\D', '', c.strip()) for c in re.split(r'[,;\n]+', cnpj_str) if c.strip()]
    return cnpjs

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
        # A biblioteca `bcb` já lida com o `start` e `end` diretamente.
        # A memória do usuário sobre "10 anos" pode se referir à disponibilidade máxima,
        # mas para o cálculo, usamos o período exato solicitado.
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

# Input de CNPJ (agora múltiplos)
cnpjs_input_raw = st.sidebar.text_area(
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

# Processar inputs
cnpjs_limpos = limpar_cnpj(cnpjs_input_raw)
data_inicial_formatada = formatar_data_api(data_inicial_input)
data_final_formatada = formatar_data_api(data_final_input)

# Validação
cnpjs_validos = False
if cnpjs_limpos:
    invalid_cnpjs = [cnpj for cnpj in cnpjs_limpos if len(cnpj) != 14]
    if invalid_cnpjs:
        st.sidebar.error(f"❌ CNPJs inválidos (devem ter 14 dígitos): {', '.join(invalid_cnpjs)}")
    else:
        st.sidebar.success(f"✅ CNPJs: {', '.join(cnpjs_limpos)}")
        cnpjs_validos = True
else:
    st.sidebar.warning("⚠️ Digite pelo menos um CNPJ.")

datas_validas = False
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
carregar_button = st.sidebar.button("Carregar Dados", type="primary", disabled=not (cnpjs_validos and datas_validas))

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

    try:
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
    except urllib.error.HTTPError as e:
        st.error(f"❌ Erro HTTP ao carregar dados para CNPJ {cnpj}: {e.code} - {e.reason}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados para CNPJ {cnpj}: {str(e)}")
        return pd.DataFrame()

# Funções de formatação
def format_brl(valor):
    if pd.isna(valor):
        return "N/A"
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_pct_port(x):
    if pd.isna(x):
        return "N/A"
    return f"{x*100:.2f}%".replace('.', ',')

def fmt_pct_port_no_mult(x):
    if pd.isna(x):
        return "N/A"
    return f"{x:.2f}%".replace('.', ',')

# Função para calcular métricas de um único fundo
def calculate_single_fund_metrics(df_fund, df_cdi_period, fund_name, dt_ini_user, dt_fim_user, tem_cdi):
    metrics = {}
    trading_days_in_year = 252

    # Filtrar o dataframe do fundo para o período exato do usuário
    df_fund_filtered = df_fund[(df_fund['DT_COMPTC'] >= dt_ini_user) & (df_fund['DT_COMPTC'] <= dt_fim_user)].copy()
    if df_fund_filtered.empty:
        return {fund_name: {
            "Patrimônio Líquido": np.nan,
            "Rentabilidade Acumulada": np.nan,
            "CAGR Médio": np.nan,
            "Max Drawdown": np.nan,
            "Vol. Histórica": np.nan,
            "Sharpe Ratio": np.nan,
            "Sortino Ratio": np.nan,
            "Information Ratio": np.nan,
            "Calmar Ratio": np.nan,
            "Sterling Ratio": np.nan,
            "Ulcer Index": np.nan,
            "Martin Ratio": np.nan,
            "Treynor Ratio": np.nan # Não calculável aqui
        }}

    df_fund_filtered = df_fund_filtered.sort_values('DT_COMPTC').reset_index(drop=True)

    # Re-normalizar a cota do fundo para começar em 1.0 (0% de rentabilidade)
    primeira_cota_fundo = df_fund_filtered['VL_QUOTA'].iloc[0]
    df_fund_filtered['VL_QUOTA_NORM'] = ((df_fund_filtered['VL_QUOTA'] / primeira_cota_fundo) - 1) * 100

    # Métricas básicas
    metrics["Patrimônio Líquido"] = df_fund_filtered['VL_PATRIM_LIQ'].iloc[-1]
    metrics["Rentabilidade Acumulada"] = df_fund_filtered['VL_QUOTA_NORM'].iloc[-1] / 100

    df_fund_filtered['Max_VL_QUOTA'] = df_fund_filtered['VL_QUOTA'].cummax()
    df_fund_filtered['Drawdown'] = (df_fund_filtered['VL_QUOTA'] / df_fund_filtered['Max_VL_QUOTA'] - 1) * 100
    metrics["Max Drawdown"] = df_fund_filtered['Drawdown'].min() / 100

    df_fund_filtered['Variacao_Perc'] = df_fund_filtered['VL_QUOTA'].pct_change()
    vol_hist = df_fund_filtered['Variacao_Perc'].std() * np.sqrt(trading_days_in_year) * 100
    metrics["Vol. Histórica"] = vol_hist / 100

    # CAGR
    df_fund_filtered['CAGR_Fundo'] = np.nan
    if len(df_fund_filtered) > trading_days_in_year:
        end_value_fundo = df_fund_filtered['VL_QUOTA'].iloc[-1]
        for i in range(len(df_fund_filtered) - trading_days_in_year):
            initial_value_fundo = df_fund_filtered['VL_QUOTA'].iloc[i]
            num_intervals = (len(df_fund_filtered) - 1) - i
            if initial_value_fundo > 0 and num_intervals > 0:
                df_fund_filtered.loc[i, 'CAGR_Fundo'] = ((end_value_fundo / initial_value_fundo) ** (trading_days_in_year / num_intervals) - 1) * 100
    mean_cagr = df_fund_filtered['CAGR_Fundo'].mean() if 'CAGR_Fundo' in df_fund_filtered.columns else 0
    if pd.isna(mean_cagr):
        mean_cagr = 0
    metrics["CAGR Médio"] = mean_cagr / 100

    # Métricas de Risco-Retorno (se CDI disponível)
    if tem_cdi and not df_cdi_period.empty:
        # Merge CDI com o fundo para o período de cálculo
        df_merged = pd.merge(df_fund_filtered, df_cdi_period[['DT_COMPTC', 'cdi', 'VL_CDI_normalizado']], on='DT_COMPTC', how='inner')
        if df_merged.empty:
            st.warning(f"⚠️ Não há dados de CDI para o fundo {fund_name} no período selecionado para cálculo de métricas de risco-retorno.")
            return {fund_name: {k: np.nan for k in metrics.keys()} | {
                "Sharpe Ratio": np.nan, "Sortino Ratio": np.nan, "Information Ratio": np.nan,
                "Calmar Ratio": np.nan, "Sterling Ratio": np.nan, "Ulcer Index": np.nan, "Martin Ratio": np.nan,
                "Treynor Ratio": np.nan
            }}

        # Re-normaliza CDI para o período do merge
        first_cdi_normalized_value_in_period = df_merged['VL_CDI_normalizado'].iloc[0]
        df_merged['CDI_COTA'] = df_merged['VL_CDI_normalizado'] / first_cdi_normalized_value_in_period
        df_merged['CDI_NORM'] = (df_merged['CDI_COTA'] - 1) * 100

        # Recalcula CAGR do CDI para o período
        df_merged['CAGR_CDI'] = np.nan
        if len(df_merged) > trading_days_in_year:
            end_value_cdi = df_merged['CDI_COTA'].iloc[-1]
            for i in range(len(df_merged) - trading_days_in_year):
                initial_value_cdi = df_merged['CDI_COTA'].iloc[i]
                num_intervals = (len(df_merged) - 1) - i
                if initial_value_cdi > 0 and num_intervals > 0:
                    df_merged.loc[i, 'CAGR_CDI'] = ((end_value_cdi / initial_value_cdi) ** (trading_days_in_year / num_intervals) - 1) * 100
        mean_cagr_cdi = df_merged['CAGR_CDI'].mean() if 'CAGR_CDI' in df_merged.columns else 0
        if pd.isna(mean_cagr_cdi):
            mean_cagr_cdi = 0

        # Retorno total do fundo e CDI no período
        total_fund_return = (df_merged['VL_QUOTA'].iloc[-1] / df_merged['VL_QUOTA'].iloc[0]) - 1
        total_cdi_return = (df_merged['CDI_COTA'].iloc[-1] / df_merged['CDI_COTA'].iloc[0]) - 1

        # Anualização dos retornos totais para consistência
        num_days_in_period = len(df_merged)
        if num_days_in_period > 0:
            annualized_fund_return = (1 + total_fund_return)**(trading_days_in_year / num_days_in_period) - 1
            annualized_cdi_return = (1 + total_cdi_return)**(trading_days_in_year / num_days_in_period) - 1
        else:
            annualized_fund_return = 0
            annualized_cdi_return = 0

        annualized_fund_volatility = metrics["Vol. Histórica"] # Já em decimal
        max_drawdown_value = metrics["Max Drawdown"] # Já em decimal
        cagr_fund_decimal = metrics["CAGR Médio"] # Já em decimal

        # Ulcer Index
        drawdown_series = (df_merged['VL_QUOTA'] / df_merged['Max_VL_QUOTA'] - 1)
        squared_drawdowns = drawdown_series**2
        ulcer_index = np.sqrt(squared_drawdowns.mean()) if not squared_drawdowns.empty and squared_drawdowns.mean() > 0 else np.nan

        # Downside Volatility
        downside_returns = df_merged['Variacao_Perc'][df_merged['Variacao_Perc'] < 0]
        annualized_downside_volatility = downside_returns.std() * np.sqrt(trading_days_in_year) if not downside_returns.empty else np.nan

        # Tracking Error
        tracking_error = np.nan
        if 'cdi' in df_merged.columns and not df_merged['Variacao_Perc'].empty:
            excess_daily_returns = df_merged['Variacao_Perc'] - (df_merged['cdi'] / 100)
            if not excess_daily_returns.empty:
                tracking_error = excess_daily_returns.std() * np.sqrt(trading_days_in_year)

        # --- Cálculo dos Ratios ---
        sharpe_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_fund_volatility if not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0 else np.nan
        sortino_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_downside_volatility if not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0 else np.nan
        information_ratio = (annualized_fund_return - annualized_cdi_return) / tracking_error if not pd.isna(tracking_error) and tracking_error != 0 else np.nan
        calmar_ratio = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value) if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(max_drawdown_value) and max_drawdown_value != 0 else np.nan
        sterling_ratio = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value) if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(max_drawdown_value) and max_drawdown_value != 0 else np.nan # Simplificado para Max Drawdown
        martin_ratio = (cagr_fund_decimal - annualized_cdi_return) / ulcer_index if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(ulcer_index) and ulcer_index != 0 else np.nan

        metrics["Sharpe Ratio"] = sharpe_ratio
        metrics["Sortino Ratio"] = sortino_ratio
        metrics["Information Ratio"] = information_ratio
        metrics["Calmar Ratio"] = calmar_ratio
        metrics["Sterling Ratio"] = sterling_ratio
        metrics["Ulcer Index"] = ulcer_index
        metrics["Martin Ratio"] = martin_ratio
        metrics["Treynor Ratio"] = np.nan # Não calculável sem Beta

    else:
        metrics.update({
            "Sharpe Ratio": np.nan, "Sortino Ratio": np.nan, "Information Ratio": np.nan,
            "Calmar Ratio": np.nan, "Sterling Ratio": np.nan, "Ulcer Index": np.nan, "Martin Ratio": np.nan,
            "Treynor Ratio": np.nan
        })

    return {fund_name: metrics}

# Verificar se deve carregar os dados
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
    st.session_state.all_funds_data = {}
    st.session_state.cdi_data = pd.DataFrame()
    st.session_state.dt_ini_user = None
    st.session_state.dt_fim_user = None
    st.session_state.mostrar_cdi = True
    st.session_state.cnpjs_carregados = []

if carregar_button and cnpjs_validos and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpjs_carregados = cnpjs_limpos
    st.session_state.data_ini_str = data_inicial_formatada
    st.session_state.data_fim_str = data_final_formatada
    st.session_state.dt_ini_user = datetime.strptime(data_inicial_formatada, '%Y%m%d')
    st.session_state.dt_fim_user = datetime.strptime(data_final_formatada, '%Y%m%d')
    st.session_state.mostrar_cdi = mostrar_cdi # Salva o estado do checkbox

    st.session_state.all_funds_data = {}
    st.session_state.cdi_data = pd.DataFrame()

    with st.spinner('🔄 Carregando dados dos fundos...'):
        for cnpj in st.session_state.cnpjs_carregados:
            df_fundo_completo = carregar_dados_api(
                cnpj,
                st.session_state.data_ini_str,
                st.session_state.data_fim_str
            )
            if not df_fundo_completo.empty:
                df_fundo_completo = df_fundo_completo.sort_values('DT_COMPTC').reset_index(drop=True)
                # Preencher valores ausentes para colunas do fundo com o último valor válido (forward-fill)
                fund_cols_to_ffill = ['VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST', 'CAPTC_DIA', 'RESG_DIA']
                for col in fund_cols_to_ffill:
                    if col in df_fundo_completo.columns:
                        df_fundo_completo[col] = df_fundo_completo[col].ffill()
                # Remover linhas onde VL_QUOTA ainda é NaN (fundo não existia ou não tinha dados mesmo após ffill)
                df_fundo_completo.dropna(subset=['VL_QUOTA'], inplace=True)

                if not df_fundo_completo.empty:
                    st.session_state.all_funds_data[cnpj] = df_fundo_completo
                else:
                    st.warning(f"⚠️ Nenhum dado de cota disponível para o CNPJ {cnpj} no período solicitado.")
            else:
                st.warning(f"⚠️ Não foi possível carregar dados para o CNPJ {cnpj}.")

    if st.session_state.mostrar_cdi and BCB_DISPONIVEL:
        with st.spinner('🔄 Carregando dados do CDI...'):
            st.session_state.cdi_data = obter_dados_cdi_real(st.session_state.dt_ini_user, st.session_state.dt_fim_user)
            if st.session_state.cdi_data.empty:
                st.warning("⚠️ Não foi possível carregar dados do CDI para o período selecionado.")

if not st.session_state.dados_carregados or not st.session_state.all_funds_data:
    st.info("👈 Preencha os campos na barra lateral e clique em 'Carregar Dados' para começar a análise.")

    st.markdown("""
    ### 📋 Como usar:

    1.  **CNPJs dos Fundos**: Digite um ou mais CNPJs dos fundos que deseja analisar, separados por vírgula ou nova linha.
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

try:
    num_funds = len(st.session_state.cnpjs_carregados)
    dt_ini_user = st.session_state.dt_ini_user
    dt_fim_user = st.session_state.dt_fim_user
    mostrar_cdi = st.session_state.mostrar_cdi
    cdi_data = st.session_state.cdi_data
    tem_cdi = mostrar_cdi and not cdi_data.empty

    # Cores para os gráficos
    colors = px.colors.qualitative.Plotly
    fund_colors = {cnpj: colors[i % len(colors)] for i, cnpj in enumerate(st.session_state.cnpjs_carregados)}

    # Preparar dados para gráficos e métricas
    processed_funds_data = {}
    all_metrics_results = {}
    for i, cnpj in enumerate(st.session_state.cnpjs_carregados):
        df_fundo = st.session_state.all_funds_data.get(cnpj)
        if df_fundo is None or df_fundo.empty:
            continue

        # Filtrar o dataframe do fundo para o período exato do usuário
        df_fundo_filtered = df_fundo[(df_fundo['DT_COMPTC'] >= dt_ini_user) & (df_fundo['DT_COMPTC'] <= dt_fim_user)].copy()
        if df_fundo_filtered.empty:
            st.warning(f"⚠️ Nenhum dado disponível para o CNPJ {cnpj} no período selecionado após filtragem.")
            continue

        df_fundo_filtered = df_fundo_filtered.sort_values('DT_COMPTC').reset_index(drop=True)

        # Re-normalizar a cota do fundo para começar em 1.0 (0% de rentabilidade)
        primeira_cota_fundo = df_fundo_filtered['VL_QUOTA'].iloc[0]
        df_fundo_filtered['VL_QUOTA_NORM'] = ((df_fundo_filtered['VL_QUOTA'] / primeira_cota_fundo) - 1) * 100

        # Adicionar dados do CDI ao dataframe do fundo se aplicável
        if tem_cdi:
            df_fundo_filtered = pd.merge(df_fundo_filtered, cdi_data[['DT_COMPTC', 'cdi', 'VL_CDI_normalizado']], on='DT_COMPTC', how='left')
            # Preencher CDI para datas onde o fundo tem dados mas o CDI não (ex: feriados)
            df_fundo_filtered['cdi'] = df_fundo_filtered['cdi'].ffill()
            df_fundo_filtered['VL_CDI_normalizado'] = df_fundo_filtered['VL_CDI_normalizado'].ffill()

            # Re-normaliza o CDI para começar em 1.0 na primeira data do 'df_fundo_filtered'
            if not df_fundo_filtered['VL_CDI_normalizado'].dropna().empty:
                first_cdi_normalized_value_in_period = df_fundo_filtered['VL_CDI_normalizado'].iloc[0]
                df_fundo_filtered['CDI_COTA'] = df_fundo_filtered['VL_CDI_normalizado'] / first_cdi_normalized_value_in_period
                df_fundo_filtered['CDI_NORM'] = (df_fundo_filtered['CDI_COTA'] - 1) * 100
            else:
                df_fundo_filtered['CDI_COTA'] = np.nan
                df_fundo_filtered['CDI_NORM'] = np.nan
        else:
            df_fundo_filtered.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado', 'CDI_COTA', 'CDI_NORM'] if col in df_fundo_filtered.columns], errors='ignore', inplace=True)

        # Calcular métricas adicionais para o fundo
        trading_days_in_year = 252
        df_fundo_filtered['Max_VL_QUOTA'] = df_fundo_filtered['VL_QUOTA'].cummax()
        df_fundo_filtered['Drawdown'] = (df_fundo_filtered['VL_QUOTA'] / df_fundo_filtered['Max_VL_QUOTA'] - 1) * 100
        df_fundo_filtered['Captacao_Liquida'] = df_fundo_filtered['CAPTC_DIA'] - df_fundo_filtered['RESG_DIA']
        df_fundo_filtered['Soma_Acumulada'] = df_fundo_filtered['Captacao_Liquida'].cumsum()
        df_fundo_filtered['Patrimonio_Liq_Medio'] = df_fundo_filtered['VL_PATRIM_LIQ'] / df_fundo_filtered['NR_COTST']

        vol_window = 21
        df_fundo_filtered['Variacao_Perc'] = df_fundo_filtered['VL_QUOTA'].pct_change()
        df_fundo_filtered['Volatilidade'] = df_fundo_filtered['Variacao_Perc'].rolling(vol_window).std() * np.sqrt(trading_days_in_year) * 100

        # CAGR
        df_fundo_filtered['CAGR_Fundo'] = np.nan
        if len(df_fundo_filtered) > trading_days_in_year:
            end_value_fundo = df_fundo_filtered['VL_QUOTA'].iloc[-1]
            for idx in range(len(df_fundo_filtered) - trading_days_in_year):
                initial_value_fundo = df_fundo_filtered['VL_QUOTA'].iloc[idx]
                num_intervals = (len(df_fundo_filtered) - 1) - idx
                if initial_value_fundo > 0 and num_intervals > 0:
                    df_fundo_filtered.loc[idx, 'CAGR_Fundo'] = ((end_value_fundo / initial_value_fundo) ** (trading_days_in_year / num_intervals) - 1) * 100

        if tem_cdi and 'CDI_COTA' in df_fundo_filtered.columns:
            df_fundo_filtered['CAGR_CDI'] = np.nan
            if len(df_fundo_filtered) > trading_days_in_year:
                end_value_cdi = df_fundo_filtered['CDI_COTA'].iloc[-1]
                for idx in range(len(df_fundo_filtered) - trading_days_in_year):
                    initial_value_cdi = df_fundo_filtered['CDI_COTA'].iloc[idx]
                    num_intervals = (len(df_fundo_filtered) - 1) - idx
                    if initial_value_cdi > 0 and num_intervals > 0:
                        df_fundo_filtered.loc[idx, 'CAGR_CDI'] = ((end_value_cdi / initial_value_cdi) ** (trading_days_in_year / num_intervals) - 1) * 100

            # Excesso de Retorno Anualizado
            df_fundo_filtered['EXCESSO_RETORNO_ANUALIZADO'] = np.nan
            valid_excess_return_indices = df_fundo_filtered.dropna(subset=['CAGR_Fundo', 'CAGR_CDI']).index
            if not valid_excess_return_indices.empty:
                df_fundo_filtered.loc[valid_excess_return_indices, 'EXCESSO_RETORNO_ANUALIZADO'] = (
                    (1 + df_fundo_filtered.loc[valid_excess_return_indices, 'CAGR_Fundo'] / 100) /
                    (1 + df_fundo_filtered.loc[valid_excess_return_indices, 'CAGR_CDI'] / 100) - 1
                ) * 100

        # VaR
        df_fundo_filtered['Retorno_21d'] = df_fundo_filtered['VL_QUOTA'].pct_change(21)

        processed_funds_data[cnpj] = df_fundo_filtered
        all_metrics_results.update(calculate_single_fund_metrics(df_fundo, cdi_data, cnpj, dt_ini_user, dt_fim_user, tem_cdi))

    if not processed_funds_data:
        st.error("❌ Nenhum fundo com dados válidos para o período selecionado.")
        st.stop()

    # Cores
    color_primary = '#1a5f3f'  # Verde escuro para o fundo
    color_secondary = '#6b9b7f'
    color_danger = '#dc3545'
    color_cdi = '#f0b429'  # Amarelo para o CDI

    # Cards de métricas (apenas se for um único fundo)
    if num_funds == 1:
        cnpj_unico = list(processed_funds_data.keys())[0]
        fund_metrics = all_metrics_results[cnpj_unico]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Patrimônio Líquido", format_brl(fund_metrics["Patrimônio Líquido"]))
        with col2:
            st.metric("Rentabilidade Acumulada", fmt_pct_port(fund_metrics["Rentabilidade Acumulada"]))
        with col3:
            st.metric("CAGR Médio", fmt_pct_port(fund_metrics["CAGR Médio"]))
        with col4:
            st.metric("Max Drawdown", fmt_pct_port(fund_metrics["Max Drawdown"]))
        with col5:
            st.metric("Vol. Histórica", fmt_pct_port(fund_metrics["Vol. Histórica"]))

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Rentabilidade", "Risco", "Patrimônio e Captação",
        "Cotistas", "Janelas Móveis"
    ])

    with tab1:
        st.subheader("Rentabilidade Histórica")

        fig1 = go.Figure()
        for i, (cnpj, df_fund) in enumerate(processed_funds_data.items()):
            fig1.add_trace(go.Scatter(
                x=df_fund['DT_COMPTC'],
                y=df_fund['VL_QUOTA_NORM'],
                mode='lines',
                name=f'Fundo {cnpj}',
                line=dict(color=fund_colors[cnpj], width=2.5),
                hovertemplate=f'<b>Fundo {cnpj}</b><br>Data: %{{x|%d/%m/%Y}}<br>Rentabilidade: %{{y:.2f}}%<extra></extra>'
            ))

        if tem_cdi:
            # Pega o CDI de um dos fundos (já normalizado para o período)
            # Assumimos que o CDI é o mesmo para todos os fundos no mesmo período
            first_fund_df = list(processed_funds_data.values())[0]
            if 'CDI_NORM' in first_fund_df.columns:
                fig1.add_trace(go.Scatter(
                    x=first_fund_df['DT_COMPTC'],
                    y=first_fund_df['CDI_NORM'],
                    mode='lines',
                    name='CDI',
                    line=dict(color=color_cdi, width=2.5, dash='dash'),
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
        # Ajusta o range do eixo X para os dados do primeiro fundo (assumindo que todos cobrem o mesmo período)
        first_fund_df = list(processed_funds_data.values())[0]
        fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[first_fund_df['DT_COMPTC'].min(), first_fund_df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("CAGR Anual por Dia de Aplicação")

        fig2 = go.Figure()
        for i, (cnpj, df_fund) in enumerate(processed_funds_data.items()):
            df_plot_cagr = df_fund.dropna(subset=['CAGR_Fundo']).copy()
            if not df_plot_cagr.empty:
                fig2.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=df_plot_cagr['CAGR_Fundo'],
                    mode='lines',
                    name=f'CAGR Fundo {cnpj}',
                    line=dict(color=fund_colors[cnpj], width=2.5),
                    hovertemplate=f'<b>CAGR Fundo {cnpj}</b><br>Data: %{{x|%d/%m/%Y}}<br>CAGR: %{{y:.2f}}%<extra></extra>'
                ))

        if tem_cdi:
            first_fund_df = list(processed_funds_data.values())[0]
            if 'CAGR_CDI' in first_fund_df.columns:
                df_plot_cagr_cdi = first_fund_df.dropna(subset=['CAGR_CDI']).copy()
                if not df_plot_cagr_cdi.empty:
                    fig2.add_trace(go.Scatter(
                        x=df_plot_cagr_cdi['DT_COMPTC'],
                        y=df_plot_cagr_cdi['CAGR_CDI'],
                        mode='lines',
                        name='CAGR do CDI',
                        line=dict(color=color_cdi, width=2.5, dash='dash'),
                        hovertemplate='<b>CAGR do CDI</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
                    ))
        if fig2.data: # Only show if there's data to plot
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
            first_fund_df = list(processed_funds_data.values())[0]
            fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[first_fund_df['DT_COMPTC'].min(), first_fund_df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("⚠️ Não há dados suficientes para calcular o CAGR (mínimo de 1 ano de dados) para os fundos selecionados.")

        st.subheader("Excesso de Retorno Anualizado")

        if tem_cdi:
            fig_excesso_retorno = go.Figure()
            has_excess_return_data = False
            for i, (cnpj, df_fund) in enumerate(processed_funds_data.items()):
                df_plot_excess = df_fund.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO']).copy()
                if not df_plot_excess.empty:
                    fig_excesso_retorno.add_trace(go.Scatter(
                        x=df_plot_excess['DT_COMPTC'],
                        y=df_plot_excess['EXCESSO_RETORNO_ANUALIZADO'],
                        mode='lines',
                        name=f'Excesso de Retorno Fundo {cnpj}',
                        line=dict(color=fund_colors[cnpj], width=2.5),
                        hovertemplate=f'<b>Excesso de Retorno Fundo {cnpj}</b><br>Data: %{{x|%d/%m/%Y}}<br>Excesso: %{{y:.2f}}%<extra></extra>'
                    ))
                    has_excess_return_data = True

            if has_excess_return_data:
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
                first_fund_df = list(processed_funds_data.values())[0]
                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64, x_range=[first_fund_df['DT_COMPTC'].min(), first_fund_df['DT_COMPTC'].max()], x_autorange=False)
                st.plotly_chart(fig_excesso_retorno, use_container_width=True)
            else:
                st.warning("⚠️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado (verifique se há dados de CDI e CAGR para o período) para os fundos selecionados.")
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar o Excesso de Retorno Anualizado.")

    with tab2:
        st.subheader("Drawdown Histórico")

        fig3 = go.Figure()
        has_drawdown_data = False
        for i, (cnpj, df_fund) in enumerate(processed_funds_data.items()):
            if not df_fund['Drawdown'].dropna().empty:
                fig3.add_trace(go.Scatter(
                    x=df_fund['DT_COMPTC'],
                    y=df_fund['Drawdown'],
                    mode='lines',
                    name=f'Drawdown Fundo {cnpj}',
                    line=dict(color=fund_colors[cnpj], width=2.5), # Usar cores dos fundos
                    hovertemplate=f'<b>Drawdown Fundo {cnpj}</b><br>Data: %{{x|%d/%m/%Y}}<br>Drawdown: %{{y:.2f}}%<extra></extra>'
                ))
                has_drawdown_data = True

        if has_drawdown_data:
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
            first_fund_df = list(processed_funds_data.values())[0]
            fig3 = add_watermark_and_style(fig3, logo_base64, x_range=[first_fund_df['DT_COMPTC'].min(), first_fund_df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("⚠️ Não há dados suficientes para calcular o Drawdown para os fundos selecionados.")

        st.subheader(f"Volatilidade Móvel ({vol_window} dias úteis)")

        fig4 = go.Figure()
        has_volatility_data = False
        for i, (cnpj, df_fund) in enumerate(processed_funds_data.items()):
            if not df_fund['Volatilidade'].dropna().empty:
                fig4.add_trace(go.Scatter(
                    x=df_fund['DT_COMPTC'],
                    y=df_fund['Volatilidade'],
                    mode='lines',
                    name=f'Volatilidade Fundo {cnpj}',
                    line=dict(color=fund_colors[cnpj], width=2.5),
                    hovertemplate=f'<b>Volatilidade Fundo {cnpj}</b><br>Data: %{{x|%d/%m/%Y}}<br>Volatilidade: %{{y:.2f}}%<extra></extra>'
                ))
                has_volatility_data = True

        if has_volatility_data:
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
            first_fund_df = list(processed_funds_data.values())[0]
            fig4 = add_watermark_and_style(fig4, logo_base64, x_range=[first_fund_df['DT_COMPTC'].min(), first_fund_df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("⚠️ Não há dados suficientes para calcular a Volatilidade para os fundos selecionados.")

        st.subheader("Value at Risk (VaR) e Expected Shortfall (ES)")

        # VaR/ES é mais complexo para múltiplos fundos no mesmo gráfico.
        # Para manter a clareza, vamos permitir selecionar um fundo para esta análise.
        if num_funds > 1:
            selected_cnpj_for_var = st.selectbox("Selecione um fundo para VaR e ES:", list(processed_funds_data.keys()), key="var_fund_select")
            df_plot_var = processed_funds_data[selected_cnpj_for_var].dropna(subset=['Retorno_21d']).copy()
            fund_name_for_var = f"Fundo {selected_cnpj_for_var}"
            fund_color_for_var = fund_colors[selected_cnpj_for_var]
        else:
            selected_cnpj_for_var = list(processed_funds_data.keys())[0]
            df_plot_var = processed_funds_data[selected_cnpj_for_var].dropna(subset=['Retorno_21d']).copy()
            fund_name_for_var = f"Fundo {selected_cnpj_for_var}"
            fund_color_for_var = fund_colors[selected_cnpj_for_var]

        VaR_95, VaR_99, ES_95, ES_99 = np.nan, np.nan, np.nan, np.nan
        if not df_plot_var.empty:
            VaR_95 = np.percentile(df_plot_var['Retorno_21d'], 5)
            VaR_99 = np.percentile(df_plot_var['Retorno_21d'], 1)
            ES_95 = df_plot_var.loc[df_plot_var['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
            ES_99 = df_plot_var.loc[df_plot_var['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()

            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=df_plot_var['DT_COMPTC'],
                y=df_plot_var['Retorno_21d'] * 100,
                mode='lines',
                name=f'Rentabilidade móvel (1m) {fund_name_for_var}',
                line=dict(color=fund_color_for_var, width=2),
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
            fig5 = add_watermark_and_style(fig5, logo_base64, x_range=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig5, use_container_width=True)

            st.info(f"""
            **Este gráfico mostra que, em um período de 1 mês, para o {fund_name_for_var}:**

            • Há **99%** de confiança de que o fundo não cairá mais do que **{fmt_pct_port(VaR_99)} (VaR)**,
            e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_99)} (ES)**.

            • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(VaR_95)} (VaR)**,
            e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_95)} (ES)**.
            """)
        else:
            st.warning(f"⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias de retorno) para o {fund_name_for_var}.")

        st.subheader("Métricas de Risco-Retorno")

        if not tem_cdi:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar as Métricas de Risco-Retorno.")
        elif not all_metrics_results:
            st.warning("⚠️ Não há dados suficientes para calcular as Métricas de Risco-Retorno (mínimo de 1 ano de dados).")
        else:
            metrics_df = pd.DataFrame(all_metrics_results).T # Transpõe para ter métricas como linhas e CNPJs como colunas

            # Formatação da tabela
            metrics_df_formatted = metrics_df.copy()
            for col in metrics_df_formatted.columns:
                if col in ["Patrimônio Líquido"]:
                    metrics_df_formatted[col] = metrics_df_formatted[col].apply(lambda x: format_brl(x) if not pd.isna(x) else "N/A")
                elif col in ["Ulcer Index"]:
                    metrics_df_formatted[col] = metrics_df_formatted[col].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "N/A")
                else: # Ratios e porcentagens
                    metrics_df_formatted[col] = metrics_df_formatted[col].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "N/A")

            st.dataframe(metrics_df_formatted.style.set_properties(**{'text-align': 'center'}), use_container_width=True)

            if num_funds == 1:
                # Exibir as explicações detalhadas apenas para um único fundo
                st.markdown("#### RISCO MEDIDO PELA VOLATILIDADE:")
                col_vol_1, col_vol_2 = st.columns(2)

                with col_vol_1:
                    st.metric("Sharpe Ratio", metrics_df_formatted.loc["Sharpe Ratio", cnpj_unico])
                    st.info("""
                    **Sharpe Ratio:** Mede o excesso de retorno do fundo (acima do CDI) por unidade de **volatilidade total** (risco). Quanto maior o Sharpe, melhor o retorno para o nível de risco assumido.
                    *   **Interpretação Geral:**
                        *   **< 1.0:** Subótimo, o retorno não compensa adequadamente o risco.
                        *   **1.0 - 1.99:** Bom, o fundo gera um bom retorno para o risco.
                        *   **2.0 - 2.99:** Muito Bom, excelente retorno ajustado ao risco.
                        *   **≥ 3.0:** Excepcional, performance muito consistente.
                    """)
                with col_vol_2:
                    st.metric("Sortino Ratio", metrics_df_formatted.loc["Sortino Ratio", cnpj_unico])
                    st.info("""
                    **Sortino Ratio:** Similar ao Sharpe, mas foca apenas na **volatilidade de baixa** (downside volatility). Ele mede o excesso de retorno por unidade de risco de queda. É útil para investidores que se preocupam mais com perdas do que com a volatilidade geral.
                    *   **Interpretação Geral:**
                        *   **< 0.0:** Retorno não cobre o risco de queda.
                        *   **0.0 - 1.0:** Aceitável, o fundo gera retorno positivo para o risco de queda.
                        *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de perdas.
                    """)

                col_vol_3, col_vol_4 = st.columns(2)
                with col_vol_3:
                    st.metric("Information Ratio", metrics_df_formatted.loc["Information Ratio", cnpj_unico])
                    st.info("""
                    **Information Ratio:** Mede a capacidade do gestor de gerar retornos acima de um benchmark (aqui, o CDI), ajustado pelo **tracking error** (risco de desvio em relação ao benchmark). Um valor alto indica que o gestor consistentemente superou o benchmark com um risco de desvio razoável.
                    *   **Interpretação Geral:**
                        *   **< 0.0:** O fundo está consistentemente abaixo do benchmark.
                        *   **0.0 - 0.5:** Habilidade modesta em superar o benchmark.
                        *   **0.5 - 1.0:** Boa habilidade e consistência em superar o benchmark.
                        *   **> 1.0:** Excelente habilidade e forte superação consistente do benchmark.
                    """)
                with col_vol_4:
                    st.metric("Treynor Ratio", metrics_df_formatted.loc["Treynor Ratio", cnpj_unico])
                    st.info("""
                    **Treynor Ratio:** Mede o excesso de retorno por unidade de **risco sistemático (Beta)**. O Beta mede a sensibilidade do fundo aos movimentos do mercado.
                    *   **Interpretação:** Um valor mais alto é preferível. É mais útil para comparar fundos com Betas semelhantes.
                    *   **Observação:** *Não é possível calcular este índice sem dados de um índice de mercado (benchmark) para determinar o Beta do fundo.*
                    """)

                st.markdown("#### RISCO MEDIDO PELO DRAWDOWN:")
                col_dd_1, col_dd_2 = st.columns(2)

                with col_dd_1:
                    st.metric("Calmar Ratio", metrics_df_formatted.loc["Calmar Ratio", cnpj_unico])
                    st.info("""
                    **Calmar Ratio:** Mede o retorno ajustado ao risco, comparando o **CAGR** (retorno anualizado) do fundo com o seu **maior drawdown** (maior queda). Um valor mais alto indica que o fundo gerou bons retornos sem grandes perdas.
                    *   **Interpretação Geral:**
                        *   **< 0.0:** Retorno negativo ou drawdown muito grande.
                        *   **0.0 - 0.5:** Aceitável, mas com espaço para melhoria.
                        *   **0.5 - 1.0:** Bom, o fundo gerencia bem o risco de drawdown.
                        *   **> 1.0:** Muito Bom, excelente retorno em relação ao risco de grandes quedas.
                    """)
                with col_dd_2:
                    st.metric("Sterling Ratio", metrics_df_formatted.loc["Sterling Ratio", cnpj_unico])
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
                    st.metric("Ulcer Index", metrics_df_formatted.loc["Ulcer Index", cnpj_unico])
                    st.info("""
                    **Ulcer Index:** Mede a profundidade e a duração dos drawdowns (quedas). Quanto menor o índice, menos dolorosas e mais curtas foram as quedas do fundo. É uma medida de risco que foca na "dor" do investidor.
                    *   **Interpretação Geral:**
                        *   **< 1.0:** Baixo risco, fundo relativamente estável.
                        *   **1.0 - 2.0:** Risco moderado, com quedas mais frequentes ou profundas.
                        *   **> 2.0:** Alto risco, fundo com quedas significativas e/ou duradouras.
                    """)
                with col_dd_4:
                    st.metric("Martin Ratio", metrics_df_formatted.loc["Martin Ratio", cnpj_unico])
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

    with tab3:
        st.subheader("Patrimônio e Captação Líquida")
        selected_cnpj_patrimonio = st.selectbox("Selecione um fundo para Patrimônio e Captação:", list(processed_funds_data.keys()), key="patrimonio_fund_select")
        df_selected_patrimonio = processed_funds_data[selected_cnpj_patrimonio]

        fig6 = go.Figure([
            go.Scatter(
                x=df_selected_patrimonio['DT_COMPTC'],
                y=df_selected_patrimonio['Soma_Acumulada'],
                mode='lines',
                name='Captação Líquida',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Captação Líquida Acumulada: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df_selected_patrimonio['Soma_Acumulada']]
            ),
            go.Scatter(
                x=df_selected_patrimonio['DT_COMPTC'],
                y=df_selected_patrimonio['VL_PATRIM_LIQ'],
                mode='lines',
                name='Patrimônio Líquido',
                line=dict(color=color_secondary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Líquido: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df_selected_patrimonio['VL_PATRIM_LIQ']]
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
        fig6 = add_watermark_and_style(fig6, logo_base64, x_range=[df_selected_patrimonio['DT_COMPTC'].min(), df_selected_patrimonio['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("Captação Líquida Mensal")

        df_monthly = df_selected_patrimonio.groupby(pd.Grouper(key='DT_COMPTC', freq='M'))[['CAPTC_DIA', 'RESG_DIA']].sum()
        df_monthly['Captacao_Liquida'] = df_monthly['CAPTC_DIA'] - df_monthly['RESG_DIA']

        colors_bar = [color_primary if x >= 0 else color_danger for x in df_monthly['Captacao_Liquida']]

        fig7 = go.Figure([
            go.Bar(
                x=df_monthly.index,
                y=df_monthly['Captacao_Liquida'],
                name='Captação Líquida Mensal',
                marker_color=colors_bar,
                text=df_monthly['Captacao_Liquida'].apply(lambda x: format_brl(x).replace('R$', '')), # Texto nas barras
                textposition='outside',
                textfont=dict(color='black', size=12),
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
            yaxis=dict(range=[df_monthly['Captacao_Liquida'].min() * 1.2, df_monthly['Captacao_Liquida'].max() * 1.2]) # Ajusta range para texto
        )
        if not df_monthly.empty:
            fig7 = add_watermark_and_style(fig7, logo_base64, x_range=[df_monthly.index.min(), df_monthly.index.max()], x_autorange=False)
        else:
            fig7 = add_watermark_and_style(fig7, logo_base64)
        st.plotly_chart(fig7, use_container_width=True)

    with tab4:
        st.subheader("Patrimônio Médio e Nº de Cotistas")
        selected_cnpj_cotistas = st.selectbox("Selecione um fundo para Cotistas:", list(processed_funds_data.keys()), key="cotistas_fund_select")
        df_selected_cotistas = processed_funds_data[selected_cnpj_cotistas]

        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(
            x=df_selected_cotistas['DT_COMPTC'],
            y=df_selected_cotistas['Patrimonio_Liq_Medio'],
            mode='lines',
            name='Patrimônio Médio por Cotista',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Patrimônio Médio: %{customdata}<extra></extra>',
            customdata=[format_brl(v) for v in df_selected_cotistas['Patrimonio_Liq_Medio']]
        ))
        fig8.add_trace(go.Scatter(
            x=df_selected_cotistas['DT_COMPTC'],
            y=df_selected_cotistas['NR_COTST'],
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
        fig8 = add_watermark_and_style(fig8, logo_base64, x_range=[df_selected_cotistas['DT_COMPTC'].min(), df_selected_cotistas['DT_COMPTC'].max()], x_autorange=False)
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

        janela_selecionada = st.selectbox("Selecione o período:", list(janelas.keys()), key="janela_select")
        dias_janela = janelas[janela_selecionada]

        fig9 = go.Figure()
        has_window_returns_data = False
        for i, (cnpj, df_fund) in enumerate(processed_funds_data.items()):
            df_returns_fund = df_fund.copy()
            if len(df_returns_fund) > dias_janela:
                df_returns_fund[f'FUNDO_{janela_selecionada}'] = df_returns_fund['VL_QUOTA'] / df_returns_fund['VL_QUOTA'].shift(dias_janela) - 1
                if not df_returns_fund[f'FUNDO_{janela_selecionada}'].dropna().empty:
                    fig9.add_trace(go.Scatter(
                        x=df_returns_fund['DT_COMPTC'],
                        y=df_returns_fund[f'FUNDO_{janela_selecionada}'],
                        mode='lines',
                        name=f"Retorno Fundo {cnpj} — {janela_selecionada}",
                        line=dict(width=2.5, color=fund_colors[cnpj]),
                        hovertemplate=f"<b>Retorno Fundo {cnpj}</b><br>Data: %{{x|%d/%m/%Y}}<br>Retorno: %{{y:.2%}}<extra></extra>"
                    ))
                    has_window_returns_data = True

        if tem_cdi:
            first_fund_df = list(processed_funds_data.values())[0]
            df_returns_cdi = first_fund_df.copy()
            if len(df_returns_cdi) > dias_janela and 'CDI_COTA' in df_returns_cdi.columns:
                df_returns_cdi[f'CDI_{janela_selecionada}'] = df_returns_cdi['CDI_COTA'] / df_returns_cdi['CDI_COTA'].shift(dias_janela) - 1
                if not df_returns_cdi[f'CDI_{janela_selecionada}'].dropna().empty:
                    fig9.add_trace(go.Scatter(
                        x=df_returns_cdi['DT_COMPTC'],
                        y=df_returns_cdi[f'CDI_{janela_selecionada}'],
                        mode='lines',
                        name=f"Retorno do CDI — {janela_selecionada}",
                        line=dict(width=2.5, color=color_cdi, dash='dash'),
                        hovertemplate="<b>Retorno do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                    ))
                    has_window_returns_data = True

        if has_window_returns_data:
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
            first_fund_df = list(processed_funds_data.values())[0]
            fig9 = add_watermark_and_style(fig9, logo_base64, x_range=[first_fund_df['DT_COMPTC'].min(), first_fund_df['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada} para os fundos selecionados.")

        # GRÁFICO: Consistência em Janelas Móveis
        st.subheader("Consistência em Janelas Móveis")

        if tem_cdi:
            consistency_data_list = []
            for cnpj, df_fund in processed_funds_data.items():
                for nome_janela, dias in janelas.items():
                    df_returns_fund = df_fund.copy()
                    if len(df_returns_fund) > dias and 'CDI_COTA' in df_returns_fund.columns:
                        df_returns_fund[f'FUNDO_{nome_janela}'] = df_returns_fund['VL_QUOTA'] / df_returns_fund['VL_QUOTA'].shift(dias) - 1
                        df_returns_fund[f'CDI_{nome_janela}'] = df_returns_fund['CDI_COTA'] / df_returns_fund['CDI_COTA'].shift(dias) - 1

                        temp_df = df_returns_fund[[f'FUNDO_{nome_janela}', f'CDI_{nome_janela}']].dropna()

                        if not temp_df.empty:
                            outperformed_count = (temp_df[f'FUNDO_{nome_janela}'] > temp_df[f'CDI_{nome_janela}']).sum()
                            total_comparisons = len(temp_df)
                            consistency_percentage = (outperformed_count / total_comparisons) * 100 if total_comparisons > 0 else np.nan
                            consistency_data_list.append({'Fundo': cnpj, 'Janela': nome_janela.split(' ')[0], 'Consistencia': consistency_percentage})
                    else:
                        consistency_data_list.append({'Fundo': cnpj, 'Janela': nome_janela.split(' ')[0], 'Consistencia': np.nan})

            df_consistency = pd.DataFrame(consistency_data_list)
            df_consistency.dropna(subset=['Consistencia'], inplace=True)

            if not df_consistency.empty:
                fig_consistency = go.Figure()
                for i, cnpj in enumerate(df_consistency['Fundo'].unique()):
                    df_fund_consistency = df_consistency[df_consistency['Fundo'] == cnpj]
                    fig_consistency.add_trace(go.Bar(
                        x=df_fund_consistency['Janela'],
                        y=df_fund_consistency['Consistencia'],
                        name=f'Fundo {cnpj}',
                        marker_color=fund_colors[cnpj],
                        text=df_fund_consistency['Consistencia'].apply(lambda x: f'{x:.2f}%'),
                        textposition='outside',
                        textfont=dict(color='black', size=12),
                        hovertemplate='<b>Fundo:</b> %{name}<br><b>Janela:</b> %{x}<br><b>Consistência:</b> %{y:.2f}%<extra></extra>'
                    ))

                fig_consistency.update_layout(
                    xaxis_title="Janela (meses)",
                    yaxis_title="Percentual de Superação do CDI (%)",
                    template="plotly_white",
                    hovermode="x unified",
                    height=500,
                    font=dict(family="Inter, sans-serif"),
                    yaxis=dict(range=[0, 110], ticksuffix="%"),
                    barmode='group', # Barras agrupadas para cada janela
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
                st.warning("⚠️ Não há dados suficientes para calcular a Consistência em Janelas Móveis para os fundos selecionados.")
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar a Consistência em Janelas Móveis.")

except Exception as e:
    st.error(f"❌ Erro ao processar os dados ou gerar gráficos: {str(e)}")
    st.info("💡 Verifique se os CNPJs estão corretos e se há dados disponíveis para o período selecionado para todos os fundos.")

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
