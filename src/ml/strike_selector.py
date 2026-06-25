'''
This is our second model and this model work along with the first in order to help 
pick the correct strike price based on all the information it has.
'''
# first we will import all the correct packages we need 
# In this model we will use Randome Forest model
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import logging
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.append('.')
from src.data.fetcher import get_stock_data, get_options_chain, get_iv_data
from src.ml.iv_predictor import train_iv_model, predict_iv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# This function creates features which we will pass onto our model(RF) to use in training
def create_strike_features(ticker: str) -> pd.DataFrame:
    """
    Creates features for the Random Forest model.

    The Features it will create:
    - IV level (high/low/moderate)
    - Price position vs moving averages
    - Days to expiry zone
    - Historical volatility ratios
    - Price momentum direction

    Args:
        ticker: Stock symbol like "F"

    Returns:
        DataFrame with features + target (best delta zone)
    """
    try:
        logger.info(f"Creating strike features for {ticker}...")

        # get 5 years of data, same as the IV predictor module
        stock_data = get_stock_data(ticker, period="5y")

        if stock_data is None or stock_data.empty:
            logger.error("Could not fetch stock data!")
            return None

        df = stock_data.copy()

        # daily returns as a feature in the Data frame
        df['daily_return'] = df['Close'].pct_change()

        # FEATURE 1: IV Level
        '''
        This feature calculates the current level of the IV to see 
        which strike price is right to puick from. 

        High IV level means we can sell further OTM strike prices
        LOW IV level means we need to go closer ATM for premium
        '''
        df['hv_20'] = df['daily_return'].rolling(20).std() * np.sqrt(252)
        df['hv_10'] = df['daily_return'].rolling(10).std() * np.sqrt(252)

        # IV ratio gives us wether the current IV is high or low vs recent history
        # >1 means IV is higher than recent average = good for selling positions
        df['iv_ratio'] = df['hv_10'] / df['hv_20']

        # FEATURE 2: Price Position
        '''
        These features help us in seeing where the is the stock vs its MA
        Stock above MA = bullish = safer to sell puts
        Stock below MA = bearish = be more careful

        we do this in increments of 20 days and 50 days
        '''
        df['ma_20'] = df['Close'].rolling(20).mean()
        df['ma_50'] = df['Close'].rolling(50).mean()
        df['dist_ma20'] = (df['Close'] - df['ma_20']) / df['ma_20']
        df['dist_ma50'] = (df['Close'] - df['ma_50']) / df['ma_50']

        # FEATURE 3: Momentum
        # Which direction is the stock moving in
        # Strong uptrend = safer to sell puts
        # Strong downtrend = be careful
        df['momentum_5'] = df['Close'].pct_change(5)
        df['momentum_10'] = df['Close'].pct_change(10)

        # FEATURE 4: Volatility Trend
        # Is volatility increasing or decreasing.
        # Rising volatility = IV about to spike
        # Falling volatility = IV about to drop
        df['hv_30'] = df['daily_return'].rolling(30).std() * np.sqrt(252)
        # short term vs long term volatility ratio
        df['vol_trend'] = df['hv_10'] / df['hv_30']

        # FEATURE 5: Price Range Expansion
        # Are daily candles getting bigger
        # Bigger candles = more volatile = higher IV
        df['daily_range'] = (df['High'] - df['Low']) / df['Close']
        df['range_ma10'] = df['daily_range'].rolling(10).mean()
        # is range expanding or getting lesser
        df['range_expansion'] = df['daily_range'] / df['range_ma10']

        # TARGET VARIABLE
        # Best delta zone for CSP based on conditions

        # We look at next 30 days outcome:
        # If stock drops < 5%  = AGGRESSIVE ok (0.35 delta)
        # If stock drops 5-10% = MODERATE (0.25 delta)
        # If stock drops > 10% = CONSERVATIVE (0.15 delta)
        #
        # This teaches the model:
        # "In these conditions, how far can stock drop?"

        # future 30 day return
        df['future_return_30'] = df['Close'].pct_change(30).shift(-30)

        # classify into delta zones based on future drop
        def classify_delta_zone(future_return):
            #this if-else block is the same thing as the big comments block above
            if pd.isna(future_return):
                return None
            elif future_return > -0.05:
                # stock stayed relatively stable
                # aggressive delta ok, more premium!
                return 'AGGRESSIVE'    # 0.30-0.40 delta
            elif future_return > -0.10:
                # moderate drop, be careful
                return 'MODERATE'      # 0.20-0.30 delta
            else:
                # big drop, be conservative
                return 'CONSERVATIVE'  # 0.10-0.20 delta

        df['delta_zone'] = df['future_return_30'].apply(classify_delta_zone)

        # drop NaN rows
        df = df.dropna()

        # drop rows where delta_zone is None
        df = df[df['delta_zone'].notna()]

        logger.info(f"Created {len(df)} samples!")
        logger.info(f"Delta zone distribution:\n{df['delta_zone'].value_counts()}")

        return df

    except Exception as e:
        logger.error(f"Feature creation error: {e}")
        return None
    

