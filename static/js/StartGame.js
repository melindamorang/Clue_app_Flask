function validate(){

    // Validate other players
    var playerRows = document.getElementsByClassName("other_players");
    var otherPlayerNames = [];
    // Make sure that each entered player also has a number of cards entered.
    for(var i=0, len=playerRows.length; i<len; i++){
        var name = playerRows[i].getElementsByClassName("player_name")[0].value;
        var num_cards = playerRows[i].getElementsByClassName("num_cards")[0].value;
        if (name.length !== 0){
            otherPlayerNames.push(name);
            if (num_cards.length === 0) {
                var text = `Enter the number of cards for each player.`
                document.getElementById("validation").innerHTML = text;
                return false;
            }
        }
    }

    // Make sure that there is at least one additional player.
    if (otherPlayerNames.length === 0){
        var text = `Enter at least one additional player.`
        document.getElementById("validation").innerHTML = text;
        return false;
    }
    // Make sure that no players have the same name.
    if ((new Set(otherPlayerNames)).size !== otherPlayerNames.length){
        var text = `Give each player a unique name.`
        document.getElementById("validation").innerHTML = text;
        return false;
    }
    // Make sure I didn't name a player "Me".
    if (otherPlayerNames.includes("Me")){
        var text = `You cannot name another player "Me".`
        document.getElementById("validation").innerHTML = text;
        return false;
    }

    // Validate number of cards.
    // There are 30 cards in the game, 3 of which are the actual solution.
    // Consequently, the total number of cards in play for each game is 27.
    const totalCards = 27;
  
    // Count my cards (number of checked boxes)
    var myCards = 0;
    var checkboxes = document.getElementsByClassName("my_card_checkbox");
    for(var i=0, len=checkboxes.length; i<len; i++){
        if (checkboxes[i].checked) myCards += 1;
    }
    // Fail if I didn't enter any cards for myself.
    if (myCards === 0) {
        var text = `Enter your cards.`
        document.getElementById("validation").innerHTML = text;
        return false;
    }

    // Count the number of other players' cards.
    var otherPlayerCardsCount = 0;
    var numCards = [myCards];
    var numCardBoxes = document.getElementsByClassName("num_cards");
    for(var i=0, len=numCardBoxes.length; i<len; i++){
        if (numCardBoxes[i].value.length != 0) {
            var num = parseInt(numCardBoxes[i].value);
            otherPlayerCardsCount += num;
            numCards.push(num)
        }
    }

    var cardsInPlay = myCards + otherPlayerCardsCount;

    // Fail if the number of cards in play is less than the total in the game.
    if (cardsInPlay !== totalCards) {
      var text = `The total number of cards must be ${totalCards}.`
      document.getElementById("validation").innerHTML = text;
      return false;
    }

    // Make sure the cards are evenly distributed
    var numPlayers = numCards.length;
    var allowedNumCards = [Math.floor(totalCards / numPlayers), Math.ceil(totalCards / numPlayers)];
    for(var i=0, len=numPlayers; i<len; i++){
        if (!allowedNumCards.includes(numCards[i])){
            var text = `The number of cards is not evenly distributed.`
            document.getElementById("validation").innerHTML = text;
            return false;
        }
    }

};
