import tkinter as tk
from tkinter import ttk
from ui.styles import *
from data.mock_data import generate_stats, generate_revenue_data, generate_visitors_data, generate_activity
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches
import numpy as np
from data.db import get_db
from data.models import Item, StockAdjust


class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.db = next(get_db())

        self.canvas = tk.Canvas(self, bg=BACKGROUND, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.setup_ui()


 
    def setup_ui(self):
 
        header_frame = ttk.Frame(self.scrollable_frame, padding=(20, 20, 30, 10))
        header_frame.pack(fill="x")

        ttk.Label(header_frame, text="Dashboard", style="H1.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text="Overview of your inventory and performance.",
                  foreground=MUTED_FOREGROUND).pack(anchor="w", pady=(5, 0))

        actions_frame = ttk.Frame(self.scrollable_frame, padding=(20, 0, 20, 20))
        actions_frame.pack(fill="x")
        
        ttk.Label(actions_frame, text="Quick Actions", style="H2.TLabel").pack(anchor="w", pady=(0, 10))
        
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack(anchor="w")
        
    
        def nav(view):
            app = self.winfo_toplevel()
            if hasattr(app, 'navigate'):
                app.navigate(view)

        ttk.Button(btn_frame, text="Add Product", style="Primary.TButton", command=lambda: nav("inventory")).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Adjust Stock", style="Outline.TButton", command=lambda: nav("stock_adjustments")).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Generate Report", style="Outline.TButton", command=lambda: nav("reports")).pack(side="left", padx=5)



        container = ttk.Frame(self.scrollable_frame, padding=(10, 10))
        container.pack(fill="x")


        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=1)

 
        stats_grid = ttk.Frame(container)
        stats_grid.grid(row=0, column=0, sticky="nsew")

        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)

      
        total_items = self.db.query(Item).count()
        low_stock = self.db.query(Item).filter(Item.current_stock < 10).count() 
        
        self.create_stat_card(stats_grid, "Total Items", str(total_items),
                              "Active products", row=0, col=0)

        self.create_stat_card(stats_grid, "Low Stock Alerts", str(low_stock),
                              "Items below reorder level", row=0, col=1)

        self.create_stat_card(stats_grid, "Total Visitors", "8,344",
                              "-14.2% today", row=1, col=0)

        self.create_stat_card(stats_grid, "Pending Orders", "12",
                              "Needs processing", row=1, col=1)

      
        charts_column = ttk.Frame(container)
        charts_column.grid(row=0, column=1, sticky="ne", padx=(20, 0))

        self.create_radar_chart(charts_column)  
        self.create_small_revenue_chart(charts_column)
        self.create_small_pie_chart(charts_column)
        

        bottom_frame = ttk.Frame(self.scrollable_frame, padding=(10, 20))
        bottom_frame.pack(fill="x", pady=(0, 20))

        self.create_activity_list(bottom_frame)



    def create_stat_card(self, parent, title, value, subtext, row, col):
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        card = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        card.pack(fill="both", expand=True)

        tk.Label(card, text=title, bg=CARD, fg=MUTED_FOREGROUND,
                 font=(FONT_FAMILY, FONT_SIZE_SM, "bold")).pack(anchor="w")

        tk.Label(card, text=value, bg=CARD, fg=FOREGROUND,
                 font=(FONT_FAMILY, FONT_SIZE_3XL, "bold")).pack(anchor="w", pady=(10, 0))

        tk.Label(card, text=subtext, bg=CARD, fg=MUTED_FOREGROUND,
                 font=(FONT_FAMILY, FONT_SIZE_SM)).pack(anchor="w")



    def create_small_revenue_chart(self, parent):
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.pack(fill="x", pady=(0, 20))

        frame = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        frame.pack(fill="x")

        tk.Label(frame, text="Revenue (Mini)", bg=CARD, fg=FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_XL, "bold")).pack(anchor="w", pady=(0, 10))

        data = generate_revenue_data()

        fig = Figure(figsize=(3.4, 2.5), dpi=100)
        fig.patch.set_facecolor(CARD)

        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        x = range(len(data["labels"]))
        width = 0.28

        ax.bar([i - width/2 for i in x], data["Soft drinks"], width, label="Soft drinks", color=ACCENT)
        ax.bar([i + width/2 for i in x], data["Frozen foods"], width, label="Frozen foods", color=PRIMARY)

        ax.set_xticks(x)
        ax.set_xticklabels(data["labels"])
        ax.legend(frameon=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()



    def create_small_pie_chart(self, parent):
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.pack(fill="x", pady=(0, 20))

        frame = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        frame.pack(fill="x")

        tk.Label(frame, text="Visitors Breakdown", bg=CARD, fg=FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_XL, "bold")).pack(anchor="w", pady=(0, 10))

        data = generate_visitors_data()

        fig = Figure(figsize=(3.2, 2.4), dpi=100)
        fig.patch.set_facecolor(CARD)
        ax = fig.add_subplot(111)

        colors = [PRIMARY, ACCENT, MUTED_FOREGROUND]

        ax.pie(
            data["values"],
            labels=data["labels"],
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops=dict(color=FOREGROUND)
        )

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()



    def create_radar_chart(self, parent):
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.pack(fill="x", anchor="e")

        frame = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Sales By Month", bg=CARD, fg=FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_2XL, "bold")).pack(anchor="w")

        tk.Label(frame, text="Showing total sales for the last 6 months", bg=CARD,
                fg=MUTED_FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_SM)).pack(anchor="w", pady=(0, 10))

        labels = ["January", "February", "March", "April", "May", "June"]

        values1 = [150, 180, 165, 140, 160, 175]
        values2 = [145, 170, 158, 135, 150, 168]

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
        values1 += values1[:1]
        values2 += values2[:1]
        angles = np.append(angles, angles[0])

        fig = Figure(figsize=(4.0, 3.0), dpi=100)
        fig.patch.set_facecolor(CARD)
        ax = fig.add_subplot(111, polar=True)
        ax.set_facecolor(CARD)

        ax.plot(angles, values1, color=ACCENT, linewidth=2)
        ax.fill(angles, values1, color=ACCENT, alpha=0.1)

        ax.plot(angles, values2, color=PRIMARY, linewidth=2)
        ax.fill(angles, values2, color=PRIMARY, alpha=0.1)

        ax.set_xticks(np.linspace(0, 2 * np.pi, len(labels), endpoint=False))
        ax.set_xticklabels(labels, color=FOREGROUND)
        ax.grid(color=BORDER)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)



    def create_activity_list(self, parent):
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.pack(side="left", fill="both", expand=True, padx=(10, 10))

        frame = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Recent Activity", bg=CARD, fg=FOREGROUND,
                 font=(FONT_FAMILY, FONT_SIZE_2XL, "bold")).pack(anchor="w", pady=(0, 20))

        activities = generate_activity()

        for act in activities:
            row = tk.Frame(frame, bg=CARD, pady=10)
            row.pack(fill="x")

            av = tk.Canvas(row, width=40, height=40, bg=CARD, highlightthickness=0)
            av.create_oval(0, 0, 40, 40, fill=SECONDARY)
            av.create_text(20, 20, text=act["user"][:2].upper(),
                           fill=SECONDARY_FOREGROUND,
                           font=(FONT_FAMILY, FONT_SIZE_SM, "bold"))
            av.pack(side="left", padx=(0, 15))

            info = tk.Frame(row, bg=CARD)
            info.pack(side="left")
            tk.Label(info, text=act["user"], bg=CARD, fg=FOREGROUND,
                     font=(FONT_FAMILY, FONT_SIZE_BASE, "bold")).pack(anchor="w")
            tk.Label(info, text=act["email"], bg=CARD, fg=MUTED_FOREGROUND,
                     font=(FONT_FAMILY, FONT_SIZE_SM)).pack(anchor="w")

            tk.Label(row, text=act["amount"], bg=CARD, fg=FOREGROUND,
                     font=(FONT_FAMILY, FONT_SIZE_BASE, "bold")).pack(side="right")