# This function is where we feed it the features we made above and train our model to gert the target variable we want
def train_strike_model(ticker: str):
    """
    Trains Random Forest to predict best delta zone

    Args:
        ticker: Stock symbol like "F"

    Returns:
        Dictionary with model, scaler, accuracy info
    """
    try:
        logger.info(f"Training Strike Selector for {ticker}...")

        df = create_strike_features(ticker) #this is a call to the function above that creates us our features

        if df is None:
            return None

        # input features for the model, WHAT WE ARE GOING TO GIVE THE MODEL TO TRAIN WITH 
        feature_cols = [
            'hv_10', 'hv_20', 'hv_30',      # volatility levels
            'iv_ratio',                        # IV high or low?
            'dist_ma20', 'dist_ma50',          # price vs MA
            'momentum_5', 'momentum_10',       # price direction
            'vol_trend',                       # volatility trend
            'daily_range', 'range_expansion'   # range analysis
        ]

        X = df[feature_cols]
        y = df['delta_zone'] #Target variable, this is what we are trying to predict

        # 80/20 split, same as Model 1
        # shuffle=False — time series, timing matters in this case.
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            shuffle=False
        )

        # scale features, so everything is on equal footing with each other
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Random Forest, 200 trees voting together
        # n_estimators=200 means 200 decision trees
        # each tree sees a random subset of features and data, this prevents overfitting
        model = RandomForestClassifier(
            n_estimators=200,    # 100 trees voting
            max_depth=5,         # tree depth
            min_samples_split=20,# minimum samples to split
            random_state=42,     # reproducible
            n_jobs=-1            # use all CPU cores!
        )

        logger.info("Training Random Forest...")
        model.fit(X_train_scaled, y_train)

        # check accuracy of the model
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)

        logger.info(f"Model trained! Accuracy: {accuracy:.2%}")

        # feature importancem, which features matter most
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        return {
            "model": model,
            "scaler": scaler,
            "feature_cols": feature_cols,
            "accuracy": accuracy,
            "feature_importance": feature_importance,
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }

    except Exception as e:
        logger.error(f"Training error: {e}")
        return None
    


