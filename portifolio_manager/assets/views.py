from django.shortcuts import render, redirect
from .models import Asset, AssetWallet, Transaction, Dividend
from .forms import AssetForm, TransactionForm, DividendForm
from datetime import datetime

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
