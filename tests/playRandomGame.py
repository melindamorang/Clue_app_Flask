import random
import sys
sys.path.insert(1, r'E:\Code\Clue_app_Flask')
import clueLogic

class RandomGame():

    def __init__(self, seed=None):

        # Specify a random seed so the game is reproducible
        if not seed:
            seed = random.randrange(sys.maxsize)
        random.seed(seed)
        print("Random seed was:", seed)

        # Create deck of cards and shuffle them
        all_cards = clueLogic.cards["suspects"] + clueLogic.cards["weapons"] + clueLogic.cards["rooms"]
        random.shuffle(all_cards)

        # Extract actual solution
        actual_suspect, actual_weapon, actual_room = self.generate_random_guess()
        self.actual_solution = [actual_suspect, actual_weapon, actual_room]
        print("Actual solution: ", self.actual_solution)
        for sol in self.actual_solution:
            all_cards.remove(sol)

        # Initialize the players and their hands
        num_players = random.randint(2, 10)
        print(f"Number of players: {num_players}")
        hands = [all_cards[i::num_players] for i in range(0, num_players)]
        random.shuffle(hands)
        self.players = {}
        # Assign a hand to each other player
        for i in range(0, num_players-1):
            player_cards = random.choice(hands)
            self.players[f"Player_{i + 1}"] = player_cards
            hands.remove(player_cards)
        # The reamining hand is mine
        my_cards = hands[0]
        for player in self.players:
            print(player, self.players[player])
        print("Me", my_cards)

        # Initialize game
        my_suspects = []
        my_weapons = []
        my_rooms = []
        for card in my_cards:
            card_type = clueLogic.get_card_type_key(card)
            if card_type == "suspect":
                my_suspects.append(card)
            elif card_type == "weapons":
                my_weapons.append(card)
            else:
                my_rooms.append(card)
        other_players_init = []
        for player in self.players:
            other_players_init.append([player, len(self.players[player])])
        self.game = clueLogic.game()
        self.game.setup_game(my_suspects, my_weapons, my_rooms, other_players_init)

    def generate_random_guess(self):
        """Return a random suspect, weapon, and room."""
        guessed_suspect = random.choice(clueLogic.cards["suspects"])
        guessed_weapon = random.choice(clueLogic.cards["weapons"])
        guessed_room = random.choice(clueLogic.cards["rooms"])
        return guessed_suspect, guessed_weapon, guessed_room

    def snoop(self, player):
        """Pick a random one of the snooped player's cards to see."""
        snooped_card = random.choice(self.players[player])
        self.game.enter_snoop(player, snooped_card)

    def guess(self):
        """Make a random guess and enter disprovers."""
        # Generate a random guess
        guessed_suspect, guessed_weapon, guessed_room = self.generate_random_guess()
        # Collect disprovers, but make sure the disprover doesn't show multiple cards
        disprovers = {"suspect": "", "weapon": "", "room": ""}
        for player in self.players:
            player_has = []
            if guessed_suspect in self.players[player]:
                player_has.append("suspect")
            if guessed_weapon in self.players[player]:
                player_has.append("weapon")
            if guessed_room in self.players[player]:
                player_has.append("room")
            if player_has:
                disprovers[random.choice(player_has)] = player
        self.game.enter_disproval_of_my_guess(guessed_suspect, guessed_weapon, guessed_room, disprovers["suspect"], disprovers["weapon"], disprovers["room"])

    def other_player_guess(self, guesser):
        """Make another player make a random guess and enter disprovers."""
        # Generate a random guess
        guessed_suspect, guessed_weapon, guessed_room = self.generate_random_guess()
        # Collect disprovers
        disprovers = []
        for player in self.players:
            if player == guesser:
                continue
            for card in [guessed_suspect, guessed_weapon, guessed_room]:
                if card in self.players[player]:
                    disprovers.append(player)
                    break
        self.game.enter_other_players_guess(guesser, guessed_suspect, guessed_weapon, guessed_room, disprovers)

    def other_player_turn(self, player):
        """Another player takes a turn. Return whether the game is finished."""
        # Give the player an 80% chance of making a guess
        if random.random() <= 0.8:
            self.other_player_guess(player)
        # print("Current solution:", self.game.actual_solution)
        return self.is_game_finished()

    def my_turn(self):
        """I take a turn. Return whether the game is finished."""
        # Give me a 25% chance of snooping
        if random.random() <= 0.25:
            self.snoop(random.choice(list(self.players.keys())))
        # print("Current solution:", self.game.actual_solution)
        # Give me an 80% chance of making a guess
        if random.random() <= 0.8:
            self.guess()
        # print("Current solution:", self.game.actual_solution)
        return self.is_game_finished()

    def is_game_finished(self):
        """Determine if the game is finished based on whether the full solution is known."""
        solution_correct = True
        if len(self.game.actual_solution) == 3:
            print("Game is finished. Determined solution:", self.game.actual_solution)
            print("Correct solution was:", self.actual_solution)
            if sorted(self.game.actual_solution) != sorted(self.actual_solution):
                print("OH NO!! THE SOLUTION WAS INCORRECT")
                solution_correct = False
            else:
                print("AWESOME! CORRECT SOLUTION DETERMINED.")
            print("Detective notebook:")
            for cat in clueLogic.cards:
                print(f"--{cat}--")
                for card in clueLogic.cards[cat]:
                    print("  ", card, self.game.detective_notebook[cat][card])
            return True, solution_correct
        return False, False


