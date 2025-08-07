from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter import messagebox, ttk
from db import init_db, execute_query, fetch_one, fetch_all
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ---------- Utility Functions ----------
def center_window(win, width=600, height=400):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    win.geometry(f'{width}x{height}+{x}+{y}')

def calculate_grade(total):
    percent = total / 3
    if percent >= 90:
        return percent, 'A'
    elif percent >= 75:
        return percent, 'B'
    elif percent >= 60:
        return percent, 'C'
    elif percent >= 40:
        return percent, 'D'
    else:
        return percent, 'F'

# ---------- Main App Class ----------
class StudentApp:
    def apply_theme(self, dark_mode):
        bg = '#2e2e2e' if dark_mode else 'SystemButtonFace'
        fg = 'white' if dark_mode else 'black'
        self.master.configure(bg=bg)
        for widget in self.master.winfo_children():
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

    def __init__(self, master):
        self.dark_mode = False
        self.master = master
        self.master.title("Student Records")
        center_window(master, 1000, 700)
        init_db()
        self.login_screen()

    def login_screen(self):
        self.clear()
        Label(self.master, text="Student Records", font=("Arial", 18, "bold")).pack(pady=10)
        frame = Frame(self.master)
        frame.pack(pady=20)
        Label(frame, text="Username:").grid(row=0, column=0, pady=5)
        self.username_entry = Entry(frame)
        self.username_entry.grid(row=0, column=1)
        Label(frame, text="Password:").grid(row=1, column=0, pady=5)
        self.password_entry = Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1)
        Button(self.master, text="Login", width=10, command=self.check_login).pack(pady=10)

    def check_login(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()
        result = fetch_one("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        if result:
            self.home_page()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    def home_page(self):
        self.clear()
        theme_toggle = Frame(self.master)
        theme_toggle.pack(anchor='ne', padx=20, pady=10)
        Button(theme_toggle, text="Toggle Theme", command=self.toggle_theme, font=("Arial", 12)).pack()
        self.clear()
        self.master.title("Student Records - Home")
        Label(self.master, text="Student Records", font=("Arial", 28, "bold")).pack(pady=30)
        grid_frame = Frame(self.master)
        grid_frame.pack()

        buttons = [
            ("Add Student Record", self.add_student),
            ("Update Student Record", self.update_student),
            ("Delete Student Record", self.delete_student),
            ("Add/Update Scores", self.manage_scores),
            ("Delete Scores", self.delete_scores),
            ("Show Student Result", self.show_result),
            ("Logout", self.login_screen)
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = Button(grid_frame, text=text, width=30, height=2, font=("Arial", 16), command=cmd, bg='#007acc', fg='white', activebackground='#005f99')
            btn.grid(row=i//2, column=i%2, padx=60, pady=30)
        
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme(self.dark_mode)

    def clear(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def add_student(self):
        self.clear()
        Label(self.master, text="Add Student", font=("Arial", 28, "bold")).pack(pady=30)
        frame = Frame(self.master)
        frame.pack()

        labels = ["Name", "DOB", "Class", "Section", "Roll No", "Address"]
        entries = []
        for i, lbl in enumerate(labels):
            Label(frame, text=lbl).grid(row=i, column=0, sticky=W, pady=5)
            ent = Entry(frame, font=("Arial", 16), width=40)
            ent.grid(row=i, column=1)
            entries.append(ent)

        def submit():
            values = [e.get() for e in entries]
            try:
                execute_query("INSERT INTO students (name, dob, class, section, roll, address) VALUES (?, ?, ?, ?, ?, ?)", values)
                messagebox.showinfo("Success", "Student record added successfully.")
                self.home_page()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(frame, text="Submit", command=submit).grid(row=6, columnspan=2, pady=10)
        Button(self.master, text="Export to PDF", command=lambda: self.export_result_to_pdf(student, score), font=("Arial", 14), bg="#4CAF50", fg="white", width=20).pack(pady=10)
        Button(self.master, text="Back to Home", command=self.home_page, font=("Arial", 14), bg="#007acc", fg="white", width=20).pack(pady=10)

    def update_student(self):
        self.clear()
        Label(self.master, text="Update Student", font=("Arial", 28, "bold")).pack(pady=30)
        Label(self.master, text="Enter Roll Number:").pack()
        roll_entry = Entry(self.master)
        roll_entry.pack()

        def fetch():
            roll = roll_entry.get()
            student = fetch_one("SELECT * FROM students WHERE roll=?", (roll,))
            if not student:
                messagebox.showerror("Not Found", "Student record not found.")
                return

            self.clear()
            Label(self.master, text="Update Student", font=("Arial", 18, "bold")).pack(pady=10)
            frame = Frame(self.master)
            frame.pack()
            labels = ["Name", "DOB", "Class", "Section", "Roll No", "Address"]
            entries = []
            for i, lbl in enumerate(labels):
                Label(frame, text=lbl).grid(row=i, column=0, sticky=W, pady=5)
                ent = Entry(frame, width=30)
                ent.insert(0, student[i+1])
                ent.grid(row=i, column=1)
                entries.append(ent)

            def update():
                values = [e.get() for e in entries] + [student[0]]
                execute_query("UPDATE students SET name=?, dob=?, class=?, section=?, roll=?, address=? WHERE id=?", values)
                messagebox.showinfo("Success", "Student record updated successfully.")
                self.home_page()

            Button(frame, text="Update", command=update).grid(row=6, columnspan=2, pady=10)
            Button(self.master, text="Back to Home", command=self.home_page).pack(pady=10)

        Button(self.master, text="Search", command=fetch).pack(pady=10)
        Button(self.master, text="Back to Home", command=self.home_page).pack(pady=10)

    def delete_student(self):
        self.clear()
        Label(self.master, text="Delete Student", font=("Arial", 28, "bold")).pack(pady=30)
        Label(self.master, text="Enter Roll Number:").pack()
        roll_entry = Entry(self.master)
        roll_entry.pack()

        def delete():
            execute_query("DELETE FROM students WHERE roll=?", (roll_entry.get(),))
            messagebox.showinfo("Deleted", "Student record deleted.")
            self.home_page()

        Button(self.master, text="Delete", command=delete).pack(pady=10)
        Button(self.master, text="Back to Home", command=self.home_page).pack(pady=10)

    def manage_scores(self):
        self.clear()
        Label(self.master, text="Manage Scores", font=("Arial", 28, "bold")).pack(pady=30)
        Label(self.master, text="Enter Roll Number:").pack()
        roll_entry = Entry(self.master)
        roll_entry.pack()

        def add_update_scores():
            roll = roll_entry.get()
            student = fetch_one("SELECT * FROM students WHERE roll=?", (roll,))
            if not student:
                messagebox.showerror("Error", "Student not found.")
                return

            score = fetch_one("SELECT * FROM scores WHERE roll=?", (roll,))
            popup = Toplevel(self.master)
            popup.title("Add/Update Scores")
            center_window(popup, 300, 250)

            labels = ["Subject 1", "Subject 2", "Subject 3"]
            entries = []
            for i, lbl in enumerate(labels):
                Label(popup, text=lbl).grid(row=i, column=0, pady=5)
                ent = Entry(popup)
                if score:
                    ent.insert(0, score[i+2])
                ent.grid(row=i, column=1)
                entries.append(ent)

            def submit():
                try:
                    marks = list(map(int, [e.get() for e in entries]))
                    total = sum(marks)
                    percent, grade = calculate_grade(total)
                    if score:
                        execute_query("UPDATE scores SET sub1=?, sub2=?, sub3=?, total=?, percent=?, grade=? WHERE roll=?",
                                      (*marks, total, percent, grade, roll))
                    else:
                        execute_query("INSERT INTO scores (roll, sub1, sub2, sub3, total, percent, grade) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                      (roll, *marks, total, percent, grade))
                    messagebox.showinfo("Success", "Scores saved successfully.")
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            Button(popup, text="Submit", command=submit).grid(row=3, columnspan=2, pady=10)

        Button(self.master, text="Add / Update Scores", command=add_update_scores).pack(pady=10)
        Button(self.master, text="Back to Home", command=self.home_page).pack(pady=10)

    def delete_scores(self):
        self.clear()
        Label(self.master, text="Delete Scores", font=("Arial", 28, "bold")).pack(pady=30)
        Label(self.master, text="Enter Roll Number:").pack()
        roll_entry = Entry(self.master)
        roll_entry.pack()

        def delete():
            execute_query("DELETE FROM scores WHERE roll=?", (roll_entry.get(),))
            messagebox.showinfo("Deleted", "Scores deleted.")
            self.home_page()

        Button(self.master, text="Delete", command=delete).pack(pady=10)
        Button(self.master, text="Back to Home", command=self.home_page).pack(pady=10)

    def show_result(self):
        self.clear()
        self.master.title("Student Result")
        center_window(self.master, 1000, 700)

        Label(self.master, text="Student Records", font=("Arial", 20)).pack(pady=5)
        Label(self.master, text="RESULT", font=("Arial", 28, "bold"), fg="#007acc").pack(pady=10)
        Label(self.master, text="Enter Roll Number:", font=("Arial", 16)).pack()

        roll_entry = Entry(self.master, font=("Arial", 14), width=20)
        roll_entry.pack(pady=10)

        def show():
            roll = roll_entry.get()  
            self.clear()            
            self.master.title("Student Result")
            center_window(self.master, 1000, 700)

            student = fetch_one("SELECT * FROM students WHERE roll=?", (roll,))
            score = fetch_one("SELECT * FROM scores WHERE roll=?", (roll,))

            if not student:
                messagebox.showerror("Error", "Student not found.")
                return

            Label(self.master, text="Student Records", font=("Arial", 20)).pack(pady=5)
            Label(self.master, text="RESULT", font=("Arial", 28, "bold"), fg="#007acc").pack(pady=10)
            Label(self.master, text=f"Name: {student[1]}\nDOB: {student[2]}\nClass: {student[3]}\nSection: {student[4]}\nRoll No: {student[5]}", font=("Arial", 14), justify=LEFT).pack(pady=10)

            if score:
                table = Frame(self.master)
                table.pack(pady=20)

                headers = ["Subject", "Marks"]
                subjects = ["Subject 1", "Subject 2", "Subject 3"]
                values = [score[2], score[3], score[4]]

                for i in range(2):
                    Label(table, text=headers[i], font=("Arial", 14, "bold"), width=15, borderwidth=2, relief="groove").grid(row=0, column=i)

                for i, subject in enumerate(subjects):
                    Label(table, text=subject, font=("Arial", 14), width=15, borderwidth=2, relief="groove").grid(row=i+1, column=0)
                    Label(table, text=values[i], font=("Arial", 14), width=15, borderwidth=2, relief="groove").grid(row=i+1, column=1)
                    Progressbar(table, value=values[i], maximum=100, length=200).grid(row=i+1, column=2, padx=10)
                    Label(table, text=f"{values[i]}%", font=("Arial", 12)).grid(row=i+1, column=3)

                Label(self.master, text=f"\nTotal: {score[5]}    Percentage: {score[6]:.2f}%    Grade: {score[7]}", font=("Arial", 16, "bold"), pady=20).pack()
            else:
                Label(self.master, text="No scores found.", font=("Arial", 16), fg="red").pack(pady=20)

            Button(self.master, text="Export to PDF", command=lambda: self.export_result_to_pdf(student, score), font=("Arial", 14), bg="#4CAF50", fg="white", width=20).pack(pady=10)
            Button(self.master, text="Back to Home", command=self.home_page, font=("Arial", 14), bg="#007acc", fg="white", width=20).pack(pady=10)

        Button(self.master, text="Show Result", command=show, font=("Arial", 14), bg="#007acc", fg="white", width=20).pack(pady=10)
        Button(self.master, text="Back to Home", command=self.home_page, font=("Arial", 14), bg="#007acc", fg="white", width=20).pack(pady=10)

    def export_result_to_pdf(self, student, score):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not filepath:
            return
        c = canvas.Canvas(filepath, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "STUDENT RESULT")
        c.setFont("Helvetica", 12)
        y = 720
        lines = [
            f"Name: {student[1]}", f"DOB: {student[2]}", f"Class: {student[3]}", f"Section: {student[4]}",
            f"Roll No: {student[5]}", f"Address: {student[6]}"
        ]
        for line in lines:
            c.drawString(50, y, line)
            y -= 20
        if score:
            c.drawString(50, y, "")
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Subject")
            c.drawString(200, y, "Marks")
            y -= 20
            c.setFont("Helvetica", 12)
            subjects = ["Subject 1", "Subject 2", "Subject 3"]
            values = [score[2], score[3], score[4]]
            for sub, val in zip(subjects, values):
                c.drawString(50, y, sub)
                c.drawString(200, y, str(val))
                y -= 20
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Total: {score[5]}    Percentage: {score[6]:.2f}%    Grade: {score[7]}")
        c.save()

# ---------- Run App ----------
if __name__ == "__main__":
    root = Tk()
    app = StudentApp(root)
    root.mainloop()
