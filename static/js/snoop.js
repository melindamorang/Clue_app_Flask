document.addEventListener('DOMContentLoaded', function (){
    var playerCombo = document.getElementById("playerCombo");
    showHideCardCombo(playerCombo);
});

function showHideCardCombo(playerCombo) {
    var player = playerCombo.value;
    var cardDiv = document.getElementById("snoopedCard");
    if (player === "") cardDiv.style.display = "none";
    else cardDiv.style.display = "inline";
}
