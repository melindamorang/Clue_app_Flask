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


if __name__ == '__main__':
    unittest.main()