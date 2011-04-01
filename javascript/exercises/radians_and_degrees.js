// What do students use for pi? 3.14?

var RADIANS_TO_DEGREES = 0;
var DEGREES_TO_RADIANS = 1;
var common_angles = [{deg: 30, rad: "pi/6"},
                    {deg: 45, rad: "pi/4"},
                    {deg: 60, rad: "pi/3"},
                    {deg: 90, rad: "pi/2"},
                    {deg: 120, rad: "2/3pi"},
                    {deg: 135, rad: "3/4pi"},
                    {deg: 150, rad: "5/6pi"},
                    {deg: 180, rad: "pi"},
                    {deg: 210, rad: "7/6pi"},
                    {deg: 225, rad: "5/4pi"},
                    {deg: 240, rad: "4/3pi"},
                    {deg: 270, rad: "3/2pi"},
                    {deg: 300, rad: "5/3pi"},
                    {deg: 315, rad: "7/4pi"},
                    {deg: 330, rad: "11/6pi"},
                    {deg: 360, rad: "2pi"}]

function RadiansAndDegreesExercise(type) {
    if (type != RADIANS_TO_DEGREES && type != DEGREES_TO_RADIANS) {
        if (getRandomIntRange(0, 1))
            var exercise = new RadiansToDegreesExercise();
        else
            var exercise = new DegreesToRadiansExercise();
    }
}

function RadiansToDegreesExercise() {
    var radian;
    var answer;

    function generateProblem() {
        if (getRandomIntRange(0, 1)) {
            var index = getRandomIntRange(0, common_angles.length - 1);
            var angle = common_angles[index];
            radian = angle.rad;
            answer = angle.deg;
            write_text("Convert `" + radian + "` radians into degrees.");
            
            for (var i = 1; i <= 3; i++) {
                var wrong_index = (index + (4 * i)) % common_angles.length;
                addWrongChoice(common_angles[wrong_index].deg + "&#176;");
            }
        } else {
            var random_degree = getRandomIntRange(0, 360);
            radian = roundToHundredth(random_degree * Math.PI / 180);
            write_text("Convert `" + radian + "` radians into degrees. Round to the nearest degree.");
            
            answer = Math.round(radian * 180 / Math.PI);
            while (getNumPossibleAnswers() < 3) {
                var offset = getRandomIntRange(10, 35);
                if (getRandomIntRange(0, 1))
                    offset *= -1;
                    
                var wrong = answer + offset;
                if (wrong >= 0 && wrong <= 360)
                    addWrongChoice(wrong + "&#176;");
            }
        }
        setCorrectAnswer(answer + "&#176;");
    }
    
    function generateHints() {
        open_left_padding(30);
        write_step("To convert from radians to degrees, you multiply by `180&#176;` and then divide by `pi`.");
        write_step("`" + radian + " * (180&#176;) / pi = " + answer + "&#176;`");
        close_left_padding();
    }
    
    generateProblem();
    generateHints();
}

function DegreesToRadiansExercise() {
    var degree;
    var answer;
    
    function generateProblem() {
        if (getRandomIntRange(0, 1)) {
            var index = getRandomIntRange(0, common_angles.length - 1);
            var angle = common_angles[index];
            degree = angle.deg;
            answer = angle.rad;
            write_text("Convert `" + degree + "&#176;` into radians.");

            for (var i = 1; i <= 3; i++) {
                var wrong_index = (index + (4 * i)) % common_angles.length;
                addWrongChoice(common_angles[wrong_index].rad);
            }
        } else {
            degree = getRandomIntRange(0, 360);
            write_text("Convert `" + degree + "&#176;` into radians. Round to the nearest hundredth.");
            
            answer = roundToHundredth(degree * Math.PI / 180);
            while (getNumPossibleAnswers() < 3) {
                var offset = getRandomIntRange(10, 35) / 100;
                if (getRandomIntRange(0, 1))
                    offset *= -1;
                    
                // If I don't call roundToHundredth, I sometimes get 5.2300000001.
                var wrong = answer + offset;
                if (wrong >= 0 && wrong <= 2 * Math.PI)
                    addWrongChoice(roundToHundredth(answer + offset));
            }
        }
        setCorrectAnswer(answer);
    }
    
    function generateHints() {
        open_left_padding(30);
        write_step("To convert from degrees to radians, you multiply by `pi` and then divide by `180&#176;`.");
        write_step("`" + degree + "&#176; * pi / (180&#176;) = " + answer + "`")
        close_left_padding();
    }
    
    generateProblem();
    generateHints();
}