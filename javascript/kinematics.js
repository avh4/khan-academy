kvars = ["d", "v_i", "v_f", "a", "t"];
kunits = {
	"d": "m",
	"v_i": "m/s",
	"v_f": "m/s",
	"a": "m/(s^2)",
	"t": "s"
}
kunits_disp = {
	"d": "\\text{m}",
	"v_i": "\\text{m}/\\text{s}",
	"v_f": "\\text{m}/\\text{s}",
	"a": "\\text{m}/(\\text{s}^2)",
	"t": "\\text{s}"
}
// number of decimal places to show
var_places = 2;

function rollUnknowns() {
	do {
		unknown = kvars[getRandomInt(kvars.length-1)];
		solving = kvars[getRandomInt(kvars.length-1)];
	} while (solving == unknown)
}

function randomFreefallMotion()
{
	// d = v_it + 1/2at^2
	// 0 = 1/2at^2 + v0t - d
	// [ -v0 +/- sqrt(v0^2 + 2ad) ] / a
	
	var accel = -9.8;
	var v_init = (getRandomInt(1) ? 0 : getRandomIntRange(-100, 300)/10);
	var time = getRandomIntRange(0, 200)/10;
	var disp = v_init*time + (1/2)*accel*time*time;
	var v_final = v_init + accel * time;
	
	return {
		d: disp,
		v_i: v_init, 
		v_f: v_final,
		a: accel,
		t: time
	};
}

function randomConstantMotion()
{
	var accel = 0;
	var time = getRandomIntRange(1, 25);
	var veloc = getRandomIntRange(5, 25);
	var disp = time * veloc;
	
	return {
		d: disp,
		v_i: veloc, 
		v_f: veloc,
		a: accel,
		t: time
	};
}
function randomAccelMotion()
{
	// generated numbers are going to be messy anyway, so might as well
	// make them all messy
	var accel = nonZeroRandomInt(-200, 200)/10;
	var v_init = getRandomIntRange(-400, 400)/10;
	var time = getRandomIntRange(100, 200)/10;
	var disp = v_init * time + (1/2) * accel * time * time;
	var v_final = v_init + accel * time;
	
	return {
		d: disp,
		v_i: v_init, 
		v_f: v_final,
		a: accel,
		t: time
	};
}

function u(kvar, variable) {
	// This function will take kvar[] as a motion array,
	// and it will also take kvar as a kinematic variable and place the
	// (ASCIIMathML-formatted) unit for the variable type.
	if (kvar["d"]) {
		// if kvar is the array
		return roundNumber(kvar[variable], var_places) + "\\ " + kunits_disp[variable];
	} else {
		return roundNumber(kvar, var_places) + "\\ " + kunits_disp[variable];
	}
}

