import random

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

# List of symbols for random selection
symbol_list = list(SYMBOLS.keys())

def spin_slot():
    """Simulate a slot spin returning 3 symbols."""
    return [random.choice(symbol_list) for _ in range(3)]

def evaluate_spin(result, bet):
    """
    Evaluate the spin outcome.
    
    Returns:
      outcome: 'triple', 'double', or 'lose'
      winnings: The calculated winnings (if any) before charity deduction.
      charity: The amount donated to charity.
      player_net: Net change to the player's balance.
      casino_net: Net profit for the casino.
    """
    # Check for a triple win
    if result[0] == result[1] == result[2]:
        multiplier = SYMBOLS[result[0]]
        winnings = bet * multiplier
        outcome = 'triple'
    # Check for a double win (exactly two adjacent symbols match)
    elif (result[0] == result[1] and result[0] != result[2]) or (result[1] == result[2] and result[1] != result[0]):
        # Determine which matching pair occurred
        if result[0] == result[1]:
            symbol = result[0]
        else:
            symbol = result[1]
        multiplier = SYMBOLS[symbol] / 2  # half multiplier for double win
        winnings = bet * multiplier
        outcome = 'double'
    else:
        outcome = 'lose'
        winnings = 0

    # Calculate payout details
    if outcome in ['triple', 'double']:
        # Charity gets 50% of the winnings
        charity = winnings * 0.5
        # Player receives the remainder of the winnings
        player_payout = winnings - charity
        # Casino collects the bet then pays out the full winnings
        casino_net = bet - winnings
        # User net is what they get minus their bet
        player_net = player_payout - bet
    else:
        # Losing spin: player loses bet but 10% is donated
        charity = bet * 0.1
        casino_net = bet - charity  # casino nets 90% of the bet
        player_net = -bet

    return outcome, winnings, charity, player_net, casino_net

def backtest(num_spins=10000, bet=10):
    total_casino_profit = 0
    total_user_profit = 0
    total_charity_profit = 0

    # For tracking outcome counts
    outcome_counts = {'triple': 0, 'double': 0, 'lose': 0}

    for _ in range(num_spins):
        result = spin_slot()
        outcome, winnings, charity, player_net, casino_net = evaluate_spin(result, bet)
        outcome_counts[outcome] += 1

        total_casino_profit += casino_net
        total_user_profit += player_net
        total_charity_profit += charity

    print(f"Backtest results over {num_spins} spins with bet {bet}:")
    print("========================================")
    print(f"Outcome counts: {outcome_counts}")
    print(f"Total Casino Profit: {total_casino_profit:.2f}")
    print(f"Total User Profit: {total_user_profit:.2f}")
    print(f"Total Charity Profit: {total_charity_profit:.2f}")
    print("========================================")
    print("Per spin averages:")
    print(f"Casino Profit per Spin: {total_casino_profit / num_spins:.4f}")
    print(f"User Profit per Spin: {total_user_profit / num_spins:.4f}")
    print(f"Charity Profit per Spin: {total_charity_profit / num_spins:.4f}")

if __name__ == "__main__":
    backtest(num_spins=50000000, bet=1)
