from django.urls import path
from .views import portfolio_view, asset_create, transaction_create, dividend_create

urlpatterns = [
    # path('portfolio/', portfolio_view , name='portfolio'),
    path('', portfolio_view , name='portfolio'),
    path('portfolio/ticker_new/', asset_create, name='ticker'),
    path('portfolio/transaction_new/', transaction_create, name='transaction'),
    path('portfolio/dividend_new/', dividend_create, name='dividend'),
]
