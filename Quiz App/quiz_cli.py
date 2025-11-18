#!/usr/bin/env python3
"""
quiz_cli.py

Intermediate CLI Quiz App with per-question timer, random question set,
and score history saved to JSON.

Works cross-platform by using a background thread to read input with timeout.
"""

import json
import random
import threading
import time
from datetime import datetime
from pathlib import Path

QUESTIONS_FILE = Path("questions.json")
HISTORY_FILE = Path("quiz_history.json")

# --- Helper: input with timeout using a thread (cross-platform) ---
def input_with_timeout(prompt: str, timeout: int):
    """
    Prompt the user and wait for input up to `timeout` seconds.
    Returns the string input, or None if timed out.
    """
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


# --- Quiz logic ---
class Quiz:
    def __init__(self, questions, per_question_time=15, num_questions=None):
        """
        questions: list of question dicts
        per_question_time: seconds allowed per question
        num_questions: if None, ask all; else random sample of this size
        """
        self.questions = questions[:]
        self.per_question_time = per_question_time
        if num_questions is None or num_questions > len(self.questions):
            self.num_questions = len(self.questions)
        else:
            self.num_questions = num_questions

    def run(self):
        print(f"\nStarting quiz — {self.num_questions} question(s). "
              f"You have {self.per_question_time} seconds per question.\n")
        asked = random.sample(self.questions, self.num_questions)
        score = 0
        answers_detail = []
        qnum = 1

        for q in asked:
            print(f"Question {qnum}/{self.num_questions}:")
            print(q["question"])
            choices = q.get("choices")
            if choices:
                for idx, choice in enumerate(choices, start=1):
                    print(f"  {idx}. {choice}")
            else:
                print("  (Open-ended answer expected)")

            # Prompt
            start = time.time()
            user_raw = input_with_timeout(f"> Your answer (enter number or text): ", self.per_question_time)
            elapsed = time.time() - start

            if user_raw is None:
                print(f"\n⏰ Time's up! (took > {self.per_question_time}s)\n")
                user_answer = None
                correct = False
            else:
                user_answer = user_raw.strip()
                # Evaluate
                if choices:
                    # Accept numeric index or exact matching text
                    try:
                        idx = int(user_answer)
                        chosen = choices[idx - 1] if 1 <= idx <= len(choices) else None
                    except Exception:
                        chosen = user_answer
                    correct_answer = q["answer"]
                    correct = (chosen == correct_answer) or (str(chosen).strip().lower() == str(correct_answer).strip().lower())
                else:
                    # open-ended: do case-insensitive comparison (simple)
                    correct_answer = q["answer"]
                    correct = user_answer.lower().strip() == str(correct_answer).lower().strip()

                if correct:
                    print("✅ Correct!\n")
                    score += 1
                else:
                    print(f"❌ Incorrect. Correct answer: {q['answer']}\n")

            answers_detail.append({
                "question": q["question"],
                "user_answer": user_answer,
                "correct_answer": q["answer"],
                "correct": bool(correct),
                "time_taken": round(elapsed, 2) if user_raw is not None else None
            })
            qnum += 1

        # Summary
        print("Quiz complete!")
        print(f"Score: {score} / {self.num_questions} ({round(score/self.num_questions*100, 1)}%)\n")
        summary = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "num_questions": self.num_questions,
            "score": score,
            "percentage": round(score/self.num_questions*100, 1),
            "per_question_time": self.per_question_time,
            "answers": answers_detail
        }
        save_history(summary)
        print(f"Result saved to {HISTORY_FILE}\n")
        return summary


# --- Persistence for history ---
def load_questions(path=QUESTIONS_FILE):
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Create a questions.json next to the script.")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Expect list of {question, choices?, answer}
    return data


def save_history(record, path=HISTORY_FILE):
    existing = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.append(record)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def show_history(path=HISTORY_FILE, limit=10):
    if not path.exists():
        print("No history found.")
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data = list(reversed(data))  # most recent first
    print(f"\nLast {min(limit, len(data))} results:")
    for rec in data[:limit]:
        ts = rec.get("timestamp", "unknown")
        score = rec.get("score", 0)
        total = rec.get("num_questions", 0)
        pct = rec.get("percentage", 0)
        print(f"  {ts} — {score}/{total} ({pct}%)")
    print("")


# --- CLI menu ---
def main_menu():
    print("=== CLI Quiz App ===")
    print("1) Take a quiz")
    print("2) View history")
    print("3) Configure (num questions / time per question)")
    print("4) Exit")

def run_cli():
    try:
        questions = load_questions()
    except FileNotFoundError as e:
        print(e)
        return

    # sensible defaults
    per_question = 15
    num_questions = None  # means all

    while True:
        main_menu()
        choice = input("Choose: ").strip()
        if choice == "1":
            qcount = num_questions if num_questions is not None else len(questions)
            print(f"\nPreparing quiz: {qcount} question(s), {per_question}s each.")
            quiz = Quiz(questions, per_question_time=per_question, num_questions=qcount)
            quiz.run()
        elif choice == "2":
            show_history()
        elif choice == "3":
            try:
                v = input(f"Enter number of questions (or press Enter for all [{len(questions)}]): ").strip()
                if v == "":
                    num_questions = None
                else:
                    n = int(v)
                    if n < 1:
                        print("Must be >= 1")
                    else:
                        num_questions = n
                t = input(f"Seconds per question (current {per_question}): ").strip()
                if t != "":
                    tt = int(t)
                    if tt < 3:
                        print("Too small; keeping previous value.")
                    else:
                        per_question = tt
            except Exception as exc:
                print("Invalid input:", exc)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    run_cli()
