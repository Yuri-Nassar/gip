from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Asset, AssetWallet, Transaction, Dividend
from .forms import AssetForm, TransactionForm, DividendForm

import pandas as pd
from datetime import datetime
from collections import defaultdict
import plotly.graph_objects as go

def is_ticker_name_valid(ticker_name, type_asset):
    if type_asset == 'FII':
        if len(ticker_name) != 6:
            return False
        if (len(ticker_name) != 6) & (ticker_name != ticker_name.upper()):
            return False
        if ticker_name[-2:] != '11':
            return False

        return True
    else:
        if len(ticker_name) not in [5,6]:
            return False
        if (len(ticker_name) not in [5,6]) & (ticker_name != ticker_name.upper()):
            return False
        if (ticker_name[-1:] != '3') & (ticker_name[-2:] != '11'):
            return False

        return True


def portfolio_view(request):
    # stocks = Asset.objects.filter(asset_type='STOCK')
    stocks = AssetWallet.objects.filter(asset_type='STOCK')
    # fiis = Asset.objects.filter(asset_type='FII')
    fiis = AssetWallet.objects.filter(asset_type='FII')
    
    # print(f'AssetWallet-A: {stocks}')
    # print(f'AssetWallet-F: {fiis}')

    stock_data = []
    for stock in stocks:
        if stock.total_quantity > 0:
            stock_data.append({
                'asset': stock.asset,
                'total_quantity': stock.total_quantity,
                'average_price': stock.average_price,
                'money_invested': stock.money_invested,
            })
    
    fiis_data = []
    # for fii in fiis:
    for fii in fiis:
        if fii.total_quantity > 0:
            fiis_data.append({
                'asset': fii.asset,
                'total_quantity': fii.total_quantity,
                'average_price': fii.average_price,
                'money_invested': fii.money_invested,
            })
    
    context = {
        'stocks': stock_data,
        'fiis': fiis_data,
    }
    return render(request, 'assets/portfolio.html', context)

def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data.get('ticker')
            asset_type = form.cleaned_data.get('asset_type')

            print(f"Criando ativo -> ticker: {ticker}, asset_type: {asset_type}")
            if not is_ticker_name_valid(ticker, asset_type):
                form.add_error('ticker', 'Formato inválido. Ex.: ADBE3, ADBE4 e ADBE11.')
            else:
                form.save()
                return redirect('portfolio')
    else:
        form = AssetForm()
    return render(request, 'assets/ticker_form.html', {'form': form})

def transaction_create(request):
    if request.method == 'POST':
        _asset = request.POST.get('asset')
        _action = request.POST.get('action')
        _date = request.POST.get('date')
        _quantity = request.POST.get('quantity')

        print(f"_asset: {_asset}, _action: {_action}, _date: {_date}, _quantity: {_quantity}")

        obj = Asset.objects.get(id=_asset)
        print(f"obj: {obj}")

        form = TransactionForm(request.POST)
        if form.is_valid():
            # Update AssetWallet
            asset_wallet, created = AssetWallet.objects.get_or_create(
                asset=obj, asset_type=obj.asset_type
            )
            
            # asset_wallet, created = AssetWallet.objects.get(asset=_asset)
            print(f"created: {created}")
            print(f"asset_wallet.asset: {asset_wallet.asset}, asset_wallet.asset_type: {asset_wallet.asset_type}, asset_wallet.total_quantity: {asset_wallet.total_quantity}")

            try:
                d = datetime.strptime(_date, '%Y-%m-%d')
            except:
                d = None

            if (int(asset_wallet.total_quantity) < int(_quantity)) & (_action == 'SELL'):
                form.add_error("quantity", f"Quantidade de venda ({_quantity}) maior que a quantidade disponível ({asset_wallet.total_quantity}).")
            elif not isinstance(d, datetime):
                form.add_error("date", f"Data inválida. Formato aceito: YYYY-MM-DD")
            else:
                transaction = form.save()

                if transaction.action == 'BUY':
                    total_quantity = asset_wallet.total_quantity + transaction.quantity
                    asset_wallet.average_price = ((asset_wallet.average_price * asset_wallet.total_quantity) + 
                                                (transaction.price * transaction.quantity)
                                                ) / total_quantity
                    asset_wallet.total_quantity = total_quantity
                    asset_wallet.money_invested += transaction.price * transaction.quantity
                elif transaction.action == 'SELL':
                    asset_wallet.total_quantity -= transaction.quantity
                    asset_wallet.money_invested = asset_wallet.average_price * asset_wallet.total_quantity
                    if asset_wallet.total_quantity == 0:
                        asset_wallet.average_price = 0
                        asset_wallet.money_invested = 0

                asset_wallet.save()

                return redirect('portfolio')
    else:
        form = TransactionForm()
    return render(request, 'assets/transaction_form.html', {'form': form})

def dividend_create(request):
    if request.method == 'POST':
        form = DividendForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portfolio')
    else:
        form = DividendForm()
    return render(request, 'assets/dividend_form.html', {'form': form})

def load_tickers(request):
    ticker_type = request.GET.get('ticker_type')
    tickers = Asset.objects.filter(asset_type=ticker_type).all()
    return JsonResponse(list(tickers.values('id','ticker')), safe=False)

def load_dividends(request):
        dividends = Dividend.objects.all()

        _dividendos_df = pd.DataFrame(dividends.values())
        plot_dividens = create_plot_dividends(_dividendos_df[['date','ticker_type','money']])
        # print(_dividendos_df)
                
        dividend_data = {}
        for dividend in dividends:
            # _date = str(dividend.date.month)+"/"+str(dividend.date.year)
            _date = dividend.date.strftime('%m/%Y')
            try:
                dividend_data[dividend.ticker_type][dividend.ticker_code][_date] += dividend.money
            except:
                if dividend.ticker_type not in dividend_data:
                    dividend_data[dividend.ticker_type] = {}
                    dividend_data[dividend.ticker_type][dividend.ticker_code] = {_date:0}
                    dividend_data[dividend.ticker_type][dividend.ticker_code][_date] += dividend.money
                elif dividend.ticker_code not in dividend_data[dividend.ticker_type]:
                    dividend_data[dividend.ticker_type][dividend.ticker_code] = {_date:dividend.money}
                    

        context = {
            'dividend_data': dividend_data,
            'plot_dividens': plot_dividens
        }

        return render(request, 'assets/dividends_list.html', context)

def create_plot_dividends(df):
    df = df.sort_values(by=['ticker_type', 'date'], ascending=[False, True])
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M').astype(str)
    df['ticker_type'] = df['ticker_type'].map({'STOCK':'Ações', 'FII':'FII', 3:'ETF', 4:'ETF Cotas'})
    df = df.drop(columns=['date'])

    # Agrupando os dados por mês/ano e tipo de ativo
    grouped = df.groupby(['month_year', 'ticker_type']).sum()\
                .unstack().fillna(0)

    # Criando o gráfico de barras empilhadas
    fig = go.Figure()

    for ticker_type in grouped['money'].columns.sort_values(ascending=False):
        fig.add_trace(go.Bar(
            x=grouped.index.astype(str),
            y=grouped['money'][ticker_type],
            name=ticker_type
        ))

    fig.update_layout(width=1000, height=300,
        plot_bgcolor='white',
        barmode='stack',
        title='Dividendos por Mês e Tipo de Ativo',
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