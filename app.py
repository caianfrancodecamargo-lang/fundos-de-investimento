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
import tempfile # Para criar arquivos temporários para os SVGs
import os # Para gerenciar arquivos temporários

# Importar bibliotecas para PDF
try:
    from fpdf import FPDF
    from PIL import Image # Usado para converter SVG para imagem para FPDF
    import plotly.io as pio # Para exportar gráficos como imagem
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False
    st.warning("⚠️ Bibliotecas 'fpdf2', 'Pillow' e/ou 'plotly' não encontradas. Instale com: pip install fpdf2 Pillow plotly")

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

# --- Inicialização do Session State para evitar o erro "cannot be modified" ---
if 'data_inicial_input_value' not in st.session_state:
    st.session_state.data_inicial_input_value = ""
if 'data_final_input_value' not in st.session_state:
    st.session_state.data_final_input_value = ""
if 'cnpj_input_value' not in st.session_state:
    st.session_state.cnpj_input_value = ""
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
if 'pdf_gerado_data' not in st.session_state:
    st.session_state.pdf_gerado_data = None
if 'pdf_file_name' not in st.session_state:
    st.session_state.pdf_file_name = ""
if 'cnpj' not in st.session_state: # Para armazenar o CNPJ válido
    st.session_state.cnpj = ""


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

# Sidebar com logo (SEM título "Configurações")
if logo_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" alt="Copaíba Invest"></div>',
        unsafe_allow_html=True
    )

# Input de CNPJ
cnpj_input = st.sidebar.text_input(
    "CNPJ do Fundo",
    value=st.session_state.cnpj_input_value, # Usa o valor do session_state
    placeholder="00.000.000/0000-00",
    help="Digite o CNPJ com ou sem formatação",
    key="cnpj_input_widget" # Novo key para evitar conflito
)
# Atualiza o session_state com o valor do widget
st.session_state.cnpj_input_value = cnpj_input


# Inputs de data
st.sidebar.markdown("#### Período de Análise")
col1_sidebar, col2_sidebar = st.sidebar.columns(2)

with col1_sidebar:
    data_inicial_input = st.text_input(
        "Data Inicial",
        value=st.session_state.data_inicial_input_value, # Usa o valor do session_state
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        key="data_inicial_widget" # Novo key para evitar conflito
    )
    st.session_state.data_inicial_input_value = data_inicial_input # Atualiza o session_state

with col2_sidebar:
    data_final_input = st.text_input(
        "Data Final",
        value=st.session_state.data_final_input_value, # Usa o valor do session_state
        placeholder="DD/MM/AAAA",
        help="Formato: DD/MM/AAAA",
        key="data_final_widget" # Novo key para evitar conflito
    )
    st.session_state.data_final_input_value = data_final_input # Atualiza o session_state


# Opção para mostrar CDI
st.sidebar.markdown("#### Indicadores de Comparação")
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
carregar_button = st.sidebar.button("Carregar Dados", type="primary", disabled=not (cnpj_valido and datas_validas))

