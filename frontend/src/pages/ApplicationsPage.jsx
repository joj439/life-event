import React, { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';

export default function ApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadApplications() {
      try {
        setLoading(true);
        const data = await api.getApplications();
        setApplications(data || []);
      } catch (err) {
        console.error('Failed to fetch applications:', err);
      } finally {
        setLoading(false);
      }
    }
    loadApplications();
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
      
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Application Tracking Dashboard
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          Monitor real-time status across multi-department citizen service requests.
        </p>
      </div>

      {/* Applications List */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-slate-400 text-sm">
          <Loader2 className="w-5 h-5 animate-spin mr-2 text-slate-600" />
          <span>Loading application statuses...</span>
        </div>
      ) : applications.length > 0 ? (
        <div className="space-y-4 mb-8">
          {applications.map((app) => (
            <div
              key={app.id}
              className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6"
            >
              {/* Application Row Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                      {app.category}
                    </span>
                    <span className="text-slate-300">&bull;</span>
                    <span className="text-xs font-mono font-semibold text-slate-600">
                      Ref: {app.tracking_number}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-900">
                    {app.service_name}
                  </h2>
                </div>

                <div className="shrink-0">
                  <StatusBadge status={app.status} size="md" />
                </div>
              </div>

              {/* Dates & Status Note */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 py-3 text-xs border-b border-slate-100">
                <div>
                  <span className="text-slate-400 font-medium">Submission Date:</span>{' '}
                  <span className="text-slate-800 font-semibold">{app.applied_date || 'Not submitted'}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-medium">Estimated Completion:</span>{' '}
                  <span className="text-slate-800 font-semibold">{app.estimated_completion_date || 'N/A'}</span>
                </div>
              </div>

              {/* Department Remark */}
              {app.remarks && (
                <div className="py-3 text-xs text-slate-700 bg-slate-50 rounded-md p-3 my-3 border border-slate-200/80">
                  <span className="font-semibold text-slate-900">Department Status Note:</span> {app.remarks}
                </div>
              )}

              {/* Milestone Checklist */}
              {app.steps && app.steps.length > 0 && (
                <div className="pt-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                    Milestone Progress
                  </span>
                  <div className="space-y-1.5">
                    {app.steps.map((step) => (
                      <div
                        key={step.step_order}
                        className={`flex items-center justify-between p-2.5 rounded-lg text-xs ${
                          step.is_completed
                            ? 'bg-emerald-50/50 text-emerald-950 border border-emerald-200/80'
                            : 'bg-slate-50 text-slate-600 border border-slate-200/80'
                        }`}
                      >
                        <div className="flex items-center space-x-2">
                          <span
                            className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${
                              step.is_completed
                                ? 'bg-emerald-700 text-white'
                                : 'bg-slate-200 text-slate-600'
                            }`}
                          >
                            {step.is_completed ? '✓' : step.step_order}
                          </span>
                          <span className="font-medium">{step.title}</span>
                        </div>

                        <span className="text-[11px] font-semibold text-slate-500">
                          {step.is_completed ? 'Completed' : 'Pending'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500 text-sm">
          No active applications tracked in this session.
        </div>
      )}

      {/* Info note */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-xs text-slate-500">
        Status records reflect demonstration citizen application states across municipal and state departments.
      </div>

    </div>
  );
}
