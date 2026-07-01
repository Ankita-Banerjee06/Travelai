import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Compass, AlertCircle } from 'lucide-react';
import { tripAPI } from '../api/client';
import TripCard from '../components/TripCard';
import './Dashboard.css';

export default function Dashboard() {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      const res = await tripAPI.listTrips();
      setTrips(res.data);
    } catch (err) {
      setError('Failed to load your trips. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this trip?')) return;
    try {
      await tripAPI.deleteTrip(id);
      setTrips(trips.filter((trip) => trip.id !== id));
    } catch (err) {
      alert('Failed to delete trip.');
    }
  };

  return (
    <div className="dashboard-page page container">
      <div className="dashboard-header">
        <div>
          <h1>Your Adventures</h1>
          <p className="text-muted">Manage and view your planned trips.</p>
        </div>
        <Link to="/plan" className="btn btn-primary" id="plan-new-trip-btn">
          <Plus size={18} />
          Plan New Trip
        </Link>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {loading ? (
        <div className="dashboard-loading">
          <div className="spinner-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      ) : trips.length > 0 ? (
        <motion.div 
          className="trips-grid"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <AnimatePresence>
            {trips.map((trip) => (
              <TripCard key={trip.id} trip={trip} onDelete={handleDelete} />
            ))}
          </AnimatePresence>
        </motion.div>
      ) : (
        <motion.div 
          className="empty-state glass-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="empty-icon-wrapper">
            <Compass size={48} className="empty-icon" />
          </div>
          <h2>No Trips Yet</h2>
          <p>It looks like you haven't planned any trips yet. Let AI help you create the perfect itinerary!</p>
          <Link to="/plan" className="btn btn-primary mt-lg" id="empty-state-plan-btn">
            Start Planning
          </Link>
        </motion.div>
      )}
    </div>
  );
}
