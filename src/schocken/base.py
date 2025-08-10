import random
from dataclasses import dataclass, field
from functools import total_ordering
from typing import List, Optional, Tuple, Union
from abc import ABC, abstractmethod
from itertools import combinations_with_replacement


@dataclass
class Die:
    value: int = field(default_factory=lambda: random.randint(1, 6))
    visible: bool = False
    taken_out: bool = False

    def __repr__(self):
        """
        Return a string representation of the Die object, showing its current value.
        Useful for debugging and display purposes.
        """
        return f"Die({self.value})"

    def __post_init__(self):
        """
        Validate the die value after initialization.
        Ensures the die value is within the valid range (1-6) or is -1 (special case for game logic).
        """
        if not (1 <= self.value <= 6) and not self.value == -1:
            raise ValueError("Die value must be between 1 and 6 or -1")

    def make_a_one(self):
        """
        Set the die value to one, mark it as taken out, and make it visible.
        This simulates the action of putting the die out in the game, typically when a player rolls a one.
        """
        self.value = 1
        self.taken_out = True
        self.visible = True

    def throw(self):
        """
        Roll the die to get a new random value between 1 and 6.
        Resets the 'taken_out' and 'visible' flags to False, simulating a fresh roll.
        """
        self.value = random.randint(1, 6)
        self.taken_out = False
        self.visible = False

    def copy(self) -> "Die":
        """
        Creates a copy of the die with the same value, visibility, and taken_out state.

        Returns:
            Die: A new Die object with the same attributes as the original.
        """
        return Die(value=self.value, visible=self.visible, taken_out=self.taken_out)


@dataclass
@total_ordering
class HandType:
    hand_type: str = ""
    hand_type_value: int = field(default=0, repr=False)
    _internal_rank: int = field(init=False, repr=False, default=0)
    _chips: int = field(init=False, repr=False)

    def __post_init__(self):
        """
        Validate and initialize the HandType instance.
        Ensures the hand_type and hand_type_value are consistent with game rules.
        Raises:
            ValueError: If the hand_type or hand_type_value is invalid for the given type.
        """
        if self.hand_type == "":
            raise ValueError("Hand type cannot be empty")
        # Validation Logic
        if self.hand_type not in [
            "Schock-out",
            "Schock",
            "General",
            "Straight",
            "High Dice",
        ]:
            raise ValueError(
                'hand_type must be one of ["Schock-out", "Schock", "General", "Straight", "High Dice"]'
            )
        elif (
            self.hand_type in ["Schock", "General", "Straight", "High Dice"]
            and self.hand_type_value == 0
        ):
            raise ValueError(
                "hand_type_value cannot be empty for Schock, General, Straight, High Dice."
            )
        elif self.hand_type == "Schock" and (
            self.hand_type_value < 2 or self.hand_type_value > 6
        ):
            raise ValueError("hand_type_value must be between 2 and 6 for Schock")
        elif self.hand_type == "General" and (
            self.hand_type_value < 2 or self.hand_type_value > 6
        ):
            raise ValueError("hand_type_value must be between 2 and 6 for General")
        elif self.hand_type == "Straight" and (
            self.hand_type_value < 1 or self.hand_type_value > 4
        ):
            raise ValueError("hand_type_value must be between 1 and 4 for Straight")
        elif self.hand_type == "High Dice" and (
            self.hand_type_value < 221 or self.hand_type_value > 665
        ):
            raise ValueError(
                f"hand_type_value must be between 221 and 665 for High Dice: {self.hand_type_value}"
            )

    def __str__(self):
        return self.hand_type

    def __eq__(self, other):
        if not isinstance(other, HandType):
            return NotImplementedError
        return self.internal_rank == other.internal_rank

    def __lt__(self, other):
        if not isinstance(other, HandType):
            return NotImplementedError
        return self.internal_rank < other.internal_rank

    @property
    def chips(self):
        if self.hand_type == "Schock-out":
            self._chips = 13
        elif self.hand_type == "Schock":
            self._chips = self.hand_type_value
        elif self.hand_type == "General":
            self._chips = 3
        elif self.hand_type == "Straight":
            self._chips = 2
        elif self.hand_type == "High Dice":
            self._chips = 1
        else:
            raise ValueError(
                "Invalid hand type. Chips can only be calculated for Schock, General, Straight, or High Dice"
            )
        return self._chips

    @chips.setter
    def chips(self, value):
        raise ValueError("Chips attribute should't be set. It's meant to be read-only")

    @property
    def internal_rank(self) -> int:
        if self.hand_type == "Schock-out":
            self._internal_rank = 5000
        elif self.hand_type == "Schock":
            self._internal_rank = 4000 + self.hand_type_value
        elif self.hand_type == "General":
            self._internal_rank = 3000 + self.hand_type_value
        elif self.hand_type == "Straight":
            self._internal_rank = 2000 + self.hand_type_value
        elif self.hand_type == "High Dice":
            self._internal_rank = 1000 + self.hand_type_value
        else:
            raise ValueError(
                "Invalid hand type. Internal rank can only be calculated for Schock-out, Schock, General, Straight, or High Dice"
            )
        return self._internal_rank

    @internal_rank.setter
    def internal_rank(self, value: int):
        raise ValueError(
            "internal rank attribute should't be set. It's meant to be read-only"
        )


