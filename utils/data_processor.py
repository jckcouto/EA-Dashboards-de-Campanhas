import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

BRT = ZoneInfo('America/Sao_Paulo')

def process_hotmart_sales(sales: list) -> pd.DataFrame:
    if not sales:
        return pd.DataFrame()
    
    processed = []
    for sale in sales:
        purchase = sale.get('purchase', {})
        buyer = sale.get('buyer', {})
        
        order_date_ms = purchase.get('order_date', 0)
        order_date = datetime.fromtimestamp(order_date_ms / 1000, tz=BRT) if order_date_ms else None
        
        processed.append({
            'transaction_id': purchase.get('transaction'),
            'order_date': order_date,
            'status': purchase.get('status'),
            'value': purchase.get('hotmart_fee', {}).get('base', 0),
            'buyer_email': buyer.get('email'),
            'buyer_name': buyer.get('name'),
            'offer_code': purchase.get('offer', {}).get('code')
        })
    
    df = pd.DataFrame(processed)
    
    if 'order_date' in df.columns and not df.empty:
        df = df.sort_values('order_date', ascending=False)
    
    return df

def calculate_sales_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            'total_sales': 0,
            'total_revenue': 0,
            'average_ticket': 0
        }
    
    return {
        'total_sales': len(df),
        'total_revenue': df['value'].sum(),
        'average_ticket': df['value'].mean()
    }

def process_sheets_data(data: list, has_header: bool = True) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()
    
    if has_header and len(data) > 1:
        return pd.DataFrame(data[1:], columns=data[0])
    
    return pd.DataFrame(data)

def group_sales_by_date(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or 'order_date' not in df.columns:
        return pd.DataFrame()
    
    df['date'] = df['order_date'].dt.date
    grouped = df.groupby('date').agg({
        'transaction_id': 'count',
        'value': 'sum'
    }).reset_index()
    
    grouped.columns = ['date', 'sales_count', 'revenue']
    return grouped
