import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import *
from data.db import get_db
from data.models import Category

class CategoriesView(ttk.Frame):
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

        ttk.Label(header, text="Categories", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")

        ttk.Button(actions, text="Add Category", style="Primary.TButton", command=self.add_category_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Edit", style="Outline.TButton", command=self.edit_category_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Delete", style="Outline.TButton", command=self.delete_category).pack(side="left", padx=5)

     
        self.tree = ttk.Treeview(container, columns=("ID", "Name", "Description", "Item Count"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Item Count", text="Item Count")

        self.tree.column("ID", width=50)
        self.tree.column("Name", width=200)
        self.tree.column("Description", width=400)
        self.tree.column("Item Count", width=100)

        self.tree.pack(fill="both", expand=True, pady=(10, 0))

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            categories = self.db.query(Category).all()
            for cat in categories:
                item_count = len(cat.items)
                self.tree.insert("", "end", values=(cat.category_id, cat.name, cat.description, item_count))
        except Exception as e:
            print(f"Error fetching categories: {e}")

    def add_category_dialog(self):
        self.show_dialog("Add Category")

    def edit_category_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a category to edit.")
            return
        
        item = self.tree.item(selected[0])
        cat_id = item['values'][0]
        category = self.db.query(Category).filter(Category.category_id == cat_id).first()
        
        if category:
            self.show_dialog("Edit Category", category)

    def show_dialog(self, title, category=None):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x300")
        top.configure(bg=BACKGROUND)

        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)

        fields = {"Name": category.name if category else "", "Description": category.description if category else ""}
        entries = {}

        for field, value in fields.items():
            f_frame = ttk.Frame(top, padding=10)
            f_frame.pack(fill="x")
            ttk.Label(f_frame, text=field).pack(anchor="w")
            entry = ttk.Entry(f_frame)
            if value:
                entry.insert(0, value)
            entry.pack(fill="x")
            entries[field] = entry

        def save():
            try:
                name = entries["Name"].get()
                description = entries["Description"].get()

                if category:
                    category.name = name
                    category.description = description
                else:
                    new_cat = Category(name=name, description=description)
                    self.db.add(new_cat)
                
                self.db.commit()
                top.destroy()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error saving category: {e}")

        ttk.Button(top, text="Save", style="Primary.TButton", command=save).pack(pady=20)

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a category to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this category?"):
            try:
                item = self.tree.item(selected[0])
                cat_id = item['values'][0]
                category = self.db.query(Category).filter(Category.category_id == cat_id).first()
                if category:
                    self.db.delete(category)
                    self.db.commit()
                    self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting category: {e}")
