"""
Memory Match Mini-Game
Remember matching pairs and select them to earn points
"""
import random


class MemoryGame:
    """Memory matching game"""

    POINTS_PER_MATCH = 20
    FLASH_DURATION = 2.0  # seconds to show the pairs
    GRID_SIZE = 4  # 4x4 grid

    def __init__(self):
        self.grid_size = self.GRID_SIZE
        self.cursor_x = 0
        self.cursor_y = 0
        self.selected_cells = []  # List of (x, y) tuples
        self.score = 0
        self.game_state = "SHOW"  # SHOW, PLAY, RESULT
        self.show_timer = 0
        self.pairs = []
        self.found_pairs = []
        self.game_over = False
        self.result_message = ""
        self.result_timer = 0

        # Generate pairs
        self._generate_pairs()

    def _generate_pairs(self):
        """Generate random matching pairs on the grid"""
        # Create a list of all positions
        positions = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size)]
        random.shuffle(positions)

        # Create 3-4 pairs
        num_pairs = 4
        self.pairs = []

        for i in range(num_pairs):
            if len(positions) >= 2:
                pos1 = positions.pop()
                pos2 = positions.pop()
                pair_id = i + 1  # 1, 2, 3, 4
                self.pairs.append((pos1, pos2, pair_id))

    def update(self, delta_time, nav_pressed, select_pressed):
        """Update game state"""
        if self.game_state == "SHOW":
            # Show pairs for a duration
            self.show_timer += delta_time
            if self.show_timer >= self.FLASH_DURATION:
                self.game_state = "PLAY"

        elif self.game_state == "PLAY":
            # Handle cursor movement
            if nav_pressed:
                self._move_cursor()

            # Handle selection
            if select_pressed:
                self._select_cell()

        elif self.game_state == "RESULT":
            # Show result for 2 seconds then end
            self.result_timer += delta_time
            if self.result_timer >= 2.0:
                self.game_over = True

    def _move_cursor(self):
        """Move cursor to next position"""
        self.cursor_x += 1
        if self.cursor_x >= self.grid_size:
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.grid_size:
                self.cursor_y = 0

    def _select_cell(self):
        """Select current cell"""
        pos = (self.cursor_x, self.cursor_y)

        # Don't select already selected cells
        if pos in self.selected_cells:
            return

        # Check if this position is part of a pair
        for pos1, pos2, pair_id in self.pairs:
            if pos == pos1 or pos == pos2:
                # Check if we already found this pair
                if pair_id in self.found_pairs:
                    return

                # Add to selected
                self.selected_cells.append(pos)

                # Check if we selected both positions of this pair
                if pos1 in self.selected_cells and pos2 in self.selected_cells:
                    # Match found!
                    self.score += self.POINTS_PER_MATCH
                    self.found_pairs.append(pair_id)
                    self.result_message = "MATCH!"
                return

        # Selected wrong cell
        self.selected_cells.append(pos)
        self.result_message = "MISS"

        # Check if game over
        if len(self.found_pairs) >= len(self.pairs) or len(self.selected_cells) >= 8:
            self.game_state = "RESULT"

    def draw(self, display):
        """Draw game screen"""
        display.fill(0)

        if self.game_state == "SHOW":
            # Show the pairs
            display.text("MEMORIZE!", 30, 2, 1)

            # Draw grid with pairs highlighted
            self._draw_grid(display, show_pairs=True)

            # Show timer
            time_left = self.FLASH_DURATION - self.show_timer
            display.text(f"{int(time_left)}s", 60, 56, 1)

        elif self.game_state == "PLAY":
            # Draw grid
            self._draw_grid(display, show_pairs=False)

            # Draw score
            display.text(f"Score:{self.score}", 2, 2, 1)

            # Draw status
            if self.result_message:
                msg_x = 45 if self.result_message == "MATCH!" else 50
                display.text(self.result_message, msg_x, 56, 1)

        elif self.game_state == "RESULT":
            # Show final result
            display.text("GAME OVER", 30, 15, 1)
            display.text(f"Score: {self.score}", 35, 30, 1)
            display.text(f"Found: {len(self.found_pairs)}/{len(self.pairs)}", 25, 42, 1)

        display.show()

    def _draw_grid(self, display, show_pairs=False):
        """Draw the grid"""
        cell_size = 12
        start_x = 20
        start_y = 15

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                px = start_x + x * cell_size
                py = start_y + y * cell_size

                # Draw cell border
                display.rect(px, py, cell_size - 1, cell_size - 1, 1)

                # Highlight cursor
                if x == self.cursor_x and y == self.cursor_y and self.game_state == "PLAY":
                    display.fill_rect(px + 1, py + 1, cell_size - 3, cell_size - 3, 1)

                # Show pairs during SHOW phase or if found
                pos = (x, y)
                if show_pairs:
                    for pos1, pos2, pair_id in self.pairs:
                        if pos == pos1 or pos == pos2:
                            # Draw pair number
                            display.text(str(pair_id), px + 3, py + 2, 1)
                            break
                elif pos in self.selected_cells:
                    # Show selected cells
                    display.text("X", px + 3, py + 2, 1)

    def is_finished(self):
        """Check if game is over"""
        return self.game_over

    def get_score(self):
        """Get final score"""
        return self.score
