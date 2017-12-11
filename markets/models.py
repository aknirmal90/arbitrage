import pytz
from django.db import models


class Coin(models.Model):
    name = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return self.name


class Exchange(models.Model):

    exch_balance_enabled = models.BooleanField(null=False, blank=False)
    exch_code = models.CharField(max_length=10, null=False, blank=False)
    exch_fee = models.DecimalField(max_digits=14, decimal_places=6)
    exch_id = models.IntegerField(null=False, blank=False)
    exch_name = models.CharField(max_length=80, null=False, blank=False)
    exch_trade_enabled = models.BooleanField(null=False, blank=False)
    exch_url = models.CharField(max_length=160, null=False, blank=False)

    is_user_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.exch_name


class Market(models.Model):

    exchange = models.ForeignKey(Exchange)
    mkt_id = models.IntegerField(null=False, blank=False)
    mkt_name = models.CharField(max_length=20, null=False, blank=False)
    exchmkt_id = models.IntegerField(null=False, blank=False)
    currency_one = models.CharField(max_length=10, null=True, blank=True)
    currency_two = models.CharField(max_length=10, null=True, blank=True)    

    is_user_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.mkt_name} on {self.exchange.exch_name}'

    class Meta:
        unique_together = ('exchange', 'mkt_id')


class Ticker(models.Model):

    market = models.ForeignKey(Market, limit_choices_to={'is_user_enabled': True})
    last_trade = models.DecimalField(max_digits=36, decimal_places=18)
    high_trade = models.DecimalField(max_digits=36, decimal_places=18)
    low_trade = models.DecimalField(max_digits=36, decimal_places=18)
    current_volume = models.DecimalField(max_digits=36, decimal_places=18)
    timestamp = models.DateTimeField(null=False, blank=False)
    ask = models.DecimalField(max_digits=36, decimal_places=18)
    bid = models.DecimalField(max_digits=36, decimal_places=18)

    def __str__(self):
        _ts = self.timestamp.astimezone(pytz.timezone('Asia/Kolkata'))
        return f'{self.market}, {_ts}'
