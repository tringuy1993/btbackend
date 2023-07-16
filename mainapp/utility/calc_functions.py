import pandas as pd
from .analytics import BSMerton
import numpy as np 

def theo_gamma_data (data):
    
    grouped_data = create_dataframe(data).groupby('exp_date_str', group_keys=True).apply(lambda x:
                                                                           calc_gamma_ex_tn2(x)).reset_index(drop=True)
    new_grouped_data = grouped_data.groupby('spot_price')['total_gamma'].sum().reset_index()
    print(new_grouped_data)
    return new_grouped_data

def calc_gamma_ex_tn2(data, r=0.0, q=0.0):
        # Need daysTillExpiration in fraction.
        # Need Levels - spot price for each strike price? levels = np.linspace(spot_price*0.7, spot_price*1.3, 60)
        # Is Volatility = Implied Volatility?
        # calc_gamma_ex(S, K, vol, T, r, q, optType, OI):
        """" Black-Scholes European-Options Gamma this method is from Sergei's Source
        S = underlying price, K = Strike Price, T = days to expiration (in years), R = "risk-free" rate, V = volatility
         """

        # Common Columns: ['strike_price', 'last_price', 'und_symbol', 'exp_date_str', 'dte_calc', 'underlying_price']

        df = data.copy()
        call_type = 'CALL'
        put_type = 'PUT'

        strikes = df['strikeprice']
        dte_exp_year = df['dte_calc']

        call_volatility = df['c_volatility']
        put_volatility = df['p_volatility']

        spot_price = df['underlying_price'].min()

        spot_price_levels = np.round_(np.linspace(
            spot_price * 0.7, spot_price * 1.3, 200), decimals=0)
        
        print("Spot_price:", spot_price)
        print("dte_exp_year", dte_exp_year)
        # r = 0
        # q = 0
        total_gamma_df = []
        for level in spot_price_levels:
            call_gamma = BSMerton(call_type, level, strikes,
                                  r, q, dte_exp_year, call_volatility).Gamma
            put_gamma = BSMerton(put_type, level, strikes,
                                 r, q, dte_exp_year, put_volatility).Gamma

            call_gamma_exposure = 100 * level ** 2 * \
                0.01 * call_gamma * df['c_openinterest']
            put_gamma_exposure = 100 * level ** 2 * \
                0.01 * put_gamma * df['p_openinterest']

            total_gamma_df.append(
                call_gamma_exposure.sum() - put_gamma_exposure.sum())
            

        df_summary = pd.DataFrame()
        df_summary['spot_price'] = spot_price_levels
        df_summary['total_gamma'] = total_gamma_df
        df_summary['und_symbol'] = df['und_symbol'].iloc[0]
        df_summary['underlying_price'] = df['underlying_price'].iloc[0]
        df_summary['exp_date_str'] = df['exp_date_str'].iloc[0]
        return df_summary

def create_dataframe(option_chain: dict) -> pd.DataFrame:
    df = pd.DataFrame(option_chain)

    df['openInterest'] = df['openInterest'].astype('uint32')
    df['totalVolume'] = df['totalVolume'].astype('uint32')
    df['volatility'] = df['volatility'].astype('float32')
    df['putCall'] = df['putCall'].astype('category')
    df['strikePrice'] = df['strikePrice'].astype('float32')

    greek_cols = ['delta', 'gamma', 'theta', 'vega']
    df[greek_cols] = df[greek_cols].astype('float32')

    price_cols = ['openPrice', 'highPrice', 'lowPrice', 'closePrice', 'underlying_price']
    df[price_cols] = df[price_cols].astype('float64')
    df.columns = df.columns.str.lower()

    put_old_col = ['p_strikeprice', 'p_und_symbol',
                    'p_exp_date_str', 'p_dte_calc', 'p_underlying_price']
    call_old_col = ['c_strikeprice', 'c_und_symbol',
                    'c_exp_date_str', 'c_dte_calc', 'c_underlying_price']

    new_col = ['strikeprice','und_symbol', 'exp_date_str', 'dte_calc', 'underlying_price']

    """ Adding prefix to put and call side."""

    put = df[df['putcall'] == 'PUT'].reset_index(drop=True)

    put = put.add_prefix('p_')

    call = df[df['putcall'] == 'CALL'].reset_index(drop=True)

    call = call.add_prefix('c_')

    # print("Put", put)
    # print("Call", call)

    put.rename(columns=dict(zip(put_old_col, new_col)), inplace=True)
    call.rename(columns=dict(zip(call_old_col, new_col)), inplace=True)

    print("PUT:", put.columns)

    df = pd.merge(put, call, on=new_col)

    return df


if __name__ == "__main__":
    from datetime import datetime
    # from dashboard.data_access.opt_chain_multi import get_option_chain

    test_trading_minute = datetime(year=2021,
                                   month=5,
                                   day=28,
                                   hour=10,
                                   minute=0,
                                   second=0)

    # test_opt_chain = get_option_chain(trading_minute=test_trading_minute)

    # df = create_dataframe(option_chain=test_opt_chain)
    # print(df)
