/*
 *
    PeriodicTable Exercises 
    Author: Case Nelson 
    Date: 2011-03-13

    Problem spec: http://www.khanacademy.org/video/orbitals?playlist=Chemistry
        What is the symbol for [element]?
        What period does [element] belong to?
        What is the atomic weight of [element]?
        How many protons does [element] have?
        What group does [element] belong to?
        
        Constraints:
            element -> any element

 */

function PeriodicTable3() {
    var exercise;
    this.init = function() {
        exercise = new OrbitalExercise();
        exercise.init();
        document.write(periodic_table.toHTML());
    }

    this.give_next_hint = function() { 
        periodic_table.highlightElement(exercise.correctElement.symbol);
        exercise.give_next_hint && exercise.give_next_hint();
    }
}

function OrbitalExercise() {
    var correctElement = null;
    var correctOrbital = null;

    this.init = function() {
        // Don't check if answer is numeric
        checkFreeAnswer = checkFreeAnswerString; 
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        var config = correctElement.electron_configuration;
        var allOrbitals = ['s','f','d','p'];
        correctOrbital = getOrbital(config, allOrbitals);

        setCorrectAnswer(correctOrbital);
        addWrongChoice(correctElement.symbol);
        
        for (var i = 0; i < allOrbitals.length; i++) { 
            var orbital = allOrbitals[i];
            if (orbital !== correctOrbital) {
                addWrongChoice(orbital);
            }
        }
    }

    function getOrbital(config, allOrbitals) {
        var highestOrbital = null;
        var shells = config.split(' ')
        for (var i = 0; i < shells.length; i++) {
            var shell = shells[i];

            // Skip parent configuration 
            if (shell.indexOf('[') !== -1){
                continue;
            }

            var orbital = shell.replace(/[0-9]/g, '');
            if (allOrbitals.indexOf(orbital) > allOrbitals.indexOf(highestOrbital)){
                highestOrbital = orbital;
            }
        }
        return highestOrbital;
    }
    
    function showProblem() {
        write_text("Which orbital block does " + correctElement.name + " belong to?");
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("Helium and all elements in groups 1 and 2 are in the s-block.");
        write_step("All elements in groups 13 to 18 except Helium are in the p-block.");
        write_step("All elements in groups 3 to 12 are in the d-block.");
        write_step("All lanthanide and actinide elements are in the f-block.");
        write_step(correctElement.name + " is in the " + correctOrbital + "-block.");
        
        close_left_padding();
    }
}

