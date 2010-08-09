var toDraw = {};
var randInt = getRandomIntRange(5,9);

var drawFunction = null;
var color1 = getNextColor();
var color2 = getNextColor();
var color3 = getNextColor();
var pointRegister = new Array();
var angleRegister = new Array();
var graphicalHints = new Array();
var initialObjectsToDraw  = new Array();

var sqr2div2 = Math.sqrt(2)/2;

var defaultColor = "black";

function colorString(string, color)
{
	return '<font color=\"'+color+'\">'+string+'</font>';	
}

hColors = ['#D9A326', '#E8887D', '#9CC9B7', '#AE9CC9', '#EAADEA', '#CD8C95', '#CFD784'];


function getSlope(p1, p2)
{
	if (p2.x==p1.x)
		return null;
	else
		return (p2.y-p1.y)/(p2.x-p1.x);	
}

function getDistance(p1,p2)
{
	return (Math.sqrt(Math.pow(p1.y-p2.y,2)+Math.pow(p1.x-p2.x, 2)));
}


var pointLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z'];
var nextPointIndex = getRandomIntRange(0,pointLabels.length-1);

function getNextLabel()
{
	nextPointIndex = (nextPointIndex+1)%pointLabels.length;
	return pointLabels[nextPointIndex];
}


function graphPoint(x,y, labelPosition)
{
	
	this.x = x;
	this.y = y;
	this.coor = [this.x,this.y];
	this.label = getNextLabel();
	this.handle = 'p_'+this.label;
	this.color = getNextColor();
	this.labelPosition = labelPosition;
	this.regStr = this.label;  
	this.colorStr = colorString(this.label,this.color);
	
		
	
	
	this.drawInColor = function()
	{
		present.fontfill = this.color;
		present.text([this.x,this.y], this.label, this.labelPosition, this.handle);
	}
	
	this.drawInOtherColor = function(color)
	{
		present.fontfill = color;
		present.text([this.x,this.y], this.label, this.labelPosition, this.handle);
	}
	
	this.draw = function()
	{
		present.fontfill = defaultColor;
		present.text([this.x,this.y], this.label, this.labelPosition, this.handle);
	}
	
	pointRegister.push(this);
}


function graphAngle(p1,vertex, p2) //p1 should be counter clockwise from p2 and less than 180 deg away
{
	this.color = getNextColor();
	this.startLine = new graphLine(vertex, p2);
	this.endLine = new graphLine(vertex, p1);

	this.p1 = p1;
	this.p2 = p2;
	this.vertex = vertex;
	this.regStr = '<B>&ang;'+p1.regStr+vertex.regStr+p2.regStr+'</B>';
	this.colorStr = colorString(this.regStr, this.color);
	this.handle = 'a_'+p1.regStr+vertex.regStr+p2.regStr;
	
	this.drawLinesInOtherColor = function(lines, color)
	{
		var baseShift = .15;
		var incrementalShift = .05;
		var startLine = new graphLine(vertex, p2);
		var endLine = new graphLine(vertex, p1);
		//alert([lines, color]);
		for(var i=0; i<lines; i++)
		{
			var howFarEnd = baseShift/this.endLine.getLength();
			var howFarStart = baseShift/this.startLine.getLength();
			
			var endX =  this.vertex.x + howFarEnd*(this.p1.x-this.vertex.x);
			var startX = this.vertex.x + howFarStart*(this.p2.x-this.vertex.x);
			var endY = this.vertex.y + howFarEnd*(this.p1.y-this.vertex.y);
			var startY = this.vertex.y + howFarStart*(this.p2.y-this.vertex.y);
			
			present.stroke = color;
			//alert([startX, startY, endX, endY, this.handle]);
			present.arc([startX, startY], [endX, endY], baseShift,this.handle+i);
			baseShift+=incrementalShift;
		}
	}
	
	
	this.eraseLines = function(lines)
	{
		for(var i=0; i<lines; i++)
		{
			
			present.line([-500, -500], [-500, -500],this.handle+i);
		}
		
	}
	
	
	this.drawLinesInColor = function(lines)
	{
		
		this.drawLinesInOtherColor(lines, this.color);
	}
	
	this.drawLines = function(lines)
	{
		this.drawLinesInOtherColor(lines, defaultColor);
	}
	
	this.draw = function()
	{
		this.eraseLines(1);
		//this.drawLines(1);
	}
	this.drawInColor = function()
	{
		this.drawLinesInColor(1);
	}
	this.drawInOtherColor = function(color)
	{
		this.drawLinesInOtherColor(color);
	}
	angleRegister.push(this);
}