# Título principal e botão de relatório
title_col, report_button_col = st.columns([0.7, 0.3])
with title_col:
    st.markdown("<h1>Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
with report_button_col:
    st.markdown("<div style='margin-top: 2.5rem;'>", unsafe_allow_html=True) # Ajuste de margem para alinhar
    gerar_relatorio_button = st.button("Gerar Relatório PDF 📄", disabled=not st.session_state.get('dados_carregados', False))
    st.markdown("</div>", unsafe_allow_html=True)

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
    if pd.isna(valor):
        return "N/A"
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_pct_port(x):
    if pd.isna(x):
        return "N/A"
    return f"{x*100:.2f}%".replace('.', ',')

# --- Funções de Análise Interpretativa ---
def analisar_rentabilidade_acumulada(rent_acum, rent_cdi_acum):
    if pd.isna(rent_acum):
        return "Não foi possível calcular a Rentabilidade Acumulada do fundo."

    analise = f"A rentabilidade acumulada do fundo no período é de {fmt_pct_port(rent_acum/100)}. "
    if pd.isna(rent_cdi_acum):
        analise += "Não foi possível comparar com o CDI."
        return analise

    analise += f"O CDI acumulado no mesmo período foi de {fmt_pct_port(rent_cdi_acum/100)}. "

    if rent_acum > rent_cdi_acum:
        analise += "O fundo **superou o CDI**, o que é um **ponto positivo** significativo, demonstrando a capacidade do gestor de gerar valor acima do benchmark de renda fixa."
        analise += "\n\n**Pontos Positivos:** Superação consistente do benchmark, indicando boa gestão e estratégia eficaz."
        analise += "\n**Pontos Negativos:** N/A (a superação é o foco principal aqui)."
    elif rent_acum < rent_cdi_acum:
        analise += "O fundo **ficou abaixo do CDI**, o que é um **ponto de atenção**, sugerindo que o retorno não foi competitivo em relação a uma aplicação de baixo risco."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Performance inferior ao benchmark, o que pode indicar desafios na estratégia ou no ambiente de mercado."
    else:
        analise += "O fundo teve uma rentabilidade similar ao CDI, o que pode ser considerado neutro, mas levanta questões sobre o risco assumido para obter o mesmo retorno do benchmark."
        analise += "\n\n**Pontos Positivos:** Retorno alinhado ao benchmark."
        analise += "\n**Pontos Negativos:** Risco assumido pode não ter sido recompensado com um retorno superior."
    return analise

def analisar_cagr(cagr_fundo, cagr_cdi):
    if pd.isna(cagr_fundo):
        return "Não foi possível calcular o CAGR do fundo."

    analise = f"O CAGR (Taxa de Crescimento Anual Composta) médio do fundo é de {fmt_pct_port(cagr_fundo/100)}. "
    if pd.isna(cagr_cdi):
        analise += "Não foi possível comparar com o CDI."
        return analise

    analise += f"O CAGR médio do CDI no mesmo período foi de {fmt_pct_port(cagr_cdi/100)}. "

    if cagr_fundo > cagr_cdi:
        analise += "O fundo **superou o CDI em termos de crescimento anual composto**, o que é um **ponto positivo** forte, indicando uma capacidade consistente de valorização ao longo do tempo."
        analise += "\n\n**Pontos Positivos:** Crescimento robusto e consistente, superando o benchmark."
        analise += "\n**Pontos Negativos:** N/A."
    elif cagr_fundo < cagr_cdi:
        analise += "O fundo **ficou abaixo do CDI em termos de crescimento anual composto**, o que é um **ponto de atenção**, sugerindo que o fundo não tem gerado valor de forma competitiva no longo prazo."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Crescimento inferior ao benchmark, o que pode impactar a rentabilidade de longo prazo."
    else:
        analise += "O fundo teve um CAGR similar ao CDI, o que pode ser neutro, mas sugere que o fundo não tem agregado valor significativo acima do benchmark."
        analise += "\n\n**Pontos Positivos:** Crescimento alinhado ao benchmark."
        analise += "\n**Pontos Negativos:** Não há superação clara do benchmark no longo prazo."
    return analise

def analisar_max_drawdown(max_drawdown):
    if pd.isna(max_drawdown):
        return "Não foi possível calcular o Max Drawdown."

    analise = f"O Max Drawdown do fundo foi de {fmt_pct_port(max_drawdown/100)}. "

    if max_drawdown > -5.0: # Quedas menores que 5%
        analise += "Este é um **Max Drawdown relativamente baixo**, indicando que o fundo tem demonstrado boa resiliência a quedas significativas no período analisado. É um **ponto positivo** para a gestão de risco."
        analise += "\n\n**Pontos Positivos:** Baixa exposição a perdas substanciais, indicando boa gestão de risco e estabilidade."
        analise += "\n**Pontos Negativos:** N/A."
    elif max_drawdown > -15.0: # Quedas entre 5% e 15%
        analise += "Este é um **Max Drawdown moderado**, comum em fundos com exposição a ativos de maior risco. A gestão deve ser avaliada em relação à recuperação pós-drawdown. É um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** Drawdown gerenciável, com potencial de recuperação."
        analise += "\n**Pontos Negativos:** Exposição a perdas que podem ser significativas para investidores mais conservadores."
    else: # Quedas maiores que 15%
        analise += "Este é um **Max Drawdown elevado**, o que indica que o fundo experimentou uma queda substancial em seu valor. Isso é um **ponto de alerta** e sugere um perfil de risco mais agressivo ou um período de mercado desfavorável."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Alta exposição a perdas, o que pode ser preocupante para a preservação de capital."
    return analise

def analisar_volatilidade(vol_hist):
    if pd.isna(vol_hist):
        return "Não foi possível calcular a Volatilidade Histórica."

    analise = f"A volatilidade histórica anualizada do fundo é de {fmt_pct_port(vol_hist/100)}. "

    if vol_hist < 5.0:
        analise += "Esta é uma **volatilidade muito baixa**, indicando um fundo com pouca oscilação de preços, geralmente associado a investimentos de renda fixa de baixo risco. É um **ponto positivo** para investidores conservadores."
        analise += "\n\n**Pontos Positivos:** Estabilidade e previsibilidade, ideal para perfis de baixo risco."
        analise += "\n**Pontos Negativos:** Potencialmente, retornos mais baixos em comparação com ativos mais voláteis."
    elif vol_hist < 15.0:
        analise += "Esta é uma **volatilidade moderada**, típica de fundos multimercado ou de renda fixa com alguma exposição a risco. É um **ponto neutro**, que deve ser avaliado em conjunto com o retorno."
        analise += "\n\n**Pontos Positivos:** Equilíbrio entre risco e retorno, adequado para perfis moderados."
        analise += "\n**Pontos Negativos:** Oscilações que podem gerar desconforto para investidores muito conservadores."
    else:
        analise += "Esta é uma **volatilidade alta**, indicando que o fundo apresenta grandes oscilações de preços, comum em fundos de ações ou com estratégias mais agressivas. É um **ponto de atenção** para investidores que buscam estabilidade."
        analise += "\n\n**Pontos Positivos:** Potencial para retornos mais altos em períodos de alta."
        analise += "\n**Pontos Negativos:** Maior risco de perdas significativas em períodos de baixa."
    return analise

def analisar_sharpe_ratio(sharpe_ratio):
    if pd.isna(sharpe_ratio):
        return "Não foi possível calcular o Sharpe Ratio."

    analise = f"O Sharpe Ratio do fundo é de {sharpe_ratio:.2f}. "

    if sharpe_ratio >= 1.0:
        analise += "Um Sharpe Ratio **igual ou superior a 1.0 é considerado bom**, indicando que o fundo está gerando um excesso de retorno razoável para o nível de risco assumido. É um **ponto positivo**."
        analise += "\n\n**Pontos Positivos:** Boa relação risco-retorno, o fundo compensa bem o risco."
        analise += "\n**Pontos Negativos:** N/A."
    elif sharpe_ratio >= 0.5:
        analise += "Um Sharpe Ratio **entre 0.5 e 1.0 é aceitável**, sugerindo que o fundo gera algum excesso de retorno, mas com uma relação risco-retorno que pode ser melhorada. É um **ponto neutro**."
        analise += "\n\n**Pontos Positivos:** Retorno positivo ajustado ao risco."
        analise += "\n**Pontos Negativos:** Pode haver oportunidades de otimização da relação risco-retorno."
    else:
        analise += "Um Sharpe Ratio **inferior a 0.5 é fraco**, indicando que o fundo não está gerando um excesso de retorno adequado para o risco que assume, ou até mesmo tem um retorno inferior ao CDI que justificasse o risco. É um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está compensando o risco, sugerindo uma performance subótima em relação ao benchmark."
    return analise

def analisar_sortino_ratio(sortino_ratio):
    if pd.isna(sortino_ratio):
        return "Não foi possível calcular o Sortino Ratio."

    analise = f"O Sortino Ratio do fundo é de {sortino_ratio:.2f}. "

    if sortino_ratio >= 1.0:
        analise += "Um Sortino Ratio **igual ou superior a 1.0 é considerado muito bom**, indicando que o fundo está gerando um excesso de retorno significativo em relação ao risco de queda (downside risk). É um **ponto positivo** forte."
        analise += "\n\n**Pontos Positivos:** Excelente relação retorno-risco de queda, o fundo protege bem o capital em momentos de baixa."
        analise += "\n**Pontos Negativos:** N/A."
    elif sortino_ratio >= 0.5:
        analise += "Um Sortino Ratio **entre 0.5 e 1.0 é aceitável**, sugerindo que o fundo gera um excesso de retorno positivo em relação ao risco de queda, mas com espaço para melhoria. É um **ponto neutro**."
        analise += "\n\n**Pontos Positivos:** Retorno positivo ajustado ao risco de queda."
        analise += "\n**Pontos Negativos:** A proteção contra quedas pode ser otimizada."
    else:
        analise += "Um Sortino Ratio **inferior a 0.5 é fraco**, indicando que o fundo não está gerando um excesso de retorno adequado em relação ao risco de queda, ou que o risco de queda é muito alto para o retorno gerado. É um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está compensando adequadamente o risco de queda, o que pode ser preocupante para a preservação de capital."
    return analise

def analisar_information_ratio(information_ratio):
    if pd.isna(information_ratio):
        return "Não foi possível calcular o Information Ratio."

    analise = f"O Information Ratio do fundo é de {information_ratio:.2f}. "

    if information_ratio >= 0.5:
        analise += "Um Information Ratio **igual ou superior a 0.5 é considerado muito bom**, indicando que o gestor tem uma habilidade consistente em gerar retornos acima do benchmark (alfa) de forma ativa. É um **ponto positivo** forte."
        analise += "\n\n**Pontos Positivos:** Forte capacidade de gestão ativa e geração de alfa."
        analise += "\n**Pontos Negativos:** N/A."
    elif information_ratio >= 0.0:
        analise += "Um Information Ratio **entre 0.0 e 0.5 é aceitável**, sugerindo que o gestor tem alguma habilidade em gerar alfa, mas com espaço para melhoria na consistência ou magnitude. É um **ponto neutro**."
        analise += "\n\n**Pontos Positivos:** Geração de alfa positiva."
        analise += "\n**Pontos Negativos:** A consistência ou o tamanho do alfa podem ser aprimorados."
    else:
        analise += "Um Information Ratio **inferior a 0.0 é fraco**, indicando que o gestor não está conseguindo gerar retornos acima do benchmark, ou que a gestão ativa está resultando em retornos abaixo do esperado. É um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Falta de habilidade em gerar alfa, a gestão ativa pode estar prejudicando a performance."
    return analise

def analisar_calmar_ratio(calmar_ratio):
    if pd.isna(calmar_ratio):
        return "Não foi possível calcular o Calmar Ratio."

    analise = f"O Calmar Ratio do fundo é de {calmar_ratio:.2f}. "

    if calmar_ratio >= 0.5:
        analise += "Um Calmar Ratio **igual ou superior a 0.5 é considerado bom**, indicando que o fundo tem um bom retorno anualizado em relação ao seu maior drawdown. É um **ponto positivo**."
        analise += "\n\n**Pontos Positivos:** Boa recuperação e resiliência após quedas, o fundo entrega bom retorno para o risco de drawdown."
        analise += "\n**Pontos Negativos:** N/A."
    elif calmar_ratio >= 0.0:
        analise += "Um Calmar Ratio **entre 0.0 e 0.5 é aceitável**, sugerindo que o fundo gera retorno positivo, mas a relação com o drawdown pode ser melhorada. É um **ponto neutro**."
        analise += "\n\n**Pontos Positivos:** Retorno positivo."
        analise += "\n**Pontos Negativos:** A recuperação após drawdowns pode ser mais lenta ou menos eficiente."
    else:
        analise += "Um Calmar Ratio **inferior a 0.0 é fraco**, indicando que o fundo não está gerando retorno suficiente para compensar seu maior drawdown, ou que o drawdown foi excessivamente grande. É um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Retorno insuficiente para o risco de drawdown, o que pode ser preocupante para a preservação de capital."
    return analise

def analisar_sterling_ratio(sterling_ratio):
    if pd.isna(sterling_ratio):
        return "Não foi possível calcular o Sterling Ratio."

    analise = f"O Sterling Ratio do fundo é de {sterling_ratio:.2f}. "

    if sterling_ratio >= 0.5:
        analise += "Um Sterling Ratio **igual ou superior a 0.5 é considerado bom**, indicando que o fundo tem um bom retorno anualizado em relação ao seu drawdown médio. É um **ponto positivo**."
        analise += "\n\n**Pontos Positivos:** Boa gestão de risco de drawdown, o fundo entrega bom retorno para a magnitude das quedas."
        analise += "\n**Pontos Negativos:** N/A."
    elif sterling_ratio >= 0.0:
        analise += "Um Sterling Ratio **entre 0.0 e 0.5 é aceitável**, sugerindo que o fundo gera retorno positivo, mas a relação com o drawdown pode ser melhorada. É um **ponto neutro**."
        analise += "\n\n**Pontos Positivos:** Retorno positivo."
        analise += "\n**Pontos Negativos:** A gestão de drawdowns pode ser mais eficiente."
    else:
        analise += "Um Sterling Ratio **inferior a 0.0 é fraco**, indicando que o fundo não está gerando retorno suficiente para compensar seus drawdowns, ou que os drawdowns são muito frequentes/intensos. É um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Retorno insuficiente para o risco de drawdown, o que pode ser preocupante para a preservação de capital."
    return analise

def analisar_ulcer_index(ulcer_index):
    if pd.isna(ulcer_index):
        return "Não foi possível calcular o Ulcer Index."

    analise = f"O Ulcer Index do fundo é de {ulcer_index:.2f}. "

    if ulcer_index < 0.05:
        analise += "Um Ulcer Index **inferior a 0.05 é considerado muito baixo**, indicando que o fundo apresenta pouca "
        analise += "profundidade e duração de drawdowns. É um **ponto positivo** para a estabilidade e conforto do investidor."
        analise += "\n\n**Pontos Positivos:** Baixa 'dor' para o investidor, com drawdowns suaves e de curta duração."
        analise += "\n**Pontos Negativos:** N/A."
    elif ulcer_index < 0.15:
        analise += "Um Ulcer Index **entre 0.05 e 0.15 é moderado**, sugerindo que o fundo tem drawdowns gerenciáveis "
        analise += "em termos de profundidade e duração. É um **ponto neutro**."
        analise += "\n\n**Pontos Positivos:** Drawdowns controlados, com impacto moderado no capital."
        analise += "\n**Pontos Negativos:** Pode haver períodos de desconforto para investidores mais avessos ao risco."
    else:
        analise += "Um Ulcer Index **superior a 0.15 é alto**, indicando que o fundo apresenta drawdowns "
        analise += "frequentes, profundos ou de longa duração. É um **ponto de atenção** para a tolerância ao risco do investidor."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Alta 'dor' para o investidor, com drawdowns que podem ser severos e prolongados."
    return analise

def analisar_martin_ratio(martin_ratio):
    if pd.isna(martin_ratio):
        return "Não foi possível calcular o Martin Ratio."

    analise = f"O Martin Ratio do fundo é de {martin_ratio:.2f}. "

    if martin_ratio >= 1.0:
        analise += "Um Martin Ratio **igual ou superior a 1.0 é considerado bom**, indicando que o fundo entrega um bom excesso de retorno em relação à 'dor' dos drawdowns (Ulcer Index). É um **ponto positivo**."
        analise += "\n\n**Pontos Positivos:** Excelente relação retorno-risco de drawdown, o fundo compensa bem o desconforto das quedas."
        analise += "\n**Pontos Negativos:** N/A."
    elif martin_ratio >= 0.0:
        analise += "Um Martin Ratio **entre 0.0 e 1.0 é aceitável**, sugerindo que o fundo gera excesso de retorno, mas a relação com o Ulcer Index pode ser melhorada. É um **ponto neutro**."
        analise += "\n\n**Pontos Positivos:** Retorno positivo ajustado ao risco de drawdown."
        analise += "\n**Pontos Negativos:** A eficiência em compensar a 'dor' dos drawdowns pode ser otimizada."
    else:
        analise += "Um Martin Ratio **inferior a 0.0 é fraco**, indicando que o fundo não está gerando excesso de retorno suficiente para compensar a 'dor' dos drawdowns, ou que o Ulcer Index é muito alto para o retorno gerado. É um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está compensando adequadamente o risco de drawdown, o que pode ser preocupante para a preservação de capital."
    return analise

def analisar_var_es(VaR_95, VaR_99, ES_95, ES_99):
    analise = "As métricas de VaR (Value at Risk) e ES (Expected Shortfall) são cruciais para entender o risco de cauda do fundo. "

    if not pd.isna(VaR_95):
        analise += f"\n\n**VaR 95% ({fmt_pct_port(VaR_95)}):** Há 95% de confiança de que a perda máxima do fundo em um mês não excederá {fmt_pct_port(VaR_95)}. "
        if VaR_95 < -0.05: # Perdas menores que 5%
            analise += "Este é um **VaR 95% relativamente baixo**, indicando que o fundo tem um risco de perda controlável. É um **ponto positivo**."
        else:
            analise += "Este é um **VaR 95% mais elevado**, sugerindo um risco de perda maior. É um **ponto de atenção**."
    else:
        analise += "\n\nVaR 95% não foi calculado."

    if not pd.isna(ES_95):
        analise += f"\n**ES 95% ({fmt_pct_port(ES_95)}):** Se a perda exceder o VaR 95%, a perda média esperada é de {fmt_pct_port(ES_95)}. "
        if ES_95 < -0.07: # Perdas médias menores que 7%
            analise += "Este **ES 95% é moderado**, indicando que as perdas extremas, quando ocorrem, são gerenciáveis. É um **ponto positivo**."
        else:
            analise += "Este **ES 95% é mais elevado**, sugerindo que as perdas extremas podem ser substanciais. É um **ponto de atenção**."
    else:
        analise += "\nES 95% não foi calculado."

    if not pd.isna(VaR_99):
        analise += f"\n\n**VaR 99% ({fmt_pct_port(VaR_99)}):** Há 99% de confiança de que a perda máxima do fundo em um mês não excederá {fmt_pct_port(VaR_99)}. "
        if VaR_99 < -0.10: # Perdas menores que 10%
            analise += "Este é um **VaR 99% relativamente baixo**, indicando um risco de cauda controlado. É um **ponto positivo**."
        else:
            analise += "Este é um **VaR 99% mais elevado**, sugerindo um risco de cauda maior. É um **ponto de atenção**."
    else:
        analise += "\n\nVaR 99% não foi calculado."

    if not pd.isna(ES_99):
        analise += f"\n**ES 99% ({fmt_pct_port(ES_99)}):** Se a perda exceder o VaR 99%, a perda média esperada é de {fmt_pct_port(ES_99)}. "
        if ES_99 < -0.12: # Perdas médias menores que 12%
            analise += "Este **ES 99% é moderado**, indicando que as perdas extremas mais raras são gerenciáveis. É um **ponto positivo**."
        else:
            analise += "Este **ES 99% é mais elevado**, sugerindo que as perdas extremas mais raras podem ser muito severas. É um **ponto de atenção**."
    else:
        analise += "\nES 99% não foi calculado."

    analise += "\n\n**Pontos Positivos:** VaR e ES baixos indicam um fundo com boa proteção contra perdas extremas."
    analise += "\n**Pontos Negativos:** VaR e ES altos indicam maior exposição a perdas significativas em cenários de estresse."
    return analise

def analisar_retornos_janelas_moveis(df_returns, tem_cdi):
    if df_returns.empty:
        return "Não há dados suficientes para analisar os retornos em janelas móveis."

    analise = "A análise de retornos em janelas móveis mostra a performance do fundo em diferentes períodos de tempo, suavizando o impacto de eventos pontuais. "

    janelas = {
        "12 meses (252 dias)": 252,
        "24 meses (504 dias)": 504,
        "36 meses (756 dias)": 756,
        "48 meses (1008 dias)": 1008,
        "60 meses (1260 dias)": 1260
    }

    for nome, dias in janelas.items():
        fund_col = f'FUNDO_{nome}'
        cdi_col = f'CDI_{nome}'

        if fund_col in df_returns.columns and not df_returns[fund_col].dropna().empty:
            retorno_fundo_medio = df_returns[fund_col].mean()
            analise += f"\n\nPara a janela de **{nome}**, o retorno médio do fundo foi de {fmt_pct_port(retorno_fundo_medio)}. "

            if tem_cdi and cdi_col in df_returns.columns and not df_returns[cdi_col].dropna().empty:
                retorno_cdi_medio = df_returns[cdi_col].mean()
                analise += f"O CDI médio foi de {fmt_pct_port(retorno_cdi_medio)}. "
                if retorno_fundo_medio > retorno_cdi_medio:
                    analise += "**O fundo superou o CDI** nesta janela, indicando uma boa performance relativa."
                elif retorno_fundo_medio < retorno_cdi_medio:
                    analise += "**O fundo ficou abaixo do CDI** nesta janela, o que é um ponto de atenção."
                else:
                    analise += "O fundo teve performance similar ao CDI nesta janela."
            else:
                analise += "Não foi possível comparar com o CDI nesta janela."
        else:
            analise += f"\n\nNão há dados suficientes para a janela de **{nome}**."

    analise += "\n\n**Pontos Positivos:** Permite identificar a consistência do fundo em diferentes ciclos de mercado. Uma superação consistente do CDI em diversas janelas é um forte indicador de qualidade."
    analise += "\n**Pontos Negativos:** Retornos passados não garantem retornos futuros. A performance em janelas específicas pode ser influenciada por eventos pontuais."
    return analise

def analisar_consistencia_janelas_moveis(df_consistency):
    if df_consistency.empty:
        return "Não há dados suficientes para analisar a consistência em janelas móveis."

    analise = "A consistência em janelas móveis mede a frequência com que o fundo superou o CDI em diferentes períodos. "

    for index, row in df_consistency.iterrows():
        janela = row['Janela']
        consistencia = row['Consistencia']
        if not pd.isna(consistencia):
            analise += f"\n\nNa janela de **{janela} meses**, o fundo superou o CDI em **{consistencia:.2f}%** das vezes. "
            if consistencia >= 70:
                analise += "Isso demonstra uma **alta consistência** na superação do benchmark, um **ponto positivo**."
            elif consistencia >= 50:
                analise += "Isso indica uma **consistência moderada**, com o fundo superando o CDI na maioria das vezes."
            else:
                analise += "Isso sugere uma **baixa consistência** na superação do CDI, um **ponto de atenção**."
        else:
            analise += f"\n\nNão há dados de consistência para a janela de **{janela} meses**."

    analise += "\n\n**Pontos Positivos:** Uma alta porcentagem de superação indica que o gestor tem uma habilidade consistente em gerar alfa."
    analise += "\n**Pontos Negativos:** Baixa consistência pode indicar que o fundo não está entregando valor superior ao benchmark de forma regular."
    return analise

# --- FUNÇÃO DE GERAÇÃO DE RELATÓRIO PDF ---
def gerar_relatorio_pdf(
    cnpj_fundo, nome_fundo, dt_ini_user, dt_fim_user,
    metrics, # Este é o dicionário metrics_display
    fig1, fig2, fig_excesso_retorno, fig3, fig4, fig5,
    fig6, fig7, fig8, fig9, fig_consistency,
    tem_cdi, logo_base64,
    df_plot_cagr, df_plot_var, df_monthly,
    df_returns, df_consistency,
    sharpe_ratio, sortino_ratio, information_ratio,
    calmar_ratio, sterling_ratio, ulcer_index, martin_ratio,
    VaR_95, VaR_99, ES_95, ES_99,
    metrics_values # Adicionado para ter acesso aos valores brutos
):
    pdf = FPDF('P', 'mm', 'A4') # 'P' para retrato, 'mm' para milímetros, 'A4' para tamanho da página
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Configurações de fonte
    pdf.set_font('Arial', '', 12)

    # Título do Relatório
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Relatório de Análise de Fundo de Investimento', 0, 1, 'C')
    pdf.ln(5)

    # Informações do Fundo
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 7, f'Fundo: {nome_fundo}', 0, 1, 'L')
    pdf.cell(0, 7, f'CNPJ: {cnpj_fundo}', 0, 1, 'L')
    pdf.cell(0, 7, f'Período: {dt_ini_user.strftime("%d/%m/%Y")} a {dt_fim_user.strftime("%d/%m/%Y")}', 0, 1, 'L')
    pdf.ln(10)

    # --- Seção de Métricas de Retorno e Risco ---
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Métricas de Retorno e Risco', 0, 1, 'L')
    pdf.ln(2)

    # Tabela de Métricas
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(70, 7, 'Métrica', 1, 0, 'L')
    pdf.cell(40, 7, 'Valor', 1, 1, 'C') # Nova linha após o valor

    pdf.set_font('Arial', '', 10)
    for metric_name, metric_value_display in metrics.items():
        pdf.cell(70, 7, metric_name, 1, 0, 'L')
        pdf.cell(40, 7, str(metric_value_display), 1, 1, 'C') # Nova linha após o valor
    pdf.ln(5)

    # Análises Interpretativas das Métricas
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 7, 'Análises Interpretativas das Métricas:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)

    # Acessando os valores brutos para as análises
    rent_acum = metrics_values.get('Rentabilidade_Acumulada_Val', np.nan)
    rent_cdi_acum = metrics_values.get('CDI_Acumulado_Val', np.nan)
    cagr_fundo = metrics_values.get('CAGR_Fundo_Val', np.nan)
    cagr_cdi = metrics_values.get('CAGR_CDI_Val', np.nan)
    max_drawdown = metrics_values.get('Max_Drawdown_Val', np.nan)
    vol_hist = metrics_values.get('Volatilidade_Historica_Val', np.nan)

    pdf.multi_cell(0, 5, analisar_rentabilidade_acumulada(rent_acum, rent_cdi_acum))
    pdf.ln(2)
    pdf.multi_cell(0, 5, analisar_cagr(cagr_fundo, cagr_cdi))
    pdf.ln(2)
    pdf.multi_cell(0, 5, analisar_max_drawdown(max_drawdown))
    pdf.ln(2)
    pdf.multi_cell(0, 5, analisar_volatilidade(vol_hist))
    pdf.ln(5)

    # --- Seção de Métricas de Risco-Retorno ---
    if tem_cdi and not pd.isna(sharpe_ratio): # Verifica se as métricas de risco-retorno foram calculadas
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '2. Métricas de Risco-Retorno', 0, 1, 'L')
        pdf.ln(2)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 7, 'Risco Medido pela Volatilidade:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, analisar_sharpe_ratio(sharpe_ratio))
        pdf.ln(2)
        pdf.multi_cell(0, 5, analisar_sortino_ratio(sortino_ratio))
        pdf.ln(2)
        pdf.multi_cell(0, 5, analisar_information_ratio(information_ratio))
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 7, 'Risco Medido pelo Drawdown:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, analisar_calmar_ratio(calmar_ratio))
        pdf.ln(2)
        pdf.multi_cell(0, 5, analisar_sterling_ratio(sterling_ratio))
        pdf.ln(2)
        pdf.multi_cell(0, 5, analisar_ulcer_index(ulcer_index))
        pdf.ln(2)
        pdf.multi_cell(0, 5, analisar_martin_ratio(martin_ratio))
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 7, 'Métricas de Risco de Cauda (VaR e ES):', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, analisar_var_es(VaR_95, VaR_99, ES_95, ES_99))
        pdf.ln(5)

    # --- Seção de Gráficos ---
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Gráficos de Performance e Risco', 0, 1, 'L')
    pdf.ln(2)

    # Helper para adicionar gráfico
    def add_plotly_figure_to_pdf(pdf_obj, fig, title, width=180, height=100):
        if fig is None:
            pdf_obj.set_font('Arial', 'I', 10)
            pdf_obj.cell(0, 10, f'Não foi possível gerar o gráfico: {title}', 0, 1, 'C')
            pdf_obj.ln(5)
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            file_path = tmpfile.name
            pio.write_image(fig, file_path, format='png', width=1200, height=600, scale=2.0) # Alta resolução

        pdf_obj.set_font('Arial', 'B', 12)
        pdf_obj.cell(0, 7, title, 0, 1, 'L')
        pdf_obj.image(file_path, x=pdf_obj.get_x(), w=width, h=height)
        pdf_obj.ln(height + 5) # Adiciona um espaço após a imagem
        os.remove(file_path) # Limpa o arquivo temporário

    # Gráfico 1: Rentabilidade Acumulada
    add_plotly_figure_to_pdf(pdf, fig1, 'Rentabilidade Acumulada do Fundo vs. CDI')
    pdf.ln(2)

    # Gráfico 2: Rentabilidade Mensal
    add_plotly_figure_to_pdf(pdf, fig2, 'Rentabilidade Mensal do Fundo vs. CDI')
    pdf.ln(2)

    # Gráfico de Excesso de Retorno
    if fig_excesso_retorno is not None:
        add_plotly_figure_to_pdf(pdf, fig_excesso_retorno, 'Excesso de Retorno Mensal do Fundo sobre o CDI')
        pdf.ln(2)

    # Gráfico 3: Distribuição de Retornos
    add_plotly_figure_to_pdf(pdf, fig3, 'Distribuição de Retornos Diários')
    pdf.ln(2)

    # Gráfico 4: Drawdown
    add_plotly_figure_to_pdf(pdf, fig4, 'Drawdown do Fundo')
    pdf.ln(2)

    # Gráfico 5: VaR e ES
    add_plotly_figure_to_pdf(pdf, fig5, 'VaR e ES Mensal')
    pdf.ln(2)

    # Gráfico 6: Patrimônio e Captação Líquida
    add_plotly_figure_to_pdf(pdf, fig6, 'Patrimônio Líquido e Captação Líquida Acumulada')
    pdf.ln(2)

    # Gráfico 7: Captação Líquida Mensal
    add_plotly_figure_to_pdf(pdf, fig7, 'Captação Líquida Mensal')
    pdf.ln(2)

    # Gráfico 8: Patrimônio Médio e Nº de Cotistas
    add_plotly_figure_to_pdf(pdf, fig8, 'Patrimônio Médio por Cotista e Número de Cotistas')
    pdf.ln(2)

    # Gráfico 9: Retornos em Janelas Móveis
    add_plotly_figure_to_pdf(pdf, fig9, 'Retornos em Janelas Móveis')
    pdf.ln(2)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, analisar_retornos_janelas_moveis(df_returns, tem_cdi))
    pdf.ln(5)

    # Gráfico de Consistência em Janelas Móveis
    if fig_consistency is not None:
        add_plotly_figure_to_pdf(pdf, fig_consistency, 'Consistência em Janelas Móveis (Superação do CDI)')
        pdf.ln(2)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, analisar_consistencia_janelas_moveis(df_consistency))
        pdf.ln(5)


    # --- Conclusão Final ---
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '4. Conclusão Geral', 0, 1, 'L')
    pdf.ln(2)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, """
    Este relatório apresenta uma análise abrangente do fundo de investimento, cobrindo aspectos de rentabilidade, risco, captação e consistência. As métricas e gráficos fornecem uma visão detalhada da performance do fundo em relação ao CDI (quando aplicável) e em diferentes cenários de mercado.

    É fundamental que a interpretação desses dados seja feita considerando a estratégia específica do fundo, seu mandato, o horizonte de investimento do cotista e as condições macroeconômicas. A performance passada não é garantia de resultados futuros.

    Para uma análise mais aprofundada ou para discutir estratégias de investimento personalizadas, entre em contato com um especialista da Copaíba Invest.
    """)
    pdf.ln(10)

    # Logo no rodapé (opcional, se quiser uma menor no final)
    if logo_base64:
        # Decodifica a imagem base64 para um arquivo temporário para FPDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_logo_file:
            tmp_logo_file.write(base64.b64decode(logo_base64))
            tmp_logo_path = tmp_logo_file.name

        pdf.image(tmp_logo_path, x=pdf.w - 40, y=pdf.h - 25, w=30)
        os.remove(tmp_logo_path) # Limpa o arquivo temporário

    return pdf.output(dest='S').encode('latin-1') # Retorna o PDF como bytes


