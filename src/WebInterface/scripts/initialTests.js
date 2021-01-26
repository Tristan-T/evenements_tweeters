//Create our map object
const map = L.map('mapdiv').setView([43.61, 3.87], 13);

//populate the map layer
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoicHl2ZXMiLCJhIjoiY2trZTRiaG9iMHhtdjJvcGFpNGQxd3g3NCJ9.fUjSwyRIh6KGjPh3WFy3_Q'
}).addTo(map);


//now add our markers and description.

let markers = [];
let markersLocation = [[43.61, 3.87],[44.61, 3.87],[43.71, 3.97]];
let markersDesc = ["Here in <b>MONTPELLIER</b>", "This is a bit north", "I don't know <br> where this"];

for(let i=0;i<markersLocation.length;i++){
	let temp=L.marker(markersLocation[i]).addTo(map);
	temp.bindPopup(markersDesc[i]);
	markers.push(temp);
}