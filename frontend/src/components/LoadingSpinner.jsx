import { Plane } from 'lucide-react';
import './LoadingSpinner.css';

export default function LoadingSpinner({ message = 'Planning your perfect trip...' }) {
  return (
    <div className="spinner-overlay">
      <div className="spinner-container">
        <div className="spinner-globe">
          <div className="spinner-ring"></div>
          <div className="spinner-ring spinner-ring-2"></div>
          <div className="spinner-plane">
            <Plane size={24} />
          </div>
        </div>
        <p className="spinner-message">{message}</p>
        <div className="spinner-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  );
}
