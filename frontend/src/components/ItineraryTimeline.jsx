import { motion } from 'framer-motion';
import { Clock, MapPin, DollarSign } from 'lucide-react';
import './ItineraryTimeline.css';

export default function ItineraryTimeline({ days }) {
  if (!days || days.length === 0) return null;

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
                <DollarSign size={14} />
                {day.estimated_cost?.toFixed(2)}
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
                        <DollarSign size={12} />
                        {activity.estimated_cost?.toFixed(2)}
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
