from flask import Flask, render_template, request

app = Flask(__name__)
DEBUG = True
app.config.from_object(__name__)

# Master list of suspects in the game
suspects = [
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
]

# Master list of weapons in the game
weapons = [
    "Knife",
    "Candlestick",
    "Revolver",
    "Rope",
    "Lead Pipe",
    "Wrench",
    "Poison",
    "Horseshoe"
]

# Master list of rooms in the game
rooms = [
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

# Players in the current game
players = ["Andy", "Susan", "Sarah", "Maud", "Sandy"]

# My detective notebook, indicating what I know about who has what.
detective_notebook = {
    "suspects": {suspect: "" for suspect in suspects},
    "weapons": {weapon: "" for weapon in weapons},
    "rooms": {room: "" for room in rooms}
}

def renderMyNotebook():
    return render_template(
        "myNotebook.html",
        suspect_dict=detective_notebook["suspects"],
        weapon_dict=detective_notebook["weapons"],
        room_dict=detective_notebook["rooms"]
        )

@app.route('/')
def index():
    return render_template(
        "index.html",
        suspects=suspects,
        weapons=weapons,
        rooms=rooms
        )

@app.route('/enterCards', methods=["POST"])
def enterCards():
    # Get player's cards from entry form
    my_suspects = request.form.getlist("suspects")
    my_weapons = request.form.getlist("weapons")
    my_rooms = request.form.getlist("rooms")
    # Update detective notebook with player's own cards
    for suspect in my_suspects:
        detective_notebook["suspects"][suspect] = "Me"
    for weapon in my_weapons:
        detective_notebook["weapons"][weapon] = "Me"
    for room in my_rooms:
        detective_notebook["rooms"][room] = "Me"
    # Render notebook
    return renderMyNotebook()

@app.route('/snoop')
def snoop():
    return render_template(
        "snoop.html",
        players=players,
        suspects=[suspect for suspect in suspects if detective_notebook["suspects"][suspect] != "Me"],
        weapons=[weapon for weapon in weapons if detective_notebook["weapons"][weapon] != "Me"],
        rooms=[room for room in rooms if detective_notebook["rooms"][room] != "Me"]
        )

@app.route('/enterSnoop', methods=["POST"])
def enterSnoop():
    # Get the player that was snooped and the card seen
    player = request.form.get("player")
    card = request.form.get("card")
    # Update detective notebook with the snoop info
    if card in suspects:
        detective_notebook["suspects"][card] = player
    elif card in weapons:
        detective_notebook["weapons"][card] = player
    elif card in rooms:
        detective_notebook["rooms"][card] = player
    # Render notebook
    return renderMyNotebook()

@app.route('/guess')
def guess():
    return render_template(
        "guess.html",
        suspects=suspects,
        weapons=weapons,
        rooms=rooms,
        suspect_dict=detective_notebook["suspects"],
        weapon_dict=detective_notebook["weapons"],
        room_dict=detective_notebook["rooms"]
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
        players=players
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
    # Enter retrieved information
    if disprover_suspect:
        detective_notebook["suspects"][guessed_suspect] = disprover_suspect
    if disprover_weapon:
        detective_notebook["weapons"][guessed_weapon] = disprover_weapon
    if disprover_room:
        detective_notebook["rooms"][guessed_room] = disprover_room
    # Render notebook
    return renderMyNotebook()


if __name__ == '__main__':
    app.run()