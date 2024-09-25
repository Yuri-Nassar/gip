import pandas as pd
import plotly.graph_objects as go

def plot_historical_dividends(df):
    df = df.sort_values(by=['ticker_type', 'date'], ascending=[False, True])
    df['date'] = pd.to_datetime(df['date'])
    # df['month_year'] = df['date'].dt.to_period('M').strtime('%m/%Y').astype(str)
    df['month_year'] = df['date'].dt.strftime('%m/%Y').astype(str)
    df['ticker_type'] = df['ticker_type'].map({'STOCK':'Ações', 'FII':'FII', 3:'ETF', 4:'ETF Cotas'})
    df = df.drop(columns=['date'])

    # Agrupando os dados por mês/ano e tipo de ativo
    grouped = df.groupby(['month_year', 'ticker_type']).sum()\
                .unstack().fillna(0)

    # Criando o gráfico de barras empilhadas
    fig = go.Figure()

    if len(df) != 0:
        for ticker_type in grouped['money'].columns.sort_values(ascending=False):
            y = grouped['money'][ticker_type]
            fig.add_trace(go.Bar(
                name=ticker_type,
                x=grouped.index.astype(str).tolist(),
                y=y,
                text=y,
                textposition='auto'
            ))

    fig.update_layout(width=1300, height=300,
        plot_bgcolor='white',
        barmode='stack',
        title='Dividendos por mês',
        # xaxis_title='Data (Mês/Ano)',
        yaxis_title='Valor (R$)',
        legend_title='Tipo de Ativo',
        margin=dict(l=0, r=0, t=30, b=0), # Remove margens
        legend=dict(
            orientation="h",  # Orientação horizontal
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    # Configurando o gráfico para ser responsivo
    config = {'responsive': True}

    # Convertendo o gráfico para HTML
    graph_div = fig.to_html(full_html=False, config=config)
    return graph_div

def plot_stack_bar(df:pd.DataFrame, x_column:str, y_column:str, color_column:str, groupby:list = [], xaxis_title:str = "", yaxis_title:str = "", legend_title:str = "", title:str = "", width:int = 1300, height:int = 300):
    
    if x_column == 'date':
        df[x_column] = pd.to_datetime(df[x_column])
        df[x_column] = df[x_column].dt.strftime('%m/%Y').astype(str)
    
    # Agrupando os dados por mês/ano e tipo de ativo
    if len(groupby) > 0:
        grouped = df.groupby([x_column, color_column]).sum()\
                    .unstack().fillna(0)
    else:
        grouped = df.groupby(groupby).sum()\
                    .unstack().fillna(0)

    # Criando o gráfico de barras empilhadas
    fig = go.Figure()

    if len(df) != 0:
        for trace_name in grouped[y_column].columns.sort_values(ascending=False):
            y = grouped[y_column][trace_name]
            fig.add_trace(go.Bar(
                name=trace_name,
                x=grouped.index.astype(str).tolist(),
                y=y,
                # text=[val if val != 0 else '' for val in y],
                text=y,
                textposition='outside'
            ))

    fig.update_layout(width=width, height=height,
        plot_bgcolor='white',
        barmode='group',
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=0, r=0, t=0, b=0), # Remove margens
        legend_title=legend_title,
        legend=dict(
            orientation="h",  # Orientação horizontal
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
        )
    
    # Configurando o gráfico para ser responsivo
    config = {'responsive': True}

    # Convertendo o gráfico para HTML
    graph_div = fig.to_html(full_html=False, config=config)
    return graph_div