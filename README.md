# 🎡 LiveTradingApplication
### AI-Powered Wheel Strategy Trading System

![Python](https://img.shields.io/badge/Python-3.11-blue)
![ML](https://img.shields.io/badge/ML-XGBoost%20%7C%20RandomForest%20%7C%20FinBERT-orange)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

---

## What is this?

An intelligent trading assistant that implements the **Wheel Strategy** using a multi-model AI system. It doesn't just suggest trades — it thinks, analyzes, and acts.

---

## How it works

Three AI models work together like a panel of expert advisors:

| Model | Question | Algorithm |
|---|---|---|
| IV Predictor | *When should I trade?* | XGBoost |
| Strike Selector | *Which strike price?* | Random Forest |
| Sentiment Analyzer | *Is it safe to trade?* | FinBERT |

Only when all three agree — a trade is suggested.

---

## Core Features

- Live options chain analysis with real-time Greeks
- Black-Scholes fair value calculation
- CSP & Covered Call screening
- ML-powered trade timing & strike selection
- Financial news sentiment analysis
- Alpaca API integration for order execution *(coming soon)*
- React dashboard *(coming soon)*

---

## Stack
Python · XGBoost · scikit-learn · HuggingFace Transformers
yfinance · FastAPI · React · Alpaca API

---