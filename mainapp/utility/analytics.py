import numpy as np
from math import e
from enum import Enum
import scipy.stats as stat
from scipy.stats import norm
import time
import pandas as pd


# Risk Free Rate: Use 3-month Treasury Yield Curve Rates
# https://quant.stackexchange.com/questions/58109/how-to-find-the-risk-free-rate-and-dividend-rate-for-sp-500-index-options
# https://github.com/tringuy1993/option3d/blob/master/options3d.py

class BSMerton:
    def __init__(self, opt_type, spot_price, strike, r: int, q: int, exp_year, volatility):
        if opt_type == "CALL":
            self.Type = 1  # 1 for a Call, - 1 for a put
        else:
            self.Type = -1
        self.S = spot_price  # Underlying asset price
        self.K = strike  # Option strike K
        self.r = r  # Continuous risk fee rate
        self.q = q  # Dividend continuous rate
        self.T = exp_year  # Compute time to expiry
        self.sigma = volatility # Underlying volatility
        self.sigmaT = self.sigma * self.T ** 0.5  # sigma*T for reusability
        self.d1 = (np.log(self.S / self.K) +
                   (self.r - self.q + 0.5 * (self.sigma ** 2))
                   * self.T) / self.sigmaT
        self.d2 = self.d1 - self.sigmaT
        [self.Premium] = self.premium()
        [self.Delta] = self.delta()
        [self.Theta] = self.theta()
        [self.Rho] = self.rho()
        [self.Vega] = self.vega()
        [self.Gamma] = self.gamma()
        [self.Phi] = self.phi()
        [self.Charm] = self.dDeltadTime()
        [self.Vanna] = self.dDeltadVol()
        [self.Vomma] = self.dVegadVol()

    def premium(self):
        tmpprem = self.Type * (self.S * e ** (-self.q * self.T) * norm.cdf(self.Type * self.d1) - \
                               self.K * e ** (-self.r * self.T) * norm.cdf(self.Type * self.d2))
        return [tmpprem]

    ############################################
    ############ 1st order greeks ##############
    ############################################

    def delta(self):
        dfq = e ** (-self.q * self.T)
        if self.Type == 1:
            return [dfq * norm.cdf(self.d1)]
        else:
            return [dfq * (norm.cdf(self.d1) - 1)]

    # Vega for 1% change in vol
    def vega(self):
        return [0.01 * self.S * e ** (-self.q * self.T) * norm.pdf(self.d1) * self.T ** 0.5]

    # Theta for 1 day change
    def theta(self):
        df = e ** -(self.r * self.T)
        dfq = e ** (-self.q * self.T)
        tmptheta = (1.0 / 365.0) \
                   * (-0.5 * self.S * dfq * norm.pdf(self.d1) * \
                      self.sigma / (self.T ** 0.5) + \
                      self.Type * (self.q * self.S * dfq * norm.cdf(self.Type * self.d1) \
                                   - self.r * self.K * df * norm.cdf(self.Type * self.d2)))
        return [tmptheta]

    def rho(self):
        df = e ** -(self.r * self.T)
        return [self.Type * self.K * self.T * df * 0.01 * norm.cdf(self.Type * self.d2)]

    def phi(self):
        return [0.01 * -self.Type * self.T * self.S * \
                e ** (-self.q * self.T) * norm.cdf(self.Type * self.d1)]

    ############################################
    ############ 2nd order greeks ##############
    ############################################

    def gamma(self):
        return [np.exp(-self.q * self.T) * norm.pdf(self.d1) / (self.S * self.sigmaT)]

    # Charm for 1 day change
    def dDeltadTime(self):
        dfq = np.exp(-self.q * self.T)
        if self.Type == 1:
            return [
                (1.0 / 365.0) * -dfq * (norm.pdf(self.d1) * ((self.r - self.q) / self.sigmaT - self.d2 / (2 * self.T)) \
                                        + (-self.q) * norm.cdf(self.d1))]
        else:
            return [
                (1.0 / 365.0) * -dfq * (norm.pdf(self.d1) * ((self.r - self.q) / self.sigmaT - self.d2 / (2 * self.T)) \
                                        + self.q * norm.cdf(-self.d1))]

    # Vanna for 1% change in vol
    def dDeltadVol(self):
        return [0.01 * np.exp(-self.q * self.T) * self.d2 / self.sigma * norm.pdf(self.d1)]

    # Vomma
    def dVegadVol(self):
        return [0.01 * np.exp(-self.q * self.T) * self.d2 / self.sigma * norm.pdf(self.d1)]


