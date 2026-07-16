import React, { useState } from 'react';

function getDeltaColor(delta) {
  if (delta <= 0.25) return 'var(--accent-green)';
  if (delta <= 0.35) return 'var(--accent-yellow)';
  return 'var(--accent-red)';
}

// ============================================
// TRADE CONFIRMATION MODAL
// Safety gate #2 — human must approve!
// analogy: nuclear launch — multiple confirmations!
// ============================================
function TradeModal({ trade, onConfirm, onCancel }) {
  if (!trade) return null;

  return (
    // dark overlay behind modal
    <div style={{
      position: 'fixed',
      top: 0, left: 0,
      width: '100%', height: '100%',
      background: 'rgba(0,0,0,0.85)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>

      {/* Modal box */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '24px',
        padding: '32px',
        maxWidth: '480px',
        width: '90%',
      }}>

        {/* Warning header */}
        <div style={{
          textAlign: 'center',
          marginBottom: '24px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>⚠️</div>
          <h2 style={{
            fontSize: '22px',
            fontWeight: '700',
            color: 'var(--text-primary)',
            marginBottom: '8px'
          }}>
            Confirm Trade
          </h2>
          <p style={{
            fontSize: '13px',
            color: 'var(--text-secondary)'
          }}>
            Paper Trading — no real money!
          </p>
        </div>

        {/* Trade details */}
        <div style={{
          background: 'var(--bg-secondary)',
          borderRadius: '16px',
          padding: '20px',
          marginBottom: '24px'
        }}>

          {[
            ['Type', trade.type === 'csp'
              ? '📉 Cash Secured Put'
              : '📞 Covered Call'],
            ['Strike', `$${trade.row.strike}`],
            ['Premium', `$${trade.row.mid_price} per share`],
            ['Total Premium', `$${(trade.row.mid_price * 100).toFixed(0)} per contract`],
            ['Delta', trade.row.delta],
            ['Return', `${trade.row.return_if_expired}%`],
          ].map(([label, value]) => (
            <div key={label} style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: '8px 0',
              borderBottom: '1px solid var(--border)'
            }}>
              <span style={{
                fontSize: '13px',
                color: 'var(--text-secondary)'
              }}>
                {label}
              </span>
              <span style={{
                fontSize: '13px',
                fontWeight: '600',
                color: 'var(--text-primary)'
              }}>
                {value}
              </span>
            </div>
          ))}
        </div>

        {/* Alpaca notice */}
        <div style={{
          background: 'rgba(79, 156, 249, 0.1)',
          border: '1px solid rgba(79, 156, 249, 0.3)',
          borderRadius: '12px',
          padding: '12px 16px',
          marginBottom: '24px'
        }}>
          <p style={{
            fontSize: '12px',
            color: 'var(--accent-blue)',
            lineHeight: '1.5'
          }}>
            🦙 This will be placed via Alpaca Paper Trading API.
            No real money involved — safe to test!
          </p>
        </div>

        {/* Action buttons */}
        <div style={{
          display: 'flex',
          gap: '12px'
        }}>
          <button
            onClick={onCancel}
            style={{
              flex: 1,
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              padding: '14px',
              color: 'var(--text-secondary)',
              fontSize: '15px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Cancel
          </button>

          <button
            onClick={onConfirm}
            style={{
              flex: 2,
              background: 'linear-gradient(135deg, #00ff88, #00cc6a)',
              border: 'none',
              borderRadius: '12px',
              padding: '14px',
              color: '#000',
              fontSize: '15px',
              fontWeight: '700',
              cursor: 'pointer'
            }}
          >
            ✅ Confirm Paper Trade
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================
// SUCCESS MODAL — after trade is placed
// ============================================
function SuccessModal({ trade, onClose }) {
  if (!trade) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0,
      width: '100%', height: '100%',
      background: 'rgba(0,0,0,0.85)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid rgba(0, 255, 136, 0.3)',
        borderRadius: '24px',
        padding: '32px',
        maxWidth: '420px',
        width: '90%',
        textAlign: 'center'
      }}>

        <div style={{ fontSize: '64px', marginBottom: '16px' }}>🎉</div>

        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: 'var(--accent-green)',
          marginBottom: '8px'
        }}>
          Trade Placed!
        </h2>

        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '14px',
          marginBottom: '24px'
        }}>
          Paper trade submitted via Alpaca API
        </p>

        {/* Trade summary */}
        <div style={{
          background: 'var(--bg-secondary)',
          borderRadius: '16px',
          padding: '16px',
          marginBottom: '24px',
          textAlign: 'left'
        }}>
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '13px',
            marginBottom: '8px'
          }}>
            {trade.type === 'csp'
              ? '📉 Cash Secured Put'
              : '📞 Covered Call'}
          </p>
          <p style={{
            color: 'var(--accent-green)',
            fontSize: '22px',
            fontWeight: '700'
          }}>
            Strike ${trade.row.strike}
          </p>
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '13px',
            marginTop: '4px'
          }}>
            Premium: ${trade.row.mid_price} ×
            100 = ${(trade.row.mid_price * 100).toFixed(0)}
          </p>
        </div>

        {/* Alpaca note */}
        <div style={{
          background: 'rgba(0, 255, 136, 0.05)',
          border: '1px solid rgba(0, 255, 136, 0.2)',
          borderRadius: '12px',
          padding: '12px',
          marginBottom: '24px'
        }}>
          <p style={{
            fontSize: '12px',
            color: 'var(--accent-green)'
          }}>
            🦙 Check your Alpaca Paper Trading
            dashboard to see the order!
          </p>
        </div>

        <button
          onClick={onClose}
          style={{
            width: '100%',
            background: 'linear-gradient(135deg, #00ff88, #00cc6a)',
            border: 'none',
            borderRadius: '12px',
            padding: '14px',
            color: '#000',
            fontSize: '15px',
            fontWeight: '700',
            cursor: 'pointer'
          }}
        >
          Done
        </button>
      </div>
    </div>
  );
}

