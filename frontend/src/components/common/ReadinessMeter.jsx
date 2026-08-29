import React from 'react';
import { CheckCircle2, AlertCircle } from 'lucide-react';

export default function ReadinessMeter({
  availableCount = 0,
  requiredCount = 0,
  percentage = null,
  compact = false,
}) {
  const req = Math.max(requiredCount, 0);
  const avail = Math.min(Math.max(availableCount, 0), req || availableCount);
  const pct = percentage !== null ? percentage : req > 0 ? Math.round((avail / req) * 100) : 100;
  const isComplete = avail === req && req > 0;

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-16 bg-slate-200 rounded-full h-1.5 overflow-hidden">
          <div
            className={`h-1.5 rounded-full ${
              isComplete ? 'bg-emerald-600' : pct >= 50 ? 'bg-blue-600' : 'bg-amber-600'
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="text-xs font-semibold text-slate-700">
          {avail}/{req}
        </span>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between text-xs font-medium mb-1.5">
        <div className="flex items-center space-x-1.5">
          {isComplete ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-blue-700" />
          )}
          <span className="text-slate-700 font-medium">
            {avail} of {req} documents ready
          </span>
        </div>
        <span className={`font-semibold ${isComplete ? 'text-emerald-700' : 'text-slate-700'}`}>
          {pct}%
        </span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${
            isComplete
              ? 'bg-emerald-600'
              : pct >= 50
              ? 'bg-blue-600'
              : 'bg-amber-600'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
