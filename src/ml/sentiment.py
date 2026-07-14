# This is the third model of our project and this model specifically  check wether its safe to do a trade in this stock based on the news. 
# we will use the FinBert model  which will output Positive / Negative / Neutral + confidence score + Trading recommendation (safe/risky), and the input will be Recent news headlines about Ford.
# we will use the yahoo finance free API here aswell

# Firstlyu we will import all the packages needed 
import pandas as pd
import logging
import sys
import warnings
warnings.filterwarnings('ignore')

from transformers import pipeline
import yfinance as yf

sys.path.append('.')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#Now we will load the FinBert Model
logger.info("Loading FinBERT model...")

# this is the m,ain part of how we assign the FinBert Model to a variable and we just call this wherever we need
sentiment_pipeline = pipeline(
    "text-classification",
    model="ProsusAI/finbert"
)

logger.info("FinBERT loaded!")


# Now here is the "News fetcher". This getys us the news/recent headlines about the stock we are tal;king about currently.
def get_stock_news(ticker: str, max_articles: int = 20) -> list:
    """
    Fetches recent news headlines for a stock.
    Uses yfinance (same library as fetcher.py)

    Args:
        ticker: Stock symbol like "F"
        max_articles: how many headlines to fetch

    Returns:
        List of headline strings
    """
    try:
        logger.info(f"Fetching news for {ticker}...")

        stock = yf.Ticker(ticker)
        news = stock.news # in built function that gets the news latest.

        # In case there was no news to fecth
        if not news:
            logger.warning(f"No news found for {ticker}")
            return []

        headlines = []
        for article in news[:max_articles]:
            # yfinance has two different formats
            # depending on version. We can handle both versions with this approach. 
            if 'content' in article:
                title = article['content'].get('title', '')
            else:
                title = article.get('title', '')

            if title:
                headlines.append(title)

        logger.info(f"Found {len(headlines)} headlines!")
        return headlines

    except Exception as e:
        logger.error(f"News fetching error: {e}")
        return []
    

# this is where we use the FinBert model and feed it all the headline news we got and 
#Finbert gives a final result as an overall score sort of.
def analyze_sentiment(headlines: list) -> dict: #we pass in the headlines list from the above function in here
    """
    Runs every headline through FinBERT

    For each headline FinBERT gives:
    - label: positive / negative / neutral
    - score: confidence 0 to 1

    Then we combine all headlines into
    one overall score!

    Args:
        headlines: list of news headline strings

    Returns:
        Dictionary with aggregated results
    """
    try:
        if not headlines:
            logger.warning("No headlines to analyze!")
            return None

        logger.info(f"Analyzing {len(headlines)} headlines...")

        results = []
        for headline in headlines:
            # max 512 characters — FinBERT limit
            prediction = sentiment_pipeline(headline[:512])[0]
            results.append({
                "headline": headline,
                "label": prediction['label'],
                "score": round(prediction['score'], 3)
            })

        df = pd.DataFrame(results) # convertring the results to a dataframe because we will be using this in the next step 

        # count positive/negative/neutral
        sentiment_counts = df['label'].value_counts().to_dict()

        # weighted score calculation
        # positive = +1, negative = -1, neutral = 0
        # multiplied by confidence score
        # analogy: 5 good reviews + 1 bad review
        # = mostly positive overall
        score_map = {"positive": 1, "negative": -1, "neutral": 0}
        df['weighted_score'] = df.apply(
            lambda row: score_map.get(row['label'], 0) * row['score'],
            axis=1
        )

        # average score across all headlines
        overall_score = df['weighted_score'].mean()

        return {
            "headlines_analyzed": len(headlines),
            "sentiment_counts": sentiment_counts,
            "overall_score": round(overall_score, 3),
            "details": df
        }

    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return None
    
