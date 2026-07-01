import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plane, MapPin, Wallet, Sparkles, Globe, Calendar, ArrowRight } from 'lucide-react';
import './Landing.css';

const features = [
  {
    icon: <Sparkles size={28} />,
    title: 'AI-Powered Itineraries',
    description: 'Get personalized day-by-day travel plans tailored to your preferences, budget, and travel style.',
    color: 'teal',
  },
  {
    icon: <Wallet size={28} />,
    title: 'Smart Budget Optimization',
    description: 'Our AI analyzes costs and suggests the best ways to maximize your travel experience within budget.',
    color: 'violet',
  },
  {
    icon: <Globe size={28} />,
    title: 'Any Destination',
    description: 'From bustling cities to hidden gems — plan trips to anywhere in the world with local insights.',
    color: 'coral',
  },
];

const stats = [
  { value: '500+', label: 'Destinations' },
  { value: '10K+', label: 'Trips Planned' },
  { value: '98%', label: 'Happy Travelers' },
];

export default function Landing() {
  return (
    <div className="landing">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-bg">
          <div className="hero-orb hero-orb-1"></div>
          <div className="hero-orb hero-orb-2"></div>
          <div className="hero-orb hero-orb-3"></div>
        </div>

        <div className="container hero-content">
          <motion.div
            className="hero-text"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="hero-badge">
              <Sparkles size={14} />
              <span>AI-Powered Travel Planning</span>
            </div>
            <h1>
              Plan Your Dream Trip
              <br />
              <span className="text-gradient">With Artificial Intelligence</span>
            </h1>
            <p className="hero-subtitle">
              Generate personalized itineraries, optimize your budget, and discover hidden gems — all powered by advanced AI that understands how you love to travel.
            </p>
            <div className="hero-cta">
              <Link to="/register" className="btn btn-primary btn-lg" id="hero-cta">
                Start Planning
                <ArrowRight size={18} />
              </Link>
              <Link to="/login" className="btn btn-secondary btn-lg" id="hero-login">
                Sign In
              </Link>
            </div>
          </motion.div>

          <motion.div
            className="hero-visual"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="hero-card-stack">
              <div className="hero-card hero-card-1 glass-card">
                <div className="hero-card-icon"><MapPin size={20} /></div>
                <div>
                  <h4>Paris, France</h4>
                  <p>5-day cultural exploration</p>
                </div>
              </div>
              <div className="hero-card hero-card-2 glass-card">
                <div className="hero-card-icon hero-card-icon-violet"><Calendar size={20} /></div>
                <div>
                  <h4>Day 1: Eiffel Tower</h4>
                  <p>Morning visit + Seine cruise</p>
                </div>
              </div>
              <div className="hero-card hero-card-3 glass-card">
                <div className="hero-card-icon hero-card-icon-coral"><Wallet size={20} /></div>
                <div>
                  <h4>Budget: $2,500</h4>
                  <p>Optimized for best value</p>
                </div>
              </div>
            </div>
            <div className="hero-plane animate-float">
              <Plane size={40} />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid">
            {stats.map((stat) => (
              <motion.div
                key={stat.label}
                className="stat-item"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4 }}
              >
                <span className="stat-value text-gradient">{stat.value}</span>
                <span className="stat-label">{stat.label}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="container">
          <motion.div
            className="section-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2>Why Choose <span className="text-gradient">TravelAI</span></h2>
            <p>Everything you need to plan the perfect trip, powered by cutting-edge AI</p>
          </motion.div>

          <div className="features-grid">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="feature-card glass-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -6 }}
              >
                <div className={`feature-icon feature-icon-${feature.color}`}>
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="container">
          <motion.div
            className="cta-card glass-card"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <h2>Ready to Start Your Adventure?</h2>
            <p>Create your free account and let AI plan your next unforgettable trip.</p>
            <Link to="/register" className="btn btn-primary btn-lg" id="cta-register">
              Get Started Free
              <ArrowRight size={18} />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <Plane size={20} />
              <span>TravelAI</span>
            </div>
            <p className="footer-copy">© 2025 TravelAI. Powered by Groq AI.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
