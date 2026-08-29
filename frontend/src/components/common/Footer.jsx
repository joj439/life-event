import React from 'react';
import { Shield } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <span className="text-sm font-semibold text-slate-200 block">LifeEvent Navigator</span>
            <p className="text-xs text-slate-400 mt-0.5">
              Citizen-centric government services organized around real-life transitions.
            </p>
          </div>

          <div className="flex items-center space-x-2 text-xs bg-slate-800/80 border border-slate-700/80 rounded-md px-3 py-1.5 text-slate-300">
            <Shield className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>Prototype Demonstration &bull; Fictional citizen demonstration data</span>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <span>&copy; {new Date().getFullYear()} LifeEvent. Public Service Navigator.</span>
          <span>Deterministic service matching architecture</span>
        </div>
      </div>
    </footer>
  );
}
