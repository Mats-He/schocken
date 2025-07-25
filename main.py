try:
    from schocken.custom_player import Player
    from schocken.game import Game
except ImportError:
    from src.schocken.custom_player import Player
    from src.schocken.game import Game


def main():
    print("\nWelcome to the game Schocken!")
    print("- Schocken heißt das Spiel! -\n")

    ###################################
    #           Example usage         #
    ###################################
    game = Game()

    # Create players for the game
    #   Note: Players with custom strategies like 'Player' can easily be created from the 'BasePlayer' abc-class.
    #   An example custom player (e.g. 'Player' in this example) can be found in custom_player.py
    p1 = Player("Alice")
    p2 = Player("Bob")
    p3 = Player("Carol")

    # Add players to the game instance
    game.add_player([p1, p2, p3])

    # Play three rounds (each round is entirely independent)
    for i in range(3):
        game.play_round(round_index=i, _print_info=True)

    # Get the final scores after all rounds
    scores = game.get_scores()
    print("\nAvailable statistics:")
    print(list(scores.keys()))
    print(f"Total rounds lost by players: {scores['rounds_lost']}")

    # More detailed game stats can be found in the game.rounds variable
    print("\nMajor game objects and their properties:")
    game_stats = {
        "Rounds": game.rounds[0],
        "Halves": game.rounds[0].halves[0],
        "Mini-rounds": game.rounds[0].halves[0].mini_rounds[0],
        "Turns": game.rounds[0].halves[0].mini_rounds[0].turns[0],
    }
    for name, stat in game_stats.items():
        print(f"{name}: {list(stat.__dict__.keys())}")


if __name__ == "__main__":
    main()
