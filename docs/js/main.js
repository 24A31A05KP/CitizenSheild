// Main JavaScript file

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('SecureShe loaded');
    
    // Update navigation based on login status
    updateNavigation();
    
    // Initialize SOS button if exists
    const sosButton = document.getElementById('sos-button');
    if (sosButton) {
        sosButton.addEventListener('click', handleSOSClick);
    }
    
    // Initialize share location button if exists
    const shareLocationBtn = document.getElementById('share-location');
    if (shareLocationBtn) {
        shareLocationBtn.addEventListener('click', handleShareLocation);
    }
    
    // Initialize hamburger menu
    const hamburger = document.querySelector('.hamburger');
    if (hamburger) {
        hamburger.addEventListener('click', toggleMobileMenu);
    }
});

// Update navigation based on login status
function updateNavigation() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    // Update login/register links
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        const loginLi = navMenu.querySelector('a[href="pages/login.html"]')?.parentElement;
        const registerLi = navMenu.querySelector('a[href="pages/register.html"]')?.parentElement;
        
        if (token && user) {
            // User is logged in
            if (loginLi) {
                loginLi.innerHTML = '<a href="#" id="logout-link">Logout</a>';
            }
            if (registerLi) {
                registerLi.style.display = 'none';
            }
            
            // Add logout handler
            const logoutLink = document.getElementById('logout-link');
            if (logoutLink) {
                logoutLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    SecureSheAPI.auth.logout();
                });
            }
        } else {
            // User is not logged in
            if (loginLi) {
                loginLi.innerHTML = '<a href="pages/login.html">Login</a>';
            }
            if (registerLi) {
                registerLi.style.display = 'list-item';
                registerLi.innerHTML = '<a href="pages/register.html" class="btn-register">Register</a>';
            }
        }
    }
}

// Handle SOS button click
function handleSOSClick() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        alert('Please login to use SOS feature');
        window.location.href = 'pages/login.html';
        return;
    }
    
    // Show SOS modal
    const modal = document.getElementById('sos-modal');
    if (modal) {
        modal.classList.add('show');
    }
}

// Handle share location
function handleShareLocation() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        alert('Please login to share location');
        window.location.href = 'pages/login.html';
        return;
    }
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                alert(`Location shared: ${position.coords.latitude}, ${position.coords.longitude}`);
                // Here you would send to backend
            },
            (error) => {
                alert('Could not get location: ' + error.message);
            }
        );
    } else {
        alert('Geolocation is not supported by your browser');
    }
}

// Toggle mobile menu
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('active');
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const colors = {
        success: '#d4edda',
        error: '#f8d7da',
        info: '#d1ecf1',
        warning: '#fff3cd'
    };
    
    const textColors = {
        success: '#155724',
        error: '#721c24',
        info: '#0c5460',
        warning: '#856404'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: ${textColors[type]};
        padding: 1rem;
        border-radius: 5px;
        box-shadow: var(--shadow);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .nav-menu.active {
        display: flex !important;
        flex-direction: column;
        position: absolute;
        top: 70px;
        left: 0;
        width: 100%;
        background: white;
        padding: 1rem;
        box-shadow: var(--shadow);
    }
`;
document.head.appendChild(style);