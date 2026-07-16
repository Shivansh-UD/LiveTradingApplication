import React from 'react';

// signal color helper
// green = good, red = bad, yellow = caution
function getSignalColor(signal) {
  if (!signal) return 'var(--text-secondary)';
  const s = signal.toUpperCase();
  if (s.includes('HIGH') || s.includes('POSITIVE') || s.includes('GREEN'))
    return 'var(--accent-green)';
  if (s.includes('LOW') || s.includes('NEGATIVE') || s.includes('DO NOT'))
    return 'var(--accent-red)';
  return 'var(--accent-yellow)';
}

function SignalCard({ title, signal, detail, emoji }) {
  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border)',
      borderRadius: '16px',
      padding: '20px',
      flex: 1,
      minWidth: '200px'
    }}>
      <div style={{
        fontSize: '12px',
        color: 'var(--text-secondary)',
        textTransform: 'uppercase',
        letterSpacing: '1px',
        marginBottom: '12px'
      }}>
        {emoji} {title}
      </div>

      <div style={{
        fontSize: '22px',
        fontWeight: '700',
        color: getSignalColor(signal),
        marginBottom: '8px'
      }}>
        {signal || 'N/A'}
      </div>

      {detail && (
        <div style={{
          fontSize: '12px',
          color: 'var(--text-secondary)',
          lineHeight: '1.5'
        }}>
          {detail}
        </div>
      )}
    </div>
  );
}

function MLSignals({ signals }) {
  if (!signals) return null;

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: '20px',
      padding: '24px',
    }}>
      <h2 style={{
        fontSize: '13px',
        fontWeight: '600',
        color: 'var(--text-secondary)',
        marginBottom: '16px',
        textTransform: 'uppercase',
        letterSpacing: '1px'
      }}>
        🤖 AI Model Signals
      </h2>

      <div style={{
        display: 'flex',
        gap: '12px',
        flexWrap: 'wrap'
      }}>

        {/* Model 1 — IV Predictor */}
        <SignalCard
          emoji="📈"
          title="IV Forecast"
          signal={signals.iv_signal}
          detail={`Predicted IV: ${signals.iv_predicted_pct}%`}
        />

        {/* Model 1 — CSP Signal */}
        <SignalCard
          emoji="📉"
          title="CSP Signal"
          signal={signals.iv_signal}
          detail={signals.csp_signal}
        />

        {/* Model 1 — CC Signal */}
        <SignalCard
          emoji="📞"
          title="CC Signal"
          signal={signals.iv_signal}
          detail={signals.cc_signal}
        />

        {/* Model 2 — Strike Selector */}
        <SignalCard
          emoji="🎯"
          title="Strike Zone"
          signal={signals.strike_zone}
          detail={`Suggested: $${signals.suggested_strike} · Confidence: ${signals.strike_confidence}%`}
        />

      </div>
    </div>
  );
}

export default MLSignals;