import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
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

INSTITUTIONAL_ORANGE = "#F94E03"
INSTITUTIONAL_LIGHT = "#E0E0DA"
INSTITUTIONAL_ORANGE_LIGHT = "#FB7B3D"

INSTITUTIONAL_STYLES = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    * {{
        font-family: 'Montserrat', sans-serif !important;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #0B1437 0%, #1A1F37 50%, #111C44 100%);
    }}
    
    .main-header {{
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }}
    
    .main-header h1 {{
        color: white;
        font-weight: 700;
        margin: 0;
        font-size: 2.5rem;
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
    }}
    
    .campaign-selector {{
        background: {INSTITUTIONAL_LIGHT};
        padding: 3rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin: 2rem 0;
    }}
    
    .campaign-selector h2 {{
        color: #1A1A1A;
        font-weight: 700;
        margin-bottom: 2rem;
    }}
    
    .glass-card {{
        background: linear-gradient(127deg, rgba(6, 11, 40, 0.94) 0%, rgba(10, 14, 35, 0.69) 100%);
        backdrop-filter: blur(120px);
        border: 1.5px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }}
    
    .glass-card h3 {{
        color: #FFFFFF;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    
    .glass-card .metric-value {{
        color: {INSTITUTIONAL_ORANGE};
        font-size: 2.5rem;
        font-weight: 700;
    }}
    
    .glass-card .metric-label {{
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
        padding: 0.75rem 1.5rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%) !important;
    }}
    
    .stButton > button {{
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(249, 78, 3, 0.4);
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
        color: {INSTITUTIONAL_ORANGE};
    }}
    
    .stSelectbox label, .stMultiSelect label {{
        color: white !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
    }}
    
    p, span, label {{
        color: rgba(255, 255, 255, 0.9);
    }}
    
    .element-container {{
        color: white;
    }}
    
    .data-table {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
    }}
    
    .status-connected {{
        color: #10B981;
        font-weight: 600;
    }}
    
    .status-disconnected {{
        color: #EF4444;
        font-weight: 600;
    }}
</style>
"""

LIGHT_THEME_STYLES = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    * {{
        font-family: 'Montserrat', sans-serif !important;
    }}
    
    .stApp {{
        background: {INSTITUTIONAL_LIGHT};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: #1A1A1A !important;
    }}
    
    p, span, label {{
        color: #4A5568;
    }}
    
    .main-header {{
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }}
    
    .main-header h1 {{
        color: white !important;
        font-weight: 700;
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.9);
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: #F1F5F9;
        border-radius: 8px;
        color: #4A5568;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%) !important;
        color: white !important;
    }}
    
    .stButton > button {{
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%);
        color: white;
        border: none;
        border-radius: 12px;
    }}
    
    div[data-testid="stMetricValue"] {{
        color: {INSTITUTIONAL_ORANGE};
    }}
    
    .light-card {{
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }}
    
    .light-card .metric-value {{
        color: {INSTITUTIONAL_ORANGE};
        font-size: 2.5rem;
        font-weight: 700;
    }}
    
    .light-card .metric-label {{
        color: #6B7280;
        font-size: 0.9rem;
    }}
</style>
"""

def init_session_state():
    if 'selected_campaign' not in st.session_state:
        st.session_state.selected_campaign = None
    if 'hotmart_client' not in st.session_state:
        st.session_state.hotmart_client = HotmartClient()
    if 'manychat_client' not in st.session_state:
        st.session_state.manychat_client = ManyChatClient()
    if 'meta_ads_client' not in st.session_state:
        st.session_state.meta_ads_client = MetaAdsClient()
    if 'sheets_client' not in st.session_state:
        st.session_state.sheets_client = GoogleSheetClient()
    if 'imersao_sheets_client' not in st.session_state:
        st.session_state.imersao_sheets_client = ImersaoSheetClient()

