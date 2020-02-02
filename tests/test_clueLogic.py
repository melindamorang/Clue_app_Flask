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
        


if __name__ == '__main__':
    unittest.main()