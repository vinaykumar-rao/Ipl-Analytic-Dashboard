import ttkbootstrap as tb
from tkinter import ttk
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAggACC
from matplotlib import rcParams
import numpy as np
import os

# ── MATPLOTLIB GLOBAL THEME ──────────────────────────────────────────────────
rcParams.update({
    "figure.facecolor":  "#0d1117",
    "axes.facecolor":    "#161b22",
    "axes.edgecolor":    "#30363d",
    "axes.labelcolor":   "#c9d1d9",
    "axes.titlecolor":   "#f0c040",
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.titlepad":     14,
    "axes.grid":         True,
    "grid.color":        "#21262d",
    "grid.linewidth":    0.8,
    "xtick.color":       "#8b949e",
    "ytick.color":       "#8b949e",
    "text.color":        "#c9d1d9",
    "legend.facecolor":  "#161b22",
    "legend.edgecolor":  "#30363d",
})

# ── COLOUR PALETTE ───────────────────────────────────────────────────────────
ACCENT  = "#f0c040"
BG_DEEP = "#0d1117"
BG_MID  = "#161b22"
BG_CARD = "#1c2128"
BORDER  = "#30363d"
FG_MAIN = "#e6edf3"
FG_DIM  = "#8b949e"
GREEN   = "#3fb950"
RED     = "#f85149"
BLUE    = "#58a6ff"
PURPLE  = "#bc8cff"

BAR_COLORS = [ACCENT, BLUE, GREEN, RED, PURPLE,
              "#ff7b72", "#79c0ff", "#56d364", "#d2a8ff", "#ffa657"]

# ── PATHS ────────────────────────────────────────────────────────────────────
DATA_PATH = r"C:\Users\DELL\OneDrive\Desktop\tk_project\IPL.csv"
IMG_ROOT  = r"C:\Users\DELL\OneDrive\Desktop\tk_project"

# ── LOAD DATA ────────────────────────────────────────────────────────────────
data = pd.read_csv(DATA_PATH, low_memory=False)
data["season"]      = pd.to_numeric(data["season"],      errors="coerce")
data["runs_batter"] = pd.to_numeric(data["runs_batter"], errors="coerce")
data["valid_ball"]  = pd.to_numeric(data["valid_ball"],  errors="coerce")
data = data[data["batter"].notna()]

players = sorted(data["batter"].dropna().unique())
years   = sorted(data["season"].dropna().astype(int).unique())

# ── IPL WINNERS ──────────────────────────────────────────────────────────────
ipl_winners = {
    2008: "Rajasthan Royals",      2009: "Deccan Chargers",
    2010: "Chennai Super Kings",   2011: "Chennai Super Kings",
    2012: "Kolkata Knight Riders", 2013: "Mumbai Indians",
    2014: "Kolkata Knight Riders", 2015: "Mumbai Indians",
    2016: "Sunrisers Hyderabad",   2017: "Mumbai Indians",
    2018: "Chennai Super Kings",   2019: "Mumbai Indians",
    2020: "Mumbai Indians",        2021: "Chennai Super Kings",
    2022: "Gujarat Titans",        2023: "Chennai Super Kings",
    2024: "Kolkata Knight Riders",
}
team_titles = {
    "Mumbai Indians": 5, "Chennai Super Kings": 5,
    "Kolkata Knight Riders": 3, "Sunrisers Hyderabad": 1,
    "Rajasthan Royals": 1, "Deccan Chargers": 1, "Gujarat Titans": 1,
}


