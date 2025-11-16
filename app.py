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
import uuid

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

# CSS customizado com suporte para múltiplos fundos
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
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%) !important;
        border-radius: 10px !important;
        padding: 0.5rem 0.7rem !important;
        margin: 0.3rem 0 !important;
        border-left: 3px solid #28a745 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        font-size: 0.8rem !important;
    }

    [data-testid="stSidebar"] .stAlert [data-testid="stMarkdownContainer"] {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Lista de CNPJs selecionados */
    .cnpj-list {
        margin: 0.5rem 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
    }

    .cnpj-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.4rem 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.4rem;
    }

    .cnpj-item:last-child {
        margin-bottom: 0;
    }

    .cnpj-text {
        font-size: 0.85rem;
        font-weight: 500;
        color: white;
    }

    .cnpj-remove {
        cursor: pointer;
        color: white;
        font-weight: bold;
        opacity: 0.7;
        transition: opacity 0.2s;
    }

    .cnpj-remove:hover {
        opacity: 1;
    }

    .color-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 6px;
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
def add_watermark_and_style(fig, logo_base64=None):
    """
    Adiciona marca d'água MUITO GRANDE cobrindo todo o gráfico
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

    # Estilização elegante com fundo transparente (sem borda)
    fig.update_layout(
        plot_bgcolor='rgba(248, 246, 241, 0.5)',
        paper_bgcolor='rgba(0,0,0,0)',  # Transparente para remover o retângulo branco
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
        # Sem shapes para remover a borda
        shapes=[]
    )

    # Estilizar eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(224, 221, 213, 0.5)',
        showline=False,  # Sem linha de borda
        linewidth=1,
        linecolor='#e0ddd5',
        title_font=dict(size=13, color="#1a5f3f", family="Inter"),
        tickfont=dict(size=11, color="#6b9b7f")
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(224, 221, 213, 0.5)',
        showline=False,  # Sem linha de borda
        linewidth=1,
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

# Função para formatar CNPJ para exibição
def formatar_cnpj_display(cnpj):
    """Formata CNPJ para exibição: 00.000.000/0000-00"""
    cnpj_limpo = limpar_cnpj(cnpj)
    if len(cnpj_limpo) == 14:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    return cnpj

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

# Função para buscar data anterior disponível
def buscar_data_anterior(df, data_alvo):
    datas_disponiveis = df['DT_COMPTC']
    datas_anteriores = datas_disponiveis[datas_disponiveis <= data_alvo]
    if len(datas_anteriores) > 0:
        return datas_anteriores.idxmax()
    return None

# Função para ajustar período de análise (SEM MOSTRAR NOTIFICAÇÃO)
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

# Cores para múltiplos fundos
def get_fund_colors(num_funds):
    """Retorna uma lista de cores distintas para os fundos"""
    base_colors = [
        '#1a5f3f',  # Verde principal
        '#e63946',  # Vermelho
        '#457b9d',  # Azul
        '#f0b429',  # Amarelo
        '#8338ec',  # Roxo
        '#ff9f1c',  # Laranja
        '#2a9d8f',  # Verde água
        '#f4a261',  # Salmão
        '#264653',  # Azul escuro
        '#e76f51',  # Terracota
    ]

    # Se precisar de mais cores, gera variações
    if num_funds <= len(base_colors):
        return base_colors[:num_funds]
    else:
        # Gera cores adicionais se necessário
        import colorsys

        additional_colors = []
        for i in range(num_funds - len(base_colors)):
            hue = i / (num_funds - len(base_colors))
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            additional_colors.append(f'rgb({int(r*255)},{int(g*255)},{int(b*255)})')

        return base_colors + additional_colors

# Inicializar state para CNPJs
if 'cnpjs' not in st.session_state:
    st.session_state.cnpjs = []  # Lista de dicionários {id, cnpj, nome}

# Sidebar com logo
if logo_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" alt="Copaíba Invest"></div>',
        unsafe_allow_html=True
    )

# Formulário para adicionar CNPJs
with st.sidebar.form(key="add_cnpj_form"):
    st.markdown("### Adicionar Fundo")

    cnpj_input = st.text_input(
        "CNPJ do Fundo",
        value="",
        placeholder="00.000.000/0000-00",
        help="Digite o CNPJ com ou sem formatação"
    )

    nome_fundo_input = st.text_input(
        "Nome do Fundo (opcional)",
        value="",
        placeholder="Ex: Fundo ABC"
    )

    submitted = st.form_submit_button("➕ Adicionar Fundo")

    if submitted:
        cnpj_limpo = limpar_cnpj(cnpj_input)
        if len(cnpj_limpo) != 14:
            st.sidebar.error("❌ CNPJ deve conter 14 dígitos")
        else:
            # Verifica se o CNPJ já existe na lista
            cnpj_exists = any(item['cnpj'] == cnpj_limpo for item in st.session_state.cnpjs)
            if cnpj_exists:
                st.sidebar.error("❌ Este CNPJ já foi adicionado")
            else:
                # Adiciona o novo CNPJ à lista
                novo_fundo = {
                    'id': str(uuid.uuid4()),
                    'cnpj': cnpj_limpo,
                    'nome': nome_fundo_input.strip() if nome_fundo_input.strip() else f"Fundo {len(st.session_state.cnpjs) + 1}"
                }
                st.session_state.cnpjs.append(novo_fundo)
                st.sidebar.success(f"✅ Fundo adicionado: {novo_fundo['nome']}")

# Exibir lista de CNPJs adicionados
if st.session_state.cnpjs:
    st.sidebar.markdown("### Fundos Selecionados")

    # Gerar cores para os fundos
    colors = get_fund_colors(len(st.session_state.cnpjs))

    # Exibir cada CNPJ com opção de remover
    cnpj_html = '<div class="cnpj-list">'

    for i, fundo in enumerate(st.session_state.cnpjs):
        color = colors[i]
        cnpj_formatado = formatar_cnpj_display(fundo['cnpj'])
        cnpj_html += f"""
        <div class="cnpj-item" id="{fundo['id']}">
            <div class="cnpj-info">
                <span class="color-indicator" style="background-color: {color};"></span>
                <span class="cnpj-text">{fundo['nome']}</span>
                <span class="cnpj-text" style="opacity: 0.7; font-size: 0.75rem; margin-left: 18px;">{cnpj_formatado}</span>
            </div>
            <span class="cnpj-remove" onclick="remove_cnpj('{fundo['id']}')">✕</span>
        </div>
        """

    cnpj_html += '</div>'

    # JavaScript para remover CNPJ
    js_code = """
    <script>
    function remove_cnpj(id) {
        window.parent.postMessage({
            type: 'remove_cnpj',
            id: id
        }, '*');
    }
    </script>
    """

    st.sidebar.markdown(cnpj_html + js_code, unsafe_allow_html=True)

    # Listener para mensagens JavaScript
    if 'remove_cnpj_id' in st.query_params:
        remove_id = st.query_params['remove_cnpj_id'][0]
        st.session_state.cnpjs = [f for f in st.session_state.cnpjs if f['id'] != remove_id]
        # Limpar query param
        st.query_params.clear()
        st.rerun()

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

st.sidebar.markdown("---")

# Processar inputs
data_inicial_formatada = formatar_data_api(data_inicial_input)
data_final_formatada = formatar_data_api(data_final_input)

# Validação
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
tem_fundos = len(st.session_state.cnpjs) > 0
carregar_button = st.sidebar.button("🔄 Carregar Dados", type="primary", disabled=not (tem_fundos and datas_validas))

# Título principal
st.markdown("<h1>📊 Dashboard Comparativo de Fundos</h1>", unsafe_allow_html=True)
st.markdown("---")

# Função para carregar dados de múltiplos fundos
@st.cache_data
def carregar_dados_api(cnpj, data_ini, data_fim):
    dt_inicial = datetime.strptime(data_ini, '%Y%m%d')
    dt_ampliada = dt_inicial - timedelta(days=60)
    data_ini_ampliada = dt_ampliada.strftime('%Y%m%d')

    url = f"https://www.okanebox.com.br/api/fundoinvestimento/hist/{cnpj}/{data_ini_ampliada}/{data_fim}/"
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
    st.session_state.dados_fundos = {}  # Dicionário para armazenar dados de múltiplos fundos

if carregar_button and tem_fundos and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada

    # Limpa dados anteriores
    st.session_state.dados_fundos = {}

if not st.session_state.dados_carregados:
    st.info("👈 Adicione pelo menos um fundo, defina o período e clique em 'Carregar Dados' para começar a análise.")

    st.markdown("""
    ### 📋 Como usar:

    1. **Adicione fundos**: Digite o CNPJ e um nome opcional para cada fundo que deseja analisar
    2. **Defina o período**: Informe as datas inicial e final para análise
    3. **Compare os fundos**: Visualize os resultados comparativos nos gráficos

    Este dashboard permite comparar o desempenho de múltiplos fundos simultaneamente.
    """)

    st.stop()

try:
    with st.spinner('🔄 Carregando dados dos fundos...'):
        # Carregar dados para cada fundo
        for i, fundo in enumerate(st.session_state.cnpjs):
            if fundo['cnpj'] not in st.session_state.dados_fundos:
                df_completo = carregar_dados_api(fundo['cnpj'], st.session_state.data_ini, st.session_state.data_fim)
                df, ajustes = ajustar_periodo_analise(df_completo, st.session_state.data_ini, st.session_state.data_fim)

                # Preparação dos dados
                df = df.sort_values('DT_COMPTC').reset_index(drop=True)
                primeira_cota = df['VL_QUOTA'].iloc[0]
                df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota) - 1) * 100

                # Calcular métricas
                df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
                df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100
                df['Captacao_Liquida'] = df['CAPTC_DIA'] - df['RESG_DIA']
                df['Soma_Acumulada'] = df['Captacao_Liquida'].cumsum()
                df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

                vol_window = 21
                trading_days = 252
                df['Variacao_Perc'] = df['VL_QUOTA'].pct_change()
                df['Volatilidade'] = df['VL_QUOTA'].pct_change().rolling(vol_window).std() * np.sqrt(trading_days) * 100
                vol_hist = round(df['Variacao_Perc'].std() * np.sqrt(trading_days) * 100, 2)

                # CAGR
                df_cagr = df.copy()
                end_value = df_cagr['VL_QUOTA'].iloc[-1]
                df_cagr['dias_uteis'] = df_cagr.index[-1] - df_cagr.index
                df_cagr = df_cagr[df_cagr['dias_uteis'] >= 252].copy()
                if not df_cagr.empty:
                    df_cagr['CAGR'] = ((end_value / df_cagr['VL_QUOTA']) ** (252 / df_cagr['dias_uteis'])) - 1
                    df_cagr['CAGR'] = df_cagr['CAGR'] * 100
                    mean_cagr = df_cagr['CAGR'].mean()
                else:
                    mean_cagr = None

                # VaR
                df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
                df_plot = df.dropna(subset=['Retorno_21d']).copy()
                if not df_plot.empty:
                    VaR_95 = np.percentile(df_plot['Retorno_21d'], 5)
                    VaR_99 = np.percentile(df_plot['Retorno_21d'], 1)
                    ES_95 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
                    ES_99 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()
                else:
                    VaR_95 = VaR_99 = ES_95 = ES_99 = None

                # Armazenar dados processados
                st.session_state.dados_fundos[fundo['cnpj']] = {
                    'df': df,
                    'df_cagr': df_cagr,
                    'vol_hist': vol_hist,
                    'mean_cagr': mean_cagr,
                    'VaR_95': VaR_95,
                    'VaR_99': VaR_99,
                    'ES_95': ES_95,
                    'ES_99': ES_99,
                    'nome': fundo['nome'],
                    'color': get_fund_colors(len(st.session_state.cnpjs))[i]
                }

    # Exibir métricas comparativas
    st.subheader("📊 Métricas Comparativas")

    # Criar colunas para métricas principais
    cols = st.columns(len(st.session_state.cnpjs))

    for i, fundo in enumerate(st.session_state.cnpjs):
        dados_fundo = st.session_state.dados_fundos[fundo['cnpj']]
        df = dados_fundo['df']

        with cols[i]:
            st.markdown(f"<h4 style='color:{dados_fundo['color']}'>{dados_fundo['nome']}</h4>", unsafe_allow_html=True)
            st.metric("💰 Patrimônio", format_brl(df['VL_PATRIM_LIQ'].iloc[-1]))
            st.metric("👥 Cotistas", f"{int(df['NR_COTST'].iloc[-1]):,}".replace(',', '.'))
            if dados_fundo['mean_cagr'] is not None:
                st.metric("📈 CAGR", f"{dados_fundo['mean_cagr']:.2f}%")
            else:
                st.metric("📈 CAGR", "N/A")
            st.metric("📊 Volatilidade", f"{dados_fundo['vol_hist']:.2f}%")

    st.markdown("---")

    # Tabs para organizar os gráficos
    tab1, tab2, tab3 = st.tabs([
        "📈 Rentabilidade Comparativa",
        "📉 Risco Comparativo",
        "💰 Patrimônio Comparativo"
    ])

    with tab1:
        st.subheader("📈 Rentabilidade Histórica Comparativa")

        fig1 = go.Figure()
        for fundo in st.session_state.cnpjs:
            dados_fundo = st.session_state.dados_fundos[fundo['cnpj']]
            df = dados_fundo['df']

            fig1.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_QUOTA_NORM'],
                mode='lines',
                name=dados_fundo['nome'],
                line=dict(color=dados_fundo['color'], width=2.5),
                hovertemplate='<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Rentabilidade: %{y:.2f}%<extra></extra>'
            ))

        fig1.update_layout(
            xaxis_title="Data",
            yaxis_title="Rentabilidade (%)",
            template="plotly_white",
            hovermode="closest",
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

        fig1 = add_watermark_and_style(fig1, logo_base64)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 CAGR Anual Comparativo")

        fig2 = go.Figure()
        for fundo in st.session_state.cnpjs:
            dados_fundo = st.session_state.dados_fundos[fundo['cnpj']]
            if not dados_fundo['df_cagr'].empty and dados_fundo['mean_cagr'] is not None:
                fig2.add_trace(go.Scatter(
                    x=dados_fundo['df_cagr']['DT_COMPTC'],
                    y=dados_fundo['df_cagr']['CAGR'],
                    mode='lines',
                    name=f"{dados_fundo['nome']}",
                    line=dict(color=dados_fundo['color'], width=2.5),
                    hovertemplate='<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>CAGR: %{y:.2f}%<extra></extra>'
                ))

                # Linha média
                fig2.add_trace(go.Scatter(
                    x=dados_fundo['df_cagr']['DT_COMPTC'],
                    y=[dados_fundo['mean_cagr']] * len(dados_fundo['df_cagr']),
                    mode='lines',
                    line=dict(dash='dash', color=dados_fundo['color'], width=1.5),
                    name=f"{dados_fundo['nome']} - Média ({dados_fundo['mean_cagr']:.2f}%)",
                    hoverinfo='skip'
                ))

        fig2.update_layout(
            xaxis_title="Data",
            yaxis_title="CAGR (% a.a)",
            template="plotly_white",
            hovermode="closest",
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

        fig2 = add_watermark_and_style(fig2, logo_base64)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("📉 Drawdown Histórico Comparativo")

        fig3 = go.Figure()
        for fundo in st.session_state.cnpjs:
            dados_fundo = st.session_state.dados_fundos[fundo['cnpj']]
            df = dados_fundo['df']

            fig3.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Drawdown'],
                mode='lines',
                name=dados_fundo['nome'],
                line=dict(color=dados_fundo['color'], width=2.5),
                hovertemplate='<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ))

        fig3.add_hline(y=0, line_dash='dash', line_color='gray', line_width=1)

        fig3.update_layout(
            xaxis_title="Data",
            yaxis_title="Drawdown (%)",
            template="plotly_white",
            hovermode="closest",
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

        fig3 = add_watermark_and_style(fig3, logo_base64)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"📊 Volatilidade Móvel Comparativa ({vol_window} dias úteis)")

        fig4 = go.Figure()
        for fundo in st.session_state.cnpjs:
            dados_fundo = st.session_state.dados_fundos[fundo['cnpj']]
            df = dados_fundo['df']

            fig4.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['Volatilidade'],
                mode='lines',
                name=dados_fundo['nome'],
                line=dict(color=dados_fundo['color'], width=2.5),
                hovertemplate='<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Volatilidade: %{y:.2f}%<extra></extra>'
            ))

        fig4.update_layout(
            xaxis_title="Data",
            yaxis_title="Volatilidade (% a.a.)",
            template="plotly_white",
            hovermode="closest",
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

        fig4 = add_watermark_and_style(fig4, logo_base64)
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        st.subheader("💰 Patrimônio Líquido Comparativo")

        fig6 = go.Figure()
        for fundo in st.session_state.cnpjs:
            dados_fundo = st.session_state.dados_fundos[fundo['cnpj']]
            df = dados_fundo['df']

            fig6.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['VL_PATRIM_LIQ'],
                mode='lines',
                name=dados_fundo['nome'],
                line=dict(color=dados_fundo['color'], width=2.5),
                hovertemplate='<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Patrimônio: %{customdata}<extra></extra>',
                customdata=[format_brl(v) for v in df['VL_PATRIM_LIQ']]
            ))

        fig6.update_layout(
            xaxis_title="Data",
            yaxis_title="Patrimônio Líquido (R$)",
            template="plotly_white",
            hovermode="closest",
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

        fig6 = add_watermark_and_style(fig6, logo_base64)
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("👥 Número de Cotistas Comparativo")

        fig8 = go.Figure()
        for fundo in st.session_state.cnpjs:
            dados_fundo = st.session_state.dados_fundos[fundo['cnpj']]
            df = dados_fundo['df']

            fig8.add_trace(go.Scatter(
                x=df['DT_COMPTC'],
                y=df['NR_COTST'],
                mode='lines',
                name=dados_fundo['nome'],
                line=dict(color=dados_fundo['color'], width=2.5),
                hovertemplate='<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Cotistas: %{y}<extra></extra>'
            ))

        fig8.update_layout(
            xaxis_title="Data",
            yaxis_title="Número de Cotistas",
            template="plotly_white",
            hovermode="closest",
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

        fig8 = add_watermark_and_style(fig8, logo_base64)
        st.plotly_chart(fig8, use_container_width=True)

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("💡 Verifique se os CNPJs estão corretos e se há dados disponíveis para o período selecionado.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 2rem 0;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        <strong>Dashboard Comparativo de Fundos</strong>
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem;'>
        Análise de Fundos de Investimentos • Copaíba Invest • 2025
    </p>
</div>
""", unsafe_allow_html=True)
