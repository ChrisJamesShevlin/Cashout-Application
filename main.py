import tkinter as tk
from tkinter import ttk

def calculate_decision():
    try:
        o_model = float(entry_model_odds.get())
        o_bookmaker = float(entry_bookmaker_odds.get())
        o_live = float(entry_live_odds.get())
        sot_home = int(entry_sot_home.get())
        sot_away = int(entry_sot_away.get())
        match_time = int(entry_match_time.get())
        fav_goals = int(entry_fav_goals.get())
        underdog_goals = int(entry_underdog_goals.get())

        # Calculate updated edge
        updated_edge = (1 / o_live) - (1 / o_model)
        
        # Adjust base probability of a goal as time progresses
        p_goal = max(0.50 - 0.0045 * match_time, 0.10)  # More gradual decay
        
        # Increase probability based on shots on target
        total_sot = sot_home + sot_away
        p_goal += 0.020 * total_sot  # Reduced weight per shot
        p_goal = min(p_goal, 0.75)  # Cap probability at 75%
        
        # Adjust if underdog is leading (increases chance of a goal)
        if underdog_goals > fav_goals:
            p_goal += 0.04
        elif fav_goals > underdog_goals:
            p_goal -= 0.04
        
        p_goal = min(max(p_goal, 0), 1.0)  # Keep within 0-100%

        # Improved Expected Value (EV) Calculations
        ev_hold = (1 - p_goal) * (1 / o_live) - p_goal * (1 / o_model)  # More balanced EV model
        ev_cashout = 1 / o_live  # Cashout value approximation
        
        # Decision Logic
        if match_time >= 75 and total_sot == 0 and o_live < 2.5:
            decision = "Cash Out"  # If no shots and draw odds are low, cash out
        elif o_live > 10 or abs(fav_goals - underdog_goals) >= 3:
            decision = "Hold"  # If draw odds are very high (10+) or goal diff is 3+, hold
        elif p_goal >= 0.65:
            decision = "Hold"  # If goal probability is very high, hold
        elif ev_hold > ev_cashout or match_time < 60:  # Ensures we don't cash out too early
            decision = "Hold"
        else:
            decision = "Cash Out"
        
        result_label["text"] = (f"Updated Edge: {updated_edge:.4f}\n"
                                 f"Goal Probability: {p_goal:.2%}\n"
                                 f"EV Hold: {ev_hold:.4f}\n"
                                 f"EV Cashout: {ev_cashout:.4f}\n"
                                 f"Decision: {decision}")
    except ValueError:
        result_label["text"] = "Please enter valid numerical values."

def reset_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    result_label["text"] = ""

# Create GUI window
root = tk.Tk()
root.title("Lay the Draw - Cash Out Decision")

fields = [
    ("Your Model Draw Odds", "entry_model_odds"),
    ("Bookmaker Draw Odds", "entry_bookmaker_odds"),
    ("Current Live Draw Odds", "entry_live_odds"),
    ("Shots on Target (Home)", "entry_sot_home"),
    ("Shots on Target (Away)", "entry_sot_away"),
    ("Match Time (Minutes)", "entry_match_time"),
    ("Goals by Favorite Team", "entry_fav_goals"),
    ("Goals by Underdog Team", "entry_underdog_goals")
]

entries = {}
for i, (label_text, var_name) in enumerate(fields):
    label = tk.Label(root, text=label_text)
    label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
    entry = ttk.Entry(root)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[var_name] = entry

# Assign entries to variables
entry_model_odds = entries["entry_model_odds"]
entry_bookmaker_odds = entries["entry_bookmaker_odds"]
entry_live_odds = entries["entry_live_odds"]
entry_sot_home = entries["entry_sot_home"]
entry_sot_away = entries["entry_sot_away"]
entry_match_time = entries["entry_match_time"]
entry_fav_goals = entries["entry_fav_goals"]
entry_underdog_goals = entries["entry_underdog_goals"]

# Buttons
calculate_button = ttk.Button(root, text="Calculate Decision", command=calculate_decision)
calculate_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

reset_button = ttk.Button(root, text="Reset Fields", command=reset_fields)
reset_button.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.grid(row=len(fields) + 2, column=0, columnspan=2, pady=10)

root.mainloop()
