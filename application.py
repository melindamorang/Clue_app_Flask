from flask import Flask, render_template, request
import clueLogic

app = Flask(__name__)
DEBUG = True
app.config.from_object(__name__)

game = clueLogic.game()

@app.route('/renderMyNotebook')
def renderMyNotebook():
    """Render the detective notebook main game page."""
    return render_template(
        "myNotebook.html",
        suspect_dict=game.detective_notebook["suspects"],
        weapon_dict=game.detective_notebook["weapons"],
        room_dict=game.detective_notebook["rooms"]
        )

@app.route('/')
def index():
    return render_template(
        "index.html",
        suspects=clueLogic.cards["suspects"],
        weapons=clueLogic.cards["weapons"],
        rooms=clueLogic.cards["rooms"]
        )

@app.route('/enterCards', methods=["POST"])
def enterCards():
    # Get player's cards from entry form
    my_suspects = request.form.getlist("suspects")
    my_weapons = request.form.getlist("weapons")
    my_rooms = request.form.getlist("rooms")

    # Get the names of the other players and how many cards they have
    other_players = []
    for i in range(2, 11):
        player_name = request.form.get(f"Player_{i}")
        num_cards = request.form.get(f"num_cards_{i}")
        if player_name and num_cards:
            other_players.append((player_name, num_cards,))

    # Set up the game
    game.setup_game(my_suspects, my_weapons, my_rooms, other_players)

    return renderMyNotebook()

@app.route('/snoop')
def snoop():
    other_players = [player for player in game.players if player != "Me"]
    return render_template(
        "snoop.html",
        players=other_players,
        suspects=[suspect for suspect in clueLogic.cards["suspects"] if suspect not in game.players["Me"].has],
        weapons=[weapon for weapon in clueLogic.cards["weapons"] if weapon not in game.players["Me"].has],
        rooms=[room for room in clueLogic.cards["rooms"] if room not in game.players["Me"].has]
        )

@app.route('/enterSnoop', methods=["POST"])
def enterSnoop():
    # Get the player that was snooped and the card seen
    player = request.form.get("player")
    card = request.form.get("card")
    # Update player info
    game.add_card(player, card)
    # Render notebook
    return renderMyNotebook()

@app.route('/guess')
def guess():
    return render_template(
        "guess.html",
        suspects=clueLogic.cards["suspects"],
        weapons=clueLogic.cards["weapons"],
        rooms=clueLogic.cards["rooms"],
        suspect_dict=game.detective_notebook["suspects"],
        weapon_dict=game.detective_notebook["weapons"],
        room_dict=game.detective_notebook["rooms"]
        )

@app.route('/enterGuess', methods=["POST"])
def enterGuess():
    # Get my entered guess from entry form
    guessed_suspect = request.form.get("guessed_suspect")
    guessed_weapon = request.form.get("guessed_weapon")
    guessed_room = request.form.get("guessed_room")
    # Render page where you can enter disproval
    return render_template(
        "DisproveMyGuess.html",
        guessed_suspect=guessed_suspect,
        guessed_weapon=guessed_weapon,
        guessed_room=guessed_room,
        players=game.players.keys()
        )

@app.route('/enterDisprove', methods=["POST"])
def enterDisprove():
    # Get my entered guess from entry form
    guessed_suspect = request.form.get("guessed_suspect")
    guessed_weapon = request.form.get("guessed_weapon")
    guessed_room = request.form.get("guessed_room")
    disprover_suspect = request.form.get("disprover_suspect")
    disprover_weapon = request.form.get("disprover_weapon")
    disprover_room = request.form.get("disprover_room")

    game.enter_disproval_of_my_guess(
        guessed_suspect, guessed_weapon, guessed_room,
        disprover_suspect, disprover_weapon, disprover_room
    )

    # Render notebook
    return renderMyNotebook()

@app.route('/otherPlayerGuess')
def otherPlayerGuess():
    other_players = [player for player in game.players if player != "Me"]
    return render_template(
        "OtherPlayerGuess.html",
        players=other_players,
        suspects=clueLogic.cards["suspects"],
        weapons=clueLogic.cards["weapons"],
        rooms=clueLogic.cards["rooms"]
        )

@app.route('/enterOtherPlayerGuess', methods=["POST"])
def enterOtherPlayerGuess():
    # Get other player's entered guess and disprovers from entry form
    guesser = request.form.get("guesser")
    guessed_suspect = request.form.get("guessed_suspect")
    guessed_weapon = request.form.get("guessed_weapon")
    guessed_room = request.form.get("guessed_room")
    disprovers = request.form.getlist("disprovers")

    game.enter_other_players_guess(guesser, guessed_suspect, guessed_weapon, guessed_room, disprovers)

    # Render notebook
    return renderMyNotebook()


if __name__ == '__main__':
    app.run(threaded=True)