//Polygons
//Author: Eric Berger
//Date: 2/15/2011
//
//Problem structure: Show a regular polygon (or a circle).  Ask the user to identify which type is is

var ExercisePolygons = {
    shapeNames: ["circle", "INVALID", "INVALID", "triangle", "square", "pentagon", "hexagon", "heptagon", "octagon", "enneagon", "decagon", "hendecagon", "dodecagon"],
    shapesToUse: [3, 4, 5, 6, 7, 8, 10, 12],

    init: function(){
        writeText("What kind of polygon is shown below?");
        var numSides = this.shapesToUse.splice(getRandomIntRange(0, this.shapesToUse.length-1), 1);
        var shapeName = this.shapeNames[numSides];
        setCorrectAnswer("`"+shapeName+"`");
        for(var i = 0; i < this.shapesToUse.length; i++){
            addWrongChoice("`"+this.shapeNames[this.shapesToUse[i]]+"`");
        }
        writeStep("How many sides does this shape have?")
        var articleUpper = 'A ';
        var article = 'a ';
        if(shapeName.match(/^[aeiou]/)){
            var articleUpper = 'An ';
            var article = 'an ';
        } 
        writeStep(articleUpper + shapeName + " is a polygon with "+numSides+" sides.");
        writeStep("Since this polygon has "+numSides+" sides, it is "+article+shapeName+".");

        var myPolygon = getRegularPolygon(numSides)
        //var myPolygon = get306090();
        initialObjectsToDraw.push(myPolygon);
    }
}
