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
                opacity=0.15,  # <<< OPACIDADE DA MARCA D'ÁGUA AJUSTADA PARA 0.15
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
    st.session_state.data_inicial = data_inicial_formatada
    st.session_state.data_final = data_final_formatada
    st.session_state.mostrar_cdi = mostrar_cdi

if st.session_state.dados_carregados:
    try:
        df_raw = carregar_dados_api(st.session_state.cnpj, st.session_state.data_inicial, st.session_state.data_final)

        if df_raw.empty:
            st.warning("⚠️ Não foram encontrados dados para o CNPJ e período selecionados.")
            st.session_state.dados_carregados = False
        else:
            # Filtrar dados para o período selecionado pelo usuário
            dt_inicial_user = datetime.strptime(st.session_state.data_inicial, '%Y%m%d')
            dt_final_user = datetime.strptime(st.session_state.data_final, '%Y%m%d')
            df = df_raw[(df_raw['DT_COMPTC'] >= dt_inicial_user) & (df_raw['DT_COMPTC'] <= dt_final_user)].copy()

            if df.empty:
                st.warning("⚠️ Não foram encontrados dados para o período selecionado após o filtro. Tente um período diferente.")
                st.session_state.dados_carregados = False
            else:
                df = df.sort_values('DT_COMPTC').reset_index(drop=True)
                df['VL_QUOTA'] = pd.to_numeric(df['VL_QUOTA'], errors='coerce')
                df['VL_PATRIM_LIQ'] = pd.to_numeric(df['VL_PATRIM_LIQ'], errors='coerce')
                df['NR_COTST'] = pd.to_numeric(df['NR_COTST'], errors='coerce')
                df['CAPTC_DIA'] = pd.to_numeric(df['CAPTC_DIA'], errors='coerce')
                df['RESG_DIA'] = pd.to_numeric(df['RESG_DIA'], errors='coerce')

                # Preencher valores ausentes para VL_QUOTA e VL_PATRIM_LIQ com o método ffill
                # Isso é importante para o cálculo de retornos e drawdowns
                df['VL_QUOTA'] = df['VL_QUOTA'].ffill()
                df['VL_PATRIM_LIQ'] = df['VL_PATRIM_LIQ'].ffill()

                # Remover linhas com NaN na quota após ffill (se houver no início da série)
                df.dropna(subset=['VL_QUOTA'], inplace=True)

                if df.empty:
                    st.warning("⚠️ Dados insuficientes após tratamento de valores ausentes.")
                    st.session_state.dados_carregados = False
                else:
                    # Calcular Retorno Diário
                    df['Retorno_Diario'] = df['VL_QUOTA'].pct_change()

                    # Calcular Drawdown
                    df['Pico'] = df['VL_QUOTA'].cummax()
                    df['Drawdown'] = ((df['VL_QUOTA'] / df['Pico']) - 1) * 100

                    # Calcular Volatilidade Móvel (21 dias úteis)
                    vol_window = 21
                    trading_days_in_year = 252
                    df['Volatilidade'] = df['Retorno_Diario'].rolling(window=vol_window).std() * np.sqrt(trading_days_in_year) * 100
                    vol_hist = df['Retorno_Diario'].std() * np.sqrt(trading_days_in_year) * 100

                    # Calcular Patrimônio Líquido Médio por Cotista
                    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

                    # Calcular Captação Líquida Acumulada
                    df['Cap_Liq_Dia'] = df['CAPTC_DIA'] - df['RESG_DIA']
                    df['Soma_Acumulada'] = df['Cap_Liq_Dia'].cumsum()

                    # Obter dados do CDI se a opção estiver marcada
                    tem_cdi = st.session_state.mostrar_cdi
                    if tem_cdi:
                        cdi_df = obter_dados_cdi_real(df['DT_COMPTC'].min(), df['DT_COMPTC'].max())
                        if not cdi_df.empty:
                            df = pd.merge(df, cdi_df[['DT_COMPTC', 'VL_CDI_normalizado']], on='DT_COMPTC', how='left')
                            df.rename(columns={'VL_CDI_normalizado': 'CDI_COTA'}, inplace=True)
                            df['CDI_COTA'] = df['CDI_COTA'].ffill() # Preenche CDI para dias sem cota do fundo
                            df.dropna(subset=['CDI_COTA'], inplace=True) # Remove se ainda houver NaN no CDI
                        else:
                            st.warning("⚠️ Não foi possível obter dados do CDI para o período. As comparações com CDI não serão exibidas.")
                            tem_cdi = False

                    # --- Cálculos para o Excesso de Retorno Anualizado (SÉRIE TEMPORAL para plotagem) ---
                    df['DAILY_RETURN_FUND'] = df['VL_QUOTA'].pct_change()

                    if tem_cdi:
                        df['DAILY_RETURN_CDI'] = df['CDI_COTA'].pct_change()
                    else:
                        df['DAILY_RETURN_CDI'] = np.nan # Garante que a coluna exista

                    rolling_window_days = trading_days_in_year # 252 dias para janela móvel de 1 ano

                    df['ROLLING_ANN_RETURN_FUND'] = np.nan
                    if len(df) >= rolling_window_days:
                        df['ROLLING_ANN_RETURN_FUND'] = (1 + df['DAILY_RETURN_FUND']).rolling(window=rolling_window_days).apply(lambda x: x.prod(), raw=True)**(trading_days_in_year / rolling_window_days) - 1

                    df['ROLLING_ANN_RETURN_CDI'] = np.nan
                    if tem_cdi and len(df) >= rolling_window_days:
                        df['ROLLING_ANN_RETURN_CDI'] = (1 + df['DAILY_RETURN_CDI']).rolling(window=rolling_window_days).apply(lambda x: x.prod(), raw=True)**(trading_days_in_year / rolling_window_days) - 1

                    # Calcular Rolling Excesso de Retorno Anualizado
                    # Esta coluna será usada para o plot
                    if tem_cdi:
                        df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'] = (df['ROLLING_ANN_RETURN_FUND'] - df['ROLLING_ANN_RETURN_CDI']) * 100 # Converte para porcentagem para plotagem
                    else:
                        df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'] = np.nan # Inicializa se CDI não selecionado
                    # --- Fim dos cálculos de Rolling Excesso de Retorno Anualizado ---


                    # --- Cálculos para as Métricas de Risco-Retorno (VALORES ESCALARES para os cards) ---
                    # Retorno total do período
                    total_return_fund = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1
                    num_days_period = (df['DT_COMPTC'].iloc[-1] - df['DT_COMPTC'].iloc[0]).days

                    cagr_fund = np.nan
                    if num_days_period > 0:
                        cagr_fund = (1 + total_return_fund)**(trading_days_in_year / num_days_period) - 1

                    cagr_cdi = np.nan
                    if tem_cdi:
                        total_return_cdi = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0]) - 1
                        if num_days_period > 0:
                            cagr_cdi = (1 + total_return_cdi)**(trading_days_in_year / num_days_period) - 1
                    # --- Fim dos cálculos para as Métricas de Risco-Retorno ---


                    # Cálculos para VaR e ES
                    df_plot_var = df.copy()
                    df_plot_var['Retorno_21d'] = df_plot_var['VL_QUOTA'].pct_change(periods=21)
                    df_plot_var.dropna(subset=['Retorno_21d'], inplace=True)

                    VaR_95 = np.nan
                    VaR_99 = np.nan
                    ES_95 = np.nan
                    ES_99 = np.nan

                    if not df_plot_var.empty:
                        VaR_95 = df_plot_var['Retorno_21d'].quantile(0.05)
                        VaR_99 = df_plot_var['Retorno_21d'].quantile(0.01)
                        ES_95 = df_plot_var['Retorno_21d'][df_plot_var['Retorno_21d'] <= VaR_95].mean()
                        ES_99 = df_plot_var['Retorno_21d'][df_plot_var['Retorno_21d'] <= VaR_99].mean()

                    # Definir cores
                    color_primary = "#1a5f3f"
                    color_secondary = "#2d8659"
                    color_accent = "#f0b429"
                    color_danger = "#dc3545" # Para drawdown

                    # Criar abas
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📈 Retorno", "📉 Risco", "💰 Patrimônio", "👥 Cotistas", "🎯 Janelas Móveis"
                    ])

                    with tab1:
                        st.subheader("📈 Retorno Acumulado")

                        fig2 = go.Figure()
                        fig2.add_trace(go.Scatter(
                            x=df['DT_COMPTC'],
                            y=df['VL_QUOTA'],
                            mode='lines',
                            name='Fundo',
                            line=dict(color=color_primary, width=2.5),
                            hovertemplate='Data: %{x|%d/%m/%Y}<br>Cota: %{y:.4f}<extra></extra>'
                        ))
                        if tem_cdi:
                            fig2.add_trace(go.Scatter(
                                x=df['DT_COMPTC'],
                                y=df['CDI_COTA'],
                                mode='lines',
                                name='CDI',
                                line=dict(color=color_secondary, width=2.5),
                                hovertemplate='Data: %{x|%d/%m/%Y}<br>CDI: %{y:.4f}<extra></extra>'
                            ))

                        fig2.update_layout(
                            xaxis_title="Data",
                            yaxis_title="Cota Normalizada",
                            template="plotly_white",
                            hovermode="x unified",
                            height=500,
                            font=dict(family="Inter, sans-serif")
                        )
                        # Ajusta o range do eixo X para os dados de df
                        fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
                        st.plotly_chart(fig2, use_container_width=True)

                        # NOVO GRÁFICO: Excesso de Retorno Anualizado
                        st.subheader("📈 Excesso de Retorno Anualizado")

                        # Usa a nova coluna ROLLING para o gráfico
                        if tem_cdi and not df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO_ROLLING']).empty:
                            fig_excesso_retorno = go.Figure()

                            # Linha do Excesso de Retorno
                            fig_excesso_retorno.add_trace(go.Scatter(
                                x=df['DT_COMPTC'],
                                y=df['EXCESSO_RETORNO_ANUALIZADO_ROLLING'], # Usando a coluna rolling
                                mode='lines',
                                name='Excesso de Retorno Anualizado',
                                line=dict(color=color_primary, width=2.5),
                                hovertemplate='<b>Excesso de Retorno</b><br>Data: %{x|%d/%m/%Y}<br>Excesso: %{y:.2f}%<extra></extra>'
                            ))

                            # Adicionar linha de 0% para referência
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
                            # Ajusta o range do eixo X para os dados de df
                            df_plot_excess = df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO_ROLLING']).copy()
                            if not df_plot_excess.empty:
                                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64, x_range=[df_plot_excess['DT_COMPTC'].min(), df_plot_excess['DT_COMPTC'].max()], x_autorange=False)
                            else:
                                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64)
                            st.plotly_chart(fig_excesso_retorno, use_container_width=True)
                        elif st.session_state.mostrar_cdi:
                            st.warning(f"⚠️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado (mínimo de {rolling_window_days} dias de dados).")
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

                        # --- Métricas de Risco-Retorno (Cards) ---
                        st.markdown("---")
                        st.markdown("### 📊 Métricas de Risco-Retorno")

                        # Condição para exibir as métricas
                        if tem_cdi and not df.empty and len(df) > trading_days_in_year:
                            # Cálculos das métricas de risco-retorno (usando cagr_fund e cagr_cdi escalares)
                            # Volatilidade anualizada do fundo
                            annualized_fund_volatility = df['Retorno_Diario'].std() * np.sqrt(trading_days_in_year)

                            # Max Drawdown (em decimal)
                            max_drawdown_value = df['Drawdown'].min() / 100 if not df['Drawdown'].empty else np.nan

                            # Ulcer Index
                            if not df['Drawdown'].empty:
                                # Drawdowns negativos em decimal
                                drawdowns_decimal = df['Drawdown'][df['Drawdown'] < 0] / 100
                                if not drawdowns_decimal.empty:
                                    squared_drawdowns = drawdowns_decimal**2
                                    ulcer_index = np.sqrt(squared_drawdowns.mean())
                                else:
                                    ulcer_index = np.nan
                            else:
                                ulcer_index = np.nan

                            # Volatilidade de Baixa (Downside Volatility)
                            downside_returns = df['Retorno_Diario'][df['Retorno_Diario'] < 0]
                            annualized_downside_volatility = downside_returns.std() * np.sqrt(trading_days_in_year) if not downside_returns.empty else np.nan

                            # Tracking Error
                            if tem_cdi:
                                excess_daily_returns = df['DAILY_RETURN_FUND'] - df['DAILY_RETURN_CDI']
                                tracking_error = excess_daily_returns.std() * np.sqrt(trading_days_in_year) if not excess_daily_returns.empty else np.nan
                            else:
                                tracking_error = np.nan

                            # Calcular os 3 piores drawdowns para o Sterling Ratio
                            negative_drawdowns = df['Drawdown'][df['Drawdown'] < 0]
                            avg_worst_drawdowns = np.nan
                            if not negative_drawdowns.empty:
                                # Pega os 3 menores (mais negativos) valores de drawdown
                                worst_drawdowns_series = negative_drawdowns.nsmallest(3)
                                # Calcula a média e divide por 100 para converter de porcentagem para decimal
                                avg_worst_drawdowns = worst_drawdowns_series.mean() / 100


                            # Calmar Ratio
                            calmar_ratio = np.nan
                            if not pd.isna(cagr_fund) and not pd.isna(cagr_cdi) and not pd.isna(max_drawdown_value) and max_drawdown_value != 0:
                                calmar_ratio = (cagr_fund - cagr_cdi) / abs(max_drawdown_value)

                            # Sterling Ratio (agora usando a média dos piores drawdowns)
                            sterling_ratio = np.nan
                            if not pd.isna(cagr_fund) and not pd.isna(cagr_cdi) and not pd.isna(avg_worst_drawdowns) and avg_worst_drawdowns != 0:
                                sterling_ratio = (cagr_fund - cagr_cdi) / abs(avg_worst_drawdowns)

                            # Ulcer Index (já calculado acima)

                            # Martin Ratio
                            martin_ratio = np.nan
                            if not pd.isna(cagr_fund) and not pd.isna(cagr_cdi) and not pd.isna(ulcer_index) and ulcer_index != 0:
                                martin_ratio = (cagr_fund - cagr_cdi) / ulcer_index

                            # Sharpe Ratio
                            sharpe_ratio = np.nan
                            if not pd.isna(cagr_fund) and not pd.isna(cagr_cdi) and not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0:
                                sharpe_ratio = (cagr_fund - cagr_cdi) / annualized_fund_volatility

                            # Sortino Ratio
                            sortino_ratio = np.nan
                            if not pd.isna(cagr_fund) and not pd.isna(cagr_cdi) and not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0:
                                sortino_ratio = (cagr_fund - cagr_cdi) / annualized_downside_volatility

                            # Information Ratio
                            information_ratio = np.nan
                            if not pd.isna(cagr_fund) and not pd.isna(cagr_cdi) and not pd.isna(tracking_error) and tracking_error != 0:
                                information_ratio = (cagr_fund - cagr_cdi) / tracking_error

                            st.markdown("#### RISCO MEDIDO PELA VOLATILIDADE:")
                            col_vol_1, col_vol_2 = st.columns(2)

                            with col_vol_1:
                                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if not pd.isna(sharpe_ratio) else "N/A")
                                st.info("""
                                **Sharpe Ratio:** Mede o excesso de retorno (acima do CDI) por unidade de **risco total (volatilidade)**. Quanto maior, melhor o retorno ajustado ao risco.
                                *   **Interpretação Geral:**
                                    *   **< 0.0:** Retorno inferior ao CDI ou risco excessivo.
                                    *   **0.0 - 0.5:** Aceitável, mas com espaço para melhoria.
                                    *   **0.5 - 1.0:** Bom, o fundo compensa bem o risco assumido.
                                    *   **> 1.0:** Muito Bom, excelente retorno ajustado ao risco.
                                """)
                            with col_vol_2:
                                st.metric("Sortino Ratio", f"{sortino_ratio:.2f}" if not pd.isna(sortino_ratio) else "N/A")
                                st.info("""
                                **Sortino Ratio:** Similar ao Sharpe, mas foca apenas no **risco de queda (volatilidade de baixa)**. Mede o excesso de retorno por unidade de risco de queda. É útil para investidores que se preocupam mais com perdas do que com a volatilidade geral.
                                *   **Interpretação Geral:**
                                    *   **< 0.0:** Retorno inferior ao CDI ou perdas excessivas.
                                    *   **0.0 - 1.0:** Aceitável, o fundo compensa o risco de queda.
                                    *   **> 1.0:** Bom, o fundo entrega um bom retorno em relação ao risco de perdas.
                                    *   **> 2.0:** Muito Bom, excelente retorno ajustado ao risco de queda.
                                """)

                            col_vol_3, col_vol_4 = st.columns(2)
                            with col_vol_3:
                                st.metric("Information Ratio", f"{information_ratio:.2f}" if not pd.isna(information_ratio) else "N/A")
                                st.info("""
                                **Information Ratio:** Mede a capacidade do gestor de gerar retornos acima de um benchmark (aqui, o CDI), ajustado pelo **tracking error** (risco de desvio em relação ao benchmark). Um valor alto indica que o gestor consistentemente superou o benchmark com um risco de desvio razoável.
                                *   **Interpretação Geral:**
                                    *   **< 0.0:** O fundo consistentemente performa abaixo do benchmark.
                                    *   **0.0 - 0.5:** O fundo tem alguma capacidade de superar o benchmark, mas com inconsistência.
                                    *   **0.5 - 1.0:** Boa capacidade de superar o benchmark.
                                    *   **> 1.0:** Excelente capacidade de superar o benchmark de forma consistente.
                                """)
                            with col_vol_4:
                                st.metric("Treynor Ratio", "Não Calculável" if not tem_cdi else "N/A")
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
                                **Sterling Ratio:** Similar ao Calmar, avalia o retorno ajustado ao risco em relação ao drawdown. Geralmente, compara o retorno anualizado com a **média dos piores drawdowns (nesta análise, os 3 piores)**. Um valor mais alto é preferível.
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

                        elif not tem_cdi:
                            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar as Métricas de Risco-Retorno.")
                        else:
                            st.warning("⚠️ Não há dados suficientes para calcular as Métricas de Risco-Retorno (mínimo de 1 ano de dados).")


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
                                    line=dict(width=2.5, color=color_cdi),
                                    hovertemplate="<b>Retorno do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                                ))

                            fig9.update_layout(
                                xaxis_title="Data",
                                yaxis_title=f"Retorno {janela_selecionada}",
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
                            # Ajusta o range do eixo X para os dados de df_returns
                            df_plot_returns = df_returns.dropna(subset=[f'FUNDO_{janela_selecionada}']).copy()
                            if not df_plot_returns.empty:
                                fig9 = add_watermark_and_style(fig9, logo_base64, x_range=[df_plot_returns['DT_COMPTC'].min(), df_plot_returns['DT_COMPTC'].max()], x_autorange=False)
                            else:
                                fig9 = add_watermark_and_style(fig9, logo_base64)
                            st.plotly_chart(fig9, use_container_width=True)
                        else:
                            st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada}.")

                        # GRÁFICO: Consistência em Janelas Móveis
                        st.subheader("📈 Consistência em Janelas Móveis")

                        if tem_cdi:
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
                                    # Adiciona o texto nas barras
                                    text=df_consistency['Consistencia'].apply(lambda x: f'{x:.2f}%'),
                                    textposition='outside', # Posição do texto fora da barra
                                    textfont=dict(color='black', size=12), # Cor e tamanho da fonte do texto
                                    hovertemplate='<b>Janela:</b> %{x}<br><b>Consistência:</b> %{y:.2f}%<extra></extra>'
                                ))

                                fig_consistency.update_layout(
                                    xaxis_title="Janela (meses)",
                                    yaxis_title="Percentual de Superação do CDI (%)",
                                    template="plotly_white",
                                    hovermode="x unified",
                                    height=500,
                                    font=dict(family="Inter, sans-serif"),
                                    yaxis=dict(range=[0, 110], ticksuffix="%") # Aumenta o range superior para dar mais espaço ao texto
                                )
                                fig_consistency = add_watermark_and_style(fig_consistency, logo_base64, x_autorange=True)
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