function equalAngles(angle1, angle2, lines)
{
	this.angle1 = angle1;
	this.angle2 = angle2;
	this.lines = lines;
	
	this.drawInColor = function()
	{
		this.angle1.drawLinesInColor(this.lines);
		this.angle2.drawLinesInColor(this.lines);
	}
	
	this.draw = function()
	{
		this.angle1.eraseLines(this.lines);
		this.angle2.eraseLines(this.lines);
	}
}

function graphRightAngle(p1,vertex, p2) //p1 should be counter clockwise from p2 and less than 180 deg away; assumes the edges are parrallel to the 
{
	this.color = getNextColor();
	this.startLine = new graphLine(vertex, p2);
	this.endLine = new graphLine(vertex, p1);

	this.p1 = p1;
	this.p2 = p2;
	this.vertex = vertex;
	
	this.allPoints = new Array(this.p1, this.p2, this.vertex);
	this.center = new graphPoint((this.p1.x+this.p2.x+this.vertex.x)/3, (this.p1.y+this.p2.y+this.vertex.y)/3);
	
	
	this.handle = 'a_'+p1.regStr+vertex.regStr+p2.regStr;
	this.regStr = '<B>&ang;'+p1.regStr+vertex.regStr+p2.regStr+'</b>';
	this.colorStr = colorString(this.regStr, this.color);
	
	this.drawInOtherColor = function(color)
	{
		var baseShift = .1;
		var startLine = new graphLine(vertex, p2);
		var endLine = new graphLine(vertex, p1);
		
	
		var howFarEnd = baseShift/endLine.getLength();
		var howFarStart = baseShift/startLine.getLength();
			
		var endShiftX = howFarEnd*(this.p1.x-this.vertex.x);
		var startShiftX = howFarStart*(this.p2.x-this.vertex.x);
		var endShiftY = howFarEnd*(this.p1.y-this.vertex.y);
		var startShiftY = howFarStart*(this.p2.y-this.vertex.y);
			
		var endX =  this.vertex.x + endShiftX;
		var startX = this.vertex.x + startShiftX;
		var endY = this.vertex.y + endShiftY;
		var startY = this.vertex.y + startShiftY;
		var midX = this.vertex.x + (endShiftX+startShiftX);
		var midY = this.vertex.y + (endShiftY+startShiftY);
			
		present.stroke = color;
		present.path([[endX, endY], [midX, midY], [startX, startY]]);
	}
	
	this.drawInColor = function()
	{
		this.drawInOtherColor(this.color);
	}
	
	this.draw = function()
	{
		this.drawInOtherColor(defaultColor);
	}
	
	
	this.rotate = function(axisPoint, degrees)
	{
		var rads = degrees*Math.PI/180;
		for(var k=0; k < this.allPoints.length; k++)
		{
			var curPoint = this.allPoints[k];
			var curLabelPosition = curPoint.labelPosition;
			curPoint.labelPosition = posArray[($.inArray(curLabelPosition,posArray)+Math.floor(degrees/45))%posArray.length];
			var distance = getDistance(axisPoint, curPoint);
			var curAngle = Math.atan2(curPoint.y-axisPoint.y, curPoint.x-axisPoint.x);
		
			var newAngle = curAngle+rads;
		
			curPoint.x = distance*Math.cos(newAngle);
			curPoint.y = distance*Math.sin(newAngle);
		
			curPoint.coor = [curPoint.x, curPoint.y];
		}
		this.center.x = (this.left.x+this.top.x+this.right.x)/3;
		this.center.y = (this.left.y+this.top.y+this.right.y)/3;
		this.center.coor = [this.center.x, this.center.y];
	}
	
	
	
	this.scale = function(factor)
	{
		for(var k=0; k<this.allPoints.length; k++)
		{
			var curPoint = this.allPoints[k];
			var distance = getDistance(this.center, curPoint);
			var curAngle = Math.atan2(curPoint.y-this.center.y, curPoint.x-this.center.x);
			
			var newDistance = distance * factor;
			
			curPoint.x = newDistance*Math.cos(curAngle);
			curPoint.y = newDistance*Math.sin(curAngle);
			curPoint.coor = [curPoint.x, curPoint.y];
		}
	}
	
	this.shift = function(xShift, yShift)
	{
		for(var k=0; k<this.allPoints.length; k++)
		{
			var curPoint = this.allPoints[k];
			curPoint.x += xShift;
			curPoint.y += yShift;
			curPoint.coor = [curPoint.x, curPoint.y];
		}
		
		this.center.x += xShift;
		this.center.y += yShift;
		this.center.coor = [this.center.x, this.center.y];
		
	}
	
	
	
	//angleRegister.push(this);	
}



