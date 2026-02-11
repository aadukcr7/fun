import random
import tkinter as tk
from tkinter import messagebox


class TicTacToeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.resizable(False, False)

        self.board = ["" for _ in range(9)]
        self.current = "X"
        self.vs_computer = tk.BooleanVar(value=False)
        self.game_over = False

        self._build_ui()
        self._update_status()

    def _build_ui(self) -> None:
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack()

        mode = tk.Checkbutton(
            top,
            text="Play vs Computer",
            variable=self.vs_computer,
            command=self._on_mode_change,
        )
        mode.grid(row=0, column=0, sticky="w")

        reset_btn = tk.Button(top, text="Reset", width=10, command=self.reset)
        reset_btn.grid(row=0, column=1, padx=(10, 0))

        self.status = tk.Label(top, text="", anchor="w")
        self.status.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        grid = tk.Frame(self.root, padx=10, pady=10)
        grid.pack(pady=(0, 10))

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                grid,
                text="",
                width=6,
                height=3,
                font=("Segoe UI", 14, "bold"),
                command=lambda idx=i: self.play(idx),
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.buttons.append(btn)

    def _on_mode_change(self) -> None:
        self.reset()

    def _update_status(self) -> None:
        if self.game_over:
            return
        if self.vs_computer.get():
            if self.current == "X":
                self.status.config(text="Your turn (X)")
            else:
                self.status.config(text="Computer thinking (O)")
        else:
            self.status.config(text=f"Player {self.current}'s turn")

    def reset(self) -> None:
        self.board = ["" for _ in range(9)]
        self.current = "X"
        self.game_over = False
        for btn in self.buttons:
            btn.config(text="", state=tk.NORMAL)
        self._update_status()

    def play(self, idx: int) -> None:
        if self.game_over or self.board[idx]:
            return
        if self.vs_computer.get() and self.current == "O":
            return

        self._make_move(idx, self.current)
        if self._check_end():
            return

        self.current = "O" if self.current == "X" else "X"
        self._update_status()

        if self.vs_computer.get() and self.current == "O":
            self.root.after(250, self._computer_move)

    def _make_move(self, idx: int, mark: str) -> None:
        self.board[idx] = mark
        self.buttons[idx].config(text=mark)

    def _computer_move(self) -> None:
        if self.game_over:
            return
        move = self._best_move("O", "X")
        self._make_move(move, "O")
        if self._check_end():
            return
        self.current = "X"
        self._update_status()

    def _best_move(self, me: str, other: str) -> int:
        # Win if possible, block if needed, otherwise pick a random spot.
        for idx in self._available_moves():
            if self._would_win(idx, me):
                return idx
        for idx in self._available_moves():
            if self._would_win(idx, other):
                return idx
        return random.choice(self._available_moves())

    def _available_moves(self) -> list[int]:
        return [i for i, v in enumerate(self.board) if not v]

    def _would_win(self, idx: int, mark: str) -> bool:
        self.board[idx] = mark
        win = self._winner() == mark
        self.board[idx] = ""
        return win

    def _winner(self) -> str | None:
        wins = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
        for a, b, c in wins:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def _check_end(self) -> bool:
        winner = self._winner()
        if winner:
            self.game_over = True
            for btn in self.buttons:
                btn.config(state=tk.DISABLED)
            if self.vs_computer.get():
                msg = "You win!" if winner == "X" else "Computer wins!"
            else:
                msg = f"Player {winner} wins!"
            messagebox.showinfo("Game Over", msg)
            self.status.config(text=msg)
            return True
        if all(self.board):
            self.game_over = True
            messagebox.showinfo("Game Over", "Draw!")
            self.status.config(text="Draw!")
            return True
        return False


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
