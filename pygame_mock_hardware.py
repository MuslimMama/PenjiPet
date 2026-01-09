"""
Pygame-based mock hardware for testing Pico code on desktop
Simulates buttons, display, and other hardware components
"""
import pygame
import time


class MockPin:
    """Mock machine.Pin class for pygame simulation"""
    IN = 0
    OUT = 1
    PULL_UP = 1

    def __init__(self, pin_num, mode=None, pull=None):
        self.pin_num = pin_num
        self.mode = mode
        self.pull = pull
        self._value = 1 if pull == self.PULL_UP else 0

    def value(self, val=None):
        if val is not None:
            self._value = val
            return None
        return self._value


class MockButton:
    """Mock button that can be controlled by keyboard"""
    def __init__(self, pin_num, keyboard_key):
        self.pin = MockPin(pin_num, MockPin.IN, MockPin.PULL_UP)
        self.keyboard_key = keyboard_key
        self._pressed = False

    def value(self):
        # Returns 0 when pressed (pull-up logic)
        return 0 if self._pressed else 1

    def update(self, keys):
        """Update button state based on pygame keys"""
        self._pressed = keys[self.keyboard_key]


class MockPWM:
    """Mock PWM for simulating heating element"""
    def __init__(self, pin):
        self.pin = pin
        self._freq = 1000
        self._duty = 0

    def freq(self, f=None):
        if f is not None:
            self._freq = f
        return self._freq

    def duty_u16(self, duty=None):
        if duty is not None:
            self._duty = duty
        return self._duty

    def get_duty_percent(self):
        """Get duty cycle as percentage"""
        return (self._duty / 65535) * 100 if self._duty > 0 else 0


class MockI2C:
    """Mock I2C interface (not really used in pygame simulator)"""
    def __init__(self, channel, scl=None, sda=None, freq=400000):
        self.channel = channel
        self.scl = scl
        self.sda = sda
        self.freq = freq


class MockFrameBuffer:
    """Mock framebuffer that stores bitmap data"""
    MONO_HLSB = 3

    def __init__(self, buffer, width, height, format):
        self.buffer = buffer
        self.width = width
        self.height = height
        self.format = format


class MockDisplay:
    """
    Mock SH1106 OLED display using pygame
    Mimics the interface of sh1106.SH1106_I2C
    """
    def __init__(self, width, height, i2c=None, res=None, addr=0x3C, delay=0):
        self.width = width
        self.height = height
        self.scale = 4  # Scale factor for pygame window

        # Create pygame surface for the display
        self.surface = pygame.Surface((width, height))
        self.surface.fill((0, 0, 0))  # Black background

        # Font for text rendering
        pygame.font.init()
        self.font = pygame.font.Font(None, 8)  # Small font to match OLED

    def fill(self, color):
        """Fill entire display with color (0=black, 1=white)"""
        pygame_color = (255, 255, 255) if color else (0, 0, 0)
        self.surface.fill(pygame_color)

    def fill_rect(self, x, y, w, h, color):
        """Fill rectangle with color"""
        pygame_color = (255, 255, 255) if color else (0, 0, 0)
        pygame.draw.rect(self.surface, pygame_color, (x, y, w, h))

    def text(self, string, x, y, color=1):
        """Draw text at position"""
        pygame_color = (255, 255, 255) if color else (0, 0, 0)
        text_surface = self.font.render(string, True, pygame_color)
        self.surface.blit(text_surface, (x, y))

    def pixel(self, x, y, color=None):
        """Set or get pixel"""
        if color is not None:
            pygame_color = (255, 255, 255) if color else (0, 0, 0)
            self.surface.set_at((x, y), pygame_color)
        else:
            pixel_color = self.surface.get_at((x, y))
            return 1 if pixel_color[0] > 127 else 0

    def hline(self, x, y, w, color):
        """Draw horizontal line"""
        pygame_color = (255, 255, 255) if color else (0, 0, 0)
        pygame.draw.line(self.surface, pygame_color, (x, y), (x + w - 1, y))

    def vline(self, x, y, h, color):
        """Draw vertical line"""
        pygame_color = (255, 255, 255) if color else (0, 0, 0)
        pygame.draw.line(self.surface, pygame_color, (x, y), (x, y + h - 1))

    def rect(self, x, y, w, h, color):
        """Draw rectangle outline"""
        pygame_color = (255, 255, 255) if color else (0, 0, 0)
        pygame.draw.rect(self.surface, pygame_color, (x, y, w, h), 1)

    def blit(self, fbuf, x, y, key=-1):
        """Blit a framebuffer onto the display"""
        # Convert framebuffer bytearray to pygame surface
        if hasattr(fbuf, 'buffer'):
            # It's a MockFrameBuffer or real FrameBuffer
            self._blit_framebuffer(fbuf.buffer, fbuf.width, fbuf.height, x, y)

    def _blit_framebuffer(self, buffer, width, height, x, y):
        """Convert MONO_HLSB framebuffer to pygame surface and blit"""
        # MONO_HLSB format: Horizontal LSB
        # Try MSB first in byte (bit 7 = leftmost pixel)
        bytes_per_row = width // 8

        for py in range(height):
            for px in range(width):
                # Which byte in this row?
                byte_in_row = px // 8
                # Which bit in that byte? Try MSB first (7 = leftmost)
                bit_in_byte = 7 - (px % 8)

                # Calculate absolute byte index
                byte_index = py * bytes_per_row + byte_in_row

                if byte_index < len(buffer):
                    byte_val = buffer[byte_index]
                    pixel_on = (byte_val >> bit_in_byte) & 1

                    if pixel_on:
                        self.surface.set_at((px + x, py + y), (255, 255, 255))
                    else:
                        self.surface.set_at((px + x, py + y), (0, 0, 0))

    def show(self):
        """Update display (no-op in pygame, rendering happens in main loop)"""
        pass

    def render_to_screen(self, screen):
        """Render the scaled display to the pygame window"""
        scaled_surface = pygame.transform.scale(
            self.surface,
            (self.width * self.scale, self.height * self.scale)
        )
        screen.blit(scaled_surface, (0, 0))


