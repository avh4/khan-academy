/*
 *
    Orbitals 
    Author: Case Nelson 
    Date: 2011-03-13

    Problem spec: http://www.khanacademy.org/video/orbitals?playlist=Chemistry
        Which orbital block does [element] belong to?
        What is the symbol for [element]?
        What period does [element] belong to?
        What is the atomic weight of [element]?
        How many protons does [element] have?
        What group does [element] belong to?
        
        Constraints:
            element -> any element

 */

function IntroToChemistry() {
    var exercise;
    this.init = function() {
        var i = getRandomIntRange(0,5);
        if (i === 0) {
            exercise = new OrbitalExercise();
        } else if (i == 1) {
            exercise = new GroupExercise();
        } else if (i == 2) {
            exercise = new ProtonExercise();
        } else if (i == 3) {
            exercise = new AtomicWeightExercise();
        } else if (i == 4) {
            exercise = new PeriodExercise();
        } else if (i == 5) {
            exercise = new SymbolExercise();
        }
        exercise.init();
        document.write(periodic_table.toHTML());
    }

    this.give_next_hint = function() { 
        periodic_table.highlightElement(exercise.correctElement.symbol);
    }
}

function SymbolExercise() {
    var correctElement = null;
    var correctPeriod = null;

    this.init = function() {
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctSymbol = correctElement.symbol;
        setCorrectAnswer(correctSymbol);
        addWrongChoice(correctElement.atomic_number);
        addWrongChoice(correctElement.symbol);
        addWrongChoice(correctElement.period);
        addWrongChoice(correctElement.atomic_weight.toFixed(2));
       
        for (var i = 1; i <= 2; i++) { 
            var wrongIndex = getRandomIntRange(0,periodic_table.length-1);
            if (correctIndex !== wrongIndex) {
                addWrongChoice(periodic_table.elements[wrongIndex].atomic_number);
                addWrongChoice(periodic_table.elements[wrongIndex].symbol);
            }
        }
    }

    function showProblem() {
        write_text("What is the symbol for " + correctElement.name + "?");
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("The element's symbol is often one or two letters which acts as abbreviation for the element name.");
        write_step("The symbol is shown prominently in each element of the periodic table.");
        write_step("The symbol for " + correctElement.name + " is " + correctElement.symbol);
        
        close_left_padding();
    }

}

function PeriodExercise() {
    var correctElement = null;
    var correctPeriod = null;

    this.init = function() {
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctPeriod = correctElement.period;
        setCorrectAnswer(correctPeriod);
        addWrongChoice(correctElement.atomic_number);
        addWrongChoice(correctElement.symbol);
        addWrongChoice(correctElement.atomic_number);
        addWrongChoice(correctElement.atomic_weight.toFixed(2));
       
        for (var i = 1; i <= 7; i++) { 
            if (i !== correctPeriod) {
                addWrongChoice(i);
            }
        }
    }

    function showProblem() {
        write_text("Which period does " + correctElement.name + " belong to?");
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("The period can be determined by counting the rows in the top table.");
        write_step("Lanthanide elements are in period 6 and actinide elements are in period 7.");
        write_step(correctElement.name + " is in period " + correctElement.period);
        
        close_left_padding();
    }

}

function AtomicWeightExercise() {
    var correctElement = null;
    var correctProton = null;

    this.init = function() {
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }


    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctWeight = correctElement.atomic_weight.toFixed(2);
        setCorrectAnswer(correctWeight);
        addWrongChoice(correctElement.atomic_number);
        addWrongChoice(correctElement.symbol);
        addWrongChoice(correctElement.period);
       
        for (var i = 1; i <= 5; i++) { 
            var wrongIndex = getRandomIntRange(0,periodic_table.length-1);
            if (correctIndex !== wrongIndex) {
                addWrongChoice(periodic_table.elements[wrongIndex].atomic_weight.toFixed(2));
            }
        }
    }

    function showProblem() {
        write_text("What is the atomic weight of " + correctElement.name + "?");
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("The atomic weight is the average atomic mass unit of an element.");
        write_step("You can see the atomic weight listed on the bottom of the element in the periodic table.");
        write_step(correctElement.name + " has an atomic weight of " + correctWeight + ".");
        
        close_left_padding();
    }
    
}

function ProtonExercise() {
    var correctElement = null;
    var correctProton = null;

    this.init = function() {
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctProton = correctElement.atomic_number;
        setCorrectAnswer(correctProton);
        addWrongChoice(correctElement.atomic_weight.toFixed(2));
        addWrongChoice(correctElement.symbol);
        addWrongChoice(correctElement.period);
       
        for (var i = 1; i <= 5; i++) { 
            var wrongIndex = getRandomIntRange(0,periodic_table.length-1);
            if (correctIndex !== wrongIndex) {
                addWrongChoice(periodic_table.elements[wrongIndex].atomic_number);
            }
        }
    }

    function showProblem() {
        write_text("How many protons does " + correctElement.name + " have?");
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("The number of protons is the most prominent number displayed for each element of the periodic table.");
        write_step(correctElement.name + " has " + correctElement.atomic_number + " protons.");
        
        close_left_padding();
    }
}

function GroupExercise() {
    var correctElement = null;
    var correctGroup = null;

    this.init = function() {
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctGroup = correctElement.group || 'No Group';
        setCorrectAnswer(correctGroup);
        addWrongChoice(correctElement.atomic_number);
        addWrongChoice(correctElement.symbol);
        addWrongChoice(correctElement.period);
        addWrongChoice(correctElement.atomic_weight.toFixed(2));
       
        if (correctGroup !== 'No Group') {
            addWrongChoice('No Group');
        }

        for (var i = 1; i <= 18; i++) { 
            if (i !== correctGroup) {
                addWrongChoice(i);
            }
        }
    }

    function showProblem() {
        write_text("Which group does " + correctElement.name + " belong to?");
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("The group can be determined by counting the columns in the top table.");
        write_step("Lanthanide or actinide elements in the bottom table do not belong to a group.");
        write_step(correctElement.name + " is in group " + correctElement.group);
        
        close_left_padding();
    }
}

function OrbitalExercise() {
    var correctElement = null;
    var correctOrbital = null;

    this.init = function() {
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

