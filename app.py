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
    dt_ampliada = dt_inicial - timedelta(days=60) # Busca 60 dias antes para ter histórico para ffill
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
def calculate_single_fund_metrics(df_fund_processed, fund_name, tem_cdi):
    metrics = {}
    trading_days_in_year = 252

    if df_fund_processed.empty:
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

    # Métricas básicas
    metrics["Patrimônio Líquido"] = df_fund_processed['VL_PATRIM_LIQ'].iloc[-1]
    metrics["Rentabilidade Acumulada"] = df_fund_processed['VL_QUOTA_NORM'].iloc[-1] / 100

    metrics["Max Drawdown"] = df_fund_processed['Drawdown'].min() / 100

    vol_hist = df_fund_processed['Variacao_Perc'].std() * np.sqrt(trading_days_in_year) * 100
    metrics["Vol. Histórica"] = vol_hist / 100

    mean_cagr = df_fund_processed['CAGR_Fundo'].mean() if 'CAGR_Fundo' in df_fund_processed.columns else 0
    if pd.isna(mean_cagr):
        mean_cagr = 0
    metrics["CAGR Médio"] = mean_cagr / 100

    # Métricas de Risco-Retorno (se CDI disponível)
    if tem_cdi and 'CDI_COTA' in df_fund_processed.columns and not df_fund_processed['CDI_COTA'].dropna().empty:
        # Retorno total do fundo e CDI no período
        total_fund_return = (df_fund_processed['VL_QUOTA'].iloc[-1] / df_fund_processed['VL_QUOTA'].iloc[0]) - 1
        total_cdi_return = (df_fund_processed['CDI_COTA'].iloc[-1] / df_fund_processed['CDI_COTA'].iloc[0]) - 1

        # Anualização dos retornos totais para consistência
        num_days_in_period = len(df_fund_processed)
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
        drawdown_series = (df_fund_processed['VL_QUOTA'] / df_fund_processed['Max_VL_QUOTA'] - 1)
        squared_drawdowns = drawdown_series**2
        ulcer_index = np.sqrt(squared_drawdowns.mean()) if not squared_drawdowns.empty and squared_drawdowns.mean() > 0 else np.nan

        # Downside Volatility
        downside_returns = df_fund_processed['Variacao_Perc'][df_fund_processed['Variacao_Perc'] < 0]
        annualized_downside_volatility = downside_returns.std() * np.sqrt(trading_days_in_year) if not downside_returns.empty else np.nan

        # Tracking Error
        tracking_error = np.nan
        if 'cdi' in df_fund_processed.columns and not df_fund_processed['Variacao_Perc'].empty:
            excess_daily_returns = df_fund_processed['Variacao_Perc'] - (df_fund_processed['cdi'] / 100)
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
    st.session_state.all_funds_raw_data = {} # Armazena dados brutos (ampliados)
    st.session_state.cdi_raw_data = pd.DataFrame() # Armazena CDI bruto (período do usuário)
    st.session_state.dt_ini_user_original = None # Data inicial do usuário
    st.session_state.dt_fim_user_original = None # Data final do usuário
    st.session_state.mostrar_cdi = True
    st.session_state.cnpjs_carregados = []
    st.session_state.processed_funds_data = {} # Dados processados e normalizados
    st.session_state.all_metrics_results = {} # Métricas calculadas

if carregar_button and cnpjs_validos and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpjs_carregados = cnpjs_limpos
