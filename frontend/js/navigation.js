// ============================================
// CitizenShield - Shared Navigation
// Handles dynamic menu updates and authentication
// ============================================

/**
 * Update navigation menu based on login status and user role
 */
function updateNavigation() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const navMenu = document.getElementById('nav-menu');
    
    if (!navMenu) return;
    
    // Get current page path to determine active class
    const currentPath = window.location.pathname;
    const isInCrimeAwareness = currentPath.includes('crime-awareness');
    const isInPages = currentPath.includes('/pages/');
    
    if (token && user) {
        // Logged in menu - ONLY these pages: Home, SOS, Helplines, Awareness, Profile, Admin, Logout
        let menuHtml = '';
        
        if (isInCrimeAwareness) {
            menuHtml += `<li><a href="../../index.html">Home</a></li>`;
            menuHtml += `<li><a href="../sos.html">SOS</a></li>`;
            menuHtml += `<li><a href="../helplines.html">Helplines</a></li>`;
            menuHtml += `<li><a href="dashboard.html" class="${currentPath.includes('dashboard.html') ? 'active' : ''}">Awareness</a></li>`;
            menuHtml += `<li><a href="../profile.html">Profile</a></li>`;
        } else if (isInPages) {
            menuHtml += `<li><a href="../index.html">Home</a></li>`;
            menuHtml += `<li><a href="sos.html" class="${currentPath.includes('sos.html') ? 'active' : ''}">SOS</a></li>`;
            menuHtml += `<li><a href="helplines.html" class="${currentPath.includes('helplines.html') ? 'active' : ''}">Helplines</a></li>`;
            menuHtml += `<li><a href="crime-awareness/dashboard.html">Awareness</a></li>`;
            menuHtml += `<li><a href="profile.html" class="${currentPath.includes('profile.html') ? 'active' : ''}">Profile</a></li>`;
        } else {
            menuHtml += `<li><a href="index.html" class="${currentPath.endsWith('index.html') || currentPath.endsWith('/') ? 'active' : ''}">Home</a></li>`;
            menuHtml += `<li><a href="pages/sos.html">SOS</a></li>`;
            menuHtml += `<li><a href="pages/helplines.html">Helplines</a></li>`;
            menuHtml += `<li><a href="pages/crime-awareness/dashboard.html">Awareness</a></li>`;
            menuHtml += `<li><a href="pages/profile.html">Profile</a></li>`;
        }
        
        // Add admin link if user is admin
        if (user.role === 'admin') {
            if (isInCrimeAwareness) {
                menuHtml += `<li><a href="../admin.html">Admin</a></li>`;
            } else if (isInPages) {
                menuHtml += `<li><a href="admin.html" class="${currentPath.includes('admin.html') ? 'active' : ''}">Admin</a></li>`;
            } else {
                menuHtml += `<li><a href="pages/admin.html">Admin</a></li>`;
            }
        }
        
        // Add logout button
        menuHtml += `<li><a href="#" id="logout-link">Logout</a></li>`;
        navMenu.innerHTML = menuHtml;
        
        // Add logout handler
        const logoutLink = document.getElementById('logout-link');
        if (logoutLink) {
            logoutLink.addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                // Redirect based on current location
                if (window.location.pathname.includes('crime-awareness')) {
                    window.location.href = '../../index.html';
                } else if (window.location.pathname.includes('/pages/')) {
                    window.location.href = '../index.html';
                } else {
                    window.location.href = 'index.html';
                }
            });
        }
    } else {
        // Logged out menu - ONLY these pages: Home, SOS, Helplines, Awareness, Login, Register
        let menuHtml = '';
        
        if (isInCrimeAwareness) {
            menuHtml += `<li><a href="../../index.html">Home</a></li>`;
            menuHtml += `<li><a href="../sos.html">SOS</a></li>`;
            menuHtml += `<li><a href="../helplines.html">Helplines</a></li>`;
            menuHtml += `<li><a href="dashboard.html">Awareness</a></li>`;
            menuHtml += `<li><a href="../login.html">Login</a></li>`;
            menuHtml += `<li><a href="../register.html" class="btn-register">Register</a></li>`;
        } else if (isInPages) {
            menuHtml += `<li><a href="../index.html">Home</a></li>`;
            menuHtml += `<li><a href="sos.html">SOS</a></li>`;
            menuHtml += `<li><a href="helplines.html">Helplines</a></li>`;
            menuHtml += `<li><a href="crime-awareness/dashboard.html">Awareness</a></li>`;
            menuHtml += `<li><a href="login.html">Login</a></li>`;
            menuHtml += `<li><a href="register.html" class="btn-register">Register</a></li>`;
        } else {
            menuHtml += `<li><a href="index.html" class="active">Home</a></li>`;
            menuHtml += `<li><a href="pages/sos.html">SOS</a></li>`;
            menuHtml += `<li><a href="pages/helplines.html">Helplines</a></li>`;
            menuHtml += `<li><a href="pages/crime-awareness/dashboard.html">Awareness</a></li>`;
            menuHtml += `<li><a href="pages/login.html">Login</a></li>`;
            menuHtml += `<li><a href="pages/register.html" class="btn-register">Register</a></li>`;
        }
        
        navMenu.innerHTML = menuHtml;
    }
}

/**
 * Check if user is logged in
 * @returns {boolean}
 */
function isLoggedIn() {
    return !!localStorage.getItem('token');
}

/**
 * Get current user from localStorage
 * @returns {object|null}
 */
function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

/**
 * Check if current user is admin
 * @returns {boolean}
 */
function isAdmin() {
    const user = getCurrentUser();
    return user && user.role === 'admin';
}

/**
 * Check if user is authenticated for protected pages
 * @returns {boolean}
 */
function checkAuth() {
    const token = localStorage.getItem('token');
    const protectedPages = ['profile.html', 'sos.html', 'helplines.html', 'admin.html', 'report-crime.html', 'crime-map.html', 'resources.html'];
    const currentPage = window.location.pathname;
    
    if (!token) {
        for (const page of protectedPages) {
            if (currentPage.includes(page)) {
                // Redirect based on current location
                if (currentPage.includes('crime-awareness')) {
                    window.location.href = '../login.html';
                } else if (currentPage.includes('/pages/')) {
                    window.location.href = 'login.html';
                } else {
                    window.location.href = 'pages/login.html';
                }
                return false;
            }
        }
    }
    return true;
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - 'success', 'error', 'warning'
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-exclamation-triangle'}"></i> ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Format date to readable string
 * @param {string} dateString - ISO date string
 * @returns {string}
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
 * Format phone number
 * @param {string} phone - Phone number
 * @returns {string}
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
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate phone number (Indian)
 * @param {string} phone
 * @returns {boolean}
 */
function isValidPhone(phone) {
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length === 10;
}

/**
 * Get password strength
 * @param {string} password
 * @returns {object}
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
 * Make authenticated API request
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise}
 */
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('token');
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
            window.location.href = 'login.html';
        }, 1500);
        throw new Error('Unauthorized');
    }
    
    return response;
}

/**
 * Handle API error
 * @param {Error} error
 */
function handleApiError(error) {
    console.error('API Error:', error);
    showToast(error.message || 'Something went wrong', 'error');
}

// Initialize navigation on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    updateNavigation();
    
    // Add active class to current page link (fallback for dynamic content)
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-menu a');
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '../index.html' && href !== '../../index.html') {
            link.classList.add('active');
        }
    });
});