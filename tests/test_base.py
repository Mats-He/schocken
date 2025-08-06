import pytest
from schocken.base import (
    Die,
    HandType,
    Hand,
    BasePlayer,
    PlayerID,
    ChipManager,
    Turn,
    MiniRound,
    Half,
    Round,
)


class DummyPlayer(BasePlayer):
    def eval_hand_and_throw(self, current_hand, *args, **kwargs):
        # Always end turn, return current hand
        return True, current_hand


def test_die_init_valid():
    d = Die(3)
    assert d.value == 3
    assert not d.visible
    assert not d.taken_out


def test_die_init_invalid():
    with pytest.raises(ValueError):
        Die(0)
    with pytest.raises(ValueError):
        Die(7)


def test_die_make_a_one():
    d = Die(5)
    d.make_a_one()
    assert d.value == 1
    assert d.taken_out
    assert d.visible


def test_die_throw():
    d = Die(2)
    d.throw()
    assert 1 <= d.value <= 6
    assert not d.taken_out
    assert not d.visible


def test_handtype_validation():
    with pytest.raises(ValueError):
        HandType("")
    with pytest.raises(ValueError):
        HandType("InvalidType")
    with pytest.raises(ValueError):
        HandType("Schock", 0)
    with pytest.raises(ValueError):
        HandType("Schock", 1)
    with pytest.raises(ValueError):
        HandType("General", 7)
    with pytest.raises(ValueError):
        HandType("Straight", 0)
    with pytest.raises(ValueError):
        HandType("High Dice", 220)
    with pytest.raises(ValueError):
        HandType("High Dice", 666)


def test_handtype_properties():
    ht = HandType("Schock-out")
    assert ht.chips == 13
    assert ht.internal_rank == 5000
    ht = HandType("Schock", 4)
    assert ht.chips == 4
    assert ht.internal_rank == 4004
    ht = HandType("General", 5)
    assert ht.chips == 3
    assert ht.internal_rank == 3005
    ht = HandType("Straight", 2)
    assert ht.chips == 2
    assert ht.internal_rank == 2002
    ht = HandType("High Dice", 321)
    assert ht.chips == 1
    assert ht.internal_rank == 1321
    with pytest.raises(ValueError):
        ht.chips = 5
    with pytest.raises(ValueError):
        ht.internal_rank = 1234


def test_handtype_comparison():
    h1 = HandType("Schock", 6)
    h2 = HandType("General", 6)
    h3 = HandType("High Dice", 665)
    assert h1 > h2
    assert h2 > h3
    assert h1 != h3
    assert h1 == HandType("Schock", 6)


def test_hand_init_and_update():
    dice = [Die(1), Die(1), Die(1)]
    h = Hand(dice)
    h.update()
    assert h.hand_type.hand_type == "Schock-out"
    dice = [Die(1), Die(1), Die(5)]
    h = Hand(dice)
    h.update()
    assert h.hand_type.hand_type == "Schock"
    assert h.hand_type.hand_type_value == 5
    dice = [Die(4), Die(4), Die(4)]
    h = Hand(dice)
    h.update()
    assert h.hand_type.hand_type == "General"
    assert h.hand_type.hand_type_value == 4
    dice = [Die(2), Die(3), Die(4)]
    h = Hand(dice)
    h.update()
    assert h.hand_type.hand_type == "Straight"
    assert h.hand_type.hand_type_value == 2
    dice = [Die(6), Die(5), Die(2)]
    h = Hand(dice)
    h.update()
    assert h.hand_type.hand_type == "High Dice"
    assert h.hand_type.hand_type_value == 652


def test_hand_to_name():
    dice = [Die(1), Die(1), Die(1)]
    h = Hand(dice)
    h.update()
    assert h.to_name() == "Schock-out"
    dice = [Die(1), Die(1), Die(3)]
    h = Hand(dice)
    h.update()
    assert h.to_name() == "Schock-3"
    dice = [Die(2), Die(2), Die(2)]
    h = Hand(dice)
    h.update()
    assert h.to_name() == "General-2"
    dice = [Die(3), Die(4), Die(5)]
    h = Hand(dice)
    h.update()
    assert h.to_name() == "Straight-3:5"
    dice = [Die(2), Die(2), Die(1)]
    h = Hand(dice)
    h.update()
    assert h.to_name() == "Motte"
    dice = [Die(6), Die(5), Die(2)]
    h = Hand(dice)
    h.update()
    assert h.to_name() == "65-2"


