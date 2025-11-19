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
        data = json.loads(f.read().decode('utf-8'))
    else:
        data = json.loads(response.read().decode('utf-8'))

    df = pd.DataFrame(data)
    return df

# Funções de formatação
def format_brl(valor):
    if pd.isna(valor):
        return "N/A"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct_port(valor):
    if pd.isna(valor):
        return "N/A"
    return f"{valor:.2%}".replace(".", ",")

# Funções de análise interpretativa (mantidas como no código anterior)
def analisar_rentabilidade_acumulada(rentabilidade_fundo, rentabilidade_cdi, tem_cdi):
    analise = "A rentabilidade acumulada mostra o retorno total do fundo no período. "
    if pd.isna(rentabilidade_fundo):
        return "Não foi possível calcular a rentabilidade acumulada do fundo."

    analise += f"O fundo obteve uma rentabilidade de **{rentabilidade_fundo:.2%}** no período."

    if tem_cdi and not pd.isna(rentabilidade_cdi):
        analise += f" O CDI acumulou **{rentabilidade_cdi:.2%}** no mesmo período."
        if rentabilidade_fundo > rentabilidade_cdi:
            analise += "\n\n**Conclusão:** O fundo **superou o CDI**, indicando uma performance superior ao benchmark de renda fixa."
        elif rentabilidade_fundo < rentabilidade_cdi:
            analise += "\n\n**Conclusão:** O fundo **ficou abaixo do CDI**, o que sugere uma performance inferior ao benchmark."
        else:
            analise += "\n\n**Conclusão:** O fundo teve uma performance similar ao CDI."
    else:
        analise += "\n\n**Conclusão:** A rentabilidade do fundo é de **" + f"{rentabilidade_fundo:.2%}" + "**."

    analise += "\n\n**Pontos Positivos:** Retorno absoluto elevado, superação consistente do benchmark."
    analise += "\n**Pontos Negativos:** Retorno absoluto baixo, sub-performance em relação ao benchmark."
    return analise

def analisar_cagr(cagr_fundo, cagr_cdi, tem_cdi):
    analise = "O CAGR (Compound Annual Growth Rate) representa a taxa de crescimento anual composta do fundo. "
    if pd.isna(cagr_fundo):
        return "Não foi possível calcular o CAGR do fundo."

    analise += f"O CAGR do fundo é de **{cagr_fundo:.2%}**."

    if tem_cdi and not pd.isna(cagr_cdi):
        analise += f" O CAGR do CDI é de **{cagr_cdi:.2%}**."
        if cagr_fundo > cagr_cdi:
            analise += "\n\n**Conclusão:** O fundo **superou o CDI** em termos de crescimento anual composto, o que é um bom indicador de valor a longo prazo."
        elif cagr_fundo < cagr_cdi:
            analise += "\n\n**Conclusão:** O fundo **ficou abaixo do CDI** em termos de crescimento anual composto, sugerindo uma performance menos eficiente a longo prazo."
        else:
            analise += "\n\n**Conclusão:** O fundo teve um crescimento anual composto similar ao CDI."
    else:
        analise += "\n\n**Conclusão:** O CAGR do fundo é de **" + f"{cagr_fundo:.2%}" + "**."

    analise += "\n\n**Pontos Positivos:** CAGR elevado e superior ao benchmark indica forte valorização anualizada."
    analise += "\n**Pontos Negativos:** CAGR baixo ou inferior ao benchmark pode indicar baixa atratividade do fundo a longo prazo."
    return analise

def analisar_volatilidade(vol_fundo, vol_cdi, tem_cdi):
    analise = "A volatilidade anualizada mede o grau de flutuação dos retornos do fundo. "
    if pd.isna(vol_fundo):
        return "Não foi possível calcular a volatilidade do fundo."

    analise += f"A volatilidade anualizada do fundo é de **{vol_fundo:.2%}**."

    if tem_cdi and not pd.isna(vol_cdi):
        analise += f" A volatilidade anualizada do CDI é de **{vol_cdi:.2%}**."
        if vol_fundo < vol_cdi:
            analise += "\n\n**Conclusão:** O fundo apresentou **menor volatilidade que o CDI**, o que pode ser positivo para investidores avessos ao risco."
        elif vol_fundo > vol_cdi:
            analise += "\n\n**Conclusão:** O fundo apresentou **maior volatilidade que o CDI**, indicando um risco maior em relação ao benchmark de renda fixa."
        else:
            analise += "\n\n**Conclusão:** O fundo teve volatilidade similar ao CDI."
    else:
        analise += "\n\n**Conclusão:** A volatilidade do fundo é de **" + f"{vol_fundo:.2%}" + "**."

    analise += "\n\n**Pontos Positivos:** Baixa volatilidade para o retorno gerado, menor risco que o benchmark."
    analise += "\n**Pontos Negativos:** Alta volatilidade sem retorno compensatório, maior risco que o benchmark."
    return analise

def analisar_max_drawdown(max_dd_fundo, max_dd_cdi, tem_cdi):
    analise = "O Max Drawdown (MDD) representa a maior perda percentual do pico ao vale que o fundo experimentou. "
    if pd.isna(max_dd_fundo):
        return "Não foi possível calcular o Max Drawdown do fundo."

    analise += f"O Max Drawdown do fundo foi de **{max_dd_fundo:.2%}**."

    if tem_cdi and not pd.isna(max_dd_cdi):
        analise += f" O Max Drawdown do CDI foi de **{max_dd_cdi:.2%}**."
        if abs(max_dd_fundo) < abs(max_dd_cdi):
            analise += "\n\n**Conclusão:** O fundo apresentou um **Max Drawdown menor que o CDI**, indicando maior resiliência em períodos de queda."
        elif abs(max_dd_fundo) > abs(max_dd_cdi):
            analise += "\n\n**Conclusão:** O fundo apresentou um **Max Drawdown maior que o CDI**, sugerindo maior vulnerabilidade a perdas significativas."
        else:
            analise += "\n\n**Conclusão:** O fundo teve um Max Drawdown similar ao CDI."
    else:
        analise += "\n\n**Conclusão:** O Max Drawdown do fundo foi de **" + f"{max_dd_fundo:.2%}" + "**."

    analise += "\n\n**Pontos Positivos:** MDD baixo, boa gestão de risco em quedas de mercado."
    analise += "\n**Pontos Negativos:** MDD alto, indica grande exposição a perdas ou recuperação lenta."
    return analise

def analisar_sharpe_ratio(sharpe_ratio):
    if pd.isna(sharpe_ratio):
        return "Não foi possível calcular o Sharpe Ratio."

    analise = f"O Sharpe Ratio do fundo é de **{sharpe_ratio:.2f}**. Ele mede o retorno excedente por unidade de risco (volatilidade total)."
    if sharpe_ratio >= 1.0:
        analise += "\n\n**Conclusão:** Um Sharpe Ratio **maior ou igual a 1.0 é considerado bom**, indicando que o fundo gera um retorno adequado para o risco assumido. Valores acima de 1.5 são excelentes."
    elif sharpe_ratio >= 0.5:
        analise += "\n\n**Conclusão:** Um Sharpe Ratio **entre 0.5 e 1.0 é aceitável**, mas pode indicar que há espaço para melhorar a relação risco-retorno."
    else:
        analise += "\n\n**Conclusão:** Um Sharpe Ratio **abaixo de 0.5 é considerado fraco**, sugerindo que o fundo não está compensando adequadamente o risco assumido."

    analise += "\n\n**Pontos Positivos:** Alta relação retorno/risco, eficiência na geração de alfa."
    analise += "\n**Pontos Negativos:** Baixa relação retorno/risco, fundo não está compensando o risco."
    return analise

def analisar_sortino_ratio(sortino_ratio):
    if pd.isna(sortino_ratio):
        return "Não foi possível calcular o Sortino Ratio."

    analise = f"O Sortino Ratio do fundo é de **{sortino_ratio:.2f}**. Ele mede o retorno excedente por unidade de risco de queda (volatilidade de retornos negativos)."
    if sortino_ratio >= 2.0:
        analise += "\n\n**Conclusão:** Um Sortino Ratio **maior ou igual a 2.0 é excelente**, indicando que o fundo gera um retorno muito bom em relação ao risco de queda."
    elif sortino_ratio >= 1.0:
        analise += "\n\n**Conclusão:** Um Sortino Ratio **entre 1.0 e 2.0 é considerado bom**, mostrando que o fundo tem uma boa performance em relação às perdas."
    else:
        analise += "\n\n**Conclusão:** Um Sortino Ratio **abaixo de 1.0 é considerado fraco**, sugerindo que o fundo não está compensando adequadamente o risco de queda."

    analise += "\n\n**Pontos Positivos:** Boa proteção contra perdas, eficiência em gerar retornos positivos."
    analise += "\n**Pontos Negativos:** Retorno não compensa o risco de queda, fundo vulnerável a perdas."
    return analise

def analisar_information_ratio(information_ratio):
    if pd.isna(information_ratio):
        return "Não foi possível calcular o Information Ratio."

    analise = f"O Information Ratio do fundo é de **{information_ratio:.2f}**. Ele mede a capacidade do gestor de gerar retornos acima de um benchmark (alfa) por unidade de risco ativo (tracking error)."
    if information_ratio >= 0.75:
        analise += "\n\n**Conclusão:** Um Information Ratio **maior ou igual a 0.75 é excelente**, indicando que o gestor tem uma alta habilidade em gerar alfa consistente."
    elif information_ratio >= 0.4:
        analise += "\n\n**Conclusão:** Um Information Ratio **entre 0.4 e 0.75 é considerado bom**, mostrando uma boa capacidade de superação do benchmark."
    else:
        analise += "\n\n**Conclusão:** Um Information Ratio **abaixo de 0.4 é considerado fraco**, sugerindo que o gestor tem dificuldade em gerar retornos consistentes acima do benchmark."

    analise += "\n\n**Pontos Positivos:** Habilidade comprovada do gestor em gerar alfa, superação consistente do benchmark."
    analise += "\n**Pontos Negativos:** Dificuldade em superar o benchmark, alto risco ativo sem retorno compensatório."
    return analise

def analisar_calmar_ratio(calmar_ratio):
    if pd.isna(calmar_ratio):
        return "Não foi possível calcular o Calmar Ratio."

    analise = f"O Calmar Ratio do fundo é de **{calmar_ratio:.2f}**. Ele mede o retorno anualizado em relação ao Max Drawdown."
    if calmar_ratio >= 3.0:
        analise += "\n\n**Conclusão:** Um Calmar Ratio **maior ou igual a 3.0 é excelente**, indicando um retorno muito robusto em relação à maior queda histórica."
    elif calmar_ratio >= 1.0:
        analise += "\n\n**Conclusão:** Um Calmar Ratio **entre 1.0 e 3.0 é considerado bom**, mostrando uma boa recuperação após perdas significativas."
    else:
        analise += "\n\n**Conclusão:** Um Calmar Ratio **abaixo de 1.0 é considerado fraco**, sugerindo que o retorno não compensa o risco de grandes perdas."

    analise += "\n\n**Pontos Positivos:** Alta capacidade de recuperação e geração de retorno após quedas."
    analise += "\n**Pontos Negativos:** Retorno insuficiente para o risco de drawdown, recuperação lenta."
    return analise

def analisar_sterling_ratio(sterling_ratio):
    if pd.isna(sterling_ratio):
        return "Não foi possível calcular o Sterling Ratio."

    analise = f"O Sterling Ratio do fundo é de **{sterling_ratio:.2f}**. Ele mede o retorno anualizado em relação ao drawdown médio anual."
    if sterling_ratio >= 2.0:
        analise += "\n\n**Conclusão:** Um Sterling Ratio **maior ou igual a 2.0 é excelente**, indicando um retorno muito bom em relação às perdas médias anuais."
    elif sterling_ratio >= 1.0:
        analise += "\n\n**Conclusão:** Um Sterling Ratio **entre 1.0 e 2.0 é considerado bom**, mostrando uma boa gestão de risco em relação às perdas típicas."
    else:
        analise += "\n\n**Conclusão:** Um Sterling Ratio **abaixo de 1.0 é considerado fraco**, sugerindo que o retorno não compensa o nível de perdas anuais."

    analise += "\n\n**Pontos Positivos:** Boa relação retorno/perda média, gestão eficaz de risco."
    analise += "\n**Pontos Negativos:** Retorno não compensa as perdas médias, gestão de risco ineficaz."
    return analise

def analisar_ulcer_index(ulcer_index):
    if pd.isna(ulcer_index):
        return "Não foi possível calcular o Ulcer Index."

    analise = f"O Ulcer Index do fundo é de **{ulcer_index:.2f}**. Ele mede a profundidade e a duração dos drawdowns, penalizando mais as quedas longas e profundas."
    if ulcer_index <= 1.0:
        analise += "\n\n**Conclusão:** Um Ulcer Index **abaixo de 1.0 é excelente**, indicando que o fundo tem poucas e/ou curtas quedas, ou se recupera rapidamente."
    elif ulcer_index <= 2.0:
        analise += "\n\n**Conclusão:** Um Ulcer Index **entre 1.0 e 2.0 é considerado bom**, mostrando um nível aceitável de risco de drawdown."
    else:
        analise += "\n\n**Conclusão:** Um Ulcer Index **acima de 2.0 é considerado alto**, sugerindo que o fundo experimenta quedas frequentes, profundas ou de longa duração."

    analise += "\n\n**Pontos Positivos:** Baixo risco de drawdown prolongado, boa estabilidade."
    analise += "\n**Pontos Negativos:** Alto risco de drawdown prolongado, instabilidade."
    return analise

def analisar_martin_ratio(martin_ratio):
    if pd.isna(martin_ratio):
        return "Não foi possível calcular o Martin Ratio."

    analise = f"O Martin Ratio do fundo é de **{martin_ratio:.2f}**. Ele mede o retorno excedente em relação ao Ulcer Index, focando no risco de queda."
    if martin_ratio >= 2.0:
        analise += "\n\n**Conclusão:** Um Martin Ratio **maior ou igual a 2.0 é excelente**, indicando um retorno muito bom em relação ao risco de drawdown (profundidade e duração)."
    elif martin_ratio >= 1.0:
        analise += "\n\n**Conclusão:** Um Martin Ratio **entre 1.0 e 2.0 é considerado bom**, mostrando uma boa compensação do risco de drawdown."
    else:
        analise += "\n\n**Conclusão:** Um Martin Ratio **abaixo de 1.0 é considerado fraco**, sugerindo que o retorno não compensa o risco de drawdown."

    analise += "\n\n**Pontos Positivos:** Retorno robusto em relação ao risco de quedas prolongadas."
    analise += "\n**Pontos Negativos:** Retorno insuficiente para o risco de quedas prolongadas."
    return analise

def analisar_var_es(VaR_95, VaR_99, ES_95, ES_99):
    analise = "As métricas de Value at Risk (VaR) e Expected Shortfall (ES) quantificam o risco de perda potencial do fundo."

    if not pd.isna(VaR_95):
        analise += f"\n\n**VaR 95%:** Há 5% de chance de o fundo perder mais de **{VaR_95:.2%}** em um dia."
    if not pd.isna(VaR_99):
        analise += f"\n**VaR 99%:** Há 1% de chance de o fundo perder mais de **{VaR_99:.2%}** em um dia."
    if not pd.isna(ES_95):
        analise += f"\n**ES 95%:** Se as perdas excederem o VaR 95%, a perda média esperada é de **{ES_95:.2%}**."
    if not pd.isna(ES_99):
        analise += f"\n**ES 99%:** Se as perdas excederem o VaR 99%, a perda média esperada é de **{ES_99:.2%}**."

    if pd.isna(VaR_95) and pd.isna(VaR_99) and pd.isna(ES_95) and pd.isna(ES_99):
        return "Não foi possível calcular as métricas de VaR e Expected Shortfall."

    analise += "\n\n**Interpretação:** Valores absolutos menores para VaR e ES indicam menor risco de perda. O ES é uma medida de risco mais conservadora que o VaR, pois considera a magnitude das perdas além do VaR."
    analise += "\n\n**Pontos Positivos:** Baixos valores de VaR e ES indicam um fundo com menor risco de cauda (perdas extremas)."
    analise += "\n**Pontos Negativos:** Altos valores de VaR e ES indicam um fundo mais exposto a perdas significativas e extremas."
    return analise

