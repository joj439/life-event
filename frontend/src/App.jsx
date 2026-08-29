import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { JourneyProvider } from './context/JourneyContext';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';
import HomePage from './pages/HomePage';
import LifeEventConfirmPage from './pages/LifeEventConfirmPage';
import ContextQuestionsPage from './pages/ContextQuestionsPage';
import JourneyPage from './pages/JourneyPage';
import ServicesListPage from './pages/ServicesListPage';
import ServiceDetailPage from './pages/ServiceDetailPage';
import DocumentsPage from './pages/DocumentsPage';
import ApplicationsPage from './pages/ApplicationsPage';
import NotFoundPage from './pages/NotFoundPage';
import AskAssistantPanel from './components/assistant/AskAssistantPanel';

function App() {
  return (
    <JourneyProvider>
      <Router>
        <div className="flex flex-col min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-blue-100 selection:text-blue-900">
          <Navbar />
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/confirm" element={<LifeEventConfirmPage />} />
              <Route path="/context" element={<ContextQuestionsPage />} />
              <Route path="/journey" element={<JourneyPage />} />
              <Route path="/services" element={<ServicesListPage />} />
              <Route path="/services/:id" element={<ServiceDetailPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/applications" element={<ApplicationsPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
          <AskAssistantPanel />
          <Footer />
        </div>
      </Router>
    </JourneyProvider>
  );
}

export default App;
