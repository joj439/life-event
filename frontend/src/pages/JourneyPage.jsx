import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, ShieldCheck, Home, ExternalLink, ShieldAlert, Heart, Activity, Compass } from 'lucide-react';
import { useJourney } from '../context/JourneyContext';
import ServiceCard from '../components/journey/ServiceCard';

export default function JourneyPage() {
  const {
    lifeEvent,
    recommendedServices,
    readinessSummary,
    fetchDocuments,
    fetchApplications,
    refreshJourney,
    applications
  } = useJourney();

  useEffect(() => {
    fetchDocuments();
    fetchApplications();
    if (lifeEvent?.id) {
      refreshJourney();
    }
  }, [lifeEvent?.id, fetchDocuments, fetchApplications, refreshJourney]);

  const eventType = lifeEvent?.event_type || 'relocation';
  const origin = lifeEvent?.origin || 'Mumbai';
  const destination = lifeEvent?.destination || 'Pune';

  const servicesToDisplay = recommendedServices.length > 0 ? recommendedServices : [];

  const totalServices = servicesToDisplay.length;
  const availDocs = readinessSummary?.total_available ?? 2;
  const reqDocs = readinessSummary?.total_required ?? 3;
  const actionsNeeded = servicesToDisplay.filter(
    (s) => s.mock_status === 'action_required' || !s.readiness?.is_ready
  ).length || 1;

  const getServiceStatus = (serviceId, defaultStatus) => {
    const app = applications.find((a) => a.service_id === serviceId);
    return app ? app.status : defaultStatus;
  };

  const getScenarioHeader = () => {
    switch (eventType) {
      case 'financial_fraud':
        return {
          title: 'Cyber Fraud Action Journey',
          badge: 'Financial Cyber Fraud Response',
          icon: ShieldAlert,
          subtitle: 'Incident intimation and dispute hold procedures',
        };
      case 'marriage':
        return {
          title: 'Marriage & Civil Service Journey',
          badge: 'Marriage / Civil Status Change',
          icon: Heart,
          subtitle: 'Legal marriage registration and identity record synchronization',
        };
      case 'family_death':
        return {
          title: 'Vital Records & Survivor Navigator',
          badge: 'Family Demise & Vital Records',
          icon: Activity,
          subtitle: 'Municipal death registration and survivor benefits transition',
        };
      default:
        return {
          title: 'Your Government Service Journey',
          badge: `Relocation • ${origin} → ${destination}`,
          icon: Compass,
          subtitle: `Recommended services for your move to ${destination}`,
        };
    }
  };

  const headerInfo = getScenarioHeader();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
      
      {/* Top Banner & Summary */}
      <div className="bg-slate-900 text-white rounded-xl p-6 sm:p-8 mb-8 border border-slate-800 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
              Personalized Action Plan
            </span>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
              {headerInfo.title}
            </h1>
            <div className="flex items-center space-x-2 text-sm text-slate-300">
              <span className="text-slate-400">Life Event:</span>
              <span className="font-semibold text-white bg-slate-800 px-2.5 py-0.5 rounded border border-slate-700">
                {headerInfo.badge}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2.5">
            <Link
              to="/documents"
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm"
            >
              <FileText className="w-4 h-4" />
              <span>{eventType === 'financial_fraud' ? 'Information Checklist' : 'Document Checklist'}</span>
            </Link>

            <Link
              to="/applications"
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-colors"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Track Applications</span>
            </Link>
          </div>
        </div>

        {/* Structured Summary Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 text-slate-200">
          <div className="bg-slate-800/80 rounded-lg p-4 border border-slate-700/70">
            <span className="text-xs text-slate-400 font-medium block">Relevant Services</span>
            <span className="text-2xl font-bold text-white mt-1 block">{totalServices || 1}</span>
          </div>

          <div className="bg-slate-800/80 rounded-lg p-4 border border-slate-700/70">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium block">
                {eventType === 'financial_fraud' ? 'Information Ready' : 'Document Readiness'}
              </span>
              {readinessSummary?.is_demo_preset ? (
                <span className="text-[9px] uppercase font-bold text-blue-300 bg-blue-900/60 px-1.5 py-0.5 rounded border border-blue-700/60">
                  Demo Preset
                </span>
              ) : (
                <span className="text-[9px] uppercase font-bold text-slate-300 bg-slate-700/60 px-1.5 py-0.5 rounded">
                  Citizen Verified
                </span>
              )}
            </div>
            <span className="text-2xl font-bold text-white mt-1 block">{availDocs} / {reqDocs} Ready</span>
          </div>

          <div className="bg-slate-800/80 rounded-lg p-4 border border-slate-700/70">
            <span className="text-xs text-slate-400 font-medium block">Actions Needed</span>
            <span className="text-2xl font-bold text-amber-400 mt-1 block">{actionsNeeded}</span>
          </div>
        </div>
      </div>

      {/* Services Section */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-900">Recommended Public Services</h2>
        <p className="text-xs sm:text-sm text-slate-600">
          {headerInfo.subtitle}
        </p>
      </div>

      {servicesToDisplay.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          {servicesToDisplay.map((service) => (
            <ServiceCard
              key={service.id}
              service={service}
              mockStatus={getServiceStatus(service.id, service.mock_status)}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center mb-10">
          <p className="text-slate-600 mb-4 text-sm">No active life event submitted yet.</p>
          <Link
            to="/"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-700 text-white text-xs sm:text-sm font-semibold rounded-lg"
          >
            <Home className="w-4 h-4" />
            <span>Describe Your Life Event</span>
          </Link>
        </div>
      )}

      {/* Official Portal Handoff Card */}
      <section className="bg-blue-50/60 border border-blue-200 rounded-xl p-6 sm:p-8 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-900 block mb-1">
              Ready to Continue
            </span>
            <h3 className="text-lg font-bold text-slate-900">
              Continue to Official Government Portals
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl">
              LifeEvent has organized your requirements and information checklist. You will proceed to the official department portals to file applications directly.
            </p>
          </div>

          <div className="shrink-0">
            <span className="text-[11px] text-slate-500 block italic">
              Note: LifeEvent does not submit applications on your behalf.
            </span>
          </div>
        </div>
      </section>

      {/* Structured Roadmap */}
      <section className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-4">
          Journey Roadmap & Procedure
        </h3>

        <div className="space-y-4">
          <div className="flex items-start space-x-3 text-sm">
            <span className="w-6 h-6 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
              1
            </span>
            <div>
              <span className="font-bold text-slate-900 block">Life Event Identification</span>
              <span className="text-xs text-slate-500">{headerInfo.badge} recorded.</span>
            </div>
          </div>

          <div className="flex items-start space-x-3 text-sm">
            <span className="w-6 h-6 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
              2
            </span>
            <div>
              <span className="font-bold text-slate-900 block">Deterministic Requirement Check</span>
              <span className="text-xs text-slate-500">{totalServices} service(s) identified through verified rules.</span>
            </div>
          </div>

          <div className="flex items-start space-x-3 text-sm">
            <span className="w-6 h-6 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
              3
            </span>
            <div>
              <span className="font-bold text-slate-900 block">Checklist Verification</span>
              <span className="text-xs text-slate-500">{availDocs} of {reqDocs} required items currently available.</span>
            </div>
          </div>

          <div className="flex items-start space-x-3 text-sm">
            <span className="w-6 h-6 rounded-full bg-blue-700 text-white text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
              4
            </span>
            <div>
              <span className="font-bold text-slate-900 block">Official Portal Submission</span>
              <span className="text-xs text-slate-500">Proceed to official verified government portals to complete filings.</span>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
