"""
Desktop Pygame Simulator for PenjiPet Vape Tamagotchi
Run this file to test the game without needing the Raspberry Pi Pico
"""
import sys
import time
import pygame_mock_hardware as mock
from pygame_mock_hardware import framebuf

# Import existing game modules (use sim version of penjipal)
import penjipal_sim as penjipal
import config_settings
import game_ball_drop
import game_memory


class GameState:
    """Game state enumeration"""
    PET_MODE = "pet"
    MENU = "menu"
    TEMP_MENU = "temp_menu"
    STATS = "stats"
    GAMES_MENU = "games_menu"
    GAME_BALL_DROP = "ball_drop"
    GAME_MEMORY = "memory"
    GAME_OVER = "game_over"


class PenjiPetSimulator:
    """Main game simulator"""

    def __init__(self):
        # Initialize hardware simulator
        self.hw = mock.HardwareSimulator()

        # Initialize game components
        self.oled = self.hw.oled
        self.penbutton = self.hw.penbutton
        self.menubutton = self.hw.menubutton
        self.selectbutton = self.hw.selectbutton
        self.volts_pwm = self.hw.volts_pwm

        # Load config
        self.config = config_settings.load_settings()
        if self.config is None:
            self.config = {"current_temp": "med"}
            config_settings.update_settings(self.config)

        # Temperature settings
        self.temp_levels = {
            "low": int(2**16 * 0.6),
            "med": int(2**16 * 0.75),
            "high": int(2**16 * 0.9)
        }
        self.volts_pwm.duty_u16(self.temp_levels[self.config["current_temp"]])

        # Initialize pet
        self.hp = 100
        self.max_hp = 100
        self.points = 0
        self.pal = penjipal.penjiPal(self.hp)

        # Game state
        self.state = GameState.PET_MODE
        self.menu_cursor = 0
        self.temp_menu_cursor = 0

        # Stats tracking
        self.total_vape_hits = 0
        self.session_start = time.time()
        self.games_won = 0

        # Vaping mechanics
        self.vaping = False
        self.vape_damage_rate = 5  # HP per second
        self.last_vape_damage_time = time.time()

        # Animation
        self.cough_animation_frame = 0
        self.cough_animation_timer = 0

        # Mini-games
        self.current_game = None
        self.games_menu_cursor = 0

    def update(self, delta_time):
        """Main update loop"""
        # Update inputs
        self.hw.update_inputs()

        # Handle vaping
        self.handle_vaping(delta_time)

        # Update based on current state
        if self.state == GameState.PET_MODE:
            self.update_pet_mode(delta_time)
        elif self.state == GameState.MENU:
            self.update_menu()
        elif self.state == GameState.TEMP_MENU:
            self.update_temp_menu()
        elif self.state == GameState.STATS:
            self.update_stats()
        elif self.state == GameState.GAMES_MENU:
            self.update_games_menu()
        elif self.state == GameState.GAME_BALL_DROP:
            self.update_ball_drop_game(delta_time)
        elif self.state == GameState.GAME_MEMORY:
            self.update_memory_game(delta_time)
        elif self.state == GameState.GAME_OVER:
            self.update_game_over()

        # Check for game over
        if self.hp <= 0 and self.state != GameState.GAME_OVER:
            self.state = GameState.GAME_OVER

    def handle_vaping(self, delta_time):
        """Handle vaping mechanics"""
        pen_pressed = self.penbutton.value() == 0

        if pen_pressed and not self.vaping:
            # Started vaping
            self.vaping = True
            self.total_vape_hits += 1

        elif not pen_pressed and self.vaping:
            # Stopped vaping
            self.vaping = False
            self.cough_animation_frame = 0

        # Deal damage while vaping
        if self.vaping:
            current_time = time.time()
            time_since_last_damage = current_time - self.last_vape_damage_time

            if time_since_last_damage >= 1.0:  # 1 second intervals
                self.hp -= self.vape_damage_rate
                if self.hp < 0:
                    self.hp = 0
                self.last_vape_damage_time = current_time

            # Update cough animation
            self.cough_animation_timer += delta_time
            if self.cough_animation_timer >= 0.2:  # Change frame every 200ms
                self.cough_animation_frame = (self.cough_animation_frame + 1) % 2
                self.cough_animation_timer = 0

    def update_pet_mode(self, delta_time):
        """Update pet display mode"""
        self.oled.fill(0)

        # Draw health bar
        self.draw_health_bar()

        # Draw pet sprite
        if self.vaping:
            # Alternate between cough animations
            if self.cough_animation_frame == 0:
                self.oled.blit(self.pal.get_cough_fb(), 0, 0)
            else:
                self.oled.blit(self.pal.get_cough2_fb(), 0, 0)
        else:
            # Normal cat sprite
            self.oled.blit(self.pal.get_cat_fb(), 0, 0)

        self.oled.show()

        # Check for menu button (using event-based input)
        if self.hw.menu_key_pressed:
            self.state = GameState.MENU
            self.menu_cursor = 0

    def draw_health_bar(self):
        """Draw HP bar at top of screen"""
        bar_width = 100
        bar_height = 6
        bar_x = (128 - bar_width) // 2
        bar_y = 2

        # Background
        self.oled.fill_rect(bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2, 1)
        self.oled.fill_rect(bar_x, bar_y, bar_width, bar_height, 0)

        # Health bar fill
        fill_width = int((self.hp / self.max_hp) * bar_width)
        if fill_width > 0:
            self.oled.fill_rect(bar_x, bar_y, fill_width, bar_height, 1)

        # HP text
        hp_text = f"{self.hp}/{self.max_hp}"
        self.oled.text(hp_text, 2, 2, 1)

    def update_menu(self):
        """Update main menu"""
        self.oled.fill(0)

        menu_items = ["Temp", "Games", "Stats", "Exit"]
        y_start = 10

        # Draw menu items
        for i, item in enumerate(menu_items):
            self.oled.text(item, 20, y_start + i * 10)

        # Draw cursor
        self.oled.text("<", 10, y_start + self.menu_cursor * 10)

        self.oled.show()

        # Handle menu navigation
        if self.hw.menu_key_pressed:
            self.menu_cursor = (self.menu_cursor + 1) % len(menu_items)

        # Handle selection
        if self.hw.select_key_pressed:
            if self.menu_cursor == 0:  # Temp
                self.state = GameState.TEMP_MENU
                self.temp_menu_cursor = 0
            elif self.menu_cursor == 1:  # Games
                self.state = GameState.GAMES_MENU
            elif self.menu_cursor == 2:  # Stats
                self.state = GameState.STATS
            elif self.menu_cursor == 3:  # Exit
                self.state = GameState.PET_MODE

    def update_temp_menu(self):
        """Update temperature menu"""
        self.oled.fill(0)

        temp_items = ["Low", "Medium", "High", "Exit"]
        y_start = 10

        # Draw menu items
        for i, item in enumerate(temp_items):
            self.oled.text(item, 20, y_start + i * 10)

        # Draw cursor
        self.oled.text("<", 10, y_start + self.temp_menu_cursor * 10)

        self.oled.show()

        # Handle navigation
        if self.hw.menu_key_pressed:
            self.temp_menu_cursor = (self.temp_menu_cursor + 1) % len(temp_items)

        # Handle selection
        if self.hw.select_key_pressed:
            if self.temp_menu_cursor == 0:  # Low
                self.config["current_temp"] = "low"
                self.volts_pwm.duty_u16(self.temp_levels["low"])
            elif self.temp_menu_cursor == 1:  # Medium
                self.config["current_temp"] = "med"
                self.volts_pwm.duty_u16(self.temp_levels["med"])
            elif self.temp_menu_cursor == 2:  # High
                self.config["current_temp"] = "high"
                self.volts_pwm.duty_u16(self.temp_levels["high"])

            config_settings.update_settings(self.config)
            self.state = GameState.MENU

    def update_stats(self):
        """Update stats screen"""
        self.oled.fill(0)

        self.oled.text("=== STATS ===", 20, 2)

        session_time = int(time.time() - self.session_start)
        minutes = session_time // 60
        seconds = session_time % 60

        stats_lines = [
            f"HP: {self.hp}/{self.max_hp}",
            f"Points: {self.points}",
            f"Vapes: {self.total_vape_hits}",
            f"Time: {minutes}m{seconds}s",
            f"Games: {self.games_won}"
        ]

        for i, line in enumerate(stats_lines):
            self.oled.text(line, 10, 15 + i * 9)

        self.oled.text("Press SELECT", 20, 58)

        self.oled.show()

        # Return to menu
        if self.hw.select_key_pressed:
            self.state = GameState.MENU

    def update_games_menu(self):
        """Update games selection menu"""
        self.oled.fill(0)

        game_items = ["Ball Drop", "Memory", "Exit"]
        y_start = 15

        # Draw title
        self.oled.text("MINI-GAMES", 25, 2, 1)

        # Draw menu items
        for i, item in enumerate(game_items):
            self.oled.text(item, 30, y_start + i * 12)

        # Draw cursor
        self.oled.text("<", 15, y_start + self.games_menu_cursor * 12)

        self.oled.show()

        # Handle navigation
        if self.hw.menu_key_pressed:
            self.games_menu_cursor = (self.games_menu_cursor + 1) % len(game_items)

        # Handle selection
        if self.hw.select_key_pressed:
            if self.games_menu_cursor == 0:  # Ball Drop
                self.current_game = game_ball_drop.BallDropGame()
                self.state = GameState.GAME_BALL_DROP
            elif self.games_menu_cursor == 1:  # Memory
                self.current_game = game_memory.MemoryGame()
                self.state = GameState.GAME_MEMORY
            elif self.games_menu_cursor == 2:  # Exit
                self.state = GameState.MENU

    def update_ball_drop_game(self, delta_time):
        """Update ball drop mini-game"""
        if self.current_game is None:
            self.state = GameState.GAMES_MENU
            return

        # Get input - dedicated left/right arrow keys
        left_pressed = self.hw.left_key_pressed
        right_pressed = self.hw.right_key_pressed

        # Update game
        self.current_game.update(delta_time, left_pressed, right_pressed)

        # Draw game
        self.current_game.draw(self.oled)

        # Check if finished
        if self.current_game.is_finished() and self.hw.select_key_pressed:
            # Award points and convert to HP
            score = self.current_game.get_score()
            self.points += score
            hp_gained = score // 10  # 10 points = 1 HP
            self.hp = min(self.max_hp, self.hp + hp_gained)

            if score > 0:
                self.games_won += 1

            # Return to games menu
            self.current_game = None
            self.state = GameState.GAMES_MENU

    def update_memory_game(self, delta_time):
        """Update memory match mini-game"""
        if self.current_game is None:
            self.state = GameState.GAMES_MENU
            return

        # Get input
        nav_pressed = self.hw.menu_key_pressed
        select_pressed = self.hw.select_key_pressed

        # Update game
        self.current_game.update(delta_time, nav_pressed, select_pressed)

        # Draw game
        self.current_game.draw(self.oled)

        # Check if finished
        if self.current_game.is_finished():
            # Award points and convert to HP
            score = self.current_game.get_score()
            self.points += score
            hp_gained = score // 10  # 10 points = 1 HP
            self.hp = min(self.max_hp, self.hp + hp_gained)

            if score > 0:
                self.games_won += 1

            # Return to games menu
            self.current_game = None
            self.state = GameState.GAMES_MENU

    def update_game_over(self):
        """Update game over screen"""
        self.oled.fill(0)
        self.oled.text("GAME OVER", 30, 20)
        self.oled.text("Your pet died", 20, 32)
        self.oled.text(f"Time: {int(time.time() - self.session_start)}s", 20, 44)
        self.oled.show()

    def get_stats_dict(self):
        """Get stats dictionary for display"""
        return {
            "hp": self.hp,
            "temp": self.config["current_temp"],
            "points": self.points,
            "vape_hits": self.total_vape_hits
        }

    def run(self):
        """Main game loop"""
        print("PenjiPet Simulator Started!")
        print("Controls:")
        print("  SPACE - Pen Button (Vape)")
        print("  M - Menu Button")
        print("  ENTER - Select Button")
        print("  ESC - Quit")

        while self.hw.running:
            # Process events
            self.hw.process_events()

            # Get delta time
            delta_time = self.hw.tick()

            # Update game logic
            self.update(delta_time)

            # Render
            self.hw.render(self.get_stats_dict())

        # Cleanup
        self.hw.cleanup()
        print("Simulator closed.")


if __name__ == "__main__":
    game = PenjiPetSimulator()
    game.run()
