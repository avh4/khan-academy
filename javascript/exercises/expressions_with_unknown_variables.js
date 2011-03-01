/*
 *
    Expressions with Unknown Variables
    Author: Marcia Lee
    Date: 2011-02-28

    Problem spec: http://www.youtube.com/watch?v=yF6pj4utRt4
    
        If a + b = 5, what is 2a + 2b?
        If a + b = 5 and c - d = 9, what is 4a + 3c - 3d + 4b?
    
    The coefficients are always set to 1 in this exercise.
    If desired, this exercise may be extended to have random coefficients.
    
    The question has either one or two expressions.
    Each expression either has two or three terms.

    The ordering of terms is random.
 *       
 */

function ExpressionsWithUnknownVariablesExercise() {
    var premises = [];
    var variables = ["abc", "xyz"]
    
    this.init = function() {
        generateProblem();
        showProblem();
        generateHints();
        setCorrectAnswer(premises.correct_answer);
    }
    
    function generateProblem() {
        generatePremise();
        if (get_random() > 0)
            generatePremise();
    }
    
    function generatePremise() {
        // p represents premise "x + y = 5" as follows:
        // terms ==> x and y
        // val ==> 5
        // factor ==> the factor by which the premise is multiplied (in the question)
        
        var p = {};
        var terms = generateTerms();
        if (!terms)
            return;
        p.terms = terms;
        p.val = get_random();
        p.factor = get_random();
        
        premises.push(p);
    }
    
    function generateTerms() {
        // t represents term "x" as follows:
        // coefficient ==> 1 (but can be set to get_random() for a challenge)
        // variable ==> x
        
        if (!variables.length)
            return null;
        
        var t = [];
        var v = variables.pop();
        var s = "";
        
        t[0] = {coefficient: 1, variable: v[0]}
        s += format_expression([t[0].coefficient], t[0].variable, noSelColor, true);
        
        t[1] = {coefficient: 1, variable: v[1]}
        s += format_expression([t[1].coefficient], t[1].variable, noSelColor, false);
        
        if (get_random() > 0) {
            t[2] = {coefficient: 1, variable: v[2]}
            s += format_expression([t[2].coefficient], t[2].variable, noSelColor, false);
        }
        
        t.to_s = s;
        return t;
    }
    
    function showProblem() {
        var premise_text = "If " + outputPremise(0);
        for (var i = 1; i < premises.length; i++) {
            premise_text += " and " + outputPremise(i);
        }
        write_text(premise_text);
        
        var conclusion_text = "Then, what is " + outputConclusion() + " ?";
        write_text(conclusion_text)
    }
    
    function outputPremise(i) {
        var p = premises[i];
        return p.terms.to_s + " `=" + p.val + "`";
    }
   
    function outputConclusion() {
        // Collect all terms into one array so that we can shuffle them around.
        var index = 0;
        var all_terms = [];
        var all_terms_string = "";
        
        for (var i = 0; i < premises.length; i++) {
            var p = premises[i];
            var terms = p.terms;
            for (var j = 0; j < terms.length; j++) {
                var t = terms[j];
                var coeff = p.factor * t.coefficient;
                all_terms[index++] = {coefficient: coeff, variable: t.variable}
                all_terms_string += format_expression([coeff], t.variable, noSelColor, i == 0 && j == 0);
            }
        }
        
        premises.to_s = all_terms_string;
        
        var random_indices = randomIndices(all_terms.length);
        var s = "";
        for (var i = 0; i < random_indices.length; i++) {
            var random_index = random_indices[i];
            var t = all_terms[random_index];
            s += format_expression([t.coefficient], t.variable, noSelColor, i == 0);
        }

        return s;
    }
        
    function generateHints() {
        open_left_padding(30);
        
        var unshuffled  = "`=` " + premises.to_s;   // 2a + 2b
        var factored    = "`=` ";                   // 2 (a + b)
        var evaled      = "`=` ";                   // 2 (5)
        var multiplied  = "`=` ";                   // 10
        premises.correct_answer = 0;                // 10
        
        for (var i = 0; i < premises.length; i++) {
            var p = premises[i];
            if (i) {
                factored    += " `+` ";
                evaled      += " `+` ";
                multiplied  += " `+` ";
            }
            factored    += "`(" + p.factor + ") * (`" + p.terms.to_s + "`)`";
            evaled      += "`(" + p.factor + ") * (" + p.val + ")`";
            
            var product = p.factor * p.val
            multiplied += "`(" + product + ")`";
            
            premises.correct_answer += product;
        }
        
        write_step(unshuffled);
        write_step(factored);
        write_step(evaled);
        if (premises.length > 1)
            write_step(multiplied);
        write_step("`= " +  premises.correct_answer + "`");
        
        close_left_padding();
    }
}
