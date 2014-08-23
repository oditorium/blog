"""
Option Pricing Library


defines objects for pricing and risk managing financial derivatives
whilst framework is generic, a Black-Scholes type environment is assumed
(eg, no term structure of rates, volatilities etc)

the base object mostly defines how to compute risk parameters, and
the actual calculations are then executed in derived classes; those
calculations are currently done using analytical formulas, but in
principle other valuation methods (Monte Carlo, PDE) could also be
implemented

VERSION

v0.1 alpha


AUTHOR AND COPYRIGHT

Copyright (c) 2014
Stefan LOESCH, oditorium
http://www.oditorium.com


IMPORTANT LEGAL INFORMATION

This software is distributed WITHOUT ANY WARRANTY and without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE,
and it does NOT CONSTITUTE INVESTMENT ADVICE. It shall not be used for
other than academic purposes, and in particular IT SHOULD NOT BE RELIED
UPON TO PRICE OR RISK MANAGE ACTUAL PORTFOLIOS.

This software is licensed under the Gnu AGPL v3.0. See the LICENSE file
or see http://www.gnu.org/licenses/

"""

#-----------------------------------------------------------------------------
#  Copyright (c) 2014  Stefan LOESCH, oditorium
#
#  Distributed under the terms of the AGPL License.
#
#  The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------

from math import exp,log,sqrt
from scipy.stats import norm

