# BACKEND API

# This is our FastAPI server — same concept
# as Spring Boot but in Python
#
# It connects our ML models and analytics
# to the React frontend via API endpoints.
#
# Think of it like a waiter in a restaurant:
# - Kitchen (ML models) = makes the food
# - Waiter (FastAPI)    = serves it to table
# - Table (React)       = where user sees it!

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import logging
import numpy as np  # moved to top — needed everywhere!

sys.path.append('.')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# CREATE THE APP — same as Spring Boot's
# @SpringBootApplication — this is the entry
# point of our entire backend!
app = FastAPI(
    title="Wheel Strategy Trading API",
    description="AI-powered Wheel Strategy analyzer",
    version="1.0.0"
)

# CORS SETUP — allows React (port 3000) to
# talk to FastAPI (port 8000)
# this is setting up the ports in simple terms
app.add_middleware(
    CORSMiddleware, # this gives permission to react so it can communicate with the backend
    allow_origins=["http://localhost:3000"],  # React's address
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, etc all allowed. REMEMBER SAME IN SPRINGBOOT THE * ALLOWS EVERYTHING BUT IF WE WANT TO WE CAN LIMIT IT TO JUST GET REQUESTS IF WE WANTED TO
    allow_headers=["*"],
)

# HEALTH CHECK ENDPOINT
# Same as Spring Boot Actuator /health
# React calls this to check if backend is up!
# THIS IS THE ROOT PAGE OF OUR APPLICATION. HOME PAGE.
@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": "Wheel Strategy API is live!"
    }

# THE STARTING BELOW PART IS OUR ACTUAL APPLICATION APIS. THREE MODELS = THREE APIs

# IMPORTS — These are all the Layers 1, 2, 3 files which we are importing here to be able to call the right functions where we need them.
# Same as @Autowired in Spring Boot!
from src.data.fetcher import (
    get_stock_data,
    get_options_chain,
    get_iv_data
)
from src.analytics.greeks import (
    csp_screener,
    covered_call_screener,
    black_scholes,
    calculate_greeks
)
from src.ml.iv_predictor import train_iv_model, predict_iv
from src.ml.strike_selector import train_strike_model, predict_strike
from src.ml.sentiment import get_sentiment_signal


# HELPER FUNCTIONS

# cleans NaN and Infinity from DataFrames
# JSON doesnt understand NaN or Infinity
# analogy: removing broken items before
# putting them in a shipping box
def clean_records(df, cols=None):
    if df is None or df.empty:
        return []
    data = df[cols] if cols else df
    return data.head(5).replace(
        [np.inf, -np.inf], None
    ).where(
        data.head(5).notna(), None
    ).to_dict('records')


# checks if price is valid
# In the night time and on an invalid ticker we get NaN value
# NaN = "Not a Number" = Yahoo Finance ne price nahi diya
def is_valid_price(price):
    if price is None:
        return False
    if isinstance(price, float) and np.isnan(price):
        return False
    return True


