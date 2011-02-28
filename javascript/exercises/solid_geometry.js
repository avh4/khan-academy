// Solid geometry
// Author: Desmond Brand
// Date: 2011-02-28
//
// Problem spec:
// http://www.youtube.com/watch?v=O-heDHKPNCI
//
// Problem layout:
// Find the volume and surface area of cylinders, cubes and triangular prisms.
//

var SolidGeometryExercise = {
    problem: null,
    
    init: function() {
        //pick a random problem type
        var problemType = randomMember([
            SolidGeometryExercise.CylinderVolume,
            SolidGeometryExercise.CylinderSurfaceArea,
            SolidGeometryExercise.CubeVolume,
            SolidGeometryExercise.CubeSurfaceArea,
            SolidGeometryExercise.TriangularPrismVolume
        ]);
        problem = new problemType();
        
        writeText(problem.questionText());
        
        for(var i = 0; i<problem.hints.length; i++) {
            writeStep(problem.hints[i].toString());
        }
        
        setCorrectAnswer('``' + problem.answer().toString() + '``');
        for(var i = 0; i<problem.wrongAnswers.length; i++)
            addWrongChoice('``' + problem.wrongAnswers[i].apply(problem).toString() + '``');
    },
    
    graphUpdate: function() {
        problem.draw(present);
    },
    
    getHint: function() {
        if(steps_given < problem.hints.length) {
            give_next_step();
            var fn = problem.hints[steps_given-1].fn;
            if(fn) fn(problem);
        }
    }
};

