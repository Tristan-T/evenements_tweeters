/**
 * Slider
 */

const inputBottom = document.getElementById("input-bottom");
const inputTop = document.getElementById("input-top");
const thumbBottom = document.querySelector(".slider > .thumb.left");
const thumbTop = document.querySelector(".slider > .thumb.right");
const range = document.querySelector(".slider > .range");
const Dmin = document.getElementById("min");
const Dmax = document.getElementById("max");

function setLeftValue() {
    let _this = inputBottom,
        min = parseInt(_this.min),
        max = parseInt(_this.max);

    _this.value = Math.min(parseInt(_this.value), parseInt(inputTop.value) - 1);

    let percent = ((_this.value - min) / (max - min)) * 100;

    thumbBottom.style.left = percent + "%";
    range.style.left = percent + "%";
    Dmin.innerHTML = "<span>"+_this.value+"</span>";
    updateMapOnSlider();
}
setLeftValue();

function setRightValue() {
    let _this = inputTop,
        min = parseInt(_this.min),
        max = parseInt(_this.max);

    _this.value = Math.max(parseInt(_this.value), parseInt(inputBottom.value) + 1);

    let percent = ((_this.value - min) / (max - min)) * 100;

    thumbTop.style.right = (100 - percent) + "%";
    range.style.right = (100 - percent) + "%";
    Dmax.innerHTML = "<span>"+_this.value+"</span>";
    updateMapOnSlider();
}
setRightValue();

function updateSlider() {
    let circlesminmax = getCircleMinMaxContent();
    inputBottom.value=(circlesminmax.min===Number.MAX_SAFE_INTEGER?0:circlesminmax.min);
    inputBottom.min=(circlesminmax.min===Number.MAX_SAFE_INTEGER?0:circlesminmax.min);
    inputBottom.max=circlesminmax.max;
    inputTop.value=circlesminmax.max;
    inputTop.min=(circlesminmax.min===Number.MAX_SAFE_INTEGER?0:circlesminmax.min);
    inputTop.max=circlesminmax.max;
    setLeftValue();
    setRightValue();
}

function updateMapOnSlider() {
    if (circles !== []) {
        let validPoints = [];
        for (let i = 0; i < circles.length; i++) {
            let content=getCircleContent(i);
            map.removeLayer(circles[i]);
            if (content.length<=inputTop.value && content.length>=inputBottom.value) {
                circles[i].addTo(map);
                content.forEach(e => validPoints.push(e));
            }
        }
        if (heatLayer) heatLayer.remove();
        validPoints.forEach((el) => el.push(0.5));
        heatLayer = L.heatLayer(validPoints, {
            radius: 30,
            blur: 35,
            maxZoom: 3,
        }).addTo(map);
    }
}

inputBottom.addEventListener("input", setLeftValue);
inputTop.addEventListener("input", setRightValue);

/**
 * Buttons
 */

document.getElementById('reset_button').addEventListener('click', function(e){
    let checkboxes = document.getElementsByClassName('custom_checkbox');
    for(const check of checkboxes){
        check.checked = true;
    }
});

document.getElementById('apply_button').addEventListener('click', function(e){
    let checkboxes = document.getElementsByClassName('custom_checkbox');
    let query = [];
    for(const check of checkboxes){
        if (check.checked){
            query.push(encodeURI(check.value));
        }
    }
    query=query.join(',');
    query='filter='+query
    query+="&time="+document.getElementById('date_selector').value;
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            //reset then add the tweet to the markerLocations and description array and redraw them
            markersLocation = [];
            markersTweets = [];
            JSON.parse(this.responseText).forEach(el=>{
                let temp = el.location[0];
                el.location[0]=el.location[1];
                el.location[1]=temp;
                markersLocation.push(el.location)
                markersTweets.push(el.url);
            });
            currentMaxTweetFactor=1;
            currentMinTweetId=0;
            displayTweets(undefined, 15);
            drawAll();
            updateSlider();
        }
    };
    let url = window.location.href;
    if(window.location.port===''){
        url = window.location.href.replace(window.location.origin, window.location.origin+':8080');
    } else if(window.location.port!==''){
        url = window.location.href.replace(window.location.port, '8080');
    }
    url = url.split('/');
    url = url.join('/');
    xhttp.open("GET", url+'/getTweets?'+query, true);
    xhttp.send();
});

// load tweets on load of page and set the sliders values
window.addEventListener('load', function (e) {
    document.getElementById('apply_button').click();
    updateSlider();
});