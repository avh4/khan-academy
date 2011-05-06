/*
 *
    Recognizing Conic Sections
    Author: Rob Fitzpatrick
    Date: 2011-04-20
       
    Problem Spec:

        Type A) 
         * This graph is a ____?
         * You are provided with 1 graph and must decide which 
           of the 4 conic sections accurately describes it.
         * Shapes are drawn to be mostly on screen and flipped & rotated
           where reasonable.

        Type B) 
         * Which of the following is a ____? 
         * You are provided with 4 graphs and must choose which 
           is an ellipse/circle/parabola/hyperbola  
         * Graph is divided into 4 quadrants with *no* axes. The axes were
           removed to provide a visual excuse for cropping hyperbolas to stay
           in their quadrant instead of extending over the other available shapes.
 *
 */

function RecognizingConicSectionsExercise() {

    //for circles, ellipses, parabolas. hyperbolae always center around 0,0
    var CENTER_MIN = -5;
    var CENTER_MAX = 5;

    //for circles and the longer axis of ellipses
    var RADIUS_MIN = 2;
    var RADIUS_MAX = 6; //allows circles & ellipses to go 1 unit off-screen

    var MAX_ELLIPSE_SQUISH = 10; //squish to 10% of default axis
    var MAX_ELLIPSE_SQUISH = 65; //squish to 65%

    //parabola stretch, applied relative to current axis/orientation
    var MIN_PARABOLA_HSCALE = 10;  // 10%
    var MAX_PARABOLA_HSCALE = 500; //500%
    
    //a & b constants for 1=x^2/a^2-y^2/b^2
    var HYPERBOLA_AB_MIN = 2; 
    var HYPERBOLA_AB_MAX = 3; 

    //names of possible answers
    //CAUTION: If you tweak these names, you also need to update the switch
    //         statements in the graph drawing or nothing will be drawn.
    var CONIC_SECTIONS = ["Circle", "Ellipse", "Parabola", "Hyperbola"];
    //quadrant labels when picking which graph is an X
    var SHAPE_LABELS = ["Shape A", "Shape B", "Shape D", "Shape C"];
    //quadrant colors when picking which graph is an X to ensure the labels
    //aren't visually associated with the wrong curve
    var CONIC_COLORS = ["blue", "red", "green", "purple"];

    //set during init to 0-3, where CONIC_SECTIONS[currentSection] is the correct answer
    var currentSection;

    //possible problem types
    var WHICH_TYPE = "which_type_of_conic_is_this_graph";
    var WHICH_GRAPH = "which_graph_is_of_conic_X";

    //set to either WHICH_TYPE or WHICH_GRAPH during init
    var problem_type;

    this.init = function() {

        if (get_random() % 2) {
            //user sees a single graph and chooses which type of conic section it is
            problem_type = WHICH_TYPE;
            generateWhichTypeProblem();
            showWhichTypeProblem();
        }
        else {
            //user sees several graphs and identifies which one is a certain conic section
            problem_type = WHICH_GRAPH;
            generateWhichGraphProblem();
            showWhichGraphProblem();
        }
        
        drawProblem();
        //hints are conveniently the same for both problem types
        generateHints();
    };


    function drawProblem() {
        appendQuestionHtml("<div id=\"raphael_container\" style=\"float: left;\"></div>");
        RaphaelWrapper.init(360, 360);
        if (problem_type == WHICH_GRAPH) {
            drawWhichGraphDisplay();

        }
        else if (problem_type == WHICH_TYPE) {
            drawWhichTypeDisplay();
        }
    }

    function drawWhichTypeDisplay() {
        initPlane(); // draws XY axes and 10x10 grid for math 

        present.stroke = "blue";

        //center x & y of the shape
        var cx = getRandomIntRange(CENTER_MIN, CENTER_MAX); 
        var cy = getRandomIntRange(-CENTER_MIN, CENTER_MAX); 

        //primary radius for circles & ellipses
        var r = getRandomIntRange(RADIUS_MIN, RADIUS_MAX);

        switch (currentSection) {

            case "Circle":
                present.ellipse([cx, cy], r, r);
                break;

            case "Ellipse":
                drawRandomizedEllipse(cx, cy, r);
                break;

            case "Parabola":
                var hScale = getRandomIntRange(MIN_PARABOLA_HSCALE, MAX_PARABOLA_HSCALE) / 100.0;
                var isHorizontal = getRandomIntRange(0, 1);
                var vFlip; 
                var c = (isHorizontal ? cx : cy);

                //if the curve is well off-center, flip it so bulk of shape is visible
                if (c < -2) vFlip = 1;
                else if (c > 2) vFlip = -1;
                //otherwise, if curve is mostly centered, randomize the flip
                else vFlip = getRandomIntRange(0, 1) * 2 - 1; //resolves to either -1 or 1

                drawParabola(cx, cy, hScale, vFlip, isHorizontal);
                break;

            case "Hyperbola":
                a = getRandomIntRange(HYPERBOLA_AB_MIN, HYPERBOLA_AB_MAX);
                b = getRandomIntRange(HYPERBOLA_AB_MIN, HYPERBOLA_AB_MAX);
                drawHyperbola(cx, cy, a, b, getRandomIntRange(0, 1));
                break;
        }
    }

    function drawWhichGraphDisplay() {
        //background for showing 4 smaller graph sections
        initQuarterGrid();

        //graph labels
        label_pos = present.belowright;
        present.fontsize = 24;
        
        //loop through each quadrant, drawing
        //a quarter-sized shape within it
        quadrant_centers = [[-5, 5], [5, 5], [5, -5], [-5, -5]];
        for (var i = 0; i < 4; i ++) {
            cx = quadrant_centers[i][0];
            cy = quadrant_centers[i][1];
            r = 3.5;

            present.stroke = CONIC_COLORS[i];
            present.fontfill = CONIC_COLORS[i];
            present.text([cx-5,cy+5.5], SHAPE_LABELS[i], label_pos);

            switch (CONIC_SECTIONS[i]) {
                case "Circle":
                    present.ellipse([cx, cy], r, r);
                    break;
                case "Ellipse":
                    drawRandomizedEllipse(cx, cy, 3.5);
                    break;
                case "Parabola":
                    var hScale = getRandomIntRange(MIN_PARABOLA_HSCALE, MAX_PARABOLA_HSCALE) / 100.0;
                    var isHorizontal = getRandomIntRange(0, 1);
                    var vFlip; 

                    parab_cx = cx;
                    parab_cy = cy;

                    if (isHorizontal) {
                        //open to the right when in the right 2 quadrants, and vice versa
                        //in the left quadrants
                        vFlip = ((i == 0 || i == 3) ? -1 : 1);
                        //scoot calculated center left/right since parabolas are lopsided
                        parab_cx -= vFlip * 4;
                    }
                    else {
                        //open to the top in the top 2 quadrants, and vice versa in the
                        //bottom ones
                        vFlip = ((i == 2 || i == 3) ? -1 : 1);
                        //scoot calculated center updward/downward since parabolas are lopsided
                        parab_cy -= vFlip * 4;
                    }

                    drawParabola(parab_cx, parab_cy, hScale, vFlip, isHorizontal);
                    break;

                case "Hyperbola":
                    a = getRandomIntRange(HYPERBOLA_AB_MIN/2, HYPERBOLA_AB_MAX/2);
                    b = getRandomIntRange(HYPERBOLA_AB_MIN/2, HYPERBOLA_AB_MAX/2);
                    
                    //crop the hyperbola's horizontal drawing to stay mostly within its
                    //own quadrant. It's still able to creep a bit too high & low, but
                    //doesn't interfere with the other shapes in a meaningful way.
                    var left = (i==0 || i==3) ? -10 : 0;
                    var right = (i==0 || i==3) ? 0 : 10;

                    drawHyperbola(cx, cy, a, b, true, left, right);
                    break;
            }
        }
    }

    //helper function which takes an ellipse's location and longer radius and
    //then randomized the shorter radius and the orientation
    function drawRandomizedEllipse(cx, cy, r_major) {

        //squish the shorter radius relative to the longer one
        var squish = getRandomIntRange(MAX_ELLIPSE_SQUISH, MAX_ELLIPSE_SQUISH) / 100.0;

        //randomize whether x or y axis is the long one
        if (getRandomIntRange(0, 1)) {
            //horizontally oriented
            present.ellipse([cx, cy], r_major, r_major * squish);
        }
        else {
           //vertically oriented
            present.ellipse([cx, cy], r_major * squish, r_major);
        }
    }

    /* vFlip is a multiplier, not a boolean, so 1 means it is
     * not flipped and -1 means it is */
    function drawParabola(cx, cy, hScale, vFlip, isHorizontal) {

        if (isHorizontal) {

            //specifying min & max seems necessary for the chart to correctly
            //render the very base of the curve where the two legs join
            var min = (vFlip > 0 ? cx : -10);
            var max = (vFlip > 0 ? 10 : cx);

            var xoff = -cx; //avoid double negative sign in plot()

            present.plot("y = "+cy+" + sqrt("+hScale*vFlip+" * ("+xoff+" + x))", min, max);
            present.plot("y = "+cy+" - sqrt("+hScale*vFlip+" * ("+xoff+" + x))", min, max);
        }
        else {
            var xoff = -cx; //avoid double negative sign in plot()

            //conditional to avoid double negative sign in plot()
            if (vFlip < 0) {
                present.plot("y = "+cy+" - ("+hScale+" * ("+xoff+" + x))^2");
            }
            else {
                present.plot("y = "+cy+" + ("+hScale+"("+xoff+" + x))^2");
            }
        }
    }

    function drawHyperbola(cx, cy, a, b, isHorizontal) {
        drawHyperbola(cx, cy, a, b, isHorizontal, 10, -10);
    }

    function drawHyperbola(cx, cy, a, b, isHorizontal, left_edge, right_edge) {
        if (isHorizontal) {
            // x^2/a^2 - y^2/b^2 = 1
            // y = sqrt((x^2/a^2 - 1)* b^2)

            //plot must be drawn in quarters instead of halves due to 
            //a graph rendering error jumping from left half of the curve
            //to the right half with an almost horizontal line.
            present.plot("y = " + cy + "+sqrt(((x+" + (-cx) + ")^2/"+a+"^2 - 1) * " + b + "^2)", cx+a, right_edge);
            present.plot("y = " + cy + "+sqrt(((x+" + (-cx) + ")^2/"+a+"^2 - 1) * " + b + "^2)", left_edge, -a+cx);
            present.plot("y = " + cy + "-sqrt(((x+" + (-cx) + ")^2/"+a+"^2 - 1) * " + b + "^2)", cx+a, right_edge);
            present.plot("y = " + cy + "-sqrt(((x+" + (-cx) + ")^2/"+a+"^2 - 1) * " + b + "^2)", left_edge, -a+cx);
        }
        else {
            // y^2/a^2 - x^2/b^2 = 1
            // y = sqrt((x^2/b^2 - 1)* a^2)
            present.plot("y = " + cy + "+sqrt(((x+" + (-cx) + ")^2/"+b+"^2 + 1) * " + a + "^2)");
            present.plot("y = " + cy + "-sqrt(((x+" + (-cx) + ")^2/"+b+"^2 + 1) * " + a + "^2)");
        }
    }

    function generateWhichTypeProblem() {

        var correctIndex = getRandomIntRange(0, CONIC_SECTIONS.length - 1);
        currentSection = CONIC_SECTIONS[correctIndex];
        setCorrectAnswer('"' + currentSection + '"');

        for (var i = 0; i < CONIC_SECTIONS.length; i ++) {
            if (i != correctIndex) {
                addWrongChoice('"' + CONIC_SECTIONS[i] + '"');
            }
        }
    }

    function showWhichTypeProblem() {
        write_text("<span class='question_text'>Which type of <span class='hint_orange'>conic section</span> is shown in this graph?</span>");
    }

    function generateHints() {

        //TODO: hardcoded width will break if exercise page layout changes
        //currently based on question area width of 655 with 400 for graph.
        document.write("<div style='float:left; padding-left: 20px; width:255px'>");

        write_step("A <span class='hint_orange'>circle</span> is perfectly round, where every point is exactly the same distance from its center.");
        write_step("An <span class='hint_orange'>ellipse</span> is like a circle that's been stretched or squished in one direction.");
        write_step("A <span class='hint_orange'>parabola</span> is like a big letter <span class='hint_orange'>'U'</span> that zooms off in one direction.");
        write_step("A <span class='hint_orange'>hyperbola</span> has two separate curves which each get closer and closer to the legs of a big imaginary <span class='hint_orange'>'X'</span> drawn between them.");

        document.write("</div>");
    }

    function generateWhichGraphProblem() {

        //shuffle conic sections by randomly swapping pairs of elements several
        //times, to avoid displaying the same shapes in the same quadrants every time
        for (var i = 0; i < 20; i ++) {
            var from = getRandomIntRange(0, CONIC_SECTIONS.length - 1);
            var to = getRandomIntRange(0, CONIC_SECTIONS.length - 1);
            var temp = CONIC_SECTIONS[to];
            CONIC_SECTIONS[to] = CONIC_SECTIONS[from];
            CONIC_SECTIONS[from] = temp;
        }
        
        var correctIndex = getRandomIntRange(0, CONIC_SECTIONS.length - 1);
        currentSection = CONIC_SECTIONS[correctIndex];
        setCorrectAnswer('"' + SHAPE_LABELS[correctIndex] + '"');

        for (var i = 0; i < CONIC_SECTIONS.length; i ++) {
            if (i != correctIndex) {
                addWrongChoice('"' + SHAPE_LABELS[i] + '"');
            }
        }
    }

    function showWhichGraphProblem() {
        write_text("<span class='question_text'>Which conic section is " + (currentSection=="Ellipse"?"an ":"a ") + "<span class='hint_orange'>" + currentSection + "</span>?</span>");
    }

    /* a modified version of the standard initPlane() helper function which draws no axes
     * and instead draws dark dividing rectangles around the quadrants. used for showing
     * multiple shapes in one graph area when the position is irrelevant */
    function initQuarterGrid() {
        present.initPicture(-10,10, -10, 10);
        
        present.stroke = "#DDDDDD";
        present.strokewidth = "2";
        for(var i=-10; i<11; i++)
        {
            present.line([i,-11], [i,11]);
            present.line([-11,i], [11,i]);
        }

        //draw dark rectangles around each quadrant
        present.stroke = "#333333";
        present.rect([-10, -10], [0, 0]);
        present.rect([0, 0], [10, 10]);
        present.rect([0, -10], [10, 0]);
        present.rect([-10, 0], [0, 10]);
    }
}
