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
        fields = ['ticker_type', 'ticker_code', 'rendimento_type', 'money', 'date']
    
        widgets = {
            'ticker_type': forms.Select(attrs={'class': 'form-control'}),
            'ticker_code': forms.Select(attrs={'class': 'form-control'}),
            'rendimento_type': forms.Select(attrs={'class': 'form-control'}),
            'money': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

        labels = {
            'ticker_type': 'Tipo de ativo',
            'ticker_code': 'Código do Ticker',
            'rendimento_type': 'Tipo de Rendimento',
            'money': 'Valor R$',
            'date': 'Data',
        }    

    def __init__(self, *args, **kwargs):
        super(DividendForm, self).__init__(*args, **kwargs)
        self.fields['ticker_code'].queryset = Asset.objects.none()

        if 'ticker_type' in self.data:
            try:
                ticker_type = self.data.get('ticker_type')
                self.fields['ticker_code'].queryset = Asset.objects.filter(asset_type=ticker_type)
            except (ValueError, TypeError):
                pass  # ignore errors from invalid data
        elif self.instance.pk:
            self.fields['ticker_code'].queryset = self.instance.ticker_code.asset_set