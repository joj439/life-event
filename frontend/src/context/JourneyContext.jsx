import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

const JourneyContext = createContext();

const STORAGE_KEY = 'life_event_journey_state_v1';

export function JourneyProvider({ children }) {
  const [lifeEvent, setLifeEvent] = useState(null);
  const [contextAnswers, setContextAnswers] = useState({
    permanent: true,
    owns_vehicle: true,
    receives_pds: true,
  });
  const [recommendedServices, setRecommendedServices] = useState([]);
  const [readinessSummary, setReadinessSummary] = useState(null);
  const [userDocuments, setUserDocuments] = useState([]);
  const [applications, setApplications] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Assistant State
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [assistantServiceContext, setAssistantServiceContext] = useState(null);
  const [assistantMessages, setAssistantMessages] = useState([
    {
      id: 'init_welcome',
      role: 'assistant',
      content: "Hello! I'm Ask LifeEvent. I can answer questions about your relocation journey, required documents, or recommended services based on verified government records.",
    }
  ]);
  const [isAssistantThinking, setIsAssistantThinking] = useState(false);

  // Hydrate state from sessionStorage on initial load
  useEffect(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.lifeEvent) setLifeEvent(parsed.lifeEvent);
        if (parsed.contextAnswers) setContextAnswers(parsed.contextAnswers);
        if (parsed.recommendedServices) setRecommendedServices(parsed.recommendedServices);
        if (parsed.readinessSummary) setReadinessSummary(parsed.readinessSummary);
      }
    } catch (e) {
      console.warn('Failed to load state from sessionStorage:', e);
    }
  }, []);

  // Sync state to sessionStorage on change
  useEffect(() => {
    try {
      if (lifeEvent) {
        const stateToSave = {
          lifeEvent,
          contextAnswers,
          recommendedServices,
          readinessSummary,
        };
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave));
      } else {
        sessionStorage.removeItem(STORAGE_KEY);
      }
    } catch (e) {
      console.warn('Failed to save state to sessionStorage:', e);
    }
  }, [lifeEvent, contextAnswers, recommendedServices, readinessSummary]);

  // Load fresh documents from backend and update summary
  const fetchDocuments = useCallback(async () => {
    try {
      const data = await api.getDocuments();
      if (data?.documents) {
        setUserDocuments(data.documents);
      }
      if (data?.summary) {
        // Always sync with backend's fresh summary
        setReadinessSummary(data.summary);
      }
      return data;
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  }, []);

  // Load fresh applications from backend
  const fetchApplications = useCallback(async () => {
    try {
      const data = await api.getApplications();
      if (data) {
        setApplications(data);
      }
      return data;
    } catch (err) {
      console.error('Failed to fetch applications:', err);
    }
  }, []);

  // Re-sync journey recommendations with backend
  const refreshJourney = useCallback(async (activeEvent = lifeEvent, activeContext = contextAnswers) => {
    if (!activeEvent?.id) return;
    try {
      const res = await api.submitContext(activeEvent.id, activeContext);
      if (res?.recommended_services) {
        setRecommendedServices(res.recommended_services);
      }
      if (res?.readiness_summary) {
        setReadinessSummary(res.readiness_summary);
      }
      return res;
    } catch (err) {
      console.error('Failed to refresh journey recommendations:', err);
    }
  }, [lifeEvent, contextAnswers]);

  // Analyze Life Event
  const analyzeLifeEvent = async (message) => {
    setIsLoading(true);
    setError(null);
    try {
      const event = await api.analyzeLifeEvent(message);
      setLifeEvent(event);
      return event;
    } catch (err) {
      setError(err.message || 'Failed to analyze life event.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Submit Context Answers
  const submitContext = async (answers) => {
    if (!lifeEvent?.id) {
      throw new Error('No active life event found. Please describe your situation first.');
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.submitContext(lifeEvent.id, answers);
      setContextAnswers(answers);
      setRecommendedServices(res.recommended_services || []);
      setReadinessSummary(res.readiness_summary || null);
      
      // Concurrently update documents and applications
      await Promise.all([fetchDocuments(), fetchApplications()]);
      return res;
    } catch (err) {
      setError(err.message || 'Failed to generate recommendations.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle user document status and immediately synchronize readiness across journey
  const toggleDocument = async (docTypeId, explicitStatus = null) => {
    try {
      const updatedDoc = await api.toggleDocument(docTypeId, explicitStatus);
      // Fetch fresh documents from backend
      await fetchDocuments();
      // If there is an active journey, re-sync service readiness
      if (lifeEvent?.id && contextAnswers) {
        await refreshJourney(lifeEvent, contextAnswers);
      }
      return updatedDoc;
    } catch (err) {
      console.error('Failed to toggle document:', err);
      throw err;
    }
  };

  // Reset demo: Invalidate session storage and restore pristine backend demo state
  const resetDemo = async () => {
    try {
      // 1. Reset backend repository
      await api.resetDemoState();
      
      // 2. Clear frontend session storage
      sessionStorage.removeItem(STORAGE_KEY);
      
      // 3. Clear in-memory journey state
      setLifeEvent(null);
      setContextAnswers({
        permanent: true,
        owns_vehicle: true,
        receives_pds: true,
      });
      setRecommendedServices([]);
      setReadinessSummary(null);
      setError(null);

      // 4. Fetch fresh default documents and applications from backend
      const [docData, appData] = await Promise.all([
        api.getDocuments(),
        api.getApplications()
      ]);

      if (docData?.documents) {
        setUserDocuments(docData.documents);
      }
      if (docData?.summary) {
        setReadinessSummary(docData.summary);
      }
      if (appData) {
        setApplications(appData);
      }

      // 5. Reset assistant state
      setAssistantServiceContext(null);
      setAssistantMessages([
        {
          id: 'init_welcome',
          role: 'assistant',
          content: "Hello! I'm Ask LifeEvent. I can answer questions about your relocation journey, required documents, or recommended services based on verified government records.",
        }
      ]);
    } catch (err) {
      console.error('Failed to reset demo state:', err);
    }
  };

  // Assistant Controls
  const openAssistant = (serviceContext = null) => {
    if (serviceContext) {
      setAssistantServiceContext(serviceContext);
    }
    setIsAssistantOpen(true);
  };

  const closeAssistant = () => {
    setIsAssistantOpen(false);
  };

  const clearAssistantMessages = () => {
    setAssistantMessages([
      {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: "Conversation cleared. How can I help you understand your government service journey today?",
      }
    ]);
  };

  const sendAssistantMessage = async (userMessageText) => {
    const text = userMessageText?.trim();
    if (!text) return;

    const userMsgId = `user_${Date.now()}`;
    const userMsg = { id: userMsgId, role: 'user', content: text };
    
    setAssistantMessages((prev) => [...prev, userMsg]);
    setIsAssistantThinking(true);

    try {
      const activeServiceId = assistantServiceContext?.id || null;
      const res = await api.askAssistant(text, lifeEvent?.id || null, activeServiceId);
      
      const assistantMsg = {
        id: `asst_${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        source: res.source,
        serviceId: res.service_id,
      };
      setAssistantMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: "I was unable to connect to the service. Please make sure the backend is active and try again.",
        isError: true,
      };
      setAssistantMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsAssistantThinking(false);
    }
  };

  // Initial load on application mount
  useEffect(() => {
    fetchDocuments();
    fetchApplications();
  }, [fetchDocuments, fetchApplications]);

  return (
    <JourneyContext.Provider
      value={{
        lifeEvent,
        setLifeEvent,
        contextAnswers,
        recommendedServices,
        readinessSummary,
        userDocuments,
        applications,
        isLoading,
        error,
        setError,
        analyzeLifeEvent,
        submitContext,
        fetchDocuments,
        fetchApplications,
        refreshJourney,
        toggleDocument,
        resetDemo,
        // Assistant
        isAssistantOpen,
        assistantServiceContext,
        assistantMessages,
        isAssistantThinking,
        openAssistant,
        closeAssistant,
        clearAssistantMessages,
        sendAssistantMessage,
      }}
    >
      {children}
    </JourneyContext.Provider>
  );
}

export function useJourney() {
  const context = useContext(JourneyContext);
  if (!context) {
    throw new Error('useJourney must be used within a JourneyProvider');
  }
  return context;
}
