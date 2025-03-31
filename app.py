import flask 
import hashlib
import json 
import os
import random
import string
import time

from flask import Flask, request, jsonify, send_file, make_response

app = Flask(__name__)

# Slot game symbols and multipliers
SYMBOLS = {
    '🍒': 0.5,  # Lowest value
    '🍋': 0.8,
    '🍊': 1,
    '🍇': 1.5,
    '🔔': 2,
    '💎': 5,
    '7️⃣': 10,
    '⭐': 20    # Highest value
}

# Initialize users database if it doesn't exist
def init_db():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump({}, f)

# Helper function to get all users
def get_users():
    with open('users.json', 'r') as f:
        return json.load(f)

# Helper function to save users
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

# Helper function to get a user
def get_user(username):
    users = get_users()
    return users.get(username)

# Helper function to create a user
def create_user(username, password):
    users = get_users()
    if username in users:
        return False
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    users[username] = {
        'password': hashed_password,
        'balance': 1000,  # Starting balance
        'spins': 0,
        'wins': 0,
        'losses': 0,
        'donated': 0,
        'created_at': time.time()
    }
    
    save_users(users)
    return True

# Helper function to update user balance
def update_balance(username, amount):
    users = get_users()
    if username not in users:
        return False
    
    users[username]['balance'] += amount
    save_users(users)
    return True

# Helper function to spin the slot
def spin_slot():
    # Get all symbols as a list
    symbol_list = list(SYMBOLS.keys())
    
    # Generate a random slot result (3 symbols)
    result = [random.choice(symbol_list) for _ in range(3)]
    
    return result

# Initialize the database
init_db()

# Routes
@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/css/style.css')
def serve_css():
    return send_file('static/css/style.css')

@app.route('/js/script.js')
def serve_js():
    return send_file('static/js/script.js')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    
    if create_user(username, password):
        return jsonify({'success': True, 'message': 'User created successfully'})
    else:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    
    user = get_user(username)
    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user['password'] != hashed_password:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    return jsonify({
        'success': True,
        'user': {
            'username': username,
            'balance': user['balance'],
            'spins': user['spins'],
            'wins': user['wins'],
            'losses': user['losses'],
            'donated': user['donated']
        }
    })

@app.route('/api/spin', methods=['POST'])
def play_spin():
    data = request.json
    username = data.get('username')
    bet_amount = data.get('bet_amount', 10)  # Default bet is 10
    
    # Validate input
    try:
        bet_amount = float(bet_amount)
        if bet_amount <= 0:
            return jsonify({'success': False, 'message': 'Bet amount must be positive'}), 400
    except:
        return jsonify({'success': False, 'message': 'Invalid bet amount'}), 400
    
    user = get_user(username)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    if user['balance'] < bet_amount:
        return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
    
    # Spin the slot
    result = spin_slot()
    
    # Check if win (all symbols are the same)
    is_win = result[0] == result[1] == result[2]
    
    # Update user stats
    users = get_users()
    users[username]['spins'] += 1
    
    if is_win:
        # Calculate winnings
        multiplier = SYMBOLS[result[0]]
        winnings = bet_amount * multiplier
        
        # 50% of winnings go to charity if win
        charity_donation = winnings * 0.5
        player_winnings = winnings - charity_donation
        
        users[username]['balance'] += player_winnings
        users[username]['wins'] += 1
        users[username]['donated'] += charity_donation
        
        message = f"You won {winnings:.2f}! {charity_donation:.2f} donated to charity."
    else:
        # 10% of bet goes to charity if lose
        charity_donation = bet_amount * 0.1
        loss_amount = bet_amount
        
        users[username]['balance'] -= loss_amount
        users[username]['losses'] += 1
        users[username]['donated'] += charity_donation
        
        message = f"You lost {loss_amount:.2f}. {charity_donation:.2f} donated to charity."
    
    save_users(users)
    
    return jsonify({
        'success': True,
        'result': result,
        'is_win': is_win,
        'message': message,
        'user': {
            'username': username,
            'balance': users[username]['balance'],
            'spins': users[username]['spins'],
            'wins': users[username]['wins'],
            'losses': users[username]['losses'],
            'donated': users[username]['donated']
        }
    })

@app.route('/api/user/<username>', methods=['GET'])
def get_user_info(username):
    user = get_user(username)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': {
            'username': username,
            'balance': user['balance'],
            'spins': user['spins'],
            'wins': user['wins'],
            'losses': user['losses'],
            'donated': user['donated']
        }
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    users = get_users()
    
    # Create a list of users with relevant stats
    leaderboard = [
        {
            'username': username,
            'balance': user['balance'],
            'spins': user['spins'],
            'donated': user['donated']
        }
        for username, user in users.items()
    ]
    
    # Sort by balance (could also sort by donated amount)
    leaderboard.sort(key=lambda x: x['balance'], reverse=True)
    
    return jsonify({
        'success': True,
        'leaderboard': leaderboard[:10]  # Return top 10
    })

if __name__ == '__main__':
    app.run(debug=False)