# --- Lógica principal do Streamlit ---
if carregar_button:
    if cnpj_valido and datas_validas:
        st.session_state.cnpj = cnpj_limpo # Armazena o CNPJ válido no session_state
        st.session_state.dt_ini_user = dt_ini # Armazena a data inicial válida
        st.session_state.dt_fim_user = dt_fim # Armazena a data final válida

        with st.spinner("Carregando dados do fundo..."):
            try:
                df_raw = carregar_dados_api(cnpj_limpo, data_inicial_formatada, data_final_formatada)

                if df_raw.empty:
                    st.error("❌ Não foram encontrados dados para o CNPJ e período selecionados.")
                    st.session_state.dados_carregados = False
                else:
                    # Filtra o DataFrame para o período exato solicitado pelo usuário
                    df = df_raw[(df_raw['DT_COMPTC'] >= st.session_state.dt_ini_user) & (df_raw['DT_COMPTC'] <= st.session_state.dt_fim_user)].copy()

                    if df.empty:
                        st.error("❌ Não há dados disponíveis para o período exato selecionado após o filtro.")
                        st.session_state.dados_carregados = False
                    else:
                        df = df.sort_values('DT_COMPTC').reset_index(drop=True)
                        df['VL_QUOTA'] = pd.to_numeric(df['VL_QUOTA'], errors='coerce')
                        df['CAPTC_DIA'] = pd.to_numeric(df['CAPTC_DIA'], errors='coerce')
                        df['RESG_DIA'] = pd.to_numeric(df['RESG_DIA'], errors='coerce')
                        df['NR_COTST'] = pd.to_numeric(df['NR_COTST'], errors='coerce')
                        df['VL_PATRIM_LIQ'] = pd.to_numeric(df['VL_PATRIM_LIQ'], errors='coerce')

                        # Preencher valores ausentes para cálculo de rentabilidade
                        df['VL_QUOTA'] = df['VL_QUOTA'].ffill().bfill()
                        df['VL_PATRIM_LIQ'] = df['VL_PATRIM_LIQ'].ffill().bfill()
                        df['NR_COTST'] = df['NR_COTST'].ffill().bfill()

                        # Calcular Patrimônio Líquido Médio por Cotista
                        df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

                        # Calcular Captação Líquida Acumulada
                        df['Soma_Acumulada'] = (df['CAPTC_DIA'] - df['RESG_DIA']).cumsum()

                        # Calcular Variação Percentual Diária
                        df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()

                        # Calcular Drawdown
                        df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
                        df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100

                        # Obter nome do fundo
                        nome_fundo = df['DENOM_SOCIAL'].iloc[0] if not df.empty else "Fundo Desconhecido"
                        st.session_state.nome_fundo = nome_fundo

                        # Obter dados do CDI
                        tem_cdi = False
                        if mostrar_cdi and BCB_DISPONIVEL:
                            cdi_df = obter_dados_cdi_real(st.session_state.dt_ini_user, st.session_state.dt_fim_user)
                            if not cdi_df.empty:
                                # Mesclar CDI com o DataFrame do fundo
                                df = pd.merge(df, cdi_df[['DT_COMPTC', 'VL_CDI_normalizado', 'cdi']], on='DT_COMPTC', how='left')
                                df = df.rename(columns={'VL_CDI_normalizado': 'CDI_COTA', 'cdi': 'CDI_TAXA_DIARIA'})
                                df['CDI_COTA'] = df['CDI_COTA'].ffill().bfill() # Preenche NaNs após merge
                                df['CDI_TAXA_DIARIA'] = df['CDI_TAXA_DIARIA'].ffill().bfill() # Preenche NaNs após merge
                                tem_cdi = True
                            else:
                                st.warning("⚠️ Não foi possível obter dados do CDI para o período selecionado.")

                        # Se não tem CDI, garante que as colunas existam com NaN para evitar erros
                        if not tem_cdi:
                            df['CDI_COTA'] = np.nan
                            df['CDI_TAXA_DIARIA'] = np.nan

                        st.session_state.df = df
                        st.session_state.tem_cdi = tem_cdi
                        st.session_state.dados_carregados = True
                        st.success(f"✅ Dados do fundo '{nome_fundo}' carregados com sucesso!")

            except urllib.error.HTTPError as http_e:
                if http_e.code == 404:
                    st.error(f"❌ CNPJ não encontrado ou dados indisponíveis para o período: {cnpj_limpo}")
                else:
                    st.error(f"❌ Erro HTTP ao carregar dados: {http_e}")
                st.session_state.dados_carregados = False
            except Exception as e:
                st.error(f"❌ Erro ao carregar os dados: {str(e)}")
                st.session_state.dados_carregados = False
    else:
        st.warning("Preencha o CNPJ e as datas corretamente para carregar os dados.")

