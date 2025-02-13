import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

@dataclass
class MatchData:
    model_odds: float
    bookmaker_odds: float
    live_odds: float
    sot_fav: int
    sot_underdog: int
    match_time: int
    fav_goals: int
    underdog_goals: int
    xg_fav: float
    xg_underdog: float
    possession_fav: float
    possession_underdog: float

def calculate_decision():
    try:
        # Read input values
        match_data = MatchData(
            model_odds=float(entries["entry_model_odds"].get()),
            bookmaker_odds=float(entries["entry_bookmaker_odds"].get()),
            live_odds=float(entries["entry_live_odds"].get()),
            sot_fav=int(entries["entry_sot_fav"].get()),
            sot_underdog=int(entries["entry_sot_underdog"].get()),
            match_time=int(entries["entry_match_time"].get()),
            fav_goals=int(entries["entry_fav_goals"].get()),
            underdog_goals=int(entries["entry_underdog_goals"].get()),
            xg_fav=float(entries["entry_xg_fav"].get()),
            xg_underdog=float(entries["entry_xg_underdog"].get()),
            possession_fav=float(entries["entry_possession_fav"].get()),
            possession_underdog=float(entries["entry_possession_underdog"].get())
        )

        # Calculate updated edge
        updated_edge = (1 / match_data.live_odds) - (1 / match_data.model_odds)

        # Probability of a goal occurring
        p_goal = max(0.50 - 0.0045 * match_data.match_time, 0.10)

        # Shots on Target (SOT) Adjustment
        total_sot = match_data.sot_fav + match_data.sot_underdog
        p_goal += 0.020 * total_sot if total_sot >= 6 else -0.05

        # Expected Goals (xG) Adjustment
        combined_xg = match_data.xg_fav + match_data.xg_underdog
        p_goal += 0.02 * combined_xg if combined_xg >= 1.2 else -0.10

        # Adjust for scoreline impact
        if match_data.underdog_goals > match_data.fav_goals:
            p_goal += 0.04  # Underdog is leading
        elif match_data.fav_goals > match_data.underdog_goals:
            p_goal -= 0.04  # Favorite is leading

        # Ensure probability is within valid range
        p_goal = min(max(p_goal, 0), 1.0)

        # Expected Value (EV) calculations
        ev_hold = (1 - p_goal) * (1 / match_data.live_odds) - p_goal * (1 / match_data.model_odds)
        ev_cashout = 1 / match_data.live_odds

        # **Generalized Cash-Out Condition Using xG & Possession**
        if (match_data.xg_underdog >= match_data.xg_fav + 0.3  # Underdog leading in xG
            or match_data.sot_underdog > match_data.sot_fav  # More shots from underdog
            or match_data.possession_fav < 45):  # Possession heavily against favorite
            decision = "Cash Out"
        else:
            decision = "Hold"

        # **Specific Late-Game Hold Condition (80+ Mins)**
        if (match_data.match_time >= 80 
            and match_data.fav_goals - match_data.underdog_goals >= 2  # Clear lead
            and match_data.xg_underdog < 1.0  # Underdog has low xG
            and match_data.sot_underdog < 3  # Underdog not creating many chances
            and match_data.possession_fav > 60):  # Favorite is controlling the game
            decision = "Hold"

        # Display results
        result_label["text"] = (
            f"Updated Edge: {updated_edge:.4f}\n"
            f"Goal Probability: {p_goal:.2%}\n"
            f"EV Hold: {ev_hold:.4f}\n"
            f"EV Cashout: {ev_cashout:.4f}\n"
            f"Decision: {decision}"
        )
        result_label["foreground"] = "green" if decision == "Hold" else "red"

    except ValueError:
        result_label["text"] = "Please enter valid numerical values."
        result_label["foreground"] = "black"

# Reset Fields
def reset_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    result_label["text"] = ""

# Create GUI
root = tk.Tk()
root.title("Lay the Draw - Cash Out Decision")

fields = [
    ("Your Model Draw Odds", "entry_model_odds"),
    ("Bookmaker Draw Odds", "entry_bookmaker_odds"),
    ("Current Live Draw Odds", "entry_live_odds"),
    ("Shots on Target (Favorite)", "entry_sot_fav"),
    ("Shots on Target (Underdog)", "entry_sot_underdog"),
    ("Match Time (Minutes)", "entry_match_time"),
    ("Goals by Favorite Team", "entry_fav_goals"),
    ("Goals by Underdog Team", "entry_underdog_goals"),
    ("Expected Goals (Favorite)", "entry_xg_fav"),
    ("Expected Goals (Underdog)", "entry_xg_underdog"),
    ("Possession (Favorite %)", "entry_possession_fav"),
    ("Possession (Underdog %)", "entry_possession_underdog")
]

entries = {}
for i, (label_text, var_name) in enumerate(fields):
    label = tk.Label(root, text=label_text)
    label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
    entry = ttk.Entry(root)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[var_name] = entry

calculate_button = ttk.Button(root, text="Calculate Decision", command=calculate_decision)
calculate_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

reset_button = ttk.Button(root, text="Reset Fields", command=reset_fields)
reset_button.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.grid(row=len(fields) + 2, column=0, columnspan=2, pady=10)

root.mainloop()