function noLabelLine(start, end)
{
	this.line = new graphLine(start, end);
	
	
	
	this.drawInOtherColor = function(color)
	{
		present.stroke = color;
		present.line(this.line.start.coor, this.line.end.coor, this.line.handle);
	}

	
	this.drawInColor = function()
	{
		this.drawInOtherColor(this.line.color);
	}
	
	this.draw = function()
	{
		this.drawInOtherColor(defaultColor);
	}
}
	

function congruentLabel(line1, line2, markers)
{
	
	this.labels1 = line1.getCrossLines(markers);
	this.labels2 = line2.getCrossLines(markers);
	this.color = getNextColor();
	
	this.drawInColor = function()
	{
		for(var k=0; k<this.labels1.length; k++)
		{
			this.labels1[k].drawInOtherColor(this.color);	
		}
		for(var k=0; k<this.labels2.length; k++)
		{
			this.labels2[k].drawInOtherColor(this.color);	
		}
	}
	
	this.draw = function()
	{
		for(var k=0; k<this.labels1.length; k++)
		{
			this.labels1[k].draw();	
		}
		for(var k=0; k<this.labels2.length; k++)
		{
			this.labels2[k].draw();	
		}
	}

}



function graphLine(start, end)
{
	this.start = start; //assumes that it is passed a graphPoint Object for start and end
	this.end = end;
	this.handle = 'l_'+start.label+'_'+end.label;
	this.color = getNextColor();
	this.regStr = '<b>'+overline(this.start.regStr+this.end.regStr)+'</b>';
	this.colorStr = colorString(this.regStr, this.color);
	
	var crossPointDistance = .04;
	var crossLineLength = .04;
	
	
	
	this.getCrossLineGivenPoint = function(x,y)
	{
		var pStart = new graphPoint(x, y-crossLineLength, above);
		var pEnd = new graphPoint(x, y+crossLineLength, above);
		var pSlope = this.perpendicularSlope();
		if (pSlope!=null)
		{
			var xShift = crossLineLength/Math.sqrt(1+Math.pow(pSlope,2));
			pStart = new graphPoint(x-xShift, y-xShift*pSlope, above);
			pEnd = new graphPoint(x+xShift, y+xShift*pSlope, above);
		}
		
		
		return  (new noLabelLine(pStart, pEnd));
	}
	
	
	this.getCrossLines = function(number)
	{
		var midX = (start.x+end.x)/2;
		var midY = (start.y+end.y)/2;
		var crossLines = new Array();
		
		
		var length = this.getLength();
		var weightIncr = crossPointDistance/length;
		
		var startWeight = .5-weightIncr*(number-1)/2; //this works if number is odd
		if (number%2==0)
		{
			startWeight+=weightIncr/2;
		}
	
		var weight = startWeight;
		
		for(var i=0; i<number; i++)
		{
			
			var curX = weight*this.start.x + (1-weight)*this.end.x;
			var curY = weight*this.start.y + (1-weight)*this.end.y;
			crossLines.push(this.getCrossLineGivenPoint(curX, curY));
			weight+=weightIncr;
		}
		
		return crossLines;
		
	}
	
	
	this.getCrossLine = function()
	{
		var midX = (this.start.x+this.end.x)/2;
		var midY = (this.start.y+this.end.y)/2;
		
		
		return this.getCrossLineGivenPoint(midX, midY);
	
	}
	
	this.drawInColor = function()
	{
		start.drawInOtherColor(this.color);
		end.drawInOtherColor(this.color);
		present.stroke = this.color;
		present.line(this.start.coor, this.end.coor, this.handle);
	}
	
	this.drawInOtherColor = function(color)
	{
		start.drawInOtherColor(color);
		end.drawInOtherColor(color);
		present.stroke = color;
		present.line(this.start.coor, this.end.coor, this.handle);
	}
	
	this.draw = function()
	{
		start.draw();
		end.draw();
		present.stroke = defaultColor;
		present.line(this.start.coor, this.end.coor, this.handle);
	}
	
	this.getLength = function()
	{
		return Math.sqrt(Math.pow(this.start.x-this.end.x, 2)+Math.pow(this.start.y-this.end.y, 2));
	}
	
	
	this.perpendicularSlope = function()
	{
		if (this.end.y==this.start.y)
			return null;
		else
			return (this.start.x-this.end.x)/(this.end.y-this.start.y);
	}
	
	
	this.getSlope = function()
	{
		if (this.end.x==this.start.x)
			return null;
		else
			return (this.end.y-this.start.y)/(this.end.x-this.start.x);
	}
	
}



