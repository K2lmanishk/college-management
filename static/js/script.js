/**
 * ============================================
 * COLLEGE MANAGEMENT SYSTEM - ULTRA ADVANCED JS
 * Version: 3.0 Professional
 * Features: AI Assistant, Voice Commands, Real-time Updates,
 *           Advanced Animations, Charts, Export Tools,
 *           Gesture Controls, Keyboard Shortcuts, PWA
 * ============================================
 */

// ============================================
// GLOBAL VARIABLES & CONFIGURATION
// ============================================

const CONFIG = {
    appName: 'College Management System',
    version: '3.0.0',
    apiBaseUrl: '/api',
    refreshInterval: 30000,
    animationDuration: 400,
    toastDuration: 4000,
    enableVoiceCommands: true,
    enableGestures: true,
    enableAutoSave: true,
    enableRealTimeUpdates: true
};

let notificationCheckInterval;
let autoSaveInterval;
let charts = {};
let voiceRecognition = null;
let isListening = false;
let currentUser = null;
let sidebarState = true;
let lastActivity = Date.now();
let pendingRequests = new Map();
let offlineQueue = [];
let socket = null;

// ============================================
// INITIALIZATION - DOM READY
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log(`🚀 ${CONFIG.appName} v${CONFIG.version} Initializing...`);
    
    initializeAll();
    detectUserActivity();
    loadUserPreferences();
    initializeWebSocket();
    setupOfflineSupport();
    registerServiceWorker();
    
    // Welcome message with delay
    setTimeout(() => {
        showWelcomeSequence();
    }, 500);
});

function initializeAll() {
    initBootstrapComponents();
    initTooltips();
    initPopovers();
    initGSAPAnimations();
    initApexCharts();
    initParticles();
    initVoiceCommands();
    initGestureControls();
    initKeyboardShortcuts();
    initDragAndDrop();
    initInfiniteScroll();
    initLazyLoading();
    autoHideAlerts();
    setupDateDefaults();
    loadNotifications();
    startIntervals();
    setupFormValidation();
    initThemeManager();
}

// ============================================
// WELCOME SEQUENCE
// ============================================

function showWelcomeSequence() {
    const hour = new Date().getHours();
    let greeting = hour < 12 ? 'Good Morning' : hour < 17 ? 'Good Afternoon' : 'Good Evening';
    
    showToast(`${greeting}! Welcome to ${CONFIG.appName}`, 'success', 5000);
    
    // Animated welcome
    gsap.from('.welcome-text', {
        duration: 1,
        y: 50,
        opacity: 0,
        ease: 'elastic.out(1, 0.3)',
        stagger: 0.1
    });
    
    // Confetti on first load of day
    const lastVisit = localStorage.getItem('lastVisit');
    const today = new Date().toDateString();
    if (lastVisit !== today) {
        setTimeout(() => celebrate(), 1000);
        localStorage.setItem('lastVisit', today);
    }
}

// ============================================
// BOOTSTRAP COMPONENTS
// ============================================

function initBootstrapComponents() {
    // Initialize all tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        new bootstrap.Tooltip(el, {
            animation: true,
            delay: { show: 200, hide: 100 },
            trigger: 'hover focus'
        });
    });
    
    // Initialize all popovers
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
        new bootstrap.Popover(el, {
            animation: true,
            trigger: 'click',
            html: true
        });
    });
    
    // Initialize dropdowns
    document.querySelectorAll('.dropdown-toggle').forEach(el => {
        new bootstrap.Dropdown(el);
    });
}

function initTooltips() {
    // Dynamic tooltips
    document.addEventListener('mouseover', (e) => {
        const target = e.target.closest('[data-tooltip]');
        if (target && !target._tooltip) {
            target._tooltip = new bootstrap.Tooltip(target, {
                title: target.dataset.tooltip,
                placement: target.dataset.placement || 'top'
            });
        }
    });
}

