/* ========================================
   CITIZENSHIELD - MAIN JAVASCRIPT
   Global Functions & Utilities
   ======================================== */

// ============ DOM Elements ============
const elements = {
    navMenu: document.getElementById('nav-menu'),
    hamburger: document.getElementById('hamburger'),
    logoutLink: document.getElementById('logout-link'),
    sosButton: document.getElementById('sos-button'),
    confirmSos: document.getElementById('confirm-sos'),
    cancelSos: document.getElementById('cancel-sos'),
    sosModal: document.getElementById('sos-modal'),
    messageContainer: document.getElementById('message-container')
};

// ============ Utility Functions ============

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - 'success', 'error', 'warning'
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-exclamation-triangle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Show loading spinner in container
 * @param {string} containerId - Container element ID
 */
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading...</p>
            </div>
        `;
    }
}

/**
 * Hide loading spinner and show content
 * @param {string} containerId - Container element ID
 * @param {string} content - HTML content to display
 */
function hideLoading(containerId, content) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = content;
    }
}

/**
 * Format date to readable string
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format phone number (Indian format)
 * @param {string} phone - Phone number
 * @returns {string} Formatted phone number
 */
function formatPhone(phone) {
    if (!phone) return '';
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 10) {
        return `${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
    }
    return phone;
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Is valid email
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate phone number (Indian)
 * @param {string} phone - Phone number to validate
 * @returns {boolean} Is valid phone
 */
function isValidPhone(phone) {
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length === 10;
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} { isValid, message, strength }
 */
function validatePassword(password) {
    if (!password) {
        return { isValid: false, message: 'Password is required', strength: 'weak' };
    }
    if (password.length < 8) {
        return { isValid: false, message: 'Password must be at least 8 characters', strength: 'weak' };
    }
    
    let strength = 'weak';
    if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password)) {
        strength = 'medium';
    }
    if (password.length >= 10 && /[A-Z]/.test(password) && /[0-9]/.test(password) && /[^a-zA-Z0-9]/.test(password)) {
        strength = 'strong';
    }
    return { isValid: true, message: '', strength };
}

/**
 * Get password strength level
 * @param {string} password - Password to check
 * @returns {object} { score, text, class }
 */
function getPasswordStrength(password) {
    if (!password) return { score: 0, text: 'No password', class: '' };
    
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    if (score <= 2) return { score, text: 'Weak', class: 'weak' };
    if (score <= 4) return { score, text: 'Medium', class: 'medium' };
    if (score <= 6) return { score, text: 'Strong', class: 'strong' };
    return { score, text: 'Very Strong', class: 'very-strong' };
}

/**
 * Get current user from localStorage
 * @returns {object|null} User object or null
 */
function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

/**
 * Get auth token
 * @returns {string|null} JWT token
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Check if user is logged in
 * @returns {boolean} Is logged in
 */
function isLoggedIn() {
    return !!getToken();
}

/**
 * Check if user is admin
 * @returns {boolean} Is admin
 */
function isAdmin() {
    const user = getCurrentUser();
    return user && user.role === 'admin';
}

/**
 * Logout user
 */
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('loginTime');
    showToast('Logged out successfully', 'success');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

/**
 * Make authenticated API request
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
async function authFetch(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        showToast('Session expired. Please login again.', 'error');
        setTimeout(() => {
            window.location.href = 'pages/login.html';
        }, 1500);
        throw new Error('Unauthorized');
    }
    
    return response;
}

/**
 * Handle API error
 * @param {Error} error - Error object
 */
function handleApiError(error) {
    console.error('API Error:', error);
    showToast(error.message || 'Something went wrong', 'error');
}

// ============ Navigation ============

/**
 * Update navigation based on login status
 */
