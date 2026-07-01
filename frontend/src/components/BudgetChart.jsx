import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { motion } from 'framer-motion';
import './BudgetChart.css';

const COLORS = ['#06b6d4', '#8b5cf6', '#f97316', '#10b981', '#f43f5e', '#f59e0b', '#6366f1'];

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div className="budget-tooltip">
        <p className="tooltip-label">{data.name}</p>
        <p className="tooltip-value">${data.value.toLocaleString()}</p>
        {data.payload.notes && (
          <p className="tooltip-notes">{data.payload.notes}</p>
        )}
      </div>
    );
  }
  return null;
};

export default function BudgetChart({ breakdown, currency = 'USD' }) {
  if (!breakdown || breakdown.length === 0) return null;

  const data = breakdown.map((item) => ({
    name: item.category,
    value: item.amount,
    notes: item.notes,
  }));

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <motion.div
      className="budget-chart-container glass-card"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <h3 className="budget-chart-title">Budget Breakdown</h3>

      <div className="budget-chart-wrapper">
        <div className="budget-chart">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={3}
                dataKey="value"
                stroke="none"
              >
                {data.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                    style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="budget-chart-center">
            <span className="budget-total-label">Total</span>
            <span className="budget-total-value">
              {currency} {total.toLocaleString()}
            </span>
          </div>
        </div>

        <div className="budget-legend">
          {data.map((item, index) => (
            <div key={item.name} className="budget-legend-item">
              <div className="legend-color" style={{ background: COLORS[index % COLORS.length] }}></div>
              <div className="legend-info">
                <span className="legend-name">{item.name}</span>
                <span className="legend-value">{currency} {item.value.toLocaleString()}</span>
              </div>
              <span className="legend-percent">{((item.value / total) * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