function initPopovers() {
    // Dynamic popovers
    document.addEventListener('click', (e) => {
        const target = e.target.closest('[data-popover]');
        if (target && !target._popover) {
            target._popover = new bootstrap.Popover(target, {
                content: target.dataset.popover,
                html: true,
                trigger: 'focus'
            });
            target._popover.show();
        }
    });
}

// ============================================
// GSAP ADVANCED ANIMATIONS
// ============================================

function initGSAPAnimations() {
    gsap.registerPlugin(ScrollTrigger, TextPlugin, MotionPathPlugin);
    
    // Animate stat cards on scroll
    gsap.from('.stat-card', {
        scrollTrigger: {
            trigger: '.stat-card',
            start: 'top 85%',
            toggleActions: 'play none none reverse'
        },
        y: 60,
        opacity: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: 'back.out(1.7)'
    });
    
    // Animate cards
    gsap.from('.card:not(.stat-card)', {
        scrollTrigger: {
            trigger: '.card',
            start: 'top 90%',
            toggleActions: 'play none none reverse'
        },
        y: 40,
        opacity: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: 'power2.out'
    });
    
    // Animate table rows
    gsap.from('tbody tr', {
        scrollTrigger: {
            trigger: 'table',
            start: 'top 85%'
        },
        x: -30,
        opacity: 0,
        duration: 0.4,
        stagger: 0.05,
        ease: 'power2.out'
    });
    
    // Parallax effect on hero sections
    gsap.to('.parallax-bg', {
        scrollTrigger: {
            trigger: '.parallax-container',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        },
        y: 200,
        scale: 1.1
    });
    
    // Sticky sidebar animation
    ScrollTrigger.create({
        trigger: '.sidebar',
        start: 'top top',
        endTrigger: 'footer',
        end: 'bottom top',
        pin: true,
        pinSpacing: false
    });
    
    // Counter animations
    document.querySelectorAll('.counter-value').forEach(el => {
        const target = parseInt(el.dataset.target);
        gsap.to(el, {
            innerText: target,
            duration: 2,
            snap: { innerText: 1 },
            scrollTrigger: {
                trigger: el,
                start: 'top 90%'
            },
            ease: 'power2.out'
        });
    });
}

// ============================================
// APEXCHARTS - ADVANCED CHARTS
// ============================================

function initApexCharts() {
    // Default chart theme
    Apex.chart = {
        fontFamily: 'Inter, Poppins, sans-serif',
        background: 'transparent'
    };
}

function createChart(elementId, type, labels, series, title, options = {}) {
    const element = document.getElementById(elementId);
    if (!element) return null;
    
    const defaultOptions = {
        series: Array.isArray(series) ? series : [{ name: title, data: series }],
        chart: {
            type: type,
            height: options.height || 350,
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800,
                animateGradually: {
                    enabled: true,
                    delay: 150
                },
                dynamicAnimation: {
                    enabled: true,
                    speed: 350
                }
            },
            toolbar: {
                show: true,
                tools: {
                    download: true,
                    selection: true,
                    zoom: true,
                    zoomin: true,
                    zoomout: true,
                    pan: true,
                    reset: true
                },
                export: {
                    csv: { filename: title },
                    svg: { filename: title },
                    png: { filename: title }
                }
            },
            background: 'transparent',
            zoom: { enabled: true }
        },
        title: {
            text: title,
            align: 'center',
            style: {
                fontSize: '16px',
                fontWeight: 'bold',
                color: document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#fff' : '#1a1a2e'
            }
        },
        theme: {
            mode: document.documentElement.getAttribute('data-bs-theme') || 'light',
            palette: 'palette1'
        },
        stroke: {
            curve: 'smooth',
            width: 3,
            lineCap: 'round'
        },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.7,
                opacityTo: 0.9,
                stops: [0, 90, 100]
            }
        },
        markers: {
            size: 5,
            hover: { size: 8 }
        },
        tooltip: {
            theme: 'dark',
            x: { show: true },
            y: { formatter: (val) => val.toLocaleString() }
        },
        legend: {
            position: 'bottom',
            horizontalAlign: 'center',
            floating: false,
            fontSize: '13px',
            markers: { radius: 12 }
        },
        grid: {
            borderColor: '#e0e0e0',
            strokeDashArray: 5,
            xaxis: { lines: { show: true } }
        },
        xaxis: {
            categories: labels,
            labels: { style: { fontSize: '12px' } }
        },
        responsive: [{
            breakpoint: 768,
            options: {
                chart: { height: 300 },
                legend: { position: 'bottom' }
            }
        }]
    };
    
    const chartOptions = { ...defaultOptions, ...options };
    
    if (charts[elementId]) {
        charts[elementId].destroy();
    }
    
    charts[elementId] = new ApexCharts(element, chartOptions);
    charts[elementId].render();
    
    return charts[elementId];
}