@dataclass
@total_ordering
class Hand:
    _dice: List[Die] = field(default_factory=list)
    _hand_type: Optional[HandType] = field(default=None, init=False, repr=False)
    put_together: bool = False
    players_turn_ind: int = 0  # idx of players turn in a game, e.g. 2 (2nd player)
    finalized: bool = False

    def __post_init__(self):
        """
        Initialize the Hand instance and update its state based on the current dice.
        """
        self.update()

    def __eq__(self, other):
        if not isinstance(other, Hand):
            return NotImplementedError
        if (
            self.players_turn_ind == other.players_turn_ind
        ):  # can only ever be true if both hands have no players turn index
            return self.hand_type == other.hand_type
        else:  # if both hands have a players turn index, i.e. scenario in a game, hands can never be equal
            return False

    def __lt__(self, other):
        if not isinstance(other, Hand):
            return NotImplementedError
        if self.hand_type == other.hand_type:
            return (
                self.players_turn_ind > other.players_turn_ind
            )  # higher index means worse hand -> invert comparison
        else:
            return self.hand_type < other.hand_type

    def __str__(self):
        return self.to_name()

    def __repr__(self):
        return (
            f"Hand(dice={self.dice}, "
            f"hand_type={self.hand_type}, "
            f"players_turn_ind={self.players_turn_ind}, "
            f"put_together={self.put_together}, "
            f"finalized={self.finalized})"
        )

    @property
    def dice(self) -> List[Die]:
        return self._dice

    @dice.setter
    def dice(self, value: List[Die]):
        if isinstance(value, list):
            if not all(isinstance(die, Die) for die in value):
                raise TypeError("All items must be of type Die")
            self._dice = value
            self.update()
        else:
            raise ValueError("Dice must be a list of 'Die'")

    @property
    def hand_type(self) -> HandType:
        if self._hand_type is None:
            return HandType()  # Return a default HandType if not set
        return self._hand_type

    @hand_type.setter
    def hand_type(self, value):
        raise ValueError(
            "hand_type attribute should't be set directly. It is calculated based on the dice in the hand"
        )

    @staticmethod
    def get_all_possible_hands(
        return_names: bool = False,
    ) -> Union[List["Hand"], List[str]]:
        """
        Returns all possible unique hands sorted by rank (worst to best).
        Useful for generating all hand types for game logic, testing, or statistics.

        Args:
            return_names (bool): Whether to return names of the hands instead of the hand themselves. Defaults to False

        Returns:
            Union[List[Hand], List[str]]: All unique hand combinations possible in the game as Hand objects or names.
        """
        possible_hands: List[Hand] = []
        # All combinations of 3 dice values (1-6), order doesn't matter
        for combo in combinations_with_replacement(range(1, 7), 3):
            # Generate all unique permutations for this combo (to cover all dice orders)
            dice = [Die(value=v) for v in sorted(combo, reverse=True)]
            hand = Hand()
            hand.dice = dice
            hand.update()
            # Create a copy of the hand for the put_together variant
            hand2 = hand.copy()
            hand2.put_together = True
            hand2.update()
            # Avoid duplicates by hand type and dice values
            if not any(
                h.hand_type.internal_rank == hand.hand_type.internal_rank
                for h in possible_hands
            ):
                possible_hands.append(hand)
            if not any(
                h.hand_type.internal_rank == hand2.hand_type.internal_rank
                for h in possible_hands
            ):
                possible_hands.append(hand2)

        possible_hands.sort()
        if return_names:
            possible_hands = [hand.to_name() for hand in possible_hands]

        return possible_hands

    def to_name(self) -> str:
        """
        Return a human-readable name for the hand, based on its type and value.

        Returns:
            str: The descriptive name of the hand (e.g., 'Schock-5', 'General-4', 'Straight-2:4', 'Motte').
        """
        name = "not defined"
        if self.hand_type.hand_type == "Schock-out":
            name = "Schock-out"
        elif self.hand_type.hand_type == "Schock":
            name = "Schock-" + str(self.hand_type.hand_type_value)
        elif self.hand_type.hand_type == "General":
            name = "General-" + str(self.hand_type.hand_type_value)
        elif self.hand_type.hand_type == "Straight":
            val = self.hand_type.hand_type_value
            name = "Straight-" + str(val) + ":" + str(val + 2)
        elif self.hand_type.hand_type == "High Dice":
            val = str(self.hand_type.hand_type_value)
            name = f"{val[:2]}-{val[2]}"
            if val == "221":
                name = "Motte"
        return name

    @classmethod
    def from_name(cls, name: str) -> "Hand":
        """
        Create a Hand instance from a name string.

        Args:
            name (str): The name of the hand (e.g., 'Schock-5', 'General-4', 'Straight-2:4').

        Returns:
            Hand: The constructed Hand object.
        """
        hand = cls()
        if name == "Motte":
            hand.dice = [Die(1), Die(2), Die(2)]
        elif "Schock-out" in name:
            hand.dice = [Die(1), Die(1), Die(1)]
        elif "Schock-" in name:
            value = int(name.split("-")[1])
            hand.dice = [Die(1), Die(1), Die(value)]
        elif "General-" in name:
            value = int(name.split("-")[1])
            hand.dice = [Die(value), Die(value), Die(value)]
        elif "Straight-" in name:
            parts = name.split("-")[1].split(":")
            value = int(parts[0])
            hand.dice = [Die(value), Die(value + 1), Die(value + 2)]
        elif "-" in name:
            values = "".join(name.split("-"))
            assert len(values) == 3, f"Invalid hand name format: {name}"
            hand.dice = [Die(int(v)) for v in values]
            if "1" in values:
                hand.put_together = True
        else:
            raise ValueError(f"Unknown hand type: {name}")

        hand.update()
        return hand

    def initialize(self):
        """
        Initialize the hand with three new dice and reset its state.
        Resets 'put_together' and 'finalized' flags, and updates the hand type.
        """
        self.dice = [Die() for _ in range(3)]
        self.put_together = False
        self.finalized = False
        self.update()

    def get_visible_dice(self) -> Union[List[Die], None]:
        """
        Get a list of visible dice in the hand.
        None is returned when player hasnt played yet, i.e. hand is not finalized.
        An empty list is returned if the hand has no visible dice. ("3 Dunkel")

        Returns:
            Union[List[Die], None]: A list of visible dice if the hand is finalized, otherwise None.
        """
        if not self.finalized:
            return None
        else:
            visible_dice = [die for die in self.dice if die.visible]
        return visible_dice

    def copy(self) -> "Hand":
        """
        Creates a deep copy of the hand, including dice values and state flags.

        Returns:
            Hand: A new Hand object with the same dice and state as the original.
        """
        new_hand = Hand()
        new_hand.dice = [die.copy() for die in self._dice]
        new_hand.put_together = self.put_together
        new_hand.players_turn_ind = self.players_turn_ind
        new_hand.finalized = self.finalized
        new_hand._hand_type = self._hand_type  # Copy the hand type
        new_hand.update()  # Ensure the new hand is updated
        return new_hand

    def sort(self):
        """
        Sort the dice in descending order by value.
        This helps with hand type determination and comparison.
        """
        self._dice.sort(key=lambda die: die.value, reverse=True)

    def clear(self):
        """
        Remove all dice from the hand, resetting it to an empty state.
        """
        self._dice.clear()

    def update(self):
        """
        Updates the hand by sorting the dice and determining the hand type.
        Also sets 'put_together' if any die was taken out.
        """
        self.sort()
        if any(die.taken_out for die in self.dice):
            # mark hand as put together, if any die was taken_out
            self.put_together = True
        self.detemine_hand_type()

    def get_chip_count(self) -> int:
        """
        Get the number of chips associated with this hand, based on its type.

        Returns:
            int: The chip count for the hand.

        Raises:
            ValueError: If the hand does not contain exactly 3 dice.
        """
        if len(self._dice) != 3:
            raise ValueError("Hand must contain exactly 3 dice to count chips")
        if self.hand_type is None or not isinstance(self.hand_type, HandType):
            return 0
        return self.hand_type.chips

    def detemine_hand_type(self):
        """
        Determines the type of hand based on the current dice values.
        Sets the hand_type attribute to the appropriate HandType instance.
        Handles all game-specific hand types: Schock-out, Schock, General, Straight, and High Dice.
        """
        if len(self._dice) != 3:
            return None

        hand_type = None

        # detect schock
        ones_count = sum(1 for die in self._dice if die.value == 1)
        if ones_count == 3:
            # Schock out
            hand_type = HandType(hand_type="Schock-out")
        elif ones_count == 2:
            die_list = [die for die in self._dice if die.value != 1]
            assert (
                len(die_list) == 1
            ), f"Schock detected, but Hand doesnt match: {self._dice}"
            schock_value = die_list[0].value
            hand_type = HandType(hand_type="Schock", hand_type_value=schock_value)

        # detect general
        elif len(set(die.value for die in self._dice)) == 1:
            general_value = self._dice[0].value
            hand_type = HandType(hand_type="General", hand_type_value=general_value)

        # detect straight + high dice
        elif len(set(die.value for die in self._dice)) == 3:
            # detect straight
            sorted_values = sorted(die.value for die in self._dice)
            if sorted_values == [1, 2, 3] and not self.put_together:
                hand_type = HandType(hand_type="Straight", hand_type_value=1)
            elif sorted_values == [2, 3, 4]:
                hand_type = HandType(hand_type="Straight", hand_type_value=2)
            elif sorted_values == [3, 4, 5]:
                hand_type = HandType(hand_type="Straight", hand_type_value=3)
            elif sorted_values == [4, 5, 6]:
                hand_type = HandType(hand_type="Straight", hand_type_value=4)
            else:
                # detect high dice
                self.sort()
                hand_type = HandType(
                    hand_type="High Dice",
                    hand_type_value=100 * self._dice[0].value
                    + 10 * self._dice[1].value
                    + self._dice[2].value,
                )
        else:
            # detect high dice
            self.sort()
            hand_type = HandType(
                hand_type="High Dice",
                hand_type_value=100 * self._dice[0].value
                + 10 * self._dice[1].value
                + self._dice[2].value,
            )
        self._hand_type = hand_type

    def finalize(self):
        """
        Finalize the hand, making all dice visible and updating the hand state.
        Sets the 'finalized' flag and ensures 'put_together' is set if any die was taken out.

        Raises:
            ValueError: If the hand does not contain exactly 3 dice.
        """
        if len(self._dice) != 3:
            raise ValueError("Hand must contain exactly 3 dice to finalize")
        self.update()
        for die in self.dice:
            if die.taken_out:
                # mark hand as put together, if any die was taken_out
                self.put_together = True
        self.finalized = True


