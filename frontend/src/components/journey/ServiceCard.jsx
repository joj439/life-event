import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Clock } from 'lucide-react';
import StatusBadge from '../common/StatusBadge';
import ReadinessMeter from '../common/ReadinessMeter';

export default function ServiceCard({ service, mockStatus = null }) {
  if (!service) return null;

  const readiness = service.readiness || {
    available_count: 0,
    required_count: (service.required_document_ids || []).length,
    percentage: 0,
    is_ready: false,
  };

  const status = mockStatus || service.mock_status || 'not_started';

  const getNextAction = (statusValue, isDocReady) => {
    switch (statusValue) {
      case 'completed':
        return 'Official record updated. Keep acknowledgment for your records.';
      case 'under_review':
        return 'Application under review at the local department office.';
      case 'action_required':
        return 'Missing documents required. Please update your document checklist.';
      case 'ready':
        return 'All documents ready. Proceed to submit application.';
      default:
        return isDocReady
          ? 'Documents available. Ready to initiate service application.'
          : 'Gather required documents before starting the update.';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm p-6 flex flex-col justify-between hover:border-slate-300 transition-colors">
      <div>
        {/* Header: Category & Status */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <span className="text-[11px] font-semibold tracking-wide text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 uppercase">
            {service.category}
          </span>
          <StatusBadge status={status} size="sm" />
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-slate-900 mb-2">
          {service.name}
        </h3>

        {/* Why Relevant */}
        <p className="text-sm text-slate-600 mb-4 leading-relaxed line-clamp-3">
          {service.why_relevant}
        </p>

        {/* Document Readiness */}
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/70 mb-4">
          <ReadinessMeter
            availableCount={readiness.available_count}
            requiredCount={readiness.required_count}
            percentage={readiness.percentage}
          />
        </div>

        {/* Next Action */}
        <div className="text-xs text-slate-500 mb-6 flex items-start space-x-1.5">
          <span className="font-semibold text-slate-700 shrink-0">Next step:</span>
          <span className="text-slate-600">{getNextAction(status, readiness.is_ready)}</span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-1.5 text-xs text-slate-500">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>Est. processing: ~{service.estimated_processing_days || 7} days</span>
        </div>

        <Link
          to={`/services/${service.id}`}
          className="inline-flex items-center space-x-1 text-xs font-semibold text-blue-700 hover:text-blue-900 transition-colors cursor-pointer"
        >
          <span>View service</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
