//Create our map object
const map = L.map('map').setView([43.61, 3.87], 3);

//populate the map layer
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    minZoom: 2,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoicHl2ZXMiLCJhIjoiY2trZTRiaG9iMHhtdjJvcGFpNGQxd3g3NCJ9.fUjSwyRIh6KGjPh3WFy3_Q',
}).addTo(map);


//MARKERS and tweets
let markers = [];
let markersLocation = [];
let markersLocations = [];
let markersTweets = [];
let markersId = [];
let heatLayer;
let circles=[];

function drawAll() {
    //Remove everything
    markers.forEach(el => {
        el.remove();
    });
    markers=[];
    if (heatLayer) heatLayer.remove();

    //And redraw
    //Markers (for debugging)
    // for (let i = 0; i < markersLocation.length; i++) {
    //     let temp = L.marker(markersLocation[i]);
    //     temp.addTo(map);
    //     // temp.bindPopup(markersDesc[i]);
    //     markers.push(temp);
    // }

    //The heatmap
    markersLocation.forEach((el) => el.push(0.5));
    heatLayer = L.heatLayer(markersLocation, {
        radius: 30,
        blur: 35,
        maxZoom: 2,
    }).addTo(map);
    markersLocation.forEach((el) => el.pop());
    drawCircles();
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

map.on('zoom', drawCircles);

function drawCircles() {
    circles.forEach((el)=>map.removeLayer(el));
    circles=[];
    const maxRegroupDist=getDistanceAtCurrentScale(100)*(map.getZoom()/19)*2;
    markersLocation.forEach((el)=>el.push(false));
    markersLocation.forEach((el)=>{
        //If the point is not a group, then we try to group it with its neighbors
        if(!el[2]){
            let neighbors=[];
            markersLocation.forEach((nei)=>{
                if(dist(nei[0], nei[1], el[0], el[1],)<=maxRegroupDist && !nei[2]){
                    neighbors.push(nei);
                    nei[2]=true;
                }
            });
            //At this point neighbors contains the regrouped points.
            //Find the center
            //Averaging doesnt not work but the classic way should work
            let lat=0;
            let long=0;
            let max=90000*(9/map.getZoom());
            if(neighbors.length>0) {
                // for (let i = 0; i < neighbors.length - 1; i++) {
                //     for (let j = i + 1; j < neighbors.length; j++) {
                //         let temp = Math.max(max, dist(neighbors[i][0], neighbors[i][1], neighbors[j][0], neighbors[j][1]));
                //         if (temp !== max) {
                //             max = temp;
                //             lat = (neighbors[i][0] + neighbors[j][0]) / 2;
                //             long = (neighbors[i][1] + neighbors[j][1]) / 2;
                //         }
                //     }
                // }
                neighbors.forEach((neig)=>{lat+=neig[0];long+=neig[1]});
                lat/=neighbors.length;
                long/=neighbors.length;
                neighbors.forEach((neig)=>max=Math.max(max,dist(lat, long, neig[0], neig[1])));
            } else {
                lat=el[0];
                long=el[1];
                max=getDistanceAtCurrentScale(100)*(map.getZoom()/19);
            }
            let c=L.circle([lat, long], max, {opacity: 0, color: 'transparent', fillColor: 'transparent'});
            c.bindPopup(JSON.stringify({lat: lat, long: long, radius: max}));
            c.addTo(map);
            circles.push(c);
        }
    });
    markersLocation.forEach((el)=>el.pop());
}

map.on("popupopen", function(e){
    //Treat the open popup as a request, text is the data in json
    const location = JSON.parse(e.popup._content);
    //Close the popup so it is seamless for the user
    map.closePopup();

    displayTweets(location)
});

//DISTANCE IN METERS BETWEEN TWO POINTS
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

function displayTweets(location){
    const container = document.getElementById("tweets_body");
    let temp='';
    container.innerHTML = '';
    if (location) {
        //Only display the tweets from the area passed
        for (let i = 0; i < markersLocation.length; i++) {
            if (dist(markersLocation[i][0], markersLocation[i][1], location.lat, location.long)<=location.radius) {
                temp += "<blockquote class='twitter-tweet' data-theme='dark' data-conversation='none' data-cards='hidden'><a href='" + markersTweets[i] + "'></a></blockquote>";
            }
        }
        container.innerHTML += temp;
    } else {
        //Display all the tweets
        markersTweets.forEach((el) => {
            temp += "<blockquote class='twitter-tweet' data-theme='dark' data-conversation='none' data-cards='hidden'><a href='" + el + "'></a></blockquote>";
        });
        container.innerHTML += temp;
    }
    twttr.widgets.load(container);
}

function displayTweet(id){
    document.getElementById("tweets_body").innerHTML = "<blockquote class='twitter-tweet' data-theme='dark' data-conversation='none' data-cards='hidden'><a href='" + id + "'></a></blockquote>";
    twttr.widgets.load(document.getElementById("tweets_body"));
}