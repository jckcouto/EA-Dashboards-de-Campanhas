# Dashboard Multi-Campanhas - Escola de Automação e I.A

## Visão Geral
Dashboard Streamlit para gerenciamento de múltiplas campanhas de marketing da Escola de Automação e I.A.

**Framework**: Streamlit (Python)
**Porta**: 5000
**URL de Produção**: https://dash.escoladeautomacao.com.br

## Identidade Visual
- **Cor Primária**: `#F94E03` (Laranja Institucional)
- **Cor Secundária**: `#E0E0DA` (Cinza Claro)
- **Tipografia**: Montserrat (Bold para títulos, Medium para textos)

## Campanhas Disponíveis

### BLACK FRIDAY 2025 (bf25)
- Período: 06/11/2025 - 08/12/2025
- Tema: Claro com azul (#4A90E2) e amarelo (#FFD166)
- 11 abas de funcionalidades

### IMERSÃO 01/26 (imersao0126)
- Período: 07/01/2026 - 31/01/2026
- Tema: Escuro com glassmorphism
- 4 abas de funcionalidades

## Estrutura de Arquivos
```
/
├── app.py                          # Aplicação principal
├── campaigns/
│   ├── __init__.py
│   └── config.py                   # Configurações das campanhas
├── server/
│   ├── google_sheet_client.py      # Cliente Google Sheets
│   ├── hotmart_client.py           # Cliente Hotmart API
│   ├── manychat_client.py          # Cliente ManyChat API
│   └── meta_ads_client.py          # Cliente Meta Ads API
├── utils/
│   ├── data_processor.py           # Processamento de dados
│   └── chart_helpers.py            # Helpers para gráficos Plotly
└── .streamlit/
    └── config.toml                 # Configurações do Streamlit
```

## Secrets Necessários
| Secret | Descrição |
|--------|-----------|
| GOOGLE_SPREADSHEET_ID | ID da planilha Google Sheets |
| HOTMART_BASIC_TOKEN | Token Base64 para autenticação Hotmart |
| MANYCHAT_API_TOKEN | Token da API ManyChat |
| META_ACCESS_TOKEN | Token do Facebook/Meta |
| META_AD_ACCOUNT_ID | ID da conta de anúncios |

## Como Executar
```bash
streamlit run app.py --server.port 5000
```

## Integrações
- Google Sheets (via Replit Connectors)
- Hotmart API (OAuth2)
- ManyChat API
- Meta Ads API
