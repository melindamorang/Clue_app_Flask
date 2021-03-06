# Master list of cards in the game
cards = {
    "suspects": [
        "M. Brunette",
        "Sgt. Gray",
        "Mr. Green",
        "Col. Mustard",
        "Miss Peach",
        "Mrs. Peacock",
        "Prof. Plum",
        "Mme Rose",
        "Miss Scarlet",
        "Mrs. White"
    ],
    "weapons": [
        "Candlestick",
        "Horseshoe",
        "Knife",
        "Lead Pipe",
        "Poison",
        "Revolver",
        "Rope",
        "Wrench"
    ],
    "rooms": [
        "Billiard Room",
        "Carriage House",
        "Conservatory",
        "Courtyard",
        "Dining Room",
        "Drawing Room",
        "Fountain",
        "Gazebo",
        "Kitchen",
        "Library",
        "Studio",
        "Trophy Room"  
    ]
}

CONFLICTING_INFO = "Warning: Conflicting information detected. Please review prior actions and remove anything incorrect."

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
        self.update_detective_notebook()

    def check_for_solution_by_elimination(self):
        """Check if we've eliminated options sufficiently to determine the actual solution."""
        for card_type in cards:
            unknown = []
            solution_known = False
            for card in cards[card_type]:
                owner = self.detective_notebook[card_type][card]
                if owner == "SOLUTION":
                    solution_known = True
                if not self.detective_notebook[card_type][card]:
                    unknown.append(card)
            # If there is only one remaining unknown in the category, this must be the actual solution.
            if len(unknown) == 1 and not solution_known:
                self.add_to_log(f"{card} is the last remaining unknown in {card_type}.")
                for player in self.players:
                    self.enter_not_has(player, unknown[0])
                self.add_to_actual_solution(unknown[0])
                self.update_detective_notebook()

    def update_detective_notebook(self):
        """Update the detective notebook based on all current info."""
        for card in self.actual_solution:
            card_type = get_card_type_key(card)
            self.detective_notebook[card_type][card] = "SOLUTION"
        for card in self.not_it_but_not_sure_who:
            card_type = get_card_type_key(card)
            self.detective_notebook[card_type][card] = "NO"
        for player in self.players:
            for card in self.players[player].has:
                card_type = get_card_type_key(card)
                self.detective_notebook[card_type][card] = player

        self.check_for_solution_by_elimination()

    def add_card(self, player_name, card):
        """Indicate that a player has a certain card."""
        if card in self.players[player_name].has:
            # We already knew this.
            return
        if card in self.players["Me"].has:
            # This is incorrect, since I have this card, so throw a warning and don't do anything.
            self.add_to_log(CONFLICTING_INFO)
            return
        self.add_to_log(f"{player_name} has {card}.")
        self.players[player_name].has.append(card)
        # In case this information conflicts with info we already have,
        # assume this new info is correct. Eliminate this card from
        # this players does_not_have and other players' has.
        if card in self.players[player_name].does_not_have:
            self.add_to_log(CONFLICTING_INFO)
            self.players[player_name].does_not_have.remove(card)
        # Since this player has this card, no one else does, and it's not in the actual solution.
        if card in self.not_it_but_not_sure_who:
            self.not_it_but_not_sure_who.remove(card)
        if card in self.actual_solution:
            # This shouldn't happen and indicates incorrect information somewhere.
            self.add_to_log(CONFLICTING_INFO)
            self.actual_solution.remove(card)
        for plyr in [p for p in self.players.keys() if p not in [player_name, "Me"]]:
            self.enter_not_has(plyr, card)
            if card in self.players[plyr].has:
                # There is conflicting info. No one else should have this card.
                self.add_to_log(CONFLICTING_INFO)
                self.players[plyr].has.remove(card)
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
        # Update detective notebook
        self.update_detective_notebook()

    def enter_not_has(self, player_name, card):
        """Indicate that a player does not have a certain card.""" 
        if card in self.players[player_name].does_not_have:
            # We already knew this.
            return
        self.add_to_log(f"{player_name} does not have {card}.")
        self.players[player_name].does_not_have.append(card)
        # If this card is in the player's has, there is a data issue, but we'll assume this new
        # information is more correct.
        if card in self.players[player_name].has:
            self.add_to_log(CONFLICTING_INFO)
            self.players[player_name].has.remove(card)
        # Check if no one has this card.  If so, we now know that this is the actual solution.
        if self.is_actual_solution(card):
            self.add_to_actual_solution(card)
            self.add_to_log(f"{card} is in actual solution!")
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
        # Update detective notebook
        self.update_detective_notebook()

    def enter_at_least_one(self, player_name, guess):
        """Indicate that the player has at least one card from this guess."""
        # If we already know this player has all the cards in the guess, then we didn't learn anything.
        if set(guess).issubset(set(self.players[player_name].has + self.actual_solution)):
            return
        # Remove cards from guess that we already know this player doesn't have or that is the actual solution
        # This also accounts for checking anything that other players do have.
        guess = [card for card in guess if card not in self.players[player_name].does_not_have + self.actual_solution]
        # If there's nothing left in the guess, we have conflicting data. Return without doing anything.
        if not guess:
            self.add_to_log(CONFLICTING_INFO)
            return
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

    def add_to_actual_solution(self, card):
        """Add card to known solution."""
        if card in self.actual_solution:
            # We already knew this
            return

        if card in self.not_it_but_not_sure_who:
            self.add_to_log(CONFLICTING_INFO)
            return

        card_type = get_card_type_key(card)
        for cd in self.actual_solution:
            if get_card_type_key(cd) == card_type:
                self.add_to_log(CONFLICTING_INFO)

        self.add_to_log(f"{card} is in actual solution!")
        self.actual_solution.append(card)

        if len(self.actual_solution) > 3:
            self.add_to_log(CONFLICTING_INFO)

        for cd in cards[card_type]:
            if cd == card:
                continue
            owner_known = False
            for player in self.players:
                if cd in self.players[player].has:
                    owner_known = True
            if not owner_known:
                self.not_it_but_not_sure_who.append(cd)
                self.not_it_but_not_sure_who = list(set(self.not_it_but_not_sure_who))

        self.update_detective_notebook()


    def enter_disproval_of_my_guess(self, guessed_suspect, guessed_weapon, guessed_room,
                                    disprover_suspect=None, disprover_weapon=None, disprover_room=None):
        """Enter info when someone disproves my guess."""
        guess = [guessed_suspect, guessed_weapon, guessed_room]
        self.add_to_log(
            f"Action: I guessed: {guessed_suspect} (Disprover: {disprover_suspect}); {guessed_weapon} (Disprover: {disprover_weapon}); {guessed_room} (Disprover: {disprover_room})"
            )
        # The non-disprovers have none of the cards in the guess
        non_disprovers = [p for p in self.players.keys() if p not in [disprover_suspect, disprover_weapon, disprover_room, "Me"]]
        for nond in non_disprovers:
            self.add_to_log(f"{nond} did not disprove.")
            for card in guess:
                self.enter_not_has(nond, card)
        # Add info for disprovers
        if disprover_suspect:
            self.add_card(disprover_suspect, guessed_suspect)
        if disprover_weapon:
            self.add_card(disprover_weapon, guessed_weapon)
        if disprover_room:
            self.add_card(disprover_room, guessed_room)

    def narrow_down_guess(self, guess, disprovers):
        """For each disprover and remaining item in the guess, eliminate possibilities."""
        # If the guess or disprovers is empty, we're done
        if not guess or not disprovers:
            return [], []

        # If the number of disprovers is greater than the length of the guess, we have a data
        # problem, so just return without doing anything
        if len(disprovers) > len(guess):
            self.add_to_log(CONFLICTING_INFO)
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
                return self.narrow_down_guess(guess, disprovers)

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
        guess = [guessed_suspect, guessed_weapon, guessed_room]
        self.add_to_log(f"Action: Guess by {guesser}: {', '.join(guess)}; Disprovers: {', '.join(disprovers)}")
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
        self.update_detective_notebook()

    def enter_snoop(self, snooped_player, card):
        """Enter a snooped card for a player."""
        self.add_to_log(f"Action: Snooped {snooped_player} and saw {card}.")
        self.add_card(snooped_player, card)

    def play_game_from_log_text(self, log):
        """Set up a game and play actions based on a list of logged actions."""
        my_suspects = []
        my_weapons = []
        my_rooms = []
        other_players_init = []
        game_initialized = False
        for idx, line in enumerate(log):
            if line.startswith("My suspects: "):
                # Indicates initialization of game. These are my cards.
                my_suspects = line.split("My suspects: ")[1].split(", ")
                if my_suspects == [""]:
                    my_suspects = []
            elif line.startswith("My weapons: "):
                # Indicates initialization of game. These are my cards.
                my_weapons = line.split("My weapons: ")[1].split(", ")
                if my_weapons == [""]:
                    my_weapons = []
            elif line.startswith("My rooms: "):
                # Indicates initialization of game. These are my cards.
                my_rooms = line.split("My rooms: ")[1].split(", ")
                if my_rooms == [""]:
                    my_rooms = []
            elif line.startswith("Initialized '"):
                # Indicates initialization of game. This is another player.
                name = line.split("Initialized '")[1].split("' with ")[0]
                num_cards = int(line.split(f"Initialized '{name}' with ")[1].split(" cards.")[0])
                other_players_init.append([name, num_cards])
            elif line.startswith("Action: "):
                if log[idx-1].startswith("Initialized '"):
                    # This is the first action in the game, and we're finished with initialization,
                    # so go ahead and pass in all the game setup.
                    game_initialized = True
                    self.setup_game(my_suspects, my_weapons, my_rooms, other_players_init)
                if line.startswith("Action: Snooped "):
                    # I snooped.
                    name = line.split("Action: Snooped ")[1].split(" and saw ")[0]
                    card = line.split(f"Action: Snooped {name} and saw ")[1].strip(".")
                    self.enter_snoop(name, card)
                elif line.startswith("Action: Guess by "):
                    # Another player guessed.
                    guesser = line.split("Action: Guess by ")[1].split(": ")[0]
                    guessed_suspect, guessed_weapon, guessed_room = line.split(f"Action: Guess by {guesser}: ")[1].split("; Disprovers: ")[0].split(", ")
                    disprovers = line.split("; Disprovers: ")[1].split(", ")
                    if disprovers == [""]:
                        disprovers = []
                    self.enter_other_players_guess(guesser, guessed_suspect, guessed_weapon, guessed_room, disprovers)
                elif line.startswith("Action: I guessed: "):
                    # I guessed.
                    guess_disprovers = line.split("Action: I guessed: ")[1].split("; ")
                    cards = []
                    disprovers = []
                    for gd in guess_disprovers:
                        card, disprover = gd.split(" (Disprover: ")
                        cards.append(card.strip())
                        disprovers.append(disprover.strip(")"))
                    self.enter_disproval_of_my_guess(cards[0], cards[1], cards[2], disprovers[0], disprovers[1], disprovers[2])
        
        # If we got all the way through the log without initializing the game, the log probably had no actions yet,
        # or all actions were removed, so go ahead and initialize it.
        if not game_initialized:
            self.setup_game(my_suspects, my_weapons, my_rooms, other_players_init)

if __name__ == '__main__':
    app.run(threaded=True)