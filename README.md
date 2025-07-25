# Schocken

Schocken is a Python implementation of the traditional dice game "Schocken". This project provides a modular and extensible framework for simulating the game, including custom player strategies and detailed game statistics.

## Features
- Simulate the Schocken dice game with multiple players
- Easily add custom player strategies
- Track detailed game statistics (rounds, halves, mini-rounds, turns/throws)
- Extensible codebase for further development/analysis

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Mats-He/schocken
   cd schocken
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate # Linux/macOS
   .venv\Scripts\activate # Windows
   ```
   or with uv:
   ```bash
   uv venv
   source .venv/bin/activate # Linux/macOS
   .venv\Scripts\activate # Windows
    ```

3. Install dependencies (*currently in v0.0.1, no external dependencies are required*):
   ```bash
   pip install .
   ```
   or with uv:
   ```bash
   uv pip install .
    ```

## Usage
In oder to simulate a Schocken game, at least two players and a game instance need to be created.
An example usage can be found in the main script. It can be run with:
```bash
python main.py
```

In the example, you will see output showing:
- "Live" updates of a game, (if `_print_info=True`)
- Final scores and statistics

### Live Updates
The "live" updates are print messages that look like this:
```
Playing round 0
        Playing half 0
                Schock out! by Bob.
                -> Half ended after 4 rounds. Alice lost.
        Playing half 1
                Schock out! by Bob.
                -> Half ended after 2 rounds. Carol lost.
                Half ended regularly
-> Final between Alice and Carol lost by Carol.

Playing round 1
        Playing half 0
                Schock out! by Alice.
                -> Half ended after 1 rounds. Bob lost.
        Playing half 1
                Schock out! by Carol.
                -> Half ended after 2 rounds. Bob lost.
Round lost clean by Bob
```
### Final Scores & Statistics
Among others, the scores and statistics look like this:
```
Available statistics:
['rounds_lost', 'halves_lost', 'minirounds_lost', 'hands_played']
Total rounds lost by players: {'Alice': 1, 'Bob': 0, 'Carol': 2}

Major game objects and their properties (for detailed analysis):
Rounds: ['round_index', 'halves', 'lost_by']
Halves: ['halves_index', 'active_players', 'mini_rounds', 'lost_by', 'stock_chips_gone', 'chip_manager']
Mini-rounds: ['mini_round_players', 'mini_round_index', 'turns', 'worst_turn', 'best_turn', 'given_chips', 'lost_by']
Turns: ['turn_index', 'player_id', 'final_hand']
```
## Design Decisions
- The game class (`Game`) manages the game flow, including rounds, halves, and mini-rounds and points. The player class (`BasePlayer`) only defines the interface for player strategies, the rest is taken care of by the game instance. Thus, scores, points, chips etc. are all part of the game or its related data objects (Round, Half, Turn etc.) and not the player instances.
- The game was build for the main purpose of simulation and analysis. It is therefore at this point not designed for real-time interaction, but rather for running simulations and analyzing the results.
- The player logic is designed to be extensible, allowing for custom player strategies by subclassing the `BasePlayer` class. This allows for easy integration of different player behaviors without modifying the core 

## Open Points
- game.py: Implement async functionality for real-time multiplayers
- Add a GUI/web interface for real-time multiplayer interaction/visualization
- Add a rulebook for the current implementation of the game (there might exist multiple variants of the game)

## Project Structure
```
main.py                # Entry point for running the game
src/schocken/          # Core game logic and player classes
    base.py            # Abstract base player class
    custom_player.py   # Example custom player implementation
    game.py            # Game logic and management
    __init__.py        # Package initialization
    __pycache__/       # Python cache files

LICENSE                # License information
pyproject.toml         # Project metadata
README.md              # Project documentation

tests/                 # Unit tests for game logic
    test_base.py       # Tests for base player
    test_game.py       # Tests for game logic
    test_hands.py      # Tests for hand evaluation
    __init__.py        # Test package initialization
    __pycache__/       # Test cache files
```

## Customization
You can create your own player strategies by subclassing the `BasePlayer` class in `base.py`. See `custom_player.py` for an example.

## License
This project is licensed under the MIT License. See `LICENSE` for details.
