import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Compass, FileText, CheckSquare, Layers, ShieldCheck, RotateCcw } from 'lucide-react';
import { useJourney } from '../../context/JourneyContext';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { resetDemo } = useJourney();

  const navLinks = [
    { name: 'Home', path: '/', icon: Compass },
    { name: 'My Journey', path: '/journey', icon: Layers },
    { name: 'Services', path: '/services', icon: CheckSquare },
    { name: 'Documents', path: '/documents', icon: FileText },
    { name: 'Applications', path: '/applications', icon: ShieldCheck },
  ];

  const handleReset = async () => {
    if (window.confirm('Reset demo state back to default initial conditions?')) {
      await resetDemo();
      navigate('/');
    }
  };

  return (
    <header className="bg-slate-900 text-slate-100 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Refined Brand Identity */}
          <Link to="/" className="flex items-center space-x-2.5 group focus:outline-none">
            {/* Minimal Path / Transition Brand Mark */}
            <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700/80 flex items-center justify-center shrink-0 group-hover:border-slate-600 transition-colors">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-blue-400"
              >
                <circle cx="6" cy="18" r="2.5" fill="#60a5fa" />
                <circle cx="18" cy="6" r="2.5" fill="#3b82f6" />
                <path
                  d="M6 15.5V11C6 8.23858 8.23858 6 11 6H15.5"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
                <path
                  d="M13.5 3.5L16.5 6L13.5 8.5"
                  stroke="#60a5fa"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>

            {/* Typography */}
            <div className="flex flex-col">
              <span className="text-base sm:text-lg font-bold tracking-tight text-white leading-tight group-hover:text-slate-100 transition-colors">
                LifeEvent
              </span>
              <span className="text-[10px] sm:text-[11px] text-slate-400 font-normal leading-none tracking-normal">
                Citizen Service Navigator
              </span>
            </div>
          </Link>

          {/* Navigation Links & Reset Action */}
          <div className="flex items-center space-x-1 sm:space-x-2">
            <nav className="flex items-center space-x-1" aria-label="Main Navigation">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = location.pathname === link.path;
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-slate-800 text-white font-semibold border border-slate-700'
                        : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                    }`}
                  >
                    <Icon className="w-4 h-4 shrink-0 text-slate-400" />
                    <span>{link.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Reset Demo Action */}
            <button
              type="button"
              onClick={handleReset}
              title="Reset demo state to initial defaults"
              className="ml-2 flex items-center space-x-1.5 px-2.5 py-1.5 text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-700/80 rounded-md transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden md:inline font-medium">Reset Demo</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
