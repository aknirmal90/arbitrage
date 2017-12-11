from django.contrib import admin
from markets.models import Exchange, Market, Ticker


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):

	readonly_fields = list(field.name for field in Exchange._meta.get_fields() if field.name != 'market')
	list_display = list(field.name for field in Exchange._meta.get_fields() if field.name != 'market')
	actions = ('enable_exchange', 'disable_exchange')

	def enable_exchange(self, request, queryset):
		for exchange in queryset.iterator():
			exchange.is_user_enabled = True
			exchange.save()
	enable_exchange.short_description = 'Enable Exchanges'

	def disable_exchange(self, request, queryset):
		for exchange in queryset.iterator():
			exchange.is_user_enabled = False
			exchange.save()			
	disable_exchange.short_description = 'Disable Exchanges'


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):

	readonly_fields = list(field.name for field in Market._meta.get_fields() if field.name not in ('sender', 'reciever', 'ticker'))
	list_display = list(field.name for field in Market._meta.get_fields() if field.name not in ('sender', 'reciever', 'ticker'))

	list_filter = ('exchange', 'currency_one', 'currency_two')
	search_fields = ('=mkt_name',)
	actions = ('enable_market', 'disable_market')

	def enable_market(self, request, queryset):
		for market in queryset.iterator():
			market.is_user_enabled = True
			market.save()
	enable_market.short_description = 'Enable Markets'

	def disable_market(self, request, queryset):
		for market in queryset.iterator():
			market.is_user_enabled = False
			market.save()			
	disable_market.short_description = 'Disable Markets'


@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
	
	list_filter = ('market',)
