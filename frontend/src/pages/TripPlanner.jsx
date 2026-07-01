import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Calendar, Users, DollarSign, Sparkles, ArrowRight, ArrowLeft } from 'lucide-react';
import { tripAPI } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import './TripPlanner.css';

const PREFERENCES_OPTIONS = [
  'Culture & History',
  'Food & Culinary',
  'Nature & Outdoors',
  'Relaxation & Spa',
  'Adventure & Sports',
  'Nightlife & Party',
  'Shopping',
  'Art & Museums',
  'Hidden Gems',
];

export default function TripPlanner() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    destination: '',
    start_date: '',
    end_date: '',
    budget: '',
    currency: 'USD',
    travelers: 1,
    preferences: [],
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const togglePreference = (pref) => {
    setFormData((prev) => ({
      ...prev,
      preferences: prev.preferences.includes(pref)
        ? prev.preferences.filter((p) => p !== pref)
        : [...prev.preferences, pref],
    }));
  };

  const nextStep = () => {
    if (step === 1 && (!formData.destination || !formData.start_date || !formData.end_date)) {
      setError('Please fill in all destination and date fields.');
      return;
    }
    
    if (step === 2 && !formData.budget) {
      setError('Please provide a budget estimate.');
      return;
    }

    if (step === 1 && new Date(formData.start_date) > new Date(formData.end_date)) {
      setError('End date must be after start date.');
      return;
    }

    setError('');
    setStep((prev) => prev + 1);
  };

  const prevStep = () => {
    setError('');
    setStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await tripAPI.planTrip({
        ...formData,
        budget: parseFloat(formData.budget),
        travelers: parseInt(formData.travelers, 10),
      });
      navigate(`/trip/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate itinerary. Please try again.');
      setLoading(false);
    }
  };

  // Step renderers
  const renderStep1 = () => (
    <motion.div
      key="step1"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="form-step"
    >
      <div className="step-header">
        <h2>Where to?</h2>
        <p>Let's start with the basics of your trip.</p>
      </div>

      <div className="form-group">
        <label>Destination (City, Country)</label>
        <div className="input-icon-wrapper">
          <MapPin size={18} className="input-icon" />
          <input
            type="text"
            name="destination"
            className="form-input input-with-icon"
            placeholder="e.g. Tokyo, Japan"
            value={formData.destination}
            onChange={handleInputChange}
          />
        </div>
      </div>

      <div className="grid-2 gap-md mt-md">
        <div className="form-group">
          <label>Start Date</label>
          <div className="input-icon-wrapper">
            <Calendar size={18} className="input-icon" />
            <input
              type="date"
              name="start_date"
              className="form-input input-with-icon"
              value={formData.start_date}
              onChange={handleInputChange}
            />
          </div>
        </div>
        <div className="form-group">
          <label>End Date</label>
          <div className="input-icon-wrapper">
            <Calendar size={18} className="input-icon" />
            <input
              type="date"
              name="end_date"
              className="form-input input-with-icon"
              value={formData.end_date}
              onChange={handleInputChange}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );

  const renderStep2 = () => (
    <motion.div
      key="step2"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="form-step"
    >
      <div className="step-header">
        <h2>Budget & Travelers</h2>
        <p>Help us tailor the options to your party size and budget.</p>
      </div>

      <div className="grid-2 gap-md">
        <div className="form-group">
          <label>Total Budget</label>
          <div className="input-icon-wrapper">
            <DollarSign size={18} className="input-icon" />
            <input
              type="number"
              name="budget"
              className="form-input input-with-icon"
              placeholder="e.g. 2500"
              min="0"
              step="100"
              value={formData.budget}
              onChange={handleInputChange}
            />
          </div>
        </div>
        <div className="form-group">
          <label>Currency</label>
          <select
            name="currency"
            className="form-input"
            value={formData.currency}
            onChange={handleInputChange}
          >
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (€)</option>
            <option value="GBP">GBP (£)</option>
            <option value="JPY">JPY (¥)</option>
            <option value="AUD">AUD ($)</option>
          </select>
        </div>
      </div>

      <div className="form-group mt-md">
        <label>Number of Travelers</label>
        <div className="input-icon-wrapper">
          <Users size={18} className="input-icon" />
          <input
            type="number"
            name="travelers"
            className="form-input input-with-icon"
            min="1"
            max="20"
            value={formData.travelers}
            onChange={handleInputChange}
          />
        </div>
      </div>
    </motion.div>
  );

  const renderStep3 = () => (
    <motion.div
      key="step3"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="form-step"
    >
      <div className="step-header">
        <h2>Travel Style</h2>
        <p>What kind of experiences are you looking for?</p>
      </div>

      <div className="preferences-grid">
        {PREFERENCES_OPTIONS.map((pref) => (
          <button
            key={pref}
            className={`pref-btn ${formData.preferences.includes(pref) ? 'selected' : ''}`}
            onClick={() => togglePreference(pref)}
            type="button"
          >
            {pref}
          </button>
        ))}
      </div>
    </motion.div>
  );

  return (
    <>
      {loading && <LoadingSpinner message="AI is crafting your perfect itinerary..." />}
      
      <div className="planner-page container container-md">
        <div className="planner-card glass-card">
          {/* Progress Bar */}
          <div className="planner-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${(step / 3) * 100}%` }}
              ></div>
            </div>
            <div className="progress-steps">
              <span className={step >= 1 ? 'active' : ''}>Basics</span>
              <span className={step >= 2 ? 'active' : ''}>Budget</span>
              <span className={step >= 3 ? 'active' : ''}>Style</span>
            </div>
          </div>

          {error && <div className="alert alert-error mb-md">{error}</div>}

          {/* Form Content */}
          <div className="planner-content">
            <AnimatePresence mode="wait">
              {step === 1 && renderStep1()}
              {step === 2 && renderStep2()}
              {step === 3 && renderStep3()}
            </AnimatePresence>
          </div>

          {/* Navigation Buttons */}
          <div className="planner-actions">
            {step > 1 ? (
              <button className="btn btn-secondary" onClick={prevStep} type="button">
                <ArrowLeft size={16} /> Back
              </button>
            ) : (
              <div></div> // Spacer
            )}

            {step < 3 ? (
              <button className="btn btn-primary" onClick={nextStep} type="button" id="next-step-btn">
                Next <ArrowRight size={16} />
              </button>
            ) : (
              <button className="btn btn-primary" onClick={handleSubmit} type="button" id="generate-itinerary-btn">
                <Sparkles size={16} /> Generate Itinerary
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
