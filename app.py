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

# Paleta de cores consistente
color_primary = "#1a5f3f"   # Fundo
color_secondary = "#2d8659" # Cotistas
color_cdi = "#000000"       # CDI
color_ibov = "#f0b429"      # Ibovespa

# CSS customizado com espaçamentos reduzidos na sidebar e fonte Inter
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

    /* Sidebar com padding reduzido (já mais clara/esverdeada) */
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
                sizex=1.75,
                sizey=1.75,
                xanchor="center",
                yanchor="middle",
                opacity=0.15,
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
        ],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

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
        x_axes_update_params['autorange'] = False
    else:
        x_axes_update_params['autorange'] = x_autorange

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

# FUNÇÃO PARA OBTER DADOS REAIS DO CDI
@st.cache_data
def obter_dados_cdi_real(data_inicio: datetime, data_fim: datetime):
    if not BCB_DISPONIVEL:
        return pd.DataFrame()

    try:
        # Série 12 = CDI Over
        dados_diarios = sgs.get(12, start=data_inicio, end=data_fim)
        dados_diarios = dados_diarios.rename(columns={'12': 'CDI_DIARIO'})
        dados_diarios['CDI_DIARIO_PERC'] = dados_diarios['CDI_DIARIO'] / 100.0
        dados_diarios['CDI_FACTOR'] = (1 + dados_diarios['CDI_DIARIO_PERC']).cumprod()
        dados_diarios['CD_ACUMULADO_NORMALIZADO'] = dados_diarios['CDI_FACTOR'] / dados_diarios['CDI_FACTOR'].iloc[0]
        dados_diarios.reset_index(inplace=True)
        dados_diarios.rename(columns={'index': 'DT_COMPTC'}, inplace=True)
        return dados_diarios[['DT_COMPTC', 'CDI_DIARIO', 'CDI_DIARIO_PERC', 'CDI_ACUMULADO_NORMALIZADO']]
    except Exception as e:
        st.warning(f"⚠️ Erro ao obter dados reais do CDI: {e}")
        return pd.DataFrame()

# FUNÇÃO PARA OBTER DADOS DO IBOVESPA
@st.cache_data
def obter_dados_ibov(data_inicio: datetime, data_fim: datetime):
    if not YF_DISPONIVEL:
        return pd.DataFrame()

    try:
        ticker = "^BVSP"
        dados_ibov = yf.download(ticker, start=data_inicio, end=data_fim)
        if dados_ibov.empty:
            return pd.DataFrame()
        dados_ibov.reset_index(inplace=True)
        dados_ibov.rename(columns={'Date': 'DT_COMPTC', 'Adj Close': 'IBOV_FECHAMENTO'}, inplace=True)
        dados_ibov['IBOV_RET_DIARIO'] = dados_ibov['IBOV_FECHAMENTO'].pct_change()
        dados_ibov['IBOV_COTA'] = (1 + dados_ibov['IBOV_RET_DIARIO']).cumprod()
        dados_ibov['IBOV_COTA'] = dados_ibov['IBOV_COTA'] / dados_ibov['IBOV_COTA'].iloc[0]
        return dados_ibov[['DT_COMPTC', 'IBOV_FECHAMENTO', 'IBOV_RET_DIARIO', 'IBOV_COTA']]
    except Exception as e:
        st.warning(f"⚠️ Erro ao obter dados do Ibovespa: {e}")
        return pd.DataFrame()

# Função para carregar dados do fundo da CVM
@st.cache_data
def carregar_dados_fundo(cnpj, data_inicio_api, data_fim_api):
    url = f"https://dados.cvm.gov.br/api/some_endpoint_ficticio?cnpj={cnpj}&data_ini={data_inicio_api}&data_fim={data_fim_api}"
    # AQUI: substitua pela URL correta da sua API CVM; mantive como placeholder.
    raise NotImplementedError("Substitua carregar_dados_fundo pela implementação real da API da CVM.")

# Formatador de moeda
def format_brl(valor):
    if pd.isna(valor):
        return "-"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# -----------------------------------------
# LAYOUT PRINCIPAL / SIDEBAR
# -----------------------------------------
st.markdown("<div class='sidebar-logo'><img src='data:image/png;base64,{}'></div>".format(logo_base64 if logo_base64 else ""), unsafe_allow_html=True)

