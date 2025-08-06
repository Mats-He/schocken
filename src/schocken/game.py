from typing import Union, List, Optional
from schocken.base import (
    HandType,
    BasePlayer,
    PlayerID,
    Round,
    MiniRound,
    Half,
)


class Game:
    """
    A class representing a game of Schocken.

    Structure:
        - The game consists of multiple rounds. A round is lost when a player collects all chips and loses both halves.
        - Each round has two halves (or three if a tiebreaker is needed).
        - Each half consists of multiple mini-rounds.
        - In each mini-round, all active players take one turn. At the end of the mini-round, chips are distributed.
        - In each turn, a player may throw up to three times.
    """

    def __init__(self):
        """
        Initialize a new Game instance with empty player, score, and round lists.
        """
        self.players: List[BasePlayer] = []
        self.scores: dict = {}
        self.rounds: List[Round] = []
        self.last_mr: Optional[MiniRound] = None

    @property
    def pids(self) -> Optional[PlayerID]:
        """
        Return a list of all player IDs currently in the game.

        Returns:
            List[PlayerID]: List of player IDs.
        """
        pids = [p.id for p in self.players] if self.players else []
        return pids

    def add_player(self, player: Union[BasePlayer, List[BasePlayer]]):
        """
        Add a player or a list of players to the game.

        Args:
            player (BasePlayer or List[BasePlayer]): The player(s) to add.

        Raises:
            ValueError: If player is empty or already exists.
            TypeError: If input is not a BasePlayer or list of BasePlayers.
        """
        if not player:
            raise ValueError("player cannot be empty.")
        if isinstance(player, BasePlayer):
            if player.id in self.pids:
                raise ValueError(f"Player with id={player.id} already exists.")

            max_pid = int(max(self.pids)) if self.players else -1
            player._id = PlayerID(max_pid + 1)
            self.players.append(player)
        elif isinstance(player, List) and all(
            isinstance(p, BasePlayer) for p in self.players
        ):
            for p in player:
                self.add_player(p)
        else:
            raise TypeError(
                "player must be an instance of BasePlayer or a List of BasePlayer instances."
            )
        assert len(self.players) == len(set(self.pids)), "Player IDs are not unique."
        self.scores["rounds_lost"] = {p.id: 0 for p in self.players}

    def get_player_by_id(self, pid: PlayerID) -> BasePlayer:
        """
        Retrieve a player object by their PlayerID.

        Args:
            pid (PlayerID): The ID of the player to retrieve.

        Returns:
            BasePlayer: The player with the given ID.

        Raises:
            ValueError: If no player with the given ID exists.
        """
        for player in self.players:
            if player.id == pid:
                return player
        raise ValueError(f"No player found with id={pid}")

    def _calculate_scores(self, condensed_hands: bool = True):
        """
        Calculate and update the scores for all players based on rounds, halves, and mini-rounds lost.
        Updates the self.scores dictionary with the latest statistics.

        Args:
            condensed_hands (bool): If True, condense hands into histogram instead of list.
        """
        all_rounds_lost = {pid: 0 for pid in self.pids}
        all_halves_lost = {pid: 0 for pid in self.pids}
        all_minirounds_lost = {pid: 0 for pid in self.pids}
        all_players_hands = {pid: [] for pid in self.pids}

        for r in self.rounds:
            all_rounds_lost[r.lost_by] += 1
            for h in r.halves:
                all_halves_lost[h.lost_by] += 1
                for mr in h.mini_rounds:
                    all_minirounds_lost[mr.lost_by] += 1
                    for t in mr.turns:
                        all_players_hands[t.player_id].append(t.final_hand.to_name())
        if condensed_hands:
            # condense hands into histogram
            for pid, hands in all_players_hands.items():
                hand_histogram = {}
                for hand in hands:
                    if hand not in hand_histogram:
                        hand_histogram[hand] = 0
                    hand_histogram[hand] += 1
                all_players_hands[pid] = hand_histogram
        score_register = {
            "rounds_lost": all_rounds_lost,
            "halves_lost": all_halves_lost,
            "minirounds_lost": all_minirounds_lost,
            "hands_played": all_players_hands,
        }
        self.scores = score_register.copy()

    def get_scores(self):
        """
        Get the current scores for all players, including rounds, halves, and mini-rounds lost, and hands played.

        Returns:
            dict: A dictionary of score categories mapped to player names (and IDs if needed).
        """
        self._calculate_scores()
        scores = self.scores.copy()
        for score, score_dict in scores.items():
            if isinstance(score_dict, dict):
                pids = [pid for pid in score_dict.keys()]
                names = [self.get_player_by_id(pid).name for pid in pids]
                if len(pids) == len(set(names)):  # only unique names
                    scores[score] = {
                        names[i]: score_dict[pids[i]] for i in range(len(pids))
                    }
                else:  # duplicate names exist -> include ids as well
                    scores[score] = {
                        names[i] + f"({int(pids[i])})": score_dict[pids[i]]
                        for i in range(len(pids))
                    }
            else:
                raise ValueError(f"score type not supported... ({type(score_dict)})")
        return scores

    def to_json(self):
        """Convert the game state to a JSON-serializable dictionary."""
        return {
            "players": [f"{p.name} ({p.id})" for p in self.players],
            "scores": self.get_scores(),
            "rounds": [r.to_json() for r in self.rounds],
            "last_mr": self.last_mr.to_json() if self.last_mr else None,
        }

    def play_mini_round(
        self,
        mini_round_players: Optional[List[BasePlayer]] = None,
        mini_round_index: int = 0,
    ) -> MiniRound:
        """
        Play a single mini-round with the given players.
        Each player takes one turn, and the results are recorded.

        Args:
            mini_round_players (List[BasePlayer], optional): The players participating in the mini-round.
            mini_round_index (int, optional): The index of the mini-round within the half.

        Returns:
            MiniRound: The completed MiniRound object with results.

        Raises:
            ValueError: If the number of players is not within the allowed range.
        """
        if not mini_round_players:
            mini_round_players = self.players.copy()

        mr = MiniRound(
            mini_round_players=mini_round_players, mini_round_index=mini_round_index
        )
        if len(mr.mini_round_players) < 2 or len(mr.mini_round_players) > 50:
            raise ValueError(
                f"Too little or too many players to play round ({len(mr.mini_round_players)})."
            )
        max_throws = 3
        for i, player in enumerate(mr.mini_round_players):
            turn = player.play_turn(max_throws=max_throws, turn_index=i, game=self)
            if i == 0:
                max_throws = turn.num_throws  # use max throws of first player
            turn.final_hand.players_turn_ind = i
            mr.turns.append(turn)

        # determine winner, loser and chips
        mr.turns.sort()
        mr.worst_turn = mr.turns[0]
        mr.best_turn = mr.turns[-1]
        mr.given_chips = mr.best_turn.final_hand.get_chip_count()
        mr.lost_by = mr.worst_turn.player_id

        return mr

    def play_half(
        self,
        halves_index=0,
        players: Union[List[BasePlayer], None] = None,
        print_info: bool = False,
    ) -> Half:
        """
        Play a half of the game, consisting of multiple mini-rounds.
        Handles chip distribution, player elimination, and determines the loser of the half.

        Args:
            halves_index (int): The index of the half (0, 1, or 2 for tiebreaker).
            players (List[BasePlayer], optional): The players participating in this half. If None, all players are included.
            print_info (bool): Whether to print detailed information about the half.

        Returns:
            Half: The completed Half object with all mini-rounds and results.

        Raises:
            ValueError: If player selection or chip distribution is invalid.
        """

        def _change_starting_player(
            active_players: List[BasePlayer], pid_of_starter: int
        ) -> List[BasePlayer]:
            """
            Shift the order of active players so that the player with the given ID starts. Initial sequence of players in maintained.

            Args:
                active_players (List[BasePlayer]): The current list of active players.
                pid_of_starter (int): The ID of the player who should start.

            Returns:
                List[BasePlayer]: The reordered list of players.

            Raises:
                ValueError: If the starting player is not in the list.
            """
            # get all active player in initial order
            active_players_og_order = [
                p for p in self.players.copy() if p in active_players
            ]
            # find index in player list of starter
            pids = [p.id for p in active_players_og_order]
            if pid_of_starter in pids:
                n = pids.index(pid_of_starter)
            else:
                raise ValueError("Player who should start is not playing...")

            players = active_players_og_order
            # shifting players inside list while maintaining initial ordering
            players = players[n:] + players[:n]
            return players

        if print_info:
            print(f"\tPlaying half {halves_index}")

        half = Half(halves_index=halves_index)
        mini_round_index = 0
        is_regular_half = False if halves_index == 2 else True

        # If it's final (third) half, not all players take part
        if (
            players
            and isinstance(players, List)
            and all(isinstance(p, BasePlayer) for p in self.players)
        ):
            half.active_players = players
            if is_regular_half:
                raise Warning(
                    "Regular half (no final) is played with specific players, potentially not all."
                )
        elif is_regular_half:
            # Normal half, no special player selection
            half.active_players = self.players.copy()
        else:
            # halves_index is 2 (final half), but no players were submitted
            raise ValueError(
                "Please either choose halves index of 0 or 1 OR provide a list of players for the final half."
            )

        half.chip_manager.chip_balances = {p.id: 0 for p in half.active_players}

        while half.lost_by == None and mini_round_index < 1000:
            # shifting players turns such that loser of last round starts
            if self.last_mr and is_regular_half:
                half.active_players = _change_starting_player(
                    half.active_players, self.last_mr.lost_by
                )

            mr = self.play_mini_round(half.active_players, mini_round_index)

            # end half if schock out occurs
            if mr.best_turn.final_hand.hand_type == HandType("Schock-out"):
                half.lost_by = mr.lost_by
                half.mini_rounds.append(mr)
                self.last_mr = mr
                mini_round_index += 1
                if print_info:
                    print(
                        f"\t\tSchock out! by {self.get_player_by_id(mr.best_turn.player_id).name}."
                    )
                break

            # distribute chips to loser
            if not half.stock_chips_gone:
                half.chip_manager.chips_in_stock -= mr.given_chips
                if half.chip_manager.chips_in_stock <= 0:
                    mr.given_chips -= abs(half.chip_manager.chips_in_stock)
                    half.chip_manager.chips_in_stock = 0
                    half.stock_chips_gone = True

            elif half.stock_chips_gone:
                mr.given_chips = min(
                    mr.given_chips,
                    half.chip_manager.chip_balances[mr.best_turn.player_id],
                )
                half.chip_manager.chip_balances[
                    mr.best_turn.player_id
                ] -= mr.given_chips

            # hand out chips to loser of mini round
            half.chip_manager.chip_balances[mr.lost_by] += mr.given_chips

            if half.stock_chips_gone:
                # check if player is out
                for p in mr.mini_round_players:
                    chips = half.chip_manager.chip_balances[p.id]
                    if chips == 0:
                        half.active_players.remove(p)

            # Add mini round to half
            half.mini_rounds.append(mr)
            self.last_mr = mr

            # Determine if a player has lost
            for pid, chips in half.chip_manager.chip_balances.items():
                if chips == 13:
                    half.lost_by = pid
                    if print_info:
                        print("\t\tHalf ended regularly")
                elif chips > 13 or chips < 0:
                    raise ValueError(
                        f"Player {pid} has {chips}, which should not be possible."
                    )

            mini_round_index += 1

        if print_info:
            print(
                f"\t\t-> Half ended after {mini_round_index} rounds. {self.get_player_by_id(half.lost_by).name} lost."
            )
        return half

    def play_round(self, round_index=0, print_info: bool = False):
        """
        Play a full round of the game, consisting of two (or three) halves.
        Determines the overall round loser and updates the game state.

        Args:
            round_index (int): The index of the round.
            print_info (bool): Whether to print detailed information about the round.

        Returns:
            Round: The completed Round object with all halves and results.

        Raises:
            ValueError: If the round logic fails or player selection is invalid.
        """
        if print_info:
            print(f"Playing round {round_index}")

        r = Round(round_index)
        halves_lost_by = []

        for halves_index in range(2):
            half = self.play_half(halves_index, print_info=print_info)
            r.halves.append(half)
            halves_lost_by.append(half.lost_by)

        assert len(halves_lost_by) == 2, "Not exactly two rounds were played."

        if len(set(halves_lost_by)) == 1:
            # player lost both rounds, so they lost entire round
            r.lost_by = halves_lost_by[0]
            if print_info:
                print(f"Round lost clean by {self.get_player_by_id(r.lost_by).name}\n")
        elif len(set(halves_lost_by)) == 2:
            # play third half
            # assemble final players in the order [lost_first_half, lost_second_half], such that the loser of the first round starts the final
            final_players = [
                next(p for p in self.players if p.id == pid) for pid in halves_lost_by
            ]
            half = self.play_half(2, players=final_players)
            r.halves.append(half)
            r.lost_by = half.lost_by
            if print_info:
                print(
                    f"-> Final between {' and '.join([self.get_player_by_id(h).name for h in halves_lost_by])} lost by {self.get_player_by_id(r.lost_by).name}.\n"
                )
        else:
            raise ValueError(f"How tf did we get here?! {halves_lost_by}")

        self.rounds.append(r)

        return r

    def play_rounds(
        self,
        num_rounds: int,
        print_info: bool = False,
    ) -> List[Round]:
        """Play a specified number of rounds in the game.

        Args:
            num_rounds (int): The number of rounds to play.
            print_info (bool): Whether to print detailed information about each round.

        Returns:
            List[Round]: A list of Round objects representing the played rounds.
        """
        rounds = []
        for i in range(num_rounds):
            r = self.play_round(round_index=i, print_info=print_info)
            rounds.append(r)
        return rounds
