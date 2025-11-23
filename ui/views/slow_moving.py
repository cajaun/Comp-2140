import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import *
from data.db import get_db
from data.models import SlowMovingOverstock, Item, Config
from datetime import datetime, timedelta

class SlowMovingView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.db = next(get_db())
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = ttk.Frame(self, padding=(20, 0, 20, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(20, 20))
        ttk.Label(header, text="Slow-Moving / Overstock", style="H1.TLabel").pack(side="left")

        content = ttk.Frame(container)
        content.pack(fill="both", expand=True)

        settings_frame = ttk.LabelFrame(content, text="Configuration", padding=20)
        settings_frame.pack(side="left", fill="y", padx=(0, 20), anchor="n")

        ttk.Label(settings_frame, text="Threshold Days").pack(anchor="w", pady=(0, 5))
        self.days_entry = ttk.Entry(settings_frame)
        self.days_entry.insert(0, "30") # Default
        self.days_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(settings_frame, text="Threshold Quantity").pack(anchor="w", pady=(0, 5))
        self.qty_entry = ttk.Entry(settings_frame)
        self.qty_entry.insert(0, "100") # Default
        self.qty_entry.pack(fill="x", pady=(0, 10))

        ttk.Button(settings_frame, text="Update Settings & Scan", style="Primary.TButton", command=self.run_scan).pack(fill="x", pady=20)


        table_frame = ttk.Frame(content)
        table_frame.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Item", "Stock", "Last Sold", "Days Since", "Suggestion"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Item", text="Item")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Last Sold", text="Last Sold")
        self.tree.heading("Days Since", text="Days Since")
        self.tree.heading("Suggestion", text="Suggestion")

        self.tree.column("ID", width=50)
        self.tree.column("Item", width=150)
        self.tree.column("Stock", width=80)
        self.tree.column("Last Sold", width=100)
        self.tree.column("Days Since", width=100)
        self.tree.column("Suggestion", width=200)

        self.tree.pack(fill="both", expand=True)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Remove Flag", command=self.remove_flag)

    def refresh_data(self):
        # Load config from the db
        try:
            days_cfg = self.db.query(Config).filter_by(parameter_name="sm_threshold_days").first()
            qty_cfg = self.db.query(Config).filter_by(parameter_name="sm_threshold_qty").first()
            
            if days_cfg:
                self.days_entry.delete(0, 'end')
                self.days_entry.insert(0, days_cfg.parameter_value)
            if qty_cfg:
                self.qty_entry.delete(0, 'end')
                self.qty_entry.insert(0, qty_cfg.parameter_value)
                
        except Exception as e:
            print(f"Error loading config: {e}")

        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            flags = self.db.query(SlowMovingOverstock).all()
            for flag in flags:
                item_name = flag.item.name if flag.item else "Unknown"
                days_since = (datetime.utcnow() - flag.last_sold_date).days if flag.last_sold_date else "N/A"
                self.tree.insert("", "end", values=(flag.sm_id, item_name, flag.stock_quantity, flag.last_sold_date, days_since, flag.suggested_action))
        except Exception as e:
            print(f"Error loading flags: {e}")

    def run_scan(self):
        try:
            days = int(self.days_entry.get())
            qty = int(self.qty_entry.get())
            
   
            self.update_config("sm_threshold_days", str(days))
            self.update_config("sm_threshold_qty", str(qty))
            
            # testing something with the mock data?
            # with real data, we should query the sales history
            # for now we can just find items with stock > qty and create a record if not exists frl
            
            items = self.db.query(Item).filter(Item.current_stock > qty).all()
            count = 0
            for item in items:
                # Check if already flagged
                existing = self.db.query(SlowMovingOverstock).filter_by(item_id=item.item_id).first()
                if not existing:
                    # Mock last sold date
                    last_sold = datetime.utcnow() - timedelta(days=days + 5) 
                    
                    flag = SlowMovingOverstock(
                        item_id=item.item_id,
                        last_sold_date=last_sold,
                        stock_quantity=item.current_stock,
                        threshold_days=days,
                        threshold_quantity=qty,
                        suggested_action="Discount / Bundle",
                        flagged_at=datetime.utcnow()
                    )
                    self.db.add(flag)
                    count += 1
            
            self.db.commit()
            messagebox.showinfo("Scan Complete", f"Scanned items. Flagged {count} new items.")
            self.refresh_data()
            
        except ValueError:
            messagebox.showerror("Error", "Thresholds must be numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"Scan failed: {e}")

    def update_config(self, name, value):
        cfg = self.db.query(Config).filter_by(parameter_name=name).first()
        if cfg:
            cfg.parameter_value = value
        else:
            cfg = Config(parameter_name=name, parameter_value=value)
            self.db.add(cfg)
        self.db.commit()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def remove_flag(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        sm_id = item['values'][0]
        
        flag = self.db.query(SlowMovingOverstock).filter(SlowMovingOverstock.sm_id == sm_id).first()
        if flag:
            self.db.delete(flag)
            self.db.commit()
            self.refresh_data()
