import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import './BudgetChart.css';

const CATEGORY_COLORS = {
  'Accommodation': '#2a78d6',
  'Food & Dining': '#1baf7a',
  'Transportation': '#eda100',
  'Activities & Entertainment': '#4a3aa7',
  'Shopping & Miscellaneous': '#e87ba4',
};

const FALLBACK_COLORS = ['#2a78d6', '#1baf7a', '#eda100', '#4a3aa7', '#e87ba4', '#e34948', '#eb6834'];

export default function BudgetChart({ breakdown = {}, currency = 'USD' }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  const entries = Object.entries(breakdown);
  const total = entries.reduce((sum, [, val]) => sum + (Number(val) || 0), 0);
  const labels = entries.map(([key]) => key);
  const values = entries.map(([, val]) => Number(val) || 0);
  const colors = labels.map((label, i) => CATEGORY_COLORS[label] || FALLBACK_COLORS[i % FALLBACK_COLORS.length]);

  useEffect(() => {
    if (!canvasRef.current || entries.length === 0) return;

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    chartRef.current = new Chart(canvasRef.current, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderColor: 'transparent',
          borderWidth: 0,
          spacing: 2,
          hoverOffset: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(17, 24, 39, 0.95)',
            titleColor: '#f1f5f9',
            bodyColor: '#94a3b8',
            borderColor: 'rgba(255,255,255,0.08)',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 8,
            displayColors: false,
          },
        },
      },
    });

    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, [breakdown]);

  if (entries.length === 0) return null;

  return (
    <div className="budget-chart glass-card">
      <p className="budget-chart-title">Budget breakdown</p>

      <div className="budget-chart-body">
        <div className="budget-chart-donut">
          <canvas ref={canvasRef} role="img" aria-label={`Donut chart of budget breakdown across ${labels.length} categories, total ${currency} ${total.toFixed(0)}`}></canvas>
          <div className="budget-chart-center">
            <span className="budget-chart-center-label">Total</span>
            <span className="budget-chart-center-value">{currency} {total.toFixed(0)}</span>
          </div>
        </div>

        <div className="budget-chart-legend">
          {entries.map(([label, value], i) => {
            const pct = total > 0 ? Math.round((value / total) * 100) : 0;
            return (
              <div className="budget-chart-legend-row" key={label}>
                <span className="budget-chart-legend-label">
                  <span className="budget-chart-swatch" style={{ background: colors[i] }}></span>
                  {label}
                </span>
                <span className="budget-chart-legend-value">
                  {currency} {Number(value).toFixed(0)} &middot; {pct}%
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}