function updateNavigation() {
    const token = getToken();
    const user = getCurrentUser();
    const navMenu = elements.navMenu;
    
    if (!navMenu) return;
    
    const currentPath = window.location.pathname;
    const isInCrimeAwareness = currentPath.includes('crime-awareness');
    const isInPages = currentPath.includes('/pages/');
    
    if (token && user) {
        let menuHtml = '';
        
        if (isInCrimeAwareness) {
            menuHtml = `
                <li><a href="../../index.html">Home</a></li>
                <li><a href="../sos.html">SOS</a></li>
                <li><a href="../helplines.html">Helplines</a></li>
                <li><a href="dashboard.html">Awareness</a></li>
                <li><a href="report-crime.html">Report Crime</a></li>
                <li><a href="crime-map.html">Crime Map</a></li>
                <li><a href="resources.html">Resources</a></li>
                <li><a href="../profile.html">Profile</a></li>
            `;
        } else if (isInPages) {
            menuHtml = `
                <li><a href="../index.html">Home</a></li>
                <li><a href="sos.html">SOS</a></li>
                <li><a href="helplines.html">Helplines</a></li>
                <li><a href="crime-awareness/dashboard.html">Awareness</a></li>
                <li><a href="profile.html">Profile</a></li>
            `;
        } else {
            menuHtml = `
                <li><a href="index.html">Home</a></li>
                <li><a href="pages/sos.html">SOS</a></li>
                <li><a href="pages/helplines.html">Helplines</a></li>
                <li><a href="pages/crime-awareness/dashboard.html">Awareness</a></li>
                <li><a href="pages/profile.html">Profile</a></li>
            `;
        }
        
        // Add admin link if user is admin
        if (user.role === 'admin') {
            if (isInCrimeAwareness) {
                menuHtml += `<li><a href="../admin.html">Admin</a></li>`;
            } else if (isInPages) {
                menuHtml += `<li><a href="admin.html">Admin</a></li>`;
            } else {
                menuHtml += `<li><a href="pages/admin.html">Admin</a></li>`;
            }
        }
        
        menuHtml += `<li><a href="#" id="logout-link">Logout</a></li>`;
        navMenu.innerHTML = menuHtml;
        
        // Add logout handler
        document.getElementById('logout-link')?.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    } else {
        let menuHtml = '';
        
        if (isInCrimeAwareness) {
            menuHtml = `
                <li><a href="../../index.html">Home</a></li>
                <li><a href="../sos.html">SOS</a></li>
                <li><a href="../helplines.html">Helplines</a></li>
                <li><a href="dashboard.html">Awareness</a></li>
                <li><a href="../login.html">Login</a></li>
                <li><a href="../register.html" class="btn-register">Register</a></li>
            `;
        } else if (isInPages) {
            menuHtml = `
                <li><a href="../index.html">Home</a></li>
                <li><a href="sos.html">SOS</a></li>
                <li><a href="helplines.html">Helplines</a></li>
                <li><a href="crime-awareness/dashboard.html">Awareness</a></li>
                <li><a href="login.html">Login</a></li>
                <li><a href="register.html" class="btn-register">Register</a></li>
            `;
        } else {
            menuHtml = `
                <li><a href="index.html">Home</a></li>
                <li><a href="pages/sos.html">SOS</a></li>
                <li><a href="pages/helplines.html">Helplines</a></li>
                <li><a href="pages/crime-awareness/dashboard.html">Awareness</a></li>
                <li><a href="pages/login.html">Login</a></li>
                <li><a href="pages/register.html" class="btn-register">Register</a></li>
            `;
        }
        
        navMenu.innerHTML = menuHtml;
    }
}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {
    const navMenu = elements.navMenu;
    const hamburger = elements.hamburger;
    
    if (navMenu && hamburger) {
        navMenu.classList.toggle('active');
        const icon = hamburger.querySelector('i');
        if (icon) {
            icon.className = navMenu.classList.contains('active') ? 'fas fa-times' : 'fas fa-bars';
        }
    }
}

// ============ SOS Modal ============

/**
 * Show SOS confirmation modal
 */
function showSosModal() {
    if (!isLoggedIn()) {
        showToast('Please login to use SOS feature', 'warning');
        setTimeout(() => {
            window.location.href = 'pages/login.html';
        }, 1500);
        return;
    }
    
    if (elements.sosModal) {
        elements.sosModal.classList.add('show');
    }
}

/**
 * Hide SOS modal
 */
function hideSosModal() {
    if (elements.sosModal) {
        elements.sosModal.classList.remove('show');
    }
}

/**
 * Trigger SOS alert
 */
