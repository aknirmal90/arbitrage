import time
import logging
from celery import Task
from markets.forms import ExchangeForm, MarketForm, TickerForm
from markets.models import Exchange, Market, Ticker
from coinigy.base import Coiningy


logger = logging.getLogger(__name__)


class SyncExchanges(Task):

	def run(self, *args, **kwargs):
		client = Coiningy()

		response = client.prepare_request('exchanges', method='POST', params={}).json()
		for ex in response['data']:
			try:
				exchange_instance = Exchange.objects.get(exch_id=int(ex['exch_id']))
				exchange_form = ExchangeForm(ex, instance=exchange_instance)
				instance = exchange_form.save()
				logger.info(f'<Exchange> {ex["exch_name"]} Updated')
			except Exchange.DoesNotExist:
				exchange_form = ExchangeForm(ex)
				if exchange_form.is_valid():
					exchange_form.save()
					logger.info(f'<Exchange> {ex["exch_name"]} Created')
				else:
					logger.info(f'<Exchange> Could not updated {exchange_form.errors}')


class SyncMarkets(Task):

	def run(self, *args, **kwargs):
		client = Coiningy()

		exchanges = Exchange.objects.all()
		for exchange in exchanges.iterator():

			response = client.prepare_request('markets', method='POST', params={'exch_code':exchange.exch_code}).json()
			for mkt in response['data']:
				try:
					mkt['exchange'] = exchange.id

					try:
						mkt['currency_one'] = mkt.get('mkt_name').split('/')[0]
						mkt['currency_two'] = mkt.get('mkt_name').split('/')[1]
					except Exception:
						pass

					market_instance = Market.objects.get(mkt_id=int(mkt['mkt_id']), exchange=exchange)
					market_form = MarketForm(mkt, instance=market_instance)
					instance = market_form.save()
					logger.info(f'<Market> {mkt["mkt_name"]} Updated')
				except Market.DoesNotExist:
					mkt['exchange'] = exchange.id

					try:
						mkt['currency_one'] = mkt.get('mkt_name').split('/')[0]
						mkt['currency_two'] = mkt.get('mkt_name').split('/')[1]
					except Exception:
						pass

					market_form = MarketForm(mkt)
					if market_form.is_valid():
						market_form.save()
						logger.info(f'<Market> {mkt["mkt_name"]} Created')
					else:
						logger.info(f'<Market> Could not updated {market_form.errors}')

			time.sleep(0.5)


class SyncTicker(Task):

	def run(self, *args, **kwargs):
		client = Coiningy()

		markets = Market.objects.filter(is_user_enabled=True, exchange__is_user_enabled=True)
		for market in markets.iterator():			
			try:
				response = client.prepare_request(resource='ticker', 
													method='POST', 
													params={"exchange_code": market.exchange.exch_code, "exchange_market": market.mkt_name}
												  ).json()
				payload = response['data'][0]
				payload['market'] = market.id
				ticker_form = TickerForm(payload)
				if ticker_form.is_valid():
					ticker_form.save()
					continue
				else:
					logger.info(f'<Ticker> {market.mkt_name} Created')
			except Exception as e:
				logger.info(f'<Ticker> {market.mkt_name} Unknown Exception {e} on {market}')