# Now this is the final stage of this process where the below function does all of the stuff from above functions and gives an overall signal of what action we should be taking
def get_sentiment_signal(ticker: str) -> dict:
    """
    Full pipeline in one function:
    fetch news → analyze → generate signal!


    Signal logic:
    score > 0.15  = POSITIVE  → safe to trade
    score < -0.15 = NEGATIVE  → DO NOT trade
    in between    = NEUTRAL   → be careful

    Args:
        ticker: Stock symbol like "F"

    Returns:
        Dictionary with final trading signal
    """
    try:
        # step 1: get news headlines (CALL TO THE VERY FIRST FUNCTION IN THIS FILE)
        headlines = get_stock_news(ticker)

        # no news found — proceed with caution
        if not headlines:
            return {
                "ticker": ticker,
                "signal": "NO DATA",
                "signal_emoji": "❓",
                "recommendation": "No recent news — proceed with normal caution",
                "overall_score": 0,
                "headlines_analyzed": 0
            }

        # step 2: analyze sentiment of headlines(CALL TO SECOND FUNCTION IN THIS FILE)
        analysis = analyze_sentiment(headlines)

        if analysis is None:
            return None

        score = analysis['overall_score'] # final score we get we put inside this column

        # step 3: generate final trading signal
        # red flag = automatic gate closes!
        if score < -0.15:
            signal = "NEGATIVE"
            signal_emoji = "🚫"
            recommendation = "DO NOT TRADE — bad news detected, stay out!"

        elif score > 0.15:
            signal = "POSITIVE"
            signal_emoji = "✅"
            recommendation = "GREEN LIGHT — news supports trading!"

        else:
            signal = "NEUTRAL"
            signal_emoji = "⚠️"
            recommendation = "PROCEED WITH CAUTION — mixed news"

        return {
            "ticker": ticker,
            "signal": signal,
            "signal_emoji": signal_emoji,
            "recommendation": recommendation,
            "overall_score": score,
            "headlines_analyzed": analysis['headlines_analyzed'],
            "sentiment_counts": analysis['sentiment_counts'],
            "details": analysis['details']
        }

    except Exception as e:
        logger.error(f"Signal error: {e}")
        return None
    

# THIS IS JUST FOR TESTING THE CODE ABOVE. THE BELOW COPDE IS AN EXAMPLE OF HOW WE CAN USE THIS

if __name__ == "__main__":

    TEST_TICKER = "F"

    def section(title):
        print(f"\n{'='*55}")
        print(f"  {title}")
        print(f"{'='*55}")

    print("\n" + "="*55)
    print("   LAYER 3 — MODEL 3 — SENTIMENT ANALYZER")
    print("   Algorithm : FinBERT")
    print(f"   Ticker    : {TEST_TICKER}")
    print("="*55)

    section("FETCHING NEWS + ANALYZING SENTIMENT")
    print(f"""
  What is happening here?
  We fetch recent Ford news headlines and run
  each one through FinBERT — a financial AI
  trained on millions of financial articles!
  It understands terms like "beat estimates"
  and "supply chain issues" perfectly!
    """)

    result = get_sentiment_signal(TEST_TICKER)

    if result:
        print(f"""
  Ticker             : {result['ticker']}
  Headlines Analyzed : {result['headlines_analyzed']}
  Overall Score      : {result['overall_score']} (-1 to +1)

  SIGNAL : {result['signal']} {result.get('signal_emoji', '')}

  RECOMMENDATION:
  {result['recommendation']}
        """)

        # show breakdown
        if 'sentiment_counts' in result:
            print("  Breakdown:")
            for label, count in result['sentiment_counts'].items():
                print(f"    {label:<10} : {count} headlines")

        # show each headline with its label
        if 'details' in result and not result['details'].empty:
            print("\n  Individual Headlines:")
            for _, row in result['details'].iterrows():
                print(f"    [{row['label'].upper():<8}] "
                      f"{row['headline'][:55]}")

    print("\n" + "="*55)
    print("  FinBERT understands financial language!")
    print("  'Missed earnings' = NEGATIVE")
    print("  'Beat guidance'   = POSITIVE")
    print("="*55 + "\n")