//Range of a function
//Author: Eric Berger
//Date: 2/2/2011
//
//Problem structure: Show a function.  Ask student to find the range of that function.  As part of the hint, the function will be graphed.

var ExerciseRangeOfAFunction = {
    equation: "",

    plotter: {
        draw: function(){
            ExerciseRangeOfAFunction.plot();
        },
        drawInColor: function(){
            present.stroke = "blue";
            ExerciseRangeOfAFunction.plot();
        }
    },
    
    init: function(){
        this.equation = this.getRandomEquation();
        writeText("What is the range of the following function?");
        writeEquation(this.equation.definition);
        setCorrectAnswer("`" + this.equation.range + "`");
        for(var i = 0; i < this.equation.wrong_answers.length; i++){
            addWrongChoice("`" + this.equation.wrong_answers[i] + "`");
        }
        writeGraphicalHint("Look at the plot of `f(x)`", [this.plotter]);
        for(var i = 0; i < this.equation.hints.length; i++){
            writeStep(this.equation.hints[i]);
        }
        initPlane();
    },

    plot: function(){
        if(this.equation.holes.length == 0){
            present.plot(this.equation.f)
        }
        else{
            //Sort the holes from min to max x
            this.equation.holes.sort(function(a, b){return a[0] - b[0];})
            //Plot each interval between holes

            var epsilon = 0.00001;
            var minx = -10;  //TODO - assumes grid ends ranges X = -10 to 10
            var maxx = 10;
            present.plot(this.equation.f, minx, this.equation.holes[0][0] - epsilon);  //Plot to the first hole.
            present.plot(this.equation.f, this.equation.holes[this.equation.holes.length - 1][0]+ epsilon, maxx);                        //Plot from the last hole.  
            if(this.equation.holes.length > 1){
                for(var i=0; i < this.equation.holes.length - 1; i++){
                    present.plot(this.equation.f, this.holes[i][0] + epsilon, this.holes[i+1] - epsilon)
                }
            }
            
            //Draw the holes themselves
            for(var i=0; i < this.equation.holes.length; i++){
                present.ASdot(this.equation.holes[i], 4, "black", "white")
            }
        }
    },

//Types of equations:
//0 f(x) = ax^2 + b
//1 f(x) = ax + b * (x-c)/(x-c)  (change parameters so that hole is at (c, b)
//2 f(x) = ax^2 + b * (x-c)/(x-c) (creates a hole, but doesn't change the range)
//3 f(x) = a if x>c, b if x<c
//
    getRandomEquation: function(){
        var equation_type = getRandomIntRange(0, 3)
	
//f(x) = a^x + b
        if(equation_type == 0){
            var a = nonZeroRandomInt(-4, 4);
            var b = getRandomIntRange(-2, 2);
            var relationship
            var wrong_relationships
            if(a > 0){
                relationship = "greater than or equal to ";
                wrong_relationships = ["greater than ", "less than ", "less than or equal to ", "except "];
            }
            else{
                relationship = "less than or equal to "
                wrong_relationships = ["greater than ", "less than ", "greater than or equal to ", "except "];
            }
            var wrong_relationship = wrong_relationships[getRandomIntRange(0, wrong_relationships.length - 1)];
            var e = {
                definition: "f(x) = "+format_first_coefficient(a)+"x^2"+format_constant(b),
                range: "Real numbers " + relationship + b,
                wrong_answers: ["Real numbers", "`{"+a+", "+(-a)+"}`", "Real numbers "+wrong_relationship+b, "Real numbers "+wrong_relationship+(a+b)],
                hints: ["`x^2` is always non-negative, so `"+format_first_coefficient(a)+"x^2` will always be "+relationship+"`0`",
                        "`"+format_first_coefficient(a)+"x^2"+format_constant(b)+"` will always be "+relationship+"`"+b+"`",
                        "The range of `f(x)` is all real numbers "+relationship+"`"+b+"`"],
                f: function(x){
                    return a * x * x + b;
                },
                holes: []
            }
        }

//f(x) = ax + b * (x-c)/(x-c)
        if(equation_type == 1){
            var a = nonZeroRandomInt(-4, 4);
            var c = getRandomIntRange(-4, 4);
            var b = getRandomIntRange(-2, 2) - (c * a); //Re-map b so that the hole is always visible on the plot
            var wrong_relationships = ["greater than ", "less than ", "greater than or equal to ", "less than or equal to "];
            var wrong_relationship = wrong_relationships[getRandomIntRange(0, wrong_relationships.length - 1)];
            var e = {
                definition:"f(x) = (("+format_first_coefficient(a)+"x"+format_constant(b)+") * (x"+format_constant(-c)+"))/(x"+format_constant(-c)+")",
                range: "Real numbers except "+(a * c + b),
                wrong_answers: ["Real numbers except " + c, "All real numbers", "Real numbers "+wrong_relationship + (a * c + b), "Real numbers "+wrong_relationship + c],
                hints: ["When `x ne "+c+"`, the `(x"+format_constant(-c)+")` terms cancel, and `f(x) = "+format_first_coefficient(a)+"x"+format_constant(b)+"`",
                        "When `x = "+c+"`, we can't divide by `(x"+format_constant(-c)+")`, so `f(x)` is undefined there",
                        "This means `f(x)` has a hole at `x="+c+"`, where `f(x)` would otherwise be equal to `"+format_first_coefficient(a)+"x"+format_constant(b)+" = "+format_first_coefficient(a)+"("+c+")"+format_constant(b)+"="+(a*c+b)+"`",
                        "This means `f(x)` can never equal `" + (a * c + b) + "`, but except for that hole, `f(x)` can equal all other values.",
                        "The range of `f(x)` is all real numbers except `"+(a * c + b)+"`"],
                f: function(x){
                    return a * x + b;
                },
                holes: [[c, a * c + b]]
            }
        }
//f(x) = ax^2 + b * (x-c)/(x-c)
        if(equation_type == 2){
            var a = nonZeroRandomInt(-3, 3);
	    //c cannot be 0, because if it was, the hole will be at the min/max of the function, so the range will also have a hole.
            var c = nonZeroRandomInt(-2, 2);
            var b = getRandomIntRange(-2, 2) - (a * c * c);
            var relationship
            if(a > 0){
                relationship = "greater than or equal to "
            }
            else{
                relationship = "less than or equal to "
            }
            var e = {
                definition:"f(x) = (("+format_first_coefficient(a)+"x^2"+format_constant(b)+") * (x"+format_constant(-c)+"))/(x"+format_constant(-c)+")",
                range: "Real numbers " + relationship + "`"+b+"`",
                wrong_answers: ["All real numbers", "Real numbers except "+c, "Real numbers "+relationship+b+" except "+c],
                hints: ["When `x ne "+c+"`, the `(x"+format_constant(-c)+")` terms cancel, and `f(x) = "+format_first_coefficient(a)+"x^2"+format_constant(b)+"`",
                        "When `x = "+c+"`, we can't divide by `(x"+format_constant(-c)+")`, so `f(x)` is undefined there",
                        "This means `f(x)` has a hole at `x="+c+"`, where `f(x)` would otherwise be equal to `"+format_first_coefficient(a)+"x^2"+format_constant(b)+" = "+format_first_coefficient(a)+"("+c+"^2)"+format_constant(b)+"="+(a*c*c+b)+"`",
                        "Even though there is a hole at `("+c+", "+(a*c*c+b)+")`, `f("+(-c)+") = "+(a*c*c+b)+"` too, so the range of `f(x)` includes `" + (a*c*c+b) +"`",
                        "`x^2` is always non-negative, so `"+format_first_coefficient(a)+"x^2` will always be "+relationship+"`0`",
                        "`"+format_first_coefficient(a)+"x^2"+format_constant(b)+"` will always be "+relationship+"`"+b+"`",
                        "The range of `f(x)` is all real numbers "+relationship+"`"+b+"`"],

                        
                f: function(x){
                    return a * x * x + b;
                },
                holes: [[c, a * c * c + b]]
            }
        }

//f(x) = a if x>c, b if x<c
        if(equation_type == 3){
            var a = getRandomIntRange(-3, 3);
            var b = getRandomIntRange(-3, 2);
            if(a == b){
                b = b + 1;
            }
            var c = getRandomIntRange(-4, 4);
            var e = { 
                definition:"f(x) = {("+a+",if x<"+c+"),("+b+",if x>="+c+"):}`",
                range: "{"+a+", "+b+"}",
                wrong_answers: ["All real numbers", "Real numbers except "+c, "Real numbers greater than "+c, a],
                hints: ["The only two values `f(x)` can take are "+a+" and "+b,
                        "The range of `f(x)` is `{"+a+", "+b+"}`"],  
                f: function(x){
                    if(x < c){
                        return a;
                    }
                    else{
                        return b;
                    }
                },
                holes: [[c, a]]
            }
        }
        return e;
    }
}