def check_secrets_status():
    secrets = {
        'HOTMART_BASIC_TOKEN': bool(os.environ.get('HOTMART_BASIC_TOKEN')),
        'MANYCHAT_API_TOKEN': bool(os.environ.get('MANYCHAT_API_TOKEN')),
        'META_ACCESS_TOKEN': bool(os.environ.get('META_ACCESS_TOKEN')),
        'META_AD_ACCOUNT_ID': bool(os.environ.get('META_AD_ACCOUNT_ID')),
        'GOOGLE_SPREADSHEET_ID': bool(os.environ.get('GOOGLE_SPREADSHEET_ID'))
    }
    return secrets

def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def render_campaign_selector():
    st.markdown(INSTITUTIONAL_STYLES, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="main-header">
            <h1>Dashboard Multi-Campanhas</h1>
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
                    f"{campaign['name']}",
                    key=f"btn_{campaign_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_campaign = campaign_id
                    st.rerun()
                
                period_start = campaign['period_start'].strftime('%d/%m/%Y')
                period_end = campaign['period_end'].strftime('%d/%m/%Y')
                st.caption(f"{period_start} - {period_end}")
    
    st.markdown("---")
    st.subheader("Status das Integrações")
    
    secrets = check_secrets_status()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status = "Conectado" if secrets['HOTMART_BASIC_TOKEN'] else "Não configurado"
        color = "#10B981" if secrets['HOTMART_BASIC_TOKEN'] else "#EF4444"
        st.markdown(f"**Hotmart API**")
        st.markdown(f"<span style='color: {color}'>{status}</span>", unsafe_allow_html=True)
    
    with col2:
        status = "Conectado" if secrets['MANYCHAT_API_TOKEN'] else "Não configurado"
        color = "#10B981" if secrets['MANYCHAT_API_TOKEN'] else "#EF4444"
        st.markdown(f"**ManyChat API**")
        st.markdown(f"<span style='color: {color}'>{status}</span>", unsafe_allow_html=True)
    
    with col3:
        status = "Conectado" if secrets['META_ACCESS_TOKEN'] and secrets['META_AD_ACCOUNT_ID'] else "Não configurado"
        color = "#10B981" if secrets['META_ACCESS_TOKEN'] and secrets['META_AD_ACCOUNT_ID'] else "#EF4444"
        st.markdown(f"**Meta Ads API**")
        st.markdown(f"<span style='color: {color}'>{status}</span>", unsafe_allow_html=True)
    
    with col4:
        status = "Conectado" if secrets['GOOGLE_SPREADSHEET_ID'] else "Não configurado"
        color = "#10B981" if secrets['GOOGLE_SPREADSHEET_ID'] else "#EF4444"
        st.markdown(f"**Google Sheets**")
        st.markdown(f"<span style='color: {color}'>{status}</span>", unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"**Hora Atual (BRT)**")
        st.markdown(f"{datetime.now(BRT).strftime('%d/%m/%Y %H:%M')}")

def render_bf25_dashboard():
    st.markdown(LIGHT_THEME_STYLES, unsafe_allow_html=True)
    
    config = get_campaign_config('bf25')
    secrets = check_secrets_status()
    
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("Voltar", key="back_bf25"):
            st.session_state.selected_campaign = None
            st.rerun()
    
    st.markdown(f"""
        <div class="main-header">
            <h1>{config['name']}</h1>
            <p>Dashboard de Acompanhamento</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(config['tabs'])
    
    with tabs[0]:
        render_bf25_captacao(secrets)
    
    with tabs[1]:
        render_bf25_vendas(config, secrets)
    
    with tabs[2]:
        render_bf25_comparar(config, secrets)
    
    with tabs[3]:
        render_bf25_origem_leads(secrets)
    
    with tabs[4]:
        render_bf25_pesquisa(secrets)
    
    with tabs[5]:
        render_bf25_investimentos()
    
    with tabs[6]:
        render_bf25_meta_ads(config, secrets)
    
    with tabs[7]:
        render_bf25_zapzap(secrets)
    
    with tabs[8]:
        render_bf25_dados(config, secrets)
    
    with tabs[9]:
        render_bf25_metas(config)
    
    with tabs[10]:
        render_bf25_planejamento()

def render_bf25_captacao(secrets):
    st.subheader("Visão da Captação")
    
    if secrets['GOOGLE_SPREADSHEET_ID']:
        try:
            client = st.session_state.sheets_client
            leads_alunos = client.get_leads_alunos()
            leads_geral = client.get_leads_geral()
            
            total_alunos = len(leads_alunos) - 1 if len(leads_alunos) > 1 else 0
            total_geral = len(leads_geral) - 1 if len(leads_geral) > 1 else 0
            total_leads = total_alunos + total_geral
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Leads", f"{total_leads:,}")
            with col2:
                st.metric("Leads Alunos", f"{total_alunos:,}")
            with col3:
                st.metric("Leads Geral", f"{total_geral:,}")
            with col4:
                conversion_rate = 0
                st.metric("Taxa de Conversão", f"{conversion_rate:.1f}%")
            
            if total_leads > 0:
                import plotly.graph_objects as go
                fig = go.Figure(data=[go.Pie(
                    labels=['Alunos EA', 'Público Geral'],
                    values=[total_alunos, total_geral],
                    hole=.4,
                    marker_colors=[INSTITUTIONAL_ORANGE, INSTITUTIONAL_ORANGE_LIGHT]
                )])
                fig.update_layout(
                    title="Distribuição de Leads",
                    font=dict(family="Montserrat")
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Erro ao carregar dados do Google Sheets: {e}")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Leads", "---")
        with col2:
            st.metric("Leads Alunos", "---")
        with col3:
            st.metric("Leads Geral", "---")
        with col4:
            st.metric("Taxa de Conversão", "---")
        
        st.info("Configure o GOOGLE_SPREADSHEET_ID nos Secrets para visualizar os dados de captação.")

def render_bf25_vendas(config, secrets):
    st.subheader("Vendas")
    
    if secrets['HOTMART_BASIC_TOKEN']:
        try:
            client = st.session_state.hotmart_client
            product_id = config['hotmart']['product_id']
            start_date = config['period_start']
            end_date = min(config['period_end'], datetime.now(BRT))
            
            with st.spinner("Carregando vendas da Hotmart..."):
                sales = client.get_approved_sales(product_id, start_date, end_date)
                refunds = client.get_refunded_sales(product_id, start_date, end_date)
            
            df_sales = process_hotmart_sales(sales)
            metrics = calculate_sales_metrics(df_sales)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Vendas", f"{metrics['total_sales']:,}")
            with col2:
                st.metric("Faturamento", format_currency(metrics['total_revenue']))
            with col3:
                st.metric("Ticket Médio", format_currency(metrics['average_ticket']))
            with col4:
                st.metric("Reembolsos", f"{len(refunds):,}")
            
            if not df_sales.empty:
                grouped = group_sales_by_date(df_sales)
                if not grouped.empty:
                    fig = create_sales_line_chart(grouped, INSTITUTIONAL_ORANGE, INSTITUTIONAL_ORANGE_LIGHT)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    fig2 = create_revenue_bar_chart(grouped, INSTITUTIONAL_ORANGE)
                    st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Erro ao carregar vendas: {e}")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Vendas", "---")
        with col2:
            st.metric("Faturamento", "---")
        with col3:
            st.metric("Ticket Médio", "---")
        with col4:
            st.metric("Reembolsos", "---")
        
        st.info("Configure o HOTMART_BASIC_TOKEN nos Secrets para visualizar as vendas.")

def render_bf25_comparar(config, secrets):
    st.subheader("Comparar Períodos")
    
    col1, col2 = st.columns(2)
    with col1:
        period1 = st.selectbox("Período 1", ["Semana 1", "Semana 2", "Semana 3", "Semana 4"], key="period1")
    with col2:
        period2 = st.selectbox("Período 2", ["Semana 1", "Semana 2", "Semana 3", "Semana 4"], index=1, key="period2")
    
    st.info("A comparação será exibida quando os dados estiverem disponíveis.")

def render_bf25_origem_leads(secrets):
    st.subheader("Origem dos Leads")
    
    if secrets['GOOGLE_SPREADSHEET_ID']:
        st.info("Análise de origem dos leads será exibida com base nos dados do Google Sheets.")
    else:
        st.info("Configure o GOOGLE_SPREADSHEET_ID nos Secrets para visualizar a origem dos leads.")

def render_bf25_pesquisa(secrets):
    st.subheader("Pesquisa")
    
    if secrets['GOOGLE_SPREADSHEET_ID']:
        try:
            client = st.session_state.sheets_client
            pesquisa_alunos = client.get_pesquisa_alunos()
            pesquisa_geral = client.get_pesquisa_geral()
            
            total_alunos = len(pesquisa_alunos) - 1 if len(pesquisa_alunos) > 1 else 0
            total_geral = len(pesquisa_geral) - 1 if len(pesquisa_geral) > 1 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Respostas Alunos", f"{total_alunos:,}")
            with col2:
                st.metric("Respostas Geral", f"{total_geral:,}")
            with col3:
                st.metric("Total Respostas", f"{total_alunos + total_geral:,}")
        except Exception as e:
            st.warning(f"Erro ao carregar pesquisa: {e}")
    else:
        st.info("Configure o GOOGLE_SPREADSHEET_ID nos Secrets para visualizar as pesquisas.")

def render_bf25_investimentos():
    st.subheader("Investimentos Extras")
    st.info("Registre aqui investimentos adicionais da campanha.")
    
    with st.expander("Adicionar Investimento"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Descrição", key="inv_desc")
        with col2:
            st.number_input("Valor (R$)", min_value=0.0, key="inv_valor")
        with col3:
            st.date_input("Data", key="inv_data")

def render_bf25_meta_ads(config, secrets):
    st.subheader("Meta Ads")
    
    if secrets['META_ACCESS_TOKEN'] and secrets['META_AD_ACCOUNT_ID']:
        try:
            client = st.session_state.meta_ads_client
            start_date = config['period_start']
            end_date = min(config['period_end'], datetime.now(BRT))
            
            with st.spinner("Carregando dados do Meta Ads..."):
                metrics = client.get_bf25_metrics(start_date, end_date)
            
            impressions = int(metrics.get('impressions', 0))
            clicks = int(metrics.get('clicks', 0))
            ctr = float(metrics.get('inline_link_click_ctr', 0))
            spend = float(metrics.get('spend', 0))
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Impressões", f"{impressions:,}")
            with col2:
                st.metric("Cliques", f"{clicks:,}")
            with col3:
                st.metric("CTR", f"{ctr:.2f}%")
            with col4:
                st.metric("Gasto", format_currency(spend))
        except Exception as e:
            st.warning(f"Erro ao carregar Meta Ads: {e}")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Impressões", "---")
        with col2:
            st.metric("Cliques", "---")
        with col3:
            st.metric("CTR", "---")
        with col4:
            st.metric("Gasto", "---")
        
        st.info("Configure o META_ACCESS_TOKEN e META_AD_ACCOUNT_ID nos Secrets.")

def render_bf25_zapzap(secrets):
    st.subheader("API Oficial do ZapZap (ManyChat)")
    
    if secrets['MANYCHAT_API_TOKEN']:
        try:
            client = st.session_state.manychat_client
            
            with st.spinner("Carregando métricas do ManyChat..."):
                metrics = client.get_bf25_metrics()
            
            st.markdown("### Alunos EA")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Boas-vindas Recebeu", f"{metrics.get('alunos_boas_vindas_recebeu', 0):,}")
            with col2:
                st.metric("Boas-vindas Clicou", f"{metrics.get('alunos_boas_vindas_clicou', 0):,}")
            
            st.markdown("### Público Geral")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Boas-vindas Recebeu", f"{metrics.get('geral_boas_vindas_recebeu', 0):,}")
            with col2:
                st.metric("Boas-vindas Clicou", f"{metrics.get('geral_boas_vindas_clicou', 0):,}")
            with col3:
                st.metric("Fluxo Instagram", f"{metrics.get('geral_fluxo_instagram', 0):,}")
        except Exception as e:
            st.warning(f"Erro ao carregar ManyChat: {e}")
    else:
        st.info("Configure o MANYCHAT_API_TOKEN nos Secrets para visualizar as métricas.")

def render_bf25_dados(config, secrets):
    st.subheader("Dados Brutos")
    
    if secrets['HOTMART_BASIC_TOKEN']:
        try:
            client = st.session_state.hotmart_client
            product_id = config['hotmart']['product_id']
            start_date = config['period_start']
            end_date = min(config['period_end'], datetime.now(BRT))
            
            sales = client.get_approved_sales(product_id, start_date, end_date)
            df = process_hotmart_sales(sales)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Exportar CSV",
                    data=csv,
                    file_name=f"vendas_bf25_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.warning(f"Erro ao carregar dados: {e}")
    else:
        st.info("Configure o HOTMART_BASIC_TOKEN nos Secrets para visualizar os dados.")

def render_bf25_metas(config):
    st.subheader("Metas da Campanha")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        meta_vendas = st.number_input("Meta de Vendas", min_value=0, value=1000, key="meta_vendas")
        st.progress(0, text="0% da meta")
    
    with col2:
        meta_faturamento = st.number_input("Meta de Faturamento (R$)", min_value=0, value=500000, key="meta_fat")
        st.progress(0, text="0% da meta")
    
    with col3:
        meta_leads = st.number_input("Meta de Leads", min_value=0, value=5000, key="meta_leads")
        st.progress(0, text="0% da meta")

def render_bf25_planejamento():
    st.subheader("Planejamento 2025")
    
    st.markdown("""
    ### Cronograma da Campanha
    
    | Fase | Período | Descrição |
    |------|---------|-----------|
    | Aquecimento | 06/11 - 15/11 | Conteúdo de valor e engajamento |
    | Pré-lançamento | 16/11 - 24/11 | Contagem regressiva e antecipação |
    | Abertura | 25/11 - 30/11 | Vendas abertas - Black Friday |
    | Encerramento | 01/12 - 08/12 | Últimas vagas e escassez |
    """)

def render_imersao_dashboard():
    st.markdown(INSTITUTIONAL_STYLES, unsafe_allow_html=True)
    
    config = get_campaign_config('imersao0126')
    secrets = check_secrets_status()
    
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button("Voltar", key="back_imersao"):
            st.session_state.selected_campaign = None
            st.rerun()
    
    st.markdown(f"""
        <div class="main-header">
            <h1>{config['name']}</h1>
            <p>Dashboard de Acompanhamento</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(config['tabs'])
    
    with tabs[0]:
        render_imersao_vendas(config, secrets)
    
    with tabs[1]:
        render_imersao_reembolsos(config, secrets)
    
    with tabs[2]:
        render_imersao_pesquisa_tab()
    
    with tabs[3]:
        render_imersao_monitoramento()

def render_imersao_vendas(config, secrets):
    st.subheader("Vendas")
    
    if secrets['HOTMART_BASIC_TOKEN']:
        try:
            client = st.session_state.hotmart_client
            ingresso_id = config['hotmart']['ingresso']['product_id']
            orderbump_id = config['hotmart']['orderbump']['product_id']
            start_date = config['period_start']
            end_date = min(config['period_end'], datetime.now(BRT))
            
            with st.spinner("Carregando vendas da Hotmart..."):
                ingressos = client.get_approved_sales(ingresso_id, start_date, end_date)
                orderbumps = client.get_approved_sales(orderbump_id, start_date, end_date)
            
            df_ingressos = process_hotmart_sales(ingressos)
            df_orderbumps = process_hotmart_sales(orderbumps)
            
            metrics_ing = calculate_sales_metrics(df_ingressos)
            metrics_ord = calculate_sales_metrics(df_orderbumps)
            
            total_revenue = metrics_ing['total_revenue'] + metrics_ord['total_revenue']
            total_sales = metrics_ing['total_sales'] + metrics_ord['total_sales']
            avg_ticket = total_revenue / total_sales if total_sales > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Total de Ingressos</div>
                        <div class="metric-value">{metrics_ing['total_sales']:,}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Orderbumps</div>
                        <div class="metric-value">{metrics_ord['total_sales']:,}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Faturamento Total</div>
                        <div class="metric-value">{format_currency(total_revenue)}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Ticket Médio</div>
                        <div class="metric-value">{format_currency(avg_ticket)}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            if not df_ingressos.empty:
                grouped = group_sales_by_date(df_ingressos)
                if not grouped.empty:
                    fig = create_sales_line_chart(grouped, INSTITUTIONAL_ORANGE, INSTITUTIONAL_ORANGE_LIGHT)
                    fig = create_dark_theme_chart(fig)
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Erro ao carregar vendas: {e}")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
                <div class="glass-card">
                    <div class="metric-label">Total de Ingressos</div>
                    <div class="metric-value">---</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="glass-card">
                    <div class="metric-label">Orderbumps</div>
                    <div class="metric-value">---</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="glass-card">
                    <div class="metric-label">Faturamento Total</div>
                    <div class="metric-value">---</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
                <div class="glass-card">
                    <div class="metric-label">Ticket Médio</div>
                    <div class="metric-value">---</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.info("Configure o HOTMART_BASIC_TOKEN nos Secrets para visualizar as vendas.")

def render_imersao_reembolsos(config, secrets):
    st.subheader("Reembolsos")
    
    if secrets['HOTMART_BASIC_TOKEN']:
        try:
            client = st.session_state.hotmart_client
            ingresso_id = config['hotmart']['ingresso']['product_id']
            start_date = config['period_start']
            end_date = min(config['period_end'], datetime.now(BRT))
            
            with st.spinner("Carregando reembolsos..."):
                refunds = client.get_refunded_sales(ingresso_id, start_date, end_date)
            
            df_refunds = process_hotmart_sales(refunds)
            metrics = calculate_sales_metrics(df_refunds)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Total de Reembolsos</div>
                        <div class="metric-value">{metrics['total_sales']:,}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Valor Reembolsado</div>
                        <div class="metric-value">{format_currency(metrics['total_revenue'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                    <div class="glass-card">
                        <div class="metric-label">Taxa de Reembolso</div>
                        <div class="metric-value">0%</div>
                    </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Erro ao carregar reembolsos: {e}")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="glass-card">
                    <div class="metric-label">Total de Reembolsos</div>
                    <div class="metric-value">---</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="glass-card">
                    <div class="metric-label">Valor Reembolsado</div>
                    <div class="metric-value">---</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="glass-card">
                    <div class="metric-label">Taxa de Reembolso</div>
                    <div class="metric-value">---</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.info("Configure o HOTMART_BASIC_TOKEN nos Secrets para visualizar os reembolsos.")

def render_imersao_pesquisa_tab():
    st.subheader("Pesquisa")
    
    try:
        client = st.session_state.imersao_sheets_client
        pesquisa = client.get_pesquisa()
        
        total = len(pesquisa) - 1 if len(pesquisa) > 1 else 0
        
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Total de Respostas</div>
                <div class="metric-value">{total:,}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if total > 0:
            df = process_sheets_data(pesquisa)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.info("Dados da pesquisa serão exibidos quando disponíveis.")

def render_imersao_monitoramento():
    st.subheader("Monitoramento de Grupos")
    
    try:
        client = st.session_state.imersao_sheets_client
        grupos = client.get_monitoramento_grupos()
        
        total = len(grupos) - 1 if len(grupos) > 1 else 0
        
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Entradas nos Grupos</div>
                <div class="metric-value">{total:,}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if total > 0:
            df = process_sheets_data(grupos)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.info("Dados de monitoramento serão exibidos quando disponíveis.")

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
