# Master list of cards in the game
cards = {
    "suspects": [
        "Col. Mustard",
        "Prof. Plum",
        "Mr. Green",
        "Mrs. Peacock",
        "Miss Scarlet",
        "Mrs. White",
        "Mme Rose",
        "Sgt. Gray",
        "M. Brunette",
        "Miss Peach"
    ],
    "weapons": [
        "Knife",
        "Candlestick",
        "Revolver",
        "Rope",
        "Lead Pipe",
        "Wrench",
        "Poison",
        "Horseshoe"
    ],
    "rooms": [
        "Courtyard",
        "Gazebo",
        "Drawing Room",
        "Dining Room",
        "Kitchen",
        "Carriage House",
        "Trophy Room",
        "Conservatory",
        "Studio",
        "Billiard Room",
        "Library",
        "Fountain"
    ]
}

def get_card_type_key(card):
    """Return the key indicating the type of card this is (suspects, weapons, rooms)."""
    if card in cards["suspects"]:
        return "suspects"
    if card in cards["weapons"]:
        return "weapons"
    if card in cards["rooms"]:
        return "rooms"


class game():

    def __init__(self):
        """Initialize a new game."""

        # Players in the current game
        self.players = {}

        # My detective notebook, indicating what I know about who has what.
        self.detective_notebook = {
            "suspects": {suspect: "" for suspect in cards["suspects"]},
            "weapons": {weapon: "" for weapon in cards["weapons"]},
            "rooms": {room: "" for room in cards["rooms"]}
        }

        # Running log of stuff happening in the game
        self.log = []
        self.add_to_log("New game initalized.")

        # The current game's actual solution
        self.actual_solution = []

        # We know none of these is the actual solution, but we don't know who has which
        self.not_it_but_not_sure_who = []

    class player():
        """Class defining a player in a game."""
        def __init__(self, name, num_cards, initial_not_has=None, initial_has=None):
            self.name = name
            self.num_cards = num_cards
            # Do not set the defaults to [] in the class definition because of
            # https://stackoverflow.com/questions/14522537/python-adding-element-to-an-instances-list-also-adds-it-to-another-instances-l
            if initial_not_has:
                self.does_not_have = initial_not_has
            else:
                self.does_not_have = []
            if initial_has:
                self.has = initial_has
            else:
                self.has = []
            self.at_least_one = []

    def add_to_log(self, msg):
        """Insert a log message at the front of the log list."""
        print(msg)
        self.log.insert(0, msg)

    def setup_game(self, my_suspects, my_weapons, my_rooms, other_players):
        """Initialize beginning-of-game info, including my own cards and the names of the other players.

        other_players: List of tuples of (player_name, number of cards for that player)"""

        # Initialize myself as a player object
        my_cards = my_suspects + my_weapons + my_rooms
        not_my_cards = [card for card in cards["suspects"] + cards["weapons"] + cards["rooms"] if card not in my_cards]
        self.players["Me"] = self.player("Me", len(my_cards), not_my_cards, my_cards)
        self.add_to_log("My suspects: " + ", ".join(my_suspects))
        self.add_to_log("My weapons: " + ", ".join(my_weapons))
        self.add_to_log("My rooms: " + ", ".join(my_rooms))
        # Initialize other players
        for player_info in other_players:
            self.players[player_info[0]] = self.player(player_info[0], player_info[1], [card for card in my_cards])
            self.add_to_log(f"Initialized '{player_info[0]}' with {player_info[1]} cards.")
        # Update the detective notebook with my cards
        for suspect in my_suspects:
            self.update_detective_notebook(suspect, "Me", "suspects")
        for weapon in my_weapons:
            self.update_detective_notebook(weapon, "Me", "weapons")
        for room in my_rooms:
            self.update_detective_notebook(room, "Me", "rooms")

    def check_for_solution_by_elimination(self):
        """Check if we've eliminated options sufficiently to determine the actual solution."""
        for card_type in cards:
            unknown = []
            for card in cards[card_type]:
                if not self.detective_notebook[card_type][card]:
                    unknown.append(card)
            # If there is only one remaining unknown in the category, this must be the actual solution.
            if len(unknown) == 1:
                self.add_to_log(f"{card} is the last remaining unknown in {card_type}.")
                self.add_to_log(f"{card} is in actual solution!")
                self.detective_notebook[card_type][unknown[0]] = "SOLUTION"
                self.actual_solution.append(unknown[0])
                self.actual_solution = list(set(self.actual_solution))
                for player in self.players:
                    self.enter_not_has(player, unknown[0])

    def update_detective_notebook(self, card, owner, card_type=None):
        """Update the detective notebook with new information."""
        if not card_type:
            card_type = get_card_type_key(card)
        if owner == "NO":
            if not self.detective_notebook[card_type][card]:
                self.detective_notebook[card_type][card] = owner
        else:
            self.detective_notebook[card_type][card] = owner
        if owner == "SOLUTION":
            # Update all other items in detective notebook with a mark indicating they aren't the solution
            for cd in cards[card_type]:
                if not self.detective_notebook[card_type][cd]:
                    self.detective_notebook[card_type][cd] = "NO"
        else:
            self.check_for_solution_by_elimination()

    def add_card(self, player_name, card):
        """Indicate that a player has a certain card."""
        if card in self.players[player_name].has:
            # We already knew this.
            return
        self.add_to_log(f"{player_name} has {card}.")
        self.players[player_name].has.append(card)
        # Update detective notebook
        self.update_detective_notebook(card, player_name)
        # Since this player has this card, no one else does.
        if card in self.not_it_but_not_sure_who:
            self.not_it_but_not_sure_who.remove(card)
        for plyr in [p for p in self.players.keys() if p not in [player_name, "Me"]]:
            self.enter_not_has(plyr, card)
        # If we now know all of the player's cards, then we know they don't have any other cards
        if len(self.players[player_name].has) == self.players[player_name].num_cards:
            for cd in cards["suspects"] + cards["weapons"] + cards["rooms"]:
                if cd not in self.players[player_name].has:
                    self.enter_not_has(player_name, cd)
        # Clean up at_least_ones with this card in it
        new_at_least_one = []
        for guess in self.players[player_name].at_least_one:
            # A guess will have either 2 or 3 cards in it
            if card in guess:
                if set(guess).issubset(set(self.players[player_name].has)):
                    # All remaining cards in the at_least_one guess belong to this player.
                    # We won't get any further info out of this guess, so don't preserve it.
                    continue
            new_at_least_one.append(guess)
        self.players[player_name].at_least_one = new_at_least_one

    def enter_not_has(self, player_name, card):
        """Indicate that a player does not have a certain card.""" 
        if card in self.players[player_name].does_not_have:
            # We already knew this.
            return
        self.add_to_log(f"{player_name} does not have {card}.")
        self.players[player_name].does_not_have.append(card)
        # Check if no one has this card.  If so, we now know that this is the actual solution.
        if self.is_actual_solution(card):
            self.actual_solution.append(card)
            self.actual_solution = list(set(self.actual_solution))
            self.add_to_log(f"{card} is in actual solution!")
            self.update_detective_notebook(card, "SOLUTION")
        # Go through prior guesses where we know they had at least one of the cards
        # and remove the current card that we know we don't have.
        new_at_least_one = []
        for guess in self.players[player_name].at_least_one:
            # A guess will have either 2 or 3 cards in it
            if card in guess:
                # We narrowed things down. Remove this card from the guess
                guess.remove(card)
                if len(guess) == 1:
                    # We learned something!
                    # The player must have the remaining card in the guess
                    self.add_card(player_name, guess[0])
                    # This guess has concluded, so continue to the next guess without
                    # preserving this one in our updated guess list
                    continue
            # Preserve still-relevant guesses
            new_at_least_one.append(guess)
        # Update self.at_least_one with our new info
        self.players[player_name].at_least_one = new_at_least_one

    def enter_at_least_one(self, player_name, guess):
        """Indicate that the player has at least one card from this guess."""
        # If we already know this player has all the cards in the guess, then we didn't learn anything.
        if set(guess).issubset(set(self.players[player_name].has + self.actual_solution)):
            return
        # Remove cards from guess that we already know this player doesn't have or that is the actual solution
        # This also accounts for checking anything that other players do have.
        guess = [card for card in guess if card not in self.players[player_name].does_not_have + self.actual_solution]
        # If there's only one card in the guess, obviously this player has it.
        if len(guess) == 1:
            self.add_card(player_name, guess[0])
            return
        # Otherwise, we know the player has at least one of the remaining guessed cards
        self.add_to_log(f"{player_name} has at least one of: {', '.join(guess)}")
        self.players[player_name].at_least_one.append(guess)

    def is_actual_solution(self, card):
        """Return True if the current card is in does_not_have for all players."""
        if card in self.actual_solution:
            # We already knew this.
            return True
        if card in self.not_it_but_not_sure_who:
            # We know somebody has it, although we don't know who.
            return False
        # Check if all players don't have it.
        for player in self.players:
            if card not in self.players[player].does_not_have:
                # As soon as we are unsure of the card, return False because we can't tell
                # if this is the real solution
                return False
        # If we found the card in all does_not_have lists, this must be the answer
        return True

    def enter_disproval_of_my_guess(self, guessed_suspect, guessed_weapon, guessed_room,
                                    disprover_suspect=None, disprover_weapon=None, disprover_room=None):
        """Enter info when someone disproves my guess."""
        self.add_to_log(f"I guessed: {guessed_suspect}, {guessed_weapon}, {guessed_room}")
        non_disprovers = [p for p in self.players.keys() if p not in [disprover_suspect, disprover_weapon, disprover_room, "Me"]]
        for nond in non_disprovers:
            self.add_to_log(f"{nond} did not disprove.")
        # Enter retrieved information
        if disprover_suspect:
            self.add_to_log(f"{disprover_suspect} disproved {guessed_suspect}.")
            self.add_card(disprover_suspect, guessed_suspect)
        else:
            self.add_to_log(f"No one disproved {guessed_suspect}.")
            for player_name in non_disprovers:
                self.enter_not_has(player_name, guessed_suspect)
        if disprover_weapon:
            self.add_to_log(f"{disprover_weapon} disproved {guessed_weapon}.")
            self.add_card(disprover_weapon, guessed_weapon)
        else:
            self.add_to_log(f"No one disproved {guessed_weapon}.")
            for player_name in non_disprovers:
                self.enter_not_has(player_name, guessed_weapon)
        if disprover_room:
            self.add_to_log(f"{disprover_room} disproved {guessed_room}.")
            self.add_card(disprover_room, guessed_room)
        else:
            self.add_to_log(f"No one disproved {guessed_room}.")
            for player_name in non_disprovers:
                self.enter_not_has(player_name, guessed_room)

    def narrow_down_guess(self, guess, disprovers):
        """For each disprover and remaining item in the guess, eliminate possibilities."""
        # If the guess is empty, we're done
        if not guess:
            return [], []

        # If there's exactly one disprover and one card remaining in the guess, then we know
        # that remaining disprover had that card, and there's nothing more to do here.
        if len(guess) == 1 and len(disprovers) == 1:
            self.add_card(disprovers[0], guess[0])
            return [], []

        # Otherwise, try to determine which disprover had which card.
        possible_disproves = {disprover: [card for card in guess] for disprover in disprovers}
        # Eliminate cards from each disprover that we know they don't have
        for disprover in possible_disproves:
            for card in guess:
                if card in self.players[disprover].does_not_have:
                    possible_disproves[disprover].remove(card)
            # If there's only one remaining possibility in the guess,
            # we know they have to have it.
            if len(possible_disproves[disprover]) == 1:
                card_to_remove = possible_disproves[disprover][0]
                self.add_card(disprover, card_to_remove)
                # Eliminate the card and disprover from the possibilities
                guess.remove(card_to_remove)
                disprovers.remove(disprover)
                # Recursively call this function to try to eliminate some more.
                self.narrow_down_guess(guess, disprovers)

        # We've run out of stuff to learn. Return remaining unknown guess items and disprovers
        return guess, disprovers

    def remove_known_from_guess(self, guesser, guess):
        """Remove items from the guess if they're mine, the guesser's, or in the known solution."""
        updated_guess = [card for card in guess]
        for card in guess:
            if card in self.players["Me"].has or card in self.players[guesser].has or card in self.actual_solution:
                updated_guess.remove(card)
        return updated_guess

    def enter_other_players_guess(self, guesser, guessed_suspect, guessed_weapon, guessed_room, disprovers):
        """Get other player's entered guess and disprovers and see what we can learn."""
        self.add_to_log(f"Guess by {guesser}: {guessed_suspect}, {guessed_weapon}, {guessed_room}")
        self.add_to_log(f"Disprovers: {', '.join(disprovers)}")
        guess = [guessed_suspect, guessed_weapon, guessed_room]
        non_disprovers = [p for p in self.players.keys() if p not in disprovers + [guesser, "Me"]]
        for nond in non_disprovers:
            self.add_to_log(f"{nond} did not disprove.")

        # Ignore the guessed card if I or the guesser has it or it's in the known solution
        guess = self.remove_known_from_guess(guesser, guess)
        if not guess:
            # I or the guesser had all the cards, or they're in the known solution, so we're done here.
            return

        # The non-disprovers definitely don't have these cards.
        for person in non_disprovers:
            for card in guess:
                self.enter_not_has(person, card)
        # Clean up the guess again in case entering not_has triggered more information
        guess = self.remove_known_from_guess(guesser, guess)
        if not guess:
            return
        
        # If the number of disprovers is equal to the number of cards remaining in the guess,
        # then the guesser definitely doesn't have any of the cards.
        if len(disprovers) == len(guess):
            for card in guess:
                self.enter_not_has(guesser, card)
        # Clean up the guess again in case entering not_has triggered more information
        guess = self.remove_known_from_guess(guesser, guess)
        if not guess:
            return

        # For each disprover and remaining item in the guess, eliminate possibilities
        guess, disprovers = self.narrow_down_guess(guess, disprovers)
        # Clean up the guess again in case entering narrowing the guess down triggered more information
        guess = self.remove_known_from_guess(guesser, guess)
        if not guess:
            # We figured it all out. We're done.
            return

        # The remaining disprovers each have at least one of the remaining cards in the guess
        for person in disprovers:
            self.enter_at_least_one(person, guess)
        # Clean up the guess again in case entering narrowing the guess down triggered more information
        guess = self.remove_known_from_guess(guesser, guess)
        if not guess:
            # We figured it all out. We're done.
            return

        # Special case when the number of remaining unknowns in the guess matches the number
        # of remaining disprovers. We know none of them is the correct
        # solution, although we don't know specifically who has what.
        if len(disprovers) == len(guess):
            print("Although we don't know who has these cards, we know they are not the correct solution:", guess)
            for card in guess:
                self.not_it_but_not_sure_who.append(card)
                self.not_it_but_not_sure_who = list(set(self.not_it_but_not_sure_who))
                # Update detective notebook
                self.update_detective_notebook(card, "NO")

    def enter_snoop(self, snooped_player, card):
        """Enter a snooped card for a player."""
        self.add_to_log(f"Snooped {snooped_player}.")
        self.add_card(snooped_player, card)

if __name__ == '__main__':
    app.run(threaded=True)