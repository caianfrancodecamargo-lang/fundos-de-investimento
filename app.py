""", unsafe_allow_html=True)

# Logo da Copaíba Invest em base64
COPAIBA_LOGO = "data:image/png;base64,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# -*- coding: utf-8 -*-
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

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Fundos de Investimentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado inspirado no site Copaíba Invest
st.markdown("""
<style>
    /* Importar fonte similar */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Variáveis de cores inspiradas no Copaíba */
    :root {
        --primary-color: #1a5f3f;
        --secondary-color: #7a9b3a;
        --accent-color: #f0b429;
        --dark-bg: #0f1419;
        --light-bg: #f8f9fa;
        --text-dark: #1a1a1a;
        --text-light: #ffffff;
        --sidebar-light: #e8f0e4;
        --sidebar-medium: #c8d9bd;
    }

    /* Fundo geral */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar com gradiente verde claro */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e8f0e4 0%, #d4e3cc 100%);
        padding: 2rem 1rem;
    }

    [data-testid="stSidebar"] * {
        color: #1a5f3f !important;
    }

    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #1a5f3f !important;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    /* INPUTS COM FONTE PRETA */
    [data-testid="stSidebar"] input {
        background-color: #ffffff !important;
        border: 2px solid #7a9b3a !important;
        color: #000000 !important;
        border-radius: 8px;
        padding: 0.5rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] input::placeholder {
        color: #666666 !important;
        opacity: 0.7 !important;
    }

    /* Garantir que o texto digitado seja preto */
    [data-testid="stSidebar"] input:focus {
        color: #000000 !important;
        border-color: #1a5f3f !important;
        box-shadow: 0 0 0 2px rgba(26, 95, 63, 0.2) !important;
    }

    /* Botão principal */
    .stButton > button {
        background: linear-gradient(135deg, #f0b429 0%, #d99b1f 100%);
        color: #1a1a1a;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(240, 180, 41, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(240, 180, 41, 0.4);
        background: linear-gradient(135deg, #d99b1f 0%, #f0b429 100%);
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
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1a5f3f;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
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
        background: linear-gradient(135deg, #1a5f3f 0%, #2d8659 100%);
        color: white !important;
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

    /* Mensagens de sucesso/erro na sidebar */
    [data-testid="stSidebar"] .stAlert {
        background-color: rgba(26, 95, 63, 0.1);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1a5f3f;
    }
    
    /* Markdown headers no sidebar */
    [data-testid="stSidebar"] h3 {
        color: #1a5f3f !important;
        font-weight: 700 !important;
    }
    
    /* Divisor no sidebar */
    [data-testid="stSidebar"] hr {
        border-color: #7a9b3a !important;
        opacity: 0.3;
    }
</style>
""", unsafe_allow_html=True)

# Logo da Copaíba Invest (base64)
COPAIBA_LOGO_BASE64 = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="""

# Função para adicionar logo aos gráficos
def adicionar_logo_grafico(fig):
    """Adiciona a logo da Copaíba como marca d'água nos gráficos"""
    fig.add_layout_image(
        dict(
            source="https://i.imgur.com/wHZ5Kpb.png",  # URL da imagem que você enviou
            xref="paper",
            yref="paper",
            x=0.95,
            y=0.05,
            sizex=0.15,
            sizey=0.15,
            xanchor="right",
            yanchor="bottom",
            opacity=0.15,
            layer="below"
        )
    )
    return fig

# Função para limpar CNPJ (remove tudo que não é número)
def limpar_cnpj(cnpj):
    if not cnpj:
        return ""
    return re.sub(r'\D', '', cnpj)

# Função para converter data brasileira (DD/MM/AAAA) para formato API (AAAAMMDD)
def formatar_data_api(data_str):
    """
    Converte data do formato brasileiro DD/MM/AAAA para AAAAMMDD
    Aceita formatos: DD/MM/AAAA, DD-MM-AAAA, DD.MM.AAAA ou DDMMAAAA
    """
    if not data_str:
        return None

    # Remove caracteres não numéricos
    data_limpa = re.sub(r'\D', '', data_str)

    # Verifica se tem 8 dígitos
    if len(data_limpa) == 8:
        try:
            # Assume formato brasileiro DDMMAAAA
            dia = data_limpa[:2]
            mes = data_limpa[2:4]
            ano = data_limpa[4:]

            # Valida a data
            datetime.strptime(f"{dia}/{mes}/{ano}", '%d/%m/%Y')

            # Retorna no formato AAAAMMDD
            return f"{ano}{mes}{dia}"
        except ValueError:
            return None

    return None

# Função para buscar data anterior disponível
def buscar_data_anterior(df, data_alvo):
    """
    Busca a data mais próxima anterior à data alvo no DataFrame
    Retorna o índice da linha encontrada ou None se não houver
    """
    datas_disponiveis = df['DT_COMPTC']
    datas_anteriores = datas_disponiveis[datas_disponiveis <= data_alvo]
    
    if len(datas_anteriores) > 0:
        return datas_anteriores.idxmax()
    return None

# Função para ajustar período de análise
def ajustar_periodo_analise(df, data_inicial_str, data_final_str):
    """
    Ajusta as datas inicial e final para as datas disponíveis mais próximas
    Retorna um DataFrame filtrado e informações sobre os ajustes
    """
    # Converter strings de data para datetime
    data_inicial = datetime.strptime(data_inicial_str, '%Y%m%d')
    data_final = datetime.strptime(data_final_str, '%Y%m%d')
    
    # Buscar datas disponíveis
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
    
    # Filtrar DataFrame
    if idx_inicial is not None and idx_final is not None:
        df_filtrado = df.loc[idx_inicial:idx_final].copy()
        return df_filtrado, ajustes
    
    return df, ajustes

# Sidebar com inputs do usuário
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <img src='https://i.imgur.com/wHZ5Kpb.png' style='width: 180px; height: auto;'>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### ⚙️ Configurações")
st.sidebar.markdown("---")

# Input de CNPJ (vazio por padrão)
cnpj_input = st.sidebar.text_input(
    "CNPJ do Fundo",
    value="",
    placeholder="00.000.000/0000-00",
    help="Digite o CNPJ com ou sem formatação"
)

# Inputs de data (vazios por padrão)
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
        # Converte para exibição
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
def carregar_dados_api(cnpj, data_ini, data_fim):
    """
    Carrega dados da API com uma janela ampliada para garantir dados suficientes
    """
    # Amplia a janela de busca em 60 dias antes da data inicial
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

# Função para formatar valores em BRL
def format_brl(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Função para formatar percentual
def fmt_pct_port(x):
    return f"{x*100:.2f}%".replace('.', ',')

# Verificar se deve carregar os dados
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False

if carregar_button and cnpj_valido and datas_validas:
    st.session_state.dados_carregados = True
    st.session_state.cnpj = cnpj_limpo
    st.session_state.data_ini = data_inicial_formatada
    st.session_state.data_fim = data_final_formatada

if not st.session_state.dados_carregados:
    st.info("👈 Preencha os campos na barra lateral e clique em 'Carregar Dados' para começar a análise.")

    # Instruções de uso
    st.markdown("""
    ### 📋 Como usar:

    1. **CNPJ do Fundo**: Digite o CNPJ do fundo que deseja analisar (com ou sem formatação)
    2. **Data Inicial**: Digite a data inicial no formato DD/MM/AAAA (ex: 01/01/2020)
    3. **Data Final**: Digite a data final no formato DD/MM/AAAA (ex: 31/12/2024)
    4. Clique em **Carregar Dados** para visualizar as análises

    ---

    ### 📊 Análises disponíveis:
    - Rentabilidade histórica e CAGR
    - Análise de risco (Drawdown, Volatilidade, VaR)
    - Evolução patrimonial e captação
    - Perfil de cotistas
    - Retornos em janelas móveis
    
    ---
    
    ### ℹ️ Sobre datas:
    Se você informar uma data em que não há cota disponível (ex: finais de semana, feriados), 
    o sistema automaticamente utilizará a última cota disponível anterior à data informada.
    """)

    st.stop()

try:
    with st.spinner('🔄 Carregando dados...'):
        df_completo = carregar_dados_api(st.session_state.cnpj, st.session_state.data_ini, st.session_state.data_fim)
        
        # Ajustar período para usar datas disponíveis
        df, ajustes = ajustar_periodo_analise(df_completo, st.session_state.data_ini, st.session_state.data_fim)
        
        # Mostrar avisos se houve ajuste de datas
        if ajustes['houve_ajuste_inicial'] or ajustes['houve_ajuste_final']:
            avisos = []
            if ajustes['houve_ajuste_inicial']:
                avisos.append(f"**Data inicial ajustada:** {ajustes['data_inicial_original'].strftime('%d/%m/%Y')} → {ajustes['data_inicial_usada'].strftime('%d/%m/%Y')}")
            if ajustes['houve_ajuste_final']:
                avisos.append(f"**Data final ajustada:** {ajustes['data_final_original'].strftime('%d/%m/%Y')} → {ajustes['data_final_usada'].strftime('%d/%m/%Y')}")
            
            st.info("ℹ️ **Ajuste de período:**\n\n" + "\n\n".join(avisos) + "\n\n*As datas foram ajustadas para as cotas disponíveis mais próximas.*")

    # Preparação dos dados
    df = df.sort_values('DT_COMPTC').reset_index(drop=True)

    # NORMALIZAR RENTABILIDADE A PARTIR DA PRIMEIRA COTA DO PERÍODO
    primeira_cota = df['VL_QUOTA'].iloc[0]
    df['VL_QUOTA_NORM'] = ((df['VL_QUOTA'] / primeira_cota) - 1) * 100

    # Calcular métricas principais
    df['Max_VL_QUOTA'] = df['VL_QUOTA'].cummax()
    df['Drawdown'] = (df['VL_QUOTA'] / df['Max_VL_QUOTA'] - 1) * 100
    df['Captacao_Liquida'] = df['CAPTC_DIA'] - df['RESG_DIA']
    df['Soma_Acumulada'] = df['Captacao_Liquida'].cumsum()
    df['Patrimonio_Liq_Medio'] = df['VL_PATRIM_LIQ'] / df['NR_COTST']

    # Volatilidade
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
    df_cagr['CAGR'] = ((end_value / df_cagr['VL_QUOTA']) ** (252 / df_cagr['dias_uteis'])) - 1
    df_cagr['CAGR'] = df_cagr['CAGR'] * 100
    mean_cagr = df_cagr['CAGR'].mean()

    # Retorno 21 dias para VaR
    df['Retorno_21d'] = df['VL_QUOTA'].pct_change(21)
    df_plot = df.dropna(subset=['Retorno_21d']).copy()
    VaR_95 = np.percentile(df_plot['Retorno_21d'], 5)
    VaR_99 = np.percentile(df_plot['Retorno_21d'], 1)
    ES_95 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_95, 'Retorno_21d'].mean()
    ES_99 = df_plot.loc[df_plot['Retorno_21d'] <= VaR_99, 'Retorno_21d'].mean()

    # Cards com métricas principais
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

    # Tabs para organizar os gráficos
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Rentabilidade", 
        "📉 Risco", 
        "💰 Patrimônio", 
        "👥 Cotistas",
        "🎯 Janelas Móveis"
    ])

    # Configuração de cores para os gráficos
    color_primary = '#1a5f3f'
    color_secondary = '#f0b429'
    color_danger = '#dc3545'

    with tab1:
        st.subheader("📈 Rentabilidade Histórica")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df['DT_COMPTC'],
            y=df['VL_QUOTA_NORM'],
            mode='lines',
            line=dict(color=color_primary, width=2.5),
            fill='tozeroy',
            fillcolor=f'rgba(26, 95, 63, 0.1)',
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
        
        fig1 = adicionar_logo_grafico(fig1)
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
        
        fig2 = adicionar_logo_grafico(fig2)
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
            fillcolor='rgba(220, 53, 69, 0.1)',
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
        
        fig3 = adicionar_logo_grafico(fig3)
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
        
        fig4 = adicionar_logo_grafico(fig4)
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
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[VaR_99 * 100, VaR_99 * 100],
            mode='lines',
            name='VaR 99%',
            line=dict(dash='dot', color='red', width=2)
        ))
        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
            y=[ES_95 * 100, ES_95 * 100],
            mode='lines',
            name='ES 95%',
            line=dict(dash='dash', color='orange', width=2)
        ))
        fig5.add_trace(go.Scatter(
            x=[df_plot['DT_COMPTC'].min(), df_plot['DT_COMPTC'].max()],
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
        
        fig5 = adicionar_logo_grafico(fig5)
        st.plotly_chart(fig5, use_container_width=True)

        st.info(f"""
        **Este gráfico mostra que, em um período de 1 mês:**

        • Há **99%** de confiança de que o fundo não cairá mais do que **{fmt_pct_port(VaR_99)} (VaR)**, 
        e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_99)} (ES)**.

        • Há **95%** de confiança de que a queda não será superior a **{fmt_pct_port(VaR_95)} (VaR)**, 
        e, caso isso ocorra, a perda média esperada será de **{fmt_pct_port(ES_95)} (ES)**.
        """)

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
        
        fig6 = adicionar_logo_grafico(fig6)
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
        
        fig7 = adicionar_logo_grafico(fig7)
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
        
        fig8 = adicionar_logo_grafico(fig8)
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
            df_returns[nome] = df_returns['VL_QUOTA'] / df_returns['VL_QUOTA'].shift(dias) - 1

        janela_selecionada = st.selectbox("Selecione o período:", list(janelas.keys()))

        if not df_returns[janela_selecionada].dropna().empty:
            fig9 = go.Figure()
            fig9.add_trace(go.Scatter(
                x=df_returns['DT_COMPTC'],
                y=df_returns[janela_selecionada],
                mode='lines',
                name=f"Retorno — {janela_selecionada}",
                line=dict(width=2.5, color=color_primary),
                fill='tozeroy',
                fillcolor=f'rgba(26, 95, 63, 0.1)',
                hovertemplate="Data: %{x|%d/%m/%Y}<br>Retorno: %{y:.2%}<extra></extra>"
            ))

            fig9.update_layout(
                xaxis_title="Data",
                yaxis_title="Retorno (%)",
                template="plotly_white",
                hovermode="x unified",
                height=500,
                yaxis=dict(tickformat=".2%"),
                font=dict(family="Inter, sans-serif")
            )
            
            fig9 = adicionar_logo_grafico(fig9)
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning(f"⚠️ Não há dados suficientes para calcular {janela_selecionada}.")

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
        Análise de Fundos de Investimentos • 2025
    </p>
</div>
""", unsafe_allow_html=True)
