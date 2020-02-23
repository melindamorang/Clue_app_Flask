document.addEventListener('DOMContentLoaded', function (){
    var guesserCombo = document.getElementById("guesserCombo");
    hideGuesserInDisprovers(guesserCombo);
});

function hideGuesserInDisprovers (guesserCombo) {
    // Find the currently-selected guesser name
    var guesser = guesserCombo.value;
    // Get the Disprovers section
    var disproversDiv = document.getElementById("Disprovers");
    // First, show all disprovers
    var disproverSubDivs = disproversDiv.getElementsByClassName("disproverCheckbox");
    for(var i=0, len=disproverSubDivs.length; i<len; i++){
        disproverSubDivs[i].style.display = "inline";
    };
    // Next, hide the current guesser's checkbox only.
    // Find the disprover checkbox div associated with this guesser
    var disproverCheckboxDiv = document.getElementById(guesser + "Checkbox");
    // Get the checkbox itself
    var disproverCheckbox = disproverCheckboxDiv.getElementsByTagName("input")[0];
    // Hide the checkbox and uncheck it
    disproverCheckbox.checked = false;
    disproverCheckboxDiv.style.display = "none";
}