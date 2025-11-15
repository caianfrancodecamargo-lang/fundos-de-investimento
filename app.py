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

# ===================== CSS =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary-color: #1a5f3f;
        --secondary-color: #2d8659;
        --accent-color: #f0b429;
        --sidebar-top: #4a7b5d;   /* topo um pouco mais escuro */
        --sidebar-bottom: #365c45;/* base um pouco mais escura */
        --text-dark: #1a1a1a;
        --text-light: #ffffff;
    }

    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar mais escura, mas não preta (bom contraste com logo) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar-top) 0%, var(--sidebar-bottom) 100%);
        padding: 1rem 0.8rem !important;
    }

    [data-testid="stSidebar"] * {
        font-family: 'Inter', sans-serif;
    }

    /* Logo na sidebar */
    [data-testid="stSidebar"] .sidebar-logo {
        text-align: center;
        padding: 0.6rem 0 0.9rem 0 !important;
        margin-bottom: 0.8rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.25);
    }

    [data-testid="stSidebar"] .sidebar-logo img {
        max-width: 240px !important;
        height: auto;
        display: block;
        margin: 0 auto;
    }

    /* Labels dos inputs */
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #f3f6f3 !important;
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
        color: #f3f6f3 !important;
    }

    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
        border-color: rgba(255, 255, 255, 0.4);
    }

    /* Inputs */
    [data-testid="stSidebar"] input {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.6) !important;
        color: #000000 !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
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

    /* Botão Carregar Dados */
    .stButton > button {
        background: linear-gradient(135deg, #6b9b7f 0%, #365c45 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.25) !important;
        width: 100% !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-top: 0.5rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 16px rgba(0, 0, 0, 0.35) !important;
        background: linear-gradient(135deg, #365c45 0%, #6b9b7f 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Mensagens de validação na sidebar */
    [data-testid="stSidebar"] .stAlert {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(245, 247, 245, 0.96) 100%) !important;
        border-radius: 10px !important;
        padding: 0.5rem 0.7rem !important;
        margin: 0.3rem 0 !important;
        border-left: 3px solid #28a745 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;
        font-size: 0.8rem !important;
    }

    /* Texto dos alerts em preto para máxima legibilidade */
    [data-testid="stSidebar"] .stAlert [data-testid="stMarkdownContainer"] {
        color: #000000 !important;  /* <<< texto dos valores agora em preto */
        font-weight: 600 !important;
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

# ===================== MARCA D'ÁGUA =====================
def add_watermark_and_style(fig, logo_base64=None):
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
                opacity=0.08,
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

# ===================== FUNÇÕES AUXILIARES =====================
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

def buscar_data_anterior(df, data_alvo):
    datas_disponiveis = df['DT_COMPTC']
    datas_anteriores = datas_disponiveis[datas_disponiveis <= data_alvo]
    if len(datas_anteriores) > 0:
        return datas_anteriores.idxmax()
    return None

def ajustar_periodo_analise(df, data_inicial_str, data_final_str):
    data_inicial = datetime.strptime(data_inicial_str, '%Y%m%d')
    data_final = datetime.strptime(data_final_str, '%Y%m%d')
    idx_inicial = buscar_data_anterior(df, data_inicial)
    idx_final = buscar_data_anterior(df, data_final)

    ajustes = {
        'data_inicial_original': data_inicial,
        'data_final_original': data_final,
        'data_inicial_usada': None,
        'data_final_usada': None,
        'houve_ajuste_inicial': False,
        'houve_ajuste_final': False
    }

    if idx_inicial is not None:
        ajustes['data_inicial_usada'] = df.loc[idx_inicial, 'DT_COMPTC']
        ajustes['houve_ajuste_inicial'] = ajustes['data_inicial_usada'].date() != data_inicial.date()

    if idx_final is not None:
        ajustes['data_final_usada'] = df.loc[idx_final, 'DT_COMPTC']
        ajustes['houve_ajuste_final'] = ajustes['data_final_usada'].date() != data_final.date()

    if idx_inicial is not None and idx_final is not None:
        df_filtrado = df.loc[idx_inicial:idx_final].copy()
        return df_filtrado, ajustes

    return df, ajustes

# ===================== SIDEBAR =====================
# Logo
if logo_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" alt="Copaíba Invest"></div>',
        unsafe_allow_html=True
    )

# -------- Formatação automática de datas enquanto digita --------
def format_date_mask(raw: str) -> str:
    """
    Aplica máscara DD/MM/AAAA conforme o usuário digita.
    Ex.: 01011900 -> 01/01/1900
    """
    digits = re.sub(r'\D', '', raw)[:8]
    if len(digits) <= 2:
        return digits
    elif len(digits) <= 4:
        return digits[:2] + '/' + digits[2:]
    else:
        return digits[:2] + '/' + digits[2:4] + '/' + digits[4:]

if 'data_inicial_text' not in st.session_state:
    st.session_state['data_inicial_text'] = ""
if 'data_final_text' not in st.session_state:
    st.session_state['data_final_text'] = ""

def on_change_data_inicial():
    txt = st.session_state['data_inicial_text']
    st.session_state['data_inicial_text'] = format_date_mask(txt)

def on_change_data_final():
    txt = st.session_state['data_final_text']
    st.session_state['data_final_text'] = format_date_mask(txt)

# Input de CNPJ
cnpj_input = st.sidebar.text_input(
    "CNPJ do Fundo",
    value="",
    placeholder="00.000.000/0000-00",
    help="Digite o CNPJ com ou sem formatação"
)

# Inputs de data com formatação automática
st.sidebar.markdown("#### 📅 Período de Análise")
col1_sidebar, col2_sidebar = st.sidebar.columns(2)

with col1_sidebar:
    data_inicial_input = st.text_input(
        "Data Inicial",
        key="data_inicial_text",
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        on_change=on_change_data_inicial
    )

with col2_sidebar:
    data_final_input = st.text_input(
        "Data Final",
        key="data_final_text",
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        on_change=on_change_data_final
    )

st.sidebar.markdown("---")

# Processar inputs
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

carregar_button = st.sidebar.button("🔄 Carregar Dados", type="primary", disabled=not (cnpj_valido and datas_validas))

# ===================== MAIN =====================
st.markdown("<h1>📊 Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
st.markdown("---")

@st.cache_data
def carregar_dados_api(cnpj, data_ini, data_fim):
    dt_inicial = datetime.strptime(data_ini, '%Y%m%d')
    dt_ampliada = dt_inicial - timedelta(days=60)
    data_ini_ampliada = dt_ampliada.strftime('%Y%m%d    url = f"https://www.okanebox.com.br/api/fundoinvestimento/hist/{cnpj}/{data_ini_ampliada}/{data_fim}/"
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

if '_carregados' not in st.session_state:
    st.session_state.dados_carregados = False

if carregar_button and cnpj_valido and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpj = cnpj_limpo
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada

if not st.session_state.dados_carregados:
    st.info("👈 Preencha os campos na barra lateral e clique em 'Carregar Dados' para começar a análise.")
    st.markdown("""
    ### 📋 Como usar:

    1. **CNPJ do Fundo**: Digite o CNPJ do fundo que deseja analisar
    2. **Data Inicial**: Digite a data inicial no formato DD/MM/AAAA
    3. **Data Final**: Digite a data final no formato DD/MM/AAAA
    4. Clique em **Carregar Dados** para visualizar as análises

    ---
    """)
    st.stop()

try:
    with st.spinner('🔄 Carregando dados...'):
        df_completo = carregar_dados_api(st.session_state.cnpj, st.session_state.data_ini, st.session_state.data_fim)
        df, ajustes = ajustar_periodo_analise(df_completo, st.session_state.data_ini, st.session_state.data_fim)

    df = df.sort_values('DT_COMPTC').reset_index(drop=True)
    primeira_cota = df['VL_QUOTA'].iloc[0]
    df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota) - 1) * 100

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

    df_cagr = df.copy()
    end_value = df_cagr['VL_QUOTA'].iloc[-1]
    df_cagr['dias_uteis'] = df_cagr.index[-1] - df_cagr.index
    df_cagr = df_cagr[df_cagr['dias_uteis'] >= 252].copy()
    df_cagr['CAGR'] = ((end_value / df_cagr['VL_QUOTA']) ** (252 / df_cagr['dias_uteis'])) - 1
    df_cagr['CAGR'] = df_cagr['CAGR'] * 100
    mean_cagr = df_cagr['CAGR'].mean()

    df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
    df_plot = df.dropna(subset=['Retorno_21d']).copy()
    VaR_95 = np.percentile(df_plot['Retorno_21d'], 5)
    VaR_99 = np.percentile(df_plot['Retorno_21d'], 1)
    ES_95 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
    ES_99 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()

    color_primary = '#1a5f3f'
    color_secondary = '#6b9b7f'
    color_danger = '#dc3545'

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
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['VL_QUOTA_NORM'],
            mode='lines',
            line=dict(color=color_primary, width=2.5),
            fill='tozeroy',
            fillcolor='rgba(26, 95, 63, 0.10)',
            hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br><b>Rentabilidade:</b> %{y:.2f}%<extra></extra>'
        ))
        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade (%)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        fig1 = add_watermark_and_style(fig1, logo_base64)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 CAGR Anual por Dia de Aplicação")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_cagr['DT_COMPTC'],
            y=df_cagr['CAGR'],
            mode='lines',
            name='CAGR',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
        ))
        fig2.add_trace(go.Scatter(
            x=df_cagr['DT_COMPTC'],
            y=[mean_cagr] * len(df_cagr),
            mode='lines',
            line=dict(dash='dash', color=color_secondary, width=2),
            name=f'CAGR Médio ({mean_cagr:.2f}%)'
        ))
        fig2.update_layout(
            xaxis_title="Data",
            yaxis_title="CAGR (% a.a)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        fig2 = add_watermark_and_style(fig2, logo_base64)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("📉 Drawdown Histórico")
        fig3 = go.Figure(data=go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Drawdown'],
            mode='lines',
            name='Drawdown',
            line=dict(color=color_danger, width=2.5),
            fill='tozeroy',
            fillcolor='rgba(220, 53, 69, 0.10)',
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
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
        fig3 = add_watermark_and_style(fig3, logo_base64)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"📊 Volatilidade Móvel ({vol_window} dias úteis)")
        fig4 = go.Figure([
            go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Volatilidade'],
                mode='lines',
                name=f'Volatilidade {vol_window} dias',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
            ),
            go.Scatter(
                x=df['DT_COMPTC'],
                y=[vol_hist] * len(df),
                mode='lines',
                line=dict(dash='dash', color=color_secondary, width=2),
                name=f'Vol. Histórica ({vol_hist:.2f}%)'
            )
        ])
        fig4.update_layout(
            xaxis_title="Data",
            yaxis_title="Volatilidade (% a.a.)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        fig4 = add_watermark_and_style(fig4, logo_base64)
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("⚠️ Value at Risk (VaR) e Expected Shortfall (ES)")
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
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPC
