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
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False
    st.warning("⚠️ Bibliotecas 'fpdf2' e/ou 'Pillow' não encontradas. Instale com: pip install fpdf2 Pillow")

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
    value="",
    placeholder="00.000.000/0000-00",
    help="Digite o CNPJ com ou sem formatação"
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

# Título principal
title_col, report_button_col = st.columns([0.7, 0.3])
with title_col:
    st.markdown("<h1>Dashboard de Fundos de Investimentos</h1>", unsafe_allow_html=True)
with report_button_col:
    st.markdown("<div style='height: 4.5rem;'></div>", unsafe_allow_html=True) # Espaçamento para alinhar
    gerar_relatorio_button = st.button("Gerar Relatório PDF 📄", disabled=not st.session_state.get('dados_carregados', False))

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
        analise += "Este é um **Max Drawdown moderado**, o que é comum para fundos com exposição a ativos de maior risco. É um **ponto de atenção** que deve ser avaliado em conjunto com a rentabilidade."
        analise += "\n\n**Pontos Positivos:** O fundo pode estar assumindo um risco calculado para buscar retornos maiores."
        analise += "\n**Pontos Negativos:** Necessidade de avaliar se o retorno compensou o risco de queda."
    else: # Quedas maiores que 15%
        analise += "Este é um **Max Drawdown elevado**, indicando que o fundo experimentou uma queda significativa em seu valor. É um **ponto de atenção** importante que sugere maior risco de perdas para o investidor."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Alta exposição a perdas, o que pode ser preocupante para investidores com menor tolerância ao risco."
    return analise

def analisar_volatilidade_historica(vol_hist):
    if pd.isna(vol_hist):
        return "Não foi possível calcular a Volatilidade Histórica."

    analise = f"A Volatilidade Histórica anualizada do fundo é de {fmt_pct_port(vol_hist/100)}. "

    if vol_hist < 5.0:
        analise += "Esta é uma **volatilidade muito baixa**, indicando que o fundo é bastante estável e com poucas oscilações de preço. É um **ponto positivo** para investidores conservadores."
        analise += "\n\n**Pontos Positivos:** Estabilidade e previsibilidade, menor risco de grandes oscilações."
        analise += "\n**Pontos Negativos:** Pode indicar menor potencial de retorno em comparação com ativos mais voláteis."
    elif vol_hist < 15.0:
        analise += "Esta é uma **volatilidade moderada**, comum para fundos com exposição a ativos de renda variável com gestão mais conservadora. É um **ponto neutro** que deve ser avaliado em relação ao retorno."
        analise += "\n\n**Pontos Positivos:** Equilíbrio entre risco e potencial de retorno."
        analise += "\n**Pontos Negativos:** O fundo pode ter oscilações que exigem alguma tolerância ao risco."
    else:
        analise += "Esta é uma **volatilidade elevada**, indicando que o fundo apresenta grandes oscilações de preço. É um **ponto de atenção** para investidores que buscam maior estabilidade, mas pode ser esperado para fundos com estratégias mais agressivas."
        analise += "\n\n**Pontos Positivos:** Potencial de retornos mais altos em períodos de alta."
        analise += "\n**Pontos Negativos:** Maior risco de perdas e maior imprevisibilidade nos retornos."
    return analise

def analisar_sharpe_ratio(sharpe_ratio):
    if pd.isna(sharpe_ratio):
        return "Não foi possível calcular o Sharpe Ratio."

    analise = f"O Sharpe Ratio do fundo é de {sharpe_ratio:.2f}. "

    if sharpe_ratio >= 3.0:
        analise += "Este é um resultado **excepcional**, indicando que o fundo tem gerado retornos muito consistentes e ajustados ao risco, superando significativamente o CDI."
        analise += "\n\n**Pontos Positivos:** Performance robusta e alta eficiência na geração de retorno por unidade de risco."
        analise += "\n**Pontos Negativos:** Manter um Sharpe tão alto pode ser desafiador em períodos de alta volatilidade de mercado."
    elif sharpe_ratio >= 2.0:
        analise += "Este é um resultado **muito bom**, mostrando que o fundo tem um excelente retorno ajustado ao risco em relação ao CDI."
        analise += "\n\n**Pontos Positivos:** Forte capacidade de gerar retornos superiores ao risco assumido."
        analise += "\n**Pontos Negativos:** Necessidade de monitoramento contínuo para garantir a manutenção dessa performance."
    elif sharpe_ratio >= 1.0:
        analise += "Este é um **bom resultado**, indicando que o fundo gera um bom retorno para o nível de risco assumido, superando o CDI de forma satisfatória."
        analise += "\n\n**Pontos Positivos:** O fundo compensa bem o risco que assume."
        analise += "\n**Pontos Negativos:** Pode haver oportunidades para otimizar ainda mais a relação risco-retorno."
    elif sharpe_ratio >= 0.0:
        analise += "O Sharpe Ratio é **positivo, mas abaixo de 1.0**, sugerindo que o retorno do fundo, embora superior ao CDI, não compensa de forma ideal o risco total assumido."
        analise += "\n\n**Pontos Positivos:** O fundo ainda supera o CDI."
        analise += "\n**Pontos Negativos:** A eficiência na geração de retorno por unidade de risco pode ser melhorada."
    else: # sharpe_ratio < 0.0
        analise += "O Sharpe Ratio é **negativo**, indicando que o fundo não conseguiu gerar um retorno superior ao CDI que justificasse o risco assumido, ou até mesmo teve um retorno inferior ao CDI."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está compensando o risco, sugerindo uma performance subótima em relação ao benchmark."

    return analise

def analisar_sortino_ratio(sortino_ratio):
    if pd.isna(sortino_ratio):
        return "Não foi possível calcular o Sortino Ratio."

    analise = f"O Sortino Ratio do fundo é de {sortino_ratio:.2f}. "

    if sortino_ratio >= 2.0:
        analise += "Este é um resultado **excepcional**, indicando que o fundo tem gerado retornos muito consistentes e ajustados ao risco de queda, com excelente proteção contra perdas."
        analise += "\n\n**Pontos Positivos:** Alta eficiência na geração de retorno por unidade de risco de queda, excelente gestão de perdas."
        analise += "\n**Pontos Negativos:** N/A."
    elif sortino_ratio >= 1.0:
        analise += "Este é um **bom resultado**, mostrando que o fundo tem um bom retorno ajustado ao risco de queda, superando o CDI de forma satisfatória considerando apenas as perdas."
        analise += "\n\n**Pontos Positivos:** O fundo compensa bem o risco de queda que assume."
        analise += "\n**Pontos Negativos:** Pode haver oportunidades para otimizar ainda mais a relação risco-retorno de queda."
    elif sortino_ratio >= 0.0:
        analise += "O Sortino Ratio é **positivo, mas abaixo de 1.0**, sugerindo que o retorno do fundo, embora superior ao CDI, não compensa de forma ideal o risco de queda."
        analise += "\n\n**Pontos Positivos:** O fundo ainda supera o CDI."
        analise += "\n**Pontos Negativos:** A eficiência na geração de retorno por unidade de risco de queda pode ser melhorada."
    else: # sortino_ratio < 0.0
        analise += "O Sortino Ratio é **negativo**, indicando que o fundo não conseguiu gerar um retorno superior ao CDI que justificasse o risco de queda assumido, ou até mesmo teve um retorno inferior ao CDI."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está compensando o risco de queda, sugerindo uma performance subótima em relação ao benchmark."
    return analise

