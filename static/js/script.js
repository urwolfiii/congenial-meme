// Global variables
let currentUser = null;

// DOM elements
const loginSection = document.getElementById('login-section');
const gameSection = document.getElementById('game-section');
const leaderboardSection = document.getElementById('leaderboard-section');

const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');
const registerBtn = document.getElementById('register-btn');
const logoutBtn = document.getElementById('logout-btn');

const userNameSpan = document.getElementById('user-name');
const userBalanceSpan = document.getElementById('user-balance');
const userDonatedSpan = document.getElementById('user-donated');

const slot1 = document.getElementById('slot-1');
const slot2 = document.getElementById('slot-2');
const slot3 = document.getElementById('slot-3');
const resultMessage = document.getElementById('result-message');
const betAmountInput = document.getElementById('bet-amount');
const spinBtn = document.getElementById('spin-btn');

const statsSpins = document.getElementById('stats-spins');
const statsWins = document.getElementById('stats-wins');
const statsLosses = document.getElementById('stats-losses');

const leaderboardList = document.getElementById('leaderboard-list');

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadLeaderboard();
    
    // Check if user is already logged in (from previous session)
    const savedUser = localStorage.getItem('casinoUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        updateUI();
    }
});

loginBtn.addEventListener('click', async () => {
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    
    if (!username || !password) {
        showMessage(resultMessage, 'Please enter username and password', 'lose');
        return;
    }
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.user;
            localStorage.setItem('casinoUser', JSON.stringify(currentUser));
            updateUI();
            showMessage(resultMessage, 'Login successful! Ready to play?', 'win');
        } else {
            showMessage(resultMessage, data.message, 'lose');
        }
    } catch (error) {
        showMessage(resultMessage, 'Error connecting to server', 'lose');
        console.error(error);
    }
});

registerBtn.addEventListener('click', async () => {
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    
    if (!username || !password) {
        showMessage(resultMessage, 'Please enter username and password', 'lose');
        return;
    }
    
    if (password.length < 6) {
        showMessage(resultMessage, 'Password must be at least 6 characters', 'lose');
        return;
    }
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Auto-login after successful registration
            loginBtn.click();
        } else {
            showMessage(resultMessage, data.message, 'lose');
        }
    } catch (error) {
        showMessage(resultMessage, 'Error connecting to server', 'lose');
        console.error(error);
    }
});

logoutBtn.addEventListener('click', () => {
    currentUser = null;
    localStorage.removeItem('casinoUser');
    updateUI();
    showMessage(resultMessage, 'Logged out successfully', 'win');
});

spinBtn.addEventListener('click', async () => {
    if (!currentUser) {
        showMessage(resultMessage, 'Please login first', 'lose');
        return;
    }
    
    const betAmount = parseFloat(betAmountInput.value);
    
    if (isNaN(betAmount) || betAmount <= 0) {
        showMessage(resultMessage, 'Please enter a valid bet amount', 'lose');
        return;
    }
    
    if (betAmount > currentUser.balance) {
        showMessage(resultMessage, 'Insufficient balance', 'lose');
        return;
    }
    
    // Disable spin button during spinning
    spinBtn.disabled = true;
    
    // Animation for spinning
    [slot1, slot2, slot3].forEach(slot => {
        slot.textContent = '?';
        slot.classList.add('spinning');
    });
    
    showMessage(resultMessage, 'Spinning...', '');
    
    try {
        const response = await fetch('/api/spin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: currentUser.username,
                bet_amount: betAmount
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Short delay to show animation
            setTimeout(() => {
                // Display results
                slot1.textContent = data.result[0];
                slot2.textContent = data.result[1];
                slot3.textContent = data.result[2];
                
                // Remove animation class
                [slot1, slot2, slot3].forEach(slot => slot.classList.remove('spinning'));
                
                // Update user data
                currentUser = data.user;
                localStorage.setItem('casinoUser', JSON.stringify(currentUser));
                
                // Show result message
                showMessage(resultMessage, data.message, data.is_win ? 'win' : 'lose');
                
                // Update UI
                updateUI();
                
                // Re-enable spin button
                spinBtn.disabled = false;
                
                // Refresh leaderboard
                loadLeaderboard();
            }, 1000);
        } else {
            showMessage(resultMessage, data.message, 'lose');
            spinBtn.disabled = false;
            [slot1, slot2, slot3].forEach(slot => slot.classList.remove('spinning'));
        }
    } catch (error) {
        showMessage(resultMessage, 'Error connecting to server', 'lose');
        console.error(error);
        spinBtn.disabled = false;
        [slot1, slot2, slot3].forEach(slot => slot.classList.remove('spinning'));
    }
});

// Helper functions
function updateUI() {
    if (currentUser) {
        loginSection.classList.add('hidden');
        gameSection.classList.remove('hidden');
        
        userNameSpan.textContent = currentUser.username;
        userBalanceSpan.textContent = currentUser.balance.toFixed(2);
        userDonatedSpan.textContent = currentUser.donated.toFixed(2);
        
        statsSpins.textContent = currentUser.spins;
        statsWins.textContent = currentUser.wins;
        statsLosses.textContent = currentUser.losses;
    } else {
        loginSection.classList.remove('hidden');
        gameSection.classList.add('hidden');
        
        // Clear form fields
        usernameInput.value = '';
        passwordInput.value = '';
    }
}

function showMessage(element, message, type) {
    element.textContent = message;
    element.className = 'message';
    
    if (type) {
        element.classList.add(type);
    }
}

async function loadLeaderboard() {
    try {
        const response = await fetch('/api/leaderboard');
        const data = await response.json();
        
        if (data.success) {
            leaderboardList.innerHTML = '';
            
            if (data.leaderboard.length === 0) {
                leaderboardList.innerHTML = '<div class="leaderboard-item">No players yet</div>';
                return;
            }
            
            data.leaderboard.forEach((user, index) => {
                const item = document.createElement('div');
                item.className = 'leaderboard-item';
                item.innerHTML = `
                    <div>${index + 1}. ${user.username}</div>
                    <div>$${user.balance.toFixed(2)} / $${user.donated.toFixed(2)} donated</div>
                `;
                leaderboardList.appendChild(item);
            });
        } else {
            leaderboardList.innerHTML = '<div class="leaderboard-item">Error loading leaderboard</div>';
        }
    } catch (error) {
        leaderboardList.innerHTML = '<div class="leaderboard-item">Error connecting to server</div>';
        console.error(error);
    }
}