import { useState } from 'react';
import './BudgetChart.css';

const CATEGORY_COLORS = {
  'Accommodation': '#2a78d6',
  'Food & Dining': '#1baf7a',
  'Transportation': '#eda100',
  'Activities & Entertainment': '#4a3aa7',
  'Shopping & Miscellaneous': '#e87ba4',
};

const FALLBACK_COLORS = ['#2a78d6', '#1baf7a', '#eda100', '#4a3aa7', '#e87ba4', '#e34948', '#eb6834'];

const SIZE = 160;
const STROKE = 22;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
const GAP_DEG = 2;

export default function BudgetChart({ breakdown = {}, currency = 'USD' }) {
  const [hovered, setHovered] = useState(null);

  const entries = Object.entries(breakdown).filter(([, val]) => Number(val) > 0);
  const total = entries.reduce((sum, [, val]) => sum + (Number(val) || 0), 0);

  if (entries.length === 0 || total === 0) return null;

  const colors = entries.map(([label], i) => CATEGORY_COLORS[label] || FALLBACK_COLORS[i % FALLBACK_COLORS.length]);

  let cumulativeDeg = -90;
  const segments = entries.map(([label, value], i) => {
    const fraction = Number(value) / total;
    const segmentDeg = fraction * 360;
    const startDeg = cumulativeDeg;
    cumulativeDeg += segmentDeg;

    const gapDeg = entries.length > 1 ? GAP_DEG : 0;
    const visibleDeg = Math.max(segmentDeg - gapDeg, 0);
    const dashLength = (visibleDeg / 360) * CIRCUMFERENCE;

    return {
      label,
      value: Number(value),
      pct: Math.round(fraction * 100),
      color: colors[i],
      dashArray: `${dashLength} ${CIRCUMFERENCE - dashLength}`,
      rotation: startDeg,
    };
  });

  return (
    <div className="budget-chart glass-card">
      <p className="budget-chart-title">Budget breakdown</p>

      <div className="budget-chart-body">
        <div className="budget-chart-donut">
          <svg
            viewBox={`0 0 ${SIZE} ${SIZE}`}
            width={SIZE}
            height={SIZE}
            role="img"
            aria-label={`Donut chart of budget breakdown across ${entries.length} categories, total ${currency} ${total.toFixed(0)}`}
          >
            <title>Budget breakdown</title>
            <desc>
              {entries.map(([label, value]) => `${label}: ${currency} ${Number(value).toFixed(0)}`).join(', ')}
            </desc>
            {segments.map((seg) => (
              <circle
                key={seg.label}
                cx={SIZE / 2}
                cy={SIZE / 2}
                r={RADIUS}
                fill="none"
                stroke={seg.color}
                strokeWidth={STROKE}
                strokeDasharray={seg.dashArray}
                strokeLinecap="round"
                transform={`rotate(${seg.rotation} ${SIZE / 2} ${SIZE / 2})`}
                opacity={hovered && hovered !== seg.label ? 0.35 : 1}
                style={{ transition: 'opacity 150ms ease', cursor: 'pointer' }}
                onMouseEnter={() => setHovered(seg.label)}
                onMouseLeave={() => setHovered(null)}
              />
            ))}
          </svg>
          <div className="budget-chart-center">
            <span className="budget-chart-center-label">Total</span>
            <span className="budget-chart-center-value">{currency} {total.toFixed(0)}</span>
          </div>
        </div>

        <div className="budget-chart-legend">
          {segments.map((seg) => (
            <div
              className="budget-chart-legend-row"
              key={seg.label}
              onMouseEnter={() => setHovered(seg.label)}
              onMouseLeave={() => setHovered(null)}
              style={{ opacity: hovered && hovered !== seg.label ? 0.5 : 1, transition: 'opacity 150ms ease' }}
            >
              <span className="budget-chart-legend-label">
                <span className="budget-chart-swatch" style={{ background: seg.color }}></span>
                {seg.label}
              </span>
              <span className="budget-chart-legend-value">
                {currency} {seg.value.toFixed(0)} &middot; {seg.pct}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}