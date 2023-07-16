query_data = """ SELECT
    expiration
    , strike
    , CASE WHEN option_type = TRUE THEN 'CALL' ELSE 'PUT' END AS option_type
    , o_open
    , o_high
    , o_low
    , o_close
    , trade_volume
    , bid_size
    , bid
    , ask_size
    , ask
    --, underlying_bid
    --, underlying_ask
    --, implied_underlying_price
    , active_underlying_price
    , implied_volatility
    , delta
    , gamma
    , theta
    , vega
    , rho
    , oi as open_interest
    , '$SPX.X' AS symbol
    , CASE
        WHEN expiration - quote_datetime::DATE <= 1 THEN 1/365::float
        ELSE (expiration-quote_datetime::DATE)/365::float
        END AS days_to_expiration
    , quote_datetime
FROM
    %(table_name)s

WHERE
    quote_datetime = %(quote_datetime)s
    AND
    expiration <= %(expiration_date)s

ORDER BY
    option_type ASC, expiration ASC, strike ASC
;"""