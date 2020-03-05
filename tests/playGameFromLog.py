import sys
sys.path.insert(1, r'E:\Code\Clue_app_Flask')
import clueLogic

log_file = r"E:\Code\Clue_app_Flask\tests\test_game_log.txt"

with open(log_file, "r") as f:
    log = f.read().splitlines()

game = clueLogic.game()
game.play_game_from_log_text(log)