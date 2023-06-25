query_avail_partitioned_tables = """SELECT inhrelid::regclass
                        FROM pg_inherits
                        WHERE inhparent = 'spxw_data'::regclass
                        ORDER BY inhrelid::regclass ASC;
                        """

zdte_dates = """
CREATE TABLE zdte_dates AS
SELECT DISTINCT quote_datetime::date
FROM dev_spxw_data
WHERE quote_datetime::date = expiration;
"""

spot_price = """
    SELECT DISTINCT active_underlying_price FROM %(table_name)s
    WHERE quote_datetime::time = %(trade_time)s
    ;
"""

queries_theo_gamma = """
    SELECT * FROM calc_theo_gamma(%(trade_date_time)s, %(expiration)s)
"""


queries_select = """
    SELECT 
        ROW_NUMBER() OVER () AS id
        ,strike
        ,active_underlying_price
        ,SUM(CASE WHEN option_type = true THEN oi ELSE 0 END) AS c_oi
        ,SUM(CASE WHEN option_type = true THEN trade_volume ELSE 0 END) AS c_trade_volume
        ,SUM(CASE WHEN option_type = false THEN oi ELSE 0 END) AS p_oi
        ,SUM(CASE WHEN option_type = false THEN trade_volume ELSE 0 END) AS p_trade_volume
"""
queries_greek = """
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('%(greek)s', %(greek)s, oi, active_underlying_price, option_type) ELSE 0 END)) AS c_%(greek)s_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('%(greek)s', %(greek)s, oi, active_underlying_price, option_type) ELSE 0 END)) AS p_%(greek)s_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('%(greek)s', %(greek)s, oi, active_underlying_price, option_type) ELSE 0 END) + 
            SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('%(greek)s', %(greek)s, oi, active_underlying_price, option_type) ELSE 0 END)) AS total_%(greek)s_notion_expo
"""

queries_vanna = """
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('%(greek)s', vanna(quote_datetime, expiration, strike, active_underlying_price, implied_volatility), oi, active_underlying_price, option_type) ELSE 0 END)) AS c_vanna_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('%(greek)s', vanna(quote_datetime, expiration, strike, active_underlying_price, implied_volatility), oi, active_underlying_price, option_type) ELSE 0 END)) AS p_vanna_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('%(greek)s', vanna(quote_datetime, expiration, strike, active_underlying_price, implied_volatility), oi, active_underlying_price, option_type) ELSE 0 END) + 
            SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('%(greek)s', vanna(quote_datetime, expiration, strike, active_underlying_price, implied_volatility), oi, active_underlying_price, option_type) ELSE 0 END)) AS total_vanna_notion_expo
"""
queries_from = """
    FROM %(table)s
    WHERE 
        quote_datetime::date = %(trade_date)s
        AND quote_datetime::time = %(trade_time)s
        AND expiration <= %(expiration)s
    GROUP BY strike, active_underlying_price
    ORDER BY strike ASC;
"""


greeks = ['gamma', 'delta', 'vanna', 'theta', 'vega', 'rho']
queries_greek_all = ""
for greek in greeks:
    if greek == 'vanna':
        query = f"""
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('{greek}', vanna(quote_datetime, expiration, strike, active_underlying_price, implied_volatility), oi, active_underlying_price, option_type) ELSE 0 END)) AS c_{greek}_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('{greek}', vanna(quote_datetime, expiration, strike, active_underlying_price, implied_volatility), oi, active_underlying_price, option_type) ELSE 0 END)) AS p_{greek}_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('{greek}', vanna(quote_datetime, expiration, strike, active_underlying_price, implied_volatility), oi, active_underlying_price, option_type) ELSE 0 END) + 
            SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('{greek}', vanna(quote_datetime, expiration, strike, active_underlying_price, implied_volatility), oi, active_underlying_price, option_type) ELSE 0 END)) AS total_{greek}_notion_expo
        """
    else:
        query = f"""
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('{greek}', {greek}, oi, active_underlying_price, option_type) ELSE 0 END)) AS c_{greek}_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('{greek}', {greek}, oi, active_underlying_price, option_type) ELSE 0 END)) AS p_{greek}_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('{greek}', {greek}, oi, active_underlying_price, option_type) ELSE 0 END) + 
            SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('{greek}', {greek}, oi, active_underlying_price, option_type) ELSE 0 END)) AS total_{greek}_notion_expo
        """
    queries_greek_all += query

queries = """
    SELECT 
        ROW_NUMBER() OVER () AS id
        ,strike
        ,%(spot_price)s as spot_price -- Add new column for spot_price value
        ,SUM(CASE WHEN option_type = true THEN oi ELSE 0 END) AS c_oi
        ,SUM(CASE WHEN option_type = true THEN trade_volume ELSE 0 END) AS c_trade_volume
        ,SUM(CASE WHEN option_type = false THEN oi ELSE 0 END) AS p_oi
        ,SUM(CASE WHEN option_type = false THEN trade_volume ELSE 0 END) AS p_trade_volume

        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('%(greek)s', %(greek)s, oi, %(spot_price)s, option_type) ELSE 0 END)) AS c_%(greek)s_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('%(greek)s', %(greek)s, oi, %(spot_price)s, option_type) ELSE 0 END)) AS p_%(greek)s_notion_expo
        ,ROUND(SUM(CASE WHEN option_type = true THEN calc_greek_notion_expo('%(greek)s', %(greek)s, oi, %(spot_price)s, option_type) ELSE 0 END) + 
            SUM(CASE WHEN option_type = false THEN calc_greek_notion_expo('%(greek)s', %(greek)s, oi, %(spot_price)s, option_type) ELSE 0 END)) AS total_%(greek)s_notion_expo
        
    FROM (
        %(subquery)s
    ) AS all_tables
    WHERE 
        quote_datetime::date BETWEEN %(start_date)s AND %(expiration)s
        AND quote_datetime::time = %(trade_time)s
        AND expiration = %(expiration)s
    GROUP BY strike
    ORDER BY strike ASC;
"""

theo_gamma_mv = """
DROP MATERIALIZED VIEW IF EXISTS theo_gamma_es;
CREATE MATERIALIZED VIEW theo_gamma_es AS
SELECT 
    ROW_NUMBER() OVER () AS id
    , exp_date
    , strike
    , SUM(theo_gamma_exposure(exp_date, optiontype, strike, ticker_last_price, iv, openinterest)) AS theo_gamma
    
FROM mainapp_es_opt_raw_data
GROUP BY exp_date, strike
ORDER BY exp_date, strike ASC
;
"""
