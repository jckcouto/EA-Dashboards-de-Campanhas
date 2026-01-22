import os
import requests
import streamlit as st

MANYCHAT_BASE_URL = "https://api.manychat.com/fb"

BF25_TAGS = {
    'alunos_boas_vindas_recebeu': '[BF25]-LEAD-ALUNO-BOASVINDAS-RECEBEU',
    'alunos_boas_vindas_clicou': '[BF25]-LEAD-ALUNO-BOASVINDAS-CLICOU',
    'geral_boas_vindas_recebeu': '[BF25]-LEAD-GERAL-BOASVINDAS-RECEBEU',
    'geral_boas_vindas_clicou': '[BF25]-LEAD-GERAL-BOASVINDAS-CLICOU',
    'geral_fluxo_instagram': 'BF25-RECEBEU-FLUXO-GERAL',
    'geral_clicou_link_lp': 'BF25-CLICOU-LINK-LP-CADASTRO',
    'geral_deixou_telefone': 'BF25-DEIXOU-TELEFONE-CADASTRO',
    'alunos_recebeu_convite_api': 'BF25-ALUNOS-RECEBEU-CONVITE-1-API',
    'alunos_interagiu_convite': 'BF25-INTERAGIU-DISPARO-API-CONVITE-ALUNOS',
    'geral_recebeu_convite_api': 'BF25-GERAL-RECEBEU-CONVITE-1-API',
    'geral_interagiu_convite': 'BF25-INTERAGIU-DISPARO-API-CONVITE-GERAL'
}

class ManyChatClient:
    def __init__(self):
        self.api_token = os.environ.get('MANYCHAT_API_TOKEN', '')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        if not self.api_token:
            return {}
        
        url = f"{MANYCHAT_BASE_URL}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers)
            else:
                response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Erro ManyChat: {e}")
        
        return {}
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_page_stats(_self) -> dict:
        result = _self._make_request('/page/getStats')
        return result.get('data', {})
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_tags(_self) -> list:
        result = _self._make_request('/page/getTags')
        return result.get('data', [])
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_subscribers_by_tag(_self, tag_name: str) -> list:
        tags = _self.get_tags()
        tag_id = None
        
        for tag in tags:
            if tag.get('name') == tag_name:
                tag_id = tag.get('id')
                break
        
        if not tag_id:
            return []
        
        result = _self._make_request('/subscribers/findByTag', 'POST', {'tag_id': tag_id})
        return result.get('data', [])
    
    def get_bf25_metrics(self) -> dict:
        metrics = {}
        
        for key, tag_name in BF25_TAGS.items():
            subscribers = self.get_subscribers_by_tag(tag_name)
            metrics[key] = len(subscribers)
        
        return metrics
