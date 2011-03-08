VectorEditor.prototype.unselect = function(shape){

  if(!shape){
    while(this.selected[0]){
      this.unselect(this.selected[0])
    }
    if(shape !== false){
      this.fire("unselected")
    }
  }else{
    this.fire("unselect", shape);
    this.array_remove(shape, this.selected);
    for(var i = 0; i < this.trackers.length; i++){
      if(this.trackers[i].shape == shape){
        this.removeTracker(this.trackers[i]);
      }
    }
  }
}


VectorEditor.prototype.selectAdd = function(shape){
  if(this.is_selected(shape) == false){
    if(this.fire("selectadd",shape)===false)return;
    
    this.selected.push(shape)
    this.showGroupTracker(shape);
  }
}

VectorEditor.prototype.selectAll = function(){
  this.unselect()
  for(var i = 0; i < this.shapes.length; i++){
    this.selectAdd(this.shapes[i])
    
  }
}

VectorEditor.prototype.selectToggle = function(shape){
  if(this.is_selected(shape) == false){
    this.selectAdd(shape)
  }else{
    this.unselect(shape)
  }
}

VectorEditor.prototype.select = function(shape){
  if(this.fire("select",shape)===false)return;
  this.unselect(false)
  this.selected = [shape]
  this.showTracker(shape)
}



VectorEditor.prototype.removeTracker = function(tracker){
  if(!tracker){
    while(this.trackers.length > 0){
      this.removeTracker(this.trackers[0]);
    }
  }else{
    tracker.remove();
    
    for(var i = 0; i < this.trackers.length; i++){
      if(this.trackers[i] == tracker){
        this.trackers.splice(i, 1)
      }
    }
  }
}


VectorEditor.prototype.updateTracker = function(tracker){
  if(!tracker){
    for(var i = 0; i < this.trackers.length; i++){
      this.updateTracker(this.trackers[i])
    }
  }else{
    var shape = tracker.shape;
    var box = shape.getBBox();
    //this is somewhat hackish, if someone finds a better way to do it...
    if(shape.type == "path" && this.action.substr(0,4) == "path"){
      var pathsplit = Raphael.parsePathString(shape.attr("path"))
      if(pathsplit.length == 2){
        tracker[0].attr({cx: box.x + box.width/2, cy: box.y + box.height/2})
        tracker[1].attr({x: pathsplit[0][1]-2, y: pathsplit[0][2]-2})
        tracker[2].attr({x: pathsplit[1][1]-2, y: pathsplit[1][2]-2})
      }
      return;
    }

    //i wish my code could be as dated as possible by referencing pieces of culture
    //though I *hope* nobody needs to use svg/vml whatever in the near future
    //there coudl be a lot of better things
    //and svg-edit is a better project
    //so if the future even uses raphael, then microsoft really sucks
    //it truly is "more evil than satan himself" which is itself dated even for the time of writing
    //and am I ever gonna read this? If it's someone that's not me that's reading this
    //please tell me (if year > 2010 or otherwise)
    tracker.translate(box.x - tracker.lastx, box.y - tracker.lasty)
    
    //now here for the magic
    if(shape._ && shape._.rt){
      tracker.rotate(shape._.rt.deg, (box.x + box.width/2), (box.y + box.height/2))
    }
    
    tracker.lastx = box.x//y = boxxy trollin!
    tracker.lasty = box.y
  }
}
VectorEditor.prototype.trackerBox = function(x, y, action){
  var w = 4
  var shape = this.draw.rect(x - w, y - w, 2*w, 2*w).attr({
    "stroke-width": 1,
    "stroke": "green",
    "fill": "white"
  //THE FOLLOWING LINES HAVE BEEN COMMENTED DUE TO A HORRIBLE BUG IN RAPHAEL
  }).mouseover(function(){
    this.attr("fill", "red")
    try{ //easy way out! try catch!
      if(this.paper.editor.trackers[0][0].attr("rotation").split(" ")[0] == "0" && this.paper.editor.action != "resize"){ //ugh
        this.paper.editor.tooltip("Click and drag to resize shape",
       {x: this.attr("x")+10, y: this.attr("y")+5});
      }else if(this.paper && this.paper.editor && this.paper.editor.hideTooltip){
        this.paper.editor.hideTooltip()
      }
    }catch(err){}
     
  }).mouseout(function(){
    this.attr("fill", "white")
    if(this.paper && this.paper.editor && this.paper.editor.hideTooltip)
      this.paper.editor.hideTooltip();
    
  }).mousedown(function(event){
    //console.log(event)
    if(this.paper && this.paper.editor)
      this.paper.editor.action = action;
    
  });
  var othis = this;
  if(mobilesafari){
	shape.node.addEventListener("touchstart", function(e){
			othis.action = action;
			e.preventDefault();
			return false
	}, false)
	shape.node.addEventListener("touchmove", function(e){
			e.preventDefault();
			return false;
	}, false)
	shape.node.addEventListener("touchend", function(e){
		e.preventDefault()
	}, false)
  }
  shape.node.is_tracker = true;
  return shape;
}

