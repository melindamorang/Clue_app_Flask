import sys
import unittest

sys.path.insert(1, r'E:\Code\Clue_app_Flask')
import clueLogic

class TestClueLogic(unittest.TestCase):

    def setUp(self):

        self.sample_game = {
            "Me": [
                "Mme Rose",
                "Prof. Plum",
                "Revolver",
                "Gazebo",
                "Carriage House",
                "Kitchen"
            ],
            "Susan": [
                "Mrs. Peacock",
                "Col. Mustard",
                "Mrs. White",
                "Miss Peach",
                "Knife",
                "Trophy Room",
                "Library"
            ],
            "Andy": [
                "Miss Scarlet",
                "Rope",
                "Lead Pipe",
                "Wrench",
                "Drawing Room",
                "Dining Room",
                "Conservatory",
            ],
            "Sarah": [
                "M. Brunette",
                "Mr. Green",
                "Horseshoe"
                "Poison",
                "Billiard Room",
                "Fountain",
                "Courtyard"
            ]
        }
        # Actual solution is Sgt. Gray, Candlestick, Studio

        self.my_suspects = [card for card in self.sample_game["Me"] if clueLogic.get_card_type_key(card) == "suspects"]
        self.my_weapons = [card for card in self.sample_game["Me"] if clueLogic.get_card_type_key(card) == "weapons"]
        self.my_rooms = [card for card in self.sample_game["Me"] if clueLogic.get_card_type_key(card) == "rooms"]
        self.other_players = [player for player in self.sample_game if player != "Me"]
        self.other_players_init = [[player, len(self.sample_game[player])] for player in self.other_players]

    def test_setup_game(self):
        """Test that calling setup_game correctly populates player cards and detective notebook."""
        game = clueLogic.game()
        game.setup_game(self.my_suspects, self.my_weapons, self.my_rooms, self.other_players_init)
        self.assertEqual(4, len(game.players))
        # Make sure players are properly initialized
        # The confusingly-named assertCountEqual does an unordered list comparison
        self.assertCountEqual(self.sample_game["Me"], game.players["Me"].has)
        for player in self.other_players:
            self.assertEqual([], game.players[player].has)
            self.assertEqual(len(self.sample_game[player]), game.players[player].num_cards)
            self.assertCountEqual(self.sample_game["Me"], game.players[player].does_not_have)
        # Check detective notebook
        expected_detective_notebook = {
            "suspects": {suspect: "" for suspect in clueLogic.cards["suspects"]},
            "weapons": {weapon: "" for weapon in clueLogic.cards["weapons"]},
            "rooms": {room: "" for room in clueLogic.cards["rooms"]}
        }
        for suspect in self.my_suspects:
            expected_detective_notebook["suspects"][suspect] = "Me"
        for weapon in self.my_weapons:
            expected_detective_notebook["weapons"][weapon] = "Me"
        for room in self.my_rooms:
            expected_detective_notebook["rooms"][room] = "Me"
        self.assertDictEqual(expected_detective_notebook, game.detective_notebook)
        
    def test_add_card(self):
        """Test add_card."""
        # Set up a contrived game with circumstances useful for testing
        game = clueLogic.game()
        game.setup_game(self.my_suspects, self.my_weapons, self.my_rooms, self.other_players_init)
        player_to_add_to = "Sarah"
        card_to_add = "Mr. Green"
        game.not_it_but_not_sure_who = [card_to_add]
        game.players[player_to_add_to].has.append("Horseshoe")
        # Set up at_least_ones. With the addition of Mr. Green, the first entry should be eliminated, and the others should remain
        game.players[player_to_add_to].at_least_one = [[card_to_add, "Horseshoe"], [card_to_add, "Lead Pipe"], ["Col. Mustard", "Billiard Room"]]
        # Add the card
        game.add_card(player_to_add_to, card_to_add)
        # Make sure card was added to player's list
        self.assertIn(card_to_add, game.players[player_to_add_to].has)
        # Make sure detective notebook was updated
        self.assertEqual(player_to_add_to, game.detective_notebook[clueLogic.get_card_type_key(card_to_add)][card_to_add])
        # Make sure card was added to the other players' does_not_have list
        for player in self.other_players:
            if player == player_to_add_to:
                continue
            self.assertIn(card_to_add, game.players[player].does_not_have)
        # Make sure the card was removed from not_it_but_not_sure_who
        self.assertEqual([], game.not_it_but_not_sure_who)
        # Make sure the player's at_least_one was updated
        self.assertEqual([[card_to_add, "Lead Pipe"], ["Col. Mustard", "Billiard Room"]], game.players[player_to_add_to].at_least_one)

    def test_enter_not_has(self):
        """Test enter_not_has."""
        # Set up a contrived game with circumstances useful for testing
        game = clueLogic.game()
        game.setup_game(self.my_suspects, self.my_weapons, self.my_rooms, self.other_players_init)
        player_to_enter = "Sarah"
        card_to_enter = "Sgt. Gray"
        game.players[player_to_enter].has.append("Horseshoe")
        for player in game.players:
            if player not in ["Me", player_to_enter]:
                game.players[player].does_not_have.append(card_to_enter)
        # Set up at_least_ones. With the removal of Miss Scarlet, the first entry should be eliminated and the Poison added to has
        # The second entry should get Miss Scarlet removed but leave the rest.
        game.players[player_to_enter].at_least_one = [[card_to_enter, "Poison"], [card_to_enter, "Horseshoe", "Billiard Room"]]
        # Add the card
        game.enter_not_has(player_to_enter, card_to_enter)
        # Make sure card was added to player's does_not_have list
        self.assertIn(card_to_enter, game.players[player_to_enter].does_not_have)
        # Make sure the player's at_least_one was updated
        self.assertEqual([["Horseshoe", "Billiard Room"]], game.players[player_to_enter].at_least_one)
        # Make sure actual_solution was updated
        self.assertEqual([card_to_enter], game.actual_solution)
        # Make sure detective notebook was updated
        self.assertEqual("SOLUTION", game.detective_notebook["suspects"][card_to_enter])
        for card in clueLogic.cards["suspects"]:
            if card in self.my_suspects:
                self.assertEqual("Me", game.detective_notebook["suspects"][card])
            elif card != card_to_enter:
                self.assertEqual("NO", game.detective_notebook["suspects"][card])

    def test_enter_at_least_one(self):
        """Test enter_at_least_one."""
        # Set up a contrived game with circumstances useful for testing
        game = clueLogic.game()
        game.setup_game(self.my_suspects, self.my_weapons, self.my_rooms, self.other_players_init)
        game.actual_solution = ["Sgt. Gray", "Studio"]
        player_to_enter = "Sarah"
        game.players[player_to_enter].has.append("Horseshoe")
        game.players[player_to_enter].does_not_have.append("Dining Room")
        # If we already know this player has all the cards in the guess, method does nothing
        game.enter_at_least_one(player_to_enter, ["Sgt. Gray", "Horseshoe"])
        self.assertEqual([], game.players[player_to_enter].at_least_one)
        # Test removing cards we know the player doesn't have from the guess and adding a card to has
        # if there is only one remaining. We know she doesn't have Sgt. Gray or the Dining Room,
        # so she must have the Poison.
        game.enter_at_least_one(player_to_enter, ["Sgt. Gray", "Poison", "Dining Room"])
        self.assertEqual([], game.players[player_to_enter].at_least_one)
        self.assertIn("Poison", game.players[player_to_enter].has)
        # Test actually adding to at_least_one when we can't determine any further info
        # Sgt. Gray should be weeded out, but we don't know about Rope and Fountain
        game.enter_at_least_one(player_to_enter, ["Sgt. Gray", "Rope", "Fountain"])
        self.assertIn(["Rope", "Fountain"], game.players[player_to_enter].at_least_one)

    def test_enter_disproval_of_my_guess(self):
        """Test enter_disproval_of_my_guess."""
        # Set up a contrived game with circumstances useful for testing
        game = clueLogic.game()
        game.setup_game(self.my_suspects, self.my_weapons, self.my_rooms, self.other_players_init)
        # Test that has gets updated for all disprovers
        guessed_suspect = "Mrs. Peacock"
        guessed_weapon = "Lead Pipe"
        guessed_room = "Fountain"
        disprover_suspect = "Susan"
        disprover_weapon = "Andy"
        disprover_room = "Sarah"
        game.enter_disproval_of_my_guess(guessed_suspect, guessed_weapon, guessed_room,
                                         disprover_suspect, disprover_weapon, disprover_room)
        self.assertIn(guessed_suspect, game.players[disprover_suspect].has)
        self.assertIn(guessed_weapon, game.players[disprover_weapon].has)
        self.assertIn(guessed_room, game.players[disprover_room].has)
        self.assertEqual([], game.players[disprover_room].at_least_one)
        # Test that all non-disprovers get cards added to does_not_have
        # Use the real solution
        guessed_suspect = "Sgt. Gray"
        guessed_weapon = "Candlestick"
        guessed_room = "Studio"
        disprover_suspect = None
        disprover_weapon = None
        disprover_room = None
        game.enter_disproval_of_my_guess(guessed_suspect, guessed_weapon, guessed_room,
                                         disprover_suspect, disprover_weapon, disprover_room)
        for player in game.players:
            self.assertIn(guessed_suspect, game.players[player].does_not_have)

    def test_narrow_down_guess(self):
        """Test narrow_down_guess."""
        # Set up a contrived game with circumstances useful for testing
        game = clueLogic.game()
        game.setup_game(self.my_suspects, self.my_weapons, self.my_rooms, self.other_players_init)

        # Test that we get empty lists if the input guess is empty
        self.assertEqual(([], []), game.narrow_down_guess([], []))

        # If there's exactly one disprover and one card remaining in the guess, we should
        # get empty lists returned, and the card should be added to the disprover
        guess = ["Mr. Green"]
        disprovers = ["Sarah"]
        self.assertEqual(([], []), game.narrow_down_guess(guess, disprovers))
        self.assertIn(guess[0], game.players[disprovers[0]].has)

        # Test that when we have no information to narrow down the guess, the function
        # just returns the input
        guess = ["Mrs. Peacock", "Lead Pipe", "Fountain"]
        disprovers = ["Susan", "Andy", "Sarah"]
        self.assertEqual((guess, disprovers), game.narrow_down_guess(guess, disprovers))

        # Test that the function successfully narrows down the possibilities to figure out who
        # at least one disprover is. We'll determine that Susan has Mrs. Peacock, and the method
        # should eliminate Susan and Mrs. Peacock from the returned lists.
        game.players["Susan"].does_not_have.append("Lead Pipe")
        game.players["Susan"].does_not_have.append("Fountain")
        guess = ["Mrs. Peacock", "Lead Pipe", "Fountain"]
        disprovers = ["Susan", "Andy", "Sarah"]
        self.assertEqual((["Lead Pipe", "Fountain"], ["Andy", "Sarah"]), game.narrow_down_guess(guess, disprovers))
        self.assertIn("Mrs. Peacock", game.players["Susan"].has)

    def test_remove_known_from_guess(self):
        """Test remove_known_from_guess."""
        # Set up a contrived game with circumstances useful for testing
        game = clueLogic.game()
        game.setup_game(self.my_suspects, self.my_weapons, self.my_rooms, self.other_players_init)
        game.players["Susan"].has.append("Mrs. Peacock")
        game.actual_solution = ["Sgt. Gray", "Studio"]

        # Function should remove something that the guesser has
        guess = ["Mrs. Peacock", "Lead Pipe", "Fountain"]
        self.assertEqual(["Lead Pipe", "Fountain"], game.remove_known_from_guess("Susan", guess))

        # Function should remove one of my cards from the guess
        guess = ["Mrs. Peacock", "Revolver", "Fountain"]
        self.assertEqual(["Mrs. Peacock", "Fountain"], game.remove_known_from_guess("Andy", guess))

        # Function should remove known solution cards from guess
        guess = ["Sgt. Gray", "Lead Pipe", "Studio"]
        self.assertEqual(["Lead Pipe"], game.remove_known_from_guess("Andy", guess))


if __name__ == '__main__':
    unittest.main()