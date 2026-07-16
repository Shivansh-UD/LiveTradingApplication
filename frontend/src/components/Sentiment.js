import React from 'react';

function Sentiment({ sentiment }) {
  if (!sentiment) return null;

  // color based on signal
  const getColor = (signal) => {
    if (!signal) return 'var(--text-secondary)';
    if (signal === 'POSITIVE') return 'var(--accent-green)';
    if (signal === 'NEGATIVE') return 'var(--accent-red)';
    return 'var(--accent-yellow)';
  };

  // background glow based on signal
  const getBg = (signal) => {
    if (signal === 'POSITIVE') return 'rgba(0, 255, 136, 0.05)';
    if (signal === 'NEGATIVE') return 'rgba(255, 71, 87, 0.05)';
    return 'rgba(255, 211, 42, 0.05)';
  };

  // border based on signal
  const getBorder = (signal) => {
    if (signal === 'POSITIVE') return 'rgba(0, 255, 136, 0.2)';
    if (signal === 'NEGATIVE') return 'rgba(255, 71, 87, 0.2)';
    return 'rgba(255, 211, 42, 0.2)';
  };

  // score bar — -1 to +1 converted to 0-100%
  const scorePercent = ((sentiment.score + 1) / 2) * 100;

  return (
    <div style={{
      background: getBg(sentiment.signal),
      border: `1px solid ${getBorder(sentiment.signal)}`,
      borderRadius: '20px',
      padding: '24px',
    }}>

      {/* Header row */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <h2 style={{
          fontSize: '13px',
          fontWeight: '600',
          color: 'var(--text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}>
          📰 News Sentiment
        </h2>

        {/* Signal badge */}
        <div style={{
          background: getBg(sentiment.signal),
          border: `1px solid ${getBorder(sentiment.signal)}`,
          borderRadius: '20px',
          padding: '6px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{
            fontSize: '18px',
            fontWeight: '700',
            color: getColor(sentiment.signal)
          }}>
            {sentiment.signal === 'POSITIVE' ? '✅' :
             sentiment.signal === 'NEGATIVE' ? '🚫' : '⚠️'}
          </span>
          <span style={{
            fontSize: '14px',
            fontWeight: '700',
            color: getColor(sentiment.signal)
          }}>
            {sentiment.signal}
          </span>
        </div>
      </div>

      {/* Score bar */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '6px'
        }}>
          <span style={{
            fontSize: '12px',
            color: 'var(--text-secondary)'
          }}>
            Sentiment Score
          </span>
          <span style={{
            fontSize: '12px',
            fontWeight: '600',
            color: getColor(sentiment.signal)
          }}>
            {sentiment.score} / 1.0
          </span>
        </div>

        {/* Progress bar background */}
        <div style={{
          background: 'var(--border)',
          borderRadius: '10px',
          height: '8px',
          overflow: 'hidden'
        }}>
          {/* Progress bar fill */}
          <div style={{
            width: `${scorePercent}%`,
            height: '100%',
            background: getColor(sentiment.signal),
            borderRadius: '10px',
            transition: 'width 1s ease'
          }} />
        </div>

        {/* Scale labels */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '4px'
        }}>
          <span style={{ fontSize: '10px', color: 'var(--accent-red)' }}>
            Very Negative
          </span>
          <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
            Neutral
          </span>
          <span style={{ fontSize: '10px', color: 'var(--accent-green)' }}>
            Very Positive
          </span>
        </div>
      </div>

      {/* Recommendation */}
      <div style={{
        background: 'var(--bg-secondary)',
        borderRadius: '12px',
        padding: '14px 16px',
        marginBottom: '16px'
      }}>
        <p style={{
          fontSize: '14px',
          color: 'var(--text-primary)',
          lineHeight: '1.5'
        }}>
          {sentiment.recommendation}
        </p>
      </div>

      {/* Headlines count */}
      <p style={{
        fontSize: '12px',
        color: 'var(--text-secondary)',
        opacity: 0.7
      }}>
        📊 Based on {sentiment.headlines_analyzed} recent news headlines
        analyzed by FinBERT
      </p>

    </div>
  );
}

export default Sentiment;