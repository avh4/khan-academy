// Line relationships
// Author: Omar Rizwan
// Date: 2011-01-21
//
// Problem spec:
// http://www.youtube.com/watch?v=iiStki6QVCM
//
// Problem layout:
// You are given 2 lines' equations.
// You have to determine whether the lines are parallel, perpendicular,
// the same, or none of these. 
//

var LineRelationshipsExercise = {
    RELATIONSHIPS: ['Parallel', 'Perpendicular', 'Same line', 'None of the others'],
    line1: {},
    line2: {},
    
    problemTypes: {
	'Parallel': function(exc) {
	    do {
		exc.line1 = exc.calculateLine(
		    nonZeroRandomInt(1, 9),
		    nonZeroRandomInt(-9, 9),
		    nonZeroRandomInt(-20, 20)
		);
		
		// The ratio between a and b must remain the same to get a parallel line
		// TODO: Generate more diverse a and b values
		var multiplier = nonZeroRandomInt(1, 5);
		exc.line2 = exc.calculateLine(
		    exc.line1.a * multiplier,
		    exc.line1.b * multiplier,
		    nonZeroRandomInt(-20, 20)
		);
	    } while (exc.identifyRelationship(exc.line1, exc.line2) != 'Parallel');

	    exc.writeLineInfo();

	    writeStep('The first line has slope <span class="line1">`'+exc.line1.dSlope+'`</span>, and the second line has the same slope of <span class="line2">`'+exc.line2.dSlope+'`</span>. Since the two lines have different y-intercepts but the same slope, they are <em>parallel</em>.');
	},

	'Perpendicular': function(exc) {
	    do {
		exc.line1 = exc.calculateLine(
		    nonZeroRandomInt(1, 9),
		    nonZeroRandomInt(-9, 9),
		    nonZeroRandomInt(-20, 20)
		);
		var multiplier = nonZeroRandomInt(1, 2);
		if (exc.line1.b < 0) {
		    exc.line2 = exc.calculateLine(
			exc.line1.b * multiplier,
			exc.line1.a * multiplier * -1,
			nonZeroRandomInt(-20, 20)
		    );
		} else {
		    exc.line2 = exc.calculateLine(
			exc.line1.b * multiplier * -1,
			exc.line1.a * multiplier,
			nonZeroRandomInt(-20, 20)
		    );
		}
	    } while (exc.identifyRelationship(exc.line1, exc.line2) != 'Perpendicular');

	    exc.writeLineInfo();

	    writeStep('The first line\'s slope <span class="line1">`'+exc.line1.dSlope+'`</span> is the negative inverse of the second line\'s slope <span class="line2">`'+exc.line2.dSlope+'`</span>. That means the lines are <em>perpendicular</em>.');
	},

	'Same line': function(exc) {
	    do {
		exc.line1 = exc.calculateLine(
		    nonZeroRandomInt(1, 9),
		    nonZeroRandomInt(-9, 9),
		    nonZeroRandomInt(-20, 20)
		);
		var multiplier = nonZeroRandomInt(2, 4);
		exc.line2 = exc.calculateLine(
		    exc.line1.a * multiplier,
		    exc.line1.b * multiplier,
		    exc.line1.c * multiplier
		);
	    } while (exc.identifyRelationship(exc.line1, exc.line2) != 'Same line');

	    exc.writeLineInfo();

	    writeStep('The first line\'s slope <span class="line1">`'+exc.line1.dSlope+'`</span> is equal to the second line\'s slope <span class="line2">`'+exc.line2.dSlope+'`</span>. Also, the first line\'s y-intercept <span class="line1">`'+exc.line1.dYInt+'`</span> is equal to the second line\'s y-intercept <span class="line2">`'+exc.line2.dYInt+'`</span>. That means the lines are <em>the same line</em>!');
	},

	'None of the others': function(exc) {
	    do {
		exc.line1 = exc.calculateLine(
		    nonZeroRandomInt(1, 9),
		    nonZeroRandomInt(-9, 9),
		    nonZeroRandomInt(-20, 20)
		);

		var multiplier = nonZeroRandomInt(1, 2);
		// TODO: more variants for line2
		randomMember([
		    function() {
			exc.line2 = exc.calculateLine(
			    exc.line1.b * multiplier,
			    exc.line1.a * multiplier,
			    nonZeroRandomInt(-20, 20)
			);
		    },

		    function() {
			exc.line2 = exc.calculateLine(
			    exc.line1.a * nonZeroRandomInt(2, 5),
			    exc.line1.b * nonZeroRandomInt(-2, -5),
			    nonZeroRandomInt(-20, 20)
			);
		    },

		    function() {
			exc.line2 = exc.calculateLine(
			    nonZeroRandomInt(-9, 9),
			    nonZeroRandomInt(-9, 9),
			    nonZeroRandomInt(-20, 20)
			);
		    }
		])();
	    } while (exc.identifyRelationship(exc.line1, exc.line2) != 'None of the others');

	    exc.writeLineInfo();
	    writeStep('The first line has slope <span class="line1">`'+exc.line1.dSlope+'`</span>, and the second line has a different slope, <span class="line2">`'+exc.line2.dSlope+'`</span>. These slopes are different, and they are not negative inverses of each other, so the lines don\'t have any of the listed relationships.');
	},
    },
    
    identifyRelationship: function(line1, line2) {
	// Ensure that we don't get randomly generated lines which
	// match an unintended answer ("none of the above" ending up having a
	// relationship, for example)

	if (line1.dSlope == line2.dSlope) {
	    // parallel or same line
	    if (line1.dYInt == line2.dYInt) {
		return 'Same line';
	    } else {
		return 'Parallel';
	    }
	} else {
	    // perpendicular or no relationship
	    if (line1.dSlope == format_fraction(line2.b, line2.a)) {
		return 'Perpendicular';
	    } else {
		return 'None of the others';
	    }
	}
    },

    calculateLine: function(a, b, c) {
	var line = {
	    a: a,
	    b: b,
	    c: c,

	    dSlope: formatFraction(-1*a, b),
	    slope: -1*a/b,

	    dYInt: formatFraction(c, b),
	    yInt: c/b
	};

	line.standard = formatFirstCoefficient(a)+'x '+formatCoefficient(b)+'y = '+c;
	line.slopeInt = 'y = '+line.dSlope+'x '+formatFractionWithSign(c, b);
	return line;
    },

    slopeInterceptHint: function(line, n) {
	return '<p>Putting equation '+n+' in `y = mx + b` form gives:</p>' +
	    '<div class="line'+n+'"><p>`'+line.standard+'`</p>' +
	    '<p>`'+formatFirstCoefficient(line.b)+'y = '+formatFirstCoefficient(-1*line.a)+'x'+formatConstant(line.c)+'`</p>' +
	    '<p>`'+line.slopeInt+'`</p></div>';
    },

    writeLineInfo: function() {
	if (getRandomIntRange(0, 1) == 1) {
	    // let's scramble line1 and line2 just to make the
	    // problem generator less predictable
	    var line = this.line1;
	    this.line1 = this.line2;
	    this.line2 = line;
	}
	writeText('<div class="line1">`'+this.line1.standard+'`</div>');
	writeText('<div class="line2">`'+this.line2.standard+'`</div>');

	writeStep(this.slopeInterceptHint(this.line1, 1));
	writeStep(this.slopeInterceptHint(this.line2, 2));
    },

    init: function() {
	var relationship = randomMember(this.RELATIONSHIPS);

	writeText("What is the relationship of the lines that represent these two equations?");

	this.problemTypes[relationship](this);
	setCorrectAnswer('`'+relationship+'`');

	for (var i = 0; i < this.RELATIONSHIPS.length; i++) {
	    addWrongChoice('`'+this.RELATIONSHIPS[i]+'`');
	}
    },

    drawNextStep: function() {
	if (Exercise.steps_given == 0) { // plot the first line
	    present.stroke = 'blue';
	    present.plot(this.line1.slopeInt);
	} else if (Exercise.steps_given == 1) { // plot the second line
	    present.stroke = 'red';
	    present.plot(this.line2.slopeInt);
	}
	give_next_step();
    }
}