function graphCircle(center, radius)
{
	this.center = center;
	this.radius = radius;
	this.handle = this.center.handle+this.radius.handle;
	this.color = getNextColor();
	this.regStr = "<B>the circle centered at point "+this.center.regStr+" with radius "+this.radius.regStr+"</B>";
	this.colorStr = colorString(this.regStr, this.color);
	
	this.drawInColor = function()
	{
		present.stroke = this.color;
		present.circle(this.center.coor, this.radius.getLength(), this.handle);
	}
	
	this.drawInOtherColor = function(color)
	{
		present.stroke = color;
		present.circle(this.center.coor, this.radius.getLength(), this.handle);
	}
	
	this.draw = function()
	{
		present.stroke = defaultColor;
		present.circle(this.center.coor, this.radius.getLength(), this.handle);
	}
}

function graphRectangle(topLeft, topRight, bottomRight, bottomLeft)
{
	this.topLeft = topLeft;
	this.topRight = topRight;
	this.bottomRight = bottomRight;
	this.bottomLeft = botomLeft;
	
	this.top = new graphLine(this.topLeft, this.topRight);
	this.right = new graphLine(this.topRight, this.bottomRight);
	this.bottom = new graphLine(this.bottomRight, this.bottomLeft);
	this.left = new graphLine(this.bottomLeft, this.topLeft);
	
	this.color = getNextColor();
	this.regStr = "<b>rectangle "+this.topLeft.regStr+this.topRight.regStr+this.bottomRight.regStr+this.bottomLeft.regStr+"</b>";
	this.colorStr = colorString(this.regStr, this.color);
	
	this.drawInColor = function()
	{
		this.top.drawInOtherColor(this.color);
		this.right.drawInOtherColor(this.color);
		this.bottom.drawInOtherColor(this.color);
		this.left.drawInOtherColor(this.color);
	}
		
	this.drawInOtherColor = function(color)
	{	
		this.top.drawInOtherColor(color);
		this.right.drawInOtherColor(color);
		this.bottom.drawInOtherColor(color);
		this.left.drawInOtherColor(color);
	}
	
	this.draw = function()
	{
		this.top.draw();
		this.right.draw();
		this.bottom.draw();
		this.left.draw();
	}
	
}