VectorEditor.prototype.trackerCircle = function(x, y){
  var w = 5
  var shape = this.draw.ellipse(x, y, w, w).attr({
    "stroke-width": 1,
    "stroke": "green",
    "fill": "white"
  //THE FOLLOWING LINES HAVE BEEN COMMENTED DUE TO A HORRIBLE BUG IN RAPHAEL
  }).mouseover(function(){
    this.attr("fill", "red")
    try{ //easy way out! try catch!
      if(this.paper.editor.trackers[0][0].attr("rotation").split(" ")[0] == "0"){ //ewwie!
      this.paper.editor.tooltip("Drag to rotate shape or double click to reset.",
       {x: this.attr("cx")+5, y: this.attr("cy")});
      }
    }catch(err){}
  }).mouseout(function(){
    this.attr("fill", "white")
    this.paper.editor.hideTooltip()
  }).mousedown(function(){
    this.paper.editor.action = "rotate";
  }).dblclick(function(){
    this.paper.editor.trackers[0].shape.rotate(0, true); //absolute!
    this.paper.editor.updateTracker();
  });
  shape.node.is_tracker = true;
  return shape;
}

VectorEditor.prototype.hideTooltip = function(){
  this.tt.hide();
}

VectorEditor.prototype.tooltip = function(t,bbox){
  if(!this.tt){
    var set = this.draw.set();
    set.push(this.draw.text(0,0,"x"))
    set.push(this.draw.rect(0,0,1,1))
    this.tt = set;
  }
  var set = this.tt;
  
  set.show();
  set.toFront();
  var text = set[0];
  var rect = set[1];
  text.attr("text", t);
  text.attr("x", bbox.x);
  text.attr("y", bbox.y);
  var txb = text.getBBox() //i wish i knew a better way to align it like that
  text.attr("x", bbox.x + txb.width/2 + 8)
  txb = text.getBBox()
  
  rect.attr({
      x: txb.x-5,
      y: txb.y,
      width: txb.width+10,
      height: txb.height,
      r: 3
    })
  rect.attr("fill","#7cb6ef") //it's the first 6 letters of the hex SHA1 hash of "false"
    .insertBefore(text);
  
  return set;
}

VectorEditor.prototype.markTracker = function(shape){
  shape.node.is_tracker = true;
  return shape;
}


VectorEditor.prototype.newTracker = function(shape){
  for(var i = 0; i < this.trackers.length; i++){
    if(this.trackers[i].shape == shape){
      this.removeTracker(this.trackers[i]);
    }
  }
  this.showTracker(shape)
}