class OptionPricing:
    """
    
    base class for pricing options (the pricing itself is implemented in
    derived classes - this object mostly deals with computing the Greeks)
    
    PARAMETERS
        mat - maturity of the option (in years)
        rate - numeraire interest rate (continous compounding)
        yld - dividend yield or foreign discount factor (continous compounding)
        time - current time (in years; default = 0.0)
    
    """
    
    _version = "0.1a"
    
    _dSpc = 0.01 # perturbation for computing Delta, Gamma (percent)
    
    def __init__(self, mat=None, rate=None, yld=None, sig=None, spot=None, time=None):
        
        if time == None: time = 0.0
        if rate == None: rate = 0.0
        if yld == None: yld = 0.0
        if sig == None: sig = 0.00001
        
        self.mat = float(mat)
        self.time = float(time)
        self.rate = float(rate)
        self.yld = float(yld)
        self.sig = float(sig)
        self.spot = float(spot)
        return
    
    def FV(self, fwd, sig, time=0.0):
        """
        
        the forward value of the option, ie the price that would have to be
        paid at its final maturity
        
        NOTE: the implementation of this method is trivial here (it always
        return 1.0, ie a bond); that's the key method to be implemented
        by the derived classes
        
        """
        return 1.0
  
    
    def df(self, mat=None, rate=None, time=None):
        """
        
        the discount factor in continous compounding
        
            df = exp(-r (T-t) )
        
        """
        if rate == None: rate = self.rate
        if time == None: time = self.time
        if mat == None: mat = self.mat
        return exp(-rate * (mat - time))
   
    
    def fdf(self, mat=None, yld=None, time=None):
        """
        
        the foreign discount factor in continous compounding (in case of fx),
        or the equivalent for equities with a percentage divident yield
        
            df = exp(-yld (T-t) )
        
        """
        if yld == None: yld = self.yld
        if time == None: time = self.time
        if mat == None: mat = self.mat
        return exp(-yld * (mat - time))
    
    
    def ff(self, mat=None, rate=None, yld=None, time=None):
        """
        
        the forward factor in continous compounding, ie forward / spot
        
            ff = exp( -(rate-yld) * (T-t) ) = df / fdf
        
        """
        return self.fdf(mat=mat, yld=yld, time=time) / self.df(mat=mat, rate=rate, time=time)
    
    
    def Forward(self, mat=None, spot=None, rate=None, yld=None, time=None):        
        """
        
        the forward
        
            forward = ff * spot
        
        """
        if spot == None: spot = self.spot
        return spot * self.ff(rate=rate, yld=yld, time=time, mat=mat)
        
    def PV(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the present value of the option, ie the price that has to be paid today
        
            PV = df FV
            
        """
        if spot == None: spot = self.spot 
        if sig == None: sig = self.sig 
        df = self.df(rate=rate, time=time)
        ff = self.ff(rate=rate, yld=yld, time=time)
        return df * self.FV(fwd = ff*spot, sig=sig, time=time)
    
    
    def Delta(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Delta" greek, ie the sensitivity of the present value 
        with respect to the spot price
            
            Delta = dPV / dS
        
        """
        if spot == None: spot = self.spot 
        dS = self._dSpc * spot
        pvp = self.PV(spot=spot+dS, time=time, rate=rate, yld=yld, sig=sig)
        pvm = self.PV(spot=spot-dS, time=time, rate=rate, yld=yld, sig=sig)
        return (pvp - pvm) / (2.0 * dS)

    
    def DeltaCash(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Cash-Delta" greek, ie the delta expressed in currency units
            
            DeltaCash = Delta x Spot
        
        """
        if spot == None: spot = self.spot 
        return spot * self.Delta(spot=spot, time=time, rate=rate, yld=yld, sig=sig)

    
    def DeltaFwd(self, fwd=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Forward Delta" greek, ie the sensitivity of the forward value
        with respect to the forward price
            
            Delta = dFV / dF
        
        """
        if fwd == None: fwd = self.Forward(rate=rate, yld=yld, time=time) 
        dF = self._dSpc * fwd
        fvp = self.FV(fwd=fwd+dF)
        fvm = self.PV(fwd=fwd-dF)
        return None
  
    
    def DeltaFwdCash(self):
        """
        
        the "Cash-Forward-Delta" greek, ie the Forward Delta expressed in currency units
            
            DeltaFwdCash = DeltaForward x Forward
        
        """
        return None

    
    def Gamma(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Gamma" greek, ie the sensitivity of the delta value
        with respect to the spot price
            
            Gamma = d^2PV / dS^2
        
        """
        if spot == None: spot = self.spot 
        dS = self._dSpc * spot
        pvp = self.PV(spot=spot+dS, time=time, rate=rate, yld=yld, sig=sig)
        pvm = self.PV(spot=spot-dS, time=time, rate=rate, yld=yld, sig=sig)
        pv = self.PV(spot=spot, time=time, rate=rate, yld=yld, sig=sig)
        return (pvp + pvm - 2.0*pv) / (dS*dS)

    def GammaCash(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "CashGamma" greek which is defined as follows
            
            GammaCash = Gamma * S^2
            
        Note: GammaCash is *not* equal to d/dS DeltaCash; it is however the 
        term that appears in the time decay in the Black Scholes PDE
        
            ... + 0.5 * sig^2 * GammaCash + ... 
        
        """
        if spot == None: spot = self.spot 
        return spot*spot * self.Gamma(spot=spot, time=time, rate=rate, yld=yld, sig=sig)
    
    def Vega(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Vega" greek, ie the sensitivity with respect to vol 
        (for 1 point change in vol)
        
            Vega = PV(sig + 0.01) - PV (sig)
        
        """
        if sig == None: sig = self.sig
        pvp = self.PV(sig=sig+0.01, spot=spot, time=time, rate=rate, yld=yld)
        pv = self.PV(sig=sig, spot=spot, time=time, rate=rate, yld=yld)
        return pvp - pv

    
    def Theta(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Theta" greek, ie the time decay 
        (for 1 calendar day change)
        
            Theta = PV(time + 1.0/365) - PV (time)
        
        """
        if time == None: time = self.time
        pvp = self.PV(time=time+0.0027397260273972603, spot=spot, rate=rate, yld=yld, sig=sig)
        pv = self.PV(time=time, spot=spot, rate=rate, yld=yld, sig=sig)
        return pvp - pv

    
    def Rho(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Rho" greek, ie the sensitivity to numeraire interest rates
        (for a 1 point change)
        
            Rho = d PV / d rate * 0.01
        
        """
        if rate == None: rate = self.rate
        pvp = self.PV(time=time, spot=spot, rate=rate+0.01, yld=yld, sig=sig)
        pv = self.PV(time=time, spot=spot, rate=rate, yld=yld, sig=sig)
        return pvp - pv
 
    def RhoYld(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "RhoYld" greek, ie the sensitivity to asset yield / foreign interest rates
        (for a 1 point change)
       
            RhoYld = d PV / d yld * 0.01

        
        """
        if yld == None: yld = self.yld
        pvp = self.PV(time=time, spot=spot, rate=rate, yld=yld+0.01, sig=sig)
        pv = self.PV(time=time, spot=spot, rate=rate, yld=yld, sig=sig)
        return pvp - pv
    
    def Volga(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Volga" greek, ie the sensitivity of Vega to volatility changes
        (volatility gamma)
        
            Volga = d^2 PV / d sig^2 * 0.01^2
        
        """
        
        if sig == None: sig = self.sig 
        pvp = self.PV(spot=spot, time=time, rate=rate, yld=yld, sig=sig+0.01)
        pvm = self.PV(spot=spot, time=time, rate=rate, yld=yld, sig=sig-0.01)
        pv = self.PV(spot=spot, time=time, rate=rate, yld=yld, sig=sig)
        return (pvp + pvm - 2.0*pv)
        
    def Vanna(self, spot=None, time=None, rate=None, yld=None, sig=None):
        """
        
        the "Vanna" greek, ie the sensitivity of Vega to spot changes
        (and the sensitivity of Delta to vol changes)
        
            Vanna = d^2 PV / d sig dS
        
        """
        if sig == None: sig = self.sig 
        delp = self.Delta(spot=spot, time=time, rate=rate, yld=yld, sig=sig+0.01)
        delm = self.Delta(spot=spot, time=time, rate=rate, yld=yld, sig=sig-0.01)
        return (delp - delm)/0.01
        
class Forward(OptionPricing):
    """
    
    class for pricing a forward
    
    PARAMETERS (like OptionPricing, plus)
        strike - the strike price
    """
    
    def __init__(self, mat=None, strike=None, rate=None, yld=None, sig=None, spot=None, time=None):
        
        self.strike =strike
        super().__init__(mat=mat, rate=rate, yld=yld, sig=sig, spot=spot, time=time)
        return
    
    def FV(self, fwd=None, sig=None, time=None):
        if fwd == None: fwd = self.Forward()
        return fwd - self.strike
class BSBase(OptionPricing):
    """
    
    intermediate class for pricing European options with a strike
    in a Black-Scholes universe (main purpose: compute d1, d2)
    
    PARAMETERS (like OptionPricing, plus)
    strike - the strike price
    
    """
    
    def __init__(self, mat=None, strike=None, rate=None, yld=None, sig=None, spot=None, time=0.0):
        
        self.strike = strike
        super().__init__(mat=mat, rate=rate, yld=yld, sig=sig, spot=spot, time=time)
        return
    
    def d12(self, fwd=None, sig=None, time=None, strike=None, mat=None):
        """
        
        compute Black-Scholes d1 and d2 (computed together for efficiency reasons)
        
            d1 = ( ln (F/S) + 0.5 sig^2 (T-t) ) / sig sqrt(T-t)
            d2 = ( ln (F/S) - 0.5 sig^2 (T-t) ) / sig sqrt(T-t)
        
        """
        if mat == None: mat = self.mat
        if time == None: time = self.time
        if fwd == None: fwd = self.Forward(mat=mat, time=time)
        if strike == None: strike = self.strike
        if sig == None: sig = self.sig
        
        lnfs = log(1.0*fwd/strike)
        sig2t = sig*sig*(mat - time)
        sigsqrt = sig*sqrt(mat - time)
        d1 = (lnfs + 0.5 * sig2t) / sigsqrt
        d2 = (lnfs - 0.5 * sig2t) / sigsqrt
        
        return d1,d2

class BSCall(BSBase):
    """
    
    compute the price of a European call option in a Black Scholes universe
    
        FV = F N(d1) - K N(d2)
        
    """
    
    def __init__(self, mat=None, strike=None, rate=None, yld=None, sig=None, spot=None, time=None):
        
        super().__init__(mat=mat, strike=strike, rate=rate, yld=yld, sig=sig, spot=spot, time=time)
        return

    def FV(self, fwd=None, sig=None, time=None):
        
        if fwd == None: fwd = self.Forward()
        d1, d2 = self.d12(fwd=fwd, sig=sig, strike=self.strike, mat=self.mat, time=time)
        return fwd * norm.cdf (d1) - self.strike * norm.cdf (d2)
    

class BSPut(BSBase):
    """
    
    compute the price of a European put option in a Black Scholes universe
    
        FV = K N(-d2) - F N(-d1)
        
    """
    
    def __init__(self, mat=None, strike=None, rate=None, yld=None, sig=None, spot=None, time=None):
        
        super().__init__(mat=mat, strike=strike, rate=rate, yld=yld, sig=sig, spot=spot, time=time)
        return

    def FV(self, fwd=None, sig=None, time=None):
        
        if fwd == None: fwd = self.Forward()
        d1, d2 = self.d12(fwd=fwd, sig=sig, strike=self.strike, mat=self.mat, time=time)
        return self.strike * norm.cdf (-d2) - fwd * norm.cdf (-d1)
    

class BSDCall(BSBase):
    """
    
    compute the price of a European digital call option in a Black Scholes universe
    (the digital European call pays one unit of the numeraire iff spot > strike at maturity)
    
        FV = N(d2)
        
    """
    
    def __init__(self, mat=None, strike=None, rate=None, yld=None, sig=None, spot=None, time=None):
        
        super().__init__(mat=mat, strike=strike, rate=rate, yld=yld, sig=sig, spot=spot, time=time)
        return

    def FV(self, fwd=None, sig=None, time=None):
        
        if fwd == None: fwd = self.Forward()
        d1, d2 = self.d12(fwd=fwd, sig=sig, strike=self.strike, mat=self.mat, time=time)
        return norm.cdf(d2)


class BSDPut(BSBase):
    """
    
    compute the price of a European digital put option in a Black Scholes universe
    (the digital European put pays one unit of the numeraire iff spot < strike at maturity)
    
        FV = 1 - N(d2)
        
    """
    
    def __init__(self, mat=None, strike=None, rate=None, yld=None, sig=None, spot=None, time=None):
        
        super().__init__(mat=mat, strike=strike, rate=rate, yld=yld, sig=sig, spot=spot, time=time)
        return

    def FV(self, fwd=None, sig=None, time=None):
        
        if fwd == None: fwd = self.Forward()
        d1, d2 = self.d12(fwd=fwd, sig=sig, strike=self.strike, mat=self.mat, time=time)
        return 1.0 - norm.cdf(d2)


class BSRDCall(BSBase):
    """
    
    compute the price of a European reverse digital call option in a Black Scholes universe
    (the digital European call pays one unit of the asset iff spot > strike at maturity)
    
        FV = F N(d1)
        
    """
    
    def __init__(self, mat=None, strike=None, rate=None, yld=None, sig=None, spot=None, time=None):
        
        super().__init__(mat=mat, strike=strike, rate=rate, yld=yld, sig=sig, spot=spot, time=time)
        return

    def FV(self, fwd=None, sig=None, time=None):
        
        if fwd == None: fwd = self.Forward()
        d1, d2 = self.d12(fwd=fwd, sig=sig, strike=self.strike, mat=self.mat, time=time)
        return fwd * norm.cdf(d1)


class BSDPut(BSBase):
    """
    
    compute the price of a European reverse digital put option in a Black Scholes universe
    (the digital European put pays one unit of the asset iff spot < strike at maturity)
  
        FV = F (1 - N(d1))
        
    """
    
    def __init__(self, mat=None, strike=None, rate=None, yld=None, sig=None, spot=None, time=None):
        
        super().__init__(mat=mat, strike=strike, rate=rate, yld=yld, sig=sig, spot=spot, time=time)
        return

    def FV(self, fwd=None, sig=None, time=None):
        
        if fwd == None: fwd = self.Forward()
        d1, d2 = self.d12(fwd=fwd, sig=sig, strike=self.strike, mat=self.mat, time=time)
        return fwd * (1.0 - norm.cdf(d1))


