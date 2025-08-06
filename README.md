# Schocken

Schocken is a modern Python implementation of the traditional dice game "Schocken". This project provides a modular and extensible framework for simulating the game, including custom player strategies and detailed game statistics.

## Features
- Simulate the Schocken dice game with multiple players
- Easily add custom player strategies
- Track detailed game statistics (rounds, halves, mini-rounds, turns/throws)
- Extensible codebase for further development/analysis

## Project Structure
```
main.py                # Example for running the game
src/schocken/          # Core game logic and player classes
    base.py            # Abstract base player class
    custom_player.py   # Example custom player implementation
    game.py            # Game logic and management

LICENSE                # License information
pyproject.toml         # Project metadata
pytest.ini             # Pytest configuration
README.md              # Project documentation

tests/                 # Unit tests for game logic
    test_base.py       # Tests for base player
    test_game.py       # Tests for game logic
    test_hands.py      # Tests for hand evaluation
    test_player.py     # Tests for player classes
```

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

3. Install this repo as a pip package (*currently in v0.0.1, no external dependencies are required*):
   ```bash
   pip install . # or pip install -r requirements.txt
   ```
   or with uv:
   ```bash
   uv pip install . # or uv pip install -r requirements.txt
    ```

## Basic Usage
In oder to simulate a Schocken game, at least two players and a game instance need to be created.
After creation, the players have to be added to the game instance.
```python
from schocken.game import Game
from schocken.custom_player import Player

# Create a game instance and players
game = Game()
p1 = Player("Alice")
p2 = Player("Bob")
p3 = Player("Carol")

# Add players to the game
game.add_player([p1, p2, p3])
```
The game is organized in units called rounds, halves, mini-rounds and turns.
- **Turn**: A turn represents a players turn, i.e. the smallest unit of the game flow. Each turn is connected to exactly one player. In their turn, players can make 1 to 3 throws with the dice. At the end of the turn there is a final hand for the player.
- **Mini-round**: In a mini-round, all players have exactly one turn. The player with the worst final hand loses the mini-round and gets penalty chips corresponding to the best final hand of that mini-round.
- **Half**: A half consists of multiple mini-rounds. It either ends when a player has all penalty chips or when a Schock-out was thrown.
- **Round**: A round consists of two regular halves and an optional final third half. The round ends when either one player has lost both regular halves or when when the final half was played and one player has lost it.

All units can be played individually, however, the default would be to play an arbitrary number of rounds.
```python
# default option for playing the game
rounds = game.play_rounds(num_rounds=3)

# playing individual units of the game
r = game.play_round()
h = game.play_half()
mr = game.play_mini_round()
t = p1.play_turn()
```

An example usage can be found in the main script. It can be run with:
```bash
python main.py
```

In the example, you will see output showing:
- "Live" updates of a game, (if `print_info=True` in the `play_round()` method)
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

## Development & Testing
For quick development/debugging, use pip install in editable mode:
```bash
uv pip install -e .
```
Instead of building the package, this creates a reference to the current directory, allowing to modify and test the code without reinstalling.

To run tests, use:
```bash
pytest tests/
```
`-v` for verbose output, `-s` to see print statements.

## Customization
You can create your own player strategies by subclassing the `BasePlayer` class in `base.py`. See `custom_player.py` for an example.


## Design Decisions
- The game class (`Game`) manages the game flow, including rounds, halves, mini-rounds and points. The player class (`BasePlayer`) only defines the interface for player strategies, the rest is taken care of by the game instance. Thus, scores, points, chips etc. are all part of the game or its related data objects (Round, Half, Turn etc.) and not the player instances.
- The game was built for the main purpose of simulation and analysis. It is therefore at this point not designed for real-time interaction, but rather for running simulations and analyzing the results.
- The player logic is designed to be extensible, allowing for custom player strategies by subclassing the `BasePlayer` class. This allows for easy integration of different player behaviors without modifying the core. 

## Open Points
- game.py: Implement async functionality for real-time multiplayers
- Add a GUI/web interface for real-time multiplayer interaction/visualization
- Add a rulebook for the current implementation of the game (there might exist multiple variants of the game)

## License
This project is licensed under the MIT License. See `LICENSE` for details.
