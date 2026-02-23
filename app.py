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
from server.google_sheet_client import GoogleSheetClient, ImersaoSheetClient, DesafioSheetClient
from utils.data_processor import process_hotmart_sales, calculate_sales_metrics, process_sheets_data, group_sales_by_date
from utils.chart_helpers import create_sales_line_chart, create_revenue_bar_chart, create_dark_theme_chart

st.set_page_config(
    page_title="Dashboard Multi-Campanhas | Escola de Automação e I.A",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Handle campaign selection via URL query params
query_params = st.query_params
if 'campaign' in query_params:
    campaign_from_url = query_params['campaign']
    if campaign_from_url in CAMPAIGNS:
        # Initialize session state if needed before setting
        if 'selected_campaign' not in st.session_state:
            st.session_state.selected_campaign = None
        st.session_state.selected_campaign = campaign_from_url

import os
INSTITUTIONAL_ORANGE = "#F94E03"
INSTITUTIONAL_LIGHT = "#E0E0DA"
INSTITUTIONAL_ORANGE_LIGHT = "#FB7B3D"
LOGO_PATH = "attached_assets/ID_VISUAL_-_CIRCLE_-_ESCOLA_DE_AUTOMACAO_(15)_1769114404584.png"
LOGO_BF25 = "attached_assets/[ID_VISUAL]_1125_-_BF_-_Artes_Gerais_EA_1769115563727.png"

def find_imersao_logo():
    for f in os.listdir('attached_assets'):
        if 'PAGO' in f and '0126' in f:
            return os.path.join('attached_assets', f)
    return None

LOGO_IMERSAO = find_imersao_logo()

SELECTOR_STYLES = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide Streamlit header bar */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        backdrop-filter: none !important;
    }}
    
    #MainMenu, footer, header {{
        visibility: hidden !important;
    }}
    
    * {{
        font-family: 'Montserrat', sans-serif !important;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #0a0f1a 0%, #0d1321 25%, #111827 50%, #0d1321 75%, #0a0f1a 100%);
        background-attachment: fixed;
    }}
    
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(249, 78, 3, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(251, 123, 61, 0.05) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(255, 255, 255, 0.02) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }}
    
    .hero-section {{
        text-align: center;
        padding: 3rem 2rem 2rem 2rem;
        position: relative;
    }}
    
    .hero-logo {{
        margin-bottom: 1.5rem;
    }}
    
    .hero-logo img {{
        height: 80px;
        filter: drop-shadow(0 4px 20px rgba(249, 78, 3, 0.3));
        transition: all 0.4s ease;
    }}
    
    .hero-logo img:hover {{
        transform: scale(1.05);
        filter: drop-shadow(0 8px 30px rgba(249, 78, 3, 0.5));
    }}
    
    .hero-title {{
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FFFFFF 0%, {INSTITUTIONAL_LIGHT} 50%, #FFFFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }}
    
    .hero-subtitle {{
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.6);
        font-weight: 400;
        letter-spacing: 0.05em;
    }}
    
    .campaigns-container {{
        padding: 2rem;
    }}
    
    .section-title {{
        text-align: center;
        margin-bottom: 2.5rem;
    }}
    
    .section-title h2 {{
        font-size: 1.5rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9) !important;
        position: relative;
        display: inline-block;
    }}
    
    .section-title h2::after {{
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, {INSTITUTIONAL_ORANGE}, {INSTITUTIONAL_ORANGE_LIGHT});
        border-radius: 2px;
    }}
    
    /* Campaign card link styling */
    .campaign-link {{
        text-decoration: none !important;
        color: inherit !important;
        display: block !important;
        position: relative;
        z-index: 1000;
        cursor: pointer !important;
    }}
    
    .campaign-link:hover {{
        text-decoration: none !important;
    }}
    
    .campaign-link * {{
        pointer-events: none;
    }}
    
    .campaign-link {{
        pointer-events: auto !important;
    }}
    
    .campaign-card {{
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    
    .campaign-card:hover {{
        transform: translateY(-8px);
        border-color: rgba(249, 78, 3, 0.3);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 60px rgba(249, 78, 3, 0.15);
    }}
    
    .campaign-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {INSTITUTIONAL_ORANGE}, {INSTITUTIONAL_ORANGE_LIGHT});
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .campaign-card:hover::before {{
        opacity: 1;
    }}
    
    .campaign-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }}
    
    .campaign-logo {{
        max-height: 80px;
        max-width: 200px;
        object-fit: contain;
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 15px rgba(0, 0, 0, 0.3));
        transition: all 0.3s ease;
    }}
    
    .campaign-card:hover .campaign-logo {{
        transform: scale(1.05);
        filter: drop-shadow(0 6px 20px rgba(0, 0, 0, 0.4));
    }}
    
    .campaign-name {{
        font-size: 1.4rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
    }}
    
    .campaign-period {{
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 1.5rem;
    }}
    
    .campaign-status {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .status-active {{
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    
    .status-upcoming {{
        background: rgba(249, 78, 3, 0.15);
        color: {INSTITUTIONAL_ORANGE};
        border: 1px solid rgba(249, 78, 3, 0.3);
    }}
    
    .status-ended {{
        background: rgba(107, 114, 128, 0.15);
        color: #9CA3AF;
        border: 1px solid rgba(107, 114, 128, 0.3);
    }}
    
    .integrations-section {{
        margin-top: 3rem;
        padding: 2rem;
    }}
    
    .integrations-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        max-width: 1000px;
        margin: 0 auto;
    }}
    
    .integration-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .integration-card:hover {{
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }}
    
    .integration-name {{
        font-size: 0.85rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 0.5rem;
    }}
    
    .integration-status {{
        font-size: 0.75rem;
        font-weight: 500;
    }}
    
    .integration-connected {{
        color: #10B981;
    }}
    
    .integration-disconnected {{
        color: #6B7280;
    }}
    
    .footer-info {{
        text-align: center;
        padding: 2rem;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.8rem;
    }}
    
    .stButton > button {{
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(249, 78, 3, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(249, 78, 3, 0.4);
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
        color: {INSTITUTIONAL_ORANGE};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
    }}
    
    p, span, label {{
        color: rgba(255, 255, 255, 0.9);
    }}
</style>
"""

INSTITUTIONAL_STYLES = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide Streamlit header bar */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    #MainMenu, footer {{
        visibility: hidden !important;
    }}
    
    * {{
        font-family: 'Montserrat', sans-serif !important;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #0B1437 0%, #1A1F37 50%, #111C44 100%);
    }}
    
    .campaign-header {{
        display: flex;
        align-items: center;
        gap: 1.5rem;
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(249, 78, 3, 0.3);
    }}
    
    .header-logo {{
        height: 70px;
        width: auto;
        object-fit: contain;
        flex-shrink: 0;
    }}
    
    .header-text {{
        flex: 1;
    }}
    
    .header-text h1 {{
        color: white !important;
        font-weight: 700;
        margin: 0 !important;
        font-size: 1.8rem;
    }}
    
    .header-text p {{
        color: rgba(255,255,255,0.9);
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }}
    
    .main-header {{
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(249, 78, 3, 0.3);
    }}
    
    .main-header h1 {{
        color: white;
        font-weight: 700;
        margin: 0;
        font-size: 2rem;
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
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
</style>
"""

LIGHT_THEME_STYLES = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    /* Hide Streamlit header bar */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    #MainMenu, footer {{
        visibility: hidden !important;
    }}
    
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
    
    .campaign-header {{
        display: flex;
        align-items: center;
        gap: 1.5rem;
        background: linear-gradient(135deg, {INSTITUTIONAL_ORANGE} 0%, {INSTITUTIONAL_ORANGE_LIGHT} 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 30px rgba(249, 78, 3, 0.25);
    }}
    
    .header-logo {{
        height: 70px;
        width: auto;
        object-fit: contain;
        flex-shrink: 0;
    }}
    
    .header-text {{
        flex: 1;
    }}
    
    .header-text h1 {{
        color: white !important;
        font-weight: 700;
        margin: 0 !important;
        font-size: 1.8rem;
    }}
    
    .header-text p {{
        color: rgba(255,255,255,0.9);
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
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
    if 'desafio_sheets_client' not in st.session_state:
        st.session_state.desafio_sheets_client = DesafioSheetClient()

def check_secrets_status():
    secrets = {
        'HOTMART_CLIENT_ID': bool(os.environ.get('HOTMART_CLIENT_ID')),
        'HOTMART_CLIENT_SECRET': bool(os.environ.get('HOTMART_CLIENT_SECRET')),
        'HOTMART_BASIC_TOKEN': bool(os.environ.get('HOTMART_BASIC_TOKEN')),
        'MANYCHAT_API_TOKEN': bool(os.environ.get('MANYCHAT_API_TOKEN')),
        'META_ACCESS_TOKEN': bool(os.environ.get('META_ACCESS_TOKEN')),
        'META_AD_ACCOUNT_ID': bool(os.environ.get('META_AD_ACCOUNT_ID')),
        'GOOGLE_SPREADSHEET_ID': bool(os.environ.get('GOOGLE_SPREADSHEET_ID') or os.environ.get('GOOGLE_SPREADSHEET_ID_BF25') or os.environ.get('GOOGLE_SPREADSHEET_ID_IMERSAO0126')),
        'GOOGLE_SPREADSHEET_ID_BF25': bool(os.environ.get('GOOGLE_SPREADSHEET_ID_BF25')),
        'GOOGLE_SPREADSHEET_ID_IMERSAO0126': bool(os.environ.get('GOOGLE_SPREADSHEET_ID_IMERSAO0126')),
        'GOOGLE_SPREADSHEET_ID_DESAFIO0326': bool(os.environ.get('GOOGLE_SPREADSHEET_ID_DESAFIO0326'))
    }
    return secrets

def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_campaign_status(campaign):
    now = datetime.now(BRT)
    if now < campaign['period_start']:
        return "upcoming", "Em breve"
    elif now > campaign['period_end']:
        return "ended", "Encerrada"
    else:
        return "active", "Ativa"

def render_campaign_selector():
    st.markdown(SELECTOR_STYLES, unsafe_allow_html=True)
    
    import base64
    
    try:
        with open(LOGO_PATH, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_data}" alt="Escola de Automação e I.A">'
    except:
        logo_html = ''
    
    st.markdown(f"""
        <div class="hero-section">
            <div class="hero-logo">
                {logo_html}
            </div>
            <div class="hero-title">Dashboard Multi-Campanhas</div>
            <div class="hero-subtitle">Acompanhe suas campanhas em tempo real</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="section-title">
            <h2>Selecione uma Campanha</h2>
        </div>
    """, unsafe_allow_html=True)
    
    secrets = check_secrets_status()
    
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    
    with col2:
        campaign_cols = st.columns(len(CAMPAIGNS))
        
        for idx, (campaign_id, campaign) in enumerate(CAMPAIGNS.items()):
            with campaign_cols[idx]:
                status_key, status_text = get_campaign_status(campaign)
                period_start = campaign['period_start'].strftime('%d/%m/%Y')
                period_end = campaign['period_end'].strftime('%d/%m/%Y')
                
                campaign_logos = {"bf25": LOGO_BF25, "imersao0126": LOGO_IMERSAO}
                logo_path = campaign_logos.get(campaign_id, LOGO_PATH)
                try:
                    with open(logo_path, "rb") as f:
                        campaign_logo_data = base64.b64encode(f.read()).decode()
                    campaign_logo_html = f'<img class="campaign-logo" src="data:image/png;base64,{campaign_logo_data}" alt="{campaign["name"]}">'
                except:
                    campaign_logo_html = f'<span class="campaign-icon">📊</span>'
                
                st.markdown(f"""
                    <div class="campaign-card">
                        {campaign_logo_html}
                        <div class="campaign-name">{campaign['name']}</div>
                        <div class="campaign-period">{period_start} - {period_end}</div>
                        <span class="campaign-status status-{status_key}">{status_text}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Acessar Dashboard", key=f"btn_{campaign_id}", type="primary", use_container_width=True):
                    st.session_state.selected_campaign = campaign_id
                    st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="section-title">
            <h2>Integrações</h2>
        </div>
    """, unsafe_allow_html=True)
    
    integrations_config = {
        "hotmart": {
            "name": "Hotmart API",
            "icon": "💳",
            "connected": secrets.get('HOTMART_CLIENT_ID') and secrets.get('HOTMART_CLIENT_SECRET') and secrets.get('HOTMART_BASIC_TOKEN'),
            "secrets_needed": ["HOTMART_CLIENT_ID", "HOTMART_CLIENT_SECRET", "HOTMART_BASIC_TOKEN"],
            "description": "Integração com a plataforma Hotmart para acompanhar vendas, reembolsos e métricas de produtos.",
            "instructions": """
**Como obter as credenciais:**
1. Acesse [Hotmart Developers](https://developers.hotmart.com/)
2. Vá em **Ferramentas → Credenciais de desenvolvedor**
3. Clique em **"Criar credencial"** → Selecione **"API Hotmart"**
4. Copie os 3 valores gerados:
   - **Client ID**
   - **Client Secret**
   - **Basic Token**

**Secrets necessários:**
- `HOTMART_CLIENT_ID` - Identificador da aplicação
- `HOTMART_CLIENT_SECRET` - Chave secreta
- `HOTMART_BASIC_TOKEN` - Token para autenticação
            """
        },
        "manychat": {
            "name": "ManyChat",
            "icon": "💬",
            "connected": secrets['MANYCHAT_API_TOKEN'],
            "secrets_needed": ["MANYCHAT_API_TOKEN"],
            "description": "Integração com ManyChat para métricas de WhatsApp, fluxos de automação e engajamento.",
            "instructions": """
**Como obter o token:**
1. Acesse [ManyChat](https://manychat.com/) e faça login
2. Vá em Settings → API
3. Copie o API Token

**Secret necessário:** `MANYCHAT_API_TOKEN`
            """
        },
        "meta_ads": {
            "name": "Meta Ads",
            "icon": "📱",
            "connected": secrets['META_ACCESS_TOKEN'] and secrets['META_AD_ACCOUNT_ID'],
            "secrets_needed": ["META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID"],
            "per_campaign": True,
            "campaign_field": "META_CAMPAIGN_NAME",
            "description": "Integração com Facebook/Meta Ads para acompanhar campanhas, gastos e métricas de anúncios.",
            "instructions": """
**Como obter os tokens:**
1. Acesse [Facebook Developers](https://developers.facebook.com/)
2. Crie um App de Marketing
3. Gere um Access Token com permissões de Ads
4. Encontre seu Ad Account ID no Gerenciador de Anúncios

**Secrets necessários:**
- `META_ACCESS_TOKEN` - Token de acesso (global)
- `META_AD_ACCOUNT_ID` - ID da conta (formato: act_XXXXXXX)
            """
        },
        "google_sheets": {
            "name": "Google Sheets",
            "icon": "📊",
            "connected": secrets['GOOGLE_SPREADSHEET_ID'],
            "secrets_needed": ["GOOGLE_SPREADSHEET_ID"],
            "per_campaign": True,
            "campaign_field": "GOOGLE_SPREADSHEET_ID",
            "description": "Integração com Google Sheets para ler dados de leads, pesquisas e informações da planilha.",
            "instructions": """
**Como configurar:**
1. Abra sua planilha no Google Sheets
2. Copie o ID da planilha da URL (entre /d/ e /edit)
3. Compartilhe a planilha com acesso público ou com a conta de serviço

*Exemplo de URL:* `https://docs.google.com/spreadsheets/d/`**`1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`**`/edit`

⚠️ **Cada campanha usa uma planilha diferente!**
            """
        }
    }
    
    col_spacer1, col_int, col_spacer2 = st.columns([1, 4, 1])
    
    with col_int:
        int_cols = st.columns(4)
        for idx, (key, config) in enumerate(integrations_config.items()):
            with int_cols[idx]:
                status_class = "integration-connected" if config['connected'] else "integration-disconnected"
                status_text = "Conectado" if config['connected'] else "Configurar"
                status_icon = "●" if config['connected'] else "⚙️"
                
                if st.button(f"{config['icon']} {config['name']}", key=f"int_btn_{key}", use_container_width=True):
                    st.session_state.config_integration = key
                
                st.markdown(f"""
                    <div style="text-align: center; margin-top: -10px;">
                        <span class="integration-status {status_class}">{status_icon} {status_text}</span>
                    </div>
                """, unsafe_allow_html=True)
    
    if 'config_integration' in st.session_state and st.session_state.config_integration:
        key = st.session_state.config_integration
        config = integrations_config[key]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
                            border-radius: 16px; padding: 2rem; margin: 1rem 0;">
                    <h3 style="color: #F94E03; margin-bottom: 0.5rem;">{config['icon']} Configurar {config['name']}</h3>
                    <p style="color: rgba(255,255,255,0.7); margin-bottom: 1.5rem;">{config['description']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(config['instructions'])
                
                st.markdown("---")
                
                is_per_campaign = config.get('per_campaign', False)
                
                if is_per_campaign:
                    st.markdown("#### 🎯 Configuração por Campanha")
                    
                    campaign_options = {
                        "bf25": "BLACK FRIDAY 2025",
                        "imersao0126": "IMERSAO 01/26",
                        "desafio0326": "DESAFIO IA 03/26"
                    }
                    
                    selected_campaign = st.selectbox(
                        "Selecione a campanha:",
                        options=list(campaign_options.keys()),
                        format_func=lambda x: campaign_options[x],
                        key="config_campaign_selector"
                    )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if key == "google_sheets":
                        sheet_id_key = f"GOOGLE_SPREADSHEET_ID_{selected_campaign.upper()}"
                        current_value = os.environ.get(sheet_id_key, "")
                        
                        st.markdown(f"**📊 Planilha para {campaign_options[selected_campaign]}:**")
                        
                        if current_value:
                            st.success(f"✅ Planilha configurada: `...{current_value[-15:]}`")
                        
                        new_sheet_id = st.text_input(
                            "ID da Planilha Google",
                            placeholder="Cole aqui o ID da planilha (entre /d/ e /edit na URL)",
                            key=f"input_sheet_{selected_campaign}"
                        )
                        
                        if new_sheet_id:
                            if st.button("💾 Salvar Planilha", key=f"save_sheet_{selected_campaign}", type="primary"):
                                os.environ[sheet_id_key] = new_sheet_id.strip()
                                st.success(f"✅ Planilha salva para {campaign_options[selected_campaign]}!")
                                st.balloons()
                    
                    elif key == "meta_ads":
                        st.markdown("##### 🔑 Credenciais Globais (todas as campanhas)")
                        
                        secret_inputs = {}
                        for secret in ["META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID"]:
                            is_configured = secrets.get(secret, False)
                            if is_configured:
                                st.success(f"✅ `{secret}` - Configurado")
                            else:
                                secret_labels = {
                                    "META_ACCESS_TOKEN": "Access Token Meta/Facebook",
                                    "META_AD_ACCOUNT_ID": "Ad Account ID (act_XXXXX)"
                                }
                                label = secret_labels.get(secret, secret)
                                secret_inputs[secret] = st.text_input(
                                    label,
                                    type="password" if "TOKEN" in secret else "default",
                                    placeholder=f"Cole aqui seu {label}",
                                    key=f"input_{secret}"
                                )
                        
                        st.markdown("---")
                        st.markdown(f"##### 📢 Nome da Campanha no Meta Ads")
                        st.markdown(f"**Campanha selecionada:** {campaign_options[selected_campaign]}")
                        
                        campaign_name_key = f"META_CAMPAIGN_NAME_{selected_campaign.upper()}"
                        current_campaign_name = os.environ.get(campaign_name_key, "")
                        
                        if current_campaign_name:
                            st.info(f"📌 Nome atual: `{current_campaign_name}`")
                        
                        new_campaign_name = st.text_input(
                            "Nome da Campanha no Meta Ads",
                            placeholder="Ex: [CONVERSÃO] Black Friday 2025",
                            key=f"input_meta_campaign_{selected_campaign}"
                        )
                        
                        has_new_input = any(v for v in secret_inputs.values() if v) or new_campaign_name
                        
                        if has_new_input:
                            if st.button("💾 Salvar Configuração", key="save_meta_config", type="primary"):
                                saved_any = False
                                for secret_name, value in secret_inputs.items():
                                    if value and value.strip():
                                        os.environ[secret_name] = value.strip()
                                        saved_any = True
                                
                                if new_campaign_name:
                                    os.environ[campaign_name_key] = new_campaign_name.strip()
                                    saved_any = True
                                
                                if saved_any:
                                    st.success("✅ Configuração salva!")
                                    st.balloons()
                
                else:
                    st.markdown("#### 🔑 Inserir Chaves de API")
                    
                    secret_inputs = {}
                    for secret in config['secrets_needed']:
                        is_configured = secrets.get(secret, False)
                        
                        if is_configured:
                            st.success(f"✅ `{secret}` - Já configurado")
                            secret_inputs[secret] = None
                        else:
                            secret_labels = {
                                "HOTMART_CLIENT_ID": "Client ID Hotmart",
                                "HOTMART_CLIENT_SECRET": "Client Secret Hotmart",
                                "HOTMART_BASIC_TOKEN": "Basic Token Hotmart",
                                "MANYCHAT_API_TOKEN": "Token ManyChat API"
                            }
                            label = secret_labels.get(secret, secret)
                            is_sensitive = "TOKEN" in secret or "SECRET" in secret
                            secret_inputs[secret] = st.text_input(
                                label,
                                type="password" if is_sensitive else "default",
                                placeholder=f"Cole aqui seu {label}",
                                key=f"input_{secret}"
                            )
                    
                    has_new_input = any(v for v in secret_inputs.values() if v)
                    
                    if has_new_input:
                        if st.button("💾 Salvar Configuração", key="save_secrets", type="primary"):
                            saved_any = False
                            for secret_name, value in secret_inputs.items():
                                if value and value.strip():
                                    os.environ[secret_name] = value.strip()
                                    saved_any = True
                            
                            if saved_any:
                                st.success("✅ Configuração salva! Recarregue a página para aplicar.")
                                st.balloons()
                
                st.markdown("""
                    <br>
                    <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">
                    🔒 Suas chaves são armazenadas de forma segura e nunca são exibidas após salvas.
                    </p>
                """, unsafe_allow_html=True)
            
            with col2:
                if config['connected']:
                    st.markdown("""
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);
                                    border-radius: 12px; padding: 1.5rem; text-align: center;">
                            <div style="font-size: 3rem; margin-bottom: 0.5rem;">✅</div>
                            <div style="color: #10B981; font-weight: 600;">Integração Ativa</div>
                            <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-top: 0.5rem;">
                                Todos os secrets necessários estão configurados.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="background: rgba(249, 78, 3, 0.1); border: 1px solid rgba(249, 78, 3, 0.3);
                                    border-radius: 12px; padding: 1.5rem; text-align: center;">
                            <div style="font-size: 3rem; margin-bottom: 0.5rem;">⚙️</div>
                            <div style="color: #F94E03; font-weight: 600;">Configuração Pendente</div>
                            <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-top: 0.5rem;">
                                Preencha os campos ao lado para ativar.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("❌ Fechar", key="close_config"):
                st.session_state.config_integration = None
                st.rerun()
    
    st.markdown(f"""
        <div class="footer-info">
            <p>Escola de Automação e I.A &bull; {datetime.now(BRT).strftime('%d/%m/%Y %H:%M')} BRT</p>
        </div>
    """, unsafe_allow_html=True)

def render_bf25_dashboard():
    st.markdown(LIGHT_THEME_STYLES, unsafe_allow_html=True)
    
    config = get_campaign_config('bf25')
    secrets = check_secrets_status()
    
    bf_logo_path = "attached_assets/[ID_VISUAL]_1125_-_BF_-_Artes_Gerais_EA_1769115563727.png"
    
    # Unified header with back button
    if st.button("← Voltar", key="back_bf25"):
        st.session_state.selected_campaign = None
        st.query_params.clear()
        st.rerun()
    
    import base64
    with open(bf_logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
        <div class="campaign-header">
            <img src="data:image/png;base64,{logo_b64}" class="header-logo" />
            <div class="header-text">
                <h1>{config['name']}</h1>
                <p>Dashboard de Acompanhamento</p>
            </div>
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
    
    if secrets.get('GOOGLE_SPREADSHEET_ID_BF25') or secrets.get('GOOGLE_SPREADSHEET_ID'):
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
        
        st.info("Configure o GOOGLE_SPREADSHEET_ID_BF25 nos Secrets para visualizar os dados de captação.")

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
    
    if secrets.get('GOOGLE_SPREADSHEET_ID_BF25') or secrets.get('GOOGLE_SPREADSHEET_ID'):
        st.info("Análise de origem dos leads será exibida com base nos dados do Google Sheets.")
    else:
        st.info("Configure o GOOGLE_SPREADSHEET_ID_BF25 nos Secrets para visualizar a origem dos leads.")

def render_bf25_pesquisa(secrets):
    st.subheader("Pesquisa")
    
    if secrets.get('GOOGLE_SPREADSHEET_ID_BF25') or secrets.get('GOOGLE_SPREADSHEET_ID'):
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
        st.info("Configure o GOOGLE_SPREADSHEET_ID_BF25 nos Secrets para visualizar as pesquisas.")

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
    
    # Unified header with back button
    if st.button("← Voltar", key="back_imersao"):
        st.session_state.selected_campaign = None
        st.query_params.clear()
        st.rerun()
    
    imersao_logo = None
    for f in os.listdir("attached_assets"):
        if "LANCAMENTO_PAGO_0126" in f.replace("Ç", "C") or "0126" in f:
            imersao_logo = f"attached_assets/{f}"
            break
    
    import base64
    logo_html = ""
    if imersao_logo:
        with open(imersao_logo, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo" />'
    
    st.markdown(f"""
        <div class="campaign-header">
            {logo_html}
            <div class="header-text">
                <h1>{config['name']}</h1>
                <p>Dashboard de Acompanhamento</p>
            </div>
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

def render_desafio_dashboard():
    st.markdown(INSTITUTIONAL_STYLES, unsafe_allow_html=True)

    config = get_campaign_config('desafio0326')
    secrets = check_secrets_status()

    if st.button("← Voltar", key="back_desafio"):
        st.session_state.selected_campaign = None
        st.query_params.clear()
        st.rerun()

    import base64
    logo_html = ""
    try:
        with open(LOGO_PATH, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo" />'
    except:
        pass

    st.markdown(f"""
        <div class="campaign-header">
            {logo_html}
            <div class="header-text">
                <h1>{config['name']}</h1>
                <p>Dashboard de Acompanhamento — 09/03 a 13/03/2026</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(config['tabs'])

    with tabs[0]:
        render_desafio_captacao(config, secrets)

    with tabs[1]:
        render_desafio_pesquisa(secrets)

    with tabs[2]:
        render_desafio_grupos(secrets)

    with tabs[3]:
        render_desafio_origem_leads(secrets)

    with tabs[4]:
        render_desafio_meta_ads(config, secrets)


def render_desafio_captacao(config, secrets):
    st.subheader("Captacao de Leads")

    has_sheets = secrets.get('GOOGLE_SPREADSHEET_ID_DESAFIO0326')
    has_hotmart = secrets.get('HOTMART_BASIC_TOKEN')

    # Hotmart sales metrics
    total_principal = 0
    total_vip = 0
    total_ea = 0
    revenue_principal = 0
    revenue_vip = 0
    revenue_ea = 0
    df_principal = pd.DataFrame()

    if has_hotmart:
        try:
            client = st.session_state.hotmart_client
            start_date = config['period_start']
            end_date = min(config['period_end'], datetime.now(BRT))

            with st.spinner("Carregando vendas da Hotmart..."):
                sales_principal = client.get_approved_sales(config['hotmart']['principal']['product_id'], start_date, end_date)
                sales_vip = client.get_approved_sales(config['hotmart']['orderbump_vip']['product_id'], start_date, end_date)
                sales_ea = client.get_approved_sales(config['hotmart']['escola_automacao']['product_id'], start_date, end_date)

            df_principal = process_hotmart_sales(sales_principal)
            df_vip = process_hotmart_sales(sales_vip)
            df_ea = process_hotmart_sales(sales_ea)

            m_principal = calculate_sales_metrics(df_principal)
            m_vip = calculate_sales_metrics(df_vip)
            m_ea = calculate_sales_metrics(df_ea)

            total_principal = m_principal['total_sales']
            total_vip = m_vip['total_sales']
            total_ea = m_ea['total_sales']
            revenue_principal = m_principal['total_revenue']
            revenue_vip = m_vip['total_revenue']
            revenue_ea = m_ea['total_revenue']
        except Exception as e:
            st.warning(f"Erro ao carregar vendas Hotmart: {e}")

    total_leads = 0
    if has_sheets:
        try:
            client = st.session_state.desafio_sheets_client
            leads = client.get_leads()
            total_leads = len(leads) - 1 if len(leads) > 1 else 0
        except Exception as e:
            st.warning(f"Erro ao carregar leads: {e}")

    total_revenue = revenue_principal + revenue_vip + revenue_ea

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Total de Leads</div>
                <div class="metric-value">{total_leads:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Vendas Desafio</div>
                <div class="metric-value">{total_principal:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Orderbumps VIP</div>
                <div class="metric-value">{total_vip:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Faturamento Total</div>
                <div class="metric-value">{format_currency(total_revenue)}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col5, col6 = st.columns(2)

    with col5:
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Vendas Escola de Automacao</div>
                <div class="metric-value">{total_ea:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col6:
        conv_rate = (total_principal / total_leads * 100) if total_leads > 0 else 0
        st.markdown(f"""
            <div class="glass-card">
                <div class="metric-label">Taxa de Conversao (Lead → Venda)</div>
                <div class="metric-value">{conv_rate:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)

    if has_hotmart and total_principal > 0:
        grouped = group_sales_by_date(df_principal)
        if not grouped.empty:
            fig = create_sales_line_chart(grouped, INSTITUTIONAL_ORANGE, INSTITUTIONAL_ORANGE_LIGHT)
            fig = create_dark_theme_chart(fig)
            fig.update_layout(title='Vendas por Dia — Desafio IA')
            st.plotly_chart(fig, use_container_width=True)

            fig2 = create_revenue_bar_chart(grouped, INSTITUTIONAL_ORANGE)
            fig2 = create_dark_theme_chart(fig2)
            fig2.update_layout(title='Faturamento por Dia — Desafio IA')
            st.plotly_chart(fig2, use_container_width=True)

    if not has_sheets and not has_hotmart:
        st.info("Configure GOOGLE_SPREADSHEET_ID_DESAFIO0326 e/ou HOTMART_BASIC_TOKEN nos Secrets para visualizar os dados.")


def render_desafio_pesquisa(secrets):
    st.subheader("Pesquisa")

    if secrets.get('GOOGLE_SPREADSHEET_ID_DESAFIO0326'):
        try:
            client = st.session_state.desafio_sheets_client
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
            st.warning(f"Erro ao carregar pesquisa: {e}")
    else:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Total de Respostas</div>
                <div class="metric-value">---</div>
            </div>
        """, unsafe_allow_html=True)
        st.info("Configure GOOGLE_SPREADSHEET_ID_DESAFIO0326 nos Secrets para visualizar a pesquisa.")


def render_desafio_grupos(secrets):
    st.subheader("Grupos")

    if secrets.get('GOOGLE_SPREADSHEET_ID_DESAFIO0326'):
        try:
            client = st.session_state.desafio_sheets_client
            grupos = client.get_grupos()

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
            st.warning(f"Erro ao carregar grupos: {e}")
    else:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Entradas nos Grupos</div>
                <div class="metric-value">---</div>
            </div>
        """, unsafe_allow_html=True)
        st.info("Configure GOOGLE_SPREADSHEET_ID_DESAFIO0326 nos Secrets para visualizar os grupos.")


def render_desafio_origem_leads(secrets):
    st.subheader("Origem dos Leads")

    if secrets.get('GOOGLE_SPREADSHEET_ID_DESAFIO0326'):
        try:
            client = st.session_state.desafio_sheets_client
            origem = client.get_origem_leads()

            total = len(origem) - 1 if len(origem) > 1 else 0

            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-label">Registros de Origem</div>
                    <div class="metric-value">{total:,}</div>
                </div>
            """, unsafe_allow_html=True)

            if total > 0:
                df = process_sheets_data(origem)
                st.dataframe(df, use_container_width=True)

                if 'origem' in [c.lower() for c in df.columns] or 'Origem' in df.columns:
                    col_name = 'Origem' if 'Origem' in df.columns else [c for c in df.columns if c.lower() == 'origem'][0]
                    counts = df[col_name].value_counts()
                    import plotly.graph_objects as go
                    fig = go.Figure(data=[go.Pie(
                        labels=counts.index.tolist(),
                        values=counts.values.tolist(),
                        hole=.4,
                        marker_colors=[INSTITUTIONAL_ORANGE, INSTITUTIONAL_ORANGE_LIGHT, '#FFD166', '#10B981', '#6366F1']
                    )])
                    fig.update_layout(title="Distribuicao por Origem")
                    fig = create_dark_theme_chart(fig)
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Erro ao carregar origem dos leads: {e}")
    else:
        st.markdown("""
            <div class="glass-card">
                <div class="metric-label">Registros de Origem</div>
                <div class="metric-value">---</div>
            </div>
        """, unsafe_allow_html=True)
        st.info("Configure GOOGLE_SPREADSHEET_ID_DESAFIO0326 nos Secrets para visualizar a origem dos leads.")


def render_desafio_meta_ads(config, secrets):
    st.subheader("Meta Ads")

    if secrets['META_ACCESS_TOKEN'] and secrets['META_AD_ACCOUNT_ID']:
        try:
            client = st.session_state.meta_ads_client
            start_date = config['period_start']
            end_date = min(config['period_end'], datetime.now(BRT))

            with st.spinner("Carregando dados do Meta Ads..."):
                metrics = client.get_desafio0326_metrics(start_date, end_date)

            impressions = int(metrics.get('impressions', 0))
            clicks = int(metrics.get('clicks', 0))
            ctr = float(metrics.get('inline_link_click_ctr', 0))
            spend = float(metrics.get('spend', 0))
            cpc = float(metrics.get('cpc', 0))

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Impressoes</div>
                        <div class="metric-value">{impressions:,}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Cliques</div>
                        <div class="metric-value">{clicks:,}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">CTR</div>
                        <div class="metric-value">{ctr:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">CPC</div>
                        <div class="metric-value">{format_currency(cpc)}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col5:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">Gasto Total</div>
                        <div class="metric-value">{format_currency(spend)}</div>
                    </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Erro ao carregar Meta Ads: {e}")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        labels = ["Impressoes", "Cliques", "CTR", "CPC", "Gasto Total"]
        cols = [col1, col2, col3, col4, col5]
        for col, label in zip(cols, labels):
            with col:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">---</div>
                    </div>
                """, unsafe_allow_html=True)
        st.info("Configure META_ACCESS_TOKEN e META_AD_ACCOUNT_ID nos Secrets para visualizar os dados.")


def main():
    init_session_state()

    if st.session_state.selected_campaign is None:
        render_campaign_selector()
    elif st.session_state.selected_campaign == 'bf25':
        render_bf25_dashboard()
    elif st.session_state.selected_campaign == 'imersao0126':
        render_imersao_dashboard()
    elif st.session_state.selected_campaign == 'desafio0326':
        render_desafio_dashboard()

if __name__ == "__main__":
    main()
