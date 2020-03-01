document.addEventListener('DOMContentLoaded', function (){
    showHideDisprovers();
    populateText();
});

function populateText() {
    guessedSuspect = document.getElementById("guessedSuspect").value;
    guessedWeapon = document.getElementById("guessedWeapon").value;
    guessedRoom = document.getElementById("guessedRoom").value;
    document.getElementById("disproverSuspect").innerHTML = guessedSuspect;
    document.getElementById("disproverWeapon").innerHTML = guessedWeapon;
    document.getElementById("disproverRoom").innerHTML = guessedRoom;
}

function showHideDisprovers() {
    var guessCombos = document.getElementsByClassName("guess");
    var disproversDiv = document.getElementById("Disprovers");
    var shouldShow = true;
    for(var i=0, len=guessCombos.length; i<len; i++){
        if (guessCombos[i].value === "") {
            shouldShow = false;
            break;
        };
    };
    populateText();
    showHideElement(disproversDiv, shouldShow);
}

function showHideElement(element, shouldShow) {
    if (shouldShow) element.style.display = "inline";
    else element.style.display = "none";
}