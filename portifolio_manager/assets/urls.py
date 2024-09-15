from django.urls import path
from .views import (portfolio_view, asset_create, asset_list, asset_update, asset_delete, transaction_create, dividend_create,
                    load_tickers, load_dividends)

urlpatterns = [
    # path('', portfolio_view , name='portfolio'),
    path('', portfolio_view, name='portfolio'),
    path('tickers/', asset_list, name='ticker_list'),
    path('ticker_new/', asset_create, name='ticker_new'),
    path('ticker_update/<int:pk>/', asset_update, name='ticker_update'),
    path('ticker_delete/<int:pk>/', asset_delete, name='ticker_delete'),
    path('transaction_new/', transaction_create, name='transaction'),
    path('dividend_new/', dividend_create, name='dividend'),
    path('ajax/load-tickers/', load_tickers, name='ajax_load_tickers'),
    path('dividends/', load_dividends, name='dividend_list'),
]
