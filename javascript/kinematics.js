kvars = ["d", "v_0", "v", "a", "t"];
kunits = {
	"d": "m",
	"v_0": "m/s",
	"v": "m/s",
	"a": "m/(s^2)",
	"t": "s"
}
// number of decimal places to show
var_places = 1;

function rollUnknowns() {
	do {
		unknown = kvars[getRandomInt(kvars.length-1)];
		solving = kvars[getRandomInt(kvars.length-1)];
	} while (solving == unknown)
}

function randomFreefallMotion()
{
	// d = v0t + 1/2at^2
	// 0 = 1/2at^2 + v0t - d
	// [ -v0 +/- sqrt(v0^2 + 2ad) ] / a
	
	var accel = -9.8;
	var v_init = (getRandomInt(1) ? 0 : getRandomIntRange(-100, 300)/10);
	var time = getRandomIntRange(0, 200)/10;
	var disp = v_init*time + (1/2)*accel*time*time;
	var v_final = v_init + accel * time;
	
	return {
		d: disp,
		v_0: v_init, 
		v: v_final,
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
		v_0: veloc, 
		v: veloc,
		a: accel,
		t: time
	};
}
function randomAccelMotion()
{
	// generated numbers are going to be messy anyway, so might as well
	// make them all messy
	var accel = getRandomIntRange(-200, 200)/10;
	var v_init = getRandomIntRange(-400, 400)/10;
	var time = getRandomIntRange(100, 200)/10;
	var disp = v_init * time + (1/2) * accel * time * time;
	var v_final = v_init + accel * time;
	
	return {
		d: disp,
		v_0: v_init, 
		v: v_final,
		a: accel,
		t: time
	};
}

function u(kvar, variable) {
	// This function will take kvar[] as a motion array,
	// and it will also take kvar as a kinematic variable and place the
	// unit for the variable type.
	if (kvar["d"]) {
		// if kvar is the array
		return roundNumber(kvar[variable], var_places) + " " + kunits[variable];
	} else {
		return roundNumber(kvar, var_places) + " " + kunits[variable];
	}
}

