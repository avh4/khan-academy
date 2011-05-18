trigFuncs = ["sin", "cos", "tan"];
dTrigFuncdx = {
	"sin": "cos",
	"cos": "-sin",
	"tan": "sec^2"
	};

function generateFunction(x)
{
    // Generate a differentiable expression object
    // {fofx, dfofx, wrongs}
    // x being the name of the variable we differentiate with respect to
    // ensure that the function isn't just 0 as well
    var f = funcGens[getRandomInt(funcGens.length-1)](x);
    while (f.fofx === '0') {
    	f = funcGens[getRandomInt(funcGens.length-1)](x);
    }
    return f;
}

function polyCoefs(low_deg, high_deg)
{
	var coefs = [];
	for (var i = high_deg; i >= low_deg; i--) {
		coefs[i] = getRandomIntRange(-7, 7);
	}
	return coefs;
}

function polyExp(low_deg, high_deg, coefs, x)
{
	if (!x) x = 'x';
	var fofx = '';
	
	for (var i = high_deg; i >= low_deg; i--) {
		var coef = coefs[i];
		
        if (coef != 0) {
            if (i == 0) { // constant
            	fofx = fofx + ' + ' + coef;
            } else if (i == 1) { // x^1
                fofx = fofx + ' + ' + coef + x;
            } else { // x^power
                fofx = fofx + ' + ' + coef + x + '^' + i;
            }
        }
    }

    fofx = cleanExp(fofx, x);
    if (fofx == '') {
       fofx = '0';
    }
    return fofx;
}

function dPolydx(low_deg, high_deg, coefs, x)
{
	if (!x) x = 'x';
	var dfofx = '';
	
	for (var i = high_deg; i >= low_deg; i--) {
		var coef = coefs[i];
		
        if (coef != 0) {
            if (i == 0) { // constant
            	// derivative is 0
            } else if (i == 1) { // nx^1 -> n
                dfofx = dfofx + ' + ' + (coef*i);
            } else if (i == 2) { // nx^2 -> 2nx
                dfofx = dfofx + ' + ' + (coef*2) + x;
            } else { // nx^i -> i*nx^(i-1)
                dfofx = dfofx + ' + ' + (coef*i) + x + '^' + (i-1);
            }
        }
    }
	
    return cleanExp(dfofx, x);
}

function dPolydx_wrong1(low_deg, high_deg, coefs)
{
	// doesn't decrement exponents
	if (!x) x = 'x';
	var dfofx = '';
	
	for (var i = high_deg; i >= low_deg; i--) {
		var coef = coefs[i];
		
        if (coef != 0) {
            if (i == 0) { // constant
            	dfofx = dfofx + ' + ' + coef;
            } else if (i == 1) { // nx -> nx
                dfofx = dfofx + ' + ' + (coef*i) + x;
            } else if (i == 2) { // nx^2 -> 2nx^2
                dfofx = dfofx + ' + ' + (coef*2) + x + '^2';
            } else { // nx^i -> i*nx^i
                dfofx = dfofx + ' + ' + (coef*i) + x + '^' + i;
            }
        }
    }
	
    return cleanExp(dfofx, x);
}

function dPolydx_wrong2(low_deg, high_deg, coefs, x)
{
	// increments negative exponents
	if (!x) x = 'x';
	var dfofx = '';
	
	for (var i = high_deg; i >= low_deg; i--) {
		var coef = coefs[i];
		
        if (coef != 0) {
            if (i == 0) { // constant
            	// derivative is 0
            } else if (i == 1) { // nx^1 -> n
                dfofx = dfofx + ' + ' + (coef*i);
            } else if (i == 2) { // nx^2 -> 2nx
                dfofx = dfofx + ' + ' + (coef*2) + x;
            } else if (i < 0) { // nx^i where i is negative ->  i*nx^(i+1)
                if (i == -1) {
                    dfofx = dfofx + ' + ' + (coef * i); // x^-1+1 = x^0 = constant
                } else {
                    dfofx = dfofx + ' + ' + (coef*i) + x + '^' + (i + 1); // adds rather than subtracting from i
                }
            } else { // x^power, derivative is power*x^(power-1) when power is +
                dfofx = dfofx + ' + ' + (coef*i) + x +'^' + (i - 1);
            }
        }
    }
	
    return cleanExp(dfofx, x);
}

function dPolydx_wrong3(low_deg, high_deg, coefs, x)
{
	// reversed signs on all terms
	if (!x) x = 'x';
	var dfofx = '';
	
	for (var i = high_deg; i >= low_deg; i--) {
		var coef = coefs[i];
		
        if (coef != 0) {
            if (i == 0) { // constant
            	// derivative is 0
            } else if (i == 1) { // nx^1 -> -n
                dfofx = dfofx + ' + ' + (coef*-1);
            } else if (i == 2) { // nx^2 -> -2nx
                dfofx = dfofx + ' + ' + (coef*2*-1) + x;
            } else { // nx^i -> -i*nx^(i-1)
                dfofx = dfofx + ' + ' + (coef*i*-1) + x + '^' + (i-1);
            }
        }
    }
	
    return cleanExp(dfofx, x);
}
function dPolydx_wrong4(low_deg, high_deg, coefs, x)
{
	// doesn't multiply coefficients
	if (!x) x = 'x';
	var dfofx = '';
	
	for (var i = high_deg; i >= low_deg; i--) {
		var coef = coefs[i];
		
        if (coef != 0) {
            if (i == 0) { // constant
            	// derivative is 0
            } else if (i == 1) { // nx^1 -> n
                dfofx = dfofx + ' + ' + coef;
            } else if (i == 2) { // nx^2 -> nx
                dfofx = dfofx + ' + ' + coef + x;
            } else { // nx^i -> nx^(i-1)
                dfofx = dfofx + ' + ' + coef + x + '^' + (i-1);
            }
        }
    }
	
    return cleanExp(dfofx, x);
}
function dPolydx_wrong5(low_deg, high_deg, coefs, x)
{
	// original with flipped signs
	if (!x) x = 'x';
	var dfofx = '';
	
	for (var i = high_deg; i >= low_deg; i--) {
		var coef = coefs[i];
		
        if (coef != 0) {
            if (i == 0) { // -constant
            	dfofx = dfofx + ' + ' + coef*-1;
            } else if (i == 1) { // -x^1
                dfofx = dfofx + ' + ' + coef*-1 + x;
            } else { // -x^power
                dfofx = dfofx + ' + ' + coef*-1 + x + '^' + i;
            }
        }
    }
	
    return cleanExp(dfofx, x);
}

