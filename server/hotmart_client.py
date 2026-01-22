import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

BRT = ZoneInfo('America/Sao_Paulo')

HOTMART_AUTH_URL = "https://api-sec-vlc.hotmart.com/security/oauth/token"
HOTMART_API_BASE = "https://developers.hotmart.com/payments/api/v1"

class HotmartClient:
    def __init__(self):
        self.basic_token = os.environ.get('HOTMART_BASIC_TOKEN', '')
        self.access_token = None
        self.token_expires_at = None
    
    def _ensure_token(self):
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return True
        
        if not self.basic_token:
            return False
        
        try:
            response = requests.post(
                HOTMART_AUTH_URL,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': f'Basic {self.basic_token}'
                },
                data={'grant_type': 'client_credentials'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                expires_in = data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                return True
        except Exception as e:
            st.error(f"Erro na autenticação Hotmart: {e}")
        
        return False
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_sales_history(_self, product_id: str, start_date: datetime, end_date: datetime, 
                          status: str = None) -> list:
        if not _self._ensure_token():
            return []
        
        all_sales = []
        seen_transactions = set()
        
        current_date = start_date
        while current_date <= end_date:
            next_date = min(current_date + timedelta(days=1), end_date)
            
            start_ms = int(current_date.timestamp() * 1000)
            end_ms = int(next_date.timestamp() * 1000)
            
            page_token = None
            while True:
                params = {
                    'product_id': product_id,
                    'start_date': start_ms,
                    'end_date': end_ms,
                    'max_results': 500
                }
                
                if status:
                    params['transaction_status'] = status
                
                if page_token:
                    params['page_token'] = page_token
                
                try:
                    response = requests.get(
                        f"{HOTMART_API_BASE}/sales/history",
                        headers={'Authorization': f'Bearer {_self.access_token}'},
                        params=params
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get('items', [])
                        
                        for sale in items:
                            transaction_id = sale.get('purchase', {}).get('transaction')
                            if transaction_id and transaction_id not in seen_transactions:
                                seen_transactions.add(transaction_id)
                                all_sales.append(sale)
                        
                        page_token = data.get('page_info', {}).get('next_page_token')
                        if not page_token or len(items) == 0:
                            break
                    else:
                        break
                except Exception:
                    break
            
            current_date = next_date + timedelta(seconds=1)
        
        return all_sales
    
    def get_approved_sales(self, product_id: str, start_date: datetime, end_date: datetime) -> list:
        approved = self.get_sales_history(product_id, start_date, end_date, 'APPROVED')
        complete = self.get_sales_history(product_id, start_date, end_date, 'COMPLETE')
        
        seen = set()
        result = []
        for sale in approved + complete:
            tid = sale.get('purchase', {}).get('transaction')
            if tid not in seen:
                seen.add(tid)
                result.append(sale)
        
        return result
    
    def get_refunded_sales(self, product_id: str, start_date: datetime, end_date: datetime) -> list:
        refund_statuses = ['REFUNDED', 'PARTIALLY_REFUNDED', 'CHARGEBACK', 'PROTESTED']
        all_refunds = []
        seen = set()
        
        for status in refund_statuses:
            refunds = self.get_sales_history(product_id, start_date, end_date, status)
            for sale in refunds:
                tid = sale.get('purchase', {}).get('transaction')
                if tid not in seen:
                    seen.add(tid)
                    all_refunds.append(sale)
        
        return all_refunds
