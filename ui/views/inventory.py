import tkinter as tk
from tkinter import ttk, Canvas, messagebox
from ui.styles import *
from data.db import get_db, init_db
from data.models import Item, Category

class InventoryView(ttk.Frame):
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

        title_row = ttk.Frame(header)
        title_row.pack(fill="x")

        ttk.Label(
            title_row,
            text="Inventory Management",
            style="H1.TLabel"
        ).pack(side="left")

        actions = ttk.Frame(title_row)
        actions.pack(side="right")

        ttk.Button(actions, text="Add Product", style="Primary.TButton", command=self.add_item_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Edit", style="Outline.TButton", command=self.edit_item_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Delete", style="Outline.TButton", command=self.delete_item).pack(side="left", padx=5)


        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill="x", pady=(0, 20))

        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)

        self.create_stat_card(stats_frame, "Total Products", "0", "Across all categories", 0)
        self.create_stat_card(stats_frame, "Low Stock", "0", "Needs restocking soon", 1)
        self.create_stat_card(stats_frame, "Out of Stock", "0", "Currently unavailable", 2)
        self.create_stat_card(stats_frame, "Categories", "0", "Organized product groups", 3)


        filter_frame = ttk.Frame(container)
        filter_frame.pack(fill="x", pady=(0, 15))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.refresh_data())
        search = ttk.Entry(filter_frame, width=50, font=(FONT_FAMILY, 10), textvariable=self.search_var)
        search.pack(side="left", padx=(0, 4), ipady=4)
        
        ttk.Button(filter_frame, text="Category", style="Outline.TButton")\
            .pack_configure(side="left", padx=5, pady=0)

        ttk.Button(filter_frame, text="Stock", style="Outline.TButton")\
            .pack_configure(side="left", padx=5, pady=0)
        

        self.tree = ttk.Treeview(container, columns=("ID", "Name", "Category", "Price", "Stock", "Unit"), show="headings")

        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Unit", text="Unit")

        self.tree.column("ID", width=50)
        self.tree.column("Name", width=200)
        self.tree.column("Category", width=100)
        self.tree.column("Price", width=100)
        self.tree.column("Stock", width=100)
        self.tree.column("Unit", width=80)

        self.tree.pack(fill="both", expand=True, pady=(10, 0))

        
    def create_stat_card(self, parent, title, value, subtext, col):

        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.grid(row=0, column=col, padx=10, sticky="nsew")

        card = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        card.pack(fill="both", expand=True)

        tk.Label(card, text=title, bg=CARD, fg=MUTED_FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_SM, "bold")).pack(anchor="w")

        label_value = tk.Label(card, text=value, bg=CARD, fg=FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_2XL, "bold"))
        label_value.pack(anchor="w", pady=(8, 0))
        
        # Store reference to update later
        if title == "Total Products": self.lbl_total = label_value
        elif title == "Low Stock": self.lbl_low = label_value
        elif title == "Out of Stock": self.lbl_out = label_value
        elif title == "Categories": self.lbl_cats = label_value

        tk.Label(card, text=subtext, bg=CARD, fg=MUTED_FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_SM)).pack(anchor="w", pady=(5, 0))


    def refresh_data(self):
        search_query = self.search_var.get().lower()
        
        # clear existing data from the tree frames 
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # fetch data from the postgre database
        try:
            query = self.db.query(Item)
            items = query.all()
            
           
            filtered_items = []
            for item in items:
                if search_query and search_query not in item.name.lower():
                    continue
                filtered_items.append(item)
            
            for item in filtered_items:
                cat_name = item.category.name if item.category else "-"
                self.tree.insert("", "end", values=(item.item_id, item.name, cat_name, f"${item.price:.2f}", item.current_stock, item.unit))
                
            # Update stats
            self.lbl_total.config(text=str(len(items)))
            self.lbl_low.config(text=str(len([i for i in items if i.current_stock < (i.reorder_level or 10)])))
            self.lbl_out.config(text=str(len([i for i in items if i.current_stock == 0])))
            self.lbl_cats.config(text=str(self.db.query(Category).count()))
            
        except Exception as e:
            print(f"Error fetching items: {e}")

    def add_item_dialog(self):
        self.show_dialog("Add Item")

    def edit_item_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an item to edit.")
            return
        
        item_val = self.tree.item(selected[0])
        item_id = item_val['values'][0]
        item = self.db.query(Item).get(item_id)
        
        if item:
            self.show_dialog("Edit Item", item)

    def show_dialog(self, title, item=None):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x600")
        top.configure(bg=BACKGROUND)
        
        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)
        
        # Fetch categories for dropdown
        categories = self.db.query(Category).all()
        cat_map = {c.name: c.category_id for c in categories}
        
        fields = ["Name", "Category", "Price", "Stock", "Unit", "Reorder Level"]
        entries = {}
        
        for field in fields:
            f_frame = ttk.Frame(top, padding=10)
            f_frame.pack(fill="x")
            ttk.Label(f_frame, text=field).pack(anchor="w")
            
            if field == "Category":
                entry = ttk.Combobox(f_frame, values=list(cat_map.keys()))
                if item and item.category:
                    entry.set(item.category.name)
            else:
                entry = ttk.Entry(f_frame)
                if item:
                    if field == "Name": entry.insert(0, item.name)
                    elif field == "Price": entry.insert(0, str(item.price))
                    elif field == "Stock": entry.insert(0, str(item.current_stock))
                    elif field == "Unit": entry.insert(0, item.unit or "")
                    elif field == "Reorder Level": entry.insert(0, str(item.reorder_level or 0))
            
            entry.pack(fill="x")
            entries[field] = entry
            
        def save():
            try:
                cat_name = entries["Category"].get()
                cat_id = cat_map.get(cat_name)
                
                if item:
                    item.name = entries["Name"].get()
                    item.category_id = cat_id
                    item.price = float(entries["Price"].get())
                    item.current_stock = int(entries["Stock"].get())
                    item.unit = entries["Unit"].get()
                    item.reorder_level = int(entries["Reorder Level"].get())
                else:
                    new_item = Item(
                        name=entries["Name"].get(),
                        category_id=cat_id,
                        price=float(entries["Price"].get()),
                        current_stock=int(entries["Stock"].get()),
                        unit=entries["Unit"].get(),
                        reorder_level=int(entries["Reorder Level"].get())
                    )
                    self.db.add(new_item)
                
                self.db.commit()
                top.destroy()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error saving: {e}")

        ttk.Button(top, text="Save", style="Primary.TButton", command=save).pack(pady=20)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an item to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            try:
                item_val = self.tree.item(selected[0])
                item_id = item_val['values'][0]
                item = self.db.query(Item).get(item_id)
                if item:
                    self.db.delete(item)
                    self.db.commit()
                    self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting item: {e}")