@dataclass(frozen=True, order=True)
class PlayerID:
    _id: int = field(init=True, default=-1)

    def __repr__(self):
        return f"PID({self._id})"

    def __int__(self):
        return self._id


@dataclass(order=True)
class Turn:
    turn_index: int = field(default=0, compare=False)
    player_id: Optional[PlayerID] = field(default=None, compare=False)
    final_hand: Optional[Hand] = field(default=None, compare=True)
    num_throws: int = field(default=0, compare=False)

    def to_json(self) -> dict:
        """Convert the turn state to a JSON-serializable dictionary."""
        return {
            "turn_index": self.turn_index,
            "player_id": str(self.player_id) if self.player_id else None,
            "final_hand": self.final_hand.to_name() if self.final_hand else None,
            "num_throws": self.num_throws,
        }


class BasePlayer(ABC):
    def __init__(self, name: str):
        self.name: str = name
        self._id: Optional[PlayerID] = None
        self.hand: Hand = Hand()
        self.throw_count: int = 0

    @property
    def id(self) -> Optional[PlayerID]:
        return self._id

    @id.setter
    def id(self, value):
        raise ValueError("Player IDs should not be modified after creation.")

    def __repr__(self):
        return f"Player(id={self.id}, name='{self.name}', hand={self.hand.dice})"

    @abstractmethod
    def eval_hand_and_throw(
        self, current_hand: Hand, max_throws: int, *args, **kwargs
    ) -> Tuple[bool, Hand]:
        """Example implementation of the Player logic: Evaluating current hand and throwing again if they decide to

        Args:
            current_hand (Hand): The player's current hand to evaluate.
            max_throws (int): Maximum number of throws allowed in a turn.
            *args: Additional positional arguments (unused).
            **kwargs: Additional keyword arguments (unused). (e.g. game state)

        Returns:
            Tuple[bool, Hand]: wether to end the turn (or throw again) and if applicable, the new hand
        """
        return False, self._throw_new_hand(current_hand)

    def play_turn(
        self,
        max_throws: int = 3,
        turn_index: int = 0,
        _print_throws: bool = False,
        **kwargs,
    ) -> Turn:
        """Play a turn for the player, evaluating the current hand and potentially throwing again.

        Args:
            max_throws (int, optional): Maximum number of throws allowed in a turn. Defaults to 3.
            turn_index (int, optional): Index of players turn, i.e. first, second player to play etc.
            _print_throws (bool, optional): Whether to print the throws during the turn. Defaults to False.
            **kwargs: Additional keyword arguments (unused).

        Returns:
            Turn: The final hand after the turn and the number of throws made
        """
        self.throw_count = 1
        self.hand.initialize()
        if _print_throws:
            print(f"Player: {self.name}")

        while self.throw_count < max_throws:
            current_hand = self.hand.copy()
            if _print_throws:
                print(f"\t{self.throw_count}. throw: {current_hand.dice}")

            # Evaluate hand and throw again if needed
            end_turn, new_hand = self.eval_hand_and_throw(
                current_hand=current_hand, max_throws=max_throws, **kwargs
            )
            if end_turn:
                break

            # finish the throw/play
            self.hand = new_hand
            self.hand.update()
            self.throw_count += 1

        # Finalize the hand after all turns
        self.hand.finalize()

        return Turn(
            player_id=self.id,
            final_hand=self.hand.copy(),
            num_throws=self.throw_count,
            turn_index=turn_index,
        )

    @staticmethod
    def _throw_new_hand(
        current_hand: Hand,
        should_take_out_ones: bool = True,
        should_convert_sixes: bool = True,
        should_throw_all: bool = False,
    ) -> Hand:
        """Auxiliary method that may be used for simplicity. Processes the player's hand by taking out ones, converting sixes to ones, and throwing all remaining dice.

        Args:
            current_hand (Hand): Current hand of the player to work with.
            should_take_out_ones (bool, optional): _description_. Defaults to True.
            should_convert_sixes (bool, optional): _description_. Defaults to True.
            should_throw_all (bool, optional): Determines whether to throw all 3 dice again. Overwrites all other options. Defaults to False.

        Returns:
            Hand: The updated hand after processing.
        """
        if any([should_convert_sixes, should_take_out_ones]) and should_throw_all:
            print(
                "INFO: Not taking out ones nor converting to sixes, because should_throw_all is True."
            )
        dice_processed = []
        new_hand = current_hand.copy()  # Create a copy of the hand for this turn

        if not should_throw_all:

            # Step 1: Take out ones
            if should_take_out_ones:
                new_hand, dice_processed = BasePlayer.take_out_ones(
                    new_hand, dice_processed
                )

            # Step 2: Change sixes to ones
            if should_convert_sixes:
                new_hand, dice_processed = BasePlayer.convert_sixes(
                    new_hand, dice_processed
                )

        for die in new_hand.dice:
            if die not in dice_processed:
                die.throw()
                dice_processed.append(die)

        assert (
            len(new_hand.dice) == 3
        ), "Hand must contain exactly 3 dice after throwing"
        assert dice_processed.sort(
            key=lambda die: die.value, reverse=True
        ) == new_hand.dice.sort(
            key=lambda die: die.value, reverse=True
        ), f"All dice should be processed after throwing, but got {dice_processed} instead of {new_hand.dice}"

        return new_hand

    @staticmethod
    def take_out_ones(hand: Hand, dice_processed: List[Die]) -> Tuple[Hand, List[Die]]:
        """Takes out ones in a hand.

        Args:
            hand (Hand): The hand to take out ones from.
            dice_processed (List[Die]): The list of dice already processed.

        Raises:
            TypeError: If the hand is not an instance of Hand.
            ValueError: If the hand is finalized.

        Returns:
            Tuple[Hand, List[Die]]: The updated hand and the list of dice processed.
        """
        if not isinstance(hand, Hand):
            raise TypeError("hand must be an instance of Hand")
        if hand.finalized:
            raise ValueError("Cannot take out ones in a finalized hand")

        # Remove processed dice
        dice_to_process = [die for die in hand.dice if not die in dice_processed]

        for die in hand.dice:
            if die in dice_to_process:
                if die.value == 1:
                    die.make_a_one()
                    dice_processed.append(die)

        return hand, dice_processed

    @staticmethod
    def convert_sixes(hand: Hand, dice_processed: List[Die]) -> Tuple[Hand, List[Die]]:
        """Converts two or three sixes in a hand to ones.

        Args:
            hand (Hand): The hand to convert sixes in.
            dice_processed (List[Die]): The list of dice already processed.

        Raises:
            TypeError: _description_
            ValueError: _description_

        Returns:
            Tuple[Hand, List[Die]]: The updated hand and the list of dice processed.
        """
        if not isinstance(hand, Hand):
            raise TypeError("hand must be an instance of Hand")
        if hand.finalized:
            raise ValueError("Cannot convert sixes in a finalized hand")
        if len(hand.dice) != 3:
            raise ValueError("Hand must contain exactly 3 dice to convert sixes")

        # Remove processed dice
        dice_to_process = [die for die in hand.dice if not die in dice_processed]

        sixes = len([die for die in dice_to_process if die.value == 6])
        if sixes == 3:
            for die in hand.dice[:-1]:
                die.make_a_one()  # Convert the first two dice to ones
                dice_processed.append(die)  # Remove the die from the dice to throw

        elif sixes == 2:
            for die in hand.dice:
                if die in dice_to_process and die.value == 6:
                    die.make_a_one()  # Convert the die to a one
                    dice_processed.append(die)  # Remove the
                    break  # Only convert one die

        return hand, dice_processed


