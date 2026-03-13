// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Get auth token
function getToken() {
    return localStorage.getItem('token');
}

// API Request wrapper
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = getToken();
    
    const headers = {
        'Content-Type': 'application/json',
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
        method,
        headers,
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth APIs
const auth = {
    register: (userData) => apiRequest('/auth/register', 'POST', userData),
    login: (credentials) => apiRequest('/auth/login', 'POST', credentials),
    getProfile: () => apiRequest('/profile', 'GET'),
    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/pages/login.html';
    }
};

// SOS APIs
const sos = {
    trigger: (locationData) => apiRequest('/sos/trigger', 'POST', locationData),
    getHistory: () => apiRequest('/sos/history', 'GET')
};

// User APIs
const user = {
    getProfile: () => apiRequest('/profile', 'GET'),
    addEmergencyContact: (contact) => apiRequest('/profile/contacts', 'POST', contact),
    getEmergencyContacts: () => apiRequest('/profile/contacts', 'GET')
};

// Helplines APIs
const helplines = {
    getAll: () => apiRequest('/helplines', 'GET'),
    getByCountry: (country) => apiRequest(`/helplines/country/${country}`, 'GET')
};

// Export all APIs
window.SecureSheAPI = {
    auth,
    sos,
    user,
    helplines
};