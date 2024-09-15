from django.db import models

TICKER_TYPE_CHOICES = (
    ('STOCK', 'Ação'),
    ('FII', 'Fundo Imobiliário'),
)

class Asset(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=6, unique=True)
    cnpj   = models.CharField(max_length=18, blank=True)
    asset_type = models.CharField(max_length=5, choices=TICKER_TYPE_CHOICES)

    class Meta:
        app_label = 'assets'

    def __str__(self):
        return f"{self.ticker}"
    
class AssetWallet(models.Model):
    ticker_code    = models.CharField(max_length=6, unique=True)
    average_price  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    money_invested = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_quantity = models.IntegerField(default=0)
    asset_type = models.CharField(max_length=5)

    class Meta:
        app_label = 'assets'
    
    def __str__(self):
        return f"{self.ticker_code}"

class Transaction(models.Model):
    ACTION_CHOICES = (
        ('BUY', 'Compra'),
        ('SELL', 'Venda'),
    )
    
    ticker_type = models.CharField(max_length=5, choices=TICKER_TYPE_CHOICES)
    ticker_code = models.CharField(max_length=6)
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    
    class Meta:
            app_label = 'assets'

    def __str__(self):
        return f"{self.ticker_code}"

class Dividend(models.Model):
    rendimento_choices = [
        ('dividendo', 'Dividendo'),
        ('jscp', 'JSCP'),
        ('rendimento', 'Rendimento'),
    ]
    
    ticker_type = models.CharField(max_length=5, choices=TICKER_TYPE_CHOICES)
    rendimento_type = models.CharField(max_length=10, choices=rendimento_choices)
    ticker_code = models.CharField(max_length=6)
    money = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    class Meta:
        app_label = 'assets'

    def __str__(self):
        return f"{self.ticker_code}"