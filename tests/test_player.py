from schocken.custom_player import Player
from schocken.base import Hand


def test_play_turn():
    player = Player("TestPlayer")
    for i in range(1, 4):
        final_hand, num_throws = player.play_turn(_print_throws=False, max_throws=i)

        # Check if the final hand is an instance of Hand
        assert isinstance(final_hand, Hand)

        # Check if the number of throws is smaller than or equal to the maximum allowed throws
        assert num_throws <= i

        # Check if the number of throws is within the expected range
        assert 1 <= num_throws <= 3

        # Check if the player's hand is correctly updated after the turn
        assert player.hand == final_hand