#This funtion basically uses our trained model to predict the strike price best for us
def predict_strike(ticker: str, model_package: dict,
                   current_price: float) -> dict:
    """

    Takes todays market conditions and outputs:
    - Which delta zone to use (aggressive/moderate/conservative)
    - Exact delta range recommendation
    - Strike price range to look at
    - Confidence score

    Args:
        ticker: Stock symbol
        model_package: output from train_strike_model()
        current_price: current stock price

    Returns:
        Dictionary with strike recommendation
    """
    try:
        model = model_package['model']
        scaler = model_package['scaler']
        feature_cols = model_package['feature_cols']

        # get latest features
        df = create_strike_features(ticker)

        if df is None:
            return None

        # todays snapshot only
        latest = df[feature_cols].iloc[-1:].values
        latest_scaled = scaler.transform(latest)

        # predict delta zone
        predicted_zone = model.predict(latest_scaled)[0]

        # confidence = how many trees agreed?
        # higher confidence = more trees voted same way!
        probabilities = model.predict_proba(latest_scaled)[0]
        confidence = max(probabilities) * 100

        # translate zone to actual delta + strike range
        if predicted_zone == 'AGGRESSIVE':
            delta_range = "0.30 — 0.40"
            delta_mid = 0.35
            zone_explanation = "Market conditions are stable — go aggressive for more premium!"
            strike_pct = 0.96  # 4% below current price

        elif predicted_zone == 'MODERATE':
            delta_range = "0.20 — 0.30"
            delta_mid = 0.25
            zone_explanation = "Some uncertainty — moderate delta is safer here"
            strike_pct = 0.94  # 6% below current price

        else:  # CONSERVATIVE
            delta_range = "0.10 — 0.20"
            delta_mid = 0.15
            zone_explanation = "Conditions are risky — stay conservative!"
            strike_pct = 0.90  # 10% below current price

        # calculate suggested strike price
        suggested_strike = round(current_price * strike_pct, 1)

        return {
            "ticker": ticker,
            "current_price": current_price,
            "predicted_zone": predicted_zone,
            "delta_range": delta_range,
            "suggested_strike": suggested_strike,
            "confidence_pct": round(confidence, 1),
            "zone_explanation": zone_explanation,
        }

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None
    



# This is used for testing only

if __name__ == "__main__":

    TEST_TICKER = "F"

    def section(title):
        print(f"\n{'='*55}")
        print(f"  {title}")
        print(f"{'='*55}")

    print("\n" + "="*55)
    print("   LAYER 3 — MODEL 2 — STRIKE SELECTOR")
    print("   Algorithm : Random Forest")
    print(f"   Ticker    : {TEST_TICKER}")
    print("="*55)

    # get current price first
    iv_data = get_iv_data(TEST_TICKER)
    current_price = iv_data['current_price']

    # STEP 1 — TRAIN
    section("STEP 1 — TRAINING THE MODEL")
    print(f"""
  What is happening here?
  We show Random Forest 5 years of market conditions
  and what happened next. It learns which delta zone
  is safest given current conditions!

  Training on {TEST_TICKER} — please wait...
    """)

    model_package = train_strike_model(TEST_TICKER)

    if model_package:
        print(f"""
  Model trained successfully!

  Training Samples : {model_package['training_samples']}
  Test Samples     : {model_package['test_samples']}
  Accuracy         : {model_package['accuracy']:.2%}

  Top 3 Most Important Features:
    """)
        # show top 3 features
        top3 = model_package['feature_importance'].head(3)
        for _, row in top3.iterrows():
            print(f"  {row['feature']:<20} importance: {row['importance']:.4f}")

    # STEP 2 — PREDICT
    section("STEP 2 — STRIKE RECOMMENDATION")
    print(f"""
  Current Price : ${current_price}

  What is happening here?
  Model looks at todays conditions and recommends
  the safest delta zone for our CSP strike!
    """)

    if model_package:
        prediction = predict_strike(
            TEST_TICKER, model_package, current_price
        )

        if prediction:
            print(f"""
  Ticker            : {prediction['ticker']}
  Current Price     : ${prediction['current_price']}
  Recommended Zone  : {prediction['predicted_zone']}
  Delta Range       : {prediction['delta_range']}
  Suggested Strike  : ${prediction['suggested_strike']}
  Confidence        : {prediction['confidence_pct']}%

  WHY THIS ZONE?
  {prediction['zone_explanation']}
            """)

    print("="*55)
    print("  This model recommends WHICH strike to pick.")
    print("  Use with Model 1 IV signal for best results!")
    print("="*55 + "\n")