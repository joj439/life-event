import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertCircle, Loader2, Compass, CheckCircle2, ShieldCheck } from 'lucide-react';
import { useJourney } from '../context/JourneyContext';

export default function HomePage() {
  const [inputText, setInputText] = useState('');
  const [localError, setLocalError] = useState(null);
  const { analyzeLifeEvent, isLoading } = useJourney();
  const navigate = useNavigate();

  const sampleChips = [
    "I moved from Mumbai to Pune.",
    "Someone made an unauthorized UPI transaction.",
    "I recently got married.",
    "My father passed away."
  ];

  const handleSubmit = async (e) => {
    e?.preventDefault();
    setLocalError(null);

    const trimmed = inputText.trim();
    if (!trimmed) {
      setLocalError("Please tell us what happened (e.g., 'I moved from Mumbai to Pune.').");
      return;
    }

    try {
      const event = await analyzeLifeEvent(trimmed);
      if (event.is_supported) {
        navigate('/confirm');
      } else {
        setLocalError(event.message || "This prototype currently supports relocation, financial fraud, marriage, and family-death scenarios.");
      }
    } catch (err) {
      setLocalError(err.message || "We couldn't analyze that right now. Please try again.");
    }
  };

  const handleChipClick = (chipText) => {
    setInputText(chipText);
    setLocalError(null);
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      
      {/* Hero Section */}
      <section className="bg-slate-900 text-white py-16 sm:py-20 border-b border-slate-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          
          <span className="inline-block text-xs font-semibold tracking-wider text-slate-400 uppercase mb-4">
            Public Service Navigator
          </span>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-white mb-4 leading-tight">
            Government services, <br className="hidden sm:block" />
            organized around your life.
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto mb-8 leading-relaxed">
            Tell us what happened. We'll help you understand what government services you may need next.
          </p>

          {/* Natural Language Input Form */}
          <form onSubmit={handleSubmit} className="max-w-2xl mx-auto mb-6">
            <div className="flex flex-col sm:flex-row items-stretch bg-white rounded-xl p-1.5 shadow-lg border border-slate-300">
              <input
                type="text"
                value={inputText}
                onChange={(e) => {
                  setInputText(e.target.value);
                  if (localError) setLocalError(null);
                }}
                disabled={isLoading}
                placeholder="I moved from Mumbai to Pune."
                aria-label="Describe your life event"
                className="w-full px-4 py-3 text-slate-900 placeholder-slate-400 bg-transparent rounded-lg focus:outline-none text-base disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="mt-2 sm:mt-0 flex items-center justify-center space-x-2 px-6 py-3 bg-blue-700 hover:bg-blue-800 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors shrink-0 cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Understanding...</span>
                  </>
                ) : (
                  <>
                    <span>Find my services</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Loading status */}
          {isLoading && (
            <p className="text-xs text-slate-400 mb-4">
              Analyzing life event and mapping relevant public services...
            </p>
          )}

          {/* Error Notice */}
          {localError && (
            <div className="max-w-2xl mx-auto mb-6 bg-slate-800 border border-amber-500/50 rounded-lg p-3.5 text-left flex items-start space-x-3 text-amber-200">
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div className="text-xs sm:text-sm">
                <p className="font-semibold text-amber-300">Notice</p>
                <p className="mt-0.5 text-slate-300">{localError}</p>
              </div>
            </div>
          )}

          {/* Subtle Example Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            <span className="text-xs text-slate-400 font-medium mr-1">Examples:</span>
            {sampleChips.map((chip, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleChipClick(chip)}
                className="text-xs bg-slate-800 hover:bg-slate-700/80 text-slate-300 border border-slate-700 rounded-md px-3 py-1 transition-colors cursor-pointer"
              >
                {chip}
              </button>
            ))}
          </div>

        </div>
      </section>

      {/* 3 Structured Pillars */}
      <section className="py-14 bg-slate-50 flex-grow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Organized Around Life Events, Not Departments
            </h2>
            <p className="text-slate-600 mt-1.5 text-sm">
              Discover and fulfill government requirements without needing to navigate administrative hierarchies.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-slate-700 mb-4 border border-slate-200/60">
                <Compass className="w-5 h-5 text-blue-700" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1.5">1. Natural Event Intake</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Describe life changes in your own words. The system identifies the relevant event and key parameters.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-slate-700 mb-4 border border-slate-200/60">
                <CheckCircle2 className="w-5 h-5 text-emerald-700" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1.5">2. Deterministic Mapping</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Verified rules match required public services and calculate document readiness without guesswork.
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-slate-700 mb-4 border border-slate-200/60">
                <ShieldCheck className="w-5 h-5 text-indigo-700" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1.5">3. Unified Tracking</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Follow requirements and multi-department applications across one clear, structured roadmap.
              </p>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
