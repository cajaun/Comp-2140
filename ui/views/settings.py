import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import *
from data.db import get_db
from data.models import Config
from datetime import datetime

class SettingsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.db = next(get_db())
        self.current_tab = "System"
        self.setup_ui()

    def setup_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header, text="Settings", style="H1.TLabel").pack(anchor="w")
        ttk.Label(header, text="Manage global system parameters.", foreground=MUTED_FOREGROUND).pack(anchor="w")
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        sidebar = ttk.Frame(main_frame, width=200)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        
        items = ["System", "Logs"]
        self.nav_buttons = {}
        
        for item in items:
            style_name = "Primary.TButton" if item == self.current_tab else "Ghost.TButton"
            btn = ttk.Button(sidebar, text=item, style=style_name, command=lambda i=item: self.navigate(i))
            btn.pack(fill="x", pady=2)
            self.nav_buttons[item] = btn
            
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        self.render_system()

    def navigate(self, tab):
        self.nav_buttons[self.current_tab].configure(style="Ghost.TButton")
        self.current_tab = tab
        self.nav_buttons[self.current_tab].configure(style="Primary.TButton")
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if tab == "System":
            self.render_system()
        elif tab == "Logs":
            self.render_logs()

    def render_system(self):
        ttk.Label(self.content_frame, text="System Configuration", style="H2.TLabel").pack(anchor="w", pady=(0, 20))
        
        self.entries = {}
        
        configs = {c.parameter_name: c.parameter_value for c in self.db.query(Config).all()}
        
        fields = [
            ("default_reorder_level", "Default Reorder Level", "10"),
            ("report_default_format", "Report Default Format", "CSV"),
            ("sm_threshold_days", "Slow Moving Threshold (Days)", "30"),
            ("notifications_enabled", "Notifications Enabled", "True")
        ]
        
        for key, label, default in fields:
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill="x", pady=10)
            
            ttk.Label(frame, text=label, font=(FONT_FAMILY, FONT_SIZE_BASE, "bold")).pack(anchor="w")
            
            entry = ttk.Entry(frame)
            entry.insert(0, configs.get(key, default))
            entry.pack(fill="x", pady=(5, 0))
            
            self.entries[key] = entry
            
        ttk.Button(self.content_frame, text="Save Changes", style="Primary.TButton", command=self.save_settings).pack(anchor="w", pady=20)

    def save_settings(self):
        try:
            for key, entry in self.entries.items():
                val = entry.get()
                cfg = self.db.query(Config).filter_by(parameter_name=key).first()
                if cfg:
                    cfg.parameter_value = val
                else:
                    cfg = Config(parameter_name=key, parameter_value=val)
                    self.db.add(cfg)
            
            self.db.commit()
            messagebox.showinfo("Success", "Settings updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {e}")

    def render_logs(self):
        ttk.Label(self.content_frame, text="Configuration Logs", style="H2.TLabel").pack(anchor="w", pady=(0, 20))
        
        tree = ttk.Treeview(self.content_frame, columns=("Parameter", "Value", "Last Updated"), show="headings")
        tree.heading("Parameter", text="Parameter")
        tree.heading("Value", text="Value")
        tree.heading("Last Updated", text="Last Updated")
        
        tree.column("Parameter", width=200)
        tree.column("Value", width=200)
        tree.column("Last Updated", width=200)
        
        tree.pack(fill="both", expand=True)
        
        try:
            configs = self.db.query(Config).order_by(Config.updated_at.desc()).all()
            for c in configs:
                tree.insert("", "end", values=(c.parameter_name, c.parameter_value, c.updated_at))
        except Exception as e:
            print(f"Error loading logs: {e}")
