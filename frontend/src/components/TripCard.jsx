import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapPin, Calendar, DollarSign, Users, Trash2, Eye } from 'lucide-react';
import { useDestinationPhoto } from '../utils/destinationImage';
import './TripCard.css';

export default function TripCard({ trip, onDelete }) {
  const navigate = useNavigate();
  const { photo, fallbackGradient } = useDestinationPhoto(trip.destination);

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getDuration = () => {
    const start = new Date(trip.start_date);
    const end = new Date(trip.end_date);
    const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    return `${days} day${days !== 1 ? 's' : ''}`;
  };

  return (
    <motion.div
      className="trip-card glass-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3 }}
      layout
    >
      <div
        className="trip-card-photo"
        style={{
          backgroundImage: photo?.thumb_url
            ? `url(${photo.thumb_url})`
            : fallbackGradient,
        }}
      >
        <div className="trip-card-photo-scrim"></div>
        <span className="badge badge-teal trip-card-duration">{getDuration()}</span>
      </div>
      {photo?.photographer && (
        <a
          href={`${photo.photographer_url}?utm_source=travelai&utm_medium=referral`}
          target="_blank"
          rel="noopener noreferrer"
          className="trip-card-photo-credit"
          onClick={(e) => e.stopPropagation()}
        >
          Photo by {photo.photographer} on Unsplash
        </a>
      )}

      <div className="trip-card-header">
        <div className="trip-destination">
          <MapPin size={18} className="trip-icon" />
          <h3>{trip.destination}</h3>
        </div>
      </div>

      <div className="trip-card-details">
        <div className="trip-detail">
          <Calendar size={14} />
          <span>{formatDate(trip.start_date)} — {formatDate(trip.end_date)}</span>
        </div>
        <div className="trip-detail">
          <DollarSign size={14} />
          <span>{trip.currency} {trip.budget.toLocaleString()}</span>
        </div>
        <div className="trip-detail">
          <Users size={14} />
          <span>{trip.travelers} traveler{trip.travelers !== 1 ? 's' : ''}</span>
        </div>
      </div>

      {trip.preferences?.length > 0 && (
        <div className="trip-tags">
          {trip.preferences.slice(0, 3).map((pref, i) => (
            <span key={i} className="badge badge-violet">{pref}</span>
          ))}
          {trip.preferences.length > 3 && (
            <span className="badge badge-coral">+{trip.preferences.length - 3}</span>
          )}
        </div>
      )}

      <div className="trip-card-actions">
        <button
          className="btn btn-primary btn-sm"
          onClick={() => navigate(`/trip/${trip.id}`)}
          id={`view-trip-${trip.id}`}
        >
          <Eye size={14} /> View Itinerary
        </button>
        <button
          className="btn btn-danger btn-sm"
          onClick={() => onDelete(trip.id)}
          id={`delete-trip-${trip.id}`}
        >
          <Trash2 size={14} />
        </button>
      </div>
    </motion.div>
  );
}
