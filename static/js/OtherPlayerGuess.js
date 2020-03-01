document.addEventListener('DOMContentLoaded', function (){
    var guesserCombo = document.getElementById("guesserCombo");
    showHideGuess(guesserCombo);
    showHideDisprovers();
    hideGuesserInDisprovers(guesserCombo);
});

function hideGuesserInDisprovers (guesserCombo, disproversDiv) {
    var guesser = guesserCombo.value;
    // First, show all disprovers
    var disproversDiv = document.getElementById("Disprovers");
    var disproverSubDivs = disproversDiv.getElementsByClassName("disproverCheckbox");
    for(var i=0, len=disproverSubDivs.length; i<len; i++){
        showHideElement(disproverSubDivs[i], true);
    };
    // If no guesser has been chosen, don't do anything else.
    if (guesser !== "") {
        // Next, hide the current guesser's checkbox only.
        // Find the disprover checkbox div associated with this guesser
        var disproverCheckboxDiv = document.getElementById(guesser + "Checkbox");
        // Get the checkbox itself
        var disproverCheckbox = disproverCheckboxDiv.getElementsByTagName("input")[0];
        // Hide the checkbox and uncheck it
        disproverCheckbox.checked = false;
        showHideElement(disproverCheckboxDiv, false);
    };
}

function showHideGuess(guesserCombo) {
    var guesser = guesserCombo.value;
    var guessDiv = document.getElementById("Guess");
    if (guesser === "") showHideElement(guessDiv, false);
    else showHideElement(guessDiv, true);
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
    showHideElement(disproversDiv, shouldShow);
}

function showHideElement(element, shouldShow) {
    if (shouldShow) element.style.display = "inline";
    else element.style.display = "none";
}