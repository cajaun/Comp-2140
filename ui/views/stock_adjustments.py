import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import *
from data.db import get_db
from data.models import StockAdjust, Item, User
from datetime import datetime

class StockAdjustmentsView(ttk.Frame):
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
        ttk.Label(header, text="Stock Adjustments", style="H1.TLabel").pack(side="left")

        content = ttk.Frame(container)
        content.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(content, text="Record Adjustment", padding=20)
        form_frame.pack(side="left", fill="y", padx=(0, 20), anchor="n")

        ttk.Label(form_frame, text="Item").pack(anchor="w", pady=(0, 5))
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(form_frame, textvariable=self.item_var)
        self.item_combo.pack(fill="x", pady=(0, 10))

        ttk.Label(form_frame, text="Type").pack(anchor="w", pady=(0, 5))
        self.type_var = tk.StringVar(value="Increase")
        ttk.Combobox(form_frame, textvariable=self.type_var, values=["Increase", "Decrease"]).pack(fill="x", pady=(0, 10))

        ttk.Label(form_frame, text="Quantity").pack(anchor="w", pady=(0, 5))
        self.qty_entry = ttk.Entry(form_frame)
        self.qty_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(form_frame, text="Reason").pack(anchor="w", pady=(0, 5))
        self.reason_entry = ttk.Entry(form_frame)
        self.reason_entry.pack(fill="x", pady=(0, 10))

        ttk.Button(form_frame, text="Record Adjustment", style="Primary.TButton", command=self.record_adjustment).pack(fill="x", pady=20)

        table_frame = ttk.Frame(content)
        table_frame.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Item", "Type", "Qty", "Reason", "User", "Date"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Item", text="Item")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Qty", text="Qty")
        self.tree.heading("Reason", text="Reason")
        self.tree.heading("User", text="User")
        self.tree.heading("Date", text="Date")

        self.tree.column("ID", width=50)
        self.tree.column("Item", width=150)
        self.tree.column("Type", width=80)
        self.tree.column("Qty", width=80)
        self.tree.column("Reason", width=200)
        self.tree.column("User", width=100)
        self.tree.column("Date", width=150)

        self.tree.pack(fill="both", expand=True)

    def refresh_data(self):
        try:
            items = self.db.query(Item).all()
            self.item_map = {f"{i.name} (ID: {i.item_id})": i.item_id for i in items}
            self.item_combo['values'] = list(self.item_map.keys())
        except Exception as e:
            print(f"Error fetching items: {e}")


        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            adjustments = self.db.query(StockAdjust).order_by(StockAdjust.created_at.desc()).all()
            for adj in adjustments:
                item_name = adj.item.name if adj.item else "Unknown"
                user_name = adj.user.username if adj.user else "Unknown"
                self.tree.insert("", "end", values=(adj.adjust_id, item_name, adj.adjust_type, adj.quantity, adj.reason, user_name, adj.created_at))
        except Exception as e:
            print(f"Error fetching adjustments: {e}")

    def record_adjustment(self):
        try:
            item_selection = self.item_var.get()
            if not item_selection:
                messagebox.showwarning("Missing Data", "Please select an item.")
                return
            
            item_id = self.item_map.get(item_selection)
            adj_type = self.type_var.get()
            qty = int(self.qty_entry.get())
            reason = self.reason_entry.get()

          
            item = self.db.query(Item).filter(Item.item_id == item_id).first()
            if not item:
                messagebox.showerror("Error", "Item not found.")
                return

            if adj_type == "Increase":
                item.current_stock += qty
            elif adj_type == "Decrease":
                if item.current_stock < qty:
                    messagebox.showwarning("Stock Error", "Insufficient stock for this decrease.")
                    return
                item.current_stock -= qty

         
            user = self.db.query(User).first()
            user_id = user.user_id if user else None

            adjust = StockAdjust(
                item_id=item_id,
                user_id=user_id,
                adjust_type=adj_type,
                quantity=qty,
                reason=reason,
                created_at=datetime.utcnow()
            )
            
            self.db.add(adjust)
            self.db.commit()
            
            messagebox.showinfo("Success", "Stock adjustment recorded.")
            self.refresh_data()
            
            self.qty_entry.delete(0, 'end')
            self.reason_entry.delete(0, 'end')

        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
