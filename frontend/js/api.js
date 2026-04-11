/* ========================================
   CITIZENSHIELD - API CLIENT
   All Backend Communication Endpoints
   ======================================== */

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// ============ API Client Class ============

class ApiClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    /**
     * Get auth token from localStorage
     * @returns {string|null}
     */
    getToken() {
        return localStorage.getItem('token');
    }

    /**
     * Set auth token
     * @param {string} token
     */
    setToken(token) {
        if (token) {
            localStorage.setItem('token', token);
        } else {
            localStorage.removeItem('token');
        }
    }

    /**
     * Get user from localStorage
     * @returns {object|null}
     */
    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    /**
     * Set user data
     * @param {object} user
     */
    setUser(user) {
        if (user) {
            localStorage.setItem('user', JSON.stringify(user));
        } else {
            localStorage.removeItem('user');
        }
    }

    /**
     * Clear all auth data (logout)
     */
    clearAuth() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('loginTime');
    }

    /**
     * Make API request
     * @param {string} endpoint - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise}
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const token = this.getToken();
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const config = {
            ...options,
            headers
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                if (response.status === 401) {
                    this.clearAuth();
                    if (!window.location.pathname.includes('login.html')) {
                        window.location.href = '/pages/login.html';
                    }
                }
                throw new Error(data.error || data.message || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // ============ Auth APIs ============

    /**
     * Register new user
     * @param {object} userData - { name, email, phone, password }
     * @returns {Promise}
     */
    async register(userData) {
        const response = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        if (response.access_token) {
            this.setToken(response.access_token);
            this.setUser(response.user);
        }
        
        return response;
    }

    /**
     * Login user
     * @param {object} credentials - { email, password }
     * @returns {Promise}
     */
    async login(credentials) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        
        if (response.access_token) {
            this.setToken(response.access_token);
            this.setUser(response.user);
            localStorage.setItem('loginTime', Date.now().toString());
        }
        
        return response;
    }

    /**
     * Refresh access token
     * @returns {Promise}
     */
    async refreshToken() {
        return this.request('/auth/refresh', {
            method: 'POST'
        });
    }

    /**
     * Get current user profile
     * @returns {Promise}
     */
    async getProfile() {
        return this.request('/profile', {
            method: 'GET'
        });
    }

    /**
     * Update user profile
     * @param {object} data - { name, email, phone }
     * @returns {Promise}
     */
    async updateProfile(data) {
        const response = await this.request('/profile/update', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        
        if (response.user) {
            const currentUser = this.getUser();
            this.setUser({ ...currentUser, ...response.user });
        }
        
        return response;
    }

    // ============ Emergency Contacts APIs ============

    /**
     * Get all emergency contacts
     * @returns {Promise}
     */
    async getEmergencyContacts() {
        const profile = await this.getProfile();
        return profile.emergency_contacts || [];
    }

    /**
     * Add emergency contact
     * @param {object} contact - { name, phone, email, relationship }
     * @returns {Promise}
     */
    async addEmergencyContact(contact) {
        return this.request('/profile/contacts', {
            method: 'POST',
            body: JSON.stringify(contact)
        });
    }

    /**
     * Delete emergency contact
     * @param {number} contactId
     * @returns {Promise}
     */
    async deleteEmergencyContact(contactId) {
        return this.request(`/profile/contacts/${contactId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Set primary emergency contact
     * @param {number} contactId
     * @returns {Promise}
     */
    async setPrimaryContact(contactId) {
        return this.request(`/profile/contacts/${contactId}/primary`, {
            method: 'PUT'
        });
    }

    // ============ SOS APIs ============

    /**
     * Trigger SOS alert
     * @param {object} location - { latitude, longitude, address, message }
     * @returns {Promise}
     */
    async triggerSos(location) {
        return this.request('/sos/trigger', {
            method: 'POST',
            body: JSON.stringify(location)
        });
    }

    /**
     * Get SOS history
     * @param {number} page - Page number
     * @returns {Promise}
     */
    async getSosHistory(page = 1) {
        return this.request(`/sos/history?page=${page}`, {
            method: 'GET'
        });
    }

    /**
     * Resolve SOS alert
     * @param {number} sosId
     * @returns {Promise}
     */
    async resolveSos(sosId) {
        return this.request(`/sos/${sosId}/resolve`, {
            method: 'PUT'
        });
    }

    // ============ Helpline APIs ============

    /**
     * Get all helplines
     * @param {string} country - Optional country filter
     * @returns {Promise}
     */
    async getHelplines(country = null) {
        const url = country ? `/helplines?country=${country}` : '/helplines';
        return this.request(url, {
            method: 'GET'
        });
    }

    /**
     * Get helplines by country
     * @param {string} country
     * @returns {Promise}
     */
    async getHelplinesByCountry(country) {
        return this.request(`/helplines/country/${country}`, {
            method: 'GET'
        });
    }

    // ============ Crime Awareness APIs ============

    /**
     * Get all crime types and statistics
     * @returns {Promise}
     */
    async getCrimeStatistics() {
        return Promise.resolve({
            cyber_crime: 35,
            theft: 28,
            assault: 18,
            fraud: 12,
            others: 7,
            total_cases_2023: 145678,
            women_safety_cases: 33892,
            cyber_crime_cases: 65893
        });
    }

    /**
     * Report a crime (anonymous)
     * @param {object} report - Crime report data
     * @returns {Promise}
     */
    async reportCrime(report) {
        return this.request('/reports', {
            method: 'POST',
            body: JSON.stringify(report)
        });
    }

    /**
     * Get safety resources
     * @param {string} category - Optional category filter
     * @returns {Promise}
     */
    async getSafetyResources(category = null) {
        const url = category ? `/resources?category=${category}` : '/resources';
        return this.request(url, {
            method: 'GET'
        });
    }

    // ============ Admin APIs ============

    /**
     * Get admin dashboard stats
     * @returns {Promise}
     */
    async getAdminStats() {
        return this.request('/admin/stats', {
            method: 'GET'
        });
    }

    /**
     * Get all users (admin only)
     * @returns {Promise}
     */
    async getAllUsers() {
        return this.request('/admin/users', {
            method: 'GET'
        });
    }

    /**
     * Get user by ID (admin only)
     * @param {number} userId
     * @returns {Promise}
     */
    async getUserById(userId) {
        return this.request(`/admin/users/${userId}`, {
            method: 'GET'
        });
    }

    /**
     * Update user (admin only)
     * @param {number} userId
     * @param {object} data
     * @returns {Promise}
     */
    async updateUser(userId, data) {
        return this.request(`/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * Delete user (admin only)
     * @param {number} userId
     * @returns {Promise}
     */
    async deleteUser(userId) {
        return this.request(`/admin/users/${userId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Get all SOS alerts (admin only)
     * @returns {Promise}
     */
    async getAllSosAlerts() {
        return this.request('/admin/sos-alerts', {
            method: 'GET'
        });
    }
}

// ============ Create and Export API Instance ============

const api = new ApiClient();

// Make available globally
window.CitizenShieldAPI = api;

// Export for module usage (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
}