(function(sge) {
    // vector class for dealing with polynomail expressions. Only tested with degree <= 1 so far!
    sge.Vector = function(number, factor) {
        if(number instanceof Array)
            this.number = number;
        else {
            // doesn't make a lot of sense to create a vector with only a 
            // constant, so Vector(scalar, factor) gives scalar * factor.
            this.number = [0, number]; 
        }
        this.factor = factor;
        
        this.copy = function() {
            return new sge.Vector(this.number.slice(), this.factor);
        };
        
        // print out a human readable polynomial.
        this.toString = function() {
            var first = true;
            var s = '';
            for(var i = this.number.length-1; i>=0; i--) {
                if(!this.number[i] || this.number[i]==0) {
                    continue;
                }
                
                if(first) {
                    if (this.number[i] < 0)
                        s += '-';
                    first = false;
                }
                else {
                    if(this.number[i] > 0)
                        s += ' + ';
                    else if (this.number[i] < 0)
                        s += ' - ';
                }
                
                var n = Math.abs(this.number[i]);
                if(n!=1)
                    s += n;
                
                if(i > 0)
                    s += factor;
                
                if(i>1)
                    s += '^' + i;
            }
            return s;
        };
        this.multiply = function(scalar) {
            var n = this.copy();
            for(var i = 0; i<n.number.length; i++)
                n.number[i] *= scalar;
            return n;
        };
        this.divide = function(scalar) {
            var n = this.copy();
            for(var i = 0; i<n.number.length; i++)
                n.number[i] /= scalar;
            return n;
        };
        this.add = function(vector) {
            if(this.factor != vector.factor) console.log('wrong factors', this, vector);
            var n = this.copy();
            for(var i = 0; i<n.number.length; i++)
                n.number[i] += vector.number[i];
            return n;
        };
        this.subtract = function(vector) {
            if(this.factor != vector.factor) console.log('wrong factors', this, vector);
            var n = this.copy();
            for(var i = 0; i<n.number.length; i++)
                n.number[i] -= vector.number[i];
            return n;
        };
    };
    
    sge.drawing = {
        distanceLabel: function(start, end, label) {
            var x1 = start[0];
            var y1 = start[1];
            var x2 = end[0];
            var y2 = end[1];
            
            var m = (y2-y1)/(x2-x1);
            var c = y1 - m*x1;
            
            var xm = (x1+x2)/2;
            var ym = (y1+y2)/2;
            
            if(Math.abs(m) <= 1) {
                x1b = xm-0.1;
                y1b = m*x1b + c;
                
                x2b = xm+0.1;
                y2b = m*x2b + c;
            }
            else {
                y1b = ym+0.1;
                y2b = ym-0.1;
                if(Math.abs(m) == Infinity) {
                    x1b = x2b = x1;
                }
                else {
                    x1b = (y1b-c)/m;
                    x2b = (y2b-c)/m;
                }
            }
    
            present.marker = "arrow";
    
            present.line([x1b, y1b], [x1, y1]);
            present.line([x2b, y2b], [x2, y2]);
            present.text([xm, ym+.05], label);
        },
        
        hiddenLine: {'stroke-dasharray': '. ', 'stroke-width': 1}
    };
    
    sge.Hint = function(text, fn) {
        this.text = text;
        this.fn = fn;
        this.toString = function() { return this.text; };
    };
    
    sge.Cylinder = function() {
            this.height = nonZeroRandomInt(3, 9);
            this.radius = nonZeroRandomInt(2, 6);
            this.baseArea = function() {
                return new sge.Vector(this.radius*this.radius, 'pi');
            };
            this.baseCircumference = function() {
                return new sge.Vector(2*this.radius, 'pi');
            };
            this.sideArea = function() {
                return this.baseCircumference().multiply(this.height);
            };
            this.surfaceArea = function() {
                return this.baseArea().multiply(2).add(this.sideArea());
            };
            this.volume = function() {
                return this.baseArea().multiply(this.height);
            };
            this.draw = function(gfx) {
                gfx.setBorder(0);
                gfx.initPicture(-2,2).attr({stroke: '#fff'});
                this.drawing.cylinderWithLabels([0, 0], 1, 2.5);
            };
            
            this.drawing = {
                cylinder: function(position, r, h) {
                    var x = position[0];
                    var y = position[1];
                    var hh = h/2;
                    var ellipse_ratio = 1/4;
    
                    present.stroke = "blue";
                    this.topSurface = present.ellipse([x,y+hh],r,r*ellipse_ratio);
                    
                    present.arc_elliptical([x-r,y-hh],[x+r,y-hh],r,r*ellipse_ratio);
                    present.arc_elliptical([x+r,y-hh],[x-r,y-hh],r,r*ellipse_ratio)
                           .attr(sge.drawing.hiddenLine);
                    present.line([x-r, y+hh], [x-r, y-hh]);
                    present.line([x+r, y-hh], [x+r, y+hh]);
                    
                    present.strokewidth = 0;
                    this.bottomSurface = present.ellipse([x,y-hh],r,r*ellipse_ratio)
                },
                
                fillTopSurface: function() {
                    this.topSurface.attr({fill: '320-#2D3D9D-#7A88D9', 'fill-opacity': .1});
                },
                
                fillBottomSurface: function() {
                    this.bottomSurface.attr({fill: '320-#2D3D9D-#7A88D9', 'fill-opacity': .01});
                },
    
                cylinderWithLabels: function(position, r, h) {
                    this.cylinder(position, r, h);
    
                    var x = position[0];
                    var y = position[1];
                    var hh = h/2;
    
                    present.stroke = "red";
                    present.strokewidth = "2";
                    present.fontweight = "bold";
                    this.radiusLabel([x, y+hh], r);
                    sge.drawing.distanceLabel([x+r+.2, hh] , [x+r+.2, -hh], 'h');
                },
    
                radiusLabel: function(position, r) {
                    var x = position[0];
                    var y = position[1];
                    present.marker = "arrow";
                    present.line([x,y], [x+r,y]);
                    present.dot([x,y], "closed");
                    var xpad = 0.1;
                    var ypad = 0.2;
                    present.text([x+r/2-xpad, y+ypad], "r");
                }
            };
        };
    
        sge.CylinderVolume = function() {
            this.questionText = function() {
                return 'Shown is a cylinder. If the radius `r` of the base of the ' +
                       'cylinder is `' + this.radius + '` and the height `h` is `' + 
                       this.height + '`, what is the total volume of the cylinder?';
            };
            this.answer = this.volume;
            this.wrongAnswers = [
                this.surfaceArea,
                this.baseArea,
                function() { return new sge.Vector(this.height + 2*this.radius, 'pi'); },
                function() { return this.answer().add(new sge.Vector(nonZeroRandomInt(1, 2*this.height), 'pi')); },
                function() { return this.answer().subtract(new sge.Vector(nonZeroRandomInt(1, 2*this.radius), 'pi')); }
            ];
            this.hints = [
                new sge.Hint(
                    "The area of the base (shaded) is `pir^2 = pi("+ this.radius +")^2 = "+this.baseArea()+"`",
                    function(problem) {
                        problem.drawing.fillTopSurface();
                    }
                ),
                "The volume of the cylinder is equal to the area of the base times the height or `"+this.baseArea()+"*6 = "+this.volume()+"`"
            ];
        };
    sge.CylinderVolume.prototype = new SolidGeometryExercise.Cylinder();
    
    sge.CylinderSurfaceArea = function() {
        this.questionText = function() {
            return 'Shown is a cylinder. If the radius `r` of the base of the ' +
                   'cylinder is `' + this.radius + '` and the height `h` is `' + 
                   this.height + '`, what is the total surface area of the cylinder?';
        };
        this.answer = this.surfaceArea;
        this.wrongAnswers = [
            this.volume,
            function() { return this.baseArea().multiply(3); },
            function() { return new sge.Vector(this.height + 2 * this.radius, 'pi'); },
            function() { return this.answer().add(new sge.Vector(nonZeroRandomInt(1, 2*this.height), 'pi')); },
            function() { return this.answer().subtract(new sge.Vector(nonZeroRandomInt(1, 2*this.radius), 'pi')); }
        ];
        this.hints = [
            new sge.Hint(
                "The area of each base (the shaded area) is `pir^2 = pi(" + 
                    this.radius +")^2 = "+this.baseArea()+"`",
                function(problem) {
                    problem.drawing.fillTopSurface();
                    problem.drawing.fillBottomSurface();
                }
            ),
            "The area of the side of the cylinder is the circumference of the base " +
                "times the height (if you unrolled the sides, you would get a rectangle):<br/>" +
                "`2pi*r*h = 2pi*" + this.radius + '*' + this.height + ' = ' + 
                this.sideArea() + '`',
            'To get the total surface area, add up two bases and the side:<br/>' +
                '`2*' + this.baseArea() + ' + ' + this.sideArea() + ' = ' + this.surfaceArea() + '`'
        ];
    };
    sge.CylinderSurfaceArea.prototype = new SolidGeometryExercise.Cylinder();
    
    sge.Cube = function() {
        this.sidelength = nonZeroRandomInt(1, 10);
        this.sideArea = function() {
            return Math.pow(this.sidelength, 2);
        };
        this.surfaceArea = function() {
            return 6 * this.sideArea();
        };
        this.volume = function() {
            return Math.pow(this.sidelength, 3);
        };
        this.draw = function(gfx) {
            gfx.setBorder(0);
            gfx.initPicture(-2,2).attr({stroke: '#fff'});
            this.drawing.cube([-1.2, -1.2], 2);
        };
        
        this.drawing = {
            cube: function(position, l) {
                var x = position[0];
                var y = position[1];
                var offset = l/3;
    
                var fbl = position;
                var fbr = [x+l, y];
                var ftl = [x, y+l];
                var ftr = [x+l, y+l];
                
                var rbl = [fbl[0] + offset, fbl[1] + offset];
                var rbr = [fbr[0] + offset, fbr[1] + offset];
                var rtl = [ftl[0] + offset, ftl[1] + offset];
                var rtr = [ftr[0] + offset, ftr[1] + offset];
                
                
                present.stroke = "blue";
                present.rect(fbl, ftr);
                
                present.line(fbl, rbl).attr(sge.drawing.hiddenLine);
                present.line(fbr, rbr);
                present.line(ftl, rtl);
                present.line(ftr, rtr);
    
                present.line(rbl, rbr).attr(sge.drawing.hiddenLine);
                present.line(rbl, rtl).attr(sge.drawing.hiddenLine);
                present.line(rtr, rtl);
                present.line(rtr, rbr);
                
                present.stroke = "red";
                present.strokewidth = "2";
                present.fontweight = "bold";
                sge.drawing.distanceLabel([x-.2, y+l], [x-.2, y], 'x');
                sge.drawing.distanceLabel([x, y-.2], [x+l, y-.2], 'x');
                sge.drawing.distanceLabel([rtl[0]-.12, rtl[1]+.12], [ftl[0]-.12, ftl[1]+.12], 'x');
            }
        };
    };
    
    sge.CubeVolume = function() {
        this.questionText = function() {
            return 'Shown is a cube. If each side is of equal length `x = ' + 
                    this.sidelength + '`, what is the total volume of the cube?';
        };
        this.answer = this.volume;
        this.wrongAnswers = [
            this.surfaceArea,
            function() { return this.surfaceArea() / nonZeroRandomInt(2, 3); },
            function() { return this.answer() + this.sideArea(); },
            function() { return this.answer() - this.sidelength; },
            function() { return this.answer() - this.sidelength - 1; },
            function() { return this.answer() + nonZeroRandomInt(1, 2); },
            function() { return this.answer() - nonZeroRandomInt(1, 2); }
        ];
        this.hints = [
            "The volume `V` of a cube is the cube of the side length: `V = x^3 = x*x*x`",
            "`V = x^3 = ("+this.sidelength+")^3 = ("+this.sidelength+")("+this.sidelength+")("+this.sidelength+") = "+this.answer()+"`"
        ];
    };
    sge.CubeVolume.prototype = new SolidGeometryExercise.Cube();
    
    sge.CubeSurfaceArea = function() {
            this.questionText = function() {
            return 'Shown is a cube. If each side is of equal length `x = ' + 
                   this.sidelength + '`, what is the total surface area of the cube?';
        };
        this.answer = this.surfaceArea;
        this.wrongAnswers = [
            this.volume,
            function() { return this.answer() + this.sidelength; },
            function() { return 6*this.sidelength; },
            function() { return 4*this.sideArea(); },
            function() { return this.answer() - this.sideArea() - 1; },
            function() { return this.answer() + nonZeroRandomInt(1, 3)*2; },
            function() { return this.answer() - nonZeroRandomInt(1, 3)*2; }
        ];
        this.hints = [
            "The area of one side of the cube is `A = x^2`",
            "The total surface area of a cube is six times the area of one side: `TSA = 6x^2`",
            "The total surface area of this cube is `TSA = 6("+this.sidelength+")^2 = "+this.surfaceArea()+"`"
        ];
    };
    sge.CubeSurfaceArea.prototype = new SolidGeometryExercise.Cube();
    
    sge.TriangularPrism = function() {
        this.width = nonZeroRandomInt(2, 7);
        this.height = nonZeroRandomInt(2, 4);
        this.length = nonZeroRandomInt(4, 9);
        this.sideArea = function() {
            return 0.5*this.width*this.height;
        };
        this.volume = function() {
            return this.sideArea() * this.length;
        };
        this.draw = function(gfx) {
            gfx.setBorder(0);
            gfx.initPicture(-2,2).attr({stroke: '#fff'});
            this.drawing.triangularPrism([-1.25, -.5], 2, 1, 3);
        };
        
        this.drawing = {
            triangularPrism: function(position, w, h, l) {
                var x = position[0];
                var y = position[1];
                var offset = l/3;
    
                var ft = [x + w/3, y + h];
                var fl = [x, y];
                var fr = [x+w, y];
                
                var rt = [ft[0] + offset, ft[1] + offset];
                var rl = [fl[0] + offset, fl[1] + offset];
                var rr = [fr[0] + offset, fr[1] + offset];
                
                
                present.stroke = "blue";
                present.line(fl, ft);
                present.line(ft, fr);
                present.line(fl, fr);
                
                present.strokewidth = 1;
                present.line(rl, rt).attr(sge.drawing.hiddenLine);
                present.line(rt, rr);
                present.line(rl, rr).attr(sge.drawing.hiddenLine);
                
                present.line(fl, rl).attr(sge.drawing.hiddenLine);
                present.line(fr, rr);
                present.line(ft, rt);
                
                present.stroke = "red";
                present.strokewidth = "2";
                present.fontweight = "bold";
                sge.drawing.distanceLabel([fl[0]-.2, fl[1]+h], [fl[0]-.2, fl[1]], 'h');
                sge.drawing.distanceLabel([fl[0], fl[1]-.2], [fr[0], fr[1]-.2], 'b');
                sge.drawing.distanceLabel([rr[0]+.15, rr[1]-.1], [fr[0]+.15, fr[1]-.1], 'l');
            }
        };
    };
    
    sge.TriangularPrismVolume = function() {
        this.questionText = function() {
            return 'Shown is a triangular prism. If the base of the triangle `b = '+this.width+
                    '`, the height of the triangle `h = '+this.height+'`, and the length of the '+
                    'prism `l = '+this.length+'`, what is the total volume of the prism?';
        };
        this.answer = this.volume;
        this.wrongAnswers = [
            function() { return 2*this.sideArea() + this.length; },
            function() { return 2*this.answer(); },
            function() { return .5*this.answer(); },
            function() { return Math.pow(this.length, 2)*this.height; },
            function() { return this.answer() + nonZeroRandomInt(1, 4); },
            function() { return this.answer() - nonZeroRandomInt(1, 4); }
        ];
        this.hints = [
            'The area of the triangular face is `A = 1/2*b*h`',
            '`A = 1/2*b*h = 1/2*('+this.width+')*('+this.height+') = '+this.sideArea()+'`',
            'The volume of the prism is equal to the area of the face times the length:<br>'+
                '`V = A*l = '+this.sideArea()+'*'+this.length+' = '+this.volume()+'`'
        ];
    };
    sge.TriangularPrismVolume.prototype = new SolidGeometryExercise.TriangularPrism();
    
})(SolidGeometryExercise);

