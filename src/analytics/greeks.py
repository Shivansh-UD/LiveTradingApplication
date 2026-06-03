# THIS FILE IS THE BRAIN OF THE APP. HERE WE DEFINE THE GREEKS
# WHAT ARE "GREEKS"?
#
# Greeks = the health report card of an option!
# Just like a report card has different subjects,
# options have different "risks" and each Greek
# measures a different one.
#
# DELTA  = if the stock moves $1 up, how much
#          does the option change?
#          Example: delta 0.30 means stock goes
#          $1 up, option goes up $0.30!
#
# THETA  = how much value does the option
#          automatically lose every single day?
#          Example: theta -0.05 means tomorrow
#          the option is automatically $0.05
#          cheaper! (sellers LOVE this!)
#
# GAMMA  = how fast is delta changing?
#          High gamma = unpredictable moves!
#          Example: gamma is high near expiry
#          so be extra careful then!
#
# VEGA   = if IV changes by 1%, how much does
#          the option price change?
#          Example: vega 0.04 means IV goes up
#          1% and option gets $0.04 more expensive!

#firstly we will import all the ncessary packages
import numpy as np
from scipy.stats import norm      # Normal distribution
from datetime import datetime
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#This function calculates the fair price of the stock
def black_scholes(S, K, T, r, sigma, option_type="put"):
    """
    This is a method that is used to calculate the theoretical fair price of the options.
    In robinhood when we see all those strike prices, this formula is what calculates them. 
    This method is still used in todays world.


    Imagine a used car dealer named xyz. A car sells in the market for $16,000, 
    but the dealer calculates its real worth at $14,500. If the dealer can get it for $13,000, 
    they buy it immediately.The Black-Scholes model does the exact same thing for stock options. 
    It calculates the true value of an option. 
    If the market option is overpriced, you sell it. If it is underpriced, you buy it.
    
    Args:
        S: Current stock price (e.g. $16.63 Ford)
        K: Strike price (e.g. $15.00)
        T: Time to expiry IN YEARS (25 days = 25/365)
        r: Risk free rate (US Treasury rate ~0.05 = 5%)
        sigma: Implied Volatility (e.g. 0.35 = 35% IV)
        option_type: "put" or "call"
        
    Returns:
        Theoretical fair price of the option
    """
    try:
        # T = 0 means that the option has expired meanig  the value = 0
        if T <= 0:
            return 0.0
        
        # Black Scholes math formula
        # d1 and d2 = are probability calculations
        # "how much the stock will move given the probablity"
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == "call":
            # Call option price
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            # Put option price
            # norm.cdf(-d1) = probability stock will go down
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            
        return round(price, 4)
        
    except Exception as e:
        logger.error(f"Black Scholes error: {e}")
        return None
    

# this fucntion calculates the greeks
def calculate_greeks(S, K, T, r, sigma):
    """
    This function calculates all the greeks together
    
    Greeks = health of the option report
    
    Args:
        Same as black_scholes()
        
    Returns:
        Dictionary with all Greeks
    """
    try:
        # T = 0 means that the option has expired meanig  the value = 0
        if T <= 0:
            return None
            
        # d1 and d2 same formula 
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # DELTA — "how much the option will move if the stock goes up by $1"
        # In a Put delta = negative (stock goes up = put put goes down)
        # we will do abs value to do comparison
        put_delta = norm.cdf(d1) - 1  # negative value for puts
        call_delta = norm.cdf(d1)      # positive value for calls
        
        # THETA — "how much value will be loss each day"
        # this is our friend when we want to sell
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) 
                 - r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
        # GAMMA — "how fast is the delta value changing"
        # High gamma = risky near expiry
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        
        # VEGA — "If IV 1% changes, what will the price of the option be"
        # Per 1% IV change
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        
        return {
            "put_delta": round(put_delta, 4),
            "call_delta": round(call_delta, 4),
            "theta": round(theta, 4),    # daily decay in dollars
            "gamma": round(gamma, 4),
            "vega": round(vega, 4),
        }
        
    except Exception as e:
        logger.error(f"Greeks calculation error: {e}")
        return None
    
