import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ui.styles import *
from data.db import get_db
from data.models import Report, User
from datetime import datetime

class ReportsView(ttk.Frame):
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
        ttk.Label(header, text="Reports", style="H1.TLabel").pack(side="left")

        content = ttk.Frame(container)
        content.pack(fill="both", expand=True)

        gen_frame = ttk.LabelFrame(content, text="Generate New Report", padding=20)
        gen_frame.pack(side="left", fill="y", padx=(0, 20), anchor="n")

        ttk.Label(gen_frame, text="Report Type").pack(anchor="w", pady=(0, 5))
        self.type_var = tk.StringVar(value="Inventory")
        ttk.Combobox(gen_frame, textvariable=self.type_var, values=["Inventory", "Sales", "Category", "Low Stock"]).pack(fill="x", pady=(0, 10))

        ttk.Label(gen_frame, text="Format").pack(anchor="w", pady=(0, 5))
        self.format_var = tk.StringVar(value="CSV")
        ttk.Combobox(gen_frame, textvariable=self.format_var, values=["CSV", "PDF"]).pack(fill="x", pady=(0, 10))

        ttk.Button(gen_frame, text="Generate Report", style="Primary.TButton", command=self.generate_report).pack(fill="x", pady=20)

        table_frame = ttk.Frame(content)
        table_frame.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Type", "Format", "Generated At", "User", "Action"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Format", text="Format")
        self.tree.heading("Generated At", text="Generated At")
        self.tree.heading("User", text="User")
        self.tree.heading("Action", text="Action")

        self.tree.column("ID", width=50)
        self.tree.column("Type", width=100)
        self.tree.column("Format", width=80)
        self.tree.column("Generated At", width=150)
        self.tree.column("User", width=100)
        self.tree.column("Action", width=100)

        self.tree.pack(fill="both", expand=True)
        
        self.tree.bind("<Double-1>", self.download_report)

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            reports = self.db.query(Report).order_by(Report.generated_at.desc()).all()
            for r in reports:
                user_name = r.user.username if r.user else "Unknown"
                # Storing format in parameters for now as it's not a column
                fmt = "CSV"
                if r.parameters and "PDF" in r.parameters:
                    fmt = "PDF"
                
                self.tree.insert("", "end", values=(r.report_id, r.report_type, fmt, r.generated_at, user_name, "Download"))
        except Exception as e:
            print(f"Error fetching reports: {e}")

    def generate_report(self):
        try:
            rtype = self.type_var.get()
            fmt = self.format_var.get()
            
      
            report_data = f"Mock data for {rtype} report in {fmt} format."
            
            user = self.db.query(User).first()
            user_id = user.user_id if user else None

            report = Report(
                report_type=rtype,
                generated_at=datetime.utcnow(),
                user_id=user_id,
                parameters=f"Format: {fmt}",
                report_data=report_data
            )
            
            self.db.add(report)
            self.db.commit()
            
            messagebox.showinfo("Success", f"{rtype} Report ({fmt}) generated successfully.")
            self.refresh_data()

        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")

    def download_report(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        report_id = item['values'][0]
        
        report = self.db.query(Report).filter(Report.report_id == report_id).first()
        if report:
            # Simulate download
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                with open(file_path, "w") as f:
                    f.write(report.report_data or "No data")
                messagebox.showinfo("Downloaded", f"Report saved to {file_path}")
