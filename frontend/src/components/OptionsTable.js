import React, { useState } from 'react';

// color code delta values
// green = safe, yellow = moderate, red = aggressive
function getDeltaColor(delta) {
  if (delta <= 0.25) return 'var(--accent-green)';
  if (delta <= 0.35) return 'var(--accent-yellow)';
  return 'var(--accent-red)';
}

// single row in the options table
function TableRow({ row, type }) {
  return (
    <tr style={{
      borderBottom: '1px solid var(--border)',
      transition: 'background 0.2s'
    }}
      onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
    >
      {/* Strike */}
      <td style={{ padding: '14px 16px', fontWeight: '700', fontSize: '15px' }}>
        ${row.strike}
      </td>

      {/* Premium */}
      <td style={{ padding: '14px 16px' }}>
        <span style={{ color: 'var(--accent-green)', fontWeight: '600' }}>
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

      {/* Delta */}
      <td style={{ padding: '14px 16px' }}>
        <span style={{
          color: getDeltaColor(row.delta),
          fontWeight: '600'
        }}>
          {row.delta}
        </span>
      </td>

      {/* Theta */}
      <td style={{ padding: '14px 16px', color: 'var(--accent-blue)' }}>
        ${row.theta}/day
      </td>

      {/* IV */}
      <td style={{ padding: '14px 16px', color: 'var(--accent-yellow)' }}>
        {row.iv_pct}%
      </td>

      {/* Return */}
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

      {/* CC only — profit if called */}
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

      {/* CSP only — break-even */}
      {type === 'csp' && row.csp_breakeven && (
        <td style={{
          padding: '14px 16px',
          color: 'var(--accent-yellow)',
          fontWeight: '600'
        }}>
          ${row.csp_breakeven?.toFixed(2)}
        </td>
      )}
    </tr>
  );
}

function OptionsTable({ analysisData, calculateData, breakeven }) {
  // iOS slider state — false = CSP, true = CC
  const [showCC, setShowCC] = useState(false);

  // use calculateData if available (break-even filter)
  // otherwise use analysisData (full analysis)
  const data = calculateData || analysisData;
  if (!data) return null;

  const cspData = data.csp_candidates || [];
  const ccData = data.cc_candidates || [];
  const currentData = showCC ? ccData : cspData;
  const isBreakevenMode = !!calculateData;

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: '20px',
      padding: '24px',
      overflow: 'hidden'
    }}>

      {/* Header row with slider */}
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

        {/* iOS STYLE SLIDER! */}
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

          {/* Toggle track */}
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
            {/* Toggle thumb — slides left/right */}
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

      {/* No data message */}
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
          <p style={{ fontSize: '13px', marginTop: '8px', opacity: 0.6 }}>
            {isBreakevenMode
              ? 'No trades beat your break-even — try a lower price'
              : 'Try during market hours for better results'}
          </p>
        </div>
      ) : (

        /* Table */
        <div style={{ overflowX: 'auto' }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '14px'
          }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border)' }}>
                {['Strike', 'Premium', 'Delta', 'Theta', 'IV', 'Return'].map(h => (
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
              </tr>
            </thead>
            <tbody>
              {currentData.map((row, i) => (
                <TableRow
                  key={i}
                  row={row}
                  type={showCC ? 'cc' : 'csp'}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary if breakeven mode */}
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
  );
}

export default OptionsTable;