# --- Exibição do Dashboard ---
if st.session_state.get('dados_carregados', False):
    df = st.session_state.df
    tem_cdi = st.session_state.tem_cdi
    nome_fundo = st.session_state.nome_fundo
    dt_ini_user = st.session_state.dt_ini_user
    dt_fim_user = st.session_state.dt_fim_user

    # Cores para os gráficos
    color_primary = '#1a5f3f'
    color_secondary = '#2d8659'
    color_accent = '#f0b429'
    color_cdi = '#6c757d'
    color_danger = '#dc3545'

    # Inicializa variáveis para os gráficos e métricas para o PDF
    fig1, fig2, fig_excesso_retorno, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig_consistency = [None] * 11
    metrics_display = {}
    metrics_values = {} # Para armazenar os valores brutos
    sharpe_ratio, sortino_ratio, information_ratio, calmar_ratio, sterling_ratio, ulcer_index, martin_ratio = [np.nan] * 7
    VaR_95, VaR_99, ES_95, ES_99 = [np.nan] * 4
    df_plot_cagr, df_plot_var, df_monthly, df_returns, df_consistency = [pd.DataFrame()] * 5


    st.subheader(f"Análise do Fundo: {nome_fundo}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Rentabilidade", "Risco", "Patrimônio e Captação", "Cotistas", "Janelas Móveis"
    ])

    with tab1:
        st.subheader("Rentabilidade Acumulada")

        # Calcular Rentabilidade Acumulada
        rent_acum = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0] - 1) * 100
        metrics_values['Rentabilidade_Acumulada_Val'] = rent_acum
        metrics_display['Rentabilidade Acumulada'] = fmt_pct_port(rent_acum / 100)

        # Calcular CDI Acumulado
        rent_cdi_acum = np.nan
        if tem_cdi and not df['CDI_COTA'].empty:
            rent_cdi_acum = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0] - 1) * 100
            metrics_values['CDI_Acumulado_Val'] = rent_cdi_acum
            metrics_display['CDI Acumulado'] = fmt_pct_port(rent_cdi_acum / 100)

        # Plotar Rentabilidade Acumulada
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=(df['VL_QUOTA'] / df['VL_QUOTA'].iloc[0] - 1) * 100,
            mode='lines',
            name='Fundo',
            line=dict(color=color_primary, width=2.5),
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
        ))
        if tem_cdi:
            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=(df['CDI_COTA'] / df['CDI_COTA'].iloc[0] - 1) * 100,
                mode='lines',
                name='CDI',
                line=dict(color=color_cdi, width=2.5, dash='dash'),
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
        fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig1, use_container_width=True)
        st.info(analisar_rentabilidade_acumulada(rent_acum, rent_cdi_acum))

        st.subheader("Rentabilidade Mensal")

        df_monthly_returns = df.set_index('DT_COMPTC')['VL_QUOTA'].resample('M').last().pct_change().dropna() * 100
        if tem_cdi:
            df_cdi_monthly_returns = df.set_index('DT_COMPTC')['CDI_COTA'].resample('M').last().pct_change().dropna() * 100

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_monthly_returns.index,
            y=df_monthly_returns,
            name='Fundo',
            marker_color=color_primary,
            hovertemplate='Mês: %{x|%b/%Y}<br>Rentabilidade Fundo: %{y:.2f}%<extra></extra>'
        ))
        if tem_cdi:
            fig2.add_trace(go.Bar(
                x=df_cdi_monthly_returns.index,
                y=df_cdi_monthly_returns,
                name='CDI',
                marker_color=color_cdi,
                hovertemplate='Mês: %{x|%b/%Y}<br>Rentabilidade CDI: %{y:.2f}%<extra></extra>'
            ))

        fig2.update_layout(
            xaxis_title="Mês",
            yaxis_title="Rentabilidade Mensal (%)",
            template="plotly_white",
            hovermode="x unified",
            barmode='group',
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
        if not df_monthly_returns.empty:
            fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df_monthly_returns.index.min(), df_monthly_returns.index.max()], x_autorange=False)
        else:
            fig2 = add_watermark_and_style(fig2, logo_base64)
        st.plotly_chart(fig2, use_container_width=True)

        # Gráfico de Excesso de Retorno Mensal (se tiver CDI)
        fig_excesso_retorno = None
        if tem_cdi and not df_monthly_returns.empty and not df_cdi_monthly_returns.empty:
            df_excess_returns = df_monthly_returns - df_cdi_monthly_returns
            colors_excess = [color_primary if x >= 0 else color_danger for x in df_excess_returns]

            fig_excesso_retorno = go.Figure([
                go.Bar(
                    x=df_excess_returns.index,
                    y=df_excess_returns,
                    name='Excesso de Retorno',
                    marker_color=colors_excess,
                    hovertemplate='Mês: %{x|%b/%Y}<br>Excesso de Retorno: %{y:.2f}%<extra></extra>'
                )
            ])
            fig_excesso_retorno.update_layout(
                xaxis_title="Mês",
                yaxis_title="Excesso de Retorno Mensal (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64, x_range=[df_excess_returns.index.min(), df_excess_returns.index.max()], x_autorange=False)
            st.plotly_chart(fig_excesso_retorno, use_container_width=True)

        st.subheader("CAGR (Taxa de Crescimento Anual Composta)")

        # Calcular CAGR
        num_days = len(df)
        trading_days_in_year = 252 # Dias úteis em um ano
        mean_cagr = np.nan
        cagr_cdi = np.nan

        if num_days >= trading_days_in_year:
            # Cálculo do CAGR do Fundo
            df_plot_cagr = df.copy()
            df_plot_cagr['CAGR_Fundo'] = np.nan
            for i in range(trading_days_in_year - 1, num_days):
                # O cálculo deve ser feito para o período de 252 dias ANTERIORES ao dia atual (i)
                # Ou seja, do dia (i - 251) até o dia (i)
                start_val = df_plot_cagr['VL_QUOTA'].iloc[i - (trading_days_in_year - 1)]
                end_val = df_plot_cagr['VL_QUOTA'].iloc[i]

                if start_val > 0:
                    cagr_calc = ((end_val / start_val)**(trading_days_in_year / trading_days_in_year) - 1) * 100
                    df_plot_cagr.loc[i, 'CAGR_Fundo'] = cagr_calc

            mean_cagr = df_plot_cagr['CAGR_Fundo'].mean() # Média dos CAGRs móveis
            metrics_values['CAGR_Fundo_Val'] = mean_cagr
            metrics_display['CAGR Fundo'] = fmt_pct_port(mean_cagr / 100)

            # Cálculo do CAGR do CDI
            if tem_cdi and not df['CDI_COTA'].empty:
                df_plot_cagr['CAGR_CDI'] = np.nan
                for i in range(trading_days_in_year - 1, num_days):
                    start_val_cdi = df_plot_cagr['CDI_COTA'].iloc[i - (trading_days_in_year - 1)]
                    end_val_cdi = df_plot_cagr['CDI_COTA'].iloc[i]
                    if start_val_cdi > 0:
                        cagr_cdi_calc = ((end_val_cdi / start_val_cdi)**(trading_days_in_year / trading_days_in_year) - 1) * 100
                        df_plot_cagr.loc[i, 'CAGR_CDI'] = cagr_cdi_calc
                cagr_cdi = df_plot_cagr['CAGR_CDI'].mean() # Média dos CAGRs móveis do CDI
                metrics_values['CAGR_CDI_Val'] = cagr_cdi
                metrics_display['CAGR CDI'] = fmt_pct_port(cagr_cdi / 100)

            fig_cagr = go.Figure()
            fig_cagr.add_trace(go.Scatter(
                x=df_plot_cagr['DT_COMPTC'],
                y=df_plot_cagr['CAGR_Fundo'],
                mode='lines',
                name='CAGR Fundo',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR Fundo: %{y:.2f}%<extra></extra>'
            ))
            if tem_cdi:
                fig_cagr.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=df_plot_cagr['CAGR_CDI'],
                    mode='lines',
                    name='CAGR CDI',
                    line=dict(color=color_cdi, width=2.5, dash='dash'),
                    hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR CDI: %{y:.2f}%<extra></extra>'
                ))
            fig_cagr.update_layout(
                xaxis_title="Data",
                yaxis_title="CAGR Anualizado (%)",
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
            fig_cagr = add_watermark_and_style(fig_cagr, logo_base64, x_range=[df_plot_cagr['DT_COMPTC'].min(), df_plot_cagr['DT_COMPTC'].max()], x_autorange=False)
            st.plotly_chart(fig_cagr, use_container_width=True)
            st.info(analisar_cagr(mean_cagr, cagr_cdi))
        else:
            st.warning("⚠️ Não há dados suficientes para calcular o CAGR (mínimo de 1 ano de dados).")
            df_plot_cagr = pd.DataFrame() # Garante que a variável seja um DataFrame vazio se não for calculada

    with tab2:
        st.subheader("Max Drawdown")

        max_drawdown_value = df['Drawdown'].min() if not df['Drawdown'].empty else np.nan
        metrics_values['Max_Drawdown_Val'] = max_drawdown_value
        metrics_display['Max Drawdown'] = fmt_pct_port(max_drawdown_value / 100)

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['Drawdown'],
            mode='lines',
            name='Drawdown',
            line=dict(color=color_danger, width=2.5),
            fill='tozeroy',
            fillcolor='rgba(220, 53, 69, 0.1)',
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
        ))
        fig4.update_layout(
            xaxis_title="Data",
            yaxis_title="Drawdown (%)",
            template="plotly_white",
            hovermode="x unified",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        fig4 = add_watermark_and_style(fig4, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig4, use_container_width=True)
        st.info(analisar_max_drawdown(max_drawdown_value))

        st.subheader("Volatilidade Histórica Anualizada")

        vol_hist = np.nan
        if not df['Variacao_Perc'].empty:
            trading_days_in_year = 252
            vol_hist = df['Variacao_Perc'].std() * np.sqrt(trading_days_in_year) * 100
        metrics_values['Volatilidade_Historica_Val'] = vol_hist
        metrics_display['Volatilidade Histórica'] = fmt_pct_port(vol_hist / 100)

        st.metric("Volatilidade Histórica Anualizada", fmt_pct_port(vol_hist / 100))
        st.info(analisar_volatilidade(vol_hist))

        st.subheader("Distribuição de Retornos Diários")

        fig3 = go.Figure(data=[go.Histogram(
            x=df['Variacao_Perc'] * 100,
            nbinsx=50,
            marker_color=color_primary,
            hovertemplate='Intervalo: %{x}<br>Frequência: %{y}<extra></extra>'
        )])
        fig3.update_layout(
            xaxis_title="Retorno Diário (%)",
            yaxis_title="Frequência",
            template="plotly_white",
            height=500,
            font=dict(family="Inter, sans-serif")
        )
        fig3 = add_watermark_and_style(fig3, logo_base64)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("VaR (Value at Risk) e ES (Expected Shortfall) Mensal")

        VaR_95, VaR_99, ES_95, ES_99 = [np.nan] * 4
        df_plot_var = pd.DataFrame()

        if not df['Variacao_Perc'].empty and len(df['Variacao_Perc'].dropna()) >= 21: # Mínimo de 21 dias para 1 mês
            # Retornos diários para cálculo
            daily_returns = df['Variacao_Perc'].dropna()

            # Calcular VaR e ES
            VaR_95 = daily_returns.quantile(0.05) * np.sqrt(21) # Mensalizado (aprox. 21 dias úteis)
            VaR_99 = daily_returns.quantile(0.01) * np.sqrt(21)

            ES_95 = daily_returns[daily_returns <= daily_returns.quantile(0.05)].mean() * np.sqrt(21)
            ES_99 = daily_returns[daily_returns <= daily_returns.quantile(0.01)].mean() * np.sqrt(21)

            metrics_values['VaR_95_Val'] = VaR_95
            metrics_values['VaR_99_Val'] = VaR_99
            metrics_values['ES_95_Val'] = ES_95
            metrics_values['ES_99_Val'] = ES_99

            metrics_display['VaR 95% (Mensal)'] = fmt_pct_port(VaR_95)
            metrics_display['ES 95% (Mensal)'] = fmt_pct_port(ES_95)
            metrics_display['VaR 99% (Mensal)'] = fmt_pct_port(VaR_99)
            metrics_display['ES 99% (Mensal)'] = fmt_pct_port(ES_99)

            # Plotar VaR e ES (simulação de distribuição para visualização)
            # Para o gráfico, vamos usar a distribuição dos retornos diários e marcar os pontos de VaR/ES
            # Criar um DataFrame para plotar a distribuição e os valores de VaR/ES
            df_plot_var = pd.DataFrame({'Retorno Diário': daily_returns * 100})

            fig5 = go.Figure()
            fig5.add_trace(go.Histogram(
                x=df_plot_var['Retorno Diário'],
                nbinsx=50,
                name='Distribuição de Retornos Diários',
                marker_color=color_primary,
                opacity=0.7,
                hovertemplate='Intervalo: %{x}<br>Frequência: %{y}<extra></extra>'
            ))

            # Adicionar linhas para VaR e ES (convertidos para diário para o gráfico)
            fig5.add_vline(x=VaR_95 * 100 / np.sqrt(21), line_width=2, line_dash="dash", line_color=color_danger,
                           annotation_text=f"VaR 95% Diário: {VaR_95 * 100 / np.sqrt(21):.2f}%",
                           annotation_position="top right")
            fig5.add_vline(x=ES_95 * 100 / np.sqrt(21), line_width=2, line_dash="dot", line_color=color_danger,
                           annotation_text=f"ES 95% Diário: {ES_95 * 100 / np.sqrt(21):.2f}%",
                           annotation_position="bottom right")
            fig5.add_vline(x=VaR_99 * 100 / np.sqrt(21), line_width=2, line_dash="dash", line_color=color_accent,
                           annotation_text=f"VaR 99% Diário: {VaR_99 * 100 / np.sqrt(21):.2f}%",
                           annotation_position="top left")
            fig5.add_vline(x=ES_99 * 100 / np.sqrt(21), line_width=2, line_dash="dot", line_color=color_accent,
                           annotation_text=f"ES 99% Diário: {ES_99 * 100 / np.sqrt(21):.2f}%",
                           annotation_position="bottom left")

            fig5.update_layout(
                xaxis_title="Rentabilidade (%)",
                yaxis_title="Frequência",
                template="plotly_white",
                hovermode="x unified",
                height=600,
                font=dict(family="Inter, sans-serif")
            )
            # Ajusta o range do eixo X para os dados de df_plot_var
            fig5 = add_watermark_and_style(fig5, logo_base64, x_autorange=True)
            st.plotly_chart(fig5, use_container_width=True)

            st.info(analisar_var_es(VaR_95, VaR_99, ES_95, ES_99))
        else:
            st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias de retorno).")
            fig5 = None # Garante que a variável seja None se o gráfico não for gerado

        st.subheader("Métricas de Risco-Retorno")

        # --- Cálculos dos Novos Indicadores ---
        calmar_ratio, sterling_ratio, ulcer_index, martin_ratio, sharpe_ratio, sortino_ratio, information_ratio = [np.nan] * 7

        if tem_cdi and not df.empty and len(df) > trading_days_in_year:
            # Retorno total do fundo e CDI no período
            total_fund_return = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1
            total_cdi_return = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0] - 1) # Usar CDI_COTA

            # Anualização dos retornos totais para consistência
            num_days_in_period = len(df)
            if num_days_in_period > 0:
                annualized_fund_return = (1 + total_fund_return)**(trading_days_in_year / num_days_in_period) - 1
                annualized_cdi_return = (1 + total_cdi_return)**(trading_days_in_year / num_days_in_period) - 1
            else:
                annualized_fund_return = np.nan
                annualized_cdi_return = np.nan

            # Volatilidade anualizada do fundo (já calculada como vol_hist, convertida para decimal)
            annualized_fund_volatility = vol_hist / 100 if not pd.isna(vol_hist) else np.nan

            # Max Drawdown (já calculada como df['Drawdown'].min(), convertida para decimal)
            max_drawdown_value_decimal = df['Drawdown'].min() / 100 if not df['Drawdown'].empty else np.nan

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

            # Tracking Error
            if 'CDI_TAXA_DIARIA' in df.columns and not df['Variacao_Perc'].empty:
                excess_daily_returns = df['Variacao_Perc'] - (df['CDI_TAXA_DIARIA'] / 100)
                if not excess_daily_returns.empty:
                    tracking_error = excess_daily_returns.std() * np.sqrt(trading_days_in_year)
                else:
                    tracking_error = np.nan
            else:
                tracking_error = np.nan

            # --- Cálculo dos Ratios ---
            if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(max_drawdown_value_decimal) and max_drawdown_value_decimal != 0:
                calmar_ratio = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value_decimal)
                sterling_ratio = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value_decimal) # Simplificado para Max Drawdown

            if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(ulcer_index) and ulcer_index != 0:
                martin_ratio = (cagr_fund_decimal - annualized_cdi_return) / ulcer_index

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0:
                sharpe_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_fund_volatility

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0:
                sortino_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_downside_volatility

            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(tracking_error) and tracking_error != 0:
                information_ratio = (annualized_fund_return - annualized_cdi_return) / tracking_error

            # --- Exibição dos Cards e Explicações ---
            st.markdown("#### RISCO MEDIDO PELA VOLATILIDADE:")
            col_vol_1, col_vol_2 = st.columns(2)

            with col_vol_1:
                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}" if not pd.isna(sharpe_ratio) else "N/A")
                st.info(analisar_sharpe_ratio(sharpe_ratio))
            with col_vol_2:
                st.metric("Sortino Ratio", f"{sortino_ratio:.2f}" if not pd.isna(sortino_ratio) else "N/A")
                st.info(analisar_sortino_ratio(sortino_ratio))

            col_vol_3, col_vol_4 = st.columns(2)
            with col_vol_3:
                st.metric("Information Ratio", f"{information_ratio:.2f}" if not pd.isna(information_ratio) else "N/A")
                st.info(analisar_information_ratio(information_ratio))
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
                st.info(analisar_calmar_ratio(calmar_ratio))
            with col_dd_2:
                st.metric("Sterling Ratio", f"{sterling_ratio:.2f}" if not pd.isna(sterling_ratio) else "N/A")
                st.info(analisar_sterling_ratio(sterling_ratio))

            col_dd_3, col_dd_4 = st.columns(2)
            with col_dd_3:
                st.metric("Ulcer Index", f"{ulcer_index:.2f}" if not pd.isna(ulcer_index) else "N/A")
                st.info(analisar_ulcer_index(ulcer_index))
            with col_dd_4:
                st.metric("Martin Ratio", f"{martin_ratio:.2f}" if not pd.isna(martin_ratio) else "N/A")
                st.info(analisar_martin_ratio(martin_ratio))

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
            fig9 = None # Garante que a variável seja None se o gráfico não for gerado

        # GRÁFICO: Consistência em Janelas Móveis
        st.subheader("Consistência em Janelas Móveis")

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
                fig_consistency = None # Garante que a variável seja None se o gráfico não for gerado
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar a Consistência em Janelas Móveis.")
            fig_consistency = None # Garante que a variável seja None se o gráfico não for gerado

