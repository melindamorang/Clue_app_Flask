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

class player():
    def __init__(name, num_cards, initial_not_has):
        self.name = name
        self.num_cards = num_cards
        self.has = []
        self.does_not_have = initial_not_has
        self.at_least_one = []

    def add_card(card):
        if card in self.has:
            # We already knew this.
            return
        self.has.append(card)
        # Clean up at_least_ones with this card in it
        for i in range(0, len(self.at_least_one)):
            guess = self.at_least_one[i]  # A guess will have either 2 or 3 cards in it
            if card in guess:
                if set(guess).issubset(set(self.has)):
                    # All remaining cards in the at_least_one guess belong to this player.
                    # We won't get any further info out of this guess, so delete it.
                    del self.at_least_one[i]
        # Since this player has this card, no one else does.
        for plyr in [p for p in players.keys() if p != self.name]:
            plyr.enter_not_has(card)

    def enter_not_has(card):
        """Indicate that a player does not have a certain card.

        Go through logic to see if we can learn anything else from this information.
        """ 
        if card in self.does_not_have:
            # We already knew this.
            return
        self.does_not_have.append(card)
        # Go through prior guesses where we know they had at least one of the cards
        # and see if we can eliminate anything.
        for i in range(0, len(self.at_least_one)):
            guess = self.at_least_one[i]  # A guess will have either 2 or 3 cards in it
            if card in guess:
                guess.remove(card)
                if len(guess) == 1:
                    # We learned something!
                    # The player must have the remaining card in the guess
                    add_card(guess[0])
                    del self.at_least_one[i]
                else:
                    # We narrowed things down. Update at_least_one.
                    self.at_least_one[i] = guess

# Players in the current game
players = {}
me = None

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
    # Initialize myself
    i_not_have = [suspect in suspects if suspect not in my_suspects] + \
        [weapon in weapons if weapon not in my_weapons] + \
            [room for room in rooms if room not in my_rooms]
    me = player("Me", len(my_suspects + my_weapons + my_rooms]), i_not_have)
    # Get the names of the other players and how many cards they have
    for i in range(2, 11):
        player_name = request.form.get(f"Player_{i}")
        num_cards = request.form.get(f"num_cards_{i}")
        if player_name and num_cards:
            # Initialize a player object
            players[player_name] = player(player_name, num_cards, my_suspects + my_weapons + my_rooms)
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
        players=players.keys(),
        suspects=[suspect for suspect in suspects if suspect not in me.has],
        weapons=[weapon for weapon in weapons if weapon not in me.has],
        rooms=[room for room in rooms if room not in me.has]
        )

@app.route('/enterSnoop', methods=["POST"])
def enterSnoop():
    # Get the player that was snooped and the card seen
    player = request.form.get("player")
    card = request.form.get("card")
    # Update player info
    players[player].add_card(card)
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
        players=players.keys()
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
    non_disprover = [p for p in players.keys() if p not in [disprover_suspect, disprover_weapon, disprover_room]]
    # Enter retrieved information
    if disprover_suspect:
        detective_notebook["suspects"][guessed_suspect] = disprover_suspect
        players[disprover_suspect].add_card(guessed_suspect)
    else:
        for player in non_disprover:
            players[player].enter_not_has(guessed_suspect)
    if disprover_weapon:
        detective_notebook["weapons"][guessed_weapon] = disprover_weapon
        players[disprover_weapon].add_card(guessed_weapon)
    else:
        for player in non_disprover:
            players[player].enter_not_has(guessed_weapon)
    if disprover_room:
        detective_notebook["rooms"][guessed_room] = disprover_room
        players[disprover_room].add_card(guessed_room)
    else:
        for player in non_disprover:
            players[player].enter_not_has(guessed_room)
    # Render notebook
    return renderMyNotebook()

@app.route('/otherPlayerGuess')
def otherPlaylerGuess():
    return render_template(
        "OtherPlayerGuess.html",
        players=["Me"] + players.keys(),
        suspects=suspects,
        weapons=weapons,
        rooms=rooms
        )

@app.route('/enterOtherPlayerGuess', methods=["POST"])
def enterOtherPlayerGuess():
    # Get other player's entered guess and disprovers from entry form
    guessed_suspect = request.form.get("guessed_suspect")
    guessed_weapon = request.form.get("guessed_weapon")
    guessed_room = request.form.get("guessed_room")
    disprovers = request.form.get("disprovers").remove("Me")
    non_disprovers = [p for p in players.keys() if p not in disprovers]
    # Enter retrieved information
    guess = [guessed_suspect, guessed_weapon, guessed_room]
    if guessed_suspect in me.has:
        guess.remove(guessed_suspect)
    if guessed_weapon in me.has:
        guess.remove(guessed_weapon)
    if guessed_room in me.has:
        guess.remove(guessed_room)
    ## TODO: Continue here
    # if guess:
    # Render notebook
    return renderMyNotebook()


if __name__ == '__main__':
    app.run()