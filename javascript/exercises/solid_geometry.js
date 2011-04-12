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
            SolidGeometryExercise.RectangleVolume,
            SolidGeometryExercise.RectangleSurfaceArea,
            SolidGeometryExercise.TriangularPrismVolume
        ]);
        problem = new problemType();
        
        problem.init();
        
        writeText(problem.questionText());
        
        for(var i = 0; i<problem.hints.length; i++) {
            writeStep(problem.hints[i].toString());
        }
        
        this.setupShortAnswer();
    },
    
    setupShortAnswer: function() {
        var answer = problem.answer();
        if(answer.substitute) {
            answer = answer.substitute(1);
        }
        setCorrectAnswer(answer);
    },
    
    graphUpdate: function() {
        problem.draw(present);
    },
    
    getHint: function() {
        if(Exercise.steps_given < problem.hints.length) {
            give_next_step();
            var fn = problem.hints[Exercise.steps_given-1].fn;
            if(fn) fn(problem);
        }
    }
};

(function(sge) {
    // vector class for dealing with polynomail expressions. Only tested with degree <= 1 so far!
    sge.Vector = function(number, factor) {
        if(number.length)
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
        this.substitute = function(x) {
            var fx = 0;
            for(var i = 0; i<this.number.length; i++)
                fx += this.number[i] * Math.pow(x, i);
            return fx;
        };
    };
    
    sge.Point = function(x, y) {
        if(x instanceof Array) {
            this.x = x[0];
            this.y = x[1];
        }
        else {
            this.x = x;
            this.y = y;
        }
        
        this.add = function(other) { return new sge.Point(this.x + other.x, this.y + other.y); };
        this.subtract = function(other) { return new sge.Point(this.x - other.x, this.y - other.y); };
        this.multiply = function(scalar) { return new sge.Point(this.x*scalar, this.y*scalar); };
        this.divide = function(scalar) { return new sge.Point(this.x/scalar, this.y/scalar); };
        this.toArray = function() { return [this.x, this.y]; };
        this.gradient = function() { return this.y/this.x; };
        this.toString = function() { return "("+this.x+", "+this.y+")"; };
    };
    
    sge.drawing = {
        distanceLabel: function(start, end, label) {
            var p1, p2;
            if(start[0] < end[0] || start[0] == end[0] && start[1] < end[1]) {
                p1 = new sge.Point(start);
                p2 = new sge.Point(end);
            }
            else {
                p1 = new sge.Point(end);
                p2 = new sge.Point(start);
            }
            
            var m = p2.subtract(p1).gradient();
            var c = p1.y - m*p1.x;
            
            var pm = p1.add(p2).divide(2);
            
            var p1b, p2b;
            if(Math.abs(m) <= 1) {
                var x = pm.x-0.1;
                p1b = new sge.Point(x, m*x + c);
                
                x = pm.x+0.1;
                p2b = new sge.Point(x, m*x + c);
            }
            else {
                var p1b = new sge.Point(0, pm.y-0.1);
                var p2b = new sge.Point(0, pm.y+0.1);
                
                if(Math.abs(m) == Infinity) {
                    p1b.x = p2b.x = p1.x;
                }
                else {
                    p1b.x = (p1b.y-c)/m;
                    p2b.x = (p2b.y-c)/m;
                }
            }
            present.marker = "arrow";
            
            present.line(p1b.toArray(), p1.toArray());
            present.line(p2b.toArray(), p2.toArray());
            present.text(pm.add(new sge.Point(0, .05)).toArray(), label);
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
                var ratio = this.drawing.normalize(3.5, this.radius, this.height);
                this.drawing.cylinderWithLabels([0, 0], this.radius/ratio, this.height/ratio);
            };
            this.init = function() {
                $(function() {$('.multiple_of_pi').show()});
            };
            
            this.drawing = {
                normalize: function(max, r, h) {
                    var y = h + 2*r/4 + 1/3;
                    var x = 2*r + 1/3;
                    return Math.max(x, y)/max;
                },
                cylinder: function(position, rx, h) {
                    var x = position[0];
                    var y = position[1];
                    var hh = h/2;
                    var ellipse_ratio = 1/4;
                    var ry = rx * ellipse_ratio;
    
                    present.stroke = "blue";
                    this.topSurface = present.ellipse([x,y+hh],rx,ry);
                    
                    // bottom surface
                    present.arc_elliptical([x-rx,y-hh],[x+rx,y-hh],rx,ry);
                    present.arc_elliptical([x+rx,y-hh],[x-rx,y-hh],rx,ry)
                           .attr(sge.drawing.hiddenLine);
                    
                    // sides
                    present.line([x-rx, y+hh], [x-rx, y-hh]);
                    present.line([x+rx, y-hh], [x+rx, y+hh]);
                    
                    // the rest have invisible edges for shading only
                    present.strokewidth = 0;
                    
                    this.bottomSurface = present.ellipse([x,y-hh],rx,ry);
                    
                    // side surface
                    var path = "";
                    path += "M" + present.coord(x-rx, y+hh);
                    path += " L" + present.coord(x-rx, y-hh);
                    
                    path += " A" + present.xscale(rx) + "," + present.yscale(ry);
                    path += " 0 0,0 ";
                    path += present.coord(x+rx, y-hh);
                    
                    path += " L " + present.coord(x+rx, y+hh);
                    
                    path += " A" + present.xscale(rx) + "," + present.yscale(ry);
                    path += " 0 1,1 ";
                    path += present.coord(x-rx, y+hh);
                    
                    path += "z";
                    
                    this.sideSurface = present.paper.path().attr({
                        path: path,
                        'stroke-width': 0
                    });
                },
                
                fillTopSurface: function(fill) {
                    if(fill)
                        this.topSurface.attr({fill: '320-#2D3D9D-#7A88D9', 'fill-opacity': .1});
                    else
                        this.topSurface.attr({fill: 'none'});
                },
                
                fillBottomSurface: function(fill) {
                    if(fill)
                        this.bottomSurface.attr({fill: '320-#2D3D9D-#7A88D9', 'fill-opacity': .01});
                    else
                        this.bottomSurface.attr({fill: 'none'});
                },
                
                fillSideSurface: function(fill) {
                    if(fill)
                        this.sideSurface.attr({fill: '0-#7A88D9-#2D3D9D:31-#7A88D9', 'fill-opacity': 1});
                    else
                        this.sideSurface.attr({fill: 'none'});
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
            this.hints = [
                new sge.Hint(
                    "The area of the base (shaded) is:<br/> `A = pir^2 = pi("+ this.radius +")^2 = "+this.baseArea()+"`",
                    function(problem) {
                        problem.drawing.fillTopSurface(true);
                    }
                ),
                "The volume of a prism is equal to the area of the base times the height:<br/>`V = A*h`",
                "`V = "+this.baseArea()+"*"+this.height+" = "+this.volume()+"`"
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
        this.hints = [
            new sge.Hint(
                "The area of each of the bases (the shaded areas) is:<br/>" + 
                    "`pir^2 = pi("+this.radius+")^2 = "+this.baseArea()+"`",
                function(problem) {
                    problem.drawing.fillTopSurface(true);
                    problem.drawing.fillBottomSurface(true);
                }
            ),
            new sge.Hint(
                "The area of the side of the cylinder is the circumference of the base " +
                    "times the height (if you unrolled the sides, you would get a rectangle):<br/>" +
                    "`2pi*r*h = 2pi*" + this.radius + '*' + this.height + ' = ' + 
                    this.sideArea() + '`',
                function(problem) {
                    problem.drawing.fillTopSurface(false);
                    problem.drawing.fillBottomSurface(false);
                    problem.drawing.fillSideSurface(true);
                }
            ),
            new sge.Hint(
                'To get the total surface area, add up the two bases and the side:<br/>' +
                    '`2*' + this.baseArea() + ' + ' + this.sideArea() + ' = ' + this.surfaceArea() + '`',
                function(p) {
                    p.drawing.fillSideSurface(false);
                }
            )
        ];
    };
    sge.CylinderSurfaceArea.prototype = new SolidGeometryExercise.Cylinder();
    
    sge.Rectangle = function() {
        this.width = nonZeroRandomInt(1, 6);
        this.height = nonZeroRandomInt(1, 6);
        this.length = nonZeroRandomInt(3, 9);
        this.widthLabel = 'w';
        this.heightLabel = 'h';
        this.lengthLabel = 'l';
        this.frontArea = function() {
            return this.width * this.height;
        };
        this.sideArea = function() {
            return this.length * this.height;
        };
        this.topArea = function() {
            return this.width * this.length;
        };
        this.surfaceArea = function() {
            return 2*this.frontArea() + 2*this.sideArea() + 2*this.topArea();
        };
        
        this.volume = function() {
            return this.width * this.height * this.length;
        };
        this.draw = function(gfx) {
            gfx.setBorder(0);
            gfx.initPicture(-2,2).attr({stroke: '#fff'});
            var ratio = this.drawing.normalize(3.5, this.width, this.height, this.length);
            this.drawing.rectangle([-1.6, -1.6], this.width/ratio, this.height/ratio, this.length/ratio,
                                                 this.widthLabel, this.heightLabel, this.lengthLabel);
        };
        this.init = function() {};
        
        this.drawing = {
            normalize: function(max, w, h, l) {
                var y = h + l/3 + 1/3;
                var x = w + l/3 + 1/3;
                return Math.max(x, y)/max;
            },
            rectangle: function(position, w, h, l, widthLabel, heightLabel, lengthLabel) {
                widthLabel =  widthLabel || "x";
                heightLabel =  heightLabel || "x";
                lengthLabel =  lengthLabel || "x";
                
                var x = position[0];
                var y = position[1];
                var offset = l/3;
    
                var fbl = position;
                var fbr = [x+w, y];
                var ftl = [x, y+h];
                var ftr = [x+w, y+h];
                
                var rbl = [fbl[0] + offset, fbl[1] + offset];
                var rbr = [fbr[0] + offset, fbr[1] + offset];
                var rtl = [ftl[0] + offset, ftl[1] + offset];
                var rtr = [ftr[0] + offset, ftr[1] + offset];
                
                
                present.stroke = "blue";
                this.frontSurface = present.rect(fbl, ftr);
                
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
                sge.drawing.distanceLabel([x-.2, y], [x-.2, y+h], heightLabel);
                sge.drawing.distanceLabel([x, y-.2], [x+w, y-.2], widthLabel);
                sge.drawing.distanceLabel([ftl[0]-.12, ftl[1]+.12], [rtl[0]-.12, rtl[1]+.12], lengthLabel);
            },
            
            fillFrontSurface: function(fill) {
                if(fill)
                    this.frontSurface.attr({fill: '170-#2D3D9D-#7A88D9', 'fill-opacity': .1});
                else
                    this.frontSurface.attr({fill: 'none'});
            }
        };
    };
    
    sge.RectangleVolume = function() {
        this.questionText = function() {
            return 'Shown is a rectangular prism. If the width is `w = ' + 
                    this.width + '`, the height is `h = '+this.height+'`, and the '+
                    'length is `l = '+this.length+'`, what is the total volume?';
        };
        this.answer = this.volume;
        this.hints = [
            new sge.Hint(
                "Like any other prism, to calculate the volume of a rectangular prism you first need to find " + 
                    'the area of a face. Start with the area of the front face.',
                function(p) {
                    p.drawing.fillFrontSurface(true);
                }
            ),
            '`A = w*h = ('+this.width+')('+this.height+')='+this.frontArea()+'`',
            'Now multiply the area of the face with the length of the prism:<br/>' +
                '`V = A*l = ('+this.frontArea()+')('+this.length+') = '+this.answer()+'`<br/><br/>' +
            "As a shortcut, for a rectangular prism you can just multiply all three side lengths together:<br/>"+
                "`V = w*h*l = ("+this.width+")("+this.height+")("+this.length+") = "+this.answer()+"`"
        ];
    };
    sge.RectangleVolume.prototype = new SolidGeometryExercise.Rectangle();
    
    sge.RectangleSurfaceArea = function() {
        this.questionText = function() {
            return 'Shown is a rectangular prism. If the width is `w = ' + 
                    this.width + '`, the height is `h = '+this.height+'`, and the '+
                    'length is `l = '+this.length+'`, what is the total surface area?';
        };
        this.answer = this.surfaceArea;
        this.hints = [
            'There are 3 different kinds of side areas on a rectangular prism, each of which occurs twice.',
            "`TSA = 2wh + 2wl + 2hl",
            "`TSA = 2("+this.width+")("+this.height+") + " + " 2("+this.width+")("+this.length+") + " + 
                "2("+this.height+")("+this.length+") = " + this.answer()+"`"
        ];
    };
    sge.RectangleSurfaceArea.prototype = new SolidGeometryExercise.Rectangle();
    
    sge.Cube = function() {
        this.width = this.height = this.length = nonZeroRandomInt(1, 6);
        this.widthLabel = this.heightLabel = this.lengthLabel = 'x';
    };
    sge.Cube.prototype = new sge.Rectangle();
    
    sge.CubeVolume = function() {
        this.questionText = function() {
            return 'Shown is a cube. If each side is of equal length `x = ' + 
                    this.width + '`, what is the total volume of the cube?';
        };
        this.answer = this.volume;
        this.hints = [
            "The volume `V` of a cube is the cube of the side length: `V = x^3 = x*x*x`",
            "`V = x^3 = ("+this.width+")^3 = ("+this.width+")("+this.width+")("+this.width+") = "+this.answer()+"`"
        ];
    };
    sge.CubeVolume.prototype = new SolidGeometryExercise.Cube();
    
    sge.CubeSurfaceArea = function() {
            this.questionText = function() {
            return 'Shown is a cube. If each side is of equal length `x = ' + 
                   this.width + '`, what is the total surface area of the cube?';
        };
        this.answer = this.surfaceArea;
        this.hints = [
            new sge.Hint(
                "The area of one side of the cube is:<br/> `A = x^2`",
                function(p) {
                    problem.drawing.fillFrontSurface(true);
                }
            ),
            "The total surface area of a cube is six times the area of one side:<br/> `TSA = 6A = 6x^2`",
            "`TSA = 6("+this.width+")^2 = "+this.surfaceArea()+"`"
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
            var ratio = this.drawing.normalize(2.5, this.width, this.height, this.length);
            this.drawing.triangularPrism([-1.25, -.5], this.width/ratio, this.height/ratio, this.length/ratio);
        };
        this.init = function() {};
        
        this.drawing = {
            normalize: function(max, b, h, l) {
                var y = h + l/3 + 1/3;
                var x = b + l/3 + 1/3;
                return Math.max(x, y)/max;
            },
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
                // side surface
                var path = "";
                path += "M" + present.coord(fl);
                path += " L" + present.coord(ft);
                path += " L" + present.coord(fr);
                path += "z";
                
                this.frontSurface = present.paper.path().attr({
                    path: path,
                    stroke: present.stroke
                });
                
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
            },
            
            fillFrontSurface: function(fill) {
                if(fill)
                    this.frontSurface.attr({fill: '10-#2D3D9D-#7A88D9', 'fill-opacity': .1});
                else
                    this.frontSurface.attr({fill: 'none'});
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
        this.hints = [
            new sge.Hint(
                'The area of the triangular face is:<br/> `A = 1/2*b*h`',
                function(p) {
                    p.drawing.fillFrontSurface(true);
                }
            ),
            '`A = 1/2*('+this.width+')*('+this.height+') = '+this.sideArea()+'`',
            'The volume of the prism is equal to the area of the face times the length:<br>'+
                '`V = A*l = '+this.sideArea()+'*'+this.length+' = '+this.volume()+'`'
        ];
    };
    sge.TriangularPrismVolume.prototype = new SolidGeometryExercise.TriangularPrism();
    
})(SolidGeometryExercise);

