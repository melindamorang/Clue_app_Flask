import sys
import random
import playRandomGame

num_games = 10000
out_file = r"E:\Code\Clue_app_Flask\tests\random_games_error_log.txt"

for x in range(0, num_games):
    seed = random.randrange(sys.maxsize)
    try:
        game_succeeded = playRandomGame.main(seed)
        if not game_succeeded:
            with open(out_file, "a") as f:
                f.write(f"{seed}\n")
    except Exception as ex:
        msg = str(ex)
        with open(out_file, "a") as f:
            f.write(f"Exception: {msg}; seed: {seed}\n")
        continue

