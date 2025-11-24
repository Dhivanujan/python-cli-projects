#!/usr/bin/env python3
"""
GUI Quiz + Leaderboard System
- Tkinter GUI for quiz
- Timed questions with countdown
- Random questions
- Leaderboard display with Matplotlib
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import random
import time
from pathlib import Path
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

QUESTIONS_FILE = Path("questions.json")
LEADERBOARD_FILE = Path("leaderboard.json")


# ---------------------- Data ----------------------
def load_questions():
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(f"{QUESTIONS_FILE} not found")
    with open(QUESTIONS_FILE, "r") as f:
        data = json.load(f)
    return data


def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []


def save_leaderboard(lb):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=2)


# ---------------------- GUI App ----------------------
class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz + Leaderboard")
        self.username = ""
        self.questions = load_questions()
        self.leaderboard = load_leaderboard()
        self.num_questions = len(self.questions)
        self.per_question_time = 15

        self.current_index = 0
        self.score = 0
        self.current_question = None
        self.remaining_time = self.per_question_time
        self.timer_id = None

        self.quiz_questions = []

        self.build_login_screen()

    # ---------------- Login ----------------
    def build_login_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.login_label = tk.Label(self.master, text="Enter your username:")
        self.login_label.pack(pady=10)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack(pady=5)
        self.login_button = tk.Button(self.master, text="Start Quiz", command=self.start_quiz)
        self.login_button.pack(pady=10)

    # ---------------- Quiz ----------------
    def start_quiz(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            self.username = "Guest"
        # Ask number of questions
        n = simpledialog.askinteger("Questions", f"Number of questions (max {len(self.questions)}):", minvalue=1, maxvalue=len(self.questions))
        self.num_questions = n if n else len(self.questions)
        t = simpledialog.askinteger("Timer", "Seconds per question:", initialvalue=15, minvalue=5, maxvalue=60)
        self.per_question_time = t if t else 15
        # Random questions
        self.quiz_questions = random.sample(self.questions, self.num_questions)
        self.current_index = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.current_question = self.quiz_questions[self.current_index]
        self.remaining_time = self.per_question_time

        # Question text
        self.q_label = tk.Label(self.master, text=f"Q{self.current_index+1}: {self.current_question['question']}", wraplength=400)
        self.q_label.pack(pady=10)

        self.answer_var = tk.StringVar()

        # Multiple-choice
        if 'choices' in self.current_question:
            self.choice_buttons = []
            for choice in self.current_question['choices']:
                rb = tk.Radiobutton(self.master, text=choice, variable=self.answer_var, value=choice)
                rb.pack(anchor='w')
                self.choice_buttons.append(rb)
        else:
            # Open-ended
            self.answer_entry = tk.Entry(self.master, textvariable=self.answer_var)
            self.answer_entry.pack(pady=5)

        # Timer label
        self.timer_label = tk.Label(self.master, text=f"Time left: {self.remaining_time}s")
        self.timer_label.pack(pady=5)

        # Submit button
        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit_answer)
        self.submit_button.pack(pady=10)

        # Start countdown
        self.countdown()

    def countdown(self):
        self.timer_label.config(text=f"Time left: {self.remaining_time}s")
        if self.remaining_time <= 0:
            self.submit_answer(timeout=True)
            return
        self.remaining_time -= 1
        self.timer_id = self.master.after(1000, self.countdown)

    def submit_answer(self, timeout=False):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)

        user_answer = self.answer_var.get().strip() if not timeout else ""
        correct_answer = self.current_question['answer']

        if timeout:
            messagebox.showinfo("Time's up!", f"Correct answer: {correct_answer}")
        else:
            if user_answer.lower() == str(correct_answer).lower():
                messagebox.showinfo("Correct!", "Your answer is correct!")
                self.score += 1
            else:
                messagebox.showinfo("Incorrect", f"Correct answer: {correct_answer}")

        self.current_index += 1
        if self.current_index < self.num_questions:
            self.show_question()
        else:
            self.finish_quiz()

    # ---------------- Finish Quiz ----------------
    def finish_quiz(self):
        # Save to leaderboard
        self.leaderboard.append({
            "user": self.username,
            "score": self.score,
            "total": self.num_questions,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        # Sort descending
        self.leaderboard.sort(key=lambda x: x['score'], reverse=True)
        save_leaderboard(self.leaderboard)

        for widget in self.master.winfo_children():
            widget.destroy()
        tk.Label(self.master, text=f"Quiz Complete! Score: {self.score}/{self.num_questions}").pack(pady=10)
        tk.Button(self.master, text="View Leaderboard", command=self.show_leaderboard).pack(pady=5)
        tk.Button(self.master, text="Exit", command=self.master.quit).pack(pady=5)

    # ---------------- Leaderboard ----------------
    def show_leaderboard(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        tk.Label(self.master, text="Leaderboard (Top 10)").pack(pady=5)
        top10 = self.leaderboard[:10]
        for idx, entry in enumerate(top10, start=1):
            tk.Label(self.master, text=f"{idx}. {entry['user']}: {entry['score']}/{entry['total']}").pack(anchor='w')

        # Plot leaderboard chart
        users = [e['user'] for e in top10]
        scores = [e['score'] for e in top10]
        fig, ax = plt.subplots(figsize=(5,3))
        ax.barh(users[::-1], scores[::-1], color='skyblue')
        ax.set_xlabel("Score")
        ax.set_title("Top 10 Scores")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

        tk.Button(self.master, text="Back to Login", command=self.build_login_screen).pack(pady=5)


# ---------------------- Run ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