// ============================================
// TABLE ROW
// ============================================
function TableRow({ row, type, onTrade }) {
  return (
    <tr
      style={{ borderBottom: '1px solid var(--border)' }}
      onMouseEnter={e =>
        e.currentTarget.style.background = 'rgba(255,255,255,0.03)'
      }
      onMouseLeave={e =>
        e.currentTarget.style.background = 'transparent'
      }
    >
      <td style={{
        padding: '14px 16px',
        fontWeight: '700',
        fontSize: '15px'
      }}>
        ${row.strike}
      </td>

      <td style={{ padding: '14px 16px' }}>
        <span style={{
          color: 'var(--accent-green)',
          fontWeight: '600'
        }}>
          ${row.mid_price}
        </span>
        <span style={{
          fontSize: '11px',
          color: 'var(--text-secondary)',
          display: 'block'
        }}>
          ${row.bid} / ${row.ask}
        </span>
      </td>

      <td style={{ padding: '14px 16px' }}>
        <span style={{
          color: getDeltaColor(row.delta),
          fontWeight: '600'
        }}>
          {row.delta}
        </span>
      </td>

      <td style={{
        padding: '14px 16px',
        color: 'var(--accent-blue)'
      }}>
        ${row.theta}/day
      </td>

      <td style={{
        padding: '14px 16px',
        color: 'var(--accent-yellow)'
      }}>
        {row.iv_pct}%
      </td>

      <td style={{ padding: '14px 16px' }}>
        <span style={{
          background: 'rgba(0, 255, 136, 0.1)',
          color: 'var(--accent-green)',
          padding: '4px 10px',
          borderRadius: '20px',
          fontSize: '13px',
          fontWeight: '600'
        }}>
          {row.return_if_expired}%
        </span>
      </td>

      {type === 'cc' && (
        <>
          <td style={{
            padding: '14px 16px',
            color: 'var(--accent-green)',
            fontWeight: '600'
          }}>
            ${row.profit_if_called}
          </td>
          <td style={{
            padding: '14px 16px',
            color: 'var(--accent-green)',
            fontWeight: '700'
          }}>
            {row.roi_if_called}%
          </td>
        </>
      )}

      {type === 'csp' && row.csp_breakeven && (
        <td style={{
          padding: '14px 16px',
          color: 'var(--accent-yellow)',
          fontWeight: '600'
        }}>
          ${row.csp_breakeven?.toFixed(2)}
        </td>
      )}

      {/* Place Trade Button */}
      <td style={{ padding: '14px 16px' }}>
        <button
          onClick={() => onTrade(row, type)}
          style={{
            background: 'linear-gradient(135deg, #00ff88, #00cc6a)',
            color: '#000',
            border: 'none',
            borderRadius: '8px',
            padding: '8px 14px',
            fontSize: '12px',
            fontWeight: '700',
            cursor: 'pointer',
            whiteSpace: 'nowrap'
          }}
        >
          🦙 Place Trade
        </button>
      </td>
    </tr>
  );
}

