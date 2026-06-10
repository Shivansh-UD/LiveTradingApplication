# firstly we will import all the ncessary packages
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
import logging
import sys
import os
import warnings
warnings.filterwarnings('ignore') #this ignores the warnings that be popping up

sys.path.append('.')
from src.data.fetcher import get_stock_data, get_options_chain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# we will now make features for our model to train on, VERY IMPORTANT AND KEEN. We will do this using the 5 years worth of data from the past of any stock
def create_iv_features(ticker: str) -> pd.DataFrame: #returns a dataframe
    """
    This function makes features from raw data that we can use to 
    trin our XGBoost model. We are doing this with data from 5 years up until now.

    Features we create:
    - Historical volatility (actual price movement)
    - Price momentum (trend direction)
    - Volume patterns (market interest)
    - Distance from moving averages
    - IV itself as a lagged feature

    Args:
        ticker: Stock symbol like "F"

    Returns:
        DataFrame with features and target variable
    """
    try:
        logger.info(f"Creating IV features for {ticker}...")

        # retrive data from last 5 years
        stock_data = get_stock_data(ticker, period="5y")

        if stock_data is None or stock_data.empty:
            logger.error("Could not fetch stock data!")
            return None

        df = stock_data.copy()

        # FEATURE 1: Historical Volatility (HV)
        # Actual price movement measure
        # If the stock goes up and down a lot it means = high HV
        # HV are IV closely related
        df['daily_return'] = df['Close'].pct_change()

        # 10 day rolling volatility — annualized
        df['hv_10'] = df['daily_return'].rolling(10).std() * np.sqrt(252) # in 1 year there are 252 trading days
        # 20 day rolling volatility
        df['hv_20'] = df['daily_return'].rolling(20).std() * np.sqrt(252)
        # 30 day rolling volatility
        df['hv_30'] = df['daily_return'].rolling(30).std() * np.sqrt(252)

        # FEATURE 2: Price Momentum
        # Trend direction, is the stock going up or down
        # Strong momentum = IV usually increases
        df['momentum_5'] = df['Close'].pct_change(5)    # 5 day
        df['momentum_10'] = df['Close'].pct_change(10)  # 10 day
        df['momentum_20'] = df['Close'].pct_change(20)  # 20 day

        # FEATURE 3: Moving Average Distance
        # how far is the price of the stock from the average of past few days.
        # Far from MA = unusual = higher IV
        # Close to MA = Low IV, market is calmer 
        df['ma_20'] = df['Close'].rolling(20).mean()
        df['ma_50'] = df['Close'].rolling(50).mean()

        # Distance from moving averages (percentage)
        df['dist_ma20'] = (df['Close'] - df['ma_20']) / df['ma_20']
        df['dist_ma50'] = (df['Close'] - df['ma_50']) / df['ma_50']

        # FEATURE 4: Volume Analysis
        # High volume = big moves coming = higher IV
        df['volume_ma20'] = df['Volume'].rolling(20).mean()
        # Volume ratio, todays vlume vs the average
        df['volume_ratio'] = df['Volume'] / df['volume_ma20']

        # FEATURE 5: Price Range (High - Low)
        # bigger range = volatile day = higher IV
        df['daily_range'] = (df['High'] - df['Low']) / df['Close']
        df['range_ma10'] = df['daily_range'].rolling(10).mean()

        # TARGET VARIABLE
        # Future 5-day realized volatility we are predicting this
        # This approximates the IV for future
        df['future_hv_5'] = (
            df['daily_return']
            .shift(-5)                    # 5 days future
            .rolling(5)                   # 5-day window
            .std() * np.sqrt(252)         # annualized
        )

        # NaN rows dropped
        df = df.dropna()

        logger.info(f"Created {len(df)} samples with features!")
        return df

    except Exception as e:
        logger.error(f"Feature creation error: {e}")
        return None
    
