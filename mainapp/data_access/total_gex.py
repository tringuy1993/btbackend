from django.db import connection
from ..data_backend.sql.queries import queries_select, queries_greek, queries_from, queries_vanna, queries_greek_all, query_avail_partitioned_tables, queries_theo_gamma
from psycopg2.extensions import AsIs


def get_all_partioned_tables():
    with connection.cursor() as curs:

        # Execute query to get all available data
        curs.execute(query_avail_partitioned_tables
                     )
        return [{'partioned_name': d[0][11:]} for d in curs.fetchall()]


def get_theo_gamma(trade_date: str, expiration: str, trade_time: str):
    query_param = {
        "trade_date_time": f'{trade_date} {trade_time}',
        "expiration": expiration,
    }

    with connection.cursor() as curs:
        # Execute query to get all available data
        curs.execute(queries_theo_gamma,
                     query_param,
                     )
        # Get the column names from the cursor description
        columns = [col[0] for col in curs.description]
        # Fetch all rows and convert them to dictionaries with column names as keys
        return [dict(zip(columns, row)) for row in curs.fetchall()]


def get_notional_greeks_0dte(tables: str, trade_date: str, expiration: str, trade_time: str, greek: str, all_greeks: bool):
    # Setting Param
    query_param = {
        "trade_date": trade_date,
        "expiration": expiration,
        "trade_time": trade_time,
        "greek": AsIs(greek),
        "table": AsIs(tables),
    }
    if greek == 'vanna':
        final_queries = queries_select+queries_vanna+queries_from
    else:
        final_queries = queries_select+queries_greek+queries_from

    if all_greeks:
        final_queries = queries_select + queries_greek_all + queries_from

    with connection.cursor() as curs:

        # Execute query to get all available data
        curs.execute(final_queries,
                     query_param,
                     )
        # Get the column names from the cursor description
        columns = [col[0] for col in curs.description]
        # Fetch all rows and convert them to dictionaries with column names as keys
        return [dict(zip(columns, row)) for row in curs.fetchall()]


query_option_chain = """
SELECT * 
FROM %(table)s 
WHERE quote_datetime::time = %(trade_time)s
AND expiration <= %(expiration)s
ORDER BY quote_datetime, expiration, strike
"""


def get_option_chain(table: str, expiration: str, trade_time: str):
    query_param = {
        # "trade_date": trade_date,
        "expiration": expiration,
        "trade_time": trade_time,
        "table": AsIs(table),
    }

    with connection.cursor() as curs:
        curs.execute(query_option_chain, query_param)
        columns = [col[0] for col in curs.description]
        # Fetch all rows and convert them to dictionaries with column names as keys
        # return [dict(zip(columns, row)) for row in curs.fetchall()]
        rows = curs.fetchall()
        # print("ROWS:", rows)
        # Initialize separate lists for option_type=true and option_type=false
        option_type_true = []
        option_type_false = []

        for row in rows:
            # Create a dictionary with column names as keys
            data = dict(zip(columns, row))

            # Check the value of option_type
            if data['option_type'] == True:
                option_type_true.append(data)
            else:
                option_type_false.append(data)

        return {'call': option_type_true, 'put': option_type_false}
