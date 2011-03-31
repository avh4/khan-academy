function RiemannSumsExercise() {
    var curExp;
    var curFunc;

    var startX;
    var endX;

    var dx;
    var divs;

    var sumType;

    function getCoefficient() {
	// For reasonably scaled functions
	var lcoef = nonZeroRandomInt(-3, 3);
	return lcoef;
    }

    function generateExpression() {
	return randomMember([ // curExp = '2x + 3', for example
	    function() {
		// polynomial
		var lcoef = getCoefficient();
		var pwr = getRandomIntRange(2, 3);
		var xcoef = getRandomIntRange(-3,3);

		return lcoef + 'x^' + pwr + formatCoefficient(xcoef) + 'x';
	    },

	    function() {
		// diagonal line
		var lcoef = getCoefficient();
		
		return lcoef + 'x';
	    },

	    function() {
		var icoef = format_fraction_first_coefficient(1, getRandomIntRange(1, 3));
		return 'ln('+icoef+'x)';
	    },

	    function() {
		// sin x + ax 
		var lcoef = getCoefficient();
		var xcoef = getRandomIntRange(-2,2);
		
		return lcoef + 'sin(x)' + formatCoefficient(xcoef) + 'x';
	    },

	    function() {
		// horizontal line
		var cons = getRandomIntRange(-3,3);
		
		return cons;
	    },

	    function() {
		// acos x
		var lcoef = getCoefficient();
		
		return lcoef + 'cos(x)';
	    },

	    function() {
		// abs(x)
		var lcoef = getCoefficient();
		var cons = getCoefficient();
		
		return lcoef + 'abs(x)' + formatConstant(cons);
	    },

	    function() {
		// ax^2 + c
		var lcoef = getCoefficient();
		var cons = getRandomIntRange(-5,5);
		
		return '1/(' + lcoef + ')x^2' + formatConstant(cons);
	    },

	    function() {
		// shifted polynomial
		var ocoef = getCoefficient();
		var icons = getCoefficient();
		var pwr = getRandomIntRange(2, 3);
		var xcoef = getRandomIntRange(-3,3);
		var ocons = getRandomIntRange(-3,3)
		
		return ocoef + '(x+' + icons + ')^' + pwr + formatCoefficient(xcoef) + 'x' + formatConstant(ocons);
	    },

	    function() {
		// shifted even-order polynomial
		var ocoef = getCoefficient();
		var icons = getCoefficient();
		var ocons = getRandomIntRange(-3,3);
		
		return ocoef + '(x+' + icons + ')^2' + formatConstant(ocons);
	    }
	])();
    }

    function generateProblem() {
	startX = 0;
	endX = 10;

	dx = 2;
	divs = (endX - startX) / dx;

	sumType = 'left-hand';//randomMember(['left-hand', 'right-hand', 'middle']);
	
	write_text('Estimate the area under the curve of `f(x)` from `x='+startX+'` to `x='+endX+'`.');
	write_text('Use a '+sumType+' Riemann sum ' +
		   randomMember(['with '+divs+' subdivisions.',
				 'with `Delta x = '+dx+'`.']));
	
	setCorrectAnswer(1);
    }

    function generateHints() {
	write_step('The area we want, `x='+startX+'` to `x='+endX+'`, has a total width of `'+(endX-startX)+'`.');
	write_step('We have to divide it into '+divs+' rectangular subdivisions. Each will have a width of '+dx+'.');
	
    }

    this.init = function() {
	curExp = generateExpression();
	curFunc = functionFrom(curExp);

	write_text('`f(x) = '+curExp+'`');

	generateProblem();
	generateHints();
    };

    this.graphUpdate = function() {
	initPlane();
	
	present.stroke="red";
	present.fontstyle="italic";
	present.fontfill="orange";
	present.fontstroke="none";
	present.fontsize="20";
	
	// plot original function
	present.plot(curExp);
    };

    this.nextStep = function() {
	if (steps_given == 1) {
	    // Draw the subdivisions
	    present.stroke = "black";
	    present.fill = "red";
	    
	    // Note: curX is x of the beginning of the subdivision
	    // height is whatever the height of the subdivision is
	    var height;
	    var div;
	    for (var curX = startX; curX < endX; curX += dx) {
		if (sumType === 'left-hand') {
		    height = curFunc(curX);
		} else if (sumType === 'right-hand') {
		    height = curFunc(curX+dx);
		} else if (sumType === 'middle') {
		    height = curFunc(curX + dx/2);
		}

		if (height > 0) {
		    div = present.rect([curX, 0], [curX+dx, height]);
		} else {
		    // can't have negative heights or widths for rect()
		    div = present.rect([curX, height], [curX+dx, 0]);
		}

		div.attr('opacity', 0.5);
	    }
	}
	give_next_step();
    };
}