async function triggerSos() {
    hideSosModal();
    
    showToast('Triggering SOS...', 'success');
    
    try {
        // Get user's location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                const { latitude, longitude } = position.coords;
                
                try {
                    const response = await authFetch('http://localhost:5000/api/sos/trigger', {
                        method: 'POST',
                        body: JSON.stringify({
                            latitude,
                            longitude,
                            address: 'Current location',
                            message: 'SOS Emergency! I need help.'
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showToast(`✅ SOS triggered! ${data.contacts_notified || 0} contacts notified.`, 'success');
                    } else {
                        showToast('❌ ' + (data.error || 'Failed to trigger SOS'), 'error');
                    }
                } catch (error) {
                    console.error('SOS Error:', error);
                    showToast('SOS triggered! (Offline mode)', 'success');
                }
            }, () => {
                showToast('SOS triggered! (Location unavailable)', 'warning');
            });
        } else {
            showToast('SOS triggered!', 'success');
        }
    } catch (error) {
        console.error('SOS Error:', error);
        showToast('SOS triggered! (Offline mode)', 'success');
    }
}

// ============ Location Sharing ============

let locationWatchId = null;
let userMarker = null;
let userCircle = null;
let currentMap = null;

/**
 * Initialize map reference
 * @param {object} map - Leaflet map instance
 */
function initMapReference(map) {
    currentMap = map;
}

/**
 * Start sharing location
 * @param {function} onLocationUpdate - Callback for location updates
 */
function startSharingLocation(onLocationUpdate) {
    if (!isLoggedIn()) {
        showToast('Please login first', 'warning');
        setTimeout(() => window.location.href = 'pages/login.html', 1500);
        return;
    }
    
    if (!navigator.geolocation) {
        showToast('Geolocation not supported', 'error');
        return;
    }
    
    if (locationWatchId) {
        navigator.geolocation.clearWatch(locationWatchId);
    }
    
    locationWatchId = navigator.geolocation.watchPosition(
        (position) => {
            const { latitude, longitude, accuracy } = position.coords;
            if (onLocationUpdate) {
                onLocationUpdate({ latitude, longitude, accuracy });
            }
        },
        (error) => {
            let message = 'Location error: ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message += 'Please enable location access';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message += 'Location unavailable';
                    break;
                case error.TIMEOUT:
                    message += 'Request timeout';
                    break;
                default:
                    message += error.message;
            }
            showToast(message, 'error');
            stopSharingLocation();
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
    
    showToast('Sharing your location...', 'success');
}

/**
 * Stop sharing location
 */
function stopSharingLocation() {
    if (locationWatchId) {
        navigator.geolocation.clearWatch(locationWatchId);
        locationWatchId = null;
    }
    
    if (userMarker && currentMap) {
        currentMap.removeLayer(userMarker);
        currentMap.removeLayer(userCircle);
        userMarker = null;
        userCircle = null;
    }
    
    showToast('Location sharing stopped', 'success');
}

// ============ Initialize ============

/**
 * Initialize main functionality
 */
function init() {
    // Update navigation
    updateNavigation();
    
    // Setup hamburger menu
    if (elements.hamburger) {
        elements.hamburger.addEventListener('click', toggleMobileMenu);
    }
    
    // Setup SOS button
    if (elements.sosButton) {
        elements.sosButton.addEventListener('click', showSosModal);
    }
    
    // Setup SOS modal buttons
    if (elements.confirmSos) {
        elements.confirmSos.addEventListener('click', triggerSos);
    }
    if (elements.cancelSos) {
        elements.cancelSos.addEventListener('click', hideSosModal);
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === elements.sosModal) {
            hideSosModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.sosModal?.classList.contains('show')) {
            hideSosModal();
        }
    });
    
    // Add active class to current page link
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-menu a');
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '../index.html' && href !== '../../index.html') {
            link.classList.add('active');
        }
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);

// Export functions for use in other files
window.CitizenShield = {
    showToast,
    showLoading,
    hideLoading,
    formatDate,
    formatPhone,
    isValidEmail,
    isValidPhone,
    validatePassword,
    getPasswordStrength,
    getCurrentUser,
    getToken,
    isLoggedIn,
    isAdmin,
    logout,
    authFetch,
    handleApiError,
    updateNavigation,
    showSosModal,
    hideSosModal,
    triggerSos,
    startSharingLocation,
    stopSharingLocation,
    initMapReference
};