function updateChart(chartId, series, categories) {
    if (charts[chartId]) {
        charts[chartId].updateSeries(series);
        if (categories) {
            charts[chartId].updateOptions({ xaxis: { categories: categories } });
        }
    }
}

function exportChart(chartId, format = 'png') {
    if (charts[chartId]) {
        charts[chartId].dataURI().then((uri) => {
            const link = document.createElement('a');
            link.href = format === 'svg' ? uri.svgURI : uri.imgURI;
            link.download = `${chartId}.${format}`;
            link.click();
            showToast(`Chart exported as ${format.toUpperCase()}`, 'success');
        });
    }
}

function toggleChartTheme() {
    const theme = document.documentElement.getAttribute('data-bs-theme');
    Object.values(charts).forEach(chart => {
        chart.updateOptions({ theme: { mode: theme } });
    });
}

// ============================================
// PARTICLES.JS BACKGROUND
// ============================================

function initParticles() {
    if (typeof particlesJS === 'undefined') return;
    
    particlesJS('particles-js', {
        particles: {
            number: { value: 50, density: { enable: true, value_area: 800 } },
            color: { value: ['#667eea', '#764ba2', '#f093fb', '#4facfe'] },
            shape: { 
                type: ['circle', 'triangle', 'edge'],
                stroke: { width: 0, color: '#000000' }
            },
            opacity: { 
                value: 0.4, 
                random: true,
                anim: { enable: true, speed: 1, opacity_min: 0.1, sync: false }
            },
            size: { 
                value: 3, 
                random: true,
                anim: { enable: true, speed: 2, size_min: 0.1, sync: false }
            },
            line_linked: { 
                enable: true, 
                distance: 150, 
                color: '#667eea', 
                opacity: 0.2, 
                width: 1 
            },
            move: { 
                enable: true, 
                speed: 2, 
                direction: 'none', 
                random: true,
                straight: false,
                out_mode: 'out',
                bounce: false,
                attract: { enable: true, rotateX: 600, rotateY: 1200 }
            }
        },
        interactivity: {
            detect_on: 'canvas',
            events: { 
                onhover: { enable: true, mode: 'grab' }, 
                onclick: { enable: true, mode: 'push' },
                resize: true
            },
            modes: { 
                grab: { distance: 200, line_linked: { opacity: 0.5 } },
                push: { particles_nb: 4 },
                remove: { particles_nb: 2 },
                repulse: { distance: 200, duration: 0.4 }
            }
        },
        retina_detect: true
    });
}

// ============================================
// VOICE COMMANDS (AI ASSISTANT)
// ============================================

function initVoiceCommands() {
    if (!CONFIG.enableVoiceCommands) return;
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    
    voiceRecognition = new SpeechRecognition();
    voiceRecognition.continuous = false;
    voiceRecognition.interimResults = false;
    voiceRecognition.lang = 'en-US';
    
    voiceRecognition.onstart = () => {
        isListening = true;
        showToast('🎤 Listening... Speak now', 'info', 2000);
        document.querySelector('.voice-indicator')?.classList.add('active');
    };
    
    voiceRecognition.onend = () => {
        isListening = false;
        document.querySelector('.voice-indicator')?.classList.remove('active');
    };
    
    voiceRecognition.onerror = (e) => {
        console.error('Voice recognition error:', e);
        showToast('Voice recognition failed', 'danger');
    };
    
    voiceRecognition.onresult = (e) => {
        const command = e.results[0][0].transcript.toLowerCase().trim();
        processVoiceCommand(command);
    };
    
    // Voice command button
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'm') {
            e.preventDefault();
            startVoiceRecognition();
        }
    });
}

