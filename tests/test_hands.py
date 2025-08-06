import pytest
from src.schocken.base import Hand, Die, Turn, MiniRound
from src.schocken.game import Game
from src.schocken.custom_player import Player


def test_hand_sorting():
    hand1 = Hand(_dice=[Die(1), Die(1), Die(1)])  # best
    hand2 = Hand(_dice=[Die(1), Die(1), Die(4)])  # middle
    hand3 = Hand(_dice=[Die(1), Die(1), Die(3)])  # worst
    hands = [hand2, hand3, hand1]
    hands.sort()
    assert hands[0] == hand3
    assert hands[1] == hand2
    assert hands[2] == hand1


def test_hand_sorting_w_player_ind():
    hand1 = Hand(_dice=[Die(1), Die(1), Die(1)], players_turn_ind=1)  # best
    hand2 = Hand(_dice=[Die(1), Die(1), Die(4)], players_turn_ind=1)  # middle
    hand3 = Hand(_dice=[Die(1), Die(1), Die(3)], players_turn_ind=1)  # worst
    hands = [hand2, hand3, hand1]
    hands.sort()
    assert hands[0] == hand3
    assert hands[1] == hand2
    assert hands[2] == hand1

    hand1 = Hand(_dice=[Die(1), Die(1), Die(3)], players_turn_ind=1)  # worst
    hand2 = Hand(_dice=[Die(1), Die(1), Die(4)], players_turn_ind=1)  # best
    hand3 = Hand(_dice=[Die(1), Die(1), Die(3)], players_turn_ind=1)  # worst
    hands = [hand2, hand3, hand1]
    hands.sort()
    assert hands[0] == hand3
    assert hands[1] == hand1
    assert hands[2] == hand2
    assert hand1 == hand3

    hand1 = Hand(_dice=[Die(1), Die(1), Die(3)], players_turn_ind=3)  # worst
    hand2 = Hand(_dice=[Die(1), Die(1), Die(4)], players_turn_ind=1)  # best
    hand3 = Hand(_dice=[Die(1), Die(1), Die(3)], players_turn_ind=2)  # middle
    hands = [hand2, hand3, hand1]
    hands.sort()
    assert hands[0] == hand1
    assert hands[1] == hand3
    assert hands[2] == hand2
    assert hand1 != hand3


def test_turn_sorting():
    hand1 = Hand(_dice=[Die(1), Die(1), Die(3)], players_turn_ind=1)  # worst
    hand2 = Hand(_dice=[Die(1), Die(1), Die(4)], players_turn_ind=1)  # best
    hand3 = Hand(_dice=[Die(1), Die(1), Die(4)], players_turn_ind=1)  # best

    turn1 = Turn(turn_index=1, final_hand=hand1)
    turn2 = Turn(turn_index=1, final_hand=hand2)
    turn3 = Turn(turn_index=1, final_hand=hand3)

    assert turn1 < turn2
    assert turn2 == turn3

    hand1 = Hand(_dice=[Die(1), Die(1), Die(3)], players_turn_ind=1)  # worst
    hand2 = Hand(_dice=[Die(1), Die(1), Die(4)], players_turn_ind=2)  # best
    hand3 = Hand(_dice=[Die(1), Die(1), Die(4)], players_turn_ind=3)  # middle

    turn1 = Turn(turn_index=1, final_hand=hand1)
    turn2 = Turn(turn_index=1, final_hand=hand2)
    turn3 = Turn(turn_index=1, final_hand=hand3)

    assert turn1 < turn2
    assert turn2 > turn3

    turns = [turn2, turn1, turn3]

    # print([t.final_hand.dice for t in turns])
    turns.sort()
    # print([t.final_hand.dice for t in turns])

    assert turns[0] == turn1
    assert turns[1] == turn3
    assert turns[2] == turn2

    turn1 = Turn(turn_index=1, final_hand=hand1)
    turn2 = Turn(turn_index=2, final_hand=hand2)
    turn3 = Turn(turn_index=3, final_hand=hand3)

    turns = [turn2, turn1, turn3]

    # print([t.final_hand.dice for t in turns])
    turns.sort()
    # print([t.final_hand.dice for t in turns])

    assert turns[0] == turn1
    assert turns[1] == turn3
    assert turns[2] == turn2


def test_from_name():
    all_hand_names = Hand.get_all_possible_hands(return_names=True)
    for i, name in enumerate(all_hand_names):
        print(f"Testing hand name: {name} ({i+1}/{len(all_hand_names)})")
        hand = Hand.from_name(name)
        assert hand.to_name() == name, f"Failed for hand name: {name}"
        assert isinstance(hand, Hand), f"Failed type check for hand name: {name}"