# This function trains the model for prediction XGBoost used here. THIS THE MAIN THING OF TIS FILE.
def train_iv_model(ticker: str):
    """
    This function trains our XGBoost model on the features
    we created above. The model learns from 5 years of data from the past and 
    attempts to predict the future IV for 5 days.

    Steps on what is hapeing at each stage:
    - Get features from create_iv_features() -> LITERALLY THE FUNCTION RIGHT ABOVE THIS ONE
    - Split data 80% train, 20% test -> simple enough use 80% to train andf the rest to test
    - Scale the features (same units) -> this important so that all the features are on equal footing and no fearture is favored more over the opther in the model training
    - Train XGBoost
    - Check accuracy
    - Return trained model

    Args:
        ticker: Stock symbol like "F"

    Returns:
        Dictionary with model, scaler, features, accuracy
    """
    try:
        logger.info(f"Training IV model for {ticker}...")

        # get the features we created above, just a simple call to the function above
        df = create_iv_features(ticker)

        # if empty return Data frame then return None
        if df is None:
            return None

        # these are all the input columns for our model
        # basically everything except the target variable
        feature_cols = [
            'hv_10', 'hv_20', 'hv_30',           # historical volatility
            'momentum_5', 'momentum_10', 'momentum_20', # price momentum
            'dist_ma20', 'dist_ma50',              # distance from MA
            'volume_ratio',                         # volume analysis
            'daily_range', 'range_ma10'            # price range
        ]

        # X = inputs (features), y = output (what we predict)
        # think of it like:
        # X = is the material we train on 
        # y = What we are trying to predict
        X = df[feature_cols]
        y = df['future_hv_5']

        # Train/Test split — 80% train, 20% test
        # shuffle=False is very important here becasue time matters
        # This is because data from the future cannot be used in training, not logical
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            shuffle=False  # time series, order matters
        )

        # Feature scaling — brings all features to same scale
        # model gets confused without scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # XGBoost model — 200 decision trees will be made
        # this is because we will have 200 decision trees that go 4 levels deep to answer, "what will be the future IV?"
        model = XGBRegressor(
            n_estimators=200,    # 200 decision trees
            max_depth=4,         # how deep each tree goes
            learning_rate=0.05,  # how big each learning step is
            subsample=0.8,       # use 80% of data per tree
            random_state=42,     # reproducible results
            verbosity=0          # no spam output
        )

        # TRAIN THE MODEL
        logger.info("Training XGBoost...")
        model.fit(X_train_scaled, y_train)

        # check how accurate it is on test data
        # MAE = Mean Absolute Error
        # lower MAE = more accurate predictions
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)

        logger.info(f"Model trained successfully.")
        logger.info(f"MAE: {mae:.4f}")
        logger.info(f"Training samples: {len(X_train)}")
        logger.info(f"Test samples    : {len(X_test)}")

        # return everything we need for predictions later
        return {
            "model": model,
            "scaler": scaler,
            "feature_cols": feature_cols,
            "mae": mae,
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }

    except Exception as e:
        logger.error(f"Model training error: {e}")
        return None