function startVoiceRecognition() {
    if (voiceRecognition && !isListening) {
        voiceRecognition.start();
    }
}

function processVoiceCommand(command) {
    console.log('🎤 Voice command:', command);
    
    const commands = {
        dashboard: () => navigateTo(getDashboardUrl()),
        'go to dashboard': () => navigateTo(getDashboardUrl()),
        profile: () => navigateTo('/profile'),
        'my profile': () => navigateTo('/profile'),
        settings: () => navigateTo('/settings'),
        students: () => navigateTo('/admin/users'),
        faculty: () => navigateTo('/admin/users'),
        programs: () => navigateTo('/admin/programs'),
        subjects: () => navigateTo('/admin/subjects'),
        attendance: () => navigateTo('/faculty/attendance'),
        marks: () => navigateTo('/faculty/marks'),
        fees: () => navigateTo('/student/fees'),
        timetable: () => navigateTo('/student/timetable'),
        logout: () => window.location.href = '/logout',
        'log out': () => window.location.href = '/logout',
        refresh: () => location.reload(),
        'dark mode': () => toggleTheme(),
        'light mode': () => toggleTheme(),
        search: () => document.getElementById('globalSearch')?.focus(),
        help: () => showHelpModal(),
        'show notifications': () => document.getElementById('notificationDropdownBtn')?.click(),
        'mark all read': () => markAllNotificationsRead(),
        'create new': () => document.querySelector('[data-action="create"]')?.click(),
        save: () => document.querySelector('form button[type="submit"]')?.click(),
        cancel: () => document.querySelector('[data-dismiss="modal"]')?.click()
    };
    
    for (const [phrase, action] of Object.entries(commands)) {
        if (command.includes(phrase)) {
            action();
            showToast(`Executing: ${phrase}`, 'success');
            celebrate();
            return;
        }
    }
    
    // Navigate to page if mentioned
    if (command.includes('go to') || command.includes('open') || command.includes('show')) {
        const page = command.replace(/go to|open|show/gi, '').trim();
        if (page.includes('student')) navigateTo('/admin/users');
        else if (page.includes('faculty')) navigateTo('/admin/users');
        else if (page.includes('program')) navigateTo('/admin/programs');
        else showToast(`Unknown page: ${page}`, 'warning');
    } else {
        showToast(`Command not recognized: "${command}"`, 'warning');
    }
}

function navigateTo(url) {
    if (url && url !== '#') {
        window.location.href = url;
    }
}

function getDashboardUrl() {
    const role = document.querySelector('.role-badge')?.textContent.toLowerCase() || '';
    if (role.includes('admin')) return '/admin/dashboard';
    if (role.includes('faculty')) return '/faculty/dashboard';
    return '/student/dashboard';
}

// ============================================
// GESTURE CONTROLS
// ============================================

