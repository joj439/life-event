import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ExternalLink,
  AlertCircle,
  FileText,
  Clock,
  Loader2,
  Building2,
  Check,
  Circle,
  MessageSquare,
  ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';
import { useJourney } from '../context/JourneyContext';
import StatusBadge from '../components/common/StatusBadge';
import ReadinessMeter from '../components/common/ReadinessMeter';

export default function ServiceDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { openAssistant } = useJourney();
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadService() {
      try {
        setLoading(true);
        const data = await api.getServiceById(id);
        setService(data);
      } catch (err) {
        setError(err.message || 'Service not found.');
      } finally {
        setLoading(false);
      }
    }
    loadService();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-slate-400 text-sm">
        <Loader2 className="w-6 h-6 animate-spin text-slate-600 mr-2" />
        <span>Loading service details...</span>
      </div>
    );
  }

  if (error || !service) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <AlertCircle className="w-10 h-10 text-amber-600 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-900 mb-1">Service Not Found</h2>
        <p className="text-sm text-slate-600 mb-6">{error || 'The requested service does not exist.'}</p>
        <Link
          to="/services"
          className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-700 text-white rounded-lg text-sm font-medium"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Directory</span>
        </Link>
      </div>
    );
  }

  const readiness = service.readiness || {
    required_documents: [],
    available_documents: [],
    missing_documents: [],
    available_count: 0,
    required_count: 0,
    percentage: 0,
    is_ready: false,
  };

  const isDocAvailable = (docId) => {
    return readiness.available_documents?.some((d) => d.id === docId);
  };

  const isRealExternalUrl = service.portal_url && service.portal_url.startsWith('http');

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
      
      {/* Back Button */}
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 mb-6 cursor-pointer"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back</span>
      </button>

      {/* Main Service Info Container */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 mb-8">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 pb-6 border-b border-slate-100">
          <div>
            <div className="flex items-center space-x-2.5 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                {service.category}
              </span>
              <StatusBadge status={service.mock_status || 'not_started'} />
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              {service.name}
            </h1>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => openAssistant({ id: service.id, name: service.name })}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5 text-blue-400" />
              <span>Ask about this service</span>
            </button>

            <div className="flex items-center space-x-1.5 text-xs text-slate-500 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-md shrink-0">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>Est. processing: <strong>~{service.estimated_processing_days} days</strong></span>
            </div>
          </div>
        </div>

        {/* Relevance Explanation */}
        <div className="bg-blue-50/60 border border-blue-200/70 rounded-lg p-4 my-6">
          <h2 className="text-xs font-bold uppercase tracking-wider text-blue-900 mb-1">
            Why this is relevant to you
          </h2>
          <p className="text-sm text-slate-800 leading-relaxed font-normal">
            {service.why_relevant}
          </p>
        </div>

        {/* Overview */}
        <div className="mb-6">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
            Service Description
          </h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            {service.description}
          </p>
        </div>

        {/* Document Readiness Breakdown */}
        <div className="border-t border-slate-100 pt-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-slate-900">
              Required Items ({readiness.available_count} of {readiness.required_count} Ready)
            </h2>
            <Link
              to="/documents"
              className="text-xs text-blue-700 hover:text-blue-900 font-semibold flex items-center space-x-1"
            >
              <span>Manage Checklist</span>
              <FileText className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="mb-4">
            <ReadinessMeter
              availableCount={readiness.available_count}
              requiredCount={readiness.required_count}
              percentage={readiness.percentage}
            />
          </div>

          {/* Document list */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {readiness.required_documents.map((doc) => {
              const available = isDocAvailable(doc.id);
              return (
                <div
                  key={doc.id}
                  className={`p-3.5 rounded-lg border flex items-start space-x-3 ${
                    available
                      ? 'bg-emerald-50/30 border-emerald-200'
                      : 'bg-amber-50/30 border-amber-200'
                  }`}
                >
                  <div
                    className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                      available ? 'bg-emerald-700 text-white' : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {available ? <Check className="w-3 h-3 stroke-[3]" /> : <Circle className="w-2.5 h-2.5 fill-amber-700" />}
                  </div>
                  <div>
                    <span className="text-xs sm:text-sm font-bold text-slate-900 block">{doc.name}</span>
                    <span className="text-[11px] text-slate-500 block mb-1">{doc.description}</span>
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${available ? 'text-emerald-700' : 'text-amber-800'}`}>
                      {available ? 'Available' : 'Needed / Pending'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Procedural Steps */}
        <div className="border-t border-slate-100 pt-6 mb-6">
          <h2 className="text-sm font-bold text-slate-900 mb-3">
            Application Procedure
          </h2>
          <div className="space-y-3">
            {service.basic_steps.map((step, idx) => (
              <div key={idx} className="flex items-start space-x-3 text-xs sm:text-sm">
                <span className="w-5 h-5 rounded-full bg-slate-100 border border-slate-300 text-slate-700 font-bold text-[11px] flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <p className="text-slate-700 leading-relaxed pt-0.5">
                  {step}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Official Portal Handoff Information Box */}
        <div className="border-t border-slate-100 pt-6 bg-slate-50 -mx-6 -mb-6 sm:-mx-8 sm:-mb-8 p-6 sm:p-8 rounded-b-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center space-x-2 mb-1">
                <Building2 className="w-4 h-4 text-slate-500" />
                <span className="text-sm font-bold text-slate-900">{service.portal_name}</span>
                {service.is_mock_portal ? (
                  <span className="text-[10px] font-bold uppercase bg-amber-100 text-amber-900 border border-amber-300 px-1.5 py-0.5 rounded">
                    Prototype portal
                  </span>
                ) : (
                  <span className="text-[10px] font-bold uppercase bg-emerald-100 text-emerald-900 border border-emerald-300 px-1.5 py-0.5 rounded">
                    Official Portal
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500">
                Official department window for electronic submission and processing.
              </p>
            </div>

            {isRealExternalUrl ? (
              <a
                href={service.portal_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center space-x-2 px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white text-xs sm:text-sm font-semibold rounded-lg transition-colors shadow-sm shrink-0"
              >
                <span>Continue to Official Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            ) : (
              <a
                href={`#`}
                onClick={(e) => {
                  e.preventDefault();
                  alert(`Demonstration link for "${service.name}". This points to the simulated prototype portal.`);
                }}
                className="inline-flex items-center justify-center space-x-2 px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white text-xs sm:text-sm font-semibold rounded-lg transition-colors shadow-sm shrink-0 cursor-pointer"
              >
                <span>Visit Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-200/80 flex items-center space-x-2 text-[11px] text-slate-500">
            <ShieldCheck className="w-4 h-4 text-slate-400 shrink-0" />
            <span>
              <strong>Notice:</strong> LifeEvent does not submit applications on your behalf. You will complete your request directly on the official portal.
            </span>
          </div>
        </div>

      </div>

    </div>
  );
}