hintWithNo = { // we have 2 unknowns, so we're solving for one "with no" of the other
	d: function(motion, solving) {
		// v_f = v0 + at
		write_step("`v_f = v_i + a*t`");
		switch (solving) {
			case "v_f":
			write_step("`v_f = " + u(motion,"v_i") + " + (" + u(motion,"a") + ")(" + u(motion,"t") + ")`");
			write_step("`v_f = " + u(motion,"v_f") + "`");
			break;
			
			case "v_i":
			write_step("`v_f - at = v_i`");
			write_step("`"+u(motion,"v_f")+" - ("+u(motion,"a")+")("+u(motion,"t")+") = v_i`");
			write_step("`"+u(motion,"v_i")+" = v_i`");
			break;
			
			case "a":
			write_step("`(v_f - v_i)/t = a`");
			write_step("`("+u(motion,"v_f")+" - "+u(motion,"v_i")+")/("+u(motion,"t")+") = a`");
			write_step("`"+u(motion,"a")+" = a`");
			break;
			
			case "t":
			write_step("`(v_f - v_i)/a = t`");
			write_step("`("+u(motion,"v_f")+" - "+u(motion,"v_i")+")/("+u(motion,"a")+") = t`");
			write_step("`"+u(motion,"t")+" = t`");
			break;
		}
	},
	v_i: function(motion, solving) {
		// d = v_ft - (1/2)at^2
		write_step("`d = v_f*t - (1/2)a*t^2`");
		switch(solving) {
			case "d":
			write_step("`d = ("+u(motion,"v_f")+")("+u(motion,"t")+") - (1/2)("+u(motion,"a")+")("+u(motion,"t")+")^2");
			write_step("`d = "+u(motion,"d"));
			break;
			
			case "v_f":
			write_step("`(d + (1/2)a*t^2)/t = v_f`");
			write_step("`("+u(motion,"d")+" + (1/2)("+u(motion,"a")+")("+u(motion,"t")+")^2)/("+u(motion,"t")+") = v_f`");
			write_step("`"+u(motion,"v_f")+" = v_f`");
			break;
			
			case "a":
			write_step("`(d - v_f*t)/(-(1/2)t^2) = a`");
			write_step("`("+u(motion,"d")+" - ("+u(motion,"v_f")+")("+u(motion,"t")+"))/(-(1/2)("+u(motion,"t")+")^2) = a`");
			write_step("`"+u(motion,"a")+" = a`");
			break;
			
			case "t":
			write_step("`0 = -(1/2)a*t^2 + v_f*t - d`");
			write_step("<p>By the quadratic formula:</p>" +
						"<p>`t = (-v_f +- sqrt(v_f^2 - 2a*d))/(-a)`</p>");
			write_step("`t = (-"+u(motion,"v_f")+" +- sqrt(("+u(motion,"v_f")+")^2 - 2("+u(motion,"a")+")("+u(motion,"d")+")))/(-"+u(motion,"a")+")`");
			write_step("`t = "+u(motion,"t")+"`");
			break;
		}
	},
	v_f: function(motion, solving) {
		// d = v_it + (1/2)at^2
		write_step("`d = v_i*t + (1/2)a*t^2`");
		switch(solving) {
			case "d":
			write_step("`d = ("+u(motion,"v_i")+")("+u(motion,"t")+") + (1/2)("+u(motion,"a")+")("+u(motion,"t")+")^2");
			write_step("`d = "+u(motion,"d"));
			break;
			
			case "v_i":
			write_step("`(d - (1/2)a*t^2)/t = v_i`");
			write_step("`("+u(motion,"d")+" - (1/2)("+u(motion,"a")+")("+u(motion,"t")+")^2)/("+u(motion,"t")+") = v_i`");
			write_step("`"+u(motion,"v_i")+" = v_i`");
			break;
			
			case "a":
			write_step("`(d - v_i*t)/((1/2)t^2) = a`");
			write_step("`("+u(motion,"d")+" - ("+u(motion,"v_i")+")("+u(motion,"t")+"))/((1/2)("+u(motion,"t")+")^2) = a`");
			write_step("`"+u(motion,"a")+" = a`");
			break;
			
			case "t":
			write_step("`0 = (1/2)a*t^2 + v_i*t - d`");
			write_step("<p>By the quadratic formula:</p>" +
						"<p>`t = (-v_i +- sqrt(v_i^2 + 2a*d))/a`</p>");
			write_step("`t = (-"+u(motion,"v_i")+" +- sqrt(("+u(motion,"v_i")+")^2 + 2("+u(motion,"a")+")("+u(motion,"d")+")))/("+u(motion,"a")+")`");
			write_step("`t = "+u(motion,"t")+"`");
			break;
		}
	},
	a: function(motion, solving) {
		// d = (1/2)(v0 + v)t
		write_step("`d = (1/2)(v_i + v_f)t`");
		switch(solving) {
			case "d":
			write_step("`d = (1/2)("+u(motion,"v_i")+" + "+u(motion,"v_f")+")("+u(motion,"t")+")`");
			write_step("`d = "+u(motion,"d"));
			break;
			
			case "v_i":
			write_step("`(2d)/t - v_f = v_i`");
			write_step("`(2("+u(motion,"d")+"))/("+u(motion,"t")+") - "+u(motion,"v_f")+" = v_i`");
			write_step("`"+u(motion,"v_i")+" = v_i`");
			break;
			
			case "v_f":
			write_step("`(2d)/t - v_i = v_f`");
			write_step("`(2("+u(motion,"d")+"))/("+u(motion,"t")+") - "+u(motion,"v_i")+" = v_f`");
			write_step("`"+u(motion,"v_f")+" = v_f`");
			break;
			
			case "t":
			write_step("`(2d)/(v_i + v_f) = t`");
			write_step("`(2("+u(motion,"d")+"))/("+u(motion,"v_i")+" + "+u(motion,"v_f")+") = t`");
			write_step("`"+u(motion,"t")+" = t`");
			break;
		}
	},
	t: function(motion, solving) {
		// v^2 = v0^2 + 2ad
		write_step("`v_f^2 = v_i^2 + 2a*d`");
		switch(solving) {
			case "d":
			write_step("`(v_f^2 - v_i^2)/(2a) = d`");
			write_step("`(("+u(motion,"v_f")+")^2 - ("+u(motion,"v_i")+")^2)/(2("+u(motion,"a")+")) = d`");
			write_step("`"+u(motion,"d")+" = d`");
			break;
			
			case "v_i":
			write_step("`+-sqrt(v_f^2 - 2ad) = v_i`");
			write_step("`+-sqrt(("+u(motion,"v_f")+")^2 - 2("+u(motion,"a")+")("+u(motion,"d")+")) = v_i`");
			write_step("`"+u(motion,"v_i")+" = v_i`");
			break;
			
			case "v_f":
			write_step("`v_f = +-sqrt(v_i^2 + 2a*d)`");
			write_step("`v_f = +-sqrt(("+u(motion,"v_i")+")^2 + 2("+u(motion,"a")+")("+u(motion,"d")+"))`");
			write_step("`"+u(motion,"v_f")+" = v_f`");
			break;
			
			case "a":
			write_step("`(v_f^2 - v_i^2)/(2d) = a`");
			write_step("`(("+u(motion,"v_f")+")^2 - ("+u(motion,"v_i")+")^2)/(2("+u(motion,"d")+")) = a`");
			write_step("`"+u(motion,"a")+" = a`");
			break;
		}
	}
}