def test_hand_sort_and_clear():
    dice = [Die(2), Die(6), Die(4)]
    h = Hand(dice)
    h.sort()
    assert [d.value for d in h.dice] == [6, 4, 2]
    h.clear()
    assert h.dice == []


def test_hand_copy():
    dice = [Die(3), Die(3), Die(3)]
    h = Hand(dice)
    h.update()
    h2 = h.copy()
    assert h2.dice[0].value == 3
    assert h2.hand_type.hand_type == "General"
    assert h2.hand_type.hand_type_value == 3
    assert h2.put_together == h.put_together
    assert h2.players_turn_ind == h.players_turn_ind
    assert h2.finalized == h.finalized


def test_hand_finalize():
    dice = [Die(1), Die(1), Die(2)]
    h = Hand(dice)
    h.dice[1].make_a_one()
    h.finalize()
    assert all(d.visible for d in h.dice)
    assert h.finalized
    assert h.put_together
    dice = [Die(1), Die(1), Die(2)]
    h = Hand(dice)
    h.finalize()
    assert all(d.visible for d in h.dice)
    assert h.finalized
    assert not h.put_together


def test_hand_get_chip_count():
    dice = [Die(1), Die(1), Die(2)]
    h = Hand(dice)
    h.update()
    assert h.get_chip_count() == 2
    h.clear()
    with pytest.raises(ValueError):
        h.get_chip_count()


def test_hand_from_str():
    h = Hand.from_str("[4, 4, 4]")
    assert [d.value for d in h.dice] == [4, 4, 4]
    assert h.hand_type.hand_type == "General"
    with pytest.raises(ValueError):
        Hand.from_str("[1, 2]")


def test_player_id():
    pid = PlayerID(5)
    assert int(pid) == 5
    assert repr(pid) == "PID(5)"


def test_baseplayer_play_turn():
    p = DummyPlayer("TestPlayer")
    hand = p.play_turn()
    assert isinstance(hand, Hand)
    assert hand.finalized
    assert all(d.visible for d in hand.dice)


def test_baseplayer_throw_new_hand():
    dice = [Die(1), Die(6), Die(3)]
    h = Hand(dice)
    new_hand = BasePlayer._throw_new_hand(
        h, should_take_out_ones=True, should_convert_sixes=True
    )
    assert isinstance(new_hand, Hand)
    assert len(new_hand.dice) == 3


def test_baseplayer_take_out_ones():
    dice = [Die(1), Die(2), Die(3)]
    h = Hand(dice)
    dice_processed = []
    h2, processed = BasePlayer.take_out_ones(h, dice_processed)
    assert processed[0].value == 1
    assert processed[0].taken_out


def test_baseplayer_convert_sixes():
    dice = [Die(6), Die(6), Die(2)]
    h = Hand(dice)
    dice_processed = []
    h2, processed = BasePlayer.convert_sixes(h, dice_processed)
    assert any(d.value == 1 for d in processed)


def test_chipmanager():
    cm = ChipManager()
    assert cm.chips_in_stock == 13
    assert isinstance(cm.chip_balances, dict)


def test_turn():
    t = Turn(1, PlayerID(2), None)
    assert t.turn_index == 1
    assert t.player_id == PlayerID(2)
    assert t.final_hand is None


def test_mini_round():
    p1 = DummyPlayer("A")
    p2 = DummyPlayer("B")
    mr = MiniRound([p1, p2], 1)
    assert mr.mini_round_index == 1
    assert mr.mini_round_players == [p1, p2]
    assert mr.turns == []
    assert mr.given_chips == 0


def test_half():
    p1 = DummyPlayer("A")
    h = Half(1, [p1])
    assert h.halves_index == 1
    assert h.active_players == [p1]
    assert isinstance(h.chip_manager, ChipManager)


def test_round():
    r = Round(1)
    assert r.round_index == 1
    assert r.halves == []
