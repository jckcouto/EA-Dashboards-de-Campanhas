import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from campaigns.config import CAMPAIGNS, get_campaign_config, BRT
from server.hotmart_client import HotmartClient
from server.manychat_client import ManyChatClient
from server.meta_ads_client import MetaAdsClient
from server.google_sheet_client import GoogleSheetClient, ImersaoSheetClient
from utils.data_processor import process_hotmart_sales, calculate_sales_metrics, process_sheets_data, group_sales_by_date
from utils.chart_helpers import create_sales_line_chart, create_revenue_bar_chart, create_dark_theme_chart

st.set_page_config(
    page_title="Dashboard Multi-Campanhas | Escola de Automação e I.A",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

INSTITUTIONAL_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0B1437 0%, #1A1F37 50%, #111C44 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #F94E03 0%, #FB7B3D 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-weight: 700;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
    }
    
    .campaign-selector {
        background: linear-gradient(135deg, #F97316 0%, #FB923C 30%, #FDBA74 60%, #FED7AA 100%);
        padding: 3rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .campaign-selector h2 {
        color: #1A1A1A;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    
    .campaign-btn {
        background: linear-gradient(135deg, #7C3AED 0%, #6366F1 50%, #8B5CF6 100%);
        color: white;
        padding: 1.5rem 3rem;
        border-radius: 16px;
        border: none;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.4);
        transition: all 0.3s ease;
        margin: 0.5rem;
    }
    
    .campaign-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(124, 58, 237, 0.6);
    }
    
    .glass-card {
        background: linear-gradient(127deg, rgba(6, 11, 40, 0.94) 0%, rgba(10, 14, 35, 0.69) 100%);
        backdrop-filter: blur(120px);
        border: 1.5px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .glass-card h3 {
        color: #FFFFFF;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .glass-card .metric-value {
        color: #F94E03;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .glass-card .metric-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
    }
    
    .light-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    .light-card h3 {
        color: #1A1A1A;
        font-weight: 600;
    }
    
    .light-card .metric-value {
        color: #4A90E2;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .tab-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #F94E03 0%, #FB7B3D 100%) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #F94E03 0%, #FB7B3D 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(249, 78, 3, 0.4);
    }
    
    .back-btn {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .stSelectbox label, .stMultiSelect label {
        color: white !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    p, span, label {
        color: rgba(255, 255, 255, 0.9);
    }
    
    .element-container {
        color: white;
    }
</style>
"""

LIGHT_THEME_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #1A1A1A !important;
    }
    
    p, span, label {
        color: #4A5568;
    }
    
    .main-header {
        background: linear-gradient(135deg, #4A90E2 0%, #5BA3F5 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white !important;
        font-weight: 700;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #F1F5F9;
        border-radius: 8px;
        color: #4A5568;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4A90E2 0%, #5BA3F5 100%) !important;
        color: white !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4A90E2 0%, #5BA3F5 100%);
        color: white;
        border: none;
        border-radius: 12px;
    }
    
    div[data-testid="stMetricValue"] {
        color: #4A90E2;
    }
</style>
"""

def init_session_state():
    if 'selected_campaign' not in st.session_state:
        st.session_state.selected_campaign = None
    if 'cached_data' not in st.session_state:
        st.session_state.cached_data = {}
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None

def render_campaign_selector():
    st.markdown(INSTITUTIONAL_STYLES, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="main-header">
            <h1>🚀 Dashboard Multi-Campanhas</h1>
            <p>Escola de Automação e I.A</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="campaign-selector">
            <h2>Selecione uma Campanha</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        cols = st.columns(len(CAMPAIGNS))
        
        for idx, (campaign_id, campaign) in enumerate(CAMPAIGNS.items()):
            with cols[idx]:
                if st.button(
                    f"📊 {campaign['name']}",
                    key=f"btn_{campaign_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_campaign = campaign_id
                    st.rerun()
                
                period_start = campaign['period_start'].strftime('%d/%m/%Y')
                period_end = campaign['period_end'].strftime('%d/%m/%Y')
                st.caption(f"📅 {period_start} - {period_end}")

def render_metric_card(title: str, value: str, subtitle: str = "", theme: str = "dark"):
    card_class = "glass-card" if theme == "dark" else "light-card"
    
    st.markdown(f"""
        <div class="{card_class}">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

def render_bf25_dashboard():
    st.markdown(LIGHT_THEME_STYLES, unsafe_allow_html=True)
    
    config = get_campaign_config('bf25')
    
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("← Voltar", key="back_bf25"):
            st.session_state.selected_campaign = None
            st.rerun()
    
    st.markdown(f"""
        <div class="main-header">
            <h1>📊 {config['name']}</h1>
            <p>Dashboard de Acompanhamento</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(config['tabs'])
    
    with tabs[0]:
        render_bf25_captacao()
    
    with tabs[1]:
        render_bf25_vendas()
    
    with tabs[2]:
        render_bf25_comparar()
    
    with tabs[3]:
        render_bf25_origem_leads()
    
    with tabs[4]:
        render_bf25_pesquisa()
    
    with tabs[5]:
        render_bf25_investimentos()
    
    with tabs[6]:
        render_bf25_meta_ads()
    
    with tabs[7]:
        render_bf25_zapzap()
    
    with tabs[8]:
        render_bf25_dados()
    
    with tabs[9]:
        render_bf25_metas()
    
    with tabs[10]:
        render_bf25_planejamento()

def render_bf25_captacao():
    st.subheader("📈 Visão da Captação")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Leads", "0", help="Leads captados na campanha")
    with col2:
        st.metric("Leads Alunos", "0", help="Leads de alunos existentes")
    with col3:
        st.metric("Leads Geral", "0", help="Leads do público geral")
    with col4:
        st.metric("Taxa de Conversão", "0%", help="Leads que viraram compradores")
    
    st.info("🔗 Conecte o Google Sheets para visualizar os dados de captação.")

def render_bf25_vendas():
    st.subheader("💰 Vendas")
    
    config = get_campaign_config('bf25')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Vendas", "0")
    with col2:
        st.metric("Faturamento", "R$ 0,00")
    with col3:
        st.metric("Ticket Médio", "R$ 0,00")
    with col4:
        st.metric("Reembolsos", "0")
    
    st.info("🔗 Configure o HOTMART_BASIC_TOKEN nos Secrets para visualizar as vendas.")

def render_bf25_comparar():
    st.subheader("📊 Comparar")
    st.info("Compare o desempenho entre diferentes períodos ou campanhas.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Período 1", ["Semana 1", "Semana 2", "Semana 3", "Semana 4"])
    with col2:
        st.selectbox("Período 2", ["Semana 1", "Semana 2", "Semana 3", "Semana 4"])

def render_bf25_origem_leads():
    st.subheader("🎯 Origem dos Leads")
    st.info("Visualize de onde estão vindo seus leads.")

def render_bf25_pesquisa():
    st.subheader("📋 Pesquisa")
    st.info("Resultados das pesquisas realizadas com os leads.")

def render_bf25_investimentos():
    st.subheader("💵 Investimentos Extras")
    st.info("Acompanhe os investimentos adicionais da campanha.")

def render_bf25_meta_ads():
    st.subheader("📱 Meta Ads")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Impressões", "0")
    with col2:
        st.metric("Cliques", "0")
    with col3:
        st.metric("CTR", "0%")
    with col4:
        st.metric("Gasto", "R$ 0,00")
    
    st.info("🔗 Configure o META_ACCESS_TOKEN e META_AD_ACCOUNT_ID nos Secrets.")

def render_bf25_zapzap():
    st.subheader("📲 API Oficial do ZapZap")
    st.info("Métricas do ManyChat - Configure o MANYCHAT_API_TOKEN nos Secrets.")

def render_bf25_dados():
    st.subheader("📑 Dados")
    st.info("Visualize e exporte os dados brutos da campanha.")

def render_bf25_metas():
    st.subheader("🎯 Metas")
    st.info("Defina e acompanhe as metas da campanha.")

def render_bf25_planejamento():
    st.subheader("📅 Planejamento 2025")
    st.info("Planejamento estratégico para 2025.")

def render_imersao_dashboard():
    st.markdown(INSTITUTIONAL_STYLES, unsafe_allow_html=True)
    
    config = get_campaign_config('imersao0126')
    
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("← Voltar", key="back_imersao"):
            st.session_state.selected_campaign = None
            st.rerun()
    
    st.markdown(f"""
        <div class="main-header">
            <h1>🎓 {config['name']}</h1>
            <p>Dashboard de Acompanhamento</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(config['tabs'])
    
    with tabs[0]:
        render_imersao_vendas()
    
    with tabs[1]:
        render_imersao_reembolsos()
    
    with tabs[2]:
        render_imersao_pesquisa()
    
    with tabs[3]:
        render_imersao_monitoramento()

def render_imersao_vendas():
    st.subheader("💰 Vendas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Total de Ingressos</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Orderbumps</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Faturamento Total</div>
                <div class="metric-value">R$ 0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Ticket Médio</div>
                <div class="metric-value">R$ 0</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("🔗 Configure o HOTMART_BASIC_TOKEN nos Secrets para visualizar as vendas.")

def render_imersao_reembolsos():
    st.subheader("↩️ Reembolsos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Total de Reembolsos</div>
                <div class="metric-value">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Valor Reembolsado</div>
                <div class="metric-value">R$ 0</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Taxa de Reembolso</div>
                <div class="metric-value">0%</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("🔗 Configure o HOTMART_BASIC_TOKEN nos Secrets para visualizar os reembolsos.")

def render_imersao_pesquisa():
    st.subheader("📋 Pesquisa")
    st.info("Resultados das pesquisas realizadas com os participantes da imersão.")

def render_imersao_monitoramento():
    st.subheader("👥 Monitoramento de Grupos")
    st.info("Acompanhe a entrada nos grupos da imersão.")

def main():
    init_session_state()
    
    if st.session_state.selected_campaign is None:
        render_campaign_selector()
    elif st.session_state.selected_campaign == 'bf25':
        render_bf25_dashboard()
    elif st.session_state.selected_campaign == 'imersao0126':
        render_imersao_dashboard()

if __name__ == "__main__":
    main()
