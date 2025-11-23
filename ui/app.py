import tkinter as tk
from tkinter import ttk
from ui.styles import *
from ui.components.sidebar import Sidebar
from ui.views.dashboard import DashboardView
from ui.views.users import UsersView
from ui.views.settings import SettingsView
from ui.views.inventory import InventoryView
from ui.views.categories import CategoriesView
from ui.views.stock_adjustments import StockAdjustmentsView
from ui.views.damaged_expired import DamagedExpiredView
from ui.views.reports import ReportsView
from ui.views.slow_moving import SlowMovingView
from data.db import init_db

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Braeton Gate Wholesale")
        self.geometry("1400x900")
        self.configure(bg=BACKGROUND)
        
        setup_styles(self)
        
        # initialize the database
        try:
            init_db()
        except Exception as e:
            print(f"DB Init Error: {e}")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = Sidebar(self, self.navigate)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        sep = tk.Frame(self, bg=MUTED, width=1)
        sep.grid(row=0, column=1, sticky="ns")
        
        self.content_area = ttk.Frame(self, style="TFrame", padding=(0, 0, 20, 20))
        self.content_area.grid(row=0, column=2, sticky="nsew")
        
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1) # Row 1 is for views
        
        top_sep = tk.Frame(self.content_area, bg=MUTED, height=1)
        top_sep.grid(row=0, column=0, sticky="ew", pady=(60, 20))

        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0) 
        self.grid_columnconfigure(2, weight=1) 
        
        self.views = {}
        self.current_view = None
        
        # start the views with the dashboard
        self.navigate("dashboard")

    def navigate(self, view_name):
        
        # going to do some lazy loading for optimizations
        # only create the view if it doesn't exist
        if view_name not in self.views:
            if view_name == "dashboard":
                self.views[view_name] = DashboardView(self.content_area)
            elif view_name == "users":
                self.views[view_name] = UsersView(self.content_area)
            elif view_name == "settings":
                self.views[view_name] = SettingsView(self.content_area)
            elif view_name == "inventory":
                self.views[view_name] = InventoryView(self.content_area)
            elif view_name == "categories":
                self.views[view_name] = CategoriesView(self.content_area)
            elif view_name == "stock_adjustments":
                self.views[view_name] = StockAdjustmentsView(self.content_area)
            elif view_name == "damaged_expired":
                self.views[view_name] = DamagedExpiredView(self.content_area)
            elif view_name == "reports":
                self.views[view_name] = ReportsView(self.content_area)
            elif view_name == "slow_moving":
                self.views[view_name] = SlowMovingView(self.content_area)
            else:
                print(f"View {view_name} not implemented")
                return
            
            # then we grid the new view 
            # by this we just stacke on top of others in the same cell
            self.views[view_name].grid(row=1, column=0, sticky="nsew")

        # since it is now stacked
        # bring the requested view to the top
        self.views[view_name].tkraise()
        self.current_view = self.views[view_name]
