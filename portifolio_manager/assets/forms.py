from django import forms
from .models import Asset, Transaction, Dividend

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'ticker', 'asset_type']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['asset', 'action', 'quantity', 'price', 'date']

class DividendForm(forms.ModelForm):
    class Meta:
        model = Dividend
        fields = ['asset', 'amount', 'date']
