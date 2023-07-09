from django.db import connection
from psycopg2.extensions import AsIs

query = """
        SELECT * FROM %(table)s
        WHERE expiration = %(expiration)s
            AND quote_datetime = %(quote_datetime)s
            AND (
                {conditions}
            )
        """
condition_template = "(strike = %(strike_{i})s AND option_type = %(option_type_{i})s)"

def queryOrder (table:str, expiration: str, quote_datetime:str, option_legs: list):
    conditions_sql = []
    query_params = {
            "table": AsIs(table),
            "expiration": expiration,
            "quote_datetime": quote_datetime
        }
    for i, condition in enumerate(option_legs):
            param_name_strike = f"strike_{i}"
            param_name_option_type = f"option_type_{i}"

            query_params[param_name_strike] = condition["strike"]
            query_params[param_name_option_type] = condition["option_type"]

            condition_sql = condition_template.format(i=i)
            conditions_sql.append(condition_sql)
    
    conditions_combined = " OR ".join(conditions_sql)
    full_query = query.format(conditions=conditions_combined)
        
    with connection.cursor() as cursor:
        try:
                cursor.execute(full_query, query_params)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
                print(str(e))