function graphTriangle(left, top, right)
{
	this.left = left;
	this.top = top;
	this.right = right;
	this.center = new graphPoint((this.left.x+this.top.x+this.right.x)/3, (this.left.y+this.top.y+this.right.y)/3);
	
	this.allPoints = new Array(this.left, this.top, this.right);
	
	
	this.leftSide = new graphLine(this.left, this.top);
	this.rightSide = new graphLine(this.top, this.right);
	this.bottomSide = new graphLine(this.right, this.left);
	
	this.rightSide.oppAngle = new graphAngle(this.top, this.left, this.right);
	this.leftSide.oppAngle = new graphAngle(this.left, this.right, this.top);
	this.bottomSide.oppAngle = new graphAngle(this.right, this.top, this.left);
	
	this.sides = [this.rightSide, this.leftSide, this.bottomSide];
	
	
	this.color = getNextColor();
	this.regStr = "<b>triangle "+this.left.regStr+this.top.regStr+this.right.regStr+"</b>";
	this.colorStr = colorString(this.regStr, this.color);
	
	
	
	this.rotate = function(axisPoint, degrees)
	{
		var rads = degrees*Math.PI/180;
	
		for(var k=0; k<this.allPoints.length; k++)
		{
			var curPoint = this.allPoints[k];
			var curLabelPosition = curPoint.labelPosition;
			curPoint.labelPosition = posArray[($.inArray(curLabelPosition, posArray)+Math.floor(degrees/45))%posArray.length];
			var distance = getDistance(axisPoint, curPoint);
			var curAngle = Math.atan2(curPoint.y-axisPoint.y, curPoint.x-axisPoint.x);
		
			var newAngle = curAngle+rads;
		
			curPoint.x = distance*Math.cos(newAngle);
			curPoint.y = distance*Math.sin(newAngle);
		
			curPoint.coor = [curPoint.x, curPoint.y];
		}
		this.center.x = (this.left.x+this.top.x+this.right.x)/3;
		this.center.y = (this.left.y+this.top.y+this.right.y)/3;
		this.center.coor = [this.center.x, this.center.y];
	}
	
	
	
	this.scale = function(factor)
	{
		for(var k=0; k<this.allPoints.length; k++)
		{
			var curPoint = this.allPoints[k];
			var distance = getDistance(this.center, curPoint);
			var curAngle = Math.atan2(curPoint.y-this.center.y, curPoint.x-this.center.x);
			
			var newDistance = distance * factor;
			
			curPoint.x = newDistance*Math.cos(curAngle);
			curPoint.y = newDistance*Math.sin(curAngle);
			curPoint.coor = [curPoint.x, curPoint.y];
		}
	}
	
	this.shift = function(xShift, yShift)
	{
		for(var k=0; k<this.allPoints.length; k++)
		{
			var curPoint = this.allPoints[k];
			curPoint.x += xShift;
			curPoint.y += yShift;
			curPoint.coor = [curPoint.x, curPoint.y];
		}
		
		this.center.x += xShift;
		this.center.y += yShift;
		this.center.coor = [this.center.x, this.center.y];
		
	}
	
	
	
	this.drawInColor = function()
	{
		this.leftSide.drawInOtherColor(this.color);
		this.rightSide.drawInOtherColor(this.color);
		this.bottomSide.drawInOtherColor(this.color);
	}
	
	this.drawInOtherColor = function(color)
	{
		this.leftSide.drawInOtherColor(color);
		this.rightSide.drawInOtherColor(color);
		this.bottomSide.drawInOtherColor(color);
	}
	
	this.draw = function()
	{
		this.leftSide.draw();
		this.rightSide.draw();
		this.bottomSide.draw();
	}
		
	this.getAltitude = function(side)
	{
		if (side=='top')
		{
			var basePoint =  getOtherAltitudePoint(this.top, this.left, this.right);
			return (new graphLine(this.top, basePoint));
		} 
		
		else if (side == 'left')
		{
			var basePoint = getOtherAltitudePoint(this.left, this.top, this.right);
			basePoint.labelPosition = aboveright;
			return (new graphLine(this.top, basePoint));
			
		} 
		else if (side == 'right')
		{
			var basePoint = getOtherAltitudePoint(this.right, this.left, this.top);
			basePoint.labelPosition = aboveleft;
			return (new graphLine(this.top, basePoint));
		}
		
	}
	
	
	
	
	function getOtherAltitudePoint(start, base1, base2)
	{
		var baseSlope = getSlope(base1, base2);
		var baseIntercept = base1.y - baseSlope*base1.x;
		var altSlope = -1/baseSlope;
		var altIntercept = start.y - altSlope*start.x;
		
		var endX = (altIntercept - baseIntercept)/(baseSlope-altSlope)
		var endY = baseSlope*endX + baseIntercept;
		var point = new graphPoint(endX, endY, below);
		return point;	
	}
	
	

}


function getEquilateral()
{
	return (new graphTriangle(new graphPoint(0,0,belowleft), new graphPoint(.5, Math.sqrt(3)/2, above), new graphPoint(1,0,belowright)));
}

function getIsoscelese()
{
	return (new graphTriangle(new graphPoint(0,0,belowleft), new graphPoint(.5, 1, above), new graphPoint(1,0, belowright)));
}

function get454590()
{
	return (new graphTriangle(new graphPoint(0,0,belowleft), new graphPoint(0,1,aboveleft), new graphPoint(1,0, belowright)));
}

