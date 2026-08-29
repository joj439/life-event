/**
 * Centralized API client for LifeEvent frontend.
 * Communicates with the FastAPI backend (/api/v1/...).
 */

const API_BASE_URL = '/api/v1';

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      let errorMessage = 'An unexpected error occurred. Please try again.';
      if (data) {
        if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail) && data.detail[0]?.msg) {
          errorMessage = data.detail[0].msg;
        } else if (data.message) {
          errorMessage = data.message;
        }
      }
      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Unable to connect to the LifeEvent service. Please ensure the backend is running.');
    }
    throw err;
  }
}

export const api = {
  // Life Event Analysis
  analyzeLifeEvent: async (message) => {
    return request('/life-events/analyze', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  },

  getLifeEvent: async (eventId) => {
    return request(`/life-events/${eventId}`, {
      method: 'GET',
    });
  },

  submitContext: async (eventId, contextAnswers) => {
    return request(`/life-events/${eventId}/context`, {
      method: 'POST',
      body: JSON.stringify(contextAnswers),
    });
  },

  // Services
  getServices: async (lifeEvent = null) => {
    const query = lifeEvent ? `?life_event=${encodeURIComponent(lifeEvent)}` : '';
    return request(`/services${query}`, {
      method: 'GET',
    });
  },

  getServiceById: async (serviceId) => {
    return request(`/services/${serviceId}`, {
      method: 'GET',
    });
  },

  // Documents
  getDocuments: async () => {
    return request('/documents', {
      method: 'GET',
    });
  },

  toggleDocument: async (documentTypeId, status = null) => {
    return request('/documents/toggle', {
      method: 'POST',
      body: JSON.stringify({
        document_type_id: documentTypeId,
        status,
      }),
    });
  },

  // Applications
  getApplications: async () => {
    return request('/applications', {
      method: 'GET',
    });
  },

  getApplicationById: async (appId) => {
    return request(`/applications/${appId}`, {
      method: 'GET',
    });
  },

  // Demo Reset
  resetDemoState: async () => {
    return request('/demo/reset', {
      method: 'POST',
    });
  },

  // Ask LifeEvent Assistant
  askAssistant: async (message, lifeEventId = null, serviceId = null) => {
    return request('/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        life_event_id: lifeEventId,
        service_id: serviceId,
      }),
    });
  },
};