function initGestureControls() {
    if (!CONFIG.enableGestures) return;
    
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    
    document.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    });
    
    document.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleGesture();
    });
    
    function handleGesture() {
        const dx = touchEndX - touchStartX;
        const dy = touchEndY - touchStartY;
        
        if (Math.abs(dx) > Math.abs(dy)) {
            // Horizontal swipe
            if (Math.abs(dx) > 100) {
                if (dx > 0) {
                    // Swipe right - open sidebar
                    document.getElementById('sidebar')?.classList.add('show');
                    showToast('Sidebar opened', 'info');
                } else {
                    // Swipe left - close sidebar
                    document.getElementById('sidebar')?.classList.remove('show');
                }
            }
        } else {
            // Vertical swipe
            if (Math.abs(dy) > 150) {
                if (dy > 0) {
                    // Swipe down - refresh
                    showToast('Pull to refresh', 'info');
                } else {
                    // Swipe up - scroll to top
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            }
        }
    }
    
    // Pinch to zoom
    let initialDistance = 0;
    
    document.addEventListener('touchstart', (e) => {
        if (e.touches.length === 2) {
            initialDistance = Math.hypot(
                e.touches[0].pageX - e.touches[1].pageX,
                e.touches[0].pageY - e.touches[1].pageY
            );
        }
    });
    
    document.addEventListener('touchmove', (e) => {
        if (e.touches.length === 2 && initialDistance) {
            e.preventDefault();
            const distance = Math.hypot(
                e.touches[0].pageX - e.touches[1].pageX,
                e.touches[0].pageY - e.touches[1].pageY
            );
            const scale = distance / initialDistance;
            document.body.style.transform = `scale(${Math.min(1.5, Math.max(0.8, scale))})`;
        }
    });
    
    document.addEventListener('touchend', () => {
        document.body.style.transform = '';
        initialDistance = 0;
    });
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ignore if typing in input
        if (e.target.matches('input, textarea, select, [contenteditable]')) return;
        
        const key = e.key.toLowerCase();
        const ctrl = e.ctrlKey || e.metaKey;
        const alt = e.altKey;
        const shift = e.shiftKey;
        
        // Global shortcuts
        if (ctrl && key === 'k') {
            e.preventDefault();
            document.getElementById('globalSearch')?.focus();
        } else if (ctrl && key === 'd') {
            e.preventDefault();
            navigateTo(getDashboardUrl());
        } else if (ctrl && key === 'p') {
            e.preventDefault();
            navigateTo('/profile');
        } else if (ctrl && key === '/') {
            e.preventDefault();
            showKeyboardShortcutsModal();
        } else if (ctrl && key === 'm') {
            e.preventDefault();
            startVoiceRecognition();
        } else if (ctrl && key === 'n') {
            e.preventDefault();
            document.querySelector('[data-action="create"]')?.click();
        } else if (ctrl && key === 's') {
            e.preventDefault();
            document.querySelector('form')?.requestSubmit();
        } else if (key === 'escape') {
            closeAllModals();
            document.getElementById('globalSearch').value = '';
            document.getElementById('globalSearch')?.blur();
        } else if (ctrl && shift && key === 't') {
            e.preventDefault();
            toggleTheme();
        } else if (ctrl && key === 'f') {
            e.preventDefault();
            toggleFullscreen();
        } else if (ctrl && key === 'r') {
            e.preventDefault();
            location.reload();
        } else if (alt && key === '1') {
            e.preventDefault();
            navigateTo('/admin/dashboard');
        } else if (alt && key === '2') {
            e.preventDefault();
            navigateTo('/admin/users');
        } else if (alt && key === '3') {
            e.preventDefault();
            navigateTo('/admin/programs');
        }
        
        // Update last activity
        lastActivity = Date.now();
    });
}

function showKeyboardShortcutsModal() {
    const shortcuts = [
        ['Ctrl + D', 'Go to Dashboard'],
        ['Ctrl + P', 'Go to Profile'],
        ['Ctrl + K', 'Focus Search'],
        ['Ctrl + M', 'Voice Command'],
        ['Ctrl + N', 'Create New'],
        ['Ctrl + S', 'Save Form'],
        ['Ctrl + F', 'Toggle Fullscreen'],
        ['Ctrl + Shift + T', 'Toggle Theme'],
        ['Ctrl + /', 'Show Shortcuts'],
        ['Esc', 'Close Modals'],
        ['Alt + 1', 'Admin Dashboard'],
        ['Alt + 2', 'Manage Users'],
        ['Alt + 3', 'Manage Programs']
    ];
    
    let html = '<table class="table table-sm">';
    shortcuts.forEach(([key, desc]) => {
        html += `<tr><th><kbd>${key}</kbd></th><td>${desc}</td></tr>`;
    });
    html += '</table>';
    
    Swal.fire({
        title: '⌨️ Keyboard Shortcuts',
        html: html,
        icon: 'info',
        confirmButtonText: 'Got it!',
        background: document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#1a1a2e' : '#fff',
        color: document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#fff' : '#1a1a2e'
    });
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
        showToast('Fullscreen mode enabled', 'success');
    } else {
        document.exitFullscreen();
        showToast('Fullscreen mode disabled', 'info');
    }
}

