import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database setup
conn = sqlite3.connect('bmi_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bmi_data
             (user_id INTEGER PRIMARY KEY, weight REAL, height REAL, bmi REAL, category TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")

        # Weight input
        tk.Label(root, text="Weight (kg):").grid(row=0, column=0)
        self.weight_entry = tk.Entry(root)
        self.weight_entry.grid(row=0, column=1)

        # Height input
        tk.Label(root, text="Height (cm):").grid(row=1, column=0)
        self.height_entry = tk.Entry(root)
        self.height_entry.grid(row=1, column=1)

        # Calculate button
        self.calculate_button = tk.Button(root, text="Calculate BMI", command=self.calculate_bmi)
        self.calculate_button.grid(row=2, column=0, columnspan=2)

        # Result display
        self.result_label = tk.Label(root, text="", font=('Helvetica', 14))
        self.result_label.grid(row=3, column=0, columnspan=2)

        # View history button
        self.history_button = tk.Button(root, text="View History", command=self.view_history)
        self.history_button.grid(row=4, column=0, columnspan=2)

    def calculate_bmi(self):
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get()) / 100  # Convert cm to meters
            if weight <= 0 or height <= 0:
                raise ValueError("Weight and Height must be positive values.")

            bmi = weight / (height ** 2)
            category = self.get_bmi_category(bmi)

            self.result_label.config(text=f"BMI: {bmi:.2f}\nCategory: {category}")

            # Store in database
            c.execute("INSERT INTO bmi_data (weight, height, bmi, category) VALUES (?, ?, ?, ?)",
                      (weight, height, bmi, category))
            conn.commit()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"

    def view_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("BMI History")

        fig, ax = plt.subplots()
        c.execute("SELECT timestamp, bmi FROM bmi_data")
        data = c.fetchall()
        if data:
            dates, bmis = zip(*data)
            ax.plot(dates, bmis, marker='o')
            ax.set(xlabel='Date', ylabel='BMI', title='BMI Over Time')
            ax.grid()

            canvas = FigureCanvasTkAgg(fig, master=history_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        else:
            tk.Label(history_window, text="No data available").pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculator(root)
    root.mainloop()

# Close the database connection
conn.close()
