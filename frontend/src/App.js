import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import StockSearch from './components/StockSearch';
import MLSignals from './components/MLSignals';
import OptionsTable from './components/OptionsTable';
import Sentiment from './components/Sentiment';

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [calculateData, setCalculateData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [ticker, setTicker] = useState('');
  const [breakeven, setBreakeven] = useState('');

  return (
    <div className="app">
      <Header />

      <StockSearch
        ticker={ticker}
        setTicker={setTicker}
        breakeven={breakeven}
        setBreakeven={setBreakeven}
        setAnalysisData={setAnalysisData}
        setCalculateData={setCalculateData}
        setLoading={setLoading}
        setError={setError}
        loading={loading}
      />

      {error && (
        <div className="error-banner">⚠️ {error}</div>
      )}

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Running AI analysis — training models...</p>
          <p className="loading-sub">This takes 30-60 seconds ☕</p>
        </div>
      )}

      {analysisData && !loading && (
        <div className="results-container">

          {/* Stock Snapshot */}
          <div className="stock-snapshot">
            <div className="snapshot-item">
              <span className="label">Current Price</span>
              <span className="value green">
                ${analysisData.stock_info.current_price}
              </span>
            </div>
            <div className="snapshot-item">
              <span className="label">52W High</span>
              <span className="value">
                ${analysisData.stock_info.week_52_high}
              </span>
            </div>
            <div className="snapshot-item">
              <span className="label">52W Low</span>
              <span className="value">
                ${analysisData.stock_info.week_52_low}
              </span>
            </div>
            <div className="snapshot-item">
              <span className="label">Price Position</span>
              <span className="value yellow">
                {analysisData.stock_info.price_position_pct}%
              </span>
            </div>
          </div>

          {/* ML Signals */}
          <MLSignals signals={analysisData.ml_signals} />

          {/* Sentiment */}
          <Sentiment sentiment={analysisData.sentiment} />

          {/* Options Table */}
          <OptionsTable
            analysisData={analysisData}
            calculateData={calculateData}
            breakeven={breakeven}
          />

        </div>
      )}

      {/* Break-even only mode — no full analysis */}
      {calculateData && !analysisData && !loading && (
        <div className="results-container">
          <OptionsTable
            analysisData={null}
            calculateData={calculateData}
            breakeven={breakeven}
          />
        </div>
      )}

    </div>
  );
}

export default App;