import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Check, ArrowLeft, Loader2, Home } from 'lucide-react';
import { useJourney } from '../context/JourneyContext';

export default function ContextQuestionsPage() {
  const { lifeEvent, submitContext, isLoading } = useJourney();
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(1);
  const [answers, setAnswers] = useState({
    permanent: true,
    owns_vehicle: true,
    receives_pds: true,
    unauthorized_txn: true,
    has_txn_id: true,
    knows_bank: true,
    details_changed: true,
    address_changed: false,
    needs_marriage_cert: true,
    looking_for_death_cert: true,
    pension_or_benefits_involved: true,
  });

  if (!lifeEvent) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <p className="text-slate-600 mb-4">No active life event found. Please start from the homepage.</p>
        <Link to="/" className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-700 text-white rounded-lg text-sm font-medium">
          <Home className="w-4 h-4" />
          <span>Return to Home</span>
        </Link>
      </div>
    );
  }

  const eventType = lifeEvent.event_type || 'relocation';

  // Define scenario-specific question sets
  const scenarioQuestions = {
    relocation: [
      {
        id: 'permanent',
        step: 1,
        title: 'Is this a permanent move?',
        description: 'Permanent relocations determine eligibility for local municipal welfare programs and voter registration updates.',
        field: 'permanent',
      },
      {
        id: 'owns_vehicle',
        step: 2,
        title: 'Do you own a vehicle?',
        description: 'Motor vehicle regulations require recording address changes on your vehicle Registration Certificate (RC).',
        field: 'owns_vehicle',
      },
      {
        id: 'receives_pds',
        step: 3,
        title: 'Are you currently receiving government food/PDS benefits?',
        description: 'Public Distribution System (PDS) ration cards must be updated to transfer grain quotas to your new locality.',
        field: 'receives_pds',
      },
    ],
    financial_fraud: [
      {
        id: 'unauthorized_txn',
        step: 1,
        title: 'Was the financial transaction unauthorized or fraudulent?',
        description: 'Unapproved debits, phishing scams, or cyber theft require filing an intimation with the National Cyber Crime Reporting mechanism.',
        field: 'unauthorized_txn',
      },
      {
        id: 'has_txn_id',
        step: 2,
        title: 'Do you have the transaction reference number (UTR / Txn ID)?',
        description: 'Having the transaction reference from your payment alert SMS or banking statement speeds up dispute holds.',
        field: 'has_txn_id',
      },
      {
        id: 'knows_bank',
        step: 3,
        title: 'Do you know which bank or payment app was involved?',
        description: 'Identifying the payment intermediary helps guide dispute intimation to the appropriate nodal officers.',
        field: 'knows_bank',
      },
    ],
    marriage: [
      {
        id: 'details_changed',
        step: 1,
        title: 'Have your personal details or surname changed?',
        description: 'Updating your legal name or marital status requires demographic modification in the Aadhaar identity registry.',
        field: 'details_changed',
      },
      {
        id: 'address_changed',
        step: 2,
        title: 'Has your residential address changed after marriage?',
        description: 'Relocating to a new residence requires updating your official address across civil records.',
        field: 'address_changed',
      },
      {
        id: 'needs_marriage_cert',
        step: 3,
        title: 'Do you need guidance on official Marriage Registration?',
        description: 'Registering your marriage provides the official legal proof required for joint civic records, visas, and benefits.',
        field: 'needs_marriage_cert',
      },
    ],
    family_death: [
      {
        id: 'looking_for_death_cert',
        step: 1,
        title: 'Are you looking for Death Registration and certificate guidance?',
        description: 'Obtaining the official Death Certificate from the municipal registrar is the primary vital record needed for all subsequent legal procedures.',
        field: 'looking_for_death_cert',
      },
      {
        id: 'pension_or_benefits_involved',
        step: 2,
        title: 'Are government pension, gratuity, or survivor welfare benefits involved?',
        description: 'If the deceased was a pensioner or eligible for social welfare, notifying the authority initiates family pension and nominee settlements.',
        field: 'pension_or_benefits_involved',
      },
    ],
  };

  const questions = scenarioQuestions[eventType] || scenarioQuestions.relocation;
  const totalSteps = questions.length;
  const currentQ = questions[Math.min(currentStep - 1, totalSteps - 1)];

  const handleSelectOption = async (value) => {
    const updatedAnswers = { ...answers, [currentQ.field]: value };
    setAnswers(updatedAnswers);

    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      // Final step submitted
      try {
        await submitContext(updatedAnswers);
        navigate('/journey');
      } catch (err) {
        console.error('Failed to submit context:', err);
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    } else {
      navigate('/confirm');
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8">
        
        {/* Step Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            <span>Context Assessment</span>
            <span className="text-blue-700 font-bold">Step {currentStep} of {totalSteps}</span>
          </div>

          <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-blue-700 h-1.5 rounded-full transition-all duration-200"
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Question Title & Description */}
        <div className="mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mb-2">
            {currentQ.title}
          </h2>

          <p className="text-sm text-slate-600 leading-relaxed">
            {currentQ.description}
          </p>
        </div>

        {/* Large Option Buttons */}
        <div className="space-y-3 mb-6">
          <button
            type="button"
            disabled={isLoading}
            onClick={() => handleSelectOption(true)}
            className={`w-full flex items-center justify-between p-4 rounded-lg border-2 transition-colors cursor-pointer ${
              answers[currentQ.field] === true
                ? 'border-blue-700 bg-blue-50/50 text-blue-950'
                : 'border-slate-200 hover:border-slate-300 bg-white text-slate-800'
            }`}
          >
            <div className="flex items-center space-x-3 text-left">
              <span className="w-6 h-6 rounded-full border border-slate-300 bg-white flex items-center justify-center font-bold text-xs text-slate-700">
                A
              </span>
              <span className="font-semibold text-base">Yes</span>
            </div>
            <Check className={`w-5 h-5 ${answers[currentQ.field] === true ? 'text-blue-700' : 'text-transparent'}`} />
          </button>

          <button
            type="button"
            disabled={isLoading}
            onClick={() => handleSelectOption(false)}
            className={`w-full flex items-center justify-between p-4 rounded-lg border-2 transition-colors cursor-pointer ${
              answers[currentQ.field] === false
                ? 'border-blue-700 bg-blue-50/50 text-blue-950'
                : 'border-slate-200 hover:border-slate-300 bg-white text-slate-800'
            }`}
          >
            <div className="flex items-center space-x-3 text-left">
              <span className="w-6 h-6 rounded-full border border-slate-300 bg-white flex items-center justify-center font-bold text-xs text-slate-700">
                B
              </span>
              <span className="font-semibold text-base">No</span>
            </div>
            <Check className={`w-5 h-5 ${answers[currentQ.field] === false ? 'text-blue-700' : 'text-transparent'}`} />
          </button>
        </div>

        {/* Footer Navigation */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <button
            type="button"
            onClick={handleBack}
            className="flex items-center space-x-1.5 text-xs sm:text-sm font-semibold text-slate-600 hover:text-slate-900 cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <div className="text-xs text-slate-400">
            {isLoading && (
              <span className="inline-flex items-center space-x-1.5 text-blue-700 font-medium">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Mapping services...</span>
              </span>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