function closeAllModals() {
    document.querySelectorAll('.modal.show').forEach(modal => {
        bootstrap.Modal.getInstance(modal)?.hide();
    });
    document.querySelectorAll('.dropdown-menu.show').forEach(dropdown => {
        bootstrap.Dropdown.getInstance(dropdown.previousElementSibling)?.hide();
    });
}

// ============================================
// DRAG AND DROP
// ============================================

function initDragAndDrop() {
    // File upload drag and drop
    document.querySelectorAll('.dropzone').forEach(dropzone => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => {
                dropzone.classList.add('drag-active');
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => {
                dropzone.classList.remove('drag-active');
            });
        });
        
        dropzone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            handleFileUpload(files, dropzone);
        });
    });
    
    // Sortable tables
    document.querySelectorAll('.sortable-table tbody').forEach(tbody => {
        new Sortable(tbody, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            onEnd: function() {
                showToast('Order updated', 'success');
            }
        });
    });
    
    // Draggable cards
    document.querySelectorAll('.draggable-card').forEach(card => {
        card.setAttribute('draggable', true);
        card.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', card.id);
            card.classList.add('dragging');
        });
        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
        });
    });
}

function handleFileUpload(files, dropzone) {
    const input = dropzone.querySelector('input[type="file"]');
    if (input) {
        input.files = files;
        input.dispatchEvent(new Event('change'));
    }
    showToast(`${files.length} file(s) ready to upload`, 'info');
}

// ============================================
// INFINITE SCROLL
// ============================================

function initInfiniteScroll() {
    const scrollContainers = document.querySelectorAll('[data-infinite-scroll]');
    
    scrollContainers.forEach(container => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !container.classList.contains('loading')) {
                    loadMoreContent(container);
                }
            });
        }, { rootMargin: '100px' });
        
        const sentinel = document.createElement('div');
        sentinel.className = 'scroll-sentinel';
        container.appendChild(sentinel);
        observer.observe(sentinel);
    });
}

function loadMoreContent(container) {
    const url = container.dataset.infiniteScroll;
    const page = parseInt(container.dataset.page || '1') + 1;
    
    container.classList.add('loading');
    
    fetch(`${url}?page=${page}`)
        .then(res => res.text())
        .then(html => {
            container.insertAdjacentHTML('beforeend', html);
            container.dataset.page = page;
            container.classList.remove('loading');
        })
        .catch(err => {
            console.error('Error loading more content:', err);
            container.classList.remove('loading');
        });
}

// ============================================
// LAZY LOADING
// ============================================

function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
    
    // Lazy load background images
    const lazyBackgrounds = document.querySelectorAll('[data-bg]');
    const bgObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                el.style.backgroundImage = `url(${el.dataset.bg})`;
                el.removeAttribute('data-bg');
                bgObserver.unobserve(el);
            }
        });
    });
    
    lazyBackgrounds.forEach(el => bgObserver.observe(el));
}

// ============================================
// WEBSOCKET - REAL-TIME UPDATES
// ============================================

