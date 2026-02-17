// Chat Online - Client-side JavaScript

let socket;
let userId = null;
let isTyping = false;
let typingTimeout = null;
let userData = {};
let currentSection = 'online';
let isLoggedIn = false;

// Country and State Data
const countries = {
    "US": { name: "United States", code: "us", states: ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"] },
    "GB": { name: "United Kingdom", code: "gb", states: [] },
    "CA": { name: "Canada", code: "ca", states: [] },
    "AU": { name: "Australia", code: "au", states: [] },
    "IN": { name: "India", code: "in", states: [] },
    "DE": { name: "Germany", code: "de", states: [] },
    "FR": { name: "France", code: "fr", states: [] },
    "ES": { name: "Spain", code: "es", states: [] },
    "IT": { name: "Italy", code: "it", states: [] },
    "BR": { name: "Brazil", code: "br", states: [] },
    "MX": { name: "Mexico", code: "mx", states: [] },
    "JP": { name: "Japan", code: "jp", states: [] },
    "KR": { name: "South Korea", code: "kr", states: [] },
    "CN": { name: "China", code: "cn", states: [] },
    "RU": { name: "Russia", code: "ru", states: [] },
    "NL": { name: "Netherlands", code: "nl", states: [] },
    "SE": { name: "Sweden", code: "se", states: [] },
    "NO": { name: "Norway", code: "no", states: [] },
    "DK": { name: "Denmark", code: "dk", states: [] },
    "FI": { name: "Finland", code: "fi", states: [] },
    "PL": { name: "Poland", code: "pl", states: [] },
    "IE": { name: "Ireland", code: "ie", states: [] },
    "NZ": { name: "New Zealand", code: "nz", states: [] },
    "SG": { name: "Singapore", code: "sg", states: [] },
    "MY": { name: "Malaysia", code: "my", states: [] },
    "PH": { name: "Philippines", code: "ph", states: [] },
    "ID": { name: "Indonesia", code: "id", states: [] },
    "TH": { name: "Thailand", code: "th", states: [] },
    "PK": { name: "Pakistan", code: "pk", states: [] },
    "EG": { name: "Egypt", code: "eg", states: [] },
    "ZA": { name: "South Africa", code: "za", states: [] },
    "NG": { name: "Nigeria", code: "ng", states: [] },
    "AR": { name: "Argentina", code: "ar", states: [] },
    "CO": { name: "Colombia", code: "co", states: [] },
    "CL": { name: "Chile", code: "cl", states: [] },
    "TR": { name: "Turkey", code: "tr", states: [] },
    "SA": { name: "Saudi Arabia", code: "sa", states: [] },
    "AE": { name: "United Arab Emirates", code: "ae", states: [] },
    "IL": { name: "Israel", code: "il", states: [] },
    "PT": { name: "Portugal", code: "pt", states: [] },
    "GR": { name: "Greece", code: "gr", states: [] }
};

// DOM Elements
const elements = {};

function initElements() {
    // Pages
    elements.entryPage = document.getElementById('entry-page');
    elements.mainPage = document.getElementById('main-page');
    elements.loginPage = document.getElementById('login-page');
    elements.registerPage = document.getElementById('register-page');
    elements.chatRoomsPage = document.getElementById('chat-rooms-page');
    elements.randomPage = document.getElementById('random-page');
    elements.profilePage = document.getElementById('profile-page');

    // Form elements
    elements.entryForm = document.getElementById('entry-form');
    elements.guestUsername = document.getElementById('guest-username');
    elements.guestAge = document.getElementById('guest-age');
    elements.guestCountry = document.getElementById('guest-country');
    elements.guestState = document.getElementById('guest-state');
    elements.stateGroup = document.getElementById('state-group');

    // Login form elements (multi-step)
    elements.loginEmailForm = document.getElementById('login-email-form');
    elements.loginPasswordForm = document.getElementById('login-password-form');
    elements.loginEmail = document.getElementById('login-email');
    elements.loginPassword = document.getElementById('login-password');
    elements.loginStepEmail = document.getElementById('login-step-email');
    elements.loginStepPassword = document.getElementById('login-step-password');
    elements.loginBackBtn = document.getElementById('login-back-btn');
    elements.loginEmailError = document.getElementById('login-email-error');
    elements.loginPasswordError = document.getElementById('login-password-error');

    // Registration form elements
    elements.registerForm = document.getElementById('register-form');
    elements.regUsername = document.getElementById('register-username');
    elements.regEmail = document.getElementById('register-email');
    elements.regPassword = document.getElementById('register-password');
    elements.regConfirmPassword = document.getElementById('register-confirm-password');
    elements.regTerms = document.getElementById('register-terms');
    elements.regError = document.getElementById('register-error');

    // Chat elements
    elements.chatWelcome = document.getElementById('chat-welcome');
    elements.chatView = document.getElementById('chat-view');
    elements.inboxView = document.getElementById('inbox-view');
    elements.partnerName = document.getElementById('partner-name');
    elements.partnerMeta = document.getElementById('partner-meta');
    elements.partnerAvatar = document.getElementById('partner-avatar');
    elements.chatMessages = document.getElementById('chat-messages');
    elements.messageInput = document.getElementById('message-input');
    elements.sendBtn = document.getElementById('send-btn');

    // Sidebar elements
    elements.onlineUsersList = document.getElementById('online-users-list');
    elements.randomChatSidebarBtn = document.getElementById('random-chat-sidebar-btn');
    elements.genderFilterBtns = document.querySelectorAll('.gender-filter-btn');
    elements.sidebarNavBtns = document.querySelectorAll('.sidebar-nav-btn');

    // Age modal
    elements.ageModal = document.getElementById('age-modal');
    elements.agreeBtn = document.getElementById('agree-btn');
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initElements();
    setupAgeVerification();
    populateAgeSelect();
    populateCountrySelect();
    setupEventListeners();
    initializeSocket();
    loadDemoUsers();
});

