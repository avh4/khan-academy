
var KnowledgeMap = {

    map: null,
    dictNodes: {},
    dictEdges: [],
    widthPoints: 200,
    heightPoints: 120,
    colors: {
        blue: "#0080C9",
        green: "#8EBE4F",
        red: "#E35D04",
        gray: "#FFFFFF"
    },
    icons: {
        proficient: "/images/node-complete.png",
        review: "/images/node-review.png",
        suggested: "/images/node-suggested.png",
        normal: "/images/node-not-started.png"
    },
    latLngHome: new google.maps.LatLng(-0.46721, 0.65387),
    latMin: 90,
    latMax: -90,
    lngMin: 180,
    lngMax: -180,
    nodeSpacing: {lat: 0.38, lng: 0.42},
    latLngBounds: null,
    reZoom: /nodeLabelZoom(\d)+/g,
    reHighlight: /nodeLabelHighlight/g,
    fCenterChanged: false,
    fZoomChanged: false,
    options: {
                getTileUrl: function(coord, zoom) {
                    // Sky tiles example from
                    // http://gmaps-samples-v3.googlecode.com/svn/trunk/planetary-maptypes/planetary-maptypes.html
                    return KnowledgeMap.getHorizontallyRepeatingTileUrl(coord, zoom, 
                            function(coord, zoom) {
                              return "http://mw1.google.com/mw-planetary/sky/skytiles_v1/" +
                                 coord.x + "_" + coord.y + '_' + zoom + '.jpg';
                            }
                )},
                tileSize: new google.maps.Size(256, 256),
                maxZoom: 10,
                minZoom: 7,
                isPng: false
    },

    init: function(latInit, lngInit, zoomInit) {

        this.discoverGraph();

        this.map = new google.maps.Map(document.getElementById("map-canvas"), {
            mapTypeControl: false,
            streetViewControl: false,
            scrollwheel: false
        });

        var knowledgeMapType = new google.maps.ImageMapType(this.options);
        this.map.mapTypes.set('knowledge', knowledgeMapType);
        this.map.setMapTypeId('knowledge');

        if (latInit && lngInit && zoomInit)
        {
            this.map.setCenter(new google.maps.LatLng(latInit, lngInit));
            this.map.setZoom(zoomInit);
        }
        else
        {
            this.map.setCenter(this.latLngHome);
            this.map.setZoom(this.options.minZoom + 2);
        }

        this.layoutGraph();
        this.latLngBounds = new google.maps.LatLngBounds(new google.maps.LatLng(this.latMin, this.lngMin), new google.maps.LatLng(this.latMax, this.lngMax)),

        google.maps.event.addListener(this.map, "center_changed", function(){KnowledgeMap.onCenterChange();});
        google.maps.event.addListener(this.map, "zoom_changed", function(){KnowledgeMap.onZoomChange();});
        google.maps.event.addListener(this.map, "idle", function(){KnowledgeMap.saveMapCoords();});

        this.giveNasaCredit();
    },

    giveNasaCredit: function() {
        // Setup a copyright/credit line, emulating the standard Google style
        // From
        // http://code.google.com/apis/maps/documentation/javascript/demogallery.html?searchquery=Planetary
        var creditNode = $("<div class='creditLabel'>Image Credit: SDSS, DSS Consortium, NASA/ESA/STScI</div>");
        creditNode[0].index = 0;
        this.map.controls[google.maps.ControlPosition.BOTTOM_RIGHT].push(creditNode[0]);
    },

    discoverGraph: function() {
        $("table.hidden_knowledge_map tr[data-id]").each(function() {
            var jel = $(this);
            KnowledgeMap.addNode({
                "id": jel.attr("data-id"),
                "name": jel.attr("data-name"),
                "h_position": jel.attr("data-h_position"),
                "v_position": jel.attr("data-v_position"),
                "status": jel.attr("data-status"),
                "url": "/exercises?exid=" + jel.attr("data-id")
            });
        });

        $("table.hidden_knowledge_map tr[data-id]").each(function(){
            var jel = $(this);
            jel.find("li[data-prereq]").each(function(i) {
                var source = jel.attr("data-id");
                var target = $(this).attr("data-prereq");
                KnowledgeMap.addEdge(source, target);
            });
        });
    },

    layoutGraph: function() {
        for (var key in this.dictNodes)
        {
            this.drawMarker(this.dictNodes[key]);
        }

        for (var key in this.dictEdges)
        {
            var rgTargets = this.dictEdges[key];
            for (var ix = 0; ix < rgTargets.length; ix++)
            {
                this.drawEdge(this.dictNodes[key], this.dictNodes[rgTargets[ix]]);
            }
        }
    },

    addNode: function(node) {
        this.dictNodes[node.id] = node;
    },

    addEdge: function(source, target) {
        if (!this.dictEdges[source]) this.dictEdges[source] = [];
        var rg = this.dictEdges[source];
        rg[rg.length] = target;
    },

    nodeStatusCount: function(status) {
        var c = 0;
        for (var ix = 1; ix < arguments.length; ix++)
        {
            if (arguments[ix].status == status) c++;
        }
        return c;
    },

    drawEdge: function(nodeSource, nodeTarget) {

        var coordinates = [
            nodeSource.latLng,
            nodeTarget.latLng
        ];

        var countProficient = this.nodeStatusCount("Proficient", nodeSource, nodeTarget);
        var countSuggested = this.nodeStatusCount("Suggested", nodeSource, nodeTarget);
        var countReview = this.nodeStatusCount("Review", nodeSource, nodeTarget);

        var color = this.colors.gray;
        var weight = 1.0;
        var opacity = 0.25;

        if (countProficient == 2)
        {
            color = this.colors.blue;
            weight = 5.0;
            opacity = 1.0;
        }
        else if (countProficient == 1 && countSuggested == 1)
        {
            color = this.colors.green;
            weight = 5.0;
            opacity = 1.0;
        }
        else if (countReview > 0)
        {
            color = this.colors.red;
            weight = 5.0;
            opacity = 1.0;
        }

        var line = new google.maps.Polyline({
            path: coordinates,
            strokeColor: color,
            strokeOpacity: opacity,
            strokeWeight: weight,
            clickable: false
        });

        window.poly = line;

        line.setMap(this.map);
    },

    drawMarker: function(node) {

        var lat = -1 * (node.h_position - 1) * this.nodeSpacing.lat;
        var lng = (node.v_position - 1) * this.nodeSpacing.lng;

        node.latLng = new google.maps.LatLng(lat, lng);

        if (lat < this.latMin) this.latMin = lat;
        if (lat > this.latMax) this.latMax = lat;
        if (lng < this.lngMin) this.lngMin = lng;
        if (lng > this.lngMax) this.lngMax = lng;

        var iconUrl = this.icons.normal;
        switch (node.status)
        {
            case "Proficient":
                iconUrl = this.icons.proficient;
                break;
            case "Suggested":
                iconUrl = this.icons.suggested;
                break;
            case "Review":
                iconUrl = this.icons.review;
                break;
        }

        var labelClass = "nodeLabel nodeLabel" + node.status;
        var zoom = this.map.getZoom();

        var marker = new MarkerWithLabel({
            position: node.latLng,
            map: this.map,
            icon: this.getMarkerIcon(iconUrl, zoom),
            flat: true,
            labelContent: node.name,
            labelAnchor: this.getLabelAnchor(zoom),
            labelClass: this.getLabelClass(labelClass, zoom)
        });

        node.marker = marker;
        node.iconUrl = iconUrl;

        google.maps.event.addListener(marker, "click", function(){KnowledgeMap.onNodeClick(node);});
        google.maps.event.addListener(marker, "mouseover", function(){KnowledgeMap.onNodeMouseover(node);});
        google.maps.event.addListener(marker, "mouseout", function(){KnowledgeMap.onNodeMouseout(node);});
    },

    getMarkerIcon: function(iconUrl, zoom) {
        if (!this.iconCache) this.iconCache = {};
        if (!this.iconCache[iconUrl + "@" + zoom])
        {
            var size = (1 / (this.options.maxZoom - zoom + 1)) * 100;
            var url = iconUrl;

            if (zoom == this.options.minZoom)
            {
                size = 15;
                url = iconUrl.replace(".png", "-star.png");
            }

            this.iconCache[iconUrl + "@" + zoom] = new google.maps.MarkerImage(url, 
                    null, 
                    null, 
                    new google.maps.Point(size / 2, size / 2), 
                    new google.maps.Size(size, size));
        }
        return this.iconCache[iconUrl+ "@" + zoom];
    },

    getLabelClass: function(classOrig, zoom, highlight) {

        classOrig = classOrig.replace(this.reZoom, "") + (" nodeLabelZoom" + zoom);

        if (highlight)
            classOrig += " nodeLabelHighlight";
        else
            classOrig = classOrig.replace(this.reHighlight, "");

        return classOrig;
    },

    getLabelAnchor: function(zoom) {
        if (!this.labelAnchorCache) this.labelAnchorCache = {};
        if (!this.labelAnchorCache[zoom])
        {
            var offset = -1 * (55 / (this.options.maxZoom - zoom + 1));
            this.labelAnchorCache[zoom] = new google.maps.Point(40, offset);
        }
        return this.labelAnchorCache[zoom];
    },

    highlightNode: function(node, highlight) {
        var marker = node.marker;
        marker.labelClass = this.getLabelClass(marker.labelClass, this.map.getZoom(), highlight);
        marker.label.setStyles();
    },

    onNodeClick: function(node) {
        if (this.map.getZoom() <= this.options.minZoom)
        {
            // Zoom on node
            this.map.setCenter(node.latLng);
            this.map.setZoom(this.map.getZoom() + 1);
        }
        else
        {
            // Go to exercise
            window.location = node.url;
        }
    },

    onNodeMouseover: function(node) {
        $(".exercise-badge[data-id=\"" + node.id + "\"]").addClass("exercise-badge-hover");
        this.highlightNode(node, true);
    },

    onNodeMouseout: function(node) {
        $(".exercise-badge[data-id=\"" + node.id + "\"]").removeClass("exercise-badge-hover");
        this.highlightNode(node, false);
    },

    onBadgeMouseover: function() {
        var exid = $(this).attr("data-id");
        var node = KnowledgeMap.dictNodes[exid];
        if (node) KnowledgeMap.highlightNode(node, true);
    },

    onBadgeMouseout: function() {
        var exid = $(this).attr("data-id");
        var node = KnowledgeMap.dictNodes[exid];
        if (node) KnowledgeMap.highlightNode(node, false);
    },

    onZoomChange: function() {

        if (zoom < this.options.minZoom) return;
        if (zoom > this.options.maxZoom) return;

        this.fZoomChanged = true;

        var zoom = this.map.getZoom();

        for (var key in this.dictNodes)
        {
            var node = this.dictNodes[key];
            var marker = node.marker;
            marker.setIcon(this.getMarkerIcon(node.iconUrl, zoom));
            marker.labelAnchor = this.getLabelAnchor(zoom);
            marker.labelClass = this.getLabelClass(marker.labelClass, zoom);
            marker.label.setStyles();
        }
    },

    saveMapCoords: function(dt) {

        if (!this.fCenterChanged && !this.fZoomChanged)
            return;

        var center = this.map.getCenter();
        $.post("/savemapcoords", {
            "lat": center.lat(),
            "lng": center.lng(),
            "zoom": this.map.getZoom()
        }); // Fire and forget
    },

    onCenterChange: function() {

        this.fCenterChanged = true;

        var center = this.map.getCenter();
        if (this.latLngBounds.contains(center)) {
            return;
        }

        var C = center;
        var X = C.lng();
        var Y = C.lat();

        var AmaxX = this.latLngBounds.getNorthEast().lng();
        var AmaxY = this.latLngBounds.getNorthEast().lat();
        var AminX = this.latLngBounds.getSouthWest().lng();
        var AminY = this.latLngBounds.getSouthWest().lat();

        if (X < AminX) {X = AminX;}
        if (X > AmaxX) {X = AmaxX;}
        if (Y < AminY) {Y = AminY;}
        if (Y > AmaxY) {Y = AmaxY;}

        this.map.setCenter(new google.maps.LatLng(Y,X));
    },

    getHorizontallyRepeatingTileUrl: function(coord, zoom, urlfunc) {

        // From http://gmaps-samples-v3.googlecode.com/svn/trunk/planetary-maptypes/planetary-maptypes.html
        var y = coord.y;
        var x = coord.x;

        // tile range in one direction range is dependent on zoom level
        // 0 = 1 tile, 1 = 2 tiles, 2 = 4 tiles, 3 = 8 tiles, etc
        var tileRange = 1 << zoom;

        // don't repeat across y-axis (vertically)
        if (y < 0 || y >= tileRange) {
            return null;
        }

        // repeat across x-axis
        if (x < 0 || x >= tileRange) {
            x = (x % tileRange + tileRange) % tileRange;
        }

        return urlfunc({x:x,y:y}, zoom);
    }
};