def analisar_information_ratio(information_ratio):
    if pd.isna(information_ratio):
        return "Não foi possível calcular o Information Ratio."

    analise = f"O Information Ratio do fundo é de {information_ratio:.2f}. "

    if information_ratio >= 1.0:
        analise += "Este é um resultado **excelente**, indicando que o gestor tem uma forte habilidade e consistência em superar o benchmark (CDI) com um risco de desvio razoável."
        analise += "\n\n**Pontos Positivos:** Forte capacidade de gerar alfa e gerenciar o risco relativo ao benchmark."
        analise += "\n**Pontos Negativos:** N/A."
    elif information_ratio >= 0.5:
        analise += "Este é um **bom resultado**, mostrando que o gestor tem uma boa habilidade e consistência em superar o benchmark (CDI)."
        analise += "\n\n**Pontos Positivos:** Habilidade consistente em superar o benchmark."
        analise += "\n**Pontos Negativos:** Pode haver oportunidades para otimizar ainda mais a superação do benchmark."
    elif information_ratio >= 0.0:
        analise += "O Information Ratio é **positivo, mas abaixo de 0.5**, sugerindo uma habilidade modesta em superar o benchmark (CDI)."
        analise += "\n\n**Pontos Positivos:** O fundo ainda supera o CDI."
        analise += "\n**Pontos Negativos:** A capacidade de gerar alfa pode ser melhorada."
    else: # information_ratio < 0.0
        analise += "O Information Ratio é **negativo**, indicando que o fundo está consistentemente abaixo do benchmark (CDI), o que é um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está superando o benchmark, sugerindo uma performance subótima em relação ao benchmark."
    return analise

def analisar_calmar_ratio(calmar_ratio):
    if pd.isna(calmar_ratio):
        return "Não foi possível calcular o Calmar Ratio."

    analise = f"O Calmar Ratio do fundo é de {calmar_ratio:.2f}. "

    if calmar_ratio >= 1.0:
        analise += "Este é um resultado **muito bom**, indicando que o fundo gerou bons retornos anuais em relação ao seu maior drawdown. O fundo gerencia bem o risco de grandes quedas."
        analise += "\n\n**Pontos Positivos:** Excelente retorno ajustado ao risco de drawdown, boa resiliência a quedas."
        analise += "\n**Pontos Negativos:** N/A."
    elif calmar_ratio >= 0.5:
        analise += "Este é um **bom resultado**, mostrando que o fundo gerou retornos razoáveis em relação ao seu maior drawdown."
        analise += "\n\n**Pontos Positivos:** O fundo consegue se recuperar de quedas de forma satisfatória."
        analise += "\n**Pontos Negativos:** Pode haver oportunidades para otimizar a relação retorno/drawdown."
    elif calmar_ratio >= 0.0:
        analise += "O Calmar Ratio é **positivo, mas abaixo de 0.5**, sugerindo que o retorno do fundo, embora positivo, não compensa de forma ideal o risco de grandes quedas."
        analise += "\n\n**Pontos Positivos:** O fundo ainda gera retorno positivo."
        analise += "\n**Pontos Negativos:** O risco de drawdown pode ser elevado em relação ao retorno gerado."
    else: # calmar_ratio < 0.0
        analise += "O Calmar Ratio é **negativo**, indicando que o fundo teve retorno negativo ou um drawdown muito grande, o que é um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está compensando o risco de drawdown, sugerindo uma performance subótima."
    return analise

def analisar_sterling_ratio(sterling_ratio):
    if pd.isna(sterling_ratio):
        return "Não foi possível calcular o Sterling Ratio."

    analise = f"O Sterling Ratio do fundo é de {sterling_ratio:.2f}. "

    if sterling_ratio >= 1.0:
        analise += "Este é um resultado **muito bom**, indicando que o fundo gerou bons retornos anuais em relação ao seu maior drawdown. O fundo gerencia bem o risco de grandes quedas."
        analise += "\n\n**Pontos Positivos:** Excelente retorno ajustado ao risco de drawdown, boa resiliência a quedas."
        analise += "\n**Pontos Negativos:** N/A."
    elif sterling_ratio >= 0.5:
        analise += "Este é um **bom resultado**, mostrando que o fundo gerou retornos razoáveis em relação ao seu maior drawdown."
        analise += "\n\n**Pontos Positivos:** O fundo consegue se recuperar de quedas de forma satisfatória."
        analise += "\n**Pontos Negativos:** Pode haver oportunidades para otimizar a relação retorno/drawdown."
    elif sterling_ratio >= 0.0:
        analise += "O Sterling Ratio é **positivo, mas abaixo de 0.5**, sugerindo que o retorno do fundo, embora positivo, não compensa de forma ideal o risco de grandes quedas."
        analise += "\n\n**Pontos Positivos:** O fundo ainda gera retorno positivo."
        analise += "\n**Pontos Negativos:** O risco de drawdown pode ser elevado em relação ao retorno gerado."
    else: # sterling_ratio < 0.0
        analise += "O Sterling Ratio é **negativo**, indicando que o fundo teve retorno negativo ou um drawdown muito grande, o que é um **ponto de atenção**."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está compensando o risco de drawdown, sugerindo uma performance subótima."
    return analise

def analisar_ulcer_index(ulcer_index):
    if pd.isna(ulcer_index):
        return "Não foi possível calcular o Ulcer Index."

    analise = f"O Ulcer Index do fundo é de {ulcer_index:.2f}. "

    if ulcer_index < 1.0:
        analise += "Este é um **Ulcer Index baixo**, indicando que o fundo teve quedas menos profundas e/ou de menor duração. É um **ponto positivo** para a estabilidade e conforto do investidor."
        analise += "\n\n**Pontos Positivos:** Baixa 'dor' para o investidor, boa gestão de risco de drawdown."
        analise += "\n**Pontos Negativos:** N/A."
    elif ulcer_index < 2.0:
        analise += "Este é um **Ulcer Index moderado**, sugerindo que o fundo teve quedas de profundidade e/ou duração razoáveis. É um **ponto neutro** que deve ser avaliado em relação ao retorno."
        analise += "\n\n**Pontos Positivos:** O fundo pode estar assumindo um risco calculado para buscar retornos maiores."
        analise += "\n**Pontos Negativos:** O fundo pode ter períodos de quedas que exigem tolerância ao risco."
    else: # ulcer_index >= 2.0
        analise += "Este é um **Ulcer Index elevado**, indicando que o fundo teve quedas significativas e/ou duradouras. É um **ponto de atenção** importante que sugere maior risco de perdas e desconforto para o investidor."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Alta 'dor' para o investidor, sugerindo maior risco de perdas e volatilidade de baixa."
    return analise

