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