document.addEventListener('DOMContentLoaded', function (){
    showHideDisprovers();
    populateText();
});

function populateText() {
    guessedSuspect = document.getElementById("guessedSuspect").value;
    guessedWeapon = document.getElementById("guessedWeapon").value;
    guessedRoom = document.getElementById("guessedRoom").value;
    document.getElementById("disproverSuspectText").innerHTML = guessedSuspect;
    document.getElementById("disproverWeaponText").innerHTML = guessedWeapon;
    document.getElementById("disproverRoomText").innerHTML = guessedRoom;
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

function validate(){
    // Make sure the user hasn't selected the same disprover for two different cards.
    disproverSelects = document.getElementsByClassName("disprovers")
    disprovers = []
    for(var i=0, len=disproverSelects.length; i<len; i++){
        if (disproverSelects[i].value !== "") {
            disprovers.push(disproverSelects[i].value)
        };
    };
    // Return false if the disprovers array has duplicates
    if ((new Set(disprovers)).size !== disprovers.length) {
        var text = `You can't choose the same disprover twice.`
        document.getElementById("validation").innerHTML = text;
        return false;
    };

};
