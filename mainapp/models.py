from django.db import models

# Create your models here.
class ZDTEDates(models.Model):
    quote_datetime = models.DateField(primary_key=True)
    class Meta:
        managed = False
        db_table = 'zdte_dates'

class NotionalGreeks(models.Model):
    auto_id = models.BigAutoField(primary_key=True, serialize=False)
    bid = models.FloatField()
    quote_datetime = models.DateTimeField()
    expiration = models.DateField()
    option_type = models.BooleanField()
    strike = models.FloatField()
    o_open = models.FloatField()
    o_high = models.FloatField()
    o_low = models.FloatField()
    o_close = models.FloatField()
    trade_volume = models.IntegerField()
    bid_size = models.IntegerField()
    ask_size = models.IntegerField()
    ask = models.FloatField()
    underlying_bid = models.FloatField()
    underlying_ask = models.FloatField()
    implied_underlying_price = models.FloatField()
    active_underlying_price = models.FloatField()
    implied_volatility = models.FloatField()
    delta = models.FloatField()
    gamma = models.FloatField()
    theta = models.FloatField()
    vega  = models.FloatField()
    rho = models.FloatField()
    oi = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dev_spxw_data_p20210803'


class PartitionedTable(models.Model):
    table_name = models.TextField()
    partition_name = models.TextField()

    class Meta:
        managed = False
        db_table = 'spxw_data'

    @classmethod
    def get_partitions(cls):
        """
        Returns a list of all partitioned tables for spxw_data.
        """
        return cls.objects.filter(table_name='spxw_data', partition_name__startswith='spxw_data_p').all()


