import { motion } from 'framer-motion';
import { Clock, MapPin } from 'lucide-react';
import './ItineraryTimeline.css';

const CURRENCY_SYMBOLS = {
  USD: '$',
  EUR: '€',
  GBP: '£',
  JPY: '¥',
  AUD: '$',
  INR: '₹',
};

function getCurrencySymbol(currency) {
  return CURRENCY_SYMBOLS[currency] || '$';
}

// Sums activity costs for a day. The AI sometimes returns 0 or omits the
// day-level estimated_cost even when individual activities have real
// costs (this happens more often for days generated later in a batch),
// so we always compute the true total from activities and only fall back
// to the AI's day-level figure if there are no activities to sum.
function getDayTotal(day) {
  const activities = day.activities || [];
  if (activities.length === 0) {
    return day.estimated_cost || 0;
  }
  return activities.reduce((sum, act) => sum + (Number(act.estimated_cost) || 0), 0);
}

export default function ItineraryTimeline({ days, currency = 'USD' }) {
  if (!days || days.length === 0) return null;

  const symbol = getCurrencySymbol(currency);

  return (
    <div className="timeline">
      {days
        .sort((a, b) => a.day_number - b.day_number)
        .map((day, dayIndex) => (
          <motion.div
            key={day.day_number}
            className="timeline-day"
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: dayIndex * 0.1, duration: 0.4 }}
          >
            <div className="timeline-day-header">
              <div className="timeline-day-badge">Day {day.day_number}</div>
              <h3 className="timeline-day-title">{day.title}</h3>
              <span className="timeline-day-cost">
                {symbol}
                {getDayTotal(day).toFixed(2)}
              </span>
            </div>

            <div className="timeline-activities">
              {(day.activities || []).map((activity, actIndex) => (
                <motion.div
                  key={actIndex}
                  className="timeline-activity glass-card"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: dayIndex * 0.1 + actIndex * 0.05 }}
                >
                  <div className="activity-time">
                    <Clock size={12} />
                    <span>{activity.time}</span>
                  </div>
                  <div className="activity-content">
                    <h4>{activity.activity}</h4>
                    <p>{activity.description}</p>
                    <div className="activity-meta">
                      {activity.location && (
                        <span className="activity-location">
                          <MapPin size={12} />
                          {activity.location}
                        </span>
                      )}
                      <span className="activity-cost">
                        {symbol}
                        {(Number(activity.estimated_cost) || 0).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        ))}
    </div>
  );
}