VectorEditor.prototype.showTracker = function(shape){
  var rot_offset = -14;
  var box = shape.getBBox();
  var tracker = this.draw.set();
  tracker.shape = shape;
  
  //define the origin to transform to
  tracker.lastx = 0 //if zero then easier
  tracker.lasty = 0 //if zero then easier
  
  tracker.push(this.markTracker(this.draw.ellipse(box.width/2, box.height/2, 7, 7).attr({
        "stroke": "gray",
        "stroke-opacity": 0.5,
        "fill": "gray",
        "fill-opacity": 0.15
      })).mousedown(function(){
        this.paper.editor.action = "move"
      }));
  
  //draw everything relative to origin (0,0) because it gets transformed later
  if(shape.subtype == "line"){
    var line = Raphael.parsePathString(shape.attr('path'));
    
    tracker.push(this.trackerBox(line[0][1]-box.x,line[0][2]-box.y,"path0"))
    tracker.push(this.trackerBox(line[1][1]-box.x,line[1][2]-box.y,"path1"))
    this.trackers.push(tracker)
  }else if(shape.type == "rect" || shape.type == "image"){
    tracker.push(this.draw.rect(-6, -6, box.width + 11, box.height + 11).attr({"opacity":0.3}))
    //tracker.push(this.trackerBox(-10, -10))
    //tracker.push(this.trackerBox(box.width + 10, -10))
    //tracker.push(this.trackerBox(box.width + 10, box.height + 10))
    //tracker.push(this.trackerBox(-10, box.height + 10))
    tracker.push(this.trackerCircle(box.width/2, rot_offset))
    tracker.push(this.trackerBox(box.width+5,box.height+5,"resize"))
    this.trackers.push(tracker)
  }else if(shape.type == "ellipse"){
    //tracker.push(this.trackerBox(box.x, box.y))
    //tracker.push(this.trackerBox(box.width, box.y))
    //tracker.push(this.trackerBox(box.width, box.height))
    //tracker.push(this.trackerBox(box.x, box.height))
    tracker.push(this.trackerCircle(box.width/2, rot_offset))
    tracker.push(this.trackerBox(box.width+5,box.height+5,"resize"))
    this.trackers.push(tracker)
  }else if(shape.type == "text"){
    tracker.push(this.draw.rect(-6, -6, box.width + 11, box.height + 11).attr({"opacity":0.3}))
    tracker.push(this.trackerCircle(box.width/2, rot_offset))
    tracker.push(this.trackerBox(box.width+5,box.height+5,"resize"))
    this.trackers.push(tracker)
  }else if(shape.type == "path" && shape.subtype != "line"){
    tracker.push(this.draw.rect(-6, -6, box.width + 11, box.height + 11).attr({"opacity":0.3}))
    tracker.push(this.trackerBox(box.width+5,box.height+5,"resize"))
    tracker.push(this.trackerCircle(box.width/2, rot_offset))
    this.trackers.push(tracker)
  }else{
    tracker.push(this.draw.rect(-6, -6, box.width + 11, box.height + 11).attr({"opacity":0.3}))
    tracker.push(this.trackerCircle(box.width/2, rot_offset))
    this.trackers.push(tracker)
  }
  this.updateTracker(tracker)
}

VectorEditor.prototype.showGroupTracker = function(shape){
  var tracker = this.draw.set();
  var box = shape.getBBox();
  
  tracker.push(this.markTracker(this.draw.ellipse(box.width/2, box.height/2, 7, 7).attr({
      "stroke": "gray",
      "stroke-opacity": 0.5,
      "fill": "gray",
      "fill-opacity": 0.15
    })).mousedown(function(){
      this.paper.editor.action = "move"
    }));
  
  tracker.push(this.draw.rect(-6, -6, box.width + 11, box.height + 11).attr({
    "stroke-dasharray": "-",
    "stroke": "blue"
  }))
  tracker.shape = shape;
  //define the origin to transform to
  tracker.lastx = 0 //if zero then easier
  tracker.lasty = 0 //if zero then easier
  this.trackers.push(tracker)
  
  this.updateTracker(tracker)
}

