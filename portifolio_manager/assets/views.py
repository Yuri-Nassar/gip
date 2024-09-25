from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import Asset, AssetWallet, Transaction, Dividend
from .forms import AssetForm, TransactionForm, DividendForm
from .plot_graphs import plot_historical_dividends, plot_stack_bar

import pandas as pd
from datetime import datetime
import time
from collections import defaultdict
import plotly.graph_objects as go

def is_ticker_name_valid(ticker, type_ticker):
    t_name = ticker[:4]
    t_code = ticker[4:]
    t_length = len(ticker)
    
    if type_ticker == 'FII':
        if t_length != 6:
            return False, "Verifique se o ticker do ativo possui 6 caracteres."
        if t_name != t_name.upper():
            return False, "Verifique se o ticker possui apenas letras maiúsculas."
        if t_code[-2:] != '11':
            return False, "Verifique se o código está correto."
    elif type_ticker == 'STOCK':
        if t_length not in [5,6]:
            return False, "Verifique se o ticker do ativo possui 5 ou 6 caracteres."
        if t_name != t_name.upper():
            return False, "Verifique se o ticker possui apenas letras maiúsculas."
        if t_code not in ['3','4','11']:
            return False, "Verifique se o código está correto."
    else:
        print(f"Tipo de ativo inválido: {type_ticker}")
        return False, "Tipo de ativo inválido."

    return True, "Válido"

def portfolio_view(request):
    # s_asset = Asset.objects.filter(asset_type='STOCK')
    assets = Asset.objects.all()
    tickers = {}
    for ticker in assets:
        tickers[ticker.ticker] = {'id': ticker.id, 'name': ticker.name, 'type': ticker.asset_type}

    assets = AssetWallet.objects.all()
    stock_data, fiis_data = [], []
    
    for asset in assets:
        data = {'name': tickers[asset.ticker_code]['name'],
                'ticker': asset.ticker_code,
                'total_quantity': asset.total_quantity,
                'average_price': asset.average_price,
                'money_invested': asset.money_invested
                }

        if asset.asset_type == 'STOCK':
            stock_data.append(data)
        else:
            fiis_data.append(data)
    
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

            bool_check , msg = is_ticker_name_valid(ticker, asset_type)
            if not bool_check:
                form.add_error('ticker', msg)
                return render(request, 'assets/ticker_form.html', {'form': form})
            else:
                form.save()
                # messages.add_message(request, messages.SUCCESS, 'Ativo criado com sucesso!')
                print(f"Criando ativo -> ticker: {ticker}, asset_type: {asset_type}")
                messages.add_message(request, messages.SUCCESS, 'Ativo criado com sucesso!')
        else:
            errors = form.errors
            print(f"Erros validação: {errors}")
            
    else:
        form = AssetForm()
    return render(request, 'assets/ticker_form.html', {'form': form})

def asset_list(request):
    assets = Asset.objects.all()
    return render(request, 'assets/ticker_list.html', {'assets': assets})

def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            
            form.save()
            # messages.success(request, 'Ativo atualizado com sucesso!')
            print("Ativo atualizado!")
            messages.add_message(request, messages.SUCCESS, 'Ativo atualizado com sucesso!')

    else:
        form = AssetForm(instance=asset)
    return render(request, 'assets/ticker_update.html', {'form': form})#, 'messages': messages.get_messages(request)})

def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        print(f"Deletando ativo -> ticker: {asset.ticker}, asset_type: {asset.asset_type}")
        messages.add_message(request, messages.SUCCESS, f'O ativo {asset.name} foi deletado com sucesso.')
    else:
        print('Ação não permitida.')
        messages.error(request, 'Ação não permitida.')

    return asset_list(request)

def transaction_create(request):
    if request.method == 'POST':
        _asset = request.POST.get('ticker_code')
        _action = request.POST.get('action')
        _date = request.POST.get('date')
        _quantity = request.POST.get('quantity')

        print(f"_asset: {_asset}, _action: {_action}, _date: {_date}, _quantity: {_quantity}")

        # obj = Asset.objects.get(id=_asset)
        obj = Asset.objects.get(ticker=_asset)
        print(f"obj: {obj}")
        print(f"obj.asset_type: {obj.asset_type}, obj.ticker: {obj.ticker}")

        form = TransactionForm(request.POST)
        if form.is_valid():
            # Update AssetWallet
            asset_wallet, created = AssetWallet.objects.get_or_create(
                ticker_code=obj.ticker, asset_type=obj.asset_type
            )
            
            # asset_wallet, created = AssetWallet.objects.get(asset=_asset)
            print(f"created: {created}")
            print(f"asset_wallet.asset: {asset_wallet.ticker_code}, asset_wallet.asset_type: {asset_wallet.asset_type}, asset_wallet.total_quantity: {asset_wallet.total_quantity}")

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
        dividendos_df = pd.DataFrame(dividends.values())

        if len(dividends) == 0:
            dividendos_df = pd.DataFrame(columns=['date','ticker_type','money'])
        
        plot_dividens = plot_historical_dividends(dividendos_df[['date','ticker_type','money']].copy())

        plot_dividends_stocks = plot_stack_bar(dividendos_df[dividendos_df['ticker_type']=='STOCK'].copy(), 'date', 'money', 'ticker_code', ['date', 'ticker_code'], yaxis_title='Valor (R$)', legend_title='Ações', title='Dividendos por Ação', height=360)
        plot_dividends_fiis = plot_stack_bar(dividendos_df[dividendos_df['ticker_type']=='FII'].copy(), 'date', 'money', 'ticker_code', ['date', 'ticker_code'], yaxis_title='Valor (R$)', legend_title='FIIs', title='Dividendos por FII', height=360)


        # dividend_data = {}
        # for dividend in dividends:
        #     # _date = str(dividend.date.month)+"/"+str(dividend.date.year)
        #     _date = dividend.date.strftime('%m/%Y')
        #     try:
        #         dividend_data[dividend.ticker_type][dividend.ticker_code][_date] += dividend.money
        #     except:
        #         if dividend.ticker_type not in dividend_data:
        #             dividend_data[dividend.ticker_type] = {}
        #             dividend_data[dividend.ticker_type][dividend.ticker_code] = {_date:dividend.money}
        #         elif dividend.ticker_code not in dividend_data[dividend.ticker_type]:
        #             dividend_data[dividend.ticker_type][dividend.ticker_code] = {_date:dividend.money}
        #         elif _date not in dividend_data[dividend.ticker_type][dividend.ticker_code]:
        #             dividend_data[dividend.ticker_type][dividend.ticker_code][_date] = dividend.money
        
        context = {
            # 'dividend_data': dividend_data,
            'plot_dividens': plot_dividens,
            'plot_dividends_stocks': plot_dividends_stocks,
            'plot_dividends_fiis': plot_dividends_fiis,
        }

        return render(request, 'assets/dividends_list.html', context)