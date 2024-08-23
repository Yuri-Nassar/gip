from django.contrib import admin
from .models import Asset, AssetWallet, Transaction, Dividend

admin.site.register(Asset)
admin.site.register(AssetWallet)
admin.site.register(Transaction)
admin.site.register(Dividend)