def analisar_martin_ratio(martin_ratio):
    if pd.isna(martin_ratio):
        return "Não foi possível calcular o Martin Ratio."

    analise = f"O Martin Ratio do fundo é de {martin_ratio:.2f}. "

    if martin_ratio >= 1.0:
        analise += "Este é um resultado **muito bom**, indicando que o fundo entrega um bom retorno considerando a 'dor' dos drawdowns (Ulcer Index). O fundo é eficiente em gerar retorno em relação ao risco de perdas."
        analise += "\n\n**Pontos Positivos:** Excelente retorno ajustado ao risco de drawdown, boa eficiência na gestão de perdas."
        analise += "\n**Pontos Negativos:** N/A."
    elif martin_ratio >= 0.5:
        analise += "Este é um **bom resultado**, mostrando que o fundo gera um retorno razoável em relação à 'dor' dos drawdowns."
        analise += "\n\n**Pontos Positivos:** O fundo consegue gerar retorno positivo considerando as quedas."
        analise += "\n**Pontos Negativos:** Pode haver oportunidades para otimizar a relação retorno/Ulcer Index."
    elif martin_ratio >= 0.0:
        analise += "O Martin Ratio é **positivo, mas abaixo de 0.5**, sugerindo que o retorno do fundo, embora positivo, não compensa de forma ideal a 'dor' dos drawdowns."
        analise += "\n\n**Pontos Positivos:** O fundo ainda gera retorno positivo."
        analise += "\n**Pontos Negativos:** O risco de drawdown pode ser elevado em relação ao retorno gerado."
    else: # martin_ratio < 0.0
        analise += "O Martin Ratio é **negativo**, indicando que o fundo não conseguiu gerar um retorno superior ao CDI que justificasse a 'dor' dos drawdowns, ou até mesmo teve um retorno inferior ao CDI."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** O fundo não está compensando o risco de drawdown, sugerindo uma performance subótima."
    return analise

def analisar_var_es(VaR_95, VaR_99, ES_95, ES_99):
    if pd.isna(VaR_95) or pd.isna(VaR_99) or pd.isna(ES_95) or pd.isna(ES_99):
        return "Não foi possível calcular VaR e ES devido à falta de dados."

    analise = f"""
    **Análise de Risco de Cauda (VaR e ES) para 1 mês:**

    • Há **99%** de confiança de que o fundo não cairá mais do que **{fmt_pct_port(VaR_99)} (VaR 99%)** em um mês. Caso essa queda ocorra, a perda média esperada será de **{fmt_pct_port(ES_99)} (ES 99%)**.
    • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(VaR_95)} (VaR 95%)** em um mês. Caso essa queda ocorra, a perda média esperada será de **{fmt_pct_port(ES_95)} (ES 95%)**.

    **Pontos Positivos:**
    *   Fornece uma estimativa quantitativa das perdas potenciais em cenários adversos, auxiliando na gestão de risco.
    *   O Expected Shortfall (ES) oferece uma visão mais completa do risco de cauda, indicando a perda média esperada em cenários extremos.

    **Pontos Negativos:**
    *   VaR e ES são estimativas baseadas em dados históricos e podem não prever eventos de "cisne negro" ou mudanças abruptas no mercado.
    *   A interpretação deve ser feita com cautela, pois não garantem que as perdas não excederão esses valores.
    """
    return analise

def analisar_patrimonio_captacao(patrimonio_liq, captacao_liquida_acum):
    analise = f"O Patrimônio Líquido atual do fundo é de {format_brl(patrimonio_liq)} e a Captação Líquida acumulada no período é de {format_brl(captacao_liquida_acum)}. "

    if captacao_liquida_acum > 0:
        analise += "A **captação líquida positiva** indica que o fundo tem atraído mais recursos do que resgatado, o que é um **ponto positivo** para o crescimento e a sustentabilidade do fundo."
        analise += "\n\n**Pontos Positivos:** Crescimento da base de ativos, confiança dos investidores, potencial para maiores economias de escala."
        analise += "\n**Pontos Negativos:** N/A."
    elif captacao_liquida_acum < 0:
        analise += "A **captação líquida negativa** indica que o fundo tem sofrido mais resgates do que novas aplicações, o que é um **ponto de atenção** para a gestão e a estabilidade do fundo."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Redução da base de ativos, possível perda de confiança dos investidores, desafios na gestão de liquidez."
    else:
        analise += "A captação líquida é neutra, sugerindo um equilíbrio entre aplicações e resgates no período."
        analise += "\n\n**Pontos Positivos:** Estabilidade na base de ativos."
        analise += "\n**Pontos Negativos:** Não há crescimento orgânico claro."
    return analise

def analisar_captacao_mensal(df_monthly):
    if df_monthly.empty:
        return "Não há dados suficientes para analisar a Captação Líquida Mensal."

    total_captacao = df_monthly['Captacao_Liquida'].sum()
    num_meses = len(df_monthly)
    meses_positivos = (df_monthly['Captacao_Liquida'] > 0).sum()
    meses_negativos = (df_monthly['Captacao_Liquida'] < 0).sum()

    analise = f"No período analisado ({num_meses} meses), o fundo teve uma captação líquida total de {format_brl(total_captacao)}. "
    analise += f"Houve {meses_positivos} meses de captação positiva e {meses_negativos} meses de captação negativa. "

    if meses_positivos > meses_negativos:
        analise += "A **predominância de meses com captação positiva** é um **ponto positivo**, indicando uma tendência de crescimento e atratividade do fundo para novos investidores."
        analise += "\n\n**Pontos Positivos:** Crescimento sustentado, boa percepção do mercado sobre o fundo."
        analise += "\n**Pontos Negativos:** N/A."
    elif meses_negativos > meses_positivos:
        analise += "A **predominância de meses com captação negativa** é um **ponto de atenção**, sugerindo uma possível perda de interesse ou confiança dos investidores no fundo."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Desafios na manutenção da base de ativos, possível impacto na liquidez."
    else:
        analise += "A captação mensal tem sido equilibrada, com um número similar de meses positivos e negativos."
        analise += "\n\n**Pontos Positivos:** Estabilidade na captação."
        analise += "\n**Pontos Negativos:** Ausência de uma tendência clara de crescimento ou retração."
    return analise

