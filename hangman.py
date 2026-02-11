import tkinter as tk
from tkinter import messagebox


HANGMAN_STAGES = [
    """
 +---+
 |   |
     |
     |
     |
     |
=======
""",
    """
 +---+
 |   |
 O   |
     |
     |
     |
=======
""",
    """
 +---+
 |   |
 O   |
 |   |
     |
     |
=======
""",
    """
 +---+
 |   |
 O   |
/|   |
     |
     |
=======
""",
    """
 +---+
 |   |
 O   |
/|\  |
     |
     |
=======
""",
    """
 +---+
 |   |
 O   |
/|\  |
/    |
     |
=======
""",
    """
 +---+
 |   |
 O   |
/|\  |
/ \  |
     |
=======
""",
]

MAX_WRONG = len(HANGMAN_STAGES) - 1


def render_progress(secret: str, guessed: set[str]) -> str:
    return " ".join([ch if (ch == " " or ch in guessed) else "_" for ch in secret])


class HangmanApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Hangman")
        self.root.resizable(False, False)

        self.player_one = tk.StringVar(value="Player 1")
        self.player_two = tk.StringVar(value="Player 2")
        self.secret = ""
        self.guessed: set[str] = set()
        self.wrong: set[str] = set()

        self._build_setup_ui()
        self._build_game_ui()
        self._show_setup()

    def _build_setup_ui(self) -> None:
        self.setup_frame = tk.Frame(self.root, padx=10, pady=10)

        tk.Label(self.setup_frame, text="Player 1 name:").grid(row=0, column=0, sticky="w")
        tk.Entry(self.setup_frame, textvariable=self.player_one, width=20).grid(
            row=0, column=1, padx=(6, 0)
        )

        tk.Label(self.setup_frame, text="Player 2 name:").grid(row=1, column=0, sticky="w")
        tk.Entry(self.setup_frame, textvariable=self.player_two, width=20).grid(
            row=1, column=1, padx=(6, 0)
        )

        tk.Label(self.setup_frame, text="Secret word or phrase:").grid(
            row=2, column=0, sticky="w"
        )
        self.secret_entry = tk.Entry(self.setup_frame, width=26, show="*")
        self.secret_entry.grid(row=2, column=1, padx=(6, 0))

        self.start_button = tk.Button(
            self.setup_frame, text="Start Game", width=16, command=self.start_game
        )
        self.start_button.grid(row=3, column=0, columnspan=2, pady=(8, 0))

    def _build_game_ui(self) -> None:
        self.game_frame = tk.Frame(self.root, padx=10, pady=10)

        self.stage_label = tk.Label(
            self.game_frame, text="", font=("Consolas", 12), justify="left"
        )
        self.stage_label.grid(row=0, column=0, columnspan=2, sticky="w")

        self.word_label = tk.Label(self.game_frame, text="", font=("Segoe UI", 14, "bold"))
        self.word_label.grid(row=1, column=0, columnspan=2, pady=(6, 0))

        self.wrong_label = tk.Label(self.game_frame, text="")
        self.wrong_label.grid(row=2, column=0, columnspan=2, pady=(4, 8))

        tk.Label(self.game_frame, text="Guess a letter:").grid(row=3, column=0, sticky="w")
        self.guess_entry = tk.Entry(self.game_frame, width=8)
        self.guess_entry.grid(row=3, column=1, sticky="w")

        self.guess_button = tk.Button(
            self.game_frame, text="Guess", width=10, command=self.make_guess
        )
        self.guess_button.grid(row=4, column=0, columnspan=2, pady=(6, 0))

        self.status_label = tk.Label(self.game_frame, text="")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(6, 0))

        self.reset_button = tk.Button(
            self.game_frame, text="New Game", width=10, command=self.reset_game
        )
        self.reset_button.grid(row=6, column=0, columnspan=2, pady=(6, 0))

    def _show_setup(self) -> None:
        self.game_frame.pack_forget()
        self.setup_frame.pack()
        self.secret_entry.delete(0, tk.END)
        self.secret_entry.focus()

    def _show_game(self) -> None:
        self.setup_frame.pack_forget()
        self.game_frame.pack()
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus()

    def start_game(self) -> None:
        secret = self.secret_entry.get().strip().lower()
        if not secret:
            messagebox.showwarning("Hangman", "Please enter a secret word or phrase.")
            return
        if not all(ch.isalpha() or ch == " " for ch in secret):
            messagebox.showwarning("Hangman", "Use letters and spaces only (a-z, space).")
            return

        self.secret = secret
        self.guessed = set()
        self.wrong = set()
        self._show_game()
        self.update_display()
        self.status_label.config(
            text=f"{self.player_two.get().strip() or 'Player 2'}, start guessing."
        )

    def update_display(self) -> None:
        self.stage_label.config(text=HANGMAN_STAGES[len(self.wrong)])
        self.word_label.config(text=render_progress(self.secret, self.guessed))
        wrong_letters = " ".join(sorted(self.wrong))
        self.wrong_label.config(
            text=f"Wrong ({len(self.wrong)}/{MAX_WRONG}): {wrong_letters}"
        )

    def end_game(self, won: bool) -> None:
        player_two = self.player_two.get().strip() or "Player 2"
        if won:
            message = f"{player_two} wins! The word was: {self.secret}"
        else:
            message = f"{player_two} loses! The word was: {self.secret}"
        messagebox.showinfo("Game Over", message)
        self.status_label.config(text=message)
        self.guess_button.config(state=tk.DISABLED)
        self.guess_entry.config(state=tk.DISABLED)

    def make_guess(self) -> None:
        guess = self.guess_entry.get().strip().lower()
        self.guess_entry.delete(0, tk.END)

        if len(guess) != 1 or not guess.isalpha():
            self.status_label.config(text="Enter a single letter (a-z).")
            return
        if guess in self.guessed or guess in self.wrong:
            self.status_label.config(text="You already guessed that letter.")
            return

        if guess in self.secret:
            self.guessed.add(guess)
            self.status_label.config(text="Correct!")
        else:
            self.wrong.add(guess)
            self.status_label.config(text="Wrong guess.")

        self.update_display()

        if all(ch == " " or ch in self.guessed for ch in self.secret):
            self.end_game(won=True)
        elif len(self.wrong) >= MAX_WRONG:
            self.end_game(won=False)

    def reset_game(self) -> None:
        self.guess_button.config(state=tk.NORMAL)
        self.guess_entry.config(state=tk.NORMAL)
        self._show_setup()


if __name__ == "__main__":
    root = tk.Tk()
    app = HangmanApp(root)
    root.mainloop()
