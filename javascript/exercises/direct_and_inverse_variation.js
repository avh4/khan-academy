//Direct and Inverse Variation
//Author: Eric Berger
//Date: 1/27/2011
//
//Problem structure: Make a statement (either A and B vary directly or A and B vary inversely), and ask students
//to identify the equation which satisfies this constraint.

var ExerciseDirectAndInverseVariation = {

    //constant values
    VARIABLE_NAMES : [['x', 'y'], ['a', 'b'], ['m', 'n']],

    v1 : "", //first variable, picked from VARIABLE_NAMES
    v2 : "", //second variable, picked from VARIABLE_NAMES
    isDirect : true, //Whether we are looking for direct or for indirect variation
    multiplier: 0, //Multiplier used, to be used for hints
    multiplier_inverse: 0, //Inverse of multiplier, to prevent 1/1/k when it's already a fraction
    
    init: function(){
        var variable_name_index = getRandomIntRange(0, this.VARIABLE_NAMES.length - 1);
        this.v1 = this.VARIABLE_NAMES[variable_name_index][0];
        this.v2 = this.VARIABLE_NAMES[variable_name_index][1];
        this.isDirect = (getRandomIntRange(0, 1) == 1);
        if(getRandomIntRange(0, 1) == 1){  //Decide on integer or fractional multiplier
            this.multiplier = this.getSmallInteger()
            this.multiplier_inverse = "1 / " + this.multiplier
        }
        else{
            this.multiplier_inverse = this.getSmallInteger()
            this.multiplier = "1 / " + this.multiplier_inverse
        }

        this.generateQuestionText();

        if(this.isDirect){
            this.generateDirectAnswersAndHints();
        }
        else{
            this.generateIndirectAnswersAndHints();
        }
    },

    getSmallInteger: function(){
        return getRandomIntRange(2, 9);
    },

    generateQuestionText: function(){
        var possibleStatements = [];
        var hint_text = "";
        if (this.isDirect){
            possibleStatements = [
            "v1 is directly proportional to v2",
            "v1 and v2 vary directly",
            "v1 varies directly with v2",
            "v1 and v2 are in direct variation"]
            hint_text = " if `v1 = k * v2` for some constant k"
        }
        else{
            possibleStatements = [
            "v1 is inversely proportional to v2",
            "v1 and v2 vary inversely",
            "v1 varies inversely with v2",
            "v1 and v2 are in inverse variation"]
            hint_text = " if `v1 = k * 1/v2` for some constant k"
        }
        var statement = possibleStatements[getRandomIntRange(0, possibleStatements.length - 1)]
        var question_text = statement + "<br>Which of these equations could represent the relationship between v1 and v2?"
        writeText(this.replace(question_text))
        writeStep(this.replace(statement + hint_text))
    },

    generateDirectAnswersAndHints: function(){
        var answer_form = getRandomIntRange(0, 2);
        //Canonical form
        if(answer_form == 0){
            writeStep(this.replace("`v1=multiplier*v2` fits this pattern, with `k=multiplier`"))
            setCorrectAnswer(this.replace("v1=multiplier*v2"))
        }

        //a/b = k
        if(answer_form == 1){
            writeStep(this.replace("If you divide each side of this by v2, you get `v1/v2 = k` for some constant k"))
            writeStep(this.replace("`v1/v2=multiplier` fits this pattern, with `k=multiplier`"))
            setCorrectAnswer(this.replace("v1/v2=multiplier"))
        }
        //k * a = b
        if(answer_form == 2){
            writeStep(this.replace("If you divide each side of this by k, you get `1/k * v1 = v2`"))
            writeStep(this.replace("`multiplier * v1 = v2` fits this pattern, with `k = multiplier_inverse`"))
            setCorrectAnswer(this.replace("multiplier * v1 = v2"))
        }
        //Generate wrong answers for direct variation questions
        addWrongChoice(this.replace("v1 * v2 = multiplier"))
        addWrongChoice(this.replace("v1 * v2 = multiplier_inverse"))
        addWrongChoice(this.replace("v1 = multiplier * 1 / v2"))
        addWrongChoice(this.replace("multiplier * v1 = 1 / v2"))
        addWrongChoice(this.replace("multiplier_inverse * v1 = 1 / v2"))
        addWrongChoice(this.replace("multiplier * 1 / v1 = v2"))
        addWrongChoice(this.replace("multiplier_inverse * 1 / v1 = v2"))
        addWrongChoice(this.replace("v1 + v2 = multiplier_inverse"))
        addWrongChoice(this.replace("v1 = multiplier - v2"))
    },

    generateIndirectAnswersAndHints: function(){
        var answer_form = getRandomIntRange(0, 2);
        //Canonical form a = k * 1/b
        if(answer_form == 0){
            writeStep(this.replace("`v1=multiplier*1/v2` fits this pattern, with `k=multiplier`"))
            setCorrectAnswer(this.replace("v1=multiplier*1/v2"))
        }

        //ab = k
        if(answer_form == 1){
            writeStep(this.replace("If you multiply each side of this by v2, you get `v1*v2 = k` for some constant k"))
            writeStep(this.replace("`v1*v2=multiplier` fits this pattern, with `k=multiplier`"))
            setCorrectAnswer(this.replace("v1*v2=multiplier"))
        }
        //k * 1/a = b
        if(answer_form == 2){
            writeStep(this.replace("If you divide each side of this by k, you get `v1 / k = 1/v2`"))
            writeStep(this.replace("Then you can take the inverse of each side, to get `k / v1 = v2`"))
            writeStep(this.replace("`multiplier * 1/v1 = v2` fits this pattern, with `k = multiplier`"))
            setCorrectAnswer(this.replace("multiplier * 1/v1 = v2"))
        }
        //Generate wrong answers for inverse variation questions
        addWrongChoice(this.replace("v1 / v2 = multiplier"))
        addWrongChoice(this.replace("v1 / v2 = multiplier_inverse"))
        addWrongChoice(this.replace("v1 = multiplier * v2"))
        addWrongChoice(this.replace("v1 = multiplier_inverse * v2"))
        addWrongChoice(this.replace("multiplier * v1 = v2"))
        addWrongChoice(this.replace("multiplier_inverse * v1 = v2"))
        addWrongChoice(this.replace("multiplier * 1 / v1 = 1 / v2"))
        addWrongChoice(this.replace("multiplier_inverse * 1 / v1 = 1 / v2"))
        addWrongChoice(this.replace("v1 - v2 = multiplier_inverse"))
        addWrongChoice(this.replace("v1 = multiplier + v2"))
    },

    replace: function(string_in){
        var str = string_in
        str = str.replace(/v1/g, this.v1)
        str = str.replace(/v2/g, this.v2)
        str = str.replace(/multiplier_inverse/g, this.multiplier_inverse)
        str = str.replace(/multiplier/g, this.multiplier)
        return str
    }
}   