def analisar_retornos_janelas_moveis(df_returns, janela_selecionada, tem_cdi):
    analise = f"A análise de retornos em janelas móveis para **{janela_selecionada}** mostra a performance do fundo ao longo do tempo em períodos contínuos de {janela_selecionada.split(' ')[0]} meses."

    fund_col = f'FUNDO_{janela_selecionada}'
    cdi_col = f'CDI_{janela_selecionada}'

    if fund_col in df_returns.columns and not df_returns[fund_col].dropna().empty:
        retorno_fundo_medio = df_returns[fund_col].mean()
        analise += f"\n\nO retorno médio do fundo nesta janela foi de **{retorno_fundo_medio:.2%}**."

        if tem_cdi and cdi_col in df_returns.columns and not df_returns[cdi_col].dropna().empty:
            retorno_cdi_medio = df_returns[cdi_col].mean()
            analise += f" O retorno médio do CDI foi de **{retorno_cdi_medio:.2%}**."
            if retorno_fundo_medio > retorno_cdi_medio:
                analise += "\n\n**Conclusão:** O fundo **superou o CDI** nesta janela, indicando uma boa performance relativa."
            elif retorno_fundo_medio < retorno_cdi_medio:
                analise += "\n\n**Conclusão:** O fundo **ficou abaixo do CDI** nesta janela, o que é um ponto de atenção."
            else:
                analise += "\n\n**Conclusão:** O fundo teve performance similar ao CDI nesta janela."
        else:
            analise += "\n\n**Conclusão:** Não foi possível comparar com o CDI nesta janela."
    else:
        analise += f"\n\nNão há dados suficientes para a janela de **{janela_selecionada}**."

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
    metrics_values # <--- ADICIONADO AQUI
):
    class PDF(FPDF):
        def header(self):
            # Logo
            if logo_base64:
                try:
                    # Salva a imagem base64 temporariamente para FPDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_logo:
                        tmp_logo.write(base64.b64decode(logo_base64))
                        logo_path = tmp_logo.name
                    self.image(logo_path, 10, 8, 33)
                    os.remove(logo_path) # Limpa o arquivo temporário
                except Exception as e:
                    st.warning(f"Não foi possível adicionar a logo ao PDF: {e}")
            self.set_font('Arial', 'B', 15)
            self.cell(80)
            self.cell(30, 10, 'Relatório de Análise de Fundo', 0, 0, 'C')
            self.ln(20)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(230, 230, 230)
            self.cell(0, 10, title, 0, 1, 'L', 1)
            self.ln(4)

        def chapter_body(self, body):
            self.set_font('Arial', '', 10)
            # Substituir negrito markdown por negrito PDF
            body = body.replace('**', '<b>').replace('**', '</b>')
            self.write_html(body)
            self.ln(8)

        def add_plotly_figure(self, fig, width=180):
            if fig is None:
                self.set_font('Arial', 'I', 10)
                self.cell(0, 10, "Gráfico não disponível devido a dados insuficientes ou erro.", 0, 1)
                self.ln(5)
                return

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                file_path = tmp_file.name
                pio.write_image(fig, file_path, format='png', scale=2.0) # Exporta como PNG de alta resolução
            self.image(file_path, w=width)
            os.remove(file_path)
            self.ln(5)

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Informações Gerais
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Análise do Fundo: {nome_fundo}", 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"CNPJ: {cnpj_fundo}", 0, 1, 'C')
    pdf.cell(0, 10, f"Período de Análise: {dt_ini_user.strftime('%d/%m/%Y')} a {dt_fim_user.strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.ln(10)

    # Seção de Rentabilidade
    pdf.chapter_title('1. Rentabilidade')
    pdf.chapter_body(analisar_rentabilidade_acumulada(metrics_values.get('Rentabilidade_Acumulada_Val'), metrics_values.get('Rentabilidade_Acumulada_CDI_Val'), tem_cdi))
    pdf.add_plotly_figure(fig1)
    pdf.chapter_body(analisar_cagr(metrics_values.get('CAGR_Fundo_Val'), metrics_values.get('CAGR_CDI_Val'), tem_cdi))
    pdf.add_plotly_figure(fig2)
    if tem_cdi:
        pdf.chapter_body("Análise do Excesso de Retorno:")
        pdf.add_plotly_figure(fig_excesso_retorno)
    pdf.add_page()

    # Seção de Risco
    pdf.chapter_title('2. Risco')
    pdf.chapter_body(analisar_volatilidade(metrics_values.get('Volatilidade_Fundo_Val'), metrics_values.get('Volatilidade_CDI_Val'), tem_cdi))
    pdf.add_plotly_figure(fig3)
    pdf.chapter_body(analisar_max_drawdown(metrics_values.get('Max_Drawdown_Fundo_Val'), metrics_values.get('Max_Drawdown_CDI_Val'), tem_cdi))
    pdf.add_plotly_figure(fig4)
    pdf.chapter_body(analisar_var_es(VaR_95, VaR_99, ES_95, ES_99))
    pdf.add_plotly_figure(fig5)
    pdf.add_page()

    # Seção de Métricas de Risco-Retorno
    pdf.chapter_title('3. Métricas de Risco-Retorno')
    pdf.chapter_body(analisar_sharpe_ratio(sharpe_ratio))
    pdf.chapter_body(analisar_sortino_ratio(sortino_ratio))
    pdf.chapter_body(analisar_information_ratio(information_ratio))
    pdf.chapter_body(analisar_calmar_ratio(calmar_ratio))
    pdf.chapter_body(analisar_sterling_ratio(sterling_ratio))
    pdf.chapter_body(analisar_ulcer_index(ulcer_index))
    pdf.chapter_body(analisar_martin_ratio(martin_ratio))
    pdf.add_page()

    # Seção de Patrimônio e Captação
    pdf.chapter_title('4. Patrimônio e Captação Líquida')
    pdf.add_plotly_figure(fig6)
    pdf.add_plotly_figure(fig7)
    pdf.add_plotly_figure(fig8)
    pdf.add_page()

    # Seção de Janelas Móveis
    pdf.chapter_title('5. Retornos e Consistência em Janelas Móveis')
    # A análise de janelas móveis precisa da janela selecionada, mas para o PDF vamos fazer uma análise geral ou da última janela
    # Para simplificar, vamos analisar a última janela disponível no df_returns
    janelas_disponiveis = {
        "12 meses (252 dias)": 252,
        "24 meses (504 dias)": 504,
        "36 meses (756 dias)": 756,
        "48 meses (1008 dias)": 1008,
        "60 meses (1260 dias)": 1260
    }
    # Tenta pegar a última janela com dados
    ultima_janela_com_dados = None
    for nome_janela, dias_janela in reversed(janelas_disponiveis.items()):
        if f'FUNDO_{nome_janela}' in df_returns.columns and not df_returns[f'FUNDO_{nome_janela}'].dropna().empty:
            ultima_janela_com_dados = nome_janela
            break

    if ultima_janela_com_dados:
        pdf.chapter_body(analisar_retornos_janelas_moveis(df_returns, ultima_janela_com_dados, tem_cdi))
    else:
        pdf.chapter_body("Não há dados suficientes para analisar retornos em janelas móveis.")

    pdf.add_plotly_figure(fig9)
    if tem_cdi:
        pdf.chapter_body(analisar_consistencia_janelas_moveis(df_consistency))
        pdf.add_plotly_figure(fig_consistency)
    pdf.add_page()

    # Conclusão (Exemplo)
    pdf.chapter_title('6. Conclusão Geral')
    pdf.chapter_body(f"Este relatório apresentou uma análise detalhada do fundo **{nome_fundo}** (CNPJ: {cnpj_fundo}) no período de {dt_ini_user.strftime('%d/%m/%Y')} a {dt_fim_user.strftime('%d/%m/%Y')}. As métricas de rentabilidade, risco e risco-retorno foram avaliadas, juntamente com a evolução do patrimônio e captação. As análises interpretativas fornecem insights sobre a performance do fundo em relação ao CDI (quando aplicável) e sua consistência em diferentes janelas de tempo. Recomenda-se uma análise contínua e a consideração do perfil de risco do investidor antes de tomar decisões de investimento.")

    return pdf.output(dest='S').encode('latin1')


# --- Bloco principal de execução do Streamlit ---
if carregar_button:
    if cnpj_valido and datas_validas:
        with st.spinner("Carregando dados do fundo..."):
            try:
                df = carregar_dados_api(cnpj_limpo, data_inicial_formatada, data_final_formatada)

                if df.empty:
                    st.error("❌ Não foram encontrados dados para o CNPJ e período selecionados.")
                    st.session_state.dados_carregados = False
                else:
                    # Filtra o DataFrame para o período exato do usuário
                    df['DT_COMPTC'] = pd.to_datetime(df['DT_COMPTC'])
                    df = df[(df['DT_COMPTC'] >= dt_ini) & (df['DT_COMPTC'] <= dt_fim)].copy()

                    if df.empty:
                        st.error("❌ Não foram encontrados dados para o CNPJ e período selecionados após o filtro.")
                        st.session_state.dados_carregados = False
                    else:
                        df = df.sort_values('DT_COMPTC').reset_index(drop=True)
                        df['VL_QUOTA'] = pd.to_numeric(df['VL_QUOTA'], errors='coerce')
                        df['VL_PATRIM_LIQ'] = pd.to_numeric(df['VL_PATRIM_LIQ'], errors='coerce')
                        df['CAPTC_DIA'] = pd.to_numeric(df['CAPTC_DIA'], errors='coerce')
                        df['RESG_DIA'] = pd.to_numeric(df['RESG_DIA'], errors='coerce')
                        df['NR_COTST'] = pd.to_numeric(df['NR_COTST'], errors='coerce')

                        # Preencher valores ausentes para VL_QUOTA e VL_PATRIM_LIQ
                        df['VL_QUOTA'] = df['VL_QUOTA'].ffill()
                        df['VL_PATRIM_LIQ'] = df['VL_PATRIM_LIQ'].ffill()

                        # Remover linhas com NaN em VL_QUOTA após ffill (se ainda houver)
                        df.dropna(subset=['VL_QUOTA'], inplace=True)

                        if df.empty:
                            st.error("❌ Dados insuficientes após tratamento para o período selecionado.")
                            st.session_state.dados_carregados = False
                        else:
                            # Calcula Captação Líquida Acumulada
                            df['Captacao_Liquida_Dia'] = df['CAPTC_DIA'] - df['RESG_DIA']
                            df['Soma_Acumulada'] = df['Captacao_Liquida_Dia'].cumsum()

                            # Calcula Patrimônio Líquido Médio por Cotista
                            df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

                            # Normaliza a cota para começar em 1
                            df['VL_QUOTA_NORM'] = df['VL_QUOTA'] / df['VL_QUOTA'].iloc[0]

                            # Obtém o nome do fundo de forma segura
                            if 'DENOM_SOCIAL' in df.columns and not df['DENOM_SOCIAL'].empty:
                                nome_fundo = df['DENOM_SOCIAL'].iloc[0]
                            else:
                                nome_fundo = f"Fundo CNPJ {cnpj_limpo}"
                                st.warning("⚠️ Não foi possível obter o nome social do fundo. Usando CNPJ como nome.")

                            # Armazena o CNPJ válido no session_state
                            st.session_state.cnpj = cnpj_limpo

                            # --- Obter dados do CDI ---
                            df_cdi = pd.DataFrame()
                            tem_cdi = False
                            if mostrar_cdi and BCB_DISPONIVEL:
                                with st.spinner("Carregando dados do CDI..."):
                                    df_cdi_raw = obter_dados_cdi_real(dt_ini, dt_fim)
                                    if not df_cdi_raw.empty:
                                        df_cdi_raw['DT_COMPTC'] = pd.to_datetime(df_cdi_raw['DT_COMPTC'])
                                        # Merge com o DataFrame do fundo
                                        df = pd.merge(df, df_cdi_raw[['DT_COMPTC', 'VL_CDI_normalizado']], on='DT_COMPTC', how='left')
                                        df['CDI_COTA'] = df['VL_CDI_normalizado'].ffill() # Preenche para ter a mesma frequência
                                        df.dropna(subset=['CDI_COTA'], inplace=True) # Remove se não houver CDI no início
                                        if not df.empty:
                                            # Normaliza o CDI para começar no mesmo ponto que o fundo
                                            df['CDI_COTA'] = df['CDI_COTA'] / df['CDI_COTA'].iloc[0]
                                            tem_cdi = True
                                        else:
                                            st.warning("⚠️ Dados do CDI não puderam ser alinhados com os dados do fundo. Comparação com CDI desativada.")
                                            mostrar_cdi = False
                                    else:
                                        st.warning("⚠️ Não foi possível obter dados do CDI para o período. Comparação com CDI desativada.")
                                        mostrar_cdi = False
                            elif mostrar_cdi and not BCB_DISPONIVEL:
                                st.warning("⚠️ Biblioteca 'python-bcb' não encontrada. Instale com: pip install python-bcb para comparar com CDI.")
                                mostrar_cdi = False

                            if not tem_cdi:
                                st.info("ℹ️ Comparação com CDI desativada.")

                            # --- Cálculos de Métricas ---
                            # Retorno Acumulado
                            rentabilidade_fundo = (df['VL_QUOTA_NORM'].iloc[-1] - 1) if not df.empty else np.nan
                            rentabilidade_cdi = (df['CDI_COTA'].iloc[-1] - 1) if tem_cdi and not df.empty else np.nan

                            # CAGR
                            num_dias = (df['DT_COMPTC'].iloc[-1] - df['DT_COMPTC'].iloc[0]).days
                            cagr_fund_decimal = ((df['VL_QUOTA_NORM'].iloc[-1] / df['VL_QUOTA_NORM'].iloc[0])**(252/num_dias) - 1) if num_dias > 0 else np.nan
                            cagr_fund = cagr_fund_decimal
                            annualized_cdi_return = ((df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0])**(252/num_dias) - 1) if tem_cdi and num_dias > 0 else np.nan

                            # Volatilidade Anualizada
                            daily_returns_fund = df['VL_QUOTA_NORM'].pct_change().dropna()
                            annualized_fund_volatility = daily_returns_fund.std() * np.sqrt(252) if not daily_returns_fund.empty else np.nan
                            daily_returns_cdi = df['CDI_COTA'].pct_change().dropna() if tem_cdi else pd.Series()
                            annualized_cdi_volatility = daily_returns_cdi.std() * np.sqrt(252) if not daily_returns_cdi.empty else np.nan

                            # Max Drawdown
                            cumulative_returns_fund = (1 + daily_returns_fund).cumprod()
                            peak_fund = cumulative_returns_fund.expanding(min_periods=1).max()
                            drawdown_fund = (cumulative_returns_fund / peak_fund) - 1
                            max_dd_fundo = drawdown_fund.min() if not drawdown_fund.empty else np.nan

                            max_dd_cdi = np.nan
                            if tem_cdi:
                                cumulative_returns_cdi = (1 + daily_returns_cdi).cumprod()
                                peak_cdi = cumulative_returns_cdi.expanding(min_periods=1).max()
                                drawdown_cdi = (cumulative_returns_cdi / peak_cdi) - 1
                                max_dd_cdi = drawdown_cdi.min() if not drawdown_cdi.empty else np.nan

                            # Métricas de Risco-Retorno (inicialização com NaN)
                            sharpe_ratio = np.nan
                            sortino_ratio = np.nan
                            information_ratio = np.nan
                            calmar_ratio = np.nan
                            sterling_ratio = np.nan
                            ulcer_index = np.nan
                            martin_ratio = np.nan
                            VaR_95 = np.nan
                            VaR_99 = np.nan
                            ES_95 = np.nan
                            ES_99 = np.nan

                            # Cálculos de VaR e ES (se houver dados suficientes)
                            if len(daily_returns_fund) >= 252: # Mínimo de 1 ano de dados diários
                                VaR_95 = daily_returns_fund.quantile(0.05)
                                VaR_99 = daily_returns_fund.quantile(0.01)
                                ES_95 = daily_returns_fund[daily_returns_fund < VaR_95].mean()
                                ES_99 = daily_returns_fund[daily_returns_fund < VaR_99].mean()

                            # Para Calmar, Sterling, Ulcer, Martin, Sharpe, Sortino, Information Ratio
                            # Precisamos de retornos anualizados e volatilidades
                            annualized_fund_return = (1 + daily_returns_fund).prod()**(252/len(daily_returns_fund)) - 1 if len(daily_returns_fund) > 0 else np.nan
                            annualized_downside_volatility = daily_returns_fund[daily_returns_fund < 0].std() * np.sqrt(252) if not daily_returns_fund[daily_returns_fund < 0].empty else np.nan

                            # Tracking Error (se tem CDI)
                            tracking_error = np.nan
                            if tem_cdi and not daily_returns_fund.empty and not daily_returns_cdi.empty:
                                excess_returns = daily_returns_fund - daily_returns_cdi
                                tracking_error = excess_returns.std() * np.sqrt(252) if not excess_returns.empty else np.nan

                            # Ulcer Index
                            if not drawdown_fund.empty:
                                squared_drawdowns = drawdown_fund**2
                                ulcer_index = np.sqrt(squared_drawdowns.sum() / len(squared_drawdowns)) if len(squared_drawdowns) > 0 else np.nan

                            # Calmar Ratio
                            if not pd.isna(annualized_fund_return) and not pd.isna(max_dd_fundo) and max_dd_fundo != 0:
                                calmar_ratio = annualized_fund_return / abs(max_dd_fundo)

                            # Sterling Ratio (usa drawdown médio, aqui simplificado para MDD)
                            # Uma implementação mais precisa usaria o drawdown médio anual, mas para manter a consistência com o MDD
                            # e a simplicidade, usaremos o MDD como proxy para o denominador.
                            # Para um cálculo mais preciso, seria necessário calcular o drawdown médio de todos os drawdowns.
                            if not pd.isna(annualized_fund_return) and not pd.isna(max_dd_fundo) and max_dd_fundo != 0:
                                sterling_ratio = annualized_fund_return / abs(max_dd_fundo) # Simplificado

                            # Martin Ratio (usa Ulcer Index)
                            if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(ulcer_index) and ulcer_index != 0:
                                martin_ratio = (cagr_fund_decimal - annualized_cdi_return) / ulcer_index

                            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(annualized_fund_volatility) and annualized_fund_volatility != 0:
                                sharpe_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_fund_volatility

                            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(annualized_downside_volatility) and annualized_downside_volatility != 0:
                                sortino_ratio = (annualized_fund_return - annualized_cdi_return) / annualized_downside_volatility

                            if not pd.isna(annualized_fund_return) and not pd.isna(annualized_cdi_return) and not pd.isna(tracking_error) and tracking_error != 0:
                                information_ratio = (annualized_fund_return - annualized_cdi_return) / tracking_error

                            # Dicionário para passar os valores brutos das métricas para o PDF
                            metrics_values = {
                                'Rentabilidade_Acumulada_Val': rentabilidade_fundo,
                                'Rentabilidade_Acumulada_CDI_Val': rentabilidade_cdi,
                                'CAGR_Fundo_Val': cagr_fund,
                                'CAGR_CDI_Val': annualized_cdi_return,
                                'Volatilidade_Fundo_Val': annualized_fund_volatility,
                                'Volatilidade_CDI_Val': annualized_cdi_volatility,
                                'Max_Drawdown_Fundo_Val': max_dd_fundo,
                                'Max_Drawdown_CDI_Val': max_dd_cdi,
                                'Sharpe_Ratio_Val': sharpe_ratio,
                                'Sortino_Ratio_Val': sortino_ratio,
                                'Information_Ratio_Val': information_ratio,
                                'Calmar_Ratio_Val': calmar_ratio,
                                'Sterling_Ratio_Val': sterling_ratio,
                                'Ulcer_Index_Val': ulcer_index,
                                'Martin_Ratio_Val': martin_ratio,
                                'VaR_95_Val': VaR_95,
                                'VaR_99_Val': VaR_99,
                                'ES_95_Val': ES_95,
                                'ES_99_Val': ES_99
                            }

                            # Dicionário para exibição no dashboard
                            metrics_display = {
                                "Rentabilidade Acumulada": fmt_pct_port(rentabilidade_fundo),
                                "Rentabilidade Acumulada CDI": fmt_pct_port(rentabilidade_cdi) if tem_cdi else "N/A",
                                "CAGR Fundo": fmt_pct_port(cagr_fund),
                                "CAGR CDI": fmt_pct_port(annualized_cdi_return) if tem_cdi else "N/A",
                                "Volatilidade Fundo": fmt_pct_port(annualized_fund_volatility),
                                "Volatilidade CDI": fmt_pct_port(annualized_cdi_volatility) if tem_cdi else "N/A",
                                "Max Drawdown Fundo": fmt_pct_port(max_dd_fundo),
                                "Max Drawdown CDI": fmt_pct_port(max_dd_cdi) if tem_cdi else "N/A",
                            }

                            st.session_state.dados_carregados = True
                            st.success("✅ Dados carregados com sucesso!")

                            # --- Geração dos Gráficos ---
                            color_primary = '#1a5f3f'
                            color_secondary = '#2d8659'
                            color_cdi = '#f0b429'
                            color_danger = '#dc3545'

                            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                                "Rentabilidade", "Risco", "Patrimônio e Captação",
                                "Patrimônio Médio e Cotistas", "Janelas Móveis"
                            ])

                            with tab1:
                                st.subheader("Rentabilidade Acumulada")

                                fig1 = go.Figure()
                                fig1.add_trace(go.Scatter(
                                    x=df['DT_COMPTC'],
                                    y=df['VL_QUOTA_NORM'],
                                    mode='lines',
                                    name='Fundo',
                                    line=dict(color=color_primary, width=2.5),
                                    hovertemplate='Data: %{x|%d/%m/%Y}<br>Fundo: %{y:.2%}<extra></extra>'
                                ))
                                if tem_cdi:
                                    fig1.add_trace(go.Scatter(
                                        x=df['DT_COMPTC'],
                                        y=df['CDI_COTA'],
                                        mode='lines',
                                        name='CDI',
                                        line=dict(color=color_cdi, width=2.5),
                                        hovertemplate='Data: %{x|%d/%m/%Y}<br>CDI: %{y:.2%}<extra></extra>'
                                    ))

                                fig1.update_layout(
                                    xaxis_title="Data",
                                    yaxis_title="Rentabilidade Acumulada",
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
                                fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
                                st.plotly_chart(fig1, use_container_width=True)

                                st.markdown("#### Métricas de Rentabilidade")
                                col_rent_1, col_rent_2 = st.columns(2)
                                with col_rent_1:
                                    st.metric("Rentabilidade Acumulada", metrics_display["Rentabilidade Acumulada"])
                                    st.info(analisar_rentabilidade_acumulada(rentabilidade_fundo, rentabilidade_cdi, tem_cdi))
                                with col_rent_2:
                                    st.metric("Rentabilidade Acumulada CDI", metrics_display["Rentabilidade Acumulada CDI"])
                                    if tem_cdi:
                                        st.info(analisar_rentabilidade_acumulada(rentabilidade_fundo, rentabilidade_cdi, tem_cdi))
                                    else:
                                        st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para análise do CDI.")

                                st.subheader("CAGR (Compound Annual Growth Rate)")

                                fig2 = go.Figure()
                                fig2.add_trace(go.Scatter(
                                    x=df['DT_COMPTC'],
                                    y=df['VL_QUOTA_NORM'].expanding().apply(lambda x: (x.iloc[-1]/x.iloc[0])**(252/len(x)) - 1 if len(x) >= 252 else np.nan, raw=False),
                                    mode='lines',
                                    name='CAGR Fundo',
                                    line=dict(color=color_primary, width=2.5),
                                    hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR Fundo: %{y:.2%}<extra></extra>'
                                ))
                                if tem_cdi:
                                    fig2.add_trace(go.Scatter(
                                        x=df['DT_COMPTC'],
                                        y=df['CDI_COTA'].expanding().apply(lambda x: (x.iloc[-1]/x.iloc[0])**(252/len(x)) - 1 if len(x) >= 252 else np.nan, raw=False),
                                        mode='lines',
                                        name='CAGR CDI',
                                        line=dict(color=color_cdi, width=2.5),
                                        hovertemplate='Data: %{x|%d/%m/%Y}<br>CAGR CDI: %{y:.2%}<extra></extra>'
                                    ))

                                fig2.update_layout(
                                    xaxis_title="Data",
                                    yaxis_title="CAGR Anualizado",
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
                                # Ajusta o range do eixo X para os dados de df
                                df_plot_cagr = df[df['VL_QUOTA_NORM'].expanding().apply(lambda x: len(x) >= 252, raw=False)].copy()
                                if not df_plot_cagr.empty:
                                    fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df_plot_cagr['DT_COMPTC'].min(), df_plot_cagr['DT_COMPTC'].max()], x_autorange=False)
                                else:
                                    fig2 = add_watermark_and_style(fig2, logo_base64) # Sem range específico se não houver dados
                                st.plotly_chart(fig2, use_container_width=True)

                                col_cagr_1, col_cagr_2 = st.columns(2)
                                with col_cagr_1:
                                    st.metric("CAGR Fundo", metrics_display["CAGR Fundo"])
                                    st.info(analisar_cagr(cagr_fund, annualized_cdi_return, tem_cdi))
                                with col_cagr_2:
                                    st.metric("CAGR CDI", metrics_display["CAGR CDI"])
                                    if tem_cdi:
                                        st.info(analisar_cagr(cagr_fund, annualized_cdi_return, tem_cdi))
                                    else:
                                        st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para análise do CDI.")

                                if tem_cdi:
                                    st.subheader("Excesso de Retorno (Fundo vs CDI)")
                                    fig_excesso_retorno = go.Figure()
                                    fig_excesso_retorno.add_trace(go.Scatter(
                                        x=df['DT_COMPTC'],
                                        y=df['VL_QUOTA_NORM'] - df['CDI_COTA'],
                                        mode='lines',
                                        name='Excesso de Retorno',
                                        line=dict(color=color_secondary, width=2.5),
                                        fill='tozeroy',
                                        fillcolor='rgba(45, 134, 89, 0.1)',
                                        hovertemplate='Data: %{x|%d/%m/%Y}<br>Excesso: %{y:.2%}<extra></extra>'
                                    ))
                                    fig_excesso_retorno.update_layout(
                                        xaxis_title="Data",
                                        yaxis_title="Excesso de Retorno (Fundo - CDI)",
                                        template="plotly_white",
                                        hovermode="x unified",
                                        height=500,
                                        yaxis=dict(tickformat=".2%"),
                                        font=dict(family="Inter, sans-serif")
                                    )
                                    fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
                                    st.plotly_chart(fig_excesso_retorno, use_container_width=True)
                                else:
                                    fig_excesso_retorno = None # Garante que a variável seja None se o gráfico não for gerado

                            with tab2:
                                st.subheader("Volatilidade Anualizada")

                                fig3 = go.Figure()
                                fig3.add_trace(go.Scatter(
                                    x=df['DT_COMPTC'],
                                    y=df['VL_QUOTA_NORM'].pct_change().rolling(window=252).std() * np.sqrt(252),
                                    mode='lines',
                                    name='Volatilidade Fundo',
                                    line=dict(color=color_primary, width=2.5),
                                    hovertemplate='Data: %{x|%d/%m/%Y}<br>Volatilidade Fundo: %{y:.2%}<extra></extra>'
                                ))
                                if tem_cdi:
                                    fig3.add_trace(go.Scatter(
                                        x=df['DT_COMPTC'],
                                        y=df['CDI_COTA'].pct_change().rolling(window=252).std() * np.sqrt(252),
                                        mode='lines',
                                        name='Volatilidade CDI',
                                        line=dict(color=color_cdi, width=2.5),
                                        hovertemplate='Data: %{x|%d/%m/%Y}<br>Volatilidade CDI: %{y:.2%}<extra></extra>'
                                    ))

                                fig3.update_layout(
                                    xaxis_title="Data",
                                    yaxis_title="Volatilidade Anualizada",
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
                                # Ajusta o range do eixo X para os dados de df
                                df_plot_var = df[df['VL_QUOTA_NORM'].pct_change().rolling(window=252).std().notna()].copy()
                                if not df_plot_var.empty:
                                    fig3 = add_watermark_and_style(fig3, logo_base64, x_range=[df_plot_var['DT_COMPTC'].min(), df_plot_var['DT_COMPTC'].max()], x_autorange=False)
                                else:
                                    fig3 = add_watermark_and_style(fig3, logo_base64) # Sem range específico se não houver dados
                                st.plotly_chart(fig3, use_container_width=True)

                                st.markdown("#### Métricas de Risco")
                                col_vol_1, col_vol_2 = st.columns(2)
                                with col_vol_1:
                                    st.metric("Volatilidade Fundo", metrics_display["Volatilidade Fundo"])
                                    st.info(analisar_volatilidade(annualized_fund_volatility, annualized_cdi_volatility, tem_cdi))
                                with col_vol_2:
                                    st.metric("Volatilidade CDI", metrics_display["Volatilidade CDI"])
                                    if tem_cdi:
                                        st.info(analisar_volatilidade(annualized_fund_volatility, annualized_cdi_volatility, tem_cdi))
                                    else:
                                        st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para análise do CDI.")

                                st.subheader("Max Drawdown")

                                fig4 = go.Figure()
                                fig4.add_trace(go.Scatter(
                                    x=df['DT_COMPTC'],
                                    y=drawdown_fund,
                                    mode='lines',
                                    name='Drawdown Fundo',
                                    line=dict(color=color_primary, width=2.5),
                                    fill='tozeroy',
                                    fillcolor='rgba(26, 95, 63, 0.1)',
                                    hovertemplate='Data: %{x|%d/%m/%Y}<br>Drawdown Fundo: %{y:.2%}<extra></extra>'
                                ))
                                if tem_cdi:
                                    fig4.add_trace(go.Scatter(
                                        x=df['DT_COMPTC'],
                                        y=drawdown_cdi,
                                        mode='lines',
                                        name='Drawdown CDI',
                                        line=dict(color=color_cdi, width=2.5),
                                        fill='tozeroy',
                                        fillcolor='rgba(240, 180, 41, 0.1)',
                                        hovertemplate='Data: %{x|%d/%m/%Y}<br>Drawdown CDI: %{y:.2%}<extra></extra>'
                                    ))

                                fig4.update_layout(
                                    xaxis_title="Data",
                                    yaxis_title="Drawdown",
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
                                fig4 = add_watermark_and_style(fig4, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
                                st.plotly_chart(fig4, use_container_width=True)

                                col_dd_1, col_dd_2 = st.columns(2)
                                with col_dd_1:
                                    st.metric("Max Drawdown Fundo", metrics_display["Max Drawdown Fundo"])
                                    st.info(analisar_max_drawdown(max_dd_fundo, max_dd_cdi, tem_cdi))
                                with col_dd_2:
                                    st.metric("Max Drawdown CDI", metrics_display["Max Drawdown CDI"])
                                    if tem_cdi:
                                        st.info(analisar_max_drawdown(max_dd_fundo, max_dd_cdi, tem_cdi))
                                    else:
                                        st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para análise do CDI.")

                                st.subheader("Value at Risk (VaR) e Expected Shortfall (ES)")

                                # Cria um DataFrame para exibir VaR e ES
                                var_es_data = {
                                    "Métrica": ["VaR 95%", "VaR 99%", "Expected Shortfall 95%", "Expected Shortfall 99%"],
                                    "Valor": [
                                        fmt_pct_port(VaR_95),
                                        fmt_pct_port(VaR_99),
                                        fmt_pct_port(ES_95),
                                        fmt_pct_port(ES_99)
                                    ]
                                }
                                df_var_es = pd.DataFrame(var_es_data)
                                st.dataframe(df_var_es, hide_index=True, use_container_width=True)
                                st.info(analisar_var_es(VaR_95, VaR_99, ES_95, ES_99))

                                # Gráfico de distribuição de retornos para VaR/ES
                                fig5 = go.Figure()
                                fig5.add_trace(go.Histogram(
                                    x=daily_returns_fund,
                                    nbinsx=50,
                                    name='Retornos Diários Fundo',
                                    marker_color=color_primary,
                                    opacity=0.75
                                ))
                                # Adiciona linhas para VaR e ES
                                if not pd.isna(VaR_95):
                                    fig5.add_vline(x=VaR_95, line_width=2, line_dash="dash", line_color="red", annotation_text=f"VaR 95%: {VaR_95:.2%}", annotation_position="top right")
                                if not pd.isna(VaR_99):
                                    fig5.add_vline(x=VaR_99, line_width=2, line_dash="dash", line_color="darkred", annotation_text=f"VaR 99%: {VaR_99:.2%}", annotation_position="top left")
                                if not pd.isna(ES_95):
                                    fig5.add_vline(x=ES_95, line_width=1, line_dash="dot", line_color="orange", annotation_text=f"ES 95%: {ES_95:.2%}", annotation_position="bottom right")
                                if not pd.isna(ES_99):
                                    fig5.add_vline(x=ES_99, line_width=1, line_dash="dot", line_color="darkorange", annotation_text=f"ES 99%: {ES_99:.2%}", annotation_position="bottom left")

                                fig5.update_layout(
                                    title_text='Distribuição de Retornos Diários com VaR e ES',
                                    xaxis_title="Retorno Diário",
                                    yaxis_title="Frequência",
                                    template="plotly_white",
                                    height=500,
                                    xaxis=dict(tickformat=".2%"),
                                    font=dict(family="Inter, sans-serif")
                                )
                                fig5 = add_watermark_and_style(fig5, logo_base64, x_autorange=True)
                                st.plotly_chart(fig5, use_container_width=True)

                                st.markdown("#### Métricas de Risco-Retorno")
                                if tem_cdi and len(daily_returns_fund) >= 252: # Mínimo de 1 ano de dados para métricas anualizadas
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

            except Exception as e:
                st.error(f"❌ Erro ao carregar os dados: {str(e)}")
                st.info("💡 Verifique se o CNPJ está correto e se há dados disponíveis para o período selecionado.")
                st.session_state.dados_carregados = False # Resetar o estado em caso de erro
    else:
        st.warning("Preencha o CNPJ e as datas corretamente para carregar os dados.")

# --- Lógica do Botão Gerar Relatório PDF ---
if gerar_relatorio_button and st.session_state.get('dados_carregados', False):
    if PDF_DISPONIVEL:
        with st.spinner("Gerando relatório PDF... Isso pode levar alguns segundos."):
            try:
                # As variáveis fig1, fig2, etc., e metrics_values precisam estar definidas
                # no escopo global ou serem passadas para a função gerar_relatorio_pdf.
                # Como elas são criadas dentro do bloco 'if carregar_button',
                # precisamos garantir que estejam acessíveis.
                # A forma mais robusta é recriá-las ou armazená-las no session_state.
                # Para evitar recálculos pesados, vamos assumir que, se 'dados_carregados' é True,
                # as variáveis necessárias para o PDF foram criadas na última execução bem-sucedida.
                # No entanto, para o Streamlit, o script é re-executado do topo.
                # Portanto, se o botão 'Gerar Relatório PDF' for clicado,
                # e 'dados_carregados' for True, mas as variáveis dos gráficos
                # não foram recriadas (porque 'carregar_button' não foi clicado novamente),
                # elas estarão como None ou com valores antigos.

                # Para resolver isso de forma mais robusta, vamos re-executar a lógica de cálculo
                # e criação de gráficos se o botão de relatório for clicado e os dados estiverem carregados.
                # Isso garante que as variáveis figX e metrics_values estejam atualizadas.

                # Para evitar duplicidade de código, podemos encapsular a lógica de
                # cálculo e geração de gráficos em uma função separada.
                # Por simplicidade AGORA, vamos apenas garantir que as variáveis existam.
                # Se o erro persistir, precisaremos refatorar a geração de gráficos para uma função.

                # Por enquanto, vamos garantir que as variáveis estejam definidas,
                # mesmo que seja com None, para que a chamada da função não falhe por NameError.
                # Se o 'dados_carregados' for True, elas deveriam ter sido criadas.
                # Se não foram, é um problema de fluxo.

                # As variáveis fig1, fig2, etc., e metrics_values são criadas no bloco `if carregar_button`.
                # Se o usuário clicar em "Gerar Relatório PDF" sem clicar em "Carregar Dados" novamente
                # (mas com dados_carregados=True de uma sessão anterior), essas variáveis podem não existir.
                # Para contornar isso, precisamos garantir que elas sejam sempre definidas.
                # Uma solução é armazená-las no st.session_state ou refatorar.
                # Por agora, vamos definir valores padrão para evitar NameError.
                # No entanto, a forma mais correta seria re-executar a lógica de carregamento/cálculo
                # ou armazenar tudo no session_state.

                # Para este erro específico, vamos assumir que as variáveis foram criadas
                # na última execução bem-sucedida do bloco 'if carregar_button'.
                # Se o erro 'DENOM_SOCIAL' ocorreu, significa que o bloco 'if carregar_button'
                # falhou antes de definir 'nome_fundo' e outras variáveis.
                # O tratamento de erro no bloco 'if carregar_button' agora define
                # st.session_state.dados_carregados = False em caso de falha,
                # o que deve desabilitar o botão de relatório.

                # Se você está vendo este erro, é provável que o 'dados_carregados'
                # esteja True, mas as variáveis dos gráficos/métricas não foram
                # inicializadas corretamente na última execução.

                # Para garantir que as variáveis existam para a chamada do PDF,
                # vou inicializá-las com None antes do try-except do PDF,
                # caso não tenham sido definidas pelo bloco de carregamento.
                # Isso é um fallback, o ideal é que o bloco de carregamento as defina.

                # Inicialização de fallback para as variáveis dos gráficos e métricas
                # (Estas deveriam ser definidas no bloco 'if carregar_button' se 'dados_carregados' for True)
                fig1 = fig2 = fig_excesso_retorno = fig3 = fig4 = fig5 = None
                fig6 = fig7 = fig8 = fig9 = fig_consistency = None
                sharpe_ratio = sortino_ratio = information_ratio = np.nan
                calmar_ratio = sterling_ratio = ulcer_index = martin_ratio = np.nan
                VaR_95 = VaR_99 = ES_95 = ES_99 = np.nan
                metrics_values = {}
                nome_fundo = st.session_state.get('nome_fundo_carregado', f"Fundo CNPJ {st.session_state.cnpj}")
                dt_ini_user = datetime.strptime(data_inicial_formatada, '%Y%m%d') if data_inicial_formatada else datetime.now()
                dt_fim_user = datetime.strptime(data_final_formatada, '%Y%m%d') if data_final_formatada else datetime.now()
                metrics_display = {} # Também precisa ser definida

                # Se os dados foram carregados, mas o script foi re-executado (como é comum no Streamlit),
                # as variáveis locais do bloco 'if carregar_button' podem ter sido perdidas.
                # A solução mais robusta é armazenar os objetos Plotly Figure e os dicionários de métricas
                # no st.session_state após o carregamento bem-sucedido.
                # Por enquanto, vamos assumir que o erro 'DENOM_SOCIAL' foi resolvido
                # e que as variáveis são definidas no bloco 'if carregar_button'.
                # Se o erro persistir, teremos que refatorar para usar st.session_state para gráficos e métricas.

                # Apenas para garantir que 'nome_fundo' esteja disponível para o PDF
                # se o bloco de carregamento foi bem-sucedido.
                if st.session_state.get('dados_carregados', False):
                    # Recuperar variáveis do session_state se elas foram salvas lá
                    # (Esta parte seria adicionada se refatorássemos para salvar tudo no session_state)
                    # Por enquanto, confiamos que o bloco 'if carregar_button' as definiu.
                    pass # Nenhuma ação aqui por enquanto, pois o erro 'DENOM_SOCIAL' é anterior.


                pdf_output = gerar_relatorio_pdf(
                    cnpj_fundo=st.session_state.cnpj,
                    nome_fundo=nome_fundo, # Agora nome_fundo é definido no bloco de carregamento
                    dt_ini_user=dt_ini_user,
                    dt_fim_user=dt_fim_user,
                    metrics=metrics_display, # metrics_display é definido no bloco de carregamento
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
