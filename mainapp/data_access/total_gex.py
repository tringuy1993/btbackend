from django.db import connection
from ..data_backend.sql.queries import queries_select, queries_greek, queries_from, queries_vanna, queries_greek_all
from psycopg2.extensions import AsIs


def get_notional_greeks_0dte(tables: str, trade_date:str, expiration:str, trade_time:str, greek:str, all_greeks:bool):

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


        



