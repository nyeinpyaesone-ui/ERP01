// ERP01 Web Interface JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

function initApp() {
    // Setup mobile menu toggle
    setupMobileMenu();
    
    // Load dynamic data
    loadModuleStatus();
    
    // Setup navigation
    setupNavigation();
}

function setupMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }
}

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(function(item) {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all items
            navItems.forEach(function(navItem) {
                navItem.classList.remove('active');
            });
            
            // Add active class to clicked item
            this.classList.add('active');
        });
    });
}

async function loadModuleStatus() {
    try {
        const response = await fetch('/api/modules');
        const data = await response.json();
        
        updateModulesGrid(data.modules);
    } catch (error) {
        console.error('Error loading module status:', error);
    }
}

function updateModulesGrid(modules) {
    const modulesGrid = document.getElementById('modulesGrid');
    
    if (!modulesGrid) return;
    
    modulesGrid.innerHTML = '';
    
    modules.forEach(function(module) {
        const moduleCard = document.createElement('div');
        const statusClass = module.status === 'active' ? 'status-active' : 'status-pending';
        
        moduleCard.className = `module-card ${statusClass}`;
        moduleCard.innerHTML = `
            <h4>${module.name}</h4>
            <span class="status-badge">${capitalizeFirstLetter(module.status)}</span>
        `;
        
        modulesGrid.appendChild(moduleCard);
    });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Utility function for API calls
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(endpoint, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.classList.add('notification-show');
    }, 100);
    
    setTimeout(function() {
        notification.classList.remove('notification-show');
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 3000);
}