function initializeSocket() {
    socket = io();

    socket.on('connect', () => console.log('Connected'));

    socket.on('connected', (data) => {
        userId = data.user_id;
        console.log('User connected with ID:', userId);
    });

    socket.on('disconnect', () => console.log('Disconnected'));

    socket.on('error', (data) => {
        console.error('Error:', data.message);
        alert(data.message);
    });

    socket.on('login_success', (data) => {
        userData = data.user;
        isLoggedIn = true;
        alert('Login successful!');
        navigateToPage('main');
    });

    socket.on('login_error', (data) => {
        alert(data.message || 'Login failed');
    });

    socket.on('register_success', (data) => {
        userData = data.user;
        isLoggedIn = true;
        alert('Registration successful!');
        navigateToPage('main');
    });

    socket.on('register_error', (data) => {
        alert(data.message || 'Registration failed');
    });

    socket.on('partner_found', (data) => {
        showChatView(data);
    });

    socket.on('new_message', (data) => {
        addMessage(data.message, data.sender);
    });

    socket.on('partner_disconnected', () => {
        showSystemMessage('Partner disconnected');
    });

    socket.on('chat_stopped', () => {
        showWelcomeView();
    });
}

function setupAgeVerification() {
    if (elements.ageModal && elements.agreeBtn) {
        elements.agreeBtn.addEventListener('click', () => {
            elements.ageModal.classList.add('hidden');
            localStorage.setItem('ageVerified', 'true');
        });

        if (localStorage.getItem('ageVerified') === 'true') {
            elements.ageModal.classList.add('hidden');
        }
    }

    const disagreeBtn = document.getElementById('disagree-btn');
    if (disagreeBtn) {
        disagreeBtn.addEventListener('click', () => {
            window.location.href = 'https://www.google.com';
        });
    }
}

function populateAgeSelect() {
    const selects = [elements.guestAge, elements.regAge];
    selects.forEach(select => {
        if (!select) return;
        for (let i = 18; i <= 99; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = i;
            select.appendChild(opt);
        }
    });
}

function populateCountrySelect() {
    const selects = [elements.guestCountry, elements.regCountry];
    selects.forEach(select => {
        if (!select) return;
        Object.keys(countries).forEach(code => {
            const opt = document.createElement('option');
            opt.value = code;
            opt.textContent = countries[code].name;
            select.appendChild(opt);
        });
    });
}