function initializeWebSocket() {
    if (!CONFIG.enableRealTimeUpdates) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    try {
        socket = new WebSocket(wsUrl);
        
        socket.onopen = () => {
            console.log('🔌 WebSocket connected');
            // Authenticate
            socket.send(JSON.stringify({
                type: 'auth',
                token: getAuthToken()
            }));
        };
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        socket.onclose = () => {
            console.log('🔌 WebSocket disconnected');
            // Reconnect after 5 seconds
            setTimeout(initializeWebSocket, 5000);
        };
        
        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    } catch (e) {
        console.log('WebSocket not available');
    }
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'notification':
            showToast(data.message, data.level || 'info');
            loadNotifications();
            break;
        case 'update':
            if (data.resource) {
                updateResource(data.resource, data.data);
            }
            break;
        case 'refresh':
            location.reload();
            break;
        case 'alert':
            showAlert(data.title, data.message, data.icon);
            break;
    }
}

function updateResource(resource, data) {
    switch (resource) {
        case 'attendance':
            updateAttendanceDisplay(data);
            break;
        case 'marks':
            updateMarksDisplay(data);
            break;
        case 'fee':
            updateFeeDisplay(data);
            break;
    }
}

function getAuthToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content || '';
}

// ============================================
// OFFLINE SUPPORT & PWA
// ============================================

function setupOfflineSupport() {
    window.addEventListener('online', () => {
        showToast('You are back online!', 'success');
        syncOfflineQueue();
    });
    
    window.addEventListener('offline', () => {
        showToast('You are offline. Changes will be saved locally.', 'warning');
    });
}

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(reg => {
                console.log('📱 Service Worker registered:', reg.scope);
                
                // Check for updates
                reg.addEventListener('updatefound', () => {
                    const newWorker = reg.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showToast('New version available! Refresh to update.', 'info', 10000);
                        }
                    });
                });
            })
            .catch(err => console.log('Service Worker failed:', err));
            
        // Handle updates
        let refreshing = false;
        navigator.serviceWorker.addEventListener('controllerchange', () => {
            if (!refreshing) {
                refreshing = true;
                window.location.reload();
            }
        });
    }
}

function syncOfflineQueue() {
    if (offlineQueue.length === 0) return;
    
    showToast(`Syncing ${offlineQueue.length} pending changes...`, 'info');
    
    const processQueue = async () => {
        for (const item of offlineQueue) {
            try {
                const response = await fetch(item.url, {
                    method: item.method,
                    headers: item.headers,
                    body: item.body
                });
                if (response.ok) {
                    offlineQueue = offlineQueue.filter(i => i.id !== item.id);
                }
            } catch (e) {
                console.error('Failed to sync:', e);
            }
        }
        showToast('Sync completed!', 'success');
    };
    
    processQueue();
}

// ============================================
// NOTIFICATION SYSTEM
// ============================================

function loadNotifications() {
    fetch(`${CONFIG.apiBaseUrl}/notifications/unread`)
        .then(res => res.json())
        .then(data => {
            updateNotificationBadge(data.length);
            updateNotificationList(data);
        })
        .catch(err => console.error('Error loading notifications:', err));
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationCount');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
        
        // Animate badge
        if (count > 0) {
            gsap.fromTo(badge, 
                { scale: 1 },
                { scale: 1.3, duration: 0.2, yoyo: true, repeat: 1 }
            );
        }
    }
    
    // Update page title
    document.title = count > 0 ? `(${count}) ${CONFIG.appName}` : CONFIG.appName;
    
    // Update favicon badge
    updateFaviconBadge(count);
}

