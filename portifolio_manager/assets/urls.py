from django.urls import path
from .views import portfolio_view, asset_create, transaction_create, dividend_create, load_tickers, load_dividends

urlpatterns = [
    # path('', portfolio_view , name='portfolio'),
    path('', portfolio_view , name='portfolio'),
    path('ticker_new/', asset_create, name='ticker'),
    path('transaction_new/', transaction_create, name='transaction'),
    path('dividend_new/', dividend_create, name='dividend'),
    path('ajax/load-tickers/', load_tickers, name='ajax_load_tickers'),
    path('dividends/', load_dividends, name='dividend_list'),
]