function addWrongChoicesFor(motion, variable)
{
	switch (variable) {
		case "d":
		addWrongChoice(u(motion.d*-1, "d"));
		
		addWrongChoice(u(motion.v_i * motion.t - (1/2)*motion.a*motion.t*motion.t, "d"));
		addWrongChoice(u(motion.v_f * motion.t + (1/2)*motion.a*motion.t*motion.t, "d"));
		addWrongChoice(u(motion.v_f * motion.t * -1 - (1/2)*motion.a*motion.t*motion.t, "d"));
		
		addWrongChoice(u(motion.a * motion.t + (1/2)*motion.a*motion.t*motion.t, "d"));
		addWrongChoice(u(motion.a * motion.t, "d"));
		break;
		
		case "v_i":
		addWrongChoice(u((motion.d + (1/2)*motion.a*motion.t*motion.t)/motion.t, "v_i"));
		addWrongChoice(u((motion.d + (1/2)*motion.a*motion.t*motion.t), "v_i"));
		
		addWrongChoice(u((motion.d - (1/2)*motion.a*motion.t*motion.t), "v_i"));
		
		addWrongChoice(u( ((2*motion.d) / motion.t) + motion.v_f, "v_i"));
		addWrongChoice(u( ((2*motion.d) + motion.v_f)/motion.t, "v_i"));
		break;
		
		case "v_f":
		addWrongChoice(u((motion.d - (1/2)*motion.a*motion.t*motion.t)/motion.t, "v_f"));
		addWrongChoice(u((motion.d - (1/2)*motion.a*motion.t)/motion.t, "v_f"));
		break;
		
		case "a":
		addWrongChoice(u(
			(Math.sqrt(Math.pow(motion.v_i, 2) + 2*motion.a*motion.d) + motion.v_i)/motion.a, "a"));
		addWrongChoice(u(motion.a * -1, "a"));
		break;
		
		case "t":
		addWrongChoice(u((motion.v_f + motion.v_i)/motion.a, "t"));
		addWrongChoice(u((-1*motion.v_f + motion.v_i)/motion.a, "t"));
	}
}

function printMotion(motion, unknowns)
{
	for (var i=0; i < kvars.length; i++) {
		if ($.inArray(kvars[i], unknowns) != -1) {
			write_text("`" + kvars[i] + " = ?`")
		} else {
			write_text("`" + kvars[i] + " = " + u(motion, kvars[i]) + "`");
		}
	}
}