function updateStateSelect(countryCode, stateSelect) {
    if (!stateSelect) return;
    stateSelect.innerHTML = '<option value="">Select State</option>';

    if (countries[countryCode] && countries[countryCode].states.length > 0) {
        countries[countryCode].states.forEach(state => {
            const opt = document.createElement('option');
            opt.value = state;
            opt.textContent = state;
            stateSelect.appendChild(opt);
        });
        stateSelect.closest('.form-group').style.display = 'block';
    } else {
        stateSelect.closest('.form-group').style.display = 'none';
    }
}

function setupEventListeners() {
    // Navigation links - allow normal navigation for links with href
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            // Let links with actual URLs work normally
            const href = link.getAttribute('href');
            if (href && href !== '#' && !href.startsWith('javascript')) {
                return; // Allow normal navigation
            }

            // Only prevent default for javascript/toggle links
            e.preventDefault();
            const pageName = link.dataset.page;
            if (pageName) {
                navigateToPage(pageName);
            }
        });
    });

    // Login form
    if (elements.loginForm) {
        elements.loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = elements.loginUsername.value.trim();
            if (!username) {
                alert('Please enter username');
                return;
            }
            socket.emit('login', { username });
        });
    }

    // Registration form
    if (elements.registerForm) {
        elements.registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = elements.regUsername.value.trim();
            const gender = document.querySelector('input[name="register_gender"]:checked');
            const age = elements.regAge.value;
            const country = elements.regCountry.value;

            if (!username || !gender || !age || !country) {
                alert('Please fill in all fields');
                return;
            }

            socket.emit('register', {
                username,
                gender: gender.value,
                age,
                country
            });
        });
    }

    // Sidebar navigation
    elements.sidebarNavBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            elements.sidebarNavBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show/hide gender filter
            const genderPanel = document.getElementById('gender-filter-panel');
            if (section === 'gender') {
                genderPanel.style.display = 'flex';
            } else {
                genderPanel.style.display = 'none';
            }

            // Show appropriate view
            if (section === 'online' || section === 'gender') {
                elements.chatWelcome?.classList.remove('hidden');
                elements.chatView?.classList.add('hidden');
                elements.inboxView?.classList.add('hidden');
            }
        });
    });

    // Gender filter
    elements.genderFilterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            elements.genderFilterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Random chat button
    if (elements.randomChatSidebarBtn) {
        elements.randomChatSidebarBtn.addEventListener('click', () => {
            navigateToPage('random');
        });
    }

    // Country change
    if (elements.guestCountry) {
        elements.guestCountry.addEventListener('change', () => {
            updateStateSelect(elements.guestCountry.value, elements.guestState);
        });
    }

    // Send message
    if (elements.sendBtn) {
        elements.sendBtn.addEventListener('click', sendMessage);
    }
    if (elements.messageInput) {
        elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

function navigateToPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.add('hidden');
    });

    // Show target page
    switch(pageName) {
        case 'entry':
            elements.entryPage?.classList.remove('hidden');
            break;
        case 'main':
        case 'home':
            elements.mainPage?.classList.remove('hidden');
            break;
        case 'login':
            elements.loginPage?.classList.remove('hidden');
            break;
        case 'register':
            elements.registerPage?.classList.remove('hidden');
            break;
        case 'chat-rooms':
            elements.chatRoomsPage?.classList.remove('hidden');
            break;
        case 'random':
            elements.randomPage?.classList.remove('hidden');
            break;
        case 'profile':
            elements.profilePage?.classList.remove('hidden');
            break;
        case 'about':
            document.getElementById('about-page')?.classList.remove('hidden');
            break;
        case 'blog':
            document.getElementById('blog-page')?.classList.remove('hidden');
            break;
        case 'faq':
            document.getElementById('faq-page')?.classList.remove('hidden');
            break;
        case 'terms':
            document.getElementById('terms-page')?.classList.remove('hidden');
            break;
        case 'privacy':
            document.getElementById('privacy-page')?.classList.remove('hidden');
            break;
        case 'safety':
            document.getElementById('safety-page')?.classList.remove('hidden');
            break;
        case 'contact':
            document.getElementById('contact-page')?.classList.remove('hidden');
            break;
    }
}

