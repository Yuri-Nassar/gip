from django.db import models

class Asset(models.Model):
    TYPE_CHOICES = (
        ('STOCK', 'Ação'),
        ('FII', 'Fundo Imobiliário'),
    )
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10, unique=True)
    asset_type = models.CharField(max_length=5, choices=TYPE_CHOICES)

    class Meta:
        app_label = 'assets'

    def __str__(self):
        return f"{self.ticker}"
    
class AssetWallet(models.Model):
    TYPE_CHOICES = (
        ('STOCK', 'Ação'),
        ('FII', 'Fundo Imobiliário'),
    )
    # asset_type = models.CharField(max_length=5, choices=TYPE_CHOICES, default='STOCK')

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    money_invested = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_quantity = models.IntegerField(default=0)
    asset_type = models.CharField(max_length=5)#, default='STOCK')

    class Meta:
        app_label = 'assets'
    
    def __str__(self):
        return f"ticker:{self.asset}"

class Transaction(models.Model):
    ACTION_CHOICES = (
        ('BUY', 'Compra'),
        ('SELL', 'Venda'),
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    
    class Meta:
            app_label = 'assets'

    def __str__(self):
        return f"{self.get_action_display()} - {self.asset.ticker} - {self.quantity} @ {self.price}"

class Dividend(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    class Meta:
        app_label = 'assets'

    def __str__(self):
        return f"Rendimento - {self.asset.ticker} - {self.amount}"