st.title("Dashboard - Fundos de Investimentos")

with st.sidebar:
    cnpj_input = st.text_input("CNPJ do Fundo", help="Digite o CNPJ do fundo sem pontos ou traços.")
    data_inicio_str = st.text_input("Data de Início (dd/mm/aaaa)")
    data_fim_str = st.text_input("Data de Fim (dd/mm/aaaa)")
    usar_cdi = st.checkbox("Comparar com CDI", value=True)
    usar_ibov = st.checkbox("Comparar com Ibovespa", value=True)
    botao_carregar = st.button("Carregar Dados")

try:
    if botao_carregar:
        cnpj_limpo = limpar_cnpj(cnpj_input)
        data_inicio_api = formatar_data_api(data_inicio_str)
        data_fim_api = formatar_data_api(data_fim_str)

        if not cnpj_limpo:
            st.warning("⚠️ Informe um CNPJ válido.")
            st.stop()
        if not data_inicio_api or not data_fim_api:
            st.warning("⚠️ Informe datas válidas no formato dd/mm/aaaa.")
            st.stop()

        # Converter para datetime
        data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
        data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")

        # Carregar dados do fundo (substitua pela sua função real)
        st.info("Esta versão contém um placeholder para a API da CVM em carregar_dados_fundo().")

        # Exemplo de df fictício para não quebrar o app (substitua por dados reais)
        datas = pd.date_range(data_inicio, data_fim, freq="B")
        df = pd.DataFrame({
            "DT_COMPTC": datas,
            "VL_QUOTA": np.cumprod(1 + np.random.normal(0.0003, 0.01, len(datas))),
            "VL_PATRIM_LIQ": np.linspace(10_000_000, 15_000_000, len(datas)),
            "NR_COTST": np.linspace(1000, 1500, len(datas)).astype(int)
        })

        df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'])
        df = df.sort_values('DT_COMPTC')

        # CDI
        tem_cdi = usar_cdi
        df_cdi = pd.DataFrame()
        if tem_cdi:
            df_cdi = obter_dados_cdi_real(data_inicio, data_fim)
            if not df_cdi.empty:
                df = pd.merge(df, df_cdi[['DT_COMPTC', 'CDI_ACUMULADO_NORMALIZADO']], on='DT_COMPTC', how='left')
                df['CDI_COTA'] = df['CDI_ACUMULADO_NORMALIZADO']
            else:
                tem_cdi = False

        # Ibovespa
        tem_ibov = usar_ibov
        df_ibov = pd.DataFrame()
        if tem_ibov:
            df_ibov = obter_dados_ibov(data_inicio, data_fim)
            if not df_ibov.empty:
                df = pd.merge(df, df_ibov[['DT_COMPTC', 'IBOV_COTA']], on='DT_COMPTC', how='left')
            else:
                tem_ibov = False

        # Patrimônio médio por cotista
        df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

        # Métricas simples no topo
        pl_atual = df['VL_PATRIM_LIQ'].iloc[-1]
        retorno_total = df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0] - 1
        pl_medio_12m = df['VL_PATRIM_LIQ'].tail(252).mean()
        cotistas_atuais = df['NR_COTST'].iloc[-1]

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("PL Atual", format_brl(pl_atual))
        col_m2.metric("Retorno Total", f"{retorno_total*100:.2f}%")
        col_m3.metric("PL Médio 12m", format_brl(pl_medio_12m))
        col_m4.metric("Cotistas Atuais", f"{cotistas_atuais:,}".replace(",", "."))

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Rentabilidade Histórica",
            "Volatilidade / Drawdown",
            "Captação Mensal",
            "Patrimônio Médio e Cotistas",
            "Janelas Móveis"
        ])

        with tab1:
            st.subheader("Rentabilidade Histórica")
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_QUOTA'] / df['VL_QUOTA'].iloc[0],
                mode='lines',
                name='Fundo',
                line=dict(color=color_primary, width=2.5),
                hovertemplate="Data: %{x|%d/%m/%Y}<br>Cota Normalizada: %{y:.4f}<extra></extra>"
            ))
            if tem_cdi:
                fig1.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['CDI_COTA'],
                    mode='lines',
                    name='CDI',
                    line=dict(color=color_cdi, width=2),
                    hovertemplate="Data: %{x|%d/%m/%Y}<br>CDI Cota: %{y:.4f}<extra></extra>"
                ))
            if tem_ibov:
                fig1.add_trace(go.Scatter(
                    x=df['DT_COMPTC'],
                    y=df['IBOV_COTA'],
                    mode='lines',
                    name='Ibovespa',
                    line=dict(color=color_ibov, width=2),
                    hovertemplate="Data: %{x|%d/%m/%Y}<br>Ibov Cota: %{y:.4f}<extra></extra>"
                ))
            fig1.update_layout(
                xaxis_title="Data",
                yaxis_title="Cota Normalizada",
                template="plotly_white",
                hovermode="x unified",
                height=500
            )
            fig1 = add_watermark_and_style(fig1, logo_base64,
                                           x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()],
                                           x_autorange=False)
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            st.subheader("Volatilidade e Drawdown (placeholder)")
            st.info("Implemente aqui os gráficos de volatilidade e drawdown conforme sua lógica original.")

        with tab3:
            st.subheader("Captação Mensal (placeholder)")
            st.info("Implemente aqui seu gráfico de captação mensal com base em df_monthly.")

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
                height=500
            )
            fig8 = add_watermark_and_style(fig8, logo_base64,
                                           x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()],
                                           x_autorange=False)
            st.plotly_chart(fig8, use_container_width=True)

        with tab5:
            st.subheader("Retornos em Janelas Móveis")

            janelas = {
                "12 meses (252 dias)": 252,
                "24 meses (504 dias)": 504,
                "36 meses (756 dias)":756,
                "48 meses (1008 dias)": 1008,
                "60 meses (1260 dias)": 1260
            }

            df_returns = df.copy()
            for nome, dias in janelas.items():
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

                fig9.add_trace(go.Scatter(
                    x=df_returns['DT_COMPTC'],
                    y=df_returns[f'FUNDO_{janela_selecionada}'],
                    mode='lines',
                    name=f"Retorno do Fundo — {janela_selecionada}",
                    line=dict(width=2.5, color=color_primary),
                    hovertemplate="<b>Retorno do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                ))

                if tem_cdi:
                    fig9.add_trace(go.Scatter(
                        x=df_returns['DT_COMPTC'],
                        y=df_returns[f'CDI_{janela_selecionada}'],
                        mode='lines',
                        name=f"Retorno do CDI — {janela_selecionada}",
                        line=dict(width=2.5, color=color_cdi),
                        hovertemplate="<b>Retorno do CDI</b><br>Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
                    ))

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
                    yaxis=dict(tickformat=".2%")
                )
                df_plot_returns = df_returns.dropna(subset=[f'FUNDO_{janela_selecionada}']).copy()
                if not df_plot_returns.empty:
                    fig9 = add_watermark_and_style(
                        fig9,
                        logo_base64,
                        x_range=[df_plot_returns['DT_COMPTC'].min(), df_plot_returns['DT_COMPTC'].max()],
                        x_autorange=False
                    )
                else:
                    fig9 = add_watermark_and_style(fig9, logo_base64)

                st.plotly_chart(fig9, use_container_width=True)
            else:
                st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada}.")

            # GRÁFICO: Consistência em Janelas Móveis (mantendo lógica de um benchmark por vez)
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
                        hovertemplate=f'<b>Janela:</b> %{{x}}<br><b>Consistência vs {benchmark_name_consistency}:</b> %{{y:.2f}}%<extra></extra>'
                    ))

                    fig_consistency.update_layout(
                        xaxis_title="Janela (meses)",
                        yaxis_title=f"Percentual de Superação do {benchmark_name_consistency} (%)",
                        template="plotly_white",
                        hovermode="x unified",
                        height=500,
                        yaxis=dict(range=[0, 100], ticksuffix="%")
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
    <p style='margin: 0; font-size: 0.9rem;'>
        <strong>Dashboard desenvolvido com Streamlit e Plotly</strong>
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem;'>
        Análise de Fundos de Investimentos • Copaíba Invest • 2025
    </p>
</div>
""", unsafe_allow_html=True)
