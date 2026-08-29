import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, RotateCcw, Loader2, Sparkles, Building2, HelpCircle } from 'lucide-react';
import { useJourney } from '../../context/JourneyContext';

export default function AskAssistantPanel() {
  const {
    lifeEvent,
    isAssistantOpen,
    assistantServiceContext,
    assistantMessages,
    isAssistantThinking,
    openAssistant,
    closeAssistant,
    clearAssistantMessages,
    sendAssistantMessage,
  } = useJourney();

  const [inputVal, setInputVal] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (isAssistantOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [assistantMessages, isAssistantOpen, isAssistantThinking]);

  // Focus input when opened
  useEffect(() => {
    if (isAssistantOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isAssistantOpen]);

  const handleSend = (e) => {
    e?.preventDefault();
    if (!inputVal.trim() || isAssistantThinking) return;
    sendAssistantMessage(inputVal);
    setInputVal('');
  };

  const handleSuggestedClick = (questionText) => {
    if (isAssistantThinking) return;
    sendAssistantMessage(questionText);
  };

  const eventType = lifeEvent?.event_type || 'relocation';

  const serviceQuestions = [
    "Why is this relevant to me?",
    "What documents/information do I need?",
    "What should I do next for this service?",
  ];

  const scenarioGeneralQuestions = {
    financial_fraud: [
      "Where should I report this?",
      "What information should I keep ready?",
      "What should I do next?",
    ],
    marriage: [
      "What changed because I got married?",
      "Why do I need Aadhaar update?",
      "What documents do I need?",
    ],
    family_death: [
      "What do I need to do first?",
      "Why is death registration relevant?",
      "What documents do I need?",
    ],
    relocation: [
      "Why do I need the vehicle update?",
      "What documents am I missing?",
      "What should I do next?",
      "What does PDS mean?",
    ],
  };

  const generalQuestions = scenarioGeneralQuestions[eventType] || scenarioGeneralQuestions.relocation;
  const currentQuestions = assistantServiceContext ? serviceQuestions : generalQuestions;

  return (
    <>
      {/* Floating Trigger Button in bottom-right */}
      {!isAssistantOpen && (
        <button
          type="button"
          onClick={() => openAssistant()}
          aria-label="Open Ask LifeEvent assistant"
          className="fixed bottom-6 right-6 z-40 flex items-center space-x-2 px-4 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-full shadow-lg border border-slate-700 transition-all hover:scale-105 active:scale-95 cursor-pointer"
        >
          <MessageSquare className="w-4 h-4 text-blue-400 shrink-0" />
          <span className="text-xs sm:text-sm font-semibold">Ask LifeEvent</span>
        </button>
      )}

      {/* Floating Assistant Panel */}
      {isAssistantOpen && (
        <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-[calc(100vw-2rem)] sm:w-[420px] h-[540px] max-h-[85vh] bg-white rounded-2xl border border-slate-300 shadow-2xl flex flex-col overflow-hidden animate-fade-in">
          
          {/* Panel Header */}
          <div className="bg-slate-900 text-white p-4 border-b border-slate-800 flex items-center justify-between shrink-0">
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-blue-700 flex items-center justify-center text-white">
                <HelpCircle className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold tracking-tight text-white leading-tight">
                  Ask LifeEvent
                </h2>
                <p className="text-[11px] text-slate-400 leading-none mt-0.5">
                  Questions about your journey?
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-1">
              <button
                type="button"
                onClick={clearAssistantMessages}
                title="Clear conversation"
                className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={closeAssistant}
                aria-label="Close assistant"
                className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Active Context Banner if asking about a specific service */}
          {assistantServiceContext && (
            <div className="bg-blue-50 border-b border-blue-200 px-3.5 py-1.5 flex items-center justify-between text-xs text-blue-900 shrink-0">
              <div className="flex items-center space-x-1.5 truncate">
                <Building2 className="w-3.5 h-3.5 text-blue-700 shrink-0" />
                <span className="font-semibold truncate">Context: {assistantServiceContext.name}</span>
              </div>
              <button
                type="button"
                onClick={() => openAssistant(null)}
                className="text-[11px] text-blue-700 hover:underline shrink-0 ml-2"
              >
                Clear Context
              </button>
            </div>
          )}

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50">
            
            {/* Suggested Question Chips (Show at top of feed) */}
            <div className="space-y-1.5 pb-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                Suggested Questions
              </span>
              <div className="flex flex-wrap gap-1.5">
                {currentQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    disabled={isAssistantThinking}
                    onClick={() => handleSuggestedClick(q)}
                    className="text-left text-xs bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-lg px-2.5 py-1.5 transition-colors cursor-pointer disabled:opacity-50"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Conversation Messages */}
            {assistantMessages.map((msg) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={msg.id}
                  className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-xl px-3.5 py-2.5 text-xs sm:text-sm leading-relaxed ${
                      isUser
                        ? 'bg-slate-900 text-white rounded-br-none'
                        : 'bg-white text-slate-800 border border-slate-200/90 shadow-2xs rounded-bl-none'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  {!isUser && (
                    <span className="text-[10px] text-slate-400 mt-0.5 ml-1">
                      Verified LifeEvent Engine
                    </span>
                  )}
                </div>
              );
            })}

            {/* Thinking Indicator */}
            {isAssistantThinking && (
              <div className="flex items-start">
                <div className="bg-white border border-slate-200 rounded-xl rounded-bl-none px-3.5 py-2 text-xs text-slate-500 flex items-center space-x-2 shadow-2xs">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-700" />
                  <span>Consulting journey records...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <form onSubmit={handleSend} className="p-3 bg-white border-t border-slate-200 shrink-0">
            <div className="flex items-center space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                disabled={isAssistantThinking}
                placeholder="Ask about your services or documents..."
                className="flex-1 px-3 py-2 text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:border-slate-400 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!inputVal.trim() || isAssistantThinking}
                className="p-2 bg-blue-700 hover:bg-blue-800 disabled:bg-slate-300 text-white rounded-lg transition-colors shrink-0 cursor-pointer disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-[10px] text-slate-400 text-center mt-1.5">
              Grounded exclusively in verified prototype data.
            </p>
          </form>

        </div>
      )}
    </>
  );
}