class RandomInvalidGame(RandomGame):
    """Play a game where inputs may be invalid, just to make sure the logic never crashes."""

    def snoop(self, player):
        """Pick a random card to see, even if it doesn't belong to this player."""
        snooped_card = random.choice(clueLogic.cards["suspects"] + clueLogic.cards["weapons"] + clueLogic.cards["rooms"])
        self.game.enter_snoop(player, snooped_card)

    def guess(self):
        """Make a random guess and enter disprovers."""
        # Generate a random guess
        guessed_suspect, guessed_weapon, guessed_room = self.generate_random_guess()
        # Collect disprovers, but make sure the disprover doesn't show multiple cards
        disprovers = {"suspect": "", "weapon": "", "room": ""}
        num_disprovers = random.randint(0, min(3, len(self.players)))
        if num_disprovers:
            disproving_players = random.sample(list(self.players.keys()), num_disprovers)
            disproving_keys = random.sample(list(disprovers.keys()), num_disprovers)
            for idx, key in enumerate(disproving_keys):
                disprovers[key] = disproving_players[idx]
        self.game.enter_disproval_of_my_guess(guessed_suspect, guessed_weapon, guessed_room, disprovers["suspect"], disprovers["weapon"], disprovers["room"])

    def other_player_guess(self, guesser):
        """Make another player make a random guess and enter disprovers."""
        # Generate a random guess
        guessed_suspect, guessed_weapon, guessed_room = self.generate_random_guess()
        # Collect disprovers
        num_disprovers = random.randint(0, min(3, len(self.players)))
        disprovers = []
        if num_disprovers:
            disprovers = random.sample(list(self.players.keys()), num_disprovers)
        self.game.enter_other_players_guess(guesser, guessed_suspect, guessed_weapon, guessed_room, disprovers)

    def is_game_finished(self):
        return False


def playRandomGame(seed = None):
    if not seed:
        seed = random.randrange(sys.maxsize)
    randomGame = RandomGame(seed)
    # Get players and choose an arbitrary turn order to go in
    players = list(randomGame.players.keys()) + ["Me"]
    random.shuffle(players)
    game_finished = False
    solution_correct = False
    while not game_finished:
        for player in players:
            if player == "Me":
                game_finished, solution_correct = randomGame.my_turn()
            else:
                game_finished, solution_correct = randomGame.other_player_turn(player)
            if game_finished:
                break
    return solution_correct

def playRandomInvalidGame(seed = None):
    if not seed:
        seed = random.randrange(sys.maxsize)
    randomGame = RandomInvalidGame(seed)
    # Get players and choose an arbitrary turn order to go in
    players = list(randomGame.players.keys()) + ["Me"]
    random.shuffle(players)
    turn_limit = 20
    for x in range(0, turn_limit):
        for player in players:
            if player == "Me":
                randomGame.my_turn()
            else:
                randomGame.other_player_turn(player)
    return True

def main(validGame = True, seed = None):
    if validGame:
        game_succeeded = playRandomGame(seed)
    else:
        game_succeeded = playRandomInvalidGame(seed)
    return game_succeeded

if __name__ == '__main__':
    seed = random.randrange(sys.maxsize)
    valid_game = True
    main(valid_game, seed)
