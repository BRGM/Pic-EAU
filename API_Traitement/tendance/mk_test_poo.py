# coding=utf-8
"""
    Runs the Mann-Kendall test for trend in time series data.
    Tested hypothesis : H0, which is the stationnarity of the series
    From JJS, manuel ESTHER
    L'hypothèse de stationnarité (H0) sera rejetée au niveau de signification alpha si la probabilité
    calculée (p-value) est inférieure à alpha : L'hypotèse H0 est peu probable, on la rejette avec le risque
    de 5 % de rejetter une série à tort.
    Cas des ESO: test bilateral (two-tailed test)
    Parameters
    ----------
    t : 1D numpy.ndarray
        array of the time points of measurements
    x : 1D numpy.ndarray
        array containing the measurements corresponding to entries of 't'
    eps : scalar, float, greater than zero
        least count error of measurements which help determine ties in the data
    alpha : scalar, float, greater than zero
        significance level of the statistical test (Type I error)
    Ha : string, options include 'up', 'down', 'upordown'
        type of test: one-sided ('up' or 'down') or two-sided ('updown')

    Returns
    -------
    MK : string
        result of the statistical test indicating whether or not to accept hte
        alternative hypothesis 'Ha'
    m : scalar, float
        slope of the linear fit to the data
    c : scalar, float
        intercept of the linear fit to the data
    p : scalar, float, greater than zero
        p-value of the obtained Z-score statistic for the Mann-Kendall test

    Raises
    ------
    AssertionError : error
                    least count error of measurements 'eps' is not given
    AssertionError : error
                    significance level of test 'alpha' is not given
    AssertionError : error
                    alternative hypothesis 'Ha' is not given
    Created: Mon Apr 17, 2017  01:18PM
    Last modified: Mon Apr 17, 2017  09:24PM
    Copyright: Bedartha Goswami <goswami@uni-potsdam.de>

    modified AH/BRGM/2018
    """

import numpy as np
from scipy.special import ndtri, ndtr
import sys

class MannKendall():
    def __init__(self,t, x, eps=None, alpha=0.05, Ha='upordown'):
        self.t=t
        self.x=x
        self.eps=eps
        self.alpha=alpha
        self.Ha=Ha

    def test(self,t, x, eps=None, alpha=None, Ha=None):

        # assert a least count for the measurements x
        assert self.eps, "Please provide least count error for measurements 'x'"
        assert self.alpha, "Please provide significance level 'alpha' for the test"
        assert self.Ha, "Please provide the alternative hypothesis 'Ha'"

        # estimate sign of all possible (n(n-1)) / 2 differences
        n = len(self.t)
        sgn = np.zeros((n, n), dtype="int")
        for i in range(n):
            tmp = x - x[i]
            tmp[np.where(np.fabs(tmp) <= self.eps)] = 0.
            sgn[i] = np.sign(tmp)

        # estimate mean of the sign of all possible differences
        S = sgn[np.triu_indices(n, k=1)].sum()

        # estimate variance of the sign of all possible differences
        # 1. Determine no. of tie groups 'p' and no. of ties in each group 'q'
        np.fill_diagonal(sgn, self.eps * 1E6)
        i, j = np.where(sgn == 0.)
        ties = np.unique(x[i])
        p = len(ties)
        q = np.zeros(len(ties), dtype="int")
        for k in range(p):
            idx =  np.where(np.fabs(x - ties[k]) < self.eps)[0]
            q[k] = len(idx)
        # 2. Determine the two terms in the variance calculation
        term1 = n * (n - 1) * (2 * n + 5)
        term2 = (q * (q - 1) * (2 * q + 5)).sum()
        # 3. estimate variance
        varS = float(term1 - term2) / 18.

        # Compute the Z-score based on above estimated mean and variance
        if S > self.eps:
            Zmk = (S - 1) / np.sqrt(varS)
        elif np.fabs(S) <= self.eps:
            Zmk = 0.
        elif S < -self.eps:
            Zmk = (S + 1) / np.sqrt(varS)

        # compute test based on given 'alpha' and alternative hypothesis
        # note: for all the following cases, the null hypothesis Ho is:
        # Ho := there is no monotonic trend
        #
        # Ha := There is an upward monotonic trend
        if self.Ha == "up":
            Z_ = ndtri(1. - self.alpha)
            if Zmk >= Z_:
                MK = "accept Ha := upward trend"
            else:
                MK = "reject Ha := upward trend"
        # Ha := There is a downward monotonic trend
        elif self.Ha == "down":
            Z_ = ndtri(1. - self.alpha)
            if Zmk <= -Z_:
                MK = "accept Ha := downward trend"
            else:
                MK = "reject Ha := downward trend"
        # Ha := There is an upward OR downward monotonic trend
        elif self.Ha == "upordown":
            Z_ = ndtri(1. - self.alpha / 2.)
            if np.fabs(Zmk) >= Z_:
                MK = "accept Ha := upward OR downward trend"
            else:
                MK = "reject Ha := upward OR downward trend"

        # ----------
        # AS A BONUS
        # ----------
        # estimate the slope and intercept of the line
        m = np.corrcoef(self.t, self.x)[0, 1] * (np.std(x) / np.std(t))
        c = np.mean(self.x) - m * np.mean(self.t)

        # ----------
        # AS A BONUS
        # ----------
        # estimate the p-value for the obtained Z-score Zmk
        if S > self.eps:
            if self.Ha == "up":
                p = 1. - ndtr(Zmk)
            elif self.Ha == "down":
                p = ndtr(Zmk)
            elif self.Ha == "upordown":
                p = 0.5 * (1. - ndtr(Zmk))
        elif np.fabs(S) <= self.eps:
            p = 0.5
        elif S < -self.eps:
            if self.Ha == "up":
                p = 1. - ndtr(Zmk)
            elif self.Ha == "down":
                p = ndtr(Zmk)
            elif self.Ha == "upordown":
                p = 0.5 * (ndtr(Zmk))

        return MK, m, c, p

if __name__== '__main__':
    MK=MannKendall()
    MK.test()