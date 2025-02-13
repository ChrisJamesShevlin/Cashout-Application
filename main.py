import tkinter as tk

class MatchData:
    def __init__(self, model_odds, bookmaker_odds, live_odds, sot_fav, sot_underdog, match_time, fav_goals, underdog_goals, xg_fav, xg_underdog, possession_fav, possession_underdog):
        self.model_odds = model_odds
        self.bookmaker_odds = bookmaker_odds
        self.live_odds = live_odds
        self.sot_fav = sot_fav
        self.sot_underdog = sot_underdog
        self.match_time = match_time
        self.fav_goals = fav_goals
        self.underdog_goals = underdog_goals
        self.xg_fav = xg_fav
        self.xg_underdog = xg_underdog
        self.possession_fav = possession_fav
        self.possession_underdog = possession_underdog

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

        # New Cash-Out Logic
        underdog_lead = match_data.underdog_goals - match_data.fav_goals
        underdog_dominating = (
            (match_data.xg_underdog >= match_data.xg_fav + 0.3) +
            (match_data.sot_underdog > match_data.sot_fav) +
            (match_data.possession_fav < 45)
        ) >= 2  # Needs at least 2 out of 3 conditions

        favorite_comeback_potential = (
            match_data.xg_fav > 1.5 and
            match_data.sot_fav >= 6 and
            match_data.possession_fav > 55
        )

        # Default to Hold if Underdog is Leading & Dominating
        decision = "Hold"
        # But Cash Out if Favorite is Showing Strong Comeback Potential
        if favorite_comeback_potential:
            decision = "Cash Out"

        # Late-Game Adjustments
        if match_data.match_time >= 80:
            if underdog_lead >= 2 and underdog_dominating:
                decision = "Hold"
            elif favorite_comeback_potential:
                decision = "Cash Out"

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

def reset_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    result_label["text"] = ""

# Initialize the GUI
root = tk.Tk()
root.title("Decision Calculator")

# Define the entry fields and result label
entries = {
    "entry_model_odds": tk.Entry(root),
    "entry_bookmaker_odds": tk.Entry(root),
    "entry_live_odds": tk.Entry(root),
    "entry_sot_fav": tk.Entry(root),
    "entry_sot_underdog": tk.Entry(root),
    "entry_match_time": tk.Entry(root),
    "entry_fav_goals": tk.Entry(root),
    "entry_underdog_goals": tk.Entry(root),
    "entry_xg_fav": tk.Entry(root),
    "entry_xg_underdog": tk.Entry(root),
    "entry_possession_fav": tk.Entry(root),
    "entry_possession_underdog": tk.Entry(root)
}

result_label = tk.Label(root, text="", font=("Helvetica", 12))

# Layout the entry fields and result label
for i, (key, entry) in enumerate(entries.items()):
    tk.Label(root, text=key.replace("entry_", "").replace("_", " ").title()).grid(row=i, column=0)
    entry.grid(row=i, column=1)

tk.Button(root, text="Calculate Decision", command=calculate_decision).grid(row=len(entries), column=0, columnspan=2)
tk.Button(root, text="Reset Fields", command=reset_fields).grid(row=len(entries) + 1, column=0, columnspan=2)
result_label.grid(row=len(entries) + 2, column=0, columnspan=2)

# Start the GUI event loop
root.mainloop()
