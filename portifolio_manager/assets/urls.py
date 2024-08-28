from django.urls import path
from .views import portfolio_view, asset_create, transaction_create, dividend_create

urlpatterns = [
    # path('', portfolio_view , name='portfolio'),
    path('', portfolio_view , name='portfolio'),
    path('ticker_new/', asset_create, name='ticker'),
    path('ransaction_new/', transaction_create, name='transaction'),
    path('dividend_new/', dividend_create, name='dividend'),
]
