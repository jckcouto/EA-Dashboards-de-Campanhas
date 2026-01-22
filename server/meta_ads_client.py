import os
import requests
import streamlit as st
from datetime import datetime

META_BASE_URL = "https://graph.facebook.com/v22.0"

class MetaAdsClient:
    def __init__(self):
        self.access_token = os.environ.get('META_ACCESS_TOKEN', '')
        self.ad_account_id = os.environ.get('META_AD_ACCOUNT_ID', '')
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        if not self.access_token or not self.ad_account_id:
            return {}
        
        url = f"{META_BASE_URL}/{endpoint}"
        
        if params is None:
            params = {}
        
        params['access_token'] = self.access_token
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Erro Meta Ads: {e}")
        
        return {}
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_account_info(_self) -> dict:
        return _self._make_request(f"act_{_self.ad_account_id}")
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_insights(_self, start_date: datetime, end_date: datetime, 
                    campaign_filter: str = None) -> dict:
        params = {
            'fields': 'impressions,clicks,inline_link_clicks,spend,actions,inline_link_click_ctr,cpc,cpm',
            'time_range': f'{{"since":"{start_date.strftime("%Y-%m-%d")}","until":"{end_date.strftime("%Y-%m-%d")}"}}'
        }
        
        if campaign_filter:
            params['filtering'] = f'[{{"field":"campaign.name","operator":"CONTAIN","value":"{campaign_filter}"}}]'
        
        return _self._make_request(f"act_{_self.ad_account_id}/insights", params)
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_campaigns(_self, name_filter: str = None) -> list:
        params = {
            'fields': 'name,status,objective,spend'
        }
        
        if name_filter:
            params['filtering'] = f'[{{"field":"name","operator":"CONTAIN","value":"{name_filter}"}}]'
        
        result = _self._make_request(f"act_{_self.ad_account_id}/campaigns", params)
        return result.get('data', [])
    
    def get_bf25_metrics(self, start_date: datetime, end_date: datetime) -> dict:
        insights = self.get_insights(start_date, end_date, 'BF25')
        
        data = insights.get('data', [{}])
        if data:
            return data[0]
        return {}
    
    def get_imersao_metrics(self, start_date: datetime, end_date: datetime) -> dict:
        insights = self.get_insights(start_date, end_date, 'WSIA_JAN26')
        
        data = insights.get('data', [{}])
        if data:
            return data[0]
        return {}