# This function is basically using the model we built above and using it to predict the IV for the next 5 days
def predict_iv(ticker: str, model_package: dict) -> dict:
    """
    This function uses our trained model to predict
    what IV will look like in the next 5 days.

    Args:
        ticker: Stock symbol like "F"
        model_package: the output from train_iv_model()
                       contains model, scaler, feature_cols

    Returns:
        Dictionary with prediction and trading signal
    """
    try:
        model = model_package['model']
        scaler = model_package['scaler']
        feature_cols = model_package['feature_cols']

        # get the latest features from raw data todays data
        df = create_iv_features(ticker)

        if df is None:
            return None

        # we only need the LATEST row 
        # analogy: we only need todays weather readings
        # to predict tomorrows weather, not last years.
        latest = df[feature_cols].iloc[-1:].values
        latest_scaled = scaler.transform(latest)

        # PREDICT
        predicted_iv = model.predict(latest_scaled)[0]

        # calculate historical average IV for comparison purpose
        # this is our baseline, basically it tells yuse what the normal IV for this stock is around/like
        hist_iv_mean = df['hv_20'].mean()
        hist_iv_std = df['hv_20'].std()

        # generate a trading signal based on prediction, meaning if we should do a trade or not
        # high IV = good time to sell options
        # low IV = wait, premiums are less
        if predicted_iv > hist_iv_mean + (0.5 * hist_iv_std):
            signal = "HIGH"
            signal_emoji = "✅"
            csp_signal = "SELL CSP, IV is high"
            cc_signal = "SELL CC, great time to collect premium!"
            recommendation = "GREAT TIME FOR WHEEL STRATEGY"

        elif predicted_iv > hist_iv_mean:
            signal = "MODERATE"
            signal_emoji = "⚠️"
            csp_signal = "CSP okay, but pick higher strike for more premium"
            cc_signal = "CC okay,  but manage position size"
            recommendation = "OKAY TO TRADE BUT BE CAREFUL"

        else:
            signal = "LOW"
            signal_emoji = "❌"
            csp_signal = "DO NOT SELL CSP, premium too low"
            cc_signal = "DO NOT SELL CC, wait for IV to rise"
            recommendation = "WAIT, IV IS LOW"

        return {
            "ticker": ticker,
            "predicted_iv_pct": round(predicted_iv * 100, 2),
            "historical_avg_iv_pct": round(hist_iv_mean * 100, 2),
            "signal": signal,
            "signal_emoji": signal_emoji,
            "csp_signal": csp_signal,     
            "cc_signal": cc_signal,     
            "recommendation": recommendation,
            "model_mae_pct": round(model_package['mae'] * 100, 4)
}

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None











#THIS IS ONLY USED FOR TESTING THE MODEL

if __name__ == "__main__":

    TEST_TICKER = "F"

    def section(title):
        print(f"\n{'='*55}")
        print(f"  {title}")
        print(f"{'='*55}")

    # header
    print("\n" + "="*55)
    print("   LAYER 3 — MODEL 1 — IV PREDICTOR")
    print("   Algorithm : XGBoost")
    print(f"   Ticker    : {TEST_TICKER}")
    print("="*55)

    # TRAIN
    section("STEP 1 — TRAINING THE MODEL")
    print(f"""
  What is happening here?
  We are feeding 5 years of Ford price data into
  XGBoost. It will learn patterns like:
  "when HV spikes + volume is high = IV goes up next week"

  Training on {TEST_TICKER} — please wait 30-60 seconds...
    """)

    model_package = train_iv_model(TEST_TICKER)

    if model_package:
        print(f"""
  Model trained successfully!

  Training Samples : {model_package['training_samples']}
  Test Samples     : {model_package['test_samples']}
  MAE              : {round(model_package['mae']*100, 4)}% """)

    # PREDICT
    section("STEP 2 — IV PREDICTION FOR NEXT 5 DAYS")
    print("""
  What is happening here?
  We take TODAYS market data for Ford and feed
  it into our trained model. It outputs a predicted
  IV for the next 5 trading days!
    """)

    if model_package:
        prediction = predict_iv(TEST_TICKER, model_package)

        if prediction:
            print(f"""
    Ticker              : {prediction['ticker']}
    Predicted IV        : {prediction['predicted_iv_pct']}%
    Historical Avg IV   : {prediction['historical_avg_iv_pct']}%
    Model Accuracy(MAE) : {prediction['model_mae_pct']}%

    IV SIGNAL  : {prediction['signal']} {prediction['signal_emoji']}

    CSP SIGNAL : {prediction['csp_signal']}
    CC SIGNAL  : {prediction['cc_signal']}

    OVERALL: {prediction['recommendation']}
    """)

    print("="*55)
    print("  NOTE: This model uses historical volatility")
    print("  as a proxy for IV. Real IV needs paid data.")
    print("  But HV and IV are strongly correlated!")
    print("="*55 + "\n")