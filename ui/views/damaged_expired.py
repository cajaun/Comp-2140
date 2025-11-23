import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import *
from data.db import get_db
from data.models import ItemCondition, Item
from datetime import datetime

class DamagedExpiredView(ttk.Frame):
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
        ttk.Label(header, text="Damaged / Expired Items", style="H1.TLabel").pack(side="left")

        content = ttk.Frame(container)
        content.pack(fill="both", expand=True)


        form_frame = ttk.LabelFrame(content, text="Record Condition", padding=20)
        form_frame.pack(side="left", fill="y", padx=(0, 20), anchor="n")

        ttk.Label(form_frame, text="Item").pack(anchor="w", pady=(0, 5))
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(form_frame, textvariable=self.item_var)
        self.item_combo.pack(fill="x", pady=(0, 10))

        ttk.Label(form_frame, text="Condition Type").pack(anchor="w", pady=(0, 5))
        self.condition_var = tk.StringVar(value="Damaged")
        ttk.Combobox(form_frame, textvariable=self.condition_var, values=["Damaged", "Expired", "Spoiled"]).pack(fill="x", pady=(0, 10))

        ttk.Label(form_frame, text="Quantity").pack(anchor="w", pady=(0, 5))
        self.qty_entry = ttk.Entry(form_frame)
        self.qty_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(form_frame, text="Reason / Cause").pack(anchor="w", pady=(0, 5))
        self.reason_entry = ttk.Entry(form_frame)
        self.reason_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(form_frame, text="Cost Impact ($)").pack(anchor="w", pady=(0, 5))
        self.cost_entry = ttk.Entry(form_frame)
        self.cost_entry.pack(fill="x", pady=(0, 10))

        ttk.Button(form_frame, text="Record & Deduct Stock", style="Primary.TButton", command=self.record_condition).pack(fill="x", pady=20)

       
        table_frame = ttk.Frame(content)
        table_frame.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Item", "Condition", "Qty", "Reason", "Cost", "Date"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Item", text="Item")
        self.tree.heading("Condition", text="Condition")
        self.tree.heading("Qty", text="Qty")
        self.tree.heading("Reason", text="Reason")
        self.tree.heading("Cost", text="Cost Impact")
        self.tree.heading("Date", text="Date")

        self.tree.column("ID", width=50)
        self.tree.column("Item", width=150)
        self.tree.column("Condition", width=100)
        self.tree.column("Qty", width=80)
        self.tree.column("Reason", width=200)
        self.tree.column("Cost", width=100)
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
            conditions = self.db.query(ItemCondition).order_by(ItemCondition.recorded_at.desc()).all()
            for cond in conditions:
                item_name = cond.item.name if cond.item else "Unknown"
                self.tree.insert("", "end", values=(cond.condition_id, item_name, cond.condition_type, cond.quantity, cond.reason, f"${cond.cost_impact:.2f}", cond.recorded_at))
        except Exception as e:
            print(f"Error fetching conditions: {e}")

    def record_condition(self):
        try:
            item_selection = self.item_var.get()
            if not item_selection:
                messagebox.showwarning("Missing Data", "Please select an item.")
                return
            
            item_id = self.item_map.get(item_selection)
            condition = self.condition_var.get()
            qty = int(self.qty_entry.get())
            reason = self.reason_entry.get()
            cost = float(self.cost_entry.get())

            item = self.db.query(Item).filter(Item.item_id == item_id).first()
            if not item:
                messagebox.showerror("Error", "Item not found.")
                return

            if item.current_stock < qty:
                messagebox.showwarning("Stock Error", "Insufficient stock to deduct.")
                return

        
            item.current_stock -= qty

          
            cond = ItemCondition(
                item_id=item_id,
                condition_type=condition,
                quantity=qty,
                reason=reason,
                cost_impact=cost,
                recorded_at=datetime.utcnow()
            )
            
            self.db.add(cond)
            self.db.commit()
            
            messagebox.showinfo("Success", "Condition recorded and stock deducted.")
            self.refresh_data()
            
            self.qty_entry.delete(0, 'end')
            self.reason_entry.delete(0, 'end')
            self.cost_entry.delete(0, 'end')

        except ValueError:
            messagebox.showerror("Input Error", "Quantity and Cost must be numbers.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
