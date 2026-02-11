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

SKY_TOP = "#7cc7ff"
SKY_BOTTOM = "#cfefff"
SUN_COLOR = "#ffe08a"
CLOUD_COLOR = "#f9fdff"

PIPE_LIGHT = "#3cb371"
PIPE_DARK = "#1f6b43"
GROUND_COLOR = "#c2b280"
GROUND_TOP = "#7dbb6a"
BIRD_COLOR = "#ffd24d"
BIRD_WING = "#f5b945"
TEXT_COLOR = "#1f1f1f"


class FlappyBirdApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flappy Bird")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=SKY_BOTTOM)
        self.canvas.pack()

        self._draw_background()

        self.score_text_shadow = self.canvas.create_text(
            WIDTH // 2 + 1,
            41,
            text="Score: 0",
            fill="#ffffff",
            font=("Segoe UI", 16, "bold"),
        )
        self.score_text = self.canvas.create_text(
            WIDTH // 2,
            40,
            text="Score: 0",
            fill=TEXT_COLOR,
            font=("Segoe UI", 16, "bold"),
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
        self.ground_top = self.canvas.create_rectangle(
            0, GROUND_Y - 10, WIDTH, GROUND_Y, fill=GROUND_TOP, outline=""
        )

        self.bird = self.canvas.create_oval(0, 0, 0, 0, fill=BIRD_COLOR, outline="", tags="bird")
        self.bird_wing = self.canvas.create_oval(
            0, 0, 0, 0, fill=BIRD_WING, outline="", tags="bird"
        )
        self.bird_eye = self.canvas.create_oval(
            0, 0, 0, 0, fill="#1f1f1f", outline="", tags="bird"
        )
        self._set_bird_position(HEIGHT // 2)

        self.velocity = 0.0
        self.pipes: list[tuple[int, int, int, int]] = []
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
        self.canvas.itemconfig(self.score_text_shadow, text="Score: 0")
        self.canvas.itemconfig(self.score_text, text="Score: 0")
        self.score = 0
        self.velocity = 0.0
        self.running = False
        self.game_over = False

        for top_id, bottom_id, top_cap, bottom_cap in self.pipes:
            self.canvas.delete(top_id)
            self.canvas.delete(bottom_id)
            self.canvas.delete(top_cap)
            self.canvas.delete(bottom_cap)
        self.pipes.clear()

        self._set_bird_position(HEIGHT // 2)
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
            fill=PIPE_LIGHT,
            outline=PIPE_DARK,
            width=2,
        )
        top_cap = self.canvas.create_rectangle(
            WIDTH - 4,
            gap_top - 14,
            WIDTH + PIPE_WIDTH + 4,
            gap_top,
            fill=PIPE_DARK,
            outline="",
        )
        bottom_id = self.canvas.create_rectangle(
            WIDTH,
            gap_bottom,
            WIDTH + PIPE_WIDTH,
            GROUND_Y,
            fill=PIPE_LIGHT,
            outline=PIPE_DARK,
            width=2,
        )
        bottom_cap = self.canvas.create_rectangle(
            WIDTH - 4,
            gap_bottom,
            WIDTH + PIPE_WIDTH + 4,
            gap_bottom + 14,
            fill=PIPE_DARK,
            outline="",
        )
        self.pipes.append((top_id, bottom_id, top_cap, bottom_cap))
        self._schedule_pipe()

    def _move_pipes(self) -> None:
        if not self.running:
            return
        to_remove: list[tuple[int, int, int, int]] = []
        for top_id, bottom_id, top_cap, bottom_cap in self.pipes:
            self.canvas.move(top_id, -PIPE_SPEED, 0)
            self.canvas.move(bottom_id, -PIPE_SPEED, 0)
            self.canvas.move(top_cap, -PIPE_SPEED, 0)
            self.canvas.move(bottom_cap, -PIPE_SPEED, 0)

            top_coords = self.canvas.coords(top_id)
            if top_coords[2] < 0:
                to_remove.append((top_id, bottom_id, top_cap, bottom_cap))
                self.score += 1
                self.canvas.itemconfig(self.score_text_shadow, text=f"Score: {self.score}")
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

        for top_id, bottom_id, top_cap, bottom_cap in to_remove:
            self.canvas.delete(top_id)
            self.canvas.delete(bottom_id)
            self.canvas.delete(top_cap)
            self.canvas.delete(bottom_cap)
            self.pipes.remove((top_id, bottom_id, top_cap, bottom_cap))

    def _bird_bounds(self) -> tuple[float, float, float, float]:
        return tuple(self.canvas.coords(self.bird))

    def _check_collisions(self) -> None:
        x1, y1, x2, y2 = self._bird_bounds()
        if y1 <= 0 or y2 >= GROUND_Y:
            self._end_game()
            return

        for top_id, bottom_id, _top_cap, _bottom_cap in self.pipes:
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
            self.canvas.move("bird", 0, self.velocity)
            self._move_pipes()
            self._check_collisions()
        self.root.after(16, self._tick)

    def _draw_background(self) -> None:
        steps = 14
        top_rgb = self._hex_to_rgb(SKY_TOP)
        bottom_rgb = self._hex_to_rgb(SKY_BOTTOM)
        band_height = HEIGHT // steps
        for i in range(steps):
            t = i / (steps - 1)
            color = self._rgb_to_hex(self._lerp_color(top_rgb, bottom_rgb, t))
            y1 = i * band_height
            y2 = HEIGHT if i == steps - 1 else (i + 1) * band_height
            self.canvas.create_rectangle(0, y1, WIDTH, y2, fill=color, outline="")

        self.canvas.create_oval(30, 40, 110, 120, fill=SUN_COLOR, outline="")

        self._draw_cloud(230, 90, 1.0)
        self._draw_cloud(300, 160, 0.8)
        self._draw_cloud(80, 160, 0.9)

    def _draw_cloud(self, x: int, y: int, scale: float) -> None:
        w = int(70 * scale)
        h = int(28 * scale)
        self.canvas.create_oval(x, y, x + w, y + h, fill=CLOUD_COLOR, outline="")
        self.canvas.create_oval(x + w // 3, y - h // 2, x + w, y + h // 2, fill=CLOUD_COLOR, outline="")
        self.canvas.create_oval(x + w // 2, y, x + w + w // 2, y + h, fill=CLOUD_COLOR, outline="")

    def _set_bird_position(self, center_y: int) -> None:
        left = BIRD_X - BIRD_SIZE // 2
        top = center_y - BIRD_SIZE // 2
        right = BIRD_X + BIRD_SIZE // 2
        bottom = center_y + BIRD_SIZE // 2

        self.canvas.coords(self.bird, left, top, right, bottom)
        self.canvas.coords(
            self.bird_wing,
            left + 2,
            top + BIRD_SIZE // 2,
            right - 6,
            bottom - 2,
        )
        self.canvas.coords(
            self.bird_eye,
            right - 10,
            top + 6,
            right - 5,
            top + 11,
        )

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    @staticmethod
    def _lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
        return (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FlappyBirdApp(root)
    root.mainloop()