function cleanExp(expr, x)
{
	if (!x) x = 'x';
	
	expr = nicefySigns(expr.substring(2));
	while (expr.indexOf(" 1"+x) != -1) {
		expr = expr.replace(" 1"+x, x);
	}
	while (expr.indexOf("-1"+x) != -1) {
		expr = expr.replace("-1"+x, "-"+x);
	}
	
	return expr;
}

function funcNotation(x)
{
	if (!x) x = 'x';
	
	notations = [
		['y', 'dy/(d'+x+')'],
		['f('+x+')', 'f\'('+x+')'],
		['g('+x+')', 'g\'('+x+')'],
		['y', 'y\''],
		['f('+x+')', 'd/(d'+x+') f('+x+')'],
		['a', 'a\''],
		['a', 'da/(d'+x+')']
			];
	n_idx = getRandomInt(notations.length-1);
	return {
		fofx: notations[n_idx][0],
		dfofx: notations[n_idx][1]
		}
}

funcGens = [];

funcGens[0] = function(x) {
    // power rule, polynomials
    var high_deg = getRandomIntRange(2, 4);
    var low_deg = getRandomIntRange(0, 2);
    var coefs = polyCoefs(low_deg, high_deg);
	
	return { fofx: polyExp(low_deg, high_deg, coefs, x),
			dfofx: dPolydx(low_deg, high_deg, coefs, x),
			wrongs: [
				dPolydx_wrong1(low_deg, high_deg, coefs, x),
				dPolydx_wrong2(low_deg, high_deg, coefs, x),
				dPolydx_wrong3(low_deg, high_deg, coefs, x),
				dPolydx_wrong4(low_deg, high_deg, coefs, x),
				dPolydx_wrong5(low_deg, high_deg, coefs, x),
				] };
}

funcGens[1] = function(x) {
	// random trig func
	var idx = getRandomInt(2); // 0 - 2 in trig funcs
	var wrongs = [];
	
    wrongs[0] = 'sin(' + x + ')';
    wrongs[1] = 'csc(' + x + ')';
    wrongs[2] = 'sec(' + x + ')';
    wrongs[3] = 'tan(' + x + ')';
    wrongs[4] = '-sec(' + x + ')';
    wrongs[5] = '-cos(' + x + ')';
	
    return { fofx: trigFuncs[idx] + '(' + x + ')',
	     dfofx: dTrigFuncdx[trigFuncs[idx]] + '(' + x + ')',
	     wrongs: wrongs };
}

funcGens[2] = function(x) {
	// basic x^power, simplified version of polynomials in [0]
	// kept this around mainly for easy wrong answer generation
	var high_deg = getRandomIntRange(2, 6);
    var low_deg = high_deg;
	
    var coefs = [];
	coefs[high_deg] = 1;
	
	return { fofx: polyExp(low_deg, high_deg, coefs, x),
			dfofx: dPolydx(low_deg, high_deg, coefs, x),
			wrongs: [
				dPolydx_wrong1(low_deg, high_deg, coefs, x),
				dPolydx_wrong2(low_deg, high_deg, coefs, x),
				dPolydx_wrong3(low_deg, high_deg, coefs, x),
				dPolydx_wrong4(low_deg, high_deg, coefs, x),
				dPolydx_wrong5(low_deg, high_deg, coefs, x),
				] };
}

funcGens[3] = function(x) {
	// ln x and e^x, combined in one because these should not be too likely
	var wrongs = [];
	
	if (getRandomInt(1)) {
		wrongs[0] = '1/(ln('+x+'))';
	    wrongs[1] = 'e^' + x;
	    wrongs[2] = '1/(e^'+ x + ')';
	    wrongs[3] = 'ln('+x+')';
	    wrongs[4] = '1/('+x+'^2)';
	    wrongs[5] = x;
		
	    return { fofx: "ln(" + x + ")",
		     dfofx: "1/" + x,
		     wrongs: wrongs };
	} else {
		wrongs[0] = x + '*e^('+x+'-1)';
	    wrongs[1] = '1/'+ x;
	    wrongs[2] = x+'*e^'+x+'';
	    wrongs[3] = 'e^('+x+'-1)';
	    wrongs[4] = '(e-'+x+')^'+x;
	    wrongs[5] = 'e/' + x;
		
		return { fofx: "e^"+ x,
				dfofx: "e^"+ x,
				wrongs: wrongs };
	}
}
