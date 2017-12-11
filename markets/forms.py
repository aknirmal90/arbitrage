from django import forms
from decimal import Decimal, ROUND_UP
from markets.models import Exchange, Market, Ticker


class ExchangeForm(forms.ModelForm):

	class Meta:
		model = Exchange
		fields = (
		'exch_balance_enabled',
		'exch_code',
		'exch_fee',
		'exch_id',
		'exch_name',
		'exch_trade_enabled',
		'exch_url',
		)


class MarketForm(forms.ModelForm):

	class Meta:
		model = Market
		fields = (
		'exchange',
		'mkt_id',
		'mkt_name',
		'exchmkt_id',
		'currency_one',
		'currency_two',
		)


class TickerForm(forms.ModelForm):

	class Meta:
		model = Ticker
		fields = (
		'market',
		'last_trade',
		'high_trade',
		'low_trade',
		'current_volume',
		'timestamp',
		'ask',
		'bid',
		)