# ENDPOINT 1, THIS IS THE FIRST API AND IT DOES ALL THE ANALYSIS PARTS OF THE APPLICATION
@app.get("/api/analyze/{ticker}")
async def analyze_ticker(ticker: str):
    """
    Master endpoint — runs everything at once

    Same as Spring Boot's @GetMapping with
    @PathVariable — ticker comes from the URL

    Example: /api/analyze/F
    Returns: complete wheel strategy analysis for Ford
    """
    try:
        logger.info(f"Full analysis requested for {ticker}")

        # Step 1: fetch live data
        # same as calling @Service methods
        iv_data = get_iv_data(ticker) # this is one of the functions we wrote in the fetcher.py file

        if iv_data is None:
            # same as Spring Boot's ResponseEntity.notFound()
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch data for {ticker}"
            )

        current_price = iv_data['current_price']

        # NaN price check — happens after market hours
        # raat mein Yahoo Finance price nahi deta
        # proper 503 error denge instead of crashing!
        if not is_valid_price(current_price):
            raise HTTPException(
                status_code=503,
                detail=f"Price unavailable for {ticker} — try during market hours (9:30AM-4PM EST)!"
            )

        # Step 2: get options chain
        options = get_options_chain(ticker)

        # Step 3: run screeners
        csp_candidates = []
        cc_candidates = []

        if options:
            # both of these functions return a dataframe
            csp_df = csp_screener(options, current_price)
            cc_df = covered_call_screener(
                options, current_price,
                cost_basis=current_price - 0.30
            )

            # convert DataFrame to list for JSON response
            # using clean_records to handle NaN values!
            csp_candidates = clean_records(csp_df, [
                'strike', 'bid', 'ask', 'mid_price',
                'delta', 'theta', 'iv_pct',
                'return_if_expired'
            ])

            cc_candidates = clean_records(cc_df, [
                'strike', 'bid', 'ask', 'mid_price',
                'delta', 'theta', 'iv_pct',
                'return_if_expired',
                'profit_if_called', 'roi_if_called'
            ])

        # Step 4: ML Models
        # WE WILL NOW RUN THE MODELS ON THE INFORMATION WE HAVE JUST FETCHED

        # IV Predictor
        iv_model = train_iv_model(ticker)
        iv_prediction = None
        if iv_model:
            iv_prediction = predict_iv(ticker, iv_model)

        # Strike Selector
        strike_model = train_strike_model(ticker)
        strike_prediction = None
        if strike_model:
            strike_prediction = predict_strike(
                ticker, strike_model, current_price
            )

        # Step 5: Sentiment
        sentiment = get_sentiment_signal(ticker) # using the FinBert model. MORE INFO ON THIS IN THE SENTIMENT.PY FILE

        # Step 6: combine everything into one response
        # JSON FORMAT
        return {
            "ticker": ticker.upper(),
            "stock_info": {
                "current_price": current_price,
                "week_52_high": iv_data['week_52_high'],
                "week_52_low": iv_data['week_52_low'],
                "price_position_pct": iv_data['price_position_pct'],
            },
            "csp_candidates": csp_candidates,
            "cc_candidates": cc_candidates,
            "ml_signals": {
                "iv_signal": iv_prediction['signal'] if iv_prediction else "N/A",
                "iv_predicted_pct": iv_prediction['predicted_iv_pct'] if iv_prediction else 0,
                "csp_signal": iv_prediction['csp_signal'] if iv_prediction else "N/A",
                "cc_signal": iv_prediction['cc_signal'] if iv_prediction else "N/A",
                "strike_zone": strike_prediction['predicted_zone'] if strike_prediction else "N/A",
                "suggested_strike": strike_prediction['suggested_strike'] if strike_prediction else 0,
                "strike_confidence": strike_prediction['confidence_pct'] if strike_prediction else 0,
            },
            "sentiment": {
                "signal": sentiment['signal'] if sentiment else "N/A",
                "score": sentiment['overall_score'] if sentiment else 0,
                "recommendation": sentiment['recommendation'] if sentiment else "N/A",
                "headlines_analyzed": sentiment['headlines_analyzed'] if sentiment else 0,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ENDPOINT 2, THIS IS OUR SECOND API AND THIS IS BASICALLY A SENTIMENT CHECK
# NO MODEL TRAINING — ALL THIS DOES IS JUST CHECK THE NEWS AND RECENT HEADLINES ABOUT THE STOCK
@app.get("/api/sentiment/{ticker}")
async def get_sentiment(ticker: str):
    """
    No ML models — just news analysis.
    Faster than full analysis
    """
    try:
        result = get_sentiment_signal(ticker) # we wrote this function in the sentiment.py file as well

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Sentiment analysis failed"
            )

        # remove 'details' DataFrame because it is not JSON serializable
        result.pop('details', None)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ENDPOINT 3, THIS IS OUR THIRD API AND WILL SHOW US THE OPTIONS CHAIN.
# IN THE WEB PAGE WE WILL SHOW THIS AS A TABLE.
@app.get("/api/options/{ticker}")
async def get_options(ticker: str):
    try:
        iv_data = get_iv_data(ticker)

        if iv_data is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        current_price = iv_data['current_price']

        # NaN price check — raat mein ya invalid ticker pe hota hai
        # NaN matlab Yahoo Finance ne price nahi diya
        if not is_valid_price(current_price):
            raise HTTPException(
                status_code=503,
                detail=f"Price unavailable for {ticker} — try during market hours (9:30AM-4PM EST)!"
            )

        options = get_options_chain(ticker)

        if options is None:
            raise HTTPException(
                status_code=404,
                detail="No options found"
            )

        csp_df = csp_screener(options, current_price)
        cc_df = covered_call_screener(
            options, current_price,
            cost_basis=current_price - 0.30
        )

        return {
            "ticker": ticker.upper(),
            "current_price": current_price,
            "expiry": options['expiry'],
            # clean_records handles NaN and Infinity
            # JSON cannot handle these values!
            "csp_candidates": clean_records(csp_df),
            "cc_candidates": clean_records(cc_df),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Options error: {e}")
        raise HTTPException(status_code=500, detail=str(e))