def analisar_cotistas(patrimonio_medio, num_cotistas):
    if pd.isna(patrimonio_medio) or pd.isna(num_cotistas):
        return "Não há dados suficientes para analisar o Patrimônio Médio e o Número de Cotistas."

    analise = f"O Patrimônio Médio por Cotista é de {format_brl(patrimonio_medio)} e o Número de Cotistas atual é de {int(num_cotistas)}. "

    if num_cotistas > 1000: # Exemplo de limiar para um fundo grande
        analise += "Um **alto número de cotistas** é um **ponto positivo**, indicando que o fundo é bem distribuído e acessível a um grande público, o que pode trazer maior estabilidade ao patrimônio."
        analise += "\n\n**Pontos Positivos:** Ampla aceitação no mercado, menor concentração de risco em poucos investidores."
        analise += "\n**Pontos Negativos:** N/A."
    elif num_cotistas > 100:
        analise += "Um **número moderado de cotistas** é um **ponto neutro**, comum para fundos de nicho ou em fase de crescimento."
        analise += "\n\n**Pontos Positivos:** Potencial de crescimento da base de cotistas."
        analise += "\n**Pontos Negativos:** Pode haver maior sensibilidade a grandes resgates de poucos cotistas."
    else:
        analise += "Um **baixo número de cotistas** é um **ponto de atenção**, sugerindo que o fundo pode ser mais concentrado e sensível a resgates de poucos investidores."
        analise += "\n\n**Pontos Positivos:** N/A."
        analise += "\n**Pontos Negativos:** Maior risco de liquidez e volatilidade do patrimônio líquido devido à concentração."
    return analise

def analisar_consistencia(df_consistency):
    if df_consistency.empty:
        return "Não há dados suficientes para analisar a Consistência em Janelas Móveis."

    analise = "A consistência do fundo em superar o CDI em diferentes janelas móveis é um indicador importante da sua performance relativa. "

    for index, row in df_consistency.iterrows():
        janela = row['Janela']
        consistencia = row['Consistencia']
        analise += f"\n\nNa janela de **{janela} meses**, o fundo superou o CDI em **{consistencia:.2f}%** do tempo. "
        if consistencia >= 70:
            analise += "Isso demonstra uma **alta consistência**, um **ponto positivo** forte."
        elif consistencia >= 50:
            analise += "Isso indica uma **consistência moderada**, um **ponto neutro**."
        else:
            analise += "Isso sugere uma **baixa consistência**, um **ponto de atenção**."

    analise += "\n\n**Pontos Positivos:** Alta consistência em janelas maiores indica uma estratégia robusta e capacidade de gerar alfa no longo prazo."
    analise += "\n**Pontos Negativos:** Baixa consistência pode indicar que o fundo tem dificuldade em superar o benchmark de forma consistente, ou que sua estratégia é mais volátil em relação ao CDI."
    return analise