@dataclass
class ChipManager:
    chips_in_stock: int = 13
    chip_balances: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        """Convert the chip manager state to a JSON-serializable dictionary."""
        return {
            "chips_in_stock": self.chips_in_stock,
            "chip_balances": {
                str(pid): balance for pid, balance in self.chip_balances.items()
            },
        }


@dataclass
class MiniRound:
    mini_round_players: List[BasePlayer] = field(init=True)
    mini_round_index: int = 0
    turns: List[Turn] = field(default_factory=list)
    worst_turn: Optional[Turn] = None
    best_turn: Optional[Turn] = None
    given_chips: int = 0
    lost_by: Optional[PlayerID] = None

    def get_visible_hands(self) -> List[Union[List[Die], None]]:
        """Get a list of all visible hands from the mini round players."""
        return [
            {player.id: player.hand.get_visible_dice()}
            for player in self.mini_round_players
            if player.hand.get_visible_dice()
        ]

    def to_json(self) -> dict:
        """Convert the mini round state to a JSON-serializable dictionary."""
        return {
            "mini_round_players": [
                f"{p.name}({p.id})" for p in self.mini_round_players
            ],
            "mini_round_index": self.mini_round_index,
            "worst_turn": self.worst_turn.to_json() if self.worst_turn else None,
            "best_turn": self.best_turn.to_json() if self.best_turn else None,
            "given_chips": self.given_chips,
            "lost_by": str(self.lost_by) if self.lost_by else None,
            "turns": [turn.to_json() for turn in self.turns],
        }


@dataclass
class Half:
    halves_index: int = 0
    active_players: List[BasePlayer] = field(default_factory=list)
    mini_rounds: List[MiniRound] = field(default_factory=list)
    lost_by: Optional[PlayerID] = None
    stock_chips_gone: bool = False
    chip_manager: Optional[ChipManager] = field(default_factory=ChipManager)

    def to_json(self) -> dict:
        """Convert the half state to a JSON-serializable dictionary."""
        return {
            "halves_index": self.halves_index,
            "active_players": [str(player.id) for player in self.active_players],
            "mini_rounds": [mr.to_json() for mr in self.mini_rounds],
            "lost_by": str(self.lost_by) if self.lost_by else None,
            "stock_chips_gone": self.stock_chips_gone,
            "chip_manager": self.chip_manager.to_json(),
        }


@dataclass
class Round:
    round_index: int = 0
    halves: List[Half] = field(default_factory=list)
    lost_by: Optional[PlayerID] = None

    def to_json(self) -> dict:
        """Convert the round state to a JSON-serializable dictionary."""
        return {
            "round_index": self.round_index,
            "halves": [half.to_json() for half in self.halves],
            "lost_by": str(self.lost_by) if self.lost_by else None,
        }
