import pytest
from schocken.game import Game
from schocken.base import BasePlayer, PlayerID


class DummyPlayer(BasePlayer):
    def eval_hand_and_throw(self, current_hand, *args, **kwargs):
        # Always end turn, return current hand
        return True, current_hand


def test_game_init():
    g = Game()
    assert g.players == []
    assert isinstance(g.scores, dict)
    assert g.rounds == []
    assert g.last_mr is None


def test_game_add_player():
    g = Game()
    p1 = DummyPlayer("A")
    g.add_player(p1)
    assert len(g.players) == 1
    assert p1.id == PlayerID(0)
    p2 = DummyPlayer("B")
    g.add_player(p2)
    assert p2.id == PlayerID(1)
    with pytest.raises(ValueError):
        g.add_player(p1)  # Duplicate
    # Add multiple players
    p3 = DummyPlayer("C")
    p4 = DummyPlayer("D")
    g.add_player([p3, p4])
    assert p3.id == PlayerID(2)
    assert p4.id == PlayerID(3)
    assert len(g.players) == 4
    # Type error
    with pytest.raises(TypeError):
        g.add_player("not a player")


def test_game_get_player_by_id():
    g = Game()
    p1 = DummyPlayer("A")
    g.add_player(p1)
    assert g.get_player_by_id(p1.id) == p1
    with pytest.raises(ValueError):
        g.get_player_by_id(PlayerID(99))


def test_game_pids():
    g = Game()
    p1 = DummyPlayer("A")
    p2 = DummyPlayer("B")
    g.add_player([p1, p2])
    assert g.pids == [p1.id, p2.id]


def test_game_play_mini_round():
    g = Game()
    p1 = DummyPlayer("A")
    p2 = DummyPlayer("B")
    g.add_player([p1, p2])
    mr = g.play_mini_round([p1, p2], 0)
    assert mr.mini_round_index == 0
    assert len(mr.turns) == 2
    assert mr.worst_turn is not None
    assert mr.best_turn is not None
    assert mr.lost_by in [p1.id, p2.id]
    assert mr.given_chips >= 1


def test_game_play_half():
    g = Game()
    p1 = DummyPlayer("A")
    p2 = DummyPlayer("B")
    g.add_player([p1, p2])
    half = g.play_half(0)
    assert half.halves_index == 0
    assert half.lost_by in [p1.id, p2.id]
    assert len(half.mini_rounds) >= 1
    assert isinstance(half.chip_manager.chip_balances, dict)


def test_game_play_round():
    g = Game()
    p1 = DummyPlayer("A")
    p2 = DummyPlayer("B")
    g.add_player([p1, p2])
    r = g.play_round(0)
    assert r.round_index == 0
    assert r.lost_by in [p1.id, p2.id]
    assert len(r.halves) >= 2
    assert g.rounds[-1] == r


def test_game_get_scores():
    g = Game()
    p1 = DummyPlayer("A")
    p2 = DummyPlayer("B")
    g.add_player([p1, p2])
    g.play_round(0)
    scores = g.get_scores()
    assert "rounds_lost" in scores
    assert "halves_lost" in scores
    assert "minirounds_lost" in scores
    assert "hands_played" in scores
    for k in ["rounds_lost", "halves_lost", "minirounds_lost"]:
        assert p1.name in scores[k] or f"{p1.name}(0)" in scores[k]
        assert p2.name in scores[k] or f"{p2.name}(1)" in scores[k]