function showWelcomeView() {
    elements.chatWelcome?.classList.remove('hidden');
    elements.chatView?.classList.add('hidden');
    elements.inboxView?.classList.add('hidden');
}

function showChatView(data) {
    elements.chatWelcome?.classList.add('hidden');
    elements.chatView?.classList.remove('hidden');
    elements.inboxView?.classList.add('hidden');

    if (elements.partnerName) {
        elements.partnerName.textContent = data.partner_name || 'Stranger';
    }
    if (elements.partnerMeta) {
        elements.partnerMeta.textContent = data.partner_info || '';
    }
    if (elements.partnerAvatar) {
        const gender = data.partner_gender;
        elements.partnerAvatar.className = 'chat-avatar ' + (gender || '');
    }
    if (elements.chatMessages) {
        elements.chatMessages.innerHTML = `
            <div class="system-message">
                <i class="fas fa-info-circle"></i>
                You are now chatting with ${data.partner_name || 'a stranger'}
            </div>
        `;
    }
}

function sendMessage() {
    const message = elements.messageInput?.value.trim();
    if (!message) return;

    socket.emit('send_message', { message });
    elements.messageInput.value = '';
}

function addMessage(message, sender) {
    if (!elements.chatMessages) return;

    const div = document.createElement('div');
    div.className = `message ${sender}`;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    div.innerHTML = `<div class="message-content">${escapeHtml(message)}</div><span class="timestamp">${time}</span>`;
    elements.chatMessages.appendChild(div);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function showSystemMessage(text) {
    if (!elements.chatMessages) return;
    const div = document.createElement('div');
    div.className = 'system-message';
    div.innerHTML = `<i class="fas fa-info-circle"></i> ${text}`;
    elements.chatMessages.appendChild(div);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Demo users
function loadDemoUsers() {
    const demoUsers = [
        { id: 1, username: 'Sarah_99', gender: 'female', age: 24, country: 'US', flag: 'us' },
        { id: 2, username: 'John_Cool', gender: 'male', age: 28, country: 'GB', flag: 'gb' },
        { id: 3, username: 'Maria_G', gender: 'female', age: 22, country: 'ES', flag: 'es' },
        { id: 4, username: 'Alex_123', gender: 'male', age: 25, country: 'DE', flag: 'de' },
        { id: 5, username: 'Emma_W', gender: 'female', age: 26, country: 'FR', flag: 'fr' },
        { id: 6, username: 'Mike_T', gender: 'male', age: 30, country: 'CA', flag: 'ca' },
        { id: 7, username: 'Lisa_22', gender: 'female', age: 22, country: 'AU', flag: 'au' },
        { id: 8, username: 'David_B', gender: 'male', age: 27, country: 'IN', flag: 'in' },
        { id: 9, username: 'Sophie_L', gender: 'female', age: 25, country: 'NL', flag: 'nl' },
        { id: 10, username: 'James_K', gender: 'male', age: 29, country: 'JP', flag: 'jp' }
    ];

    // Get the user list container
    const userListContainer = document.getElementById('user-list-container');
    if (!userListContainer) return;

    userListContainer.innerHTML = '';

    demoUsers.forEach(user => {
        const item = document.createElement('div');
        item.className = 'user-card';
        item.innerHTML = `
            <div class="user-card-avatar ${user.gender}">
                <i class="fas fa-user"></i>
                <span class="online-dot"></span>
            </div>
            <div class="user-card-info">
                <div class="user-card-name">${user.username} <span class="flag-icon flag-icon-${user.flag}"></span></div>
                <div class="user-card-meta">${user.age} | Online</div>
            </div>
        `;
        item.addEventListener('click', () => {
            // Show chat view with this user
            userListContainer.querySelectorAll('.user-card').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            showChatView({
                partner_name: user.username,
                partner_info: `${user.age} | ${countries[user.country]?.name || user.country}`,
                partner_gender: user.gender
            });
        });
        userListContainer.appendChild(item);
    });
}

window.addEventListener('beforeunload', () => {
    if (socket?.connected) socket.disconnect();
});
