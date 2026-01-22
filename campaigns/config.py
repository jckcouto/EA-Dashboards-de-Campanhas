from datetime import datetime
from zoneinfo import ZoneInfo

BRT = ZoneInfo('America/Sao_Paulo')

CAMPAIGNS = {
    "bf25": {
        "id": "bf25",
        "name": "BLACK FRIDAY 2025",
        "period_start": datetime(2025, 11, 6, 19, 0, tzinfo=BRT),
        "period_end": datetime(2025, 12, 8, 23, 59, tzinfo=BRT),
        "colors": {
            "primary": "#4A90E2",
            "secondary": "#FFD166",
            "background": "#FFFFFF",
            "text": "#1A1A1A"
        },
        "hotmart": {
            "product_id": "6398418",
            "product_name": "Escola de Automação - Acesso Vitalício"
        },
        "tabs": [
            "VISÃO DA CAPTAÇÃO",
            "VENDAS",
            "COMPARAR",
            "ORIGEM DOS LEADS",
            "PESQUISA",
            "INVESTIMENTOS EXTRAS",
            "META ADS",
            "API OFICIAL DO ZAPZAP",
            "DADOS",
            "METAS",
            "PLANEJAMENTO 2025"
        ],
        "integrations": {
            "google_sheets": True,
            "hotmart": True,
            "manychat": True,
            "meta_ads": True
        },
        "theme": "light"
    },
    "imersao0126": {
        "id": "imersao0126",
        "name": "IMERSÃO 01/26",
        "period_start": datetime(2026, 1, 7, 0, 0, tzinfo=BRT),
        "period_end": datetime(2026, 1, 31, 23, 59, tzinfo=BRT),
        "colors": {
            "primary": "#F94E03",
            "secondary": "#FB7B3D",
            "background": "#0B1437",
            "text": "#FFFFFF"
        },
        "hotmart": {
            "ingresso": {
                "product_id": "6926419",
                "product_name": "Ingresso Imersão"
            },
            "orderbump": {
                "product_id": "6926479",
                "product_name": "Orderbump Gravação"
            }
        },
        "google_sheets_id": "1KwL7xYFSp-M_tqnHvMfBcDwiJqcoQy8FtPefUSefdNk",
        "tabs": [
            "VENDAS",
            "REEMBOLSOS",
            "PESQUISA",
            "MONITORAMENTO GRUPOS"
        ],
        "integrations": {
            "google_sheets": True,
            "hotmart": True,
            "manychat": False,
            "meta_ads": False
        },
        "theme": "dark"
    }
}

def get_campaign_config(campaign_id: str) -> dict:
    return CAMPAIGNS.get(campaign_id, {})
