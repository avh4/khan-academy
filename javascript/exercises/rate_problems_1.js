/*
 *
    Rate Problems
    Author: Marcia Lee
    Date: 2011-03-02

    Problem spec: http://www.youtube.com/watch?v=at4T4n4JYNc
        Alice traveled by bike at an average speed of X miles per hour.
        Then, she traveled by train at an average speed of Y miles per hour.
        In total, she traveled D miles for T hours.
        
        Constraints:
            X --> [11, 20] mph
            Y --> [41, 50] mph
            avg rate --> [31, 40] mph
            T --> [1, 10] hours
        
        For how many miles did Alice travel by bike?
        For how many miles did Alice travel by train?
        For how many minutes did Alice travel by bike?
        For how many minutes did Alice travel by train?
        
        For fun, bike and train are randomly replaced by a few other vehicles.
 *       
 */

function RateProblemsExercise() {
    var trips = [];
    generateProblem();
    showProblem();
    generateHints();

    function generateProblem() {
        // See constraints in comments above
        trips.time = 11 - Math.abs(get_random());
        var first_rate = 21 - Math.abs(get_random());
        var second_rate = 51 - Math.abs(get_random());
        var avg_rate = 41 - Math.abs(get_random());

        trips.distance = avg_rate * trips.time;
                
        var second_d = (first_rate * second_rate * trips.time - trips.distance * second_rate) / (first_rate - second_rate);
        var first_d = trips.distance - second_d;
        
        trips[0] = {distance: first_d, rate: first_rate, vehicle: getFirstVehicle()};
        trips[1] = {distance: second_d, rate: second_rate, vehicle: getSecondVehicle()};

        switch (get_random() % 4) {
            case 0:
                trips.question = "How many miles did Alice travel by " + trips[0].vehicle + "? (Round to the nearest mile.)";
                setCorrectAnswer(Math.round(trips[0].distance));
                break;
            case 1:
                trips.question = "How many miles did Alice travel by " + trips[1].vehicle + "? (Round to the nearest mile.)";
                setCorrectAnswer(Math.round(trips[1].distance));               
                break;
            case 2:
                trips.question = "How many minutes did Alice travel by " + trips[0].vehicle + "? (Round to the nearest minute.)";
                setCorrectAnswer(Math.round(trips[0].distance / trips[0].rate * 60));
                break;
            default:
                trips.question = "How many minutes did Alice travel by " + trips[1].vehicle + "? (Round to the nearest minute.)";
                setCorrectAnswer(Math.round(trips[1].distance / trips[1].rate * 60));
        }
    }
    
    function showProblem() {
        var first_leg = "Alice traveled by " + trips[0].vehicle 
                        + " at an average speed of " + trips[0].rate + " miles per hour.";
        var second_leg = "Then, she traveled by " + trips[1].vehicle
                        + " at an average speed of " + trips[1].rate + " miles per hour.";
        var pluralization = (trips.time > 1 ? "s" : "");
        var total_journey = "In total, she traveled " + trips.distance + " miles for " + trips.time + " hour" + pluralization + "."
        
        write_text(first_leg);
        write_text(second_leg);
        write_text(total_journey);
        write_text(trips.question)
    }
    
    function generateHints() {
        open_left_padding(30);

        presentKnowns();
        substituteEquations();
        multiplyEquations();
        simplifyEquations();
        
        close_left_padding();
    }
    
    function presentKnowns() {
        write_step("Remember that `d = r * t`, or written another way, `t = d / r`");

        var total_d_str = "Total distance: <span class='hint_orange'>` ";
        var total_t_str = "Total time: <span class='hint_blue'>` ";
        var separate_t_str = "<span class='hint_blue'>";
        
        for (var i = 0; i < trips.length; i++) {
            // variables' subscript is first letter of the vehicle name
            trips[i].d_str = "d_" + trips[i].vehicle[0];
            trips[i].t_str = "t_" + trips[i].vehicle[0];
            
            write_step("`" + trips[i].d_str  + " = ` distance that Alice traveled by " + trips[i].vehicle);  
            
            if (i) {
                total_d_str += " + ";                
                total_t_str += " + ";
                separate_t_str += " `and` ";
            }
            
            total_d_str += trips[i].d_str;
            total_t_str += trips[i].t_str;
            
            var time_str = "(" + trips[i].d_str + ") / " + trips[i].rate;
            trips[i].time_str = time_str;
            
            separate_t_str += "`" + trips[i].t_str + " = " + time_str + "`";
        }
        
        // "Total distance: d_b + d_t = D"
        // "Total time: t_b + t_t = T"
        // "t_b = d_b / r_b and t_t = d_t / r_t"
        write_step(total_d_str + " = " + trips.distance + "`</span>");
        write_step(total_t_str + " = " + trips.time + "`</span>");
        write_step(separate_t_str + "</span>");        
    }
    
    function substituteEquations() {
        // "Substitute the blue equations for: d_b / r_b + d_t / r_b = T"
        var str = "Substitute the blue equations for: `";
        for (var i = 0; i < trips.length ; i++) {
            if (i)
                str += " + ";
            str += trips[i].time_str;
        }
        str += " = " + trips.time + "`";
        write_step(str);
    }
    
    function multiplyEquations() {
        // "Multiply the above equation by -r_b for: -d_b - ...."
        var str = "<span class='hint_orange'> ` - " + trips[0].d_str;
        str += format_fraction(-trips[0].rate, trips[1].rate) + trips[1].d_str;
        trips.rhs = -trips[0].rate * trips.time;
        
        write_step("Multiply the above equation by ` - " + trips[0].rate + "` for: " + str + " = " + trips.rhs + " ` </span>");
    }
    
    function simplifyEquations() {
        var numerator = trips[1].rate - trips[0].rate;
        var denominator = trips[1].rate;
        trips.rhs = trips.distance + trips.rhs;

        write_step("Add the two orange equations for: `" + format_fraction(numerator, denominator) 
                + trips[1].d_str + " = " + trips.rhs + "`");

        var t_0 = Math.round(trips[0].distance / trips[0].rate * 60);
        var t_1 = Math.round(trips[1].distance / trips[1].rate * 60);
                                
        write_step("Simplify and round to the nearest integer: `" + trips[1].d_str + " = " + Math.round(trips[1].distance) + "` miles`; " 
                    + trips[0].d_str + " = " + Math.round(trips[0].distance) + "` miles`; "
                    + trips[0].t_str + " = " + t_0 + "` minutes`; "
                    + trips[1].t_str + " = " + t_1 + "` minutes");
    }

    // A few fun methods of transportation.
    function getFirstVehicle() {
        switch (get_random() % 4) {
            case 0:
                return "bike";
            case 1:
                return "bus";
            case 2:
                return "camel";
            default:
                return "elephant";
        }
    }
    
    function getSecondVehicle() {
        switch (get_random() % 4) {
            case 0:
                return "horse";
            case 1:
                return "moped";
            case 2:
                return "scooter";
            default:
                return "train";                
        }
    }
}
