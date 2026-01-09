# PenjiPet Desktop Simulator

This is a pygame-based simulator for testing the PenjiPet Vape Tamagotchi game without needing the Raspberry Pi Pico hardware.

## Requirements

- Python 3.7+
- pygame

## Installation

1. Install pygame:
```bash
pip install pygame
```

## Running the Simulator

Simply run the simulator script:

```bash
python simulator_main.py
```

## Controls

| Key | Function | Description |
|-----|----------|-------------|
| **SPACE** | Pen Button | Hold to vape (damages pet) |
| **M** or **DOWN** | Menu Button | Navigate/cycle through menu options |
| **ENTER** | Select Button | Confirm selections |
| **LEFT** / **RIGHT** | Game Controls | Move in mini-games |
| **ESC** | Quit | Close the simulator |

## Features

### Current Implementation

✅ **Pet Mode** - Main screen with animated cat sprite
- Health bar at top showing HP (0-100)
- Normal cat sprite when idle
- Coughing animation while vaping
- HP decreases 5 points per second while holding SPACE

✅ **Menu System** - Navigate with M/DOWN, select with ENTER/RIGHT
- Temperature settings (Low/Med/High)
- Mini-games menu (Ball Drop, Memory Match)
- Stats screen
- Exit back to pet

✅ **Temperature Settings**
- Low: 60% PWM
- Medium: 75% PWM
- High: 90% PWM
- Settings persist to settings.json

✅ **Stats Screen**
- Current HP / Max HP
- Total points earned
- Total vape hits
- Session time
- Games won

### Game Mechanics

**Health System:**
- Starting HP: 100
- Vaping damage: -5 HP per second (while pen button held)
- Pet dies at 0 HP → Game Over screen

**Points System (Not Yet Implemented):**
- Earn points from mini-games
- Every 10 points = +1 HP restored
- Play games to heal your pet!

### Mini-Games

✅ **Ball Drop Mini-Game**
- 20 second duration
- Catch falling balls with bucket
- **Controls:** LEFT = move left, RIGHT = move right, ENTER = confirm when done
- 10 points per ball caught
- Points automatically convert to HP (10 points = 1 HP)

✅ **Memory Match Mini-Game**
- 4x4 grid with matching pairs
- Watch pairs flash for 2 seconds
- Remember locations and select matching pairs
- **Controls:** DOWN = move cursor, ENTER = select cell
- 20 points per correct pair
- Points automatically convert to HP (10 points = 1 HP)

✅ **Point to HP Conversion**
- Automatic: Every 10 points earned = +1 HP restored
- Happens immediately after game ends
- HP cannot exceed maximum (100)

🔲 **Persistent Stats**
- Save lifetime stats
- High scores
- Total games played

## File Structure

```
PenjiPet-main/
├── simulator_main.py          # Main simulator entry point
├── pygame_mock_hardware.py    # Mock Pico hardware for pygame
├── penjipal_sim.py           # Modified penjipal for simulator
├── penjipal.py               # Original Pico version
├── config_settings.py        # Settings save/load (works for both)
├── init.py                   # Pico hardware init (not used in sim)
├── sh1106.py                 # OLED driver (not used in sim)
├── main.py                   # Original Pico main (not used in sim)
└── settings.json             # Saved settings (auto-created)
```

## How It Works

The simulator uses **mock hardware classes** that mimic the Raspberry Pi Pico interface:

- `MockDisplay` - Simulates SH1106 OLED using pygame Surface
- `MockButton` - Maps keyboard keys to button presses (pull-up logic)
- `MockPWM` - Simulates PWM for heating element control
- `MockFrameBuffer` - Compatible framebuffer for sprite rendering

The game logic in `simulator_main.py` is designed to work identically to how it will run on the actual Pico hardware.

## Testing Workflow

1. **Develop on Desktop** - Use the simulator to test all game logic
2. **Iterate Quickly** - Fast edit-test cycles without flashing Pico
3. **Deploy to Pico** - Once tested, deploy code to actual hardware

## Current State

The simulator currently has:
- ✅ Full menu navigation
- ✅ Temperature settings with persistence
- ✅ Vaping mechanics with HP damage
- ✅ Cough animations
- ✅ Stats tracking
- ✅ Health bar display
- ✅ **Ball Drop mini-game** (NEW!)
- ✅ **Memory Match mini-game** (NEW!)
- ✅ **Point-to-HP conversion system** (NEW!)
- ✅ Game over screen

**Next Steps:**
1. Add persistent lifetime stats
2. Balance game difficulty
3. Polish UI and animations
4. Port to actual Pico hardware

## Notes

- The simulator runs at 30 FPS (Pico will run at 10-15 FPS)
- Settings are saved to `settings.json` in the same directory
- The display is scaled 4x for visibility (512x256 window)
- Button debouncing uses 200ms delay to prevent rapid triggering

## Troubleshooting

**"pygame not found"**
```bash
pip install pygame
```

**Settings not saving**
- Check file permissions in the current directory
- Make sure you have write access

**Framerate issues**
- The simulator targets 30 FPS
- Lower-powered machines might run slower

## License

This is a personal project. Use freely for learning and experimentation.
