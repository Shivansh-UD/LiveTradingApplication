import React from 'react';

function Header() {
  return (
    <header style={{
      padding: '24px 0 20px',
      borderBottom: '1px solid var(--border)',
      marginBottom: '24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }}>
      {/* Logo + Title */}
      <div>
        <h1 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: 'var(--text-primary)',
          letterSpacing: '-0.5px'
        }}>
          🎡 <span style={{ color: 'var(--accent-green)' }}>Wheel</span>
          Strategy AI
        </h1>
        <p style={{
          fontSize: '13px',
          color: 'var(--text-secondary)',
          marginTop: '4px'
        }}>
          Powered by XGBoost · Random Forest · FinBERT
        </p>
      </div>

      {/* Live indicator */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        background: 'rgba(0, 255, 136, 0.1)',
        border: '1px solid rgba(0, 255, 136, 0.3)',
        padding: '8px 16px',
        borderRadius: '20px'
      }}>
        <div style={{
          width: '8px',
          height: '8px',
          background: 'var(--accent-green)',
          borderRadius: '50%',
          animation: 'pulse 2s infinite'
        }} />
        <span style={{
          fontSize: '13px',
          color: 'var(--accent-green)',
          fontWeight: '600'
        }}>
          LIVE
        </span>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </header>
  );
}

export default Header;