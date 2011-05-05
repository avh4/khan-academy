// Borrowed from derivatives_1.html, may want to unify later.
function Polynomial(degree) {
    var roots = [];
    var coeffs = [];
    var polyn_str = "";
    
    generateCoefficients(degree);
    
    function sumOfProduct(set) {
        var result = 0;
        for (var i = 0; i < set.length; i++) {
            var factors = set[i];
            var product = 1;
            for (var j = 0 ; j < factors.length; j++) {
                product *= factors[j];
            }
            result += product;
        }
        return result;
    }
    
    // It would be nicer to choose some good looking points
    // and then get the function that goes through those points.
    // The below chooses a few roots and then divides by 30 or so.
    function generateCoefficients (degree) {
        for (var i = 0; i < degree; i++) {
            roots[i] = getRandomIntRange(-7, 7);
        }
        
        var factor = getRandomIntRange(0, 1) ? -30 : 30;
        for (var i = 0; i <= degree; i++) {
            var combos = choose(roots, i);
            var coeff = sumOfProduct(combos) / factor;
            coeffs[i] = coeff;
            
            var exp = degree - i;

            if (coeff) {
                polyn_str += " + " + coeff;
                if (exp == 1)
                    polyn_str += "x";
                else if (exp != 0)
                    polyn_str += "x^" + exp;
            }
        }
        
        polyn_str = nicefySigns(polyn_str);
    }
    
    this.toString = function() {
        console.log(polyn_str);
        return polyn_str;
    }
    
    this.evaluateAt = function(x) {
        var y = 0;
        for (var i = 0; i < coeffs.length; i++) {
            var exp = coeffs.length - i - 1;
            y += coeffs[i] * Math.pow(x, exp);
        }
    	return y;
    }
    
    this.evaluateDerivativeAt = function(x) {
        var y = 0;
        for (var i = 0; i < coeffs.length; i++) {
            var exp = coeffs.length - i - 1;
    		y += (coeffs[i] * exp) * Math.pow(x, exp - 1);
    	} 
    	return y;
    }
}
