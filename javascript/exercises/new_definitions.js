//New Operator Definitions (code for exercises new_definitions_1 and new_definitions_2)
//Author: Eric Berger
//Date: 1/28/2011
//
//Problem structure: Define some new operators, present students with an expression that uses them, and ask them to evaluate it.

var ExerciseNewDefinitions = {
    symbols: ["ox", "oplus", "odot"],
    definitions: ["k * x + y", "k * x - y", "x + k * y", "x - k * y", "(x + y) / 2", "x * (y - 1)", "x * (x - y)", "x * y - k", "k * (x - y)", "x - k"],

    getRandomOperator: function(){
        var definition = this.definitions.splice(getRandomIntRange(0, this.definitions.length - 1), 1)[0].replace(/k/g, getRandomIntRange(2, 6));
        var symbol = this.symbols.splice(getRandomIntRange(0, this.symbols.length - 1), 1)[0];
        var operator = ExerciseNewDefinitions.Operator(symbol, definition);
        return operator;
    },

    init_level_2: function(){
        var Operator1 = this.getRandomOperator();
        var Operator2 = this.getRandomOperator();

        writeText("Given that " + Operator1.define());
        writeText("and that " + Operator2.define());

        var structure = getRandomIntRange(0, 2); //Until we test this with kids, I have worries about the number of parenthesis involved in the bigger problems
        //Also, ranges here are changed to have generally more positive than negative numbers in the equations
        if(structure == 0){
            var a = Operator1.init(ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-5, 5)), ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 5)));
            var b = Operator2.init(ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 5)), ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-5, 5)));
            var expression = Operator2.init(a, b);
        }
        if(structure == 1){
            var a = Operator1.init(ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-5, 5)), ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 5)));
            var b = Operator2.init(a, ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 5)));
            var expression = Operator1.init(b, ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, -5)));
        }
        if(structure == 2){
            var a = Operator1.init(ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 5)), ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-5, 5)));
            var b = Operator1.init(ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 5)), a);
            var expression = Operator2.init(b, ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-5, -5)));
        }
        if(structure == 3){
            //Crazy problem = THREE OPERATORS !!!
            var Operator3 = this.getRandomOperator();
            writeText("and that " + Operator3.define());

            var a = Operator1.init(ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 3)), ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-2, 2)));
            var b = Operator2.init(ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 3)), ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 3)));
            var c = Operator3.init(a, ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-2, 2)));
            var d = Operator2.init(b, c);
            var expression = Operator1.init(d, ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(0, 3)));
        }

        this.displayQuestion(expression);
    },

    init_level_1: function(){
        //Define operators (currently hard-coded)
        Operator1 = this.getRandomOperator();

        writeText("Given that " + Operator1.define());

        //Ask a question using the new operator
        var a = Operator1.init(ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-5, 5)), ExerciseNewDefinitions.ConstantExpression(nonZeroRandomInt(-5, 5)));
        this.displayQuestion(a);
    },
    
    displayQuestion: function(expression){
        writeText("Evaluate this expression:" + expression.print(true, false));

        //Generate set of hints that shows how we get there
        expression.generateHints();

        var rightAnswer = expression.evaluate();
        setCorrectAnswer(rightAnswer.toString());
        var possibleAnswers = expression.evaluatePossibleAnswers();
        
        //Rely on existing code to de-duplicate and remove correct answer
        for(var i in possibleAnswers){
            addWrongChoice(possibleAnswers[i].toString());
        } 
    },

    //TODO - this is currently hard-coded to binary operators, since that's all we're doing in the current system (and all that ASCIIMathML supports well, as far as I can find)
    Operator: function(symbol, definition){
        var op = {
            symbol:symbol,
            definition:definition,

            init: function(x, y){
                return ExerciseNewDefinitions.BinaryExpression(this.symbol, this.definition, x, y);
            },

            define: function(){
                return "`x"+this.symbol+"y="+this.definition+"`";
            }
        }
        return op;
    },

    BinaryExpression: function(symbol_in, definition_in, x, y){
        var c = {
            op1: x,
            op2: y,
            symbol: symbol_in,
            definition: definition_in,

            print: function(toplevel, reduce_operands){
                var guts = "";
                if(reduce_operands){
                    //Use ExerciseNewDefinitions.ConstantExpression to get consistent formatting, parenthesis around negatives, etc.
                    op1str = ExerciseNewDefinitions.ConstantExpression(this.op1.evaluate()).print(false, false);
                    op2str = ExerciseNewDefinitions.ConstantExpression(this.op2.evaluate()).print(false, false);
                    guts = op1str + this.symbol + op2str;
                }
                else{
                    guts = this.op1.print(false, false) + this.symbol + this.op2.print(false, false);
                }

                if(toplevel){
                    return "`" + guts + "`";
                }
                else{
                    return "(" + guts + ")";
                }
            },

            getEvalString: function(){
                //Use constant expression to get consistent parenthesizing of negatives, etc.
                var op1str = ExerciseNewDefinitions.ConstantExpression(this.op1.evaluate()).print(false, false);
                var op2str = ExerciseNewDefinitions.ConstantExpression(this.op2.evaluate()).print(false, false);
                    
                var eval_string = this.definition.replace(/x/g, op1str);
                eval_string = eval_string.replace(/y/g, op2str);
                return eval_string;
            },
        
            evaluate: function(){
                return eval(this.getEvalString());
            },

            evaluatePossibleAnswers: function(){
                //Generate 5 possible answers (likely including correct answer)
                var op1_options = this.op1.evaluatePossibleAnswers();
                var op2_options = this.op2.evaluatePossibleAnswers();
                //writeText("Generated options for both operands");
                //writeText("op1:" + op1_options + "  op2:" + op2_options);
                var answers = [];
                while(answers.length < 8){
                    //Pick random choice from each operand
                    var x = op1_options[getRandomIntRange(0, op1_options.length-1)];
                    var y = op2_options[getRandomIntRange(0, op2_options.length-1)];
                    //Switch operands with each-other 25 percent of the time
                    if(getRandomIntRange(0, 3) == 0){
                        var tmp = x;
                        x = y;
                        y = tmp;
                    }
                    var eval_string = this.definition.replace(/x/g, x.toString());
                    eval_string = eval_string.replace(/y/g, y.toString());
                    var answer = eval(eval_string);
                    answers.push(eval(answer));  //TODO - It would be nice to deduplicate this list here, but that adds the possibility of infinite loops if e.g. both operands are 0, the function is x * y, and there are only three unique answers that will ever be generated.  Skipping for now and doing de-duplication where the answers are displayed.
                }
                return answers;
            },

            generateHints: function(){
                //Reduce operands
                var operands_reduced = false;
                operands_reduced |= this.op1.generateHints();
                operands_reduced |= this.op2.generateHints();

                var first_hint_term = "";
                if(operands_reduced){
                    writeStep("So " + this.print(true, false) + " is equivalent to " + this.print(true, true));
                    first_hint_term = this.print(true, false) + "`=" + this.print(true, true) + "`<br>";
                }
                else{
                    first_hint_term = "";
                }
                writeStep("Substitute " + this.print(true, true) + " into the definition of `"+ this.symbol + "` with `x = "+this.op1.evaluate()+"` and `y="+this.op2.evaluate()+"`");
                //writeStep("<center>"+first_hint_term+"=`" + this.definition + "`<br>" + first_hint_term+"=`"+ this.getEvalString() + " = " + this.evaluate() + "`</center>");
                writeStep("<center>" + first_hint_term + this.print(true, false) + "`=" + this.definition + "`</center>")
                writeStep("<center>" + this.print(true, false) + "`=" + this.getEvalString() + "`</center>")
                writeStep("<center>" + this.print(true, false) + "`=" + this.evaluate() + "`</center>")


                return true
            }
        }
        return c;
    },

    ConstantExpression: function(x){
        var c = {
            value: x,

            print: function(toplevel, reduce_operands){
                if(toplevel)
                    return "`"+x+"`";
                else{
                    if(x >= 0){
                        return x.toString();
                    }
                    if(x < 0){
                        return("(" + x.toString() + ")");
                    }
                }

            },

            evaluate: function(){
                return x;
            },

            generateHints: function(){
                return false;
            },

            //Generate wrong answers by walking up tree    
            evaluatePossibleAnswers: function(){
                return [x, x, x, -x, x+1, x-1]; //Bias towards getting each individual operand right
            }
        }
        return c ;
    }
}
