import React, { useState } from 'react';
import { FileText, CheckCircle2, AlertCircle, Loader2, Check, Circle, Info, HelpCircle } from 'lucide-react';
import { useJourney } from '../context/JourneyContext';
import ReadinessMeter from '../components/common/ReadinessMeter';

export default function DocumentsPage() {
  const { userDocuments, toggleDocument, readinessSummary, lifeEvent, recommendedServices } = useJourney();
  const [togglingId, setTogglingId] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);

  const handleToggle = async (docTypeId, currentStatus) => {
    setTogglingId(docTypeId);
    try {
      const nextStatus = currentStatus === 'available' ? 'missing' : 'available';
      await toggleDocument(docTypeId, nextStatus);
      setToastMessage(`Status updated to ${nextStatus === 'available' ? 'Available' : 'Needed'}.`);
      setTimeout(() => setToastMessage(null), 3000);
    } catch (err) {
      console.error('Failed to toggle document:', err);
    } finally {
      setTogglingId(null);
    }
  };

  // Extract list of document IDs required for active scenario services
  const activeRequiredDocIds = new Set();
  if (recommendedServices && recommendedServices.length > 0) {
    recommendedServices.forEach((svc) => {
      svc.required_document_ids?.forEach((id) => activeRequiredDocIds.add(id));
    });
  }

  // Filter documents to show active scenario items first if an event is active
  const displayedDocs = activeRequiredDocIds.size > 0
    ? userDocuments.filter((d) => activeRequiredDocIds.has(d.document_type_id))
    : userDocuments;

  const totalAvail = readinessSummary?.total_available ?? displayedDocs.filter((d) => d.status === 'available').length;
  const totalReq = readinessSummary?.total_required ?? displayedDocs.length;
  const isDemoPreset = readinessSummary?.is_demo_preset ?? (lifeEvent?.event_type === 'relocation');

  const eventType = lifeEvent?.event_type || 'relocation';

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            {eventType === 'financial_fraud' ? 'Information & Document Checklist' : 'Document Readiness Checklist'}
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            {eventType === 'financial_fraud'
              ? 'Keep necessary transaction details and proofs ready before continuing to the official cybercrime portal.'
              : 'Mark required documents as available to verify readiness for government service applications.'}
          </p>
        </div>

        {toastMessage && (
          <div className="inline-flex items-center space-x-1.5 bg-emerald-50 text-emerald-800 border border-emerald-300 px-3 py-1.5 rounded-md text-xs font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
            <span>{toastMessage}</span>
          </div>
        )}
      </div>

      {/* Summary Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6 mb-6">
        <div className="max-w-md">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">
              Readiness Assessment
            </span>
            {isDemoPreset ? (
              <span className="text-[10px] font-bold uppercase bg-blue-50 text-blue-800 border border-blue-200 px-1.5 py-0.5 rounded">
                Demo Baseline Preset
              </span>
            ) : (
              <span className="text-[10px] font-bold uppercase bg-slate-100 text-slate-700 border border-slate-300 px-1.5 py-0.5 rounded">
                Citizen Self-Verified
              </span>
            )}
          </div>

          <div className="text-xl font-bold text-slate-900 mb-3">
            {totalAvail} / {totalReq} {eventType === 'financial_fraud' ? 'Items' : 'Documents'} Available
          </div>

          <ReadinessMeter
            availableCount={totalAvail}
            requiredCount={totalReq}
          />
        </div>
      </div>

      {/* Checklist Items */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm divide-y divide-slate-200 mb-6">
        {displayedDocs.map((doc) => {
          const isAvailable = doc.status === 'available';
          const isBusy = togglingId === doc.document_type_id;

          return (
            <div
              key={doc.id}
              className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/50 transition-colors"
            >
              <div className="flex items-start space-x-3.5">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                    isAvailable
                      ? 'bg-emerald-700 text-white'
                      : 'bg-slate-100 border border-slate-300 text-slate-400'
                  }`}
                >
                  {isAvailable ? (
                    <Check className="w-3.5 h-3.5 stroke-[3]" />
                  ) : (
                    <Circle className="w-2.5 h-2.5 fill-slate-400" />
                  )}
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-bold text-slate-900 text-sm sm:text-base">
                      {doc.document_name}
                    </h2>

                    {doc.is_information_item && (
                      <span className="text-[10px] font-bold uppercase tracking-wider bg-purple-50 text-purple-800 border border-purple-200 px-1.5 py-0.5 rounded">
                        Information Record
                      </span>
                    )}

                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
                        isAvailable
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          : 'bg-amber-50 text-amber-900 border-amber-300'
                      }`}
                    >
                      {isAvailable ? 'Available' : 'Needed / Not yet verified'}
                    </span>
                  </div>

                  <span className="text-xs text-slate-500 block mt-0.5">
                    {doc.updated_at ? `Recorded: ${new Date(doc.updated_at).toLocaleDateString()}` : 'Status pending citizen confirmation'}
                  </span>
                </div>
              </div>

              {/* Action Button */}
              <button
                type="button"
                disabled={isBusy}
                onClick={() => handleToggle(doc.document_type_id, doc.status)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors shrink-0 cursor-pointer ${
                  isAvailable
                    ? 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-50'
                    : 'bg-blue-700 hover:bg-blue-800 text-white shadow-sm'
                }`}
              >
                {isBusy ? (
                  <span className="inline-flex items-center space-x-1">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Updating...</span>
                  </span>
                ) : isAvailable ? (
                  'Mark as Needed'
                ) : (
                  'Mark as Available'
                )}
              </button>
            </div>
          );
        })}
      </div>

    </div>
  );
}
