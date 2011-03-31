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

function PeriodicTable1() {
    var exercise;
    this.init = function() {
        var i = getRandomIntRange(0,1);
        if (i === 0) {
            exercise = new PeriodExercise();
        } else if (i == 1) {
            exercise = new GroupExercise();
        }
        exercise.init();
        document.write(periodic_table.toHTML());
    }

    this.give_next_hint = function() { 
        periodic_table.highlightElement(exercise.correctElement.symbol);
        exercise.give_next_hint && exercise.give_next_hint();
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

    this.give_next_hint = function() {
        periodic_table.highlightPeriod(correctPeriod);
    }

    function generateProblem() {
        var correctIndex = getRandomIntRange(0,periodic_table.length-1);
        correctElement = periodic_table.elements[correctIndex];
        correctPeriod = correctElement.period;
        setCorrectAnswer(correctPeriod);
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
function GroupExercise() {
    var correctElement = null;
    var correctGroup = null;

    this.init = function() {
        generateProblem();
        showProblem();
        generateHints();
        this.correctElement = correctElement;
    }

    this.give_next_hint = function() {
        periodic_table.highlightGroup(correctGroup);
    }

    function generateProblem() {
        while (!correctGroup) {
            var correctIndex = getRandomIntRange(0,periodic_table.length-1);
            correctElement = periodic_table.elements[correctIndex];
            correctGroup = correctElement.group;
        }
        setCorrectAnswer(correctGroup);
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