# this is the WHEEL STRATGY SCREENER 
def csp_screener(options_chain, current_price, risk_free_rate=0.05):
    """
    This function goes through all the options and picks 
    the puts that are the best for the WHEEL Strat.
    
    Criteria that we will check:
    1. Delta 0.20 - 0.35 (sweet spot)
    2. Bid > $0.05 (make sure there is some premium at least)
    3. Open Interest > 100 (enough liquidity should be there, . It measures how many active positions exist for a specific option (calls or puts) at a particular strike price and expiration date )
    4. IV > 20% (agar IV bahut kamtoo less — we will not get good premium)
    
    Args:
        options_chain: fetcher.py (we get the options data)
        current_price: Stocks current price
        risk_free_rate: US Treasury rate (default 5%)
        
    Returns:
        Filtered DataFrame — only best wheel candidates!
    """
    try:
        puts = options_chain["puts"].copy()
        expiry = options_chain["expiry"]
        
        # Days to expiry calculate
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
        today = datetime.now()
        days_to_expiry = (expiry_date - today).days
        
        # Time to expiry IN YEARS, Black Scholes 
        T = days_to_expiry / 365
        
        logger.info(f"Screening {len(puts)} puts for Wheel Strategy!!!")
        logger.info(f"Days to expiry: {days_to_expiry}")
        
        # we will calculate the greeks for every put anmd append it in the list as following
        results = []
        
        for _, row in puts.iterrows():
            strike = row['strike']
            iv = row['impliedVolatility']
            bid = row['bid']
            ask = row['ask']
            open_interest = row['openInterest']
            
            # IV check, if its 0 then we skip that option
            if iv <= 0 or pd.isna(iv):
                continue
                
            # Greeks calculation
            greeks = calculate_greeks(
                S=current_price,
                K=strike,
                T=T,
                r=risk_free_rate,
                sigma=iv
            )
            
            if greeks is None:
                continue
            
            # Absolute delta (puts negative are negative in delta value)
            abs_delta = abs(greeks['put_delta'])
            
            # Fair value calculations
            fair_value = black_scholes(
                S=current_price,
                K=strike,
                T=T,
                r=risk_free_rate,
                sigma=iv,
                option_type="put"
            )
            
            # Midpoint price (bid + ask / 2)
            mid_price = (bid + ask) / 2
            
            results.append({
                "strike": strike,
                "bid": bid,
                "ask": ask,
                "mid_price": round(mid_price, 2),
                "fair_value": fair_value,
                "iv_pct": round(iv * 100, 1),     # percentage
                "delta": round(abs_delta, 3),
                "theta": greeks['theta'],           # daily decay
                "gamma": greeks['gamma'],
                "vega": greeks['vega'],
                "open_interest": open_interest,
                "days_to_expiry": days_to_expiry,
                # Potential return if put expires worthless
                "return_if_expired": round((mid_price / strike) * 100, 2)
            })
        
        # DataFrame generate
        df = pd.DataFrame(results)
        
        if df.empty:
            logger.warning("No valid puts found!")
            return None
        
        # WHEEL STRATEGY FILTER ONLY THE BEST PUTS
        csp_candidates = df[
            (df['delta'] >= 0.15) &       
            (df['delta'] <= 0.45) &       
            (df['bid'] >= 0.01) &         
            (df['open_interest'] >= 10) & 
            (df['iv_pct'] >= 10)          
        ].copy()
        
        # Sort based on the best returns
        csp_candidates = csp_candidates.sort_values(
            'return_if_expired', ascending=False
        )
        
        logger.info(f"Found {len(csp_candidates)} CSP candidates!")
        return csp_candidates
        
    except Exception as e:
        logger.error(f"CSP screener error: {e}")
        return None
    