# ═════════════════════════════════════════════════════════════════════════════
class IPLDashboard:

    def __init__(self, root):
        self.root = root
        self.root.title("IPL Advanced Analytics Dashboard")
        self.root.geometry("1440x820")
        self.root.configure(bg=BG_DEEP)

        # IMPORTANT: create status_var before anything else so all methods
        # can safely call self.status_var.set(...)
        self.status_var = tk.StringVar(value="Ready")

        self._apply_styles()
        self._build_ui()

    # ── STYLES ───────────────────────────────────────────────────────────────
    def _apply_styles(self):
        s = ttk.Style()
        s.configure("TCombobox",
                    fieldbackground=BG_MID, background=BG_MID,
                    foreground=FG_MAIN, arrowcolor=ACCENT,
                    bordercolor=BORDER, insertcolor=FG_MAIN,
                    selectforeground=ACCENT, selectbackground=BG_CARD,
                    padding=6)
        s.map("TCombobox",
              fieldbackground=[("readonly", BG_MID)],
              foreground=[("readonly", FG_MAIN)])

    # ── FULL UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        tk.Frame(self.root, bg=ACCENT, height=3).pack(fill="x")

        body = tk.Frame(self.root, bg=BG_DEEP)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_main(body)
        self._build_statusbar()

    # ── HEADER ───────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG_CARD, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🏏", font=("Segoe UI Emoji", 26),
                 bg=BG_CARD, fg=ACCENT).pack(side="left", padx=(20, 6))
        tk.Label(hdr, text="IPL ADVANCED ANALYTICS",
                 font=("Impact", 22), bg=BG_CARD, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text="  DASHBOARD",
                 font=("Impact", 22), bg=BG_CARD, fg=FG_MAIN).pack(side="left")
        tk.Label(hdr, text="Indian Premier League  •  2008 – 2024",
                 font=("Trebuchet MS", 10), bg=BG_CARD, fg=FG_DIM
                 ).pack(side="right", padx=24)

    # ── STATUSBAR ────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG_CARD, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Label(bar,
                 text=(f"  {len(players):,} players  •  "
                       f"{len(years)} seasons  •  "
                       f"{len(data):,} deliveries loaded"),
                 font=("Consolas", 9), bg=BG_CARD, fg=FG_DIM
                 ).pack(side="left")

        # Re-use the same status_var already created in __init__
        tk.Label(bar, textvariable=self.status_var,
                 font=("Consolas", 9), bg=BG_CARD, fg=GREEN
                 ).pack(side="right", padx=10)

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=BG_CARD, width=230)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # PLAYER SECTION
        self._section_label(sb, "PLAYER")
        self.player_box = ttk.Combobox(sb, values=players, width=22)
        self.player_box.pack(padx=14, pady=(0, 4))
        self.player_box.bind("<KeyRelease>", self._filter_players)
        self._hint(sb, "Type to search…")

        for label, cmd in [
            ("👤  Player Stats",   self.player_stats),
            ("🍕  Boundary Chart", self.boundary_chart),
            ("🪁  Wagon Wheel",    self.wagon_wheel),
            ("💫  Runs vs SR",     self.scatter_plot),
        ]:
            self._nav_btn(sb, label, cmd)

        self._divider(sb)

        # SEASON SECTION
        self._section_label(sb, "SEASON")
        self.year_box = ttk.Combobox(sb, values=years, width=22)
        self.year_box.pack(padx=14, pady=(0, 4))
        self._hint(sb, "Select a season…")
        self._gold_btn(sb, "🏆  Season Winner", self.ipl_winner)

        self._divider(sb)

        # LEAGUE SECTION
        self._section_label(sb, "LEAGUE")
        for label, cmd in [
            ("🏏  Top Batsmen",  self.top_batsmen),
            ("🎳  Top Bowlers",  self.top_bowlers),
            ("🥇  Team Titles",  self.team_wins),
        ]:
            self._nav_btn(sb, label, cmd)

    # ── SIDEBAR HELPERS ──────────────────────────────────────────────────────
    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Consolas", 9, "bold"),
                 bg=BG_CARD, fg=ACCENT).pack(anchor="w", padx=16, pady=(14, 4))

    def _hint(self, parent, text):
        tk.Label(parent, text=text, font=("Trebuchet MS", 8),
                 bg=BG_CARD, fg=FG_DIM).pack(anchor="w", padx=16, pady=(0, 6))

    def _divider(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=12, pady=6)

    def _nav_btn(self, parent, text, cmd):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=("Trebuchet MS", 11), bg=BG_CARD, fg=FG_MAIN,
                        activebackground=BG_MID, activeforeground=ACCENT,
                        relief="flat", bd=0, anchor="w", cursor="hand2",
                        padx=16, pady=8)
        btn.pack(fill="x", padx=8, pady=2)
        btn.bind("<Enter>", lambda e, b=btn: b.config(fg=ACCENT, bg=BG_MID))
        btn.bind("<Leave>", lambda e, b=btn: b.config(fg=FG_MAIN, bg=BG_CARD))

    def _gold_btn(self, parent, text, cmd):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=("Trebuchet MS", 11, "bold"),
                        bg=ACCENT, fg=BG_DEEP,
                        activebackground="#d4a820", activeforeground=BG_DEEP,
                        relief="flat", bd=0, cursor="hand2",
                        padx=16, pady=9)
        btn.pack(fill="x", padx=10, pady=4)

    # ── MAIN PANEL ───────────────────────────────────────────────────────────
    def _build_main(self, parent):
        main = tk.Frame(parent, bg=BG_DEEP)
        main.pack(side="right", fill="both", expand=True)

        # Stat-cards row
        self.cards_frame = tk.Frame(main, bg=BG_DEEP)
        self.cards_frame.pack(fill="x", padx=16, pady=(12, 6))
        self._reset_header_cards()

        # Chart canvas
        cf = tk.Frame(main, bg=BG_DEEP,
                      highlightthickness=1, highlightbackground=BORDER)
        cf.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.fig = plt.Figure(figsize=(10, 6), facecolor=BG_DEEP)
        self.canvas = FigureCanvasTkAgg(self.fig, cf)
        self.canvas.get_tk_widget().configure(bg=BG_DEEP, highlightthickness=0)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._show_default_image()

    # ── STAT CARDS ───────────────────────────────────────────────────────────
    def _build_stat_card(self, parent, title, value):
        card = tk.Frame(parent, bg=BG_CARD, padx=18, pady=12,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(card, text=title, font=("Trebuchet MS", 9),
                 bg=BG_CARD, fg=FG_DIM).pack(anchor="w")
        tk.Label(card, text=value, font=("Impact", 20),
                 bg=BG_CARD, fg=ACCENT).pack(anchor="w")

    def _reset_header_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        for title, val in [
            ("Total Seasons",    "17"),
            ("Total Teams",      "10+"),
            ("Total Players",    f"{len(players):,}"),
            ("Total Deliveries", f"{len(data):,}"),
        ]:
            self._build_stat_card(self.cards_frame, title, val)

    def _show_player_cards(self, runs, balls, sr, fours, sixes):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        for title, val in [
            ("Total Runs",      str(runs)),
            ("Balls Faced",     str(balls)),
            ("Strike Rate",     f"{sr:.1f}"),
            ("Fours  |  Sixes", f"{fours}  |  {sixes}"),
        ]:
            self._build_stat_card(self.cards_frame, title, val)

    # ── PLAYER FILTER ────────────────────────────────────────────────────────
    def _filter_players(self, event):
        typed  = self.player_box.get().lower()
        start  = [n for n in players if n.lower().startswith(typed)]
        others = [n for n in players
                  if not n.lower().startswith(typed) and typed in n.lower()]
        self.player_box["values"] = start + others

    # ── DEFAULT IMAGE ────────────────────────────────────────────────────────
    def _show_default_image(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        img_path = os.path.join(IMG_ROOT, "iplimg.jpg")
        if os.path.exists(img_path):
            ax.imshow(plt.imread(img_path), aspect="auto")
        else:
            ax.set_facecolor(BG_MID)
            ax.text(0.5, 0.5, "🏏  Welcome to IPL Analytics Dashboard",
                    ha="center", va="center", fontsize=18,
                    color=ACCENT, fontfamily="Impact",
                    transform=ax.transAxes)
        ax.axis("off")
        self.fig.tight_layout(pad=0)
        self.canvas.draw()
        self.status_var.set("Ready")

    # ─────────────────────────────────────────────────────────────────────────
    # CHART METHODS
    # ─────────────────────────────────────────────────────────────────────────

    # ── PLAYER STATS ─────────────────────────────────────────────────────────
    def player_stats(self):
        player = self.player_box.get().strip()
        if not player:
            return
        self.status_var.set(f"Loading stats for {player}…")

        df    = data[data["batter"] == player]
        runs  = int(df["runs_batter"].sum())
        balls = int(df["valid_ball"].sum())
        sr    = (runs / balls * 100) if balls > 0 else 0
        fours = int((df["runs_batter"] == 4).sum())
        sixes = int((df["runs_batter"] == 6).sum())

        self._show_player_cards(runs, balls, sr, fours, sixes)

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        img_path = os.path.join(IMG_ROOT, "player.png")
        if os.path.exists(img_path):
            ax.imshow(plt.imread(img_path), aspect="auto")
        else:
            ax.set_facecolor(BG_MID)
            ax.text(0.5, 0.62, player,
                    ha="center", va="center", fontsize=26,
                    fontweight="bold", color=ACCENT,
                    transform=ax.transAxes)
            ax.text(0.5, 0.50,
                    f"Runs: {runs}   |   SR: {sr:.1f}   |   4s: {fours}   |   6s: {sixes}",
                    ha="center", va="center", fontsize=13, color=FG_MAIN,
                    transform=ax.transAxes)
        ax.axis("off")
        self.fig.tight_layout(pad=0)
        self.canvas.draw()
        self.status_var.set(f"Stats loaded — {player}")

    # ── BOUNDARY CHART ───────────────────────────────────────────────────────
    def boundary_chart(self):
        player = self.player_box.get().strip()
        if not player:
            return
        self._reset_header_cards()
        df = data[data["batter"] == player]

        labels = ["Fours", "Sixes", "Singles", "Twos", "Threes", "Dots"]
        values = [
            int((df["runs_batter"] == 4).sum()),
            int((df["runs_batter"] == 6).sum()),
            int((df["runs_batter"] == 1).sum()),
            int((df["runs_batter"] == 2).sum()),
            int((df["runs_batter"] == 3).sum()),
            int((df["runs_batter"] == 0).sum()),
        ]
        colors = [ACCENT, BLUE, GREEN, RED, PURPLE, FG_DIM]

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%",
            colors=colors, startangle=140,
            wedgeprops=dict(linewidth=2, edgecolor=BG_DEEP),
            textprops=dict(color=FG_MAIN, fontsize=11),
            pctdistance=0.82,
        )
        for at in autotexts:
            at.set_fontsize(10)
            at.set_color(BG_DEEP)
            at.set_fontweight("bold")

        ax.set_title(f"{player}  •  Run Distribution",
                     color=ACCENT, fontsize=14, fontweight="bold")
        self.fig.tight_layout()
        self.canvas.draw()
        self.status_var.set(f"Boundary chart — {player}")

    # ── TOP BATSMEN ──────────────────────────────────────────────────────────
    def top_batsmen(self):
        self._reset_header_cards()
        runs = data.groupby("batter")["runs_batter"].sum().sort_values().tail(10)

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        bars = ax.barh(runs.index, runs.values,
                       color=BAR_COLORS[:len(runs)],
                       edgecolor=BG_DEEP, linewidth=0.5)
        for bar, val in zip(bars, runs.values):
            ax.text(val + 40, bar.get_y() + bar.get_height() / 2,
                    f"{int(val):,}", va="center", fontsize=9, color=ACCENT)

        ax.set_xlabel("Total Runs", color=FG_DIM, fontsize=10)
        ax.set_title("Top 10 IPL Batsmen — All-time Runs",
                     color=ACCENT, fontsize=14, fontweight="bold")
        ax.tick_params(axis="y", labelcolor=FG_MAIN, labelsize=10)
        ax.set_xlim(0, runs.max() * 1.15)
        self.fig.tight_layout()
        self.canvas.draw()
        self.status_var.set("Top 10 Batsmen loaded")

    # ── TOP BOWLERS ──────────────────────────────────────────────────────────
    def top_bowlers(self):
        self._reset_header_cards()
        wickets = (data[data["player_out"].notna()]
                   .groupby("bowler")["player_out"].count()
                   .sort_values().tail(10))

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        bars = ax.barh(wickets.index, wickets.values,
                       color=BAR_COLORS[:len(wickets)],
                       edgecolor=BG_DEEP, linewidth=0.5)
        for bar, val in zip(bars, wickets.values):
            ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
                    str(int(val)), va="center", fontsize=9, color=ACCENT)

        ax.set_xlabel("Total Wickets", color=FG_DIM, fontsize=10)
        ax.set_title("Top 10 IPL Bowlers — All-time Wickets",
                     color=ACCENT, fontsize=14, fontweight="bold")
        ax.tick_params(axis="y", labelcolor=FG_MAIN, labelsize=10)
        ax.set_xlim(0, wickets.max() * 1.15)
        self.fig.tight_layout()
        self.canvas.draw()
        self.status_var.set("Top 10 Bowlers loaded")

    # ── TEAM TITLES ──────────────────────────────────────────────────────────
    def team_wins(self):
        self._reset_header_cards()
        teams = list(team_titles.keys())
        wins  = list(team_titles.values())
        gold_shades = ["#f0c040", "#e6b535", "#dba92a", "#d19e1f",
                       "#c79314", "#bd8809", "#b37d00"]

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        colors_used = [gold_shades[i % len(gold_shades)] for i in range(len(teams))]
        bars = ax.barh(teams, wins, color=colors_used,
                       edgecolor=BG_DEEP, linewidth=0.8)
        for bar, val in zip(bars, wins):
            ax.text(val + 0.08, bar.get_y() + bar.get_height() / 2,
                    "🏆" * val, va="center", fontsize=11)

        ax.set_xlabel("IPL Titles", color=FG_DIM, fontsize=10)
        ax.set_title("IPL Title Count by Franchise",
                     color=ACCENT, fontsize=14, fontweight="bold")
        ax.tick_params(axis="y", labelcolor=FG_MAIN, labelsize=10)
        ax.set_xlim(0, max(wins) + 1.5)
        self.fig.tight_layout()
        self.canvas.draw()
        self.status_var.set("Team titles loaded")

    # ── WAGON WHEEL ──────────────────────────────────────────────────────────
    def wagon_wheel(self):
        player = self.player_box.get().strip()
        if not player:
            return
        df         = data[data["batter"] == player]
        total_runs = df["runs_batter"].sum()
        if total_runs == 0:
            self.status_var.set(f"No data for {player}")
            return

        directions = 12
        angles  = np.linspace(0, 2 * np.pi, directions, endpoint=False)
        fours   = int((df["runs_batter"] == 4).sum())
        sixes   = int((df["runs_batter"] == 6).sum())
        singles = int((df["runs_batter"] == 1).sum())
        twos    = int((df["runs_batter"] == 2).sum())

        seed = np.array([fours, sixes, singles, twos,
                         fours, sixes, singles, fours,
                         sixes, singles, twos, fours], dtype=float)
        seed = np.where(seed == 0, 1, seed)
        seed += np.random.uniform(0, seed.mean() * 0.3, size=directions)
        runs_dist = seed / seed.sum() * total_runs

        grad_colors = plt.cm.YlOrBr(np.linspace(0.3, 0.95, directions))

        self.fig.clear()
        ax = self.fig.add_subplot(111, polar=True)
        ax.set_facecolor(BG_MID)
        ax.bar(angles, runs_dist, width=0.48, color=grad_colors,
               edgecolor=BG_DEEP, linewidth=1, alpha=0.92)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_title(f"{player}  •  Wagon Wheel", va="bottom",
                     color=ACCENT, fontsize=14, fontweight="bold")
        ax.spines["polar"].set_color(BORDER)
        self.fig.tight_layout()
        self.canvas.draw()
        self.status_var.set(f"Wagon wheel — {player}")

    # ── SCATTER PLOT ─────────────────────────────────────────────────────────
    def scatter_plot(self):
        self._reset_header_cards()
        grouped = (data.groupby("batter")
                   .agg({"runs_batter": "sum", "valid_ball": "sum"})
                   .reset_index())
        grouped = grouped[grouped["valid_ball"] >= 50]
        grouped["strike_rate"] = grouped["runs_batter"] / grouped["valid_ball"] * 100

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        sc = ax.scatter(grouped["runs_batter"], grouped["strike_rate"],
                        c=grouped["strike_rate"], cmap="YlOrBr",
                        alpha=0.75, s=28, linewidths=0.3, edgecolors=BG_DEEP)

        cbar = self.fig.colorbar(sc, ax=ax)
        cbar.set_label("Strike Rate", color=FG_DIM, fontsize=9)
        cbar.ax.yaxis.set_tick_params(color=FG_DIM, labelcolor=FG_DIM)

        top5 = grouped.nlargest(5, "runs_batter")
        for _, row in top5.iterrows():
            ax.annotate(row["batter"],
                        xy=(row["runs_batter"], row["strike_rate"]),
                        xytext=(8, 4), textcoords="offset points",
                        fontsize=8, color=ACCENT)

        ax.set_xlabel("Total Runs", color=FG_DIM, fontsize=10)
        ax.set_ylabel("Strike Rate", color=FG_DIM, fontsize=10)
        ax.set_title("Runs vs Strike Rate  (≥ 50 balls faced)",
                     color=ACCENT, fontsize=14, fontweight="bold")
        self.fig.tight_layout()
        self.canvas.draw()
        self.status_var.set("Runs vs Strike Rate loaded")

    # ── IPL WINNER ───────────────────────────────────────────────────────────
    def ipl_winner(self):
        year_str = self.year_box.get().strip()
        if not year_str:
            return
        year = int(year_str)
        if year not in ipl_winners:
            self.status_var.set("Winner data unavailable")
            return

        team   = ipl_winners[year]
        titles = team_titles.get(team, 0)

        for w in self.cards_frame.winfo_children():
            w.destroy()
        for title, val in [
            ("Season",       str(year)),
            ("🏆 Champion",  team),
            ("Total Titles", str(titles)),
            ("Trophy Count", "🏆" * titles),
        ]:
            self._build_stat_card(self.cards_frame, title, val)

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        img_path = os.path.join(IMG_ROOT, f"{year}.jpg")
        if os.path.exists(img_path):
            ax.imshow(plt.imread(img_path), aspect="auto")
        else:
            ax.set_facecolor(BG_MID)
            ax.text(0.5, 0.62, f"IPL {year}",
                    ha="center", va="center", fontsize=36,
                    fontfamily="Impact", color=ACCENT,
                    transform=ax.transAxes)
            ax.text(0.5, 0.50, "🏆",
                    ha="center", va="center", fontsize=52,
                    fontfamily="Segoe UI Emoji",
                    transform=ax.transAxes)
            ax.text(0.5, 0.38, team,
                    ha="center", va="center", fontsize=22,
                    fontweight="bold", color=FG_MAIN,
                    transform=ax.transAxes)
            ax.text(0.5, 0.28,
                    f"{titles} IPL Title{'s' if titles > 1 else ''}",
                    ha="center", va="center", fontsize=14, color=FG_DIM,
                    transform=ax.transAxes)

        ax.axis("off")
        self.fig.tight_layout(pad=0)
        self.canvas.draw()
        self.status_var.set(f"IPL {year} Winner — {team}")


# ── RUN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app  = IPLDashboard(root)
    root.mainloop()


