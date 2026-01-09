"""
Ball Drop Mini-Game
Catch falling balls to earn points and heal your pet
"""
import time
import random


class Ball:
    """Represents a falling ball"""
    def __init__(self, x):
        self.x = x
        self.y = 0
        self.size = 3
        self.speed = 15  # pixels per second
        self.active = True

    def update(self, delta_time):
        """Update ball position"""
        self.y += self.speed * delta_time
        if self.y >= 64:  # Reached bottom
            self.active = False

    def draw(self, display):
        """Draw the ball"""
        if self.active:
            # Draw a simple filled circle (rectangle for simplicity)
            display.fill_rect(int(self.x), int(self.y), self.size, self.size, 1)


class Bucket:
    """Player-controlled bucket to catch balls"""
    def __init__(self):
        self.x = 64 - 8  # Center of screen
        self.y = 58
        self.width = 16
        self.height = 4

    def move_left(self):
        """Move bucket left"""
        self.x = max(0, self.x - 8)

    def move_right(self):
        """Move bucket right"""
        self.x = min(128 - self.width, self.x + 8)

    def check_collision(self, ball):
        """Check if ball hits bucket"""
        if not ball.active:
            return False

        # Check if ball is at bucket height
        if ball.y + ball.size >= self.y and ball.y <= self.y + self.height:
            # Check horizontal overlap
            if ball.x + ball.size >= self.x and ball.x <= self.x + self.width:
                return True
        return False

    def draw(self, display):
        """Draw the bucket"""
        # Draw bucket as rectangle
        display.fill_rect(self.x, self.y, self.width, self.height, 1)
        # Draw top edge for visibility
        display.hline(self.x, self.y - 1, self.width, 1)


class BallDropGame:
    """Ball Drop mini-game"""

    GAME_DURATION = 20  # seconds
    POINTS_PER_BALL = 10
    MIN_SPAWN_INTERVAL = 0.5  # seconds
    MAX_SPAWN_INTERVAL = 2.0  # seconds

    def __init__(self):
        self.bucket = Bucket()
        self.balls = []
        self.score = 0
        self.time_remaining = self.GAME_DURATION
        self.next_spawn_time = random.uniform(self.MIN_SPAWN_INTERVAL, self.MAX_SPAWN_INTERVAL)
        self.spawn_timer = 0
        self.game_over = False

    def update(self, delta_time, left_pressed, right_pressed):
        """Update game state"""
        if self.game_over:
            return

        # Update timer
        self.time_remaining -= delta_time
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True
            return

        # Handle input
        if left_pressed:
            self.bucket.move_left()
        if right_pressed:
            self.bucket.move_right()

        # Spawn new balls
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.next_spawn_time:
            self.spawn_ball()
            self.spawn_timer = 0
            self.next_spawn_time = random.uniform(self.MIN_SPAWN_INTERVAL, self.MAX_SPAWN_INTERVAL)

        # Update balls
        for ball in self.balls[:]:
            ball.update(delta_time)

            # Check collision
            if self.bucket.check_collision(ball):
                self.score += self.POINTS_PER_BALL
                ball.active = False

            # Remove inactive balls
            if not ball.active:
                self.balls.remove(ball)

    def spawn_ball(self):
        """Spawn a new ball at random x position"""
        x = random.randint(0, 128 - 3)  # 3 is ball size
        self.balls.append(Ball(x))

    def draw(self, display):
        """Draw game screen"""
        display.fill(0)

        if not self.game_over:
            # Draw all balls
            for ball in self.balls:
                ball.draw(display)

            # Draw bucket
            self.bucket.draw(display)

            # Draw score
            display.text(f"Score:{self.score}", 2, 2, 1)

            # Draw time
            time_text = f"Time:{int(self.time_remaining)}"
            display.text(time_text, 75, 2, 1)
        else:
            # Game over screen
            display.text("TIME UP!", 40, 20, 1)
            display.text(f"Score: {self.score}", 35, 35, 1)
            display.text("Press SELECT", 25, 50, 1)

        display.show()

    def is_finished(self):
        """Check if game is over"""
        return self.game_over

    def get_score(self):
        """Get final score"""
        return self.score