# this function is used for the covered calls part of the wheel strat
def covered_call_screener(options_chain, current_price, 
                          cost_basis, risk_free_rate=0.05):
    """
    This filters the best strike prices for covered calls
    
    Key difference from CSP screener:
    - CSP we want that the stock stays high
    - CC we want that the stock does not go super high
    - Strike price should be higher than the current price
    - Delta 0.20-0.35 same sweet spot
    
    Args:
        options_chain: fetcher.py fecthed the options data
        current_price: Stocks current price
        cost_basis: Our actual cost — If we buy 100 shares of Ford at
                    $16, with premium $0.50 per share
                   then our cost basis = $15.50
        risk_free_rate: US Treasury rate (default 5%)
        
    Returns:
        Filtered DataFrame — only best CC candidates
    """
    try:
        calls = options_chain["calls"].copy()
        expiry = options_chain["expiry"]
        
        # Days to expiry calculation
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
        today = datetime.now()
        days_to_expiry = (expiry_date - today).days
        
        # Time in years for Black Scholes
        T = days_to_expiry / 365
        
        logger.info(f"Screening {len(calls)} calls for Covered Call...")
        logger.info(f"Cost basis: ${cost_basis}")
        
        results = []
        
        for _, row in calls.iterrows():
            strike = row['strike']
            iv = row['impliedVolatility']
            bid = row['bid']
            ask = row['ask']
            open_interest = row['openInterest']
            
            # for a CC strike price should be higher than the current price other wise we will get assigned
            if strike <= current_price:
                continue
                
            # IV check
            if iv <= 0 or pd.isna(iv):
                continue
            
            # Greeks calculation
            greeks = calculate_greeks(
                S=current_price,
                K=strike,
                T=T,
                r=risk_free_rate,
                sigma=iv
            )
            
            if greeks is None:
                continue
            
            # Call delta will be used here (positive)
            call_delta = greeks['call_delta']
            
            # Fair value
            fair_value = black_scholes(
                S=current_price,
                K=strike,
                T=T,
                r=risk_free_rate,
                sigma=iv,
                option_type="call"
            )
            
            # Mid price
            mid_price = (bid + ask) / 2
            
            # Profit if called away, If we get assigned the call then after 
            #combining the strike price at which the shares got sold and the premium we collected
            # compare it with our cost basis
            profit_if_called = round(
                ((strike - cost_basis) + mid_price), 2
            )
            
            # Return on investment if the call got assigned
            roi_if_called = round(
                (profit_if_called / cost_basis) * 100, 2
            )
            
            results.append({
                "strike": strike,
                "bid": bid,
                "ask": ask,
                "mid_price": round(mid_price, 2),
                "fair_value": fair_value,
                "iv_pct": round(iv * 100, 1),
                "delta": round(call_delta, 3),
                "theta": greeks['theta'],
                "gamma": greeks['gamma'],
                "vega": greeks['vega'],
                "open_interest": open_interest,
                "days_to_expiry": days_to_expiry,
                # return on Premium collection
                "return_if_expired": round(
                    (mid_price / current_price) * 100, 2
                ),
                # if we get assigned
                "profit_if_called": profit_if_called,
                "roi_if_called": roi_if_called
            })
        
        df = pd.DataFrame(results)
        
        if df.empty:
            logger.warning("No valid calls found!")
            return None
        
        # COVERED CALL FILTER
        cc_candidates = df[
            (df['delta'] >= 0.15) &
            (df['delta'] <= 0.45) &
            (df['bid'] >= 0.01) &
            (df['open_interest'] >= 10) &
            (df['iv_pct'] >= 10) &
            (df['profit_if_called'] > 0)
        ].copy()
        
        # Best returns returned
        cc_candidates = cc_candidates.sort_values(
            'roi_if_called', ascending=False
        )
        
        logger.info(f"Found {len(cc_candidates)} CC candidates!")
        return cc_candidates
        
    except Exception as e:
        logger.error(f"Covered call screener error: {e}")
        return None
    

    
#THIS USED FOR TESTING ONLY
if __name__ == "__main__":
    
    # fetcher.py used to get the data
    import sys
    sys.path.append('.')
    from src.data.fetcher import get_stock_data, get_options_chain, get_iv_data
    
    TEST_TICKER = "F"
    
    print("\n" + "="*50)
    print(f"LAYER 2 - ANALYTICS ENGINE - {TEST_TICKER}")
    print("="*50)
    
    # fecth the data
    iv_data = get_iv_data(TEST_TICKER)
    options = get_options_chain(TEST_TICKER)
    
    current_price = iv_data['current_price']
    print(f"\nCurrent Price: ${current_price}")

    # TEMPORARY DEBUG — raw puts data dekhte hain
    print("\n🔍 RAW PUTS DATA:")
    raw_options = get_options_chain(TEST_TICKER)
    if raw_options:
        puts_df = raw_options['puts']
        print(puts_df[['strike', 'bid', 'ask', 
                    'impliedVolatility', 
                    'openInterest']].to_string())
    
    # Black Scholes test
    print("\n📐 BLACK SCHOLES TEST:")
    bs_price = black_scholes(
        S=current_price,
        K=current_price * 0.95,  # 5% OTM put
        T=25/365,
        r=0.05,
        sigma=0.35
    )
    print(f"Fair value of 5% OTM put: ${bs_price}")
    
    # Greeks test
    print("\n🏛️ GREEKS TEST:")
    greeks = calculate_greeks(
        S=current_price,
        K=current_price * 0.95,
        T=25/365,
        r=0.05,
        sigma=0.35
    )
    for key, value in greeks.items():
        print(f"  {key}: {value}")
    
    # Wheel Screener test
    print("\n CASH SECURED PUT SCREENER:")
    if options:
        candidates = csp_screener(options, current_price)
        if candidates is not None and not candidates.empty:
            print(f"\nTop CSP Candidates:")
            print(candidates[['strike', 'bid', 'delta', 
                             'theta', 'iv_pct', 
                             'return_if_expired']].to_string())
        else:
            print("No candidates found matching criteria")
    
    # Covered Call Screener test
    print("\n COVERED CALL SCREENER:")
    if options:
        # If ford got assigned at $16.63
        # and we got $0.30 premium when we did the CSP 
        # then the cost basis = 16.63 - 0.30 = 16.33
        cost_basis = current_price - 0.30
        
        cc_candidates = covered_call_screener(
            options, current_price, cost_basis
        )
        if cc_candidates is not None and not cc_candidates.empty:
            print(f"\nTop Covered Call Candidates:")
            print(cc_candidates[['strike', 'bid', 'delta',
                                 'theta', 'iv_pct',
                                 'return_if_expired',
                                 'profit_if_called',
                                 'roi_if_called']].to_string())
        else:
            print("No CC candidates found matching criteria")
