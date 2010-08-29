trigFuncs = ["sin", "cos", "tan"];
dTrigFuncdx = {
	"sin": "cos",
	"cos": "-sin",
	"tan": "sec^2"
	};

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
	
    return cleanExp(fofx, x);
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