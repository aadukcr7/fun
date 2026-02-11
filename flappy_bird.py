import random
import tkinter as tk


WIDTH = 400
HEIGHT = 600
GROUND_Y = 540

BIRD_X = 100
BIRD_SIZE = 26

GRAVITY = 0.45
FLAP_STRENGTH = -8.5

PIPE_WIDTH = 70
PIPE_GAP = 160
PIPE_SPEED = 3.2
PIPE_INTERVAL_MS = 1600

BG_COLOR = "#87ceeb"
PIPE_COLOR = "#2e8b57"
GROUND_COLOR = "#c2b280"
BIRD_COLOR = "#ffd24d"
TEXT_COLOR = "#1f1f1f"


class FlappyBirdApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flappy Bird")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
        self.canvas.pack()

        self.score_text = self.canvas.create_text(
            WIDTH // 2, 40, text="Score: 0", fill=TEXT_COLOR, font=("Segoe UI", 16, "bold")
        )
        self.message_text = self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text="Click or press Space to start",
            fill=TEXT_COLOR,
            font=("Segoe UI", 14, "bold"),
        )

        self.ground = self.canvas.create_rectangle(
            0, GROUND_Y, WIDTH, HEIGHT, fill=GROUND_COLOR, outline=""
        )

        self.bird = self.canvas.create_oval(
            BIRD_X - BIRD_SIZE // 2,
            HEIGHT // 2 - BIRD_SIZE // 2,
            BIRD_X + BIRD_SIZE // 2,
            HEIGHT // 2 + BIRD_SIZE // 2,
            fill=BIRD_COLOR,
            outline="",
        )

        self.velocity = 0.0
        self.pipes: list[tuple[int, int]] = []
        self.score = 0
        self.running = False
        self.game_over = False
        self.pipe_timer: str | None = None

        self.root.bind("<space>", self.flap)
        self.root.bind("<Button-1>", self.flap)

        self._tick()

    def start_game(self) -> None:
        if self.running:
            return
        if self.game_over:
            self.reset_game()
        self.running = True
        self.canvas.itemconfig(self.message_text, text="")
        self._schedule_pipe()

    def reset_game(self) -> None:
        self.canvas.itemconfig(self.score_text, text="Score: 0")
        self.score = 0
        self.velocity = 0.0
        self.running = False
        self.game_over = False

        for top_id, bottom_id in self.pipes:
            self.canvas.delete(top_id)
            self.canvas.delete(bottom_id)
        self.pipes.clear()

        self.canvas.coords(
            self.bird,
            BIRD_X - BIRD_SIZE // 2,
            HEIGHT // 2 - BIRD_SIZE // 2,
            BIRD_X + BIRD_SIZE // 2,
            HEIGHT // 2 + BIRD_SIZE // 2,
        )
        self.canvas.itemconfig(self.message_text, text="Click or press Space to start")

    def flap(self, _event: tk.Event | None = None) -> None:
        if not self.running:
            self.start_game()
        if self.game_over:
            return
        self.velocity = FLAP_STRENGTH

    def _schedule_pipe(self) -> None:
        if self.pipe_timer:
            self.root.after_cancel(self.pipe_timer)
        self.pipe_timer = self.root.after(PIPE_INTERVAL_MS, self._spawn_pipe)

    def _spawn_pipe(self) -> None:
        if not self.running or self.game_over:
            return
        gap_center = random.randint(160, GROUND_Y - 160)
        gap_top = gap_center - PIPE_GAP // 2
        gap_bottom = gap_center + PIPE_GAP // 2

        top_id = self.canvas.create_rectangle(
            WIDTH,
            0,
            WIDTH + PIPE_WIDTH,
            gap_top,
            fill=PIPE_COLOR,
            outline="",
        )
        bottom_id = self.canvas.create_rectangle(
            WIDTH,
            gap_bottom,
            WIDTH + PIPE_WIDTH,
            GROUND_Y,
            fill=PIPE_COLOR,
            outline="",
        )
        self.pipes.append((top_id, bottom_id))
        self._schedule_pipe()

    def _move_pipes(self) -> None:
        if not self.running:
            return
        to_remove: list[tuple[int, int]] = []
        for top_id, bottom_id in self.pipes:
            self.canvas.move(top_id, -PIPE_SPEED, 0)
            self.canvas.move(bottom_id, -PIPE_SPEED, 0)

            top_coords = self.canvas.coords(top_id)
            if top_coords[2] < 0:
                to_remove.append((top_id, bottom_id))
                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

        for top_id, bottom_id in to_remove:
            self.canvas.delete(top_id)
            self.canvas.delete(bottom_id)
            self.pipes.remove((top_id, bottom_id))

    def _bird_bounds(self) -> tuple[float, float, float, float]:
        return tuple(self.canvas.coords(self.bird))

    def _check_collisions(self) -> None:
        x1, y1, x2, y2 = self._bird_bounds()
        if y1 <= 0 or y2 >= GROUND_Y:
            self._end_game()
            return

        for top_id, bottom_id in self.pipes:
            if self._overlap(self.canvas.coords(top_id), (x1, y1, x2, y2)):
                self._end_game()
                return
            if self._overlap(self.canvas.coords(bottom_id), (x1, y1, x2, y2)):
                self._end_game()
                return

    def _overlap(self, rect_a: list[float], rect_b: tuple[float, float, float, float]) -> bool:
        ax1, ay1, ax2, ay2 = rect_a
        bx1, by1, bx2, by2 = rect_b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

    def _end_game(self) -> None:
        if self.game_over:
            return
        self.game_over = True
        self.running = False
        self.canvas.itemconfig(
            self.message_text, text="Game Over! Click or press Space to restart"
        )

    def _tick(self) -> None:
        if self.running and not self.game_over:
            self.velocity += GRAVITY
            self.canvas.move(self.bird, 0, self.velocity)
            self._move_pipes()
            self._check_collisions()
        self.root.after(16, self._tick)


if __name__ == "__main__":
    root = tk.Tk()
    app = FlappyBirdApp(root)
    root.mainloop()
