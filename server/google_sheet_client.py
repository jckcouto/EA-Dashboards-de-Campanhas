import os
import requests
import streamlit as st

class GoogleSheetClient:
    def __init__(self, spreadsheet_id: str = None):
        self.spreadsheet_id = spreadsheet_id or os.environ.get('GOOGLE_SPREADSHEET_ID', '')
        self.connector_hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME', '')
        self.identity_token = os.environ.get('WEB_REPL_RENEWAL') or os.environ.get('REPL_IDENTITY', '')
    
    def _get_headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.identity_token}',
            'Content-Type': 'application/json'
        }
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_sheet_data(_self, sheet_name: str, range_str: str = 'A:Z') -> list:
        if not _self.spreadsheet_id:
            return []
        
        try:
            if _self.connector_hostname:
                url = f"https://{_self.connector_hostname}/google-sheets/spreadsheets/{_self.spreadsheet_id}/values/{sheet_name}!{range_str}"
                response = requests.get(url, headers=_self._get_headers())
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('values', [])
        except Exception as e:
            st.error(f"Erro ao acessar Google Sheets: {e}")
        
        return []
    
    def get_leads_alunos(self) -> list:
        return self.get_sheet_data('Leads [EA Alunos]')
    
    def get_leads_geral(self) -> list:
        return self.get_sheet_data('Leads [Geral]')
    
    def get_pesquisa_alunos(self) -> list:
        return self.get_sheet_data('Pesquisa [EA Alunos]')
    
    def get_pesquisa_geral(self) -> list:
        return self.get_sheet_data('Pesquisa [Geral]')
    
    def get_grupo_alunos(self) -> list:
        return self.get_sheet_data('Entrou no Grupo [EA Alunos]')
    
    def get_grupo_geral(self) -> list:
        return self.get_sheet_data('Entrou no Grupo [Geral]')


class ImersaoSheetClient(GoogleSheetClient):
    def __init__(self):
        super().__init__(spreadsheet_id=os.environ.get('GOOGLE_SPREADSHEET_ID_IMERSAO0126', ''))
    
    def get_vendas(self) -> list:
        return self.get_sheet_data('VENDAS')
    
    def get_reembolsos(self) -> list:
        return self.get_sheet_data('REEMBOLSOS')
    
    def get_pesquisa(self) -> list:
        return self.get_sheet_data('PESQUISA')
    
    def get_monitoramento_grupos(self) -> list:
        return self.get_sheet_data('MONITORAMENTO GRUPOS')