function updateFaviconBadge(count) {
    // Create canvas for favicon
    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');
    
    // Draw background
    ctx.fillStyle = '#667eea';
    ctx.beginPath();
    ctx.arc(16, 16, 14, 0, 2 * Math.PI);
    ctx.fill();
    
    // Draw count
    if (count > 0) {
        ctx.fillStyle = '#ff0844';
        ctx.beginPath();
        ctx.arc(24, 8, 8, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.fillStyle = 'white';
        ctx.font = 'bold 10px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(count > 9 ? '9+' : count, 24, 8);
    }
    
    // Update favicon
    const link = document.querySelector("link[rel*='icon']") || document.createElement('link');
    link.type = 'image/x-icon';
    link.rel = 'shortcut icon';
    link.href = canvas.toDataURL('image/png');
    document.getElementsByTagName('head')[0].appendChild(link);
}

function updateNotificationList(notifications) {
    const container = document.getElementById('notificationList');
    if (!container) return;
    
    if (!notifications || notifications.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-bell-slash" style="font-size: 3rem; opacity: 0.3;"></i>
                <p class="text-muted mt-3">No new notifications</p>
                <small class="text-muted">You're all caught up!</small>
            </div>
        `;
        return;
    }
    
    let html = '';
    notifications.forEach(n => {
        html += `
            <div class="notification-item p-3 border-bottom" data-id="${n.id}">
                <div class="d-flex justify-content-between">
                    <strong>${n.title}</strong>
                    <small class="text-muted">${n.created_at}</small>
                </div>
                <p class="mb-0 small">${n.message}</p>
                <button class="btn btn-sm btn-link p-0 mark-read" data-id="${n.id}">Mark as read</button>
            </div>
        `;
    });
    container.innerHTML = html;
    
    // Add event listeners for mark read
    document.querySelectorAll('.mark-read').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = btn.dataset.id;
            markNotificationRead(id);
        });
    });
}

function markNotificationRead(id) {
    fetch(`/api/notification/mark-read/${id}`, { method: 'POST' })
        .then(() => loadNotifications());
}

function markAllNotificationsRead() {
    fetch('/api/notification/mark-all-read', { method: 'POST' })
        .then(() => loadNotifications());
}

// ============================================
// THEME MANAGEMENT
// ============================================

function initThemeManager() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);
    toggleChartTheme();
}

function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-bs-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
    toggleChartTheme();
    showToast(`${newTheme} mode activated`, 'info');
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function showToast(message, type = 'info', duration = 4000) {
    const toastContainer = document.querySelector('.toast-container') || (() => {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    })();
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    const icons = { success: 'check-circle', danger: 'exclamation-circle', warning: 'exclamation-triangle', info: 'info-circle' };
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-${icons[type] || 'bell'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: duration });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

function celebrate() {
    if (typeof confetti === 'function') {
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
    }
}

function showAlert(title, message, icon) {
    Swal.fire({ title, text: message, icon, confirmButtonText: 'OK' });
}

function showHelpModal() {
    Swal.fire({
        title: 'Help Center',
        html: `
            <p>Welcome to ${CONFIG.appName} Help</p>
            <ul class="text-start">
                <li>Use <kbd>Ctrl + K</kbd> to search</li>
                <li>Use <kbd>Ctrl + M</kbd> for voice commands</li>
                <li>Use <kbd>Ctrl + /</kbd> for keyboard shortcuts</li>
                <li>Swipe left/right on mobile to toggle sidebar</li>
            </ul>
        `,
        icon: 'info'
    });
}

function autoHideAlerts() {
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
}

function setupDateDefaults() {
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.value) input.value = today;
    });
}

function setupFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            const required = form.querySelectorAll('[required]');
            let valid = true;
            required.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    valid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            if (!valid) {
                e.preventDefault();
                showToast('Please fill all required fields', 'warning');
            }
        });
    });
}

function startIntervals() {
    notificationCheckInterval = setInterval(() => {
        loadNotifications();
    }, CONFIG.refreshInterval);
}

function loadUserPreferences() {
    const sidebarPref = localStorage.getItem('sidebarCollapsed');
    if (sidebarPref === 'true') {
        document.getElementById('sidebar')?.classList.add('collapsed');
    }
}

function detectUserActivity() {
    document.addEventListener('mousemove', () => { lastActivity = Date.now(); });
    document.addEventListener('keypress', () => { lastActivity = Date.now(); });
}

// Stubs for functions that may be called but not fully implemented
function updateAttendanceDisplay(data) { console.log('Attendance update:', data); }
function updateMarksDisplay(data) { console.log('Marks update:', data); }
function updateFeeDisplay(data) { console.log('Fee update:', data); }

console.log('✅ College Management System JS Initialized');