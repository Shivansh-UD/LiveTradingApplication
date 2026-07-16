import React from 'react';
import axios from 'axios';

function StockSearch({
  ticker, setTicker,
  breakeven, setBreakeven,
  setAnalysisData, setCalculateData,
  setLoading, setError, loading
}) {

  // Full analysis — runs all 3 ML models
  const handleAnalyze = async () => {
    if (!ticker) {
      setError('Please enter a ticker symbol!');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setAnalysisData(null);
      setCalculateData(null);

      const response = await axios.get(
        `http://localhost:8000/api/analyze/${ticker.toUpperCase()}`
      );
      setAnalysisData(response.data);

    } catch (err) {
      if (err.response?.status === 503) {
        setError('Market is closed! Try during market hours (9:30AM-4PM EST)');
      } else if (err.response?.status === 404) {
        setError('Ticker not found! Check the symbol and try again.');
      } else {
        setError('Something went wrong. Please try again!');
      }
    } finally {
      setLoading(false);
    }
  };

  // Break-even filter — instant, no ML training
  const handleCalculate = async () => {
    if (!ticker) {
      setError('Please enter a ticker symbol!');
      return;
    }
    if (!breakeven) {
      setError('Please enter your break-even price!');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setCalculateData(null);

      const response = await axios.get(
        `http://localhost:8000/api/calculate/${ticker.toUpperCase()}`,
        { params: { breakeven: parseFloat(breakeven) } }
      );
      setCalculateData(response.data);

    } catch (err) {
      if (err.response?.status === 503) {
        setError('Market is closed! Try during market hours (9:30AM-4PM EST)');
      } else {
        setError('Something went wrong. Please try again!');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleAnalyze();
  };

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: '20px',
      padding: '28px',
      marginBottom: '20px',
    }}>

      <h2 style={{
        fontSize: '13px',
        fontWeight: '600',
        color: 'var(--text-secondary)',
        marginBottom: '20px',
        textTransform: 'uppercase',
        letterSpacing: '1px'
      }}>
        Analyze a Stock
      </h2>

      <div style={{
        display: 'flex',
        gap: '12px',
        flexWrap: 'wrap'
      }}>

        {/* Ticker Input */}
        <div style={{ flex: 1, minWidth: '150px' }}>
          <label style={{
            fontSize: '12px',
            color: 'var(--text-secondary)',
            display: 'block',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Stock Ticker
          </label>
          <input
            type="text"
            placeholder="e.g. F, AAPL, MSFT"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            onKeyPress={handleKeyPress}
            style={{
              width: '100%',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              padding: '14px 16px',
              color: 'var(--text-primary)',
              fontSize: '16px',
              fontWeight: '600',
              outline: 'none',
              letterSpacing: '2px'
            }}
          />
        </div>

        {/* Break-even Input */}
        <div style={{ flex: 1, minWidth: '150px' }}>
          <label style={{
            fontSize: '12px',
            color: 'var(--text-secondary)',
            display: 'block',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Your Break-Even Price
          </label>
          <input
            type="number"
            placeholder="e.g. 14.50"
            value={breakeven}
            onChange={(e) => setBreakeven(e.target.value)}
            style={{
              width: '100%',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              padding: '14px 16px',
              color: 'var(--accent-yellow)',
              fontSize: '16px',
              fontWeight: '600',
              outline: 'none',
            }}
          />
        </div>

        {/* Buttons */}
        <div style={{
          display: 'flex',
          gap: '10px',
          alignItems: 'flex-end',
          flexWrap: 'wrap'
        }}>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{
              background: loading
                ? 'var(--border)'
                : 'linear-gradient(135deg, #00ff88, #00cc6a)',
              color: '#000',
              border: 'none',
              borderRadius: '12px',
              padding: '14px 28px',
              fontSize: '15px',
              fontWeight: '700',
              cursor: loading ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            {loading ? '⏳ Analyzing...' : '🔍 Full Analysis'}
          </button>

          <button
            onClick={handleCalculate}
            disabled={loading || !breakeven}
            style={{
              background: loading || !breakeven
                ? 'var(--border)'
                : 'linear-gradient(135deg, #4f9cf9, #2563eb)',
              color: '#fff',
              border: 'none',
              borderRadius: '12px',
              padding: '14px 28px',
              fontSize: '15px',
              fontWeight: '700',
              cursor: loading || !breakeven ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            {loading ? '⏳ Calculating...' : '🎯 Beat My Break-Even'}
          </button>

        </div>
      </div>

      <p style={{
        fontSize: '12px',
        color: 'var(--text-secondary)',
        marginTop: '14px',
        opacity: 0.7
      }}>
        💡 Full Analysis runs all 3 AI models (30-60 sec) ·
        Break-Even filter is instant!
      </p>
    </div>
  );
}

export default StockSearch;