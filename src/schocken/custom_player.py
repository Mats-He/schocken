from schocken.base import BasePlayer


class Player(BasePlayer):
    """
    A basic player implementation for the Schocken game.
    Implements a simple strategy for evaluating the current hand and deciding whether to throw again.
    """

    def eval_hand_and_throw(self, current_hand, *args, **kwargs):
        """
        Evaluate the current hand and decide whether to end the turn or throw again.

        Args:
            current_hand (Hand): The player's current hand to evaluate.
            *args: Additional positional arguments (unused).
            **kwargs: Additional keyword arguments (unused).

        Returns:
            Tuple[bool, Hand]:
                - end_turn (bool): Whether the player should end their turn.
                - new_hand (Hand): The potentially updated hand after throwing.

        The current implementation always throws again, taking out ones and converting sixes to ones.
        """
        end_turn = False
        # Evaluation
        # TODO: if current hand > any other players hand, end turn (unless its a schock thats higher -> try to get schock out)
        # TODO: calculated risk: if many players have ones out, a high dice or small straight might be enough
        # TODO: end turn on schock out

        # Throwing again
        new_hand = self._throw_new_hand(
            current_hand=current_hand,
            should_take_out_ones=True,
            should_convert_sixes=True,
            should_throw_all=False,
        )

        return end_turn, new_hand
