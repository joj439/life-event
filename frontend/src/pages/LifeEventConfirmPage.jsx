import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowRight, Edit3, Home, ShieldAlert, Heart, Activity } from 'lucide-react';
import { useJourney } from '../context/JourneyContext';

export default function LifeEventConfirmPage() {
  const { lifeEvent } = useJourney();
  const navigate = useNavigate();

  if (!lifeEvent) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <p className="text-slate-600 mb-4">No active life event detected. Please start from the homepage.</p>
        <Link to="/" className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-700 text-white rounded-lg text-sm font-medium">
          <Home className="w-4 h-4" />
          <span>Return to Home</span>
        </Link>
      </div>
    );
  }

  const eventType = lifeEvent.event_type || 'relocation';
  const origin = lifeEvent.origin || 'Mumbai';
  const destination = lifeEvent.destination || 'Pune';

  const getEventBadge = () => {
    switch (eventType) {
      case 'financial_fraud':
        return {
          title: 'Financial Cyber Fraud',
          icon: ShieldAlert,
          color: 'bg-rose-50 text-rose-800 border-rose-200',
          subtitle: 'Unauthorized payment or financial scam intimation',
        };
      case 'marriage':
        return {
          title: 'Marriage & Civil Status Change',
          icon: Heart,
          color: 'bg-indigo-50 text-indigo-800 border-indigo-200',
          subtitle: 'Marriage registration and demographic record updates',
        };
      case 'family_death':
        return {
          title: 'Family Demise & Vital Records',
          icon: Activity,
          color: 'bg-slate-100 text-slate-800 border-slate-300',
          subtitle: "We're sorry for your loss. We'll guide you through the essential civil records.",
        };
      default:
        return {
          title: 'Relocation',
          icon: ArrowRight,
          color: 'bg-blue-50 text-blue-800 border-blue-200',
          subtitle: 'Inter-city or municipal residential transition',
        };
    }
  };

  const badge = getEventBadge();

  return (
    <div className="min-h-[75vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8">
        
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-2">
          Step 1: Event Identification
        </span>

        <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mb-2">
          Here's what we understood
        </h2>
        
        <p className="text-xs sm:text-sm text-slate-600 mb-6">
          {eventType === 'family_death'
            ? "We're sorry for your loss. We detected the following situation from your description:"
            : "We detected your situation from your description:"}
        </p>

        {/* Structured Extraction Card */}
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-5 mb-6">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-200">
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase block">Event Category</span>
              <span className="text-base font-bold text-slate-900">{badge.title}</span>
            </div>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${badge.color}`}>
              Detected
            </span>
          </div>

          {eventType === 'relocation' ? (
            <div className="flex items-center justify-between bg-white rounded-md p-3.5 border border-slate-200">
              <div>
                <span className="text-[10px] uppercase font-semibold text-slate-400 block">From</span>
                <span className="font-bold text-slate-900 text-sm sm:text-base">{origin}</span>
              </div>

              <div className="flex items-center space-x-1 px-3 text-slate-400">
                <span className="text-xs text-blue-700 font-medium">to</span>
                <ArrowRight className="w-4 h-4 text-blue-700" />
              </div>

              <div className="text-right">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block">To</span>
                <span className="font-bold text-blue-700 text-sm sm:text-base">{destination}</span>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-md p-3.5 border border-slate-200 text-xs sm:text-sm text-slate-700">
              {badge.subtitle}
            </div>
          )}

          <div className="mt-3 text-xs text-slate-500">
            <span>&ldquo;{lifeEvent.raw_input}&rdquo;</span>
          </div>
        </div>

        {/* Prompt */}
        <p className="text-sm font-semibold text-slate-800 mb-4 text-center">
          Is this correct?
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="w-full sm:w-1/2 flex items-center justify-center space-x-1.5 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold rounded-lg transition-colors cursor-pointer"
          >
            <Edit3 className="w-4 h-4" />
            <span>Edit</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/context')}
            className="w-full sm:w-1/2 flex items-center justify-center space-x-1.5 px-4 py-2.5 bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold rounded-lg transition-colors shadow-sm cursor-pointer"
          >
            <span>Yes, continue</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
}