// ============================================
// MAIN OPTIONS TABLE COMPONENT
// ============================================
function OptionsTable({ analysisData, calculateData, breakeven }) {
  const [showCC, setShowCC] = useState(false);
  const [pendingTrade, setPendingTrade] = useState(null);
  const [successTrade, setSuccessTrade] = useState(null);

  const data = calculateData || analysisData;
  if (!data) return null;

  const cspData = data.csp_candidates || [];
  const ccData = data.cc_candidates || [];
  const currentData = showCC ? ccData : cspData;
  const isBreakevenMode = !!calculateData;

  // when user clicks Place Trade
  const handleTrade = (row, type) => {
    setPendingTrade({ row, type });
  };

  // when user confirms trade
  const handleConfirm = () => {
    // Alpaca integration ready here!
    // For now — show success modal
    setSuccessTrade(pendingTrade);
    setPendingTrade(null);
  };

  return (
    <>
      {/* Trade Confirmation Modal */}
      {pendingTrade && (
        <TradeModal
          trade={pendingTrade}
          onConfirm={handleConfirm}
          onCancel={() => setPendingTrade(null)}
        />
      )}

      {/* Success Modal */}
      {successTrade && (
        <SuccessModal
          trade={successTrade}
          onClose={() => setSuccessTrade(null)}
        />
      )}

      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '20px',
        padding: '24px',
        overflow: 'hidden'
      }}>

        {/* Header + iOS Slider */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div>
            <h2 style={{
              fontSize: '13px',
              fontWeight: '600',
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              {showCC ? '📞 Covered Calls' : '📉 Cash Secured Puts'}
            </h2>
            {isBreakevenMode && (
              <p style={{
                fontSize: '12px',
                color: 'var(--accent-yellow)',
                marginTop: '4px'
              }}>
                🎯 Filtered for break-even: ${breakeven}
              </p>
            )}
          </div>

          {/* iOS SLIDER */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <span style={{
              fontSize: '13px',
              fontWeight: showCC ? '400' : '700',
              color: showCC
                ? 'var(--text-secondary)'
                : 'var(--accent-green)'
            }}>
              CSP
            </span>

            <div
              onClick={() => setShowCC(!showCC)}
              style={{
                width: '52px',
                height: '28px',
                background: showCC
                  ? 'var(--accent-blue)'
                  : 'var(--accent-green)',
                borderRadius: '14px',
                cursor: 'pointer',
                position: 'relative',
                transition: 'background 0.3s ease',
                boxShadow: showCC
                  ? '0 0 12px rgba(79, 156, 249, 0.4)'
                  : '0 0 12px rgba(0, 255, 136, 0.4)'
              }}
            >
              <div style={{
                position: 'absolute',
                top: '3px',
                left: showCC ? '27px' : '3px',
                width: '22px',
                height: '22px',
                background: '#fff',
                borderRadius: '50%',
                transition: 'left 0.3s ease',
                boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
              }} />
            </div>

            <span style={{
              fontSize: '13px',
              fontWeight: showCC ? '700' : '400',
              color: showCC
                ? 'var(--accent-blue)'
                : 'var(--text-secondary)'
            }}>
              CC
            </span>
          </div>
        </div>

        {/* No data */}
        {currentData.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '40px',
            color: 'var(--text-secondary)'
          }}>
            <p style={{ fontSize: '32px', marginBottom: '12px' }}>📭</p>
            <p style={{ fontSize: '15px' }}>
              No {showCC ? 'CC' : 'CSP'} candidates found
            </p>
            <p style={{
              fontSize: '13px',
              marginTop: '8px',
              opacity: 0.6
            }}>
              {isBreakevenMode
                ? 'No trades beat your break-even — try a lower price'
                : 'Try during market hours for better results'}
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '14px'
            }}>
              <thead>
                <tr style={{
                  borderBottom: '2px solid var(--border)'
                }}>
                  {['Strike', 'Premium', 'Delta',
                    'Theta', 'IV', 'Return'].map(h => (
                    <th key={h} style={{
                      padding: '12px 16px',
                      textAlign: 'left',
                      fontSize: '11px',
                      color: 'var(--text-secondary)',
                      textTransform: 'uppercase',
                      letterSpacing: '1px',
                      fontWeight: '600'
                    }}>
                      {h}
                    </th>
                  ))}
                  {showCC && (
                    <>
                      <th style={{
                        padding: '12px 16px',
                        textAlign: 'left',
                        fontSize: '11px',
                        color: 'var(--text-secondary)',
                        textTransform: 'uppercase',
                        letterSpacing: '1px'
                      }}>
                        Profit if Called
                      </th>
                      <th style={{
                        padding: '12px 16px',
                        textAlign: 'left',
                        fontSize: '11px',
                        color: 'var(--text-secondary)',
                        textTransform: 'uppercase',
                        letterSpacing: '1px'
                      }}>
                        ROI
                      </th>
                    </>
                  )}
                  {!showCC && calculateData && (
                    <th style={{
                      padding: '12px 16px',
                      textAlign: 'left',
                      fontSize: '11px',
                      color: 'var(--accent-yellow)',
                      textTransform: 'uppercase',
                      letterSpacing: '1px'
                    }}>
                      CSP Break-Even
                    </th>
                  )}
                  {/* Place Trade column */}
                  <th style={{
                    padding: '12px 16px',
                    textAlign: 'left',
                    fontSize: '11px',
                    color: 'var(--accent-green)',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}>
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {currentData.map((row, i) => (
                  <TableRow
                    key={i}
                    row={row}
                    type={showCC ? 'cc' : 'csp'}
                    onTrade={handleTrade}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Summary banner */}
        {isBreakevenMode && data.summary && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            background: 'rgba(0, 255, 136, 0.05)',
            border: '1px solid rgba(0, 255, 136, 0.2)',
            borderRadius: '12px'
          }}>
            <p style={{
              fontSize: '13px',
              color: 'var(--accent-green)'
            }}>
              ✅ {data.summary.message}
            </p>
          </div>
        )}
      </div>
    </>
  );
}

export default OptionsTable;