function get306090()
{
	return (new graphTriangle(new graphPoint(0,0,belowleft), new graphPoint(0, Math.sqrt(3)/2, aboveleft), new graphPoint(.5,0,belowright)));
}

function getFlipped306090()
{
	var t = new graphTriangle(new graphPoint(-.5,0,belowleft), new graphPoint(0, Math.sqrt(3)/2, aboveright),new graphPoint(0,0,belowright));
	//The 3 lines below are to make sure that the corressponding sides to a non-flipped triangle are still corressponding
	var temp = t.sides[0];
	t.sides[0] = t.sides[1];
	t.sides[1] = temp;
	return t;
}

function getSeparateSimilarTriangles()
{
	var t1 = get306090();
	var t2 = getFlipped306090();
	
	if (getRandomIntRange(0,1)==1)
		t2 = get306090();
	
	t2.rotate(t2.center, getRandomIntRange(0,359));
	t2.scale(.75);
	t2.shift(-.6, .4);
	
	return [t1, t2];
}


function getOverlayedSimilarTriangles()
{
		
		var topPoint = new graphPoint(getRandomIntRange(-2,2)/10,1, above);
		//alert(1);
		var bigLeftPoint = new graphPoint(getRandomIntRange(-6,4)/10,0,belowleft);
		var bigRightPoint = new graphPoint(getRandomIntRange(bigLeftPoint.x+5, bigLeftPoint.x+10)/10,0, belowright);
		var midLinePosition = getRandomIntRange(40,60);
		//alert(2);
		
		var smallLeftPoint = new graphPoint(midLinePosition*topPoint.x/100+(100-midLinePosition)*bigLeftPoint.x/100, midLinePosition*topPoint.y/100+(100-midLinePosition)*bigLeftPoint.y/100, left);
		var smallRightPoint = new graphPoint(midLinePosition*topPoint.x/100+(100-midLinePosition)*bigRightPoint.x/100, midLinePosition*topPoint.y/100+(100-midLinePosition)*bigRightPoint.y/100, right);
		//alert(3);
		
		var t1 = new graphTriangle(bigLeftPoint, topPoint, bigRightPoint);
		var t2 = new graphTriangle(smallLeftPoint, topPoint, smallRightPoint);
		
		
		//var t1 = new graphTriangle(new graphPoint(0,0,belowleft), new graphPoint(0, Math.sqrt(3)/2, aboveleft), new graphPoint(.5,0,belowright));
		//var t2 = new graphTriangle(new graphPoint(-.5,0,belowleft), new graphPoint(0, Math.sqrt(3)/2, aboveright),new graphPoint(0,0,belowright));
		
		//alert(4);
		return [t1,t2];
	
}



function overline(x)
{
	return ('<font style=\"text-decoration: overline;\">'+x+'</font>');
}


function writeGraphicalHint(hint, stuffToDraw)
{
	if (stuffToDraw!=null)
	{
		graphicalHints[next_step_to_write] = stuffToDraw;
	}
	writeStep(hint);
}


KhanAcademy_hint_by_id = {};

// Store away the innerHTML of the hints so that users don't accidentally see it if they copy/paste
// the page to a text editor as described in issue 57.
function hide_hints() {
	var step = 1;
	while(true) {
		var part = 1;
		while (true) {
			var id = "step" + step + "_" + part;
			var elem = document.getElementById(id);
			if (!elem) 
				break;
			KhanAcademy_hint_by_id[id] = elem.innerHTML;
			elem.innerHTML = '';
			part++;
		}
		if (part == 1) 
			// Nothing for this step so we must be done
			break;
		step++;
	}	
}

function give_next_step() {
	
	var justDrawn = graphicalHints[steps_given];
	if (justDrawn)
	{
		for(var k=0; k<justDrawn.length; k++)
			justDrawn[k].draw();
	}
	steps_given++;
	var toDraw = graphicalHints[steps_given];
	if (toDraw)
	{
		for(var k=0; k<toDraw.length; k++)
			toDraw[k].drawInColor();
	}
	
	
	
	//graph_update();
	for(var i=1; i<=display_per_step; i++)
	{
		show_step(i);
	}
	translate(); // Process any ASCII Math -> MathML
}

function show_step(i)
{
	var id = "step"+steps_given+"_"+i;
	var elem = document.getElementById(id);
	if (elem) 
	{
		elem.innerHTML = KhanAcademy_hint_by_id[id];
		elem.style.visibility = 'visible';				
	}
}