class HardwareSimulator:
    """Main hardware simulator for pygame"""

    def __init__(self):
        pygame.init()

        # Display settings
        self.display_width = 128
        self.display_height = 64
        self.scale = 4

        # Create window
        window_width = self.display_width * self.scale
        window_height = self.display_height * self.scale + 100  # Extra space for UI
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("PenjiPet Simulator - Vape Tamagotchi")

        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.fps = 30

        # Mock hardware components
        self.i2c = MockI2C(0)
        self.penbutton = MockButton(6, pygame.K_SPACE)
        self.menubutton = MockButton(7, pygame.K_m)
        self.selectbutton = MockButton(8, pygame.K_RETURN)
        self.oled = MockDisplay(self.display_width, self.display_height)

        # Track key events for single presses
        self.menu_key_pressed = False
        self.select_key_pressed = False
        self.left_key_pressed = False
        self.right_key_pressed = False

        # PWM for heating element
        self.pwm_pin = MockPin(0)
        self.volts_pwm = MockPWM(self.pwm_pin)

        # UI font
        self.ui_font = pygame.font.Font(None, 24)

        self.running = True

    def update_inputs(self):
        """Update button states from keyboard"""
        keys = pygame.key.get_pressed()
        self.penbutton.update(keys)
        self.menubutton.update(keys)
        self.selectbutton.update(keys)

    def render(self, stats=None):
        """Render everything to screen"""
        # Clear screen
        self.screen.fill((40, 40, 40))

        # Render OLED display
        self.oled.render_to_screen(self.screen)

        # Render UI controls info
        ui_y = self.display_height * self.scale + 10

        controls = [
            "SPACE: Vape (hold)",
            "M/DOWN: Navigate menus",
            "LEFT/RIGHT: Game controls",
            "ENTER: Select/Confirm"
        ]

        for i, text in enumerate(controls):
            text_surface = self.ui_font.render(text, True, (200, 200, 200))
            self.screen.blit(text_surface, (10, ui_y + i * 25))

        # Render stats if provided
        if stats:
            stats_x = 300
            stat_texts = [
                f"HP: {stats.get('hp', 0)}",
                f"Temp: {stats.get('temp', 'med')}",
                f"PWM: {self.volts_pwm.get_duty_percent():.1f}%"
            ]

            for i, text in enumerate(stat_texts):
                text_surface = self.ui_font.render(text, True, (255, 255, 100))
                self.screen.blit(text_surface, (stats_x, ui_y + i * 25))

        pygame.display.flip()

    def process_events(self):
        """Process pygame events"""
        # Reset single-press flags
        self.menu_key_pressed = False
        self.select_key_pressed = False
        self.left_key_pressed = False
        self.right_key_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_m or event.key == pygame.K_DOWN:
                    self.menu_key_pressed = True
                elif event.key == pygame.K_RETURN:
                    self.select_key_pressed = True
                elif event.key == pygame.K_LEFT:
                    self.left_key_pressed = True
                elif event.key == pygame.K_RIGHT:
                    self.right_key_pressed = True

    def tick(self):
        """Tick the simulator clock"""
        self.clock.tick(self.fps)
        return self.clock.get_time() / 1000.0  # Return delta time in seconds

    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()


# Mock module exports to mimic micropython modules
class machine:
    """Mock machine module"""
    Pin = MockPin
    I2C = MockI2C
    PWM = MockPWM


class framebuf:
    """Mock framebuf module"""
    FrameBuffer = MockFrameBuffer
    MONO_HLSB = 3
