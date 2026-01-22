import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_sales_line_chart(df: pd.DataFrame, primary_color: str = '#F94E03', 
                           secondary_color: str = '#FB7B3D') -> go.Figure:
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['sales_count'],
        mode='lines+markers',
        name='Vendas',
        line=dict(color=primary_color, width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Vendas por Dia',
        xaxis_title='Data',
        yaxis_title='Quantidade de Vendas',
        template='plotly_white',
        font=dict(family='Montserrat'),
        hovermode='x unified'
    )
    
    return fig

def create_revenue_bar_chart(df: pd.DataFrame, primary_color: str = '#F94E03') -> go.Figure:
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['revenue'],
        name='Faturamento',
        marker_color=primary_color
    ))
    
    fig.update_layout(
        title='Faturamento por Dia',
        xaxis_title='Data',
        yaxis_title='Faturamento (R$)',
        template='plotly_white',
        font=dict(family='Montserrat'),
        hovermode='x unified'
    )
    
    return fig

def create_pie_chart(labels: list, values: list, colors: list = None) -> go.Figure:
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors
    ))
    
    fig.update_layout(
        template='plotly_white',
        font=dict(family='Montserrat')
    )
    
    return fig

def create_dark_theme_chart(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#FFFFFF')
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#FFFFFF')
        )
    )
    return fig