# --- Função de Geração de Relatório PDF ---
def gerar_relatorio_pdf(
    cnpj_fundo, nome_fundo, dt_ini_user, dt_fim_user,
    metrics,
    fig1, fig2, fig_excesso_retorno, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig_consistency,
    tem_cdi, logo_base64,
    df_plot_cagr, df_plot_var, df_monthly, df_returns, df_consistency,
    sharpe_ratio, sortino_ratio, information_ratio, calmar_ratio, sterling_ratio, ulcer_index, martin_ratio,
    VaR_95, VaR_99, ES_95, ES_99
):
    if not PDF_DISPONIVEL:
        st.error("As bibliotecas 'fpdf2' e 'Pillow' não estão instaladas. Não é possível gerar o PDF.")
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título do Relatório
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(26, 95, 63) # Cor primária
    pdf.cell(0, 10, "Relatório de Análise de Fundo de Investimento", 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"Fundo: {nome_fundo} (CNPJ: {cnpj_fundo})", 0, 1, 'C')
    pdf.cell(0, 7, f"Período de Análise: {dt_ini_user.strftime('%d/%m/%Y')} a {dt_fim_user.strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.ln(10)

    # --- Sumário Executivo ---
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(26, 95, 63)
    pdf.cell(0, 10, "1. Sumário Executivo", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, f"""
    Este relatório apresenta uma análise detalhada do fundo {nome_fundo} (CNPJ: {cnpj_fundo}) no período de {dt_ini_user.strftime('%d/%m/%Y')} a {dt_fim_user.strftime('%d/%m/%Y')}.
    Foram avaliadas métricas de rentabilidade, risco, patrimônio, captação e consistência, com comparações ao CDI quando aplicável.

    **Principais Métricas:**
    - Patrimônio Líquido: {metrics['Patrimonio_Liq']}
    - Rentabilidade Acumulada: {metrics['Rentabilidade_Acumulada']}
    - CAGR Médio: {metrics['CAGR_Medio']}
    - Max Drawdown: {metrics['Max_Drawdown']}
    - Volatilidade Histórica: {metrics['Vol_Historica']}
    """, 0, 'L')
    pdf.ln(5)

    # Conclusão geral (a ser aprimorada com base nas análises individuais)
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 6, "Conclusão Geral:", 0, 'L')
    pdf.set_font("Arial", '', 10)

    # Geração da conclusão geral baseada nas análises individuais
    conclusao_geral_texto = ""

    # Rentabilidade
    if metrics['Rentabilidade_Acumulada_Val'] is not None and metrics['CDI_Acumulada_Val'] is not None:
        if metrics['Rentabilidade_Acumulada_Val'] > metrics['CDI_Acumulada_Val']:
            conclusao_geral_texto += "O fundo demonstrou uma **sólida performance de rentabilidade**, superando o CDI no período. "
        elif metrics['Rentabilidade_Acumulada_Val'] < metrics['CDI_Acumulada_Val']:
            conclusao_geral_texto += "A rentabilidade do fundo ficou **abaixo do CDI**, indicando um desempenho não competitivo. "
        else:
            conclusao_geral_texto += "A rentabilidade do fundo foi similar ao CDI. "

    # Risco (Sharpe e Max Drawdown)
    if not pd.isna(sharpe_ratio) and sharpe_ratio >= 1.0:
        conclusao_geral_texto += "Com um **Sharpe Ratio favorável**, o fundo tem sido eficiente em gerar retorno ajustado ao risco. "
    elif not pd.isna(sharpe_ratio) and sharpe_ratio < 0.0:
        conclusao_geral_texto += "O **Sharpe Ratio negativo** sugere que o fundo não compensou o risco assumido. "

    if not pd.isna(metrics['Max_Drawdown_Val']) and metrics['Max_Drawdown_Val'] > -10.0:
        conclusao_geral_texto += "O **Max Drawdown foi contido**, indicando boa gestão de perdas. "
    elif not pd.isna(metrics['Max_Drawdown_Val']) and metrics['Max_Drawdown_Val'] <= -10.0:
        conclusao_geral_texto += "O **Max Drawdown foi significativo**, apontando para períodos de maior volatilidade de baixa. "

    # Captação
    if metrics['Captacao_Liquida_Acum_Val'] is not None:
        if metrics['Captacao_Liquida_Acum_Val'] > 0:
            conclusao_geral_texto += "A **captação líquida positiva** reflete a confiança dos investidores. "
        elif metrics['Captacao_Liquida_Acum_Val'] < 0:
            conclusao_geral_texto += "A **captação líquida negativa** indica desafios na atração/retenção de recursos. "

    if not conclusao_geral_texto:
        conclusao_geral_texto = "Não foi possível gerar uma conclusão geral devido à falta de dados ou métricas insuficientes."

    pdf.multi_cell(0, 6, conclusao_geral_texto, 0, 'L')
    pdf.ln(10)

    # --- Seções Detalhadas ---
    sections = [
        ("2. Rentabilidade Histórica", fig1, "Rentabilidade Acumulada", analisar_rentabilidade_acumulada(metrics['Rentabilidade_Acumulada_Val'], metrics['CDI_Acumulada_Val'])),
        ("3. CAGR Anual por Dia de Aplicação", fig2, "CAGR Anual por Dia de Aplicação", analisar_cagr(metrics['CAGR_Medio_Val'], metrics['CAGR_CDI_Medio_Val'])),
        ("4. Excesso de Retorno Anualizado", fig_excesso_retorno, "Excesso de Retorno Anualizado", "O Excesso de Retorno Anualizado mede a capacidade do fundo de gerar retornos acima do CDI, ajustado pelo tempo. Valores positivos indicam superação do benchmark."),
        ("5. Drawdown Histórico", fig3, "Drawdown Histórico", analisar_max_drawdown(metrics['Max_Drawdown_Val'])),
        ("6. Volatilidade Móvel", fig4, "Volatilidade Móvel", analisar_volatilidade_historica(metrics['Vol_Historica_Val'])),
        ("7. Value at Risk (VaR) e Expected Shortfall (ES)", fig5, "VaR e ES", analisar_var_es(VaR_95, VaR_99, ES_95, ES_99)),
        ("8. Patrimônio e Captação Líquida", fig6, "Patrimônio e Captação Líquida", analisar_patrimonio_captacao(metrics['Patrimonio_Liq_Val'], metrics['Captacao_Liquida_Acum_Val'])),
        ("9. Captação Líquida Mensal", fig7, "Captação Líquida Mensal", analisar_captacao_mensal(df_monthly)),
        ("10. Patrimônio Médio e Nº de Cotistas", fig8, "Patrimônio Médio e Nº de Cotistas", analisar_cotistas(metrics['Patrimonio_Medio_Cotista_Val'], metrics['Num_Cotistas_Val'])),
        ("11. Retornos em Janelas Móveis", fig9, "Retornos em Janelas Móveis", "Este gráfico mostra a performance do fundo em diferentes janelas de tempo, permitindo avaliar a consistência dos retornos ao longo do tempo."),
        ("12. Consistência em Janelas Móveis", fig_consistency, "Consistência em Janelas Móveis", analisar_consistencia(df_consistency))
    ]

    # Adicionar métricas de risco-retorno como texto
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(26, 95, 63)
    pdf.cell(0, 10, "13. Métricas de Risco-Retorno", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.ln(5)

    if tem_cdi:
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 6, "RISCO MEDIDO PELA VOLATILIDADE:", 0, 'L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, f"Sharpe Ratio: {sharpe_ratio:.2f}" if not pd.isna(sharpe_ratio) else "Sharpe Ratio: N/A", 0, 'L')
        pdf.multi_cell(0, 6, analisar_sharpe_ratio(sharpe_ratio), 0, 'L')
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"Sortino Ratio: {sortino_ratio:.2f}" if not pd.isna(sortino_ratio) else "Sortino Ratio: N/A", 0, 'L')
        pdf.multi_cell(0, 6, analisar_sortino_ratio(sortino_ratio), 0, 'L')
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"Information Ratio: {information_ratio:.2f}" if not pd.isna(information_ratio) else "Information Ratio: N/A", 0, 'L')
        pdf.multi_cell(0, 6, analisar_information_ratio(information_ratio), 0, 'L')
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 6, "RISCO MEDIDO PELO DRAWDOWN:", 0, 'L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, f"Calmar Ratio: {calmar_ratio:.2f}" if not pd.isna(calmar_ratio) else "Calmar Ratio: N/A", 0, 'L')
        pdf.multi_cell(0, 6, analisar_calmar_ratio(calmar_ratio), 0, 'L')
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"Sterling Ratio: {sterling_ratio:.2f}" if not pd.isna(sterling_ratio) else "Sterling Ratio: N/A", 0, 'L')
        pdf.multi_cell(0, 6, analisar_sterling_ratio(sterling_ratio), 0, 'L')
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"Ulcer Index: {ulcer_index:.2f}" if not pd.isna(ulcer_index) else "Ulcer Index: N/A", 0, 'L')
        pdf.multi_cell(0, 6, analisar_ulcer_index(ulcer_index), 0, 'L')
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"Martin Ratio: {martin_ratio:.2f}" if not pd.isna(martin_ratio) else "Martin Ratio: N/A", 0, 'L')
        pdf.multi_cell(0, 6, analisar_martin_ratio(martin_ratio), 0, 'L')
        pdf.ln(5)
    else:
        pdf.multi_cell(0, 6, "As Métricas de Risco-Retorno requerem a comparação com o CDI.", 0, 'L')
    pdf.ln(10)

    # Adicionar gráficos e análises
    for i, (section_title, fig, chart_title, analysis_text) in enumerate(sections):
        if fig is None: # Pula se o gráfico não foi gerado (ex: falta de dados)
            continue

        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(26, 95, 63)
        pdf.cell(0, 10, section_title, 0, 1, 'L')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 10)
        pdf.ln(5)

        # Salvar gráfico como SVG temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmp_svg:
            fig.write_image(tmp_svg.name, format='svg', width=1000, height=500) # Aumenta a resolução para PDF
            svg_path = tmp_svg.name

        # Converter SVG para PNG para FPDF (FPDF não suporta SVG diretamente)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_png:
            img = Image.open(svg_path)
            img.save(tmp_png.name, format='PNG')
            png_path = tmp_png.name

        # Adicionar imagem ao PDF
        pdf.image(png_path, x=10, w=pdf.w - 20) # Ajusta largura para caber na página
        pdf.ln(5)

        # Adicionar análise
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 6, f"Análise de {chart_title}:", 0, 'L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, analysis_text, 0, 'L')
        pdf.ln(10)

        # Limpar arquivos temporários
        os.remove(svg_path)
        os.remove(png_path)

    # Conclusão Final do Relatório
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(26, 95, 63)
    pdf.cell(0, 10, "14. Conclusão Final", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.ln(5)
    pdf.multi_cell(0, 6, conclusao_geral_texto, 0, 'L') # Reutiliza a conclusão geral
    pdf.ln(10)

    # Rodapé
    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(108, 117, 125)
    pdf.cell(0, 10, f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} - Copaíba Invest", 0, 0, 'C')

    return pdf.output(dest='S').encode('latin-1') # Retorna o PDF como bytes

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

    1.  **CNPJ do Fundo**: Digite o CNPJ do fundo que deseja analisar
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

# Inicializa variáveis para os gráficos e métricas para evitar NameError
# quando o botão de relatório é clicado antes de carregar os dados
df = pd.DataFrame()
df_plot_cagr = pd.DataFrame()
df_plot_var = pd.DataFrame()
df_monthly = pd.DataFrame()
df_returns = pd.DataFrame()
df_consistency = pd.DataFrame()

fig1, fig2, fig_excesso_retorno, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig_consistency = [None] * 11
metrics_display = {}
metrics_values = {}
sharpe_ratio, sortino_ratio, information_ratio, calmar_ratio, sterling_ratio, ulcer_index, martin_ratio = [np.nan] * 7
VaR_95, VaR_99, ES_95, ES_99 = [np.nan] * 4
tem_cdi = False
nome_fundo = "Fundo Não Identificado" # Default

try:
    with st.spinner('🔄 Carregando dados...'):
        # Converte as datas de input do usuário para objetos datetime
        dt_ini_user = datetime.strptime(st.session_state.data_ini, '%Y%m%d')
        dt_fim_user = datetime.strptime(st.session_state.data_fim, '%Y%m%d')

        # 1. BAIXAR DADOS DO FUNDO (período ampliado para ffill)
        df_fundo_completo = carregar_dados_api(
            st.session_state.cnpj,
            st.session_state.data_ini,
            st.session_state.data_fim
        )
        df_fundo_completo = df_fundo_completo.sort_values('DT_COMPTC').reset_index(drop=True)

        if not df_fundo_completo.empty and 'DENOM_SOCIAL' in df_fundo_completo.columns:
            nome_fundo = df_fundo_completo['DENOM_SOCIAL'].iloc[0]
        else:
            nome_fundo = f"Fundo CNPJ: {st.session_state.cnpj}"

        # 2. OBTER DADOS DO CDI para o período EXATO solicitado pelo usuário
        df_cdi_raw = pd.DataFrame()
        if st.session_state.mostrar_cdi and BCB_DISPONIVEL:
            df_cdi_raw = obter_dados_cdi_real(dt_ini_user, dt_fim_user)
            if not df_cdi_raw.empty:
                df_cdi_raw = df_cdi_raw.sort_values('DT_COMPTC').reset_index(drop=True)

        # 3. COMBINAR FUNDO E CDI, USANDO DATAS DO CDI COMO BASE
        if not df_cdi_raw.empty:
            # Usa as datas do CDI como base (left merge) e adiciona os dados do fundo
            df_final = df_cdi_raw[['DT_COMPTC', 'cdi', 'VL_CDI_normalizado']].copy()
            df_final = df_final.merge(df_fundo_completo, on='DT_COMPTC', how='left')
        else:
            # Se CDI não for solicitado ou não estiver disponível, usa os dados do fundo como base
            df_final = df_fundo_completo.copy()
            # Garante que colunas CDI não existam se não forem usadas
            df_final.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado'] if col in df_final.columns], errors='ignore', inplace=True)

        # Garante que o dataframe esteja ordenado por data
        df_final = df_final.sort_values('DT_COMPTC').reset_index(drop=True)

        # 4. Preencher valores ausentes para colunas do fundo com o último valor válido (forward-fill)
        fund_cols_to_ffill = ['VL_QUOTA', 'VL_PATRIM_LIQ', 'NR_COTST', 'CAPTC_DIA', 'RESG_DIA']
        for col in fund_cols_to_ffill:
            if col in df_final.columns:
                df_final[col] = df_final[col].ffill()

        # 5. Remover linhas onde VL_QUOTA ainda é NaN (fundo não existia ou não tinha dados mesmo após ffill)
        df_final.dropna(subset=['VL_QUOTA'], inplace=True)

        # 6. Filtrar o dataframe combinado para o período EXATO solicitado pelo usuário
        df = df_final[(df_final['DT_COMPTC'] >= dt_ini_user) & (df_final['DT_COMPTC'] <= dt_fim_user)].copy()

        # Verifica se o dataframe final está vazio após todas as operações
        if df.empty:
            st.error("❌ Não há dados disponíveis para o fundo no período selecionado após a combinação com o CDI ou o fundo não possui dados suficientes.")
            st.stop()

        # 7. Re-normalizar a cota do fundo para começar em 1.0 (0% de rentabilidade) na primeira data do 'df' final
        primeira_cota_fundo = df['VL_QUOTA'].iloc[0]
        df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota_fundo) - 1) * 100

        # Processa e re-normaliza os dados do CDI para o 'df' final
        tem_cdi = False
        if st.session_state.mostrar_cdi and 'VL_CDI_normalizado' in df.columns:
            # Re-normaliza o CDI para começar em 1.0 na primeira data do 'df' final
            first_cdi_normalized_value_in_period = df['VL_CDI_normalizado'].iloc[0]
            df['CDI_COTA'] = df['VL_CDI_normalizado'] / first_cdi_normalized_value_in_period
            df['CDI_NORM'] = (df['CDI_COTA'] - 1) * 100
            tem_cdi = True
        else:
            # Garante que colunas CDI sejam removidas se não forem solicitadas ou não estiverem disponíveis
            df.drop(columns=[col for col in ['cdi', 'VL_CDI_normalizado', 'CDI_COTA', 'CDI_NORM'] if col in df.columns], errors='ignore', inplace=True)

    # 3. CALCULAR MÉTRICAS (agora usando o 'df' combinado e normalizado)
    df = df.sort_values('DT_COMPTC').reset_index(drop=True)

    # Métricas do fundo
    df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
    df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100
    df['Captacao_Liquida'] = df['CAPTC_DIA'] - df['RESG_DIA']
    df['Soma_Acumulada'] = df['Captacao_Liquida'].cumsum()
    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

    vol_window = 21
    trading_days_in_year = 252 # Número de dias úteis em um ano para anualização
    df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()
    df['Volatilidade'] = df['Variacao_Perc'].rolling(vol_window).std() * np.sqrt(trading_days_in_year) * 100
    vol_hist = round(df['Variacao_Perc'].std() * np.sqrt(trading_days_in_year) * 100, 2)

    # CAGR - Cálculo conforme sua especificação: última cota fixa, cota inicial variável
    df['CAGR_Fundo'] = np.nan
    if tem_cdi:
        df['CAGR_CDI'] = np.nan

    if not df.empty and len(df) > trading_days_in_year:
        end_value_fundo = df['VL_QUOTA'].iloc[-1]
        if tem_cdi:
            end_value_cdi = df['CDI_COTA'].iloc[-1]

        # O loop vai até o índice que é 'trading_days_in_year' antes do último.
        # Isso garante que o último ponto plotado no gráfico de CAGR seja 252 dias antes do final.
        # O range vai de 0 até (len(df) - trading_days_in_year)
        for i in range(len(df) - trading_days_in_year):
            initial_value_fundo = df['VL_QUOTA'].iloc[i]

            # num_intervals é o número de intervalos (dias úteis) do ponto inicial (i) até o ponto final (último)
            # Ex: para índices 0,1,2,3 (len=4). Se i=0, num_intervals = (3-0) = 3.
            # Se i=1, num_intervals = (3-1) = 2.
            num_intervals = (len(df) - 1) - i

            if initial_value_fundo > 0 and num_intervals > 0:
                df.loc[i, 'CAGR_Fundo'] = ((end_value_fundo / initial_value_fundo) ** (trading_days_in_year / num_intervals) - 1) * 100

            if tem_cdi and 'CDI_COTA' in df.columns:
                initial_value_cdi = df['CDI_COTA'].iloc[i]
                if initial_value_cdi > 0 and num_intervals > 0:
                    df.loc[i, 'CAGR_CDI'] = ((end_value_cdi / initial_value_cdi) ** (trading_days_in_year / num_intervals) - 1) * 100

    # Calcular CAGR médio para o card de métricas (baseado na nova coluna CAGR_Fundo)
    mean_cagr = df['CAGR_Fundo'].mean() if 'CAGR_Fundo' in df.columns else 0
    if pd.isna(mean_cagr): # Lida com casos onde todos os CAGRs são NaN por falta de dados
        mean_cagr = 0

    mean_cagr_cdi = df['CAGR_CDI'].mean() if 'CAGR_CDI' in df.columns else 0
    if pd.isna(mean_cagr_cdi):
        mean_cagr_cdi = 0

    # Excesso de Retorno Anualizado
    df['EXCESSO_RETORNO_ANUALIZADO'] = np.nan
    if tem_cdi and 'CAGR_Fundo' in df.columns and 'CAGR_CDI' in df.columns:
        # Apenas calcula onde ambos os CAGRs estão disponíveis
        valid_excess_return_indices = df.dropna(subset=['CAGR_Fundo', 'CAGR_CDI']).index
        if not valid_excess_return_indices.empty:
            df.loc[valid_excess_return_indices, 'EXCESSO_RETORNO_ANUALIZADO'] = (
                (1 + df.loc[valid_excess_return_indices, 'CAGR_Fundo'] / 100) /
                (1 + df.loc[valid_excess_return_indices, 'CAGR_CDI'] / 100) - 1
            ) * 100 # Multiplica por 100 para exibir em porcentagem

    # VaR
    df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
    df_plot_var = df.dropna(subset=['Retorno_21d']).copy()
    VaR_95, VaR_99, ES_95, ES_99 = np.nan, np.nan, np.nan, np.nan # Inicializa com NaN
    if not df_plot_var.empty:
        VaR_95 = np.percentile(df_plot_var['Retorno_21d'], 5)
        VaR_99 = np.percentile(df_plot_var['Retorno_21d'], 1)
        ES_95 = df_plot_var.loc[df_plot_var['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
        ES_99 = df_plot_var.loc[df_plot_var['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()
    else:
        st.warning("⚠️ Não há dados suficientes para calcular VaR e ES (mínimo de 21 dias de retorno).")

    # Cores
    color_primary = '#1a5f3f'  # Verde escuro para o fundo
    color_secondary = '#6b9b7f'
    color_danger = '#dc3545'
    color_cdi = '#f0b429'  # Amarelo para o CDI

    # Cards de métricas
    col1, col2, col3, col4, col5 = st.columns(5)

    # Coleta de valores para o PDF
    patrimonio_liq_val = df['VL_PATRIM_LIQ'].iloc[-1]
    rent_acum_val = df['VL_QUOTA_NORM'].iloc[-1]
    cagr_medio_val = mean_cagr
    max_drawdown_val = df['Drawdown'].min()
    vol_hist_val = vol_hist
    cdi_acum_val = df['CDI_NORM'].iloc[-1] if tem_cdi else np.nan
    captacao_liquida_acum_val = df['Soma_Acumulada'].iloc[-1]
    patrimonio_medio_cotista_val = df['Patrimonio_Liq_Medio'].iloc[-1]
    num_cotistas_val = df['NR_COTST'].iloc[-1]

    metrics_display = {
        "Patrimonio_Liq": format_brl(patrimonio_liq_val),
        "Rentabilidade_Acumulada": fmt_pct_port(rent_acum_val / 100),
        "CAGR_Medio": fmt_pct_port(cagr_medio_val / 100),
        "Max_Drawdown": fmt_pct_port(max_drawdown_val / 100),
        "Vol_Historica": fmt_pct_port(vol_hist_val / 100),
        "CDI_Acumulada": fmt_pct_port(cdi_acum_val / 100) if tem_cdi else "N/A",
        "Captacao_Liquida_Acum": format_brl(captacao_liquida_acum_val),
        "Patrimonio_Medio_Cotista": format_brl(patrimonio_medio_cotista_val),
        "Num_Cotistas": f"{int(num_cotistas_val):,}".replace(',', '.')
    }

    metrics_values = {
        "Patrimonio_Liq_Val": patrimonio_liq_val,
        "Rentabilidade_Acumulada_Val": rent_acum_val,
        "CAGR_Medio_Val": cagr_medio_val,
        "Max_Drawdown_Val": max_drawdown_val,
        "Vol_Historica_Val": vol_hist_val,
        "CDI_Acumulada_Val": cdi_acum_val,
        "CAGR_CDI_Medio_Val": mean_cagr_cdi,
        "Captacao_Liquida_Acum_Val": captacao_liquida_acum_val,
        "Patrimonio_Medio_Cotista_Val": patrimonio_medio_cotista_val,
        "Num_Cotistas_Val": num_cotistas_val
    }

    with col1:
        st.metric("Patrimônio Líquido", metrics_display["Patrimonio_Liq"])
    with col2:
        st.metric("Rentabilidade Acumulada", metrics_display["Rentabilidade_Acumulada"])
    with col3:
        st.metric("CAGR Médio", metrics_display["CAGR_Medio"])
    with col4:
        st.metric("Max Drawdown", metrics_display["Max_Drawdown"])
    with col5:
        st.metric("Vol. Histórica", metrics_display["Vol_Historica"])

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
        # Ajusta o range do eixo X para os dados de df
        fig1 = add_watermark_and_style(fig1, logo_base64, x_range=[df['DT_COMPTC'].min(), df['DT_COMPTC'].max()], x_autorange=False)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("CAGR Anual por Dia de Aplicação")

        fig2 = go.Figure()

        # Usar um dataframe filtrado para o plot do CAGR, removendo NaNs iniciais
        df_plot_cagr = df.dropna(subset=['CAGR_Fundo']).copy()

        if not df_plot_cagr.empty:
            # CAGR do Fundo
            fig2.add_trace(go.Scatter(
                x=df_plot_cagr['DT_COMPTC'],
                y=df_plot_cagr['CAGR_Fundo'], # Usar a nova coluna de CAGR
                mode='lines',
                name='CAGR do Fundo',
                line=dict(color=color_primary, width=2.5),
                hovertemplate='<b>CAGR do Fundo</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
            ))

            fig2.add_trace(go.Scatter(
                x=df_plot_cagr['DT_COMPTC'], # Usar df_plot_cagr para o eixo X
                y=[mean_cagr] * len(df_plot_cagr),
                mode='lines',
                line=dict(dash='dash', color=color_secondary, width=2),
                name=f'CAGR Médio ({mean_cagr:.2f}%)'
            ))

            # CAGR do CDI (se disponível)
            if tem_cdi and 'CAGR_CDI' in df_plot_cagr.columns:
                fig2.add_trace(go.Scatter(
                    x=df_plot_cagr['DT_COMPTC'],
                    y=df_plot_cagr['CAGR_CDI'], # Usar a nova coluna de CAGR do CDI
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
        # Ajusta o range do eixo X para os dados de df_plot_cagr
        if not df_plot_cagr.empty:
            fig2 = add_watermark_and_style(fig2, logo_base64, x_range=[df_plot_cagr['DT_COMPTC'].min(), df_plot_cagr['DT_COMPTC'].max()], x_autorange=False)
        else:
            fig2 = add_watermark_and_style(fig2, logo_base64) # Sem range específico se não houver dados
        st.plotly_chart(fig2, use_container_width=True)

        # NOVO GRÁFICO: Excesso de Retorno Anualizado
        st.subheader("Excesso de Retorno Anualizado")

        if tem_cdi and not df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO']).empty:
            fig_excesso_retorno = go.Figure()

            # Linha do Excesso de Retorno
            fig_excesso_retorno.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['EXCESSO_RETORNO_ANUALIZADO'],
                mode='lines',
                name='Excesso de Retorno Anualizado',
                line=dict(color=color_primary, width=2.5), # Cor alterada para color_primary
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
            df_plot_excess = df.dropna(subset=['EXCESSO_RETORNO_ANUALIZADO']).copy()
            if not df_plot_excess.empty:
                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64, x_range=[df_plot_excess['DT_COMPTC'].min(), df_plot_excess['DT_COMPTC'].max()], x_autorange=False)
            else:
                fig_excesso_retorno = add_watermark_and_style(fig_excesso_retorno, logo_base64) # Sem range específico se não houver dados
            st.plotly_chart(fig_excesso_retorno, use_container_width=True)
        elif st.session_state.mostrar_cdi:
            st.warning("⚠️ Não há dados suficientes para calcular o Excesso de Retorno Anualizado (verifique se há dados de CDI e CAGR para o período).")
            fig_excesso_retorno = None # Garante que a variável seja None se o gráfico não for gerado
        else:
            st.info("ℹ️ Selecione a opção 'Comparar com CDI' na barra lateral para visualizar o Excesso de Retorno Anualizado.")
            fig_excesso_retorno = None # Garante que a variável seja None se o gráfico não for gerado

    with tab2:
        st.subheader("Drawdown Histórico")

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

        st.subheader(f"Volatilidade Móvel ({vol_window} dias úteis)")

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

        st.subheader("Value at Risk (VaR) e Expected Shortfall (ES)")

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
            fig5 = None # Garante que a variável seja None se o gráfico não for gerado

        st.subheader("Métricas de Risco-Retorno")

        # --- Cálculos dos Novos Indicadores ---
        calmar_ratio, sterling_ratio, ulcer_index, martin_ratio, sharpe_ratio, sortino_ratio, information_ratio = [np.nan] * 7

        if tem_cdi and not df.empty and len(df) > trading_days_in_year:
            # Retorno total do fundo e CDI no período
            total_fund_return = (df['VL_QUOTA'].iloc[-1] / df['VL_QUOTA'].iloc[0]) - 1
            total_cdi_return = (df['CDI_COTA'].iloc[-1] / df['CDI_COTA'].iloc[0]) - 1

            # Anualização dos retornos totais para consistência
            num_days_in_period = len(df)
            if num_days_in_period > 0:
                annualized_fund_return = (1 + total_fund_return)**(trading_days_in_year / num_days_in_period) - 1
                annualized_cdi_return = (1 + total_cdi_return)**(trading_days_in_year / num_days_in_period) - 1
            else:
                annualized_fund_return = 0
                annualized_cdi_return = 0

            # Volatilidade anualizada do fundo (já calculada como vol_hist, convertida para decimal)
            annualized_fund_volatility = vol_hist / 100 if vol_hist else np.nan

            # Max Drawdown (já calculada como df['Drawdown'].min(), convertida para decimal)
            max_drawdown_value = df['Drawdown'].min() / 100 if not df['Drawdown'].empty else np.nan

            # CAGR do fundo (já calculada como mean_cagr, convertida para decimal)
            cagr_fund_decimal = mean_cagr / 100 if mean_cagr else np.nan

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
            if 'cdi' in df.columns and not df['Variacao_Perc'].empty:
                excess_daily_returns = df['Variacao_Perc'] - (df['cdi'] / 100)
                if not excess_daily_returns.empty:
                    tracking_error = excess_daily_returns.std() * np.sqrt(trading_days_in_year)
                else:
                    tracking_error = np.nan
            else:
                tracking_error = np.nan

            # --- Cálculo dos Ratios ---
            if not pd.isna(cagr_fund_decimal) and not pd.isna(annualized_cdi_return) and not pd.isna(max_drawdown_value) and max_drawdown_value != 0:
                calmar_ratio = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value)
                sterling_ratio = (cagr_fund_decimal - annualized_cdi_return) / abs(max_drawdown_value) # Simplificado para Max Drawdown

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

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("💡 Verifique se o CNPJ está correto e se há dados disponíveis para o período selecionado.")

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
                    VaR_95=VaR_95, VaR_99=VaR_99, ES_95=ES_95, ES_99=ES_99
                )
                if pdf_output:
                    st.download_button(
                        label="Download Relatório PDF",
                        data=pdf_output,
                        file_name=f"Relatorio_Fundo_{st.session_state.cnpj}_{dt_ini_user.strftime('%Y%m%d')}_{dt_fim_user.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ Relatório PDF gerado com sucesso!")
                else:
                    st.error("❌ Falha ao gerar o relatório PDF.")
            except Exception as e:
                st.error(f"❌ Erro ao gerar o relatório PDF: {e}")
    else:
        st.error("❌ As bibliotecas 'fpdf2' e 'Pillow' são necessárias para gerar o PDF. Por favor, instale-as.")


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
