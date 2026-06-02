# Firstly we will import the packages we will need 
import yfinance as yf        # Yahoo Finance will be used to get the stock/options data
import pandas as pd          # we will use a dataframe to comvert the data in a tabular form
import numpy as np           # Math operations 
from datetime import datetime # Dates handling
import logging
import time

"""
This file is basically our "data getter" from the offcial stock index Yahoo Finance

we will have 3 main functions in this file listed below,

get_stock_data()      ← Price history
get_options_chain()   ← Calls & Puts  
get_iv_data()         ← Implied Volatility
"""

# Logger setup 
# This is basically the big brother of print because it prints with timestamps and severity levels
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# this is the function that gets the stock data
def get_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame: #returns a pandas data frame
    """
    This fetches the stock price history 
    
    Args:
        ticker: Stock symbol like "AAPL", "MSFT", "TSLA"
        period: what is the range of data we are trying to get, "1y" = 1 year
        
    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
    """
    try:
        logger.info(f"Getting stock data for {ticker}!!!")
        
        # yfinance used and make a object of the stock 
        stock = yf.Ticker(ticker)

        time.sleep(2)
        
        #  this is where we get the Price history
        # period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y SIMIALR TO ROBINHOOD OR ANYTHING ELSE
        hist = stock.history(period=period)
        
        # This checks if data even got retrived
        if hist.empty:
            logger.error(f"No data found for {ticker}")
            return None
            
        logger.info(f"Got {len(hist)} days of data for {ticker}")
        return hist
        
    except Exception as e:
        # Log the error and return None
        logger.error(f"Error fetching stock data: {e}")
        return None
    
# This function gets the options chain similar to how we go in the robinhood app and look at different options contracts we can get.
def get_options_chain(ticker: str, expiry_days_min: int = 20, expiry_days_max: int = 50) -> dict: # returns a dictionary
    """
    for the wheel stratgy 20-50 days of data is good
    
    Args:
        ticker: Stock symbol
        expiry_days_min: Minimum days to expiry (default 20)
        expiry_days_max: Maximum days to expiry (default 50)
        
    Returns:
        Dictionary with 'puts' and 'calls' DataFrames
    """
    try:
        logger.info(f"Getting options chain for {ticker}!!!")
        
        stock = yf.Ticker(ticker)

        time.sleep(2)
        
        # Take all the expiration dates from the data
        expirations = stock.options
        
        # returns None(logs error) if no expirations were find 
        if not expirations:
            logger.error(f"No options found for {ticker}")
            return None
        
        # takeing todays date
        today = datetime.now()
        
        # only working with those dates that are 20-50 days old
        # Why? because it is best for the wheel stratgy
        # theta decay is the fastest between 30-45 days
        valid_expiries = [] # pushed the correct expiries to this list
        for exp in expirations:
            exp_date = datetime.strptime(exp, "%Y-%m-%d")
            days_away = (exp_date - today).days
            if expiry_days_min <= days_away <= expiry_days_max:
                valid_expiries.append(exp)
                
        if not valid_expiries:
            logger.warning(f"No expiries found in {expiry_days_min}-{expiry_days_max} day range")
            # if none were found then we use the nearest one possible 
            valid_expiries = [expirations[0]]
            
        logger.info(f"Found {len(valid_expiries)} valid expiries: {valid_expiries}")
        
        # now we willl take the options chain for the first valid expiry. THIS SIMILAR TO HOW WE GO ON ROBINHOOD AND EE THE CONTRACTS BY EXPRIY ON FRIDAYS AND ALL
        # we will update this to multiple expiries soon
        chain = stock.option_chain(valid_expiries[0])
        
        # return the puts and call seperatley
        return {
            "puts": chain.puts,
            "calls": chain.calls,
            "expiry": valid_expiries[0],
            "all_valid_expiries": valid_expiries
        }
        
    except Exception as e:
        logger.error(f"Error fetching options chain: {e}")
        return None
    

# this is the implied volatility function and we are fecthing it using this function 
def get_iv_data(ticker: str) -> dict:
    """
    IV = the fear in the market high IV means sudden changes can happen any moment of time, low IV means not much change will happen
    
    Args:
        ticker: Stock symbol
        
    Returns:
        Dictionary with IV stats
    """
    try:
        logger.info(f"Fetching IV data for {ticker}!!!")
        
        stock = yf.Ticker(ticker)

        time.sleep(2)
        
        # basic information about the stock
        info = stock.info
        
        # 52 week high/low will be useful for context of the IV
        hist = stock.history(period="1y")
        
        # Current price
        current_price = hist['Close'].iloc[-1]
        
        # getting the 52 week price range
        week_52_high = hist['Close'].max()
        week_52_low = hist['Close'].min()
        
        # position of the price, throughout the 52 week kaha pe hai wo price
        # 0% = 52 week low, 100% = 52 week high
        price_position = ((current_price - week_52_low) / 
                         (week_52_high - week_52_low)) * 100
        
        # IV data dictionary
        iv_data = {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "week_52_high": round(week_52_high, 2),
            "week_52_low": round(week_52_low, 2),
            "price_position_pct": round(price_position, 2),
            "avg_volume": info.get("averageVolume", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
        }
        
        logger.info(f"{ticker} current price: ${iv_data['current_price']}")
        return iv_data
        
    except Exception as e:
        logger.error(f"Error fetching IV data: {e}")
        return None
    



# we will do testing now using the code below
if __name__ == "__main__":  # this makes this the main file file for now
    
    # Test ticker
    TEST_TICKER = "F"
    
    print("\n" + "="*50)
    print(f"TESTING FETCHER WITH {TEST_TICKER}")
    print("="*50)
    
    # Test 1 — Stock data
    print("\nSTOCK DATA:")
    stock_data = get_stock_data(TEST_TICKER)
    if stock_data is not None:
        print(f"Last 5 days:\n{stock_data.tail()}")
    
    # Test 2 — Options chain
    print("\nOPTIONS CHAIN:")
    options = get_options_chain(TEST_TICKER)
    if options is not None:
        print(f"Expiry: {options['expiry']}")
        print(f"Number of puts: {len(options['puts'])}")
        print(f"Number of calls: {len(options['calls'])}")
        print(f"\nTop 5 puts:\n{options['puts'][['strike', 'bid', 'ask', 'impliedVolatility', 'openInterest']].head()}")
    
    # Test 3 — IV data
    print("\nIV DATA:")
    iv_data = get_iv_data(TEST_TICKER)
    if iv_data is not None:
        for key, value in iv_data.items():
            print(f"  {key}: {value}")