hintWithNo = { // we have 2 unknowns, so we're solving for one "with no" of the other
	d: function(motion, solving) {
		// v = v0 + at
		write_step("`v = v_0 + at`");
		switch (solving) {
			case "v":
			write_step("`v = " + u(motion,"v_0") + " + (" + u(motion,"a") + ")(" + u(motion,"t") + ")`");
			write_step("`v = " + u(motion,"v") + "`");
			break;
			
			case "v_0":
			write_step("`v - at = v_0`");
			write_step("`"+u(motion,"v")+" - ("+u(motion,"a")+")("+u(motion,"t")+") = v_0`");
			write_step("`"+u(motion,"v_0")+" = v_0`");
			break;
			
			case "a":
			write_step("`(v - v_0)/t = a`");
			write_step("`("+u(motion,"v")+" - "+u(motion,"v_0")+")/("+u(motion,"t")+") = a`");
			write_step("`"+u(motion,"a")+" = a`");
			break;
			
			case "t":
			write_step("`(v - v_0)/a = t`");
			write_step("`("+u(motion,"v")+" - "+u(motion,"v_0")+")/("+u(motion,"a")+") = t`");
			write_step("`"+u(motion,"t")+" = t`");
			break;
		}
	},
	v_0: function(motion, solving) {
		// d = vt - (1/2)at^2
		write_step("`d = vt - (1/2)at^2`");
		switch(solving) {
			case "d":
			write_step("`d = ("+u(motion,"v")+")("+u(motion,"t")+") - (1/2)("+u(motion,"a")+")("+u(motion,"t")+")^2");
			write_step("`d = "+u(motion,"d"));
			break;
			
			case "v":
			write_step("`(d + (1/2)at^2)/t = v`");
			write_step("`("+u(motion,"d")+" + (1/2)+("+u(motion,"a")+")("+u(motion,"t")+")^2)/("+u(motion,"t")+") = v`");
			write_step("`"+u(motion,"v")+" = v`");
			break;
			
			case "a":
			write_step("`(d - vt)/(-(1/2)t^2) = a`");
			write_step("`("+u(motion,"d")+" - ("+u(motion,"v")+")("+u(motion,"t")+"))/(-(1/2)("+u(motion,"t")+")^2) = a`");
			write_step("`"+u(motion,"a")+" = a`");
			break;
			
			case "t":
			write_step("`0 = -(1/2)at^2 + vt - d`");
			write_step("<p>By the quadratic formula:</p>" +
						"<p>`t = (-v +- sqrt(v^2 - 2ad))/(-a)`</p>");
			write_step("`t = (-"+u(motion,"v")+" +- sqrt(("+u(motion,"v")+")^2 - 2("+u(motion,"a")+")("+u(motion,"d")+")))/(-"+u(motion,"a")+")`");
			write_step("`t = "+u(motion,"t")+"`");
			break;
		}
	},
	v: function(motion, solving) {
		// d = v0t + (1/2)at^2
		write_step("`d = v_0t + (1/2)at^2`");
		switch(solving) {
			case "d":
			write_step("`d = ("+u(motion,"v_0")+")("+u(motion,"t")+") + (1/2)("+u(motion,"a")+")("+u(motion,"t")+")^2");
			write_step("`d = "+u(motion,"d"));
			break;
			
			case "v_0":
			write_step("`(d - (1/2)at^2)/t = v_0`");
			write_step("`("+u(motion,"d")+" - (1/2)+("+u(motion,"a")+")("+u(motion,"t")+")^2)/("+u(motion,"t")+") = v_0`");
			write_step("`"+u(motion,"v_0")+" = v_0`");
			break;
			
			case "a":
			write_step("`(d - v_0t)/((1/2)t^2) = a`");
			write_step("`("+u(motion,"d")+" - ("+u(motion,"v_0")+")("+u(motion,"t")+"))/((1/2)("+u(motion,"t")+")^2) = a`");
			write_step("`"+u(motion,"a")+" = a`");
			break;
			
			case "t":
			write_step("`0 = (1/2)at^2 + v_0t - d`");
			write_step("<p>By the quadratic formula:</p>" +
						"<p>`t = (-v_0 +- sqrt(v_0^2 + 2ad))/a`</p>");
			write_step("`t = (-"+u(motion,"v_0")+" +- sqrt(("+u(motion,"v_0")+")^2 + 2("+u(motion,"a")+")("+u(motion,"d")+")))/("+u(motion,"a")+")`");
			write_step("`t = "+u(motion,"t")+"`");
			break;
		}
	},
	a: function(motion, solving) {
		// d = (1/2)(v0 + v)t
		write_step("`d = (1/2)(v_0 + v)t`");
		switch(solving) {
			case "d":
			write_step("`d = (1/2)("+u(motion,"v_0")+" + "+u(motion,"t")+")("+u(motion,"t")+")`");
			write_step("`d = "+u(motion,"d"));
			break;
			
			case "v_0":
			write_step("`2d/t - v = v_0`");
			write_step("`2("+u(motion,"d")+")/("+u(motion,"t")+") - "+u(motion,"v")+" = v_0`");
			write_step("`"+u(motion,"v_0")+" = v_0`");
			break;
			
			case "v":
			write_step("`(2d)/t - v_0 = v`");
			write_step("`(2("+u(motion,"d")+"))/("+u(motion,"t")+") - "+u(motion,"v_0")+" = v`");
			write_step("`"+u(motion,"v")+" = v`");
			break;
			
			case "t":
			write_step("`(2d)/(v_0 + v) = t`");
			write_step("`(2("+u(motion,"d")+"))/("+u(motion,"v_0")+" + "+u(motion,"v")+") = t`");
			write_step("`"+u(motion,"t")+" = t`");
			break;
		}
	},
	t: function(motion, solving) {
		// v^2 = v0^2 + 2ad
		write_step("`v^2 = v_0^2 + 2ad`");
		switch(solving) {
			case "d":
			write_step("`(v^2 - v_0^2)/(2a) = d`");
			write_step("`(("+u(motion,"v")+")^2 - ("+u(motion,"v_0")+")^2)/(2("+u(motion,"a")+")) = d`");
			write_step("`"+u(motion,"d")+" = d`");
			break;
			
			case "v_0":
			write_step("`+-sqrt(v^2 - 2ad) = v_0`");
			write_step("`+-sqrt(("+u(motion,"v")+")^2 - 2("+u(motion,"a")+")("+u(motion,"d")+")) = v_0`");
			write_step("`"+u(motion,"v_0")+" = v_0`");
			break;
			
			case "v":
			write_step("`v = +-sqrt(v_0^2 + 2ad)`");
			write_step("`v = +-sqrt(("+u(motion,"v_0")+")^2 + 2("+u(motion,"a")+")("+u(motion,"d")+"))`");
			write_step("`"+u(motion,"v")+" = v`");
			break;
			
			case "a":
			write_step("`(v^2 - v_0^2)/(2d) = a`");
			write_step("`(("+u(motion,"v")+")^2 - ("+u(motion,"v_0")+")^2)/(2("+u(motion,"d")+")) = a`");
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
		
		addWrongChoice(u(motion.v_0 * t - (1/2)*motion.a*motion.t*motion.t, "d"));
		addWrongChoice(u(motion.v * t + (1/2)*motion.a*motion.t*motion.t, "d"));
		addWrongChoice(u(motion.v * t * -1 - (1/2)*motion.a*motion.t*motion.t, "d"));
		
		addWrongChoice(u(motion.a * t + (1/2)*motion.a*motion.t*motion.t, "d"));
		addWrongChoice(u(motion.a * t, "d"));
		break;
		
		case "v_0":
		addWrongChoice(u((motion.d + (1/2)*motion.a*motion.t*motion.t)/motion.t, "v_0"));
		addWrongChoice(u((motion.d + (1/2)*motion.a*motion.t*motion.t), "v_0"));
		
		addWrongChoice(u((motion.d - (1/2)*motion.a*motion.t*motion.t), "v_0"));
		
		addWrongChoice(u( ((2*motion.d) / motion.t) + motion.v, "v_0"));
		addWrongChoice(u( ((2*motion.d) + motion.v)/motion.t, "v_0"));
		break;
		
		case "v":
		addWrongChoice(u((motion.d - (1/2)*motion.a*motion.t*motion.t)/motion.t, "v"));
		addWrongChoice(u((motion.d - (1/2)*motion.a*motion.t)/motion.t, "v"));
		break;
		
		case "a":
		addWrongChoice(u(
			(Math.sqrt(Math.pow(motion.v_0, 2) + 2*motion.a*motion.d) + motion.v_0)/motion.a, "a"));
		addWrongChoice(u(motion.a * -1, "a"));
		break;
		
		case "t":
		addWrongChoice(u((motion.v + motion.v_0)/motion.a, "t"));
		addWrongChoice(u((-1*motion.v + motion.v_0)/motion.a, "t"));
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