function randomRotation()
{
	rotateGraph(getRandomIntRange(0,359));
}


var posArray = new Array(above, aboveleft, left, belowleft, below, belowright, right, aboveright);
var flipArray = {above: above, aboveleft: aboveright, left: right, belowleft: belowright, below: below, belowright: belowleft, right: left, aboveright:aboveleft};
	

function rotateGraph(degrees) {
	var dimensionMax = .25;
	var dimensionMin = 0;
	
	var flip = false;
	if (getRandomIntRange(1,2)==2)
		flip = true;
	
	
	
	for(var k=0; k<pointRegister.length; k++)
	{
		var curPoint = pointRegister[k];
		dimensionMax = Math.max(dimensionMax, Math.max(curPoint.x, curPoint.y));
		dimensionMin = Math.min(dimensionMin, Math.min(curPoint.x, curPoint.y));
	}
	
	var center = .5*(dimensionMax+dimensionMin);
	var rads = degrees*Math.PI/180;
	var centerPoint = new graphPoint(center, center, above);
	
	for(var k=0; k<pointRegister.length; k++)
	{
		var curPoint = pointRegister[k];
		var curLabelPosition = curPoint.labelPosition;
		curPoint.labelPosition = posArray[($.inArray(curLabelPosition,posArray)+Math.floor(degrees/45))%posArray.length];
		var distance = getDistance(centerPoint, curPoint);
		var curAngle = Math.atan2(curPoint.y-centerPoint.y, curPoint.x-centerPoint.x);
		
		var newAngle = curAngle+rads;
		
		curPoint.x = distance*Math.cos(newAngle);
		curPoint.y = distance*Math.sin(newAngle);
		
		
		
		if (flip)
		{
			curPoint.x = -1*curPoint.x;
			curPoint.labelPosition = flipArray[curPoint.labelPosition];
		}
		curPoint.coor = [curPoint.x, curPoint.y];
	}
	
	if (flip)
	{
		for(var k=0; k<angleRegister.length; k++)
		{
			var curAngle = angleRegister[k];
			
			var tempLine = curAngle.startLine;
			curAngle.startLine = curAngle.endLine;
			curAngle.endLine = tempLine;
			
			var tempPoint = curAngle.p1;
			curAngle.p1 = curAngle.p2;
			curAngle.p2 = tempPoint;
		}
	}
}




function initGraph() {
	
	//var dimensionMax = .25;
	//var dimensionMin = 0;
	
	var xMax = .25;
	var yMax = .25;
	var xMin = 0;
	var yMin = 0;
	
	for(var k=0; k < pointRegister.length; k++)
	{
		var curPoint = pointRegister[k];
		xMax = Math.max(xMax, curPoint.x);
		yMax = Math.max(yMax, curPoint.y);
		xMin = Math.min(xMin, curPoint.x);
		yMin = Math.min(yMin, curPoint.y);
		//dimensionMax = Math.max(dimensionMax, Math.max(curPoint.x, curPoint.y));
		//dimensionMin = Math.min(dimensionMin, Math.min(curPoint.x, curPoint.y));
	}
	
	
	var yCenter = (yMax+yMin)/2;
	var xCenter = (xMax+xMin)/2;
	
	if ((xMax-xMin)>(yMax-yMin))
	{
		var margin = .25*(xMax-xMin);
		//alert([xMin-margin, xMax+margin, yCenter-margin-(xMax-xMin)/2, yCenter+margin+(xMax-xMin)/2]);
		present.initPicture(xMin-margin, xMax+margin, yCenter-margin-(xMax-xMin)/2, yCenter+margin+(xMax-xMin)/2);
	}
	else
	{
		var margin = .25*(yMax-yMin);
		present.initPicture(xCenter-margin-(yMax-yMin)/2, xCenter+margin+(yMax-yMin)/2, yMin-margin, yMax+margin);
		
	}
	
	//var margin = .25*(dimensionMax - dimensionMin);
	present.strokewidth = "2";
	//present.initPicture(dimensionMin-margin,dimensionMax+margin, dimensionMin-margin,dimensionMax+margin);
	for(var k=0; k < initialObjectsToDraw.length; k++)
	{
		initialObjectsToDraw[k].draw();
	}


}

function graph_update() {
	
	initGraph();
}


	
