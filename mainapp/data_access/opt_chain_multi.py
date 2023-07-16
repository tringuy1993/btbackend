from functools import lru_cache
from django.db import connection
from ..data_backend.sql.queries_opt_chain import query_data
from psycopg2.extensions import AsIs
from ..utility.calc_functions import create_dataframe, calc_gamma_ex_tn2
import matplotlib.pyplot as plt


class NameMapper(object):
    MAPPING = {  # Define all mappings in this dict.
        "symbol": "und_symbol",
        "expiration": "exp_date_str",
        "option_type": "putCall",
        "strike": "strikePrice",
        "o_open": "openPrice",
        "o_high": "highPrice",
        "o_low": "lowPrice",
        "o_close": "closePrice",
        "trade_volume": "totalVolume",
        "bid_size": "bidSize",
        "ask_size": "askSize",
        "active_underlying_price": "underlying_price",
        "implied_volatility": "volatility",
        "open_interest": "openInterest",
        "days_to_expiration": "dte_calc"
    }

    @classmethod
    @lru_cache(maxsize=15)
    def get_mapping(cls, db_column):
        try:
            target_name = cls.MAPPING[db_column]
        except KeyError:
            target_name = db_column

        return target_name


def get_option_chain_df(table, quote_datetime, expiration):
    # Query Trading Minute and Expiration Date only.
    query_param = {
        "table_name": AsIs(table),
        "quote_datetime": quote_datetime,
        "expiration_date": expiration}
    

    with connection.cursor() as cursor:
        try:
            cursor.execute(query_data, query_param)
            columns = [col[0] for col in cursor.description]
            new_columns = [NameMapper.get_mapping(col) for col in columns]
            data = [dict(zip(new_columns, row)) for row in cursor.fetchall()]

            return data
        except Exception as e:

            print("Error GetOPtion_Chain:", str(e))



if __name__ == "__main__":
    from datetime import datetime

    test_trading_minute = datetime(year=2021,
                                   month=5,
                                   day=28,
                                   hour=10,
                                   minute=0,
                                   second=0)

    # test_opt_chain = get_option_chain(trading_minute=test_trading_minute)