# --- Lógica do Botão Gerar Relatório PDF ---
if gerar_relatorio_button and st.session_state.get('dados_carregados', False):
    if PDF_DISPONIVEL:
        with st.spinner("Gerando relatório PDF... Isso pode levar alguns segundos."):
            try:
                pdf_output = gerar_relatorio_pdf(
                    cnpj_fundo=st.session_state.cnpj,
                    nome_fundo=nome_fundo,
                    dt_ini_user=dt_ini_user,
                    dt_fim_user=dt_fim_user,
                    metrics=metrics_display,
                    fig1=fig1, fig2=fig2, fig_excesso_retorno=fig_excesso_retorno, fig3=fig3, fig4=fig4, fig5=fig5,
                    fig6=fig6, fig7=fig7, fig8=fig8, fig9=fig9, fig_consistency=fig_consistency,
                    tem_cdi=tem_cdi, logo_base64=logo_base64,
                    df_plot_cagr=df_plot_cagr, df_plot_var=df_plot_var, df_monthly=df_monthly,
                    df_returns=df_returns, df_consistency=df_consistency,
                    sharpe_ratio=sharpe_ratio, sortino_ratio=sortino_ratio, information_ratio=information_ratio,
                    calmar_ratio=calmar_ratio, sterling_ratio=sterling_ratio, ulcer_index=ulcer_index, martin_ratio=martin_ratio,
                    VaR_95=VaR_95, VaR_99=VaR_99, ES_95=ES_95, ES_99=ES_99,
                    metrics_values=metrics_values
                )
                if pdf_output:
                    st.session_state.pdf_gerado_data = pdf_output
                    st.session_state.pdf_file_name = f"Relatorio_Fundo_{st.session_state.cnpj}_{dt_ini_user.strftime('%Y%m%d')}_{dt_fim_user.strftime('%Y%m%d')}.pdf"
                    st.success("✅ Relatório PDF gerado com sucesso! Clique no botão abaixo para fazer o download.")
                else:
                    st.error("❌ Falha ao gerar o relatório PDF.")
            except Exception as e:
                st.error(f"❌ Erro ao gerar o relatório PDF: {e}")
    else:
        st.error("❌ As bibliotecas 'fpdf2' e 'Pillow' são necessárias para gerar o PDF. Por favor, instale-as.")

# Botão de download só aparece se o PDF foi gerado
if st.session_state.pdf_gerado_data:
    st.download_button(
        label="Download Relatório PDF",
        data=st.session_state.pdf_gerado_data,
        file_name=st.session_state.pdf_file_name,
        mime="application/pdf"
    )


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
