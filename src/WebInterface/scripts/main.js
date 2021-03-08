//Create our map object
const map = L.map('map').setView([43.61, 3.87], 13);

//populate the map layer
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoicHl2ZXMiLCJhIjoiY2trZTRiaG9iMHhtdjJvcGFpNGQxd3g3NCJ9.fUjSwyRIh6KGjPh3WFy3_Q'
}).addTo(map);


//MARKERS AND DESC
let markers = [];
let markersLocation = [];
let markersDesc = [];
let heatLayer;

function drawAll() {
    //Remove everything
    markers.forEach(el => {
        el.remove();
    });
    markers=[];
    if (heatLayer) heatLayer.remove();

    //And redraw
    //Markers (for debugging)
    for (let i = 0; i < markersLocation.length; i++) {
        let temp = L.marker(markersLocation[i]);
        temp.addTo(map);
        temp.bindPopup(markersDesc[i]);
        markers.push(temp);
    }

    //The heatmap
    markersLocation.forEach((el) => el.push(0.5));
    heatLayer = L.heatLayer(markersLocation, {
        radius: 40,
        blur: 35,
        maxZoom: 1,
    }).addTo(map);
    markersLocation.forEach((el) => el.pop());
}

drawAll();

//CHECK CLICK AREA FOR MARKERS
// map.on('click', function(e) {
//     var popLocation= e.latlng;
//     var popup = L.popup()
//         .setLatLng(popLocation)
//         .setContent('<p>Hello world!<br />This is a nice popup.</p>')
//         .openOn(map);
// });
/*
let circles=[];
map.on('zoom', function(e) {
    console.log("-----");
    circles.forEach((el)=>map.removeLayer(el));
    circles=[];
    const maxRegroupDist=getDistanceAtCurrentScale(100)*4*(map.getZoom()/19);
    markersLocation.forEach((el)=>el.push(false));
    markersLocation.forEach((el)=>{
        //If the point is not a group, then we try to group it with its neighbors
        if(!el[2]){
            let neighbors=[];
            markersLocation.forEach((nei)=>{
                if(dist(nei[0], nei[1], el[0], el[1],)<=maxRegroupDist*2 && !nei[2]){
                    neighbors.push(nei);
                    nei[2]=true;
                }
            });
            //At this point neighbors contains the regrouped points.
            //Find the center
            //Averaging doesnt not work but the classic way should work
            let lat=0;
            let long=0;
            let max=0;
            // neighbors.forEach((neig)=>{lat+=neig[0];long+=neig[1]});
            // lat/=neighbors.length;
            // long/=neighbors.length;
            // neighbors.forEach((neig)=>max=Math.max(max,dist(lat, long, neig[0], neig[1])));
            if(neighbors.length>1) {
                for (let i = 0; i < neighbors.length - 1; i++) {
                    for (let j = i + 1; j < neighbors.length; j++) {
                        let temp = Math.max(max, dist(neighbors[i][0], neighbors[i][1], neighbors[j][0], neighbors[j][1]));
                        if (temp !== max) {
                            max = temp;
                            lat = (neighbors[i][0] + neighbors[j][0]) / 2;
                            long = (neighbors[i][1] + neighbors[j][1]) / 2;
                        }
                    }
                }
            } else {
                lat=neighbors[0][0];
                long=neighbors[0][1];
                max=getDistanceAtCurrentScale(100)*(map.getZoom()/19);
            }

            let c=L.circle([lat, long], max/1.5);
            c.addTo(map);
            circles.push(c);
            console.log(neighbors);
        }
    });
    markersLocation.forEach((el)=>el.pop());
    console.log("-----");
});
*/
//DISTANCE ION METERS BETWEEN TWO POINTS
function dist(lat1, lon1, lat2, lon2){
    var dLat = lat2 * Math.PI / 180 - lat1 * Math.PI / 180;
    var dLon = lon2 * Math.PI / 180 - lon1 * Math.PI / 180;
    var a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
    return 6378.137 * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))) *1000;
}

function getDistanceAtCurrentScale(pixelsDistance) {
    var containerMidHeight = map.getSize().y / 2,
        point1 = map.containerPointToLatLng([0, containerMidHeight]),
        point2 = map.containerPointToLatLng([pixelsDistance, containerMidHeight]);

    return point1.distanceTo(point2);
}

function loadDoc() {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            //add the tweet to the markerLocations array and redraw them
            console.log(this.responseText);
            JSON.parse(this.responseText).forEach(el=>{
                let temp = el.location[0];
                el.location[0]=el.location[1];
                el.location[1]=temp;
                markersLocation.push(el.location)
                markersDesc.push(el.text)
            });
            drawAll();
        }
    };
    let url = window.location.href.split('/');
    url.pop();
    url.push("allTweets")
    url.join('/');
    xhttp.open("GET", 'allTweets', true);
    xhttp.send();
}