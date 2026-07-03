import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapPin, Calendar, Users, Wand2, Share, ArrowLeft, Download } from 'lucide-react';
import { tripAPI } from '../api/client';
import ItineraryTimeline from '../components/ItineraryTimeline';
import BudgetChart from '../components/BudgetChart';
import LoadingSpinner from '../components/LoadingSpinner';
import { getDestinationImageUrl } from '../utils/destinationImage';
import './ItineraryView.css';

export default function ItineraryView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState('');
  const [optimizationGoal, setOptimizationGoal] = useState('reduce_costs');
  const [showOptimizeMenu, setShowOptimizeMenu] = useState(false);

  useEffect(() => {
    loadTrip();
  }, [id]);

  const loadTrip = async () => {
    try {
      const res = await tripAPI.getTrip(id);
      setTrip(res.data);
    } catch (err) {
      setError('Failed to load itinerary. It may not exist or you may not have permission.');
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    setOptimizing(true);
    setShowOptimizeMenu(false);
    try {
      const res = await tripAPI.optimizeBudget(id, { optimization_goal: optimizationGoal });
      setTrip(res.data);
    } catch (err) {
      alert('Failed to optimize budget. Please try again.');
    } finally {
      setOptimizing(false);
    }
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) return <LoadingSpinner message="Loading your itinerary..." />;
  
  if (error) {
    return (
      <div className="container mt-xl text-center">
        <div className="alert alert-error">{error}</div>
        <button className="btn btn-secondary mt-md" onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  if (!trip) return null;

  return (
    <>
      {optimizing && <LoadingSpinner message="AI is optimizing your budget..." />}

      {/* Hero Header */}
      <div className="itinerary-header">
        <div
          className="itinerary-header-bg cinematic-bg"
          style={{ backgroundImage: `url(${getDestinationImageUrl(trip.destination)})` }}
        ></div>
        <div className="itinerary-header-scrim"></div>
        <div className="container">
          <button className="btn-icon back-btn" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={20} /> Back
          </button>
          
          <motion.div 
            className="itinerary-title-box"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="badge badge-teal mb-md">AI Generated Itinerary</div>
            <h1>{trip.destination}</h1>
            
            <div className="itinerary-meta-grid">
              <div className="meta-item">
                <Calendar size={18} />
                <div>
                  <span className="meta-label">Dates</span>
                  <span className="meta-value">{formatDate(trip.start_date)} - {formatDate(trip.end_date)}</span>
                </div>
              </div>
              <div className="meta-item">
                <Users size={18} />
                <div>
                  <span className="meta-label">Travelers</span>
                  <span className="meta-value">{trip.travelers} Person(s)</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="container page itinerary-content">
        <div className="itinerary-grid">
          
          {/* Left Column: Itinerary */}
          <div className="itinerary-main">
            <div className="section-header-row">
              <h2>Your Daily Plan</h2>
              <div className="action-buttons">
                <button className="btn btn-secondary btn-sm" onClick={() => window.print()}>
                  <Download size={14} /> Export
                </button>
              </div>
            </div>
            
            <ItineraryTimeline days={trip.itinerary_days} />
          </div>

          {/* Right Column: Budget & Stats */}
          <div className="itinerary-sidebar">
            <div className="sticky-sidebar">
              <BudgetChart breakdown={trip.budget_breakdown} currency={trip.currency} />
              
              <motion.div 
                className="ai-optimize-card glass-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div className="ai-optimize-header">
                  <Wand2 size={24} className="text-gradient" />
                  <h3>AI Budget Optimizer</h3>
                </div>
                <p className="text-muted">Let AI adjust your itinerary to better fit your financial goals.</p>
                
                {showOptimizeMenu ? (
                  <div className="optimize-options mt-md">
                    <select 
                      className="form-input mb-md" 
                      value={optimizationGoal}
                      onChange={(e) => setOptimizationGoal(e.target.value)}
                    >
                      <option value="reduce_costs">Reduce Costs</option>
                      <option value="balance">Balance Budget & Luxury</option>
                      <option value="luxury">Upgrade Experiences (Luxury)</option>
                    </select>
                    <div className="flex gap-sm">
                      <button className="btn btn-primary flex-1" onClick={handleOptimize} id="confirm-optimize-btn">Apply</button>
                      <button className="btn btn-secondary" onClick={() => setShowOptimizeMenu(false)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <button 
                    className="btn btn-secondary w-full mt-md" 
                    onClick={() => setShowOptimizeMenu(true)}
                    id="show-optimize-btn"
                  >
                    Optimize Budget
                  </button>
                )}
              </motion.div>
            </div>
          </div>
          
        </div>
      </div>
    </>
  );
}
