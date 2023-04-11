calc_greek_notion_expo = """
            CREATE OR REPLACE FUNCTION calc_greek_notion_expo(greek TEXT, greek_val NUMERIC, openinterest NUMERIC, spot_price NUMERIC, optiontype BOOL)
            RETURNS NUMERIC AS $$
            DECLARE
                gamma_value DOUBLE PRECISION;
                open_interest_value INTEGER;
                option_type_value INTEGER;
            BEGIN
                IF optiontype = true THEN
                    option_type_value :=1;
                ELSIF optiontype = false THEN
                    option_type_value :=-1;
                ELSE
                    RAISE EXCEPTION 'Invalid option type value: %', option_type;
                END IF;
                
                IF greek = 'gamma' THEN
                    RETURN (greek_val * openinterest * 100 * spot_price * spot_price * 0.01 * option_type_value);
                ELSE
                    RETURN (greek_val * openinterest * 100 * spot_price);

                END IF;
                

            END;
            $$ LANGUAGE plpgsql;
"""

calc_vanna = """
DROP FUNCTION vanna(timestamp without time zone,date,numeric,numeric,numeric);
CREATE OR REPLACE FUNCTION vanna (quote_datetime TIMESTAMP, expiration DATE, strike NUMERIC, spot_price NUMERIC, implied_volatility NUMERIC) RETURNS NUMERIC
AS
$$
DECLARE
	r_rate NUMERIC := 0;
	q_rate NUMERIC := 0;
	
	dte INTEGER;
	time_exp NUMERIC;
	sigma_t NUMERIC;
	d1 FLOAT4;
	d2 FLOAT4;
	vanna FLOAT4;
BEGIN
	dte := expiration - quote_datetime::DATE;
	
	IF dte < 2 THEN 
		time_exp := 1.0/365;
	ELSE
		time_exp := dte::FLOAT/365;
	END IF;
	
	sigma_t := implied_volatility * SQRT(time_exp);
	d1 := (LN(spot_price / NULLIF(strike, 0)) + (r_rate - q_rate + 0.5 * POWER(implied_volatility, 2)) * time_exp) / NULLIF(sigma_t, 0);
	d2 := d1 - sigma_t;
	
	IF ABS(d1) < 8 THEN
		IF ABS(d1) < 0.001 THEN
			vanna := 0.01 * EXP(-q_rate * time_exp) * d2 / implied_volatility * 0.3989420;
		ELSE
			vanna := 0.01 * EXP(-q_rate * time_exp) * d2 / implied_volatility * norm_pdf(d1);
		END IF;
	ELSE
		-- norm_pdf(value) for value > 8 becomes 0, hence vanna becomes 0.
		vanna := 0;
	END IF;
	
	RETURN vanna;
END;
$$ LANGUAGE plpgsql
;
"""

calc_gamma = """

CREATE OR REPLACE FUNCTION gamma (quote_datetime TIMESTAMP, expiration DATE, strike NUMERIC, spot_price NUMERIC, implied_volatility NUMERIC) RETURNS NUMERIC
AS $$
DECLARE
	r_rate NUMERIC := 0;
	q_rate NUMERIC := 0;
	
	dte INTEGER;
	time_exp NUMERIC;
	sigma_t NUMERIC;
	d1 FLOAT4;
	d2 FLOAT4;
	gamma FLOAT4;
BEGIN
	dte := expiration - quote_datetime::DATE;
	
	IF dte < 2 THEN 
		time_exp := 1.0/365;
	ELSE
		time_exp := dte::FLOAT/365;
	END IF;
	
	sigma_t := implied_volatility * SQRT(time_exp);
	d1 := (LN(spot_price / NULLIF(strike, 0)) + (r_rate - q_rate + 0.5 * POWER(implied_volatility, 2)) * time_exp) / NULLIF(sigma_t, 0);
	d2 := d1 - sigma_t;
	
	IF ABS(d1) < 8 THEN
		IF ABS(d1) < 0.001 THEN
			gamma := EXP(-q_rate * time_exp) * 0.3989420 / (spot_price*sigma_t);
		ELSE
			gamma := EXP(-q_rate * time_exp) * norm_pdf(d1) / (spot_price*sigma_t);
		END IF;
	ELSE
		-- norm_pdf(value) for value > 8 becomes 0, hence vanna becomes 0.
		gamma := 0;
	END IF;
	
	RETURN gamma;
END;
$$ LANGUAGE plpgsql
;
"""


calc_theo_gamma_exposure = """
CREATE OR REPLACE FUNCTION norm_pdf(z FLOAT4, mu FLOAT4 DEFAULT 0, sigma FLOAT4 DEFAULT 1)
RETURNS FLOAT4 AS $$
DECLARE
  coef FLOAT4;
  expon FLOAT4;
  pdf_result FLOAT4;
BEGIN
  coef := 1 / (sigma * SQRT(2.0 * PI()));
  expon := -1.0 * POWER((z - mu), 2.0) / (2.0 * POWER(sigma, 2.0));
  pdf_result := coef * EXP(expon);
  RETURN pdf_result;
END;
$$ LANGUAGE plpgsql
;

CREATE OR REPLACE FUNCTION theo_gamma_exposure (expiration DATE, option_type CHAR, strike DOUBLE PRECISION, underlying_price DOUBLE PRECISION, implied_volatility DOUBLE PRECISION, oi INTEGER) RETURNS NUMERIC
AS
$$
DECLARE
    r_rate NUMERIC := 0;
    q_rate NUMERIC := 0;
    
    dte INTEGER;
    time_exp NUMERIC;
    sigma_t NUMERIC;
    
    spot_perc NUMERIC;
    spot_qty INTEGER;
    spot_price NUMERIC;
    d1 FLOAT4;
    gamma NUMERIC;
    gamma_exposure BIGINT;
    
BEGIN
    dte := expiration - NOW()::DATE;

    IF dte < 2 THEN 
        time_exp := 1.0/365;
    ELSE
        time_exp := dte::FLOAT/365;
    END IF;

    sigma_t := implied_volatility * SQRT(time_exp);
    
    spot_perc := 0.05 + (dte::FLOAT / 365) * 0.30;
    spot_qty := CEILING(100 + (dte::FLOAT / 365) * 100);
    
    gamma_exposure := 0;
    
    FOR i IN 1..spot_qty LOOP
        spot_price := ROUND((underlying_price * ((1-spot_perc) + i*2*spot_perc/spot_qty))::NUMERIC, 1);
        
        CONTINUE WHEN spot_price <= 0;
        
        IF sigma_t != 0 THEN
            d1 := (LN(spot_price / strike) + (r_rate - q_rate + 0.5 * POWER(implied_volatility, 2)) * time_exp) / sigma_t;
            
            IF ABS(d1) < 8 THEN  -- Assumption: Larger values for d1 will result in gamma = 0, so discard.
                IF ABS(d1) < 0.001 THEN  -- Very small values around 0 result in norm_pdf of 0.3989420. Use that value instead of calculating.
                    gamma := EXP(-q_rate * time_exp) * 0.3989420 / (spot_price * sigma_t);
                ELSE
                    gamma := EXP(-q_rate * time_exp) * norm_pdf(d1) / (spot_price * sigma_t);
                END IF;
                gamma_exposure := gamma_exposure + (POWER(spot_price, 2) * gamma * oi);
            END IF;
        END IF;
    END LOOP;
    
    IF option_type = 'p' THEN
        gamma_exposure := -1 * gamma_exposure;
    END IF;
    
    RETURN gamma_exposure;
END;
$$ LANGUAGE plpgsql
;
"""