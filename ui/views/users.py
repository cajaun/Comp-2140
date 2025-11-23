import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import *
from data.db import get_db
from data.models import User
from datetime import datetime

class UsersView(ttk.Frame):
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
        ttk.Label(header, text="User Management", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Add User", style="Primary.TButton", command=self.add_user_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Edit", style="Outline.TButton", command=self.edit_user_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Delete", style="Outline.TButton", command=self.delete_user).pack(side="left", padx=5)

      
        self.tree = ttk.Treeview(container, columns=("ID", "Username", "Role", "Last Login", "Created At"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Last Login", text="Last Login")
        self.tree.heading("Created At", text="Created At")

        self.tree.column("ID", width=50)
        self.tree.column("Username", width=150)
        self.tree.column("Role", width=100)
        self.tree.column("Last Login", width=150)
        self.tree.column("Created At", width=150)

        self.tree.pack(fill="both", expand=True, pady=(10, 0))

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            users = self.db.query(User).all()
            for u in users:
                self.tree.insert("", "end", values=(u.user_id, u.username, u.role, u.last_login, u.created_at))
        except Exception as e:
            print(f"Error fetching users: {e}")

    def add_user_dialog(self):
        self.show_dialog("Add User")

    def edit_user_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user to edit.")
            return
        
        item = self.tree.item(selected[0])
        user_id = item['values'][0]
        user = self.db.query(User).get(user_id)
        
        if user:
            self.show_dialog("Edit User", user)

    def show_dialog(self, title, user=None):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x400")
        top.configure(bg=BACKGROUND)

        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)

        fields = ["Username", "Password", "Role"]
        entries = {}

        for field in fields:
            f_frame = ttk.Frame(top, padding=10)
            f_frame.pack(fill="x")
            ttk.Label(f_frame, text=field).pack(anchor="w")
            
            if field == "Role":
                entry = ttk.Combobox(f_frame, values=["admin", "staff", "manager"])
                if user: entry.set(user.role)
            else:
                entry = ttk.Entry(f_frame, show="*" if field == "Password" else "")
                if user and field == "Username":
                    entry.insert(0, user.username)
                
            
            entry.pack(fill="x")
            entries[field] = entry

        def save():
            try:
                username = entries["Username"].get()
                password = entries["Password"].get()
                role = entries["Role"].get()

                if user:
                    user.username = username
                    user.role = role
                    if password: 
                        user.password_hash = password # going to use some hashing/salting method for this
                else:
                    new_user = User(
                        username=username,
                        password_hash=password, 
                        role=role,
                        created_at=datetime.utcnow()
                    )
                    self.db.add(new_user)
                
                self.db.commit()
                top.destroy()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error saving user: {e}")

        ttk.Button(top, text="Save", style="Primary.TButton", command=save).pack(pady=20)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            try:
                item = self.tree.item(selected[0])
                user_id = item['values'][0]
                user = self.db.query(User).get(user_id)
                if user:
                    self.db.delete(user)
                    self.db.commit()
                    self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting user: {e}")
