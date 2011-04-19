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

function PeriodicTable2() {
    var exercise;
    this.init = function() {
        var i = getRandomIntRange(0,2);
        if (i === 0) {
            exercise = new ProtonExercise();
        } else if (i == 1) {
            exercise = new AtomicWeightExercise();
        } else if (i == 2) {
            exercise = new SymbolExercise();
        }
        exercise.init();
        document.write(periodic_table.toHTML());
    }

    this.give_next_hint = function() { 
        periodic_table.highlightElement(exercise.correctElement.symbol);
        exercise.give_next_hint && exercise.give_next_hint();
    }
}

function AtomicWeightExercise() {
    var correctElement = null;
    var correctWeight = null;

    this.init = function() {
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }

    this.give_next_hint = function() {
        periodic_table.highlightElementWeight(correctElement.symbol);
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctWeight = correctElement.atomic_weight.toFixed(2);
        setCorrectAnswer(correctWeight);
    }

    function showProblem() {
        write_text("What is the atomic weight of " + correctElement.name + "?");
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("The atomic weight is the average weight of the atoms of an element as measured from a given source.");
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

    this.give_next_hint = function() {
        periodic_table.highlightElementNumber(correctElement.symbol);
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctProton = correctElement.atomic_number;
        setCorrectAnswer(correctProton);
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


function SymbolExercise() {
    var correctElement = null;
    var correctPeriod = null;

    this.init = function() {
        // Don't check if answer is numeric
        checkFreeAnswer = checkFreeAnswerString; 
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }

    this.give_next_hint = function() {
        periodic_table.highlightElementSymbol(correctElement.symbol);
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctSymbol = correctElement.symbol;
        setCorrectAnswer(correctSymbol);
    }

    function showProblem() {
        write_text("What is the symbol for " + correctElement.name + "?");
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("The element's symbol is often one or two letters which act as an abbreviation for the element name.");
        write_step("The symbol is shown prominently in each element of the periodic table.");
        write_step("The symbol for " + correctElement.name + " is " + correctElement.symbol);
        
        close_left_padding();
    }

}
