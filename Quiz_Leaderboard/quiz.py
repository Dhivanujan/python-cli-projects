#!/usr/bin/env python3
"""
Quiz + Leaderboard CLI App
Features:
- Multi-user support
- Timed questions
- Randomized questions
- Score tracking
- Leaderboard saved in JSON
"""

import json
import random
import threading
import time
from datetime import datetime
from pathlib import Path

QUESTIONS_FILE = Path("questions.json")
LEADERBOARD_FILE = Path("leaderboard.json")


# ---------------------- Input with Timeout ----------------------
def input_with_timeout(prompt, timeout):
    """Prompt user input with timeout using a background thread."""
    result = {"value": None}

    def target():
        try:
            result["value"] = input(prompt)
        except Exception:
            result["value"] = None

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return None
    return result["value"]


# ---------------------- Quiz Classes ----------------------
class Question:
    def __init__(self, question_text, answer, choices=None):
        self.text = question_text
        self.choices = choices
        self.answer = answer

    def ask(self, timeout):
        print(f"\n{self.text}")
        if self.choices:
            for idx, choice in enumerate(self.choices, start=1):
                print(f"  {idx}. {choice}")
        start = time.time()
        user_input = input_with_timeout("> Your answer: ", timeout)
        elapsed = time.time() - start
        if user_input is None:
            print(f"⏰ Time's up!")
            return False, elapsed
        else:
            user_input = user_input.strip()
            correct = False
            if self.choices:
                # numeric index or text
                try:
                    idx = int(user_input)
                    chosen = self.choices[idx - 1] if 1 <= idx <= len(self.choices) else None
                except:
                    chosen = user_input
                correct = str(chosen).strip().lower() == str(self.answer).strip().lower()
            else:
                correct = user_input.strip().lower() == str(self.answer).strip().lower()
            if correct:
                print("✅ Correct!")
            else:
                print(f"❌ Incorrect. Correct answer: {self.answer}")
            return correct, elapsed


class Quiz:
    def __init__(self, questions, per_question_time=15, num_questions=None):
        self.questions = questions[:]
        self.per_question_time = per_question_time
        self.num_questions = num_questions if num_questions else len(self.questions)

    def start(self):
        asked = random.sample(self.questions, self.num_questions)
        score = 0
        details = []
        for q in asked:
            correct, elapsed = q.ask(self.per_question_time)
            details.append({
                "question": q.text,
                "correct": correct,
                "time": round(elapsed, 2)
            })
            if correct:
                score += 1
        return score, details


# ---------------------- Leaderboard ----------------------
def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []


def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=2)


def update_leaderboard(username, score, total):
    leaderboard = load_leaderboard()
    leaderboard.append({
        "user": username,
        "score": score,
        "total": total,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    # Sort by score descending
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    save_leaderboard(leaderboard)


def show_leaderboard(limit=10):
    leaderboard = load_leaderboard()
    print("\n=== Leaderboard ===")
    for i, entry in enumerate(leaderboard[:limit], start=1):
        user = entry["user"]
        score = entry["score"]
        total = entry["total"]
        ts = entry["timestamp"]
        print(f"{i}. {user}: {score}/{total} ({ts})")
    print("==================\n")


# ---------------------- CLI ----------------------
def load_questions():
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(f"{QUESTIONS_FILE} not found!")
    with open(QUESTIONS_FILE, "r") as f:
        data = json.load(f)
    questions = []
    for q in data:
        questions.append(Question(q["question"], q["answer"], q.get("choices")))
    return questions


def main():
    print("=== Welcome to Quiz + Leaderboard System ===")
    username = input("Enter your username: ").strip() or "Guest"

    questions = load_questions()
    while True:
        print("\nMenu:")
        print("1) Take Quiz")
        print("2) View Leaderboard")
        print("3) Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            num_q = input(f"Number of questions (max {len(questions)}): ").strip()
            try:
                num_q = int(num_q)
                if num_q < 1 or num_q > len(questions):
                    num_q = len(questions)
            except:
                num_q = len(questions)
            per_question_time = input("Seconds per question (default 15): ").strip()
            try:
                per_question_time = int(per_question_time)
            except:
                per_question_time = 15
            quiz = Quiz(questions, per_question_time, num_q)
            score, details = quiz.start()
            print(f"\nQuiz Complete! Score: {score}/{num_q}")
            update_leaderboard(username, score, num_q)
        elif choice == "2":
            show_leaderboard()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
