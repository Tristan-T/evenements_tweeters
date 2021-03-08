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
    query=query.join('+');
    console.log(query)
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            //reset then add the tweet to the markerLocations and description array and redraw them
            markersLocation = [];
            markersDesc = [];
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
    xhttp.open("GET", 'getTweets?'+query, true);
    xhttp.send();
});

/**
 * Slider
 */

const inputLeft = document.getElementById("input-left");
const inputRight = document.getElementById("input-right");
const thumbLeft = document.querySelector(".slider > .thumb.left");
const thumbRight = document.querySelector(".slider > .thumb.right");
const range = document.querySelector(".slider > .range");
const Dmin = document.getElementById("min");
const Dmax = document.getElementById("max");

function setLeftValue() {
    let _this = inputLeft,
        min = parseInt(_this.min),
        max = parseInt(_this.max);

    _this.value = Math.min(parseInt(_this.value), parseInt(inputRight.value) - 1);

    let percent = ((_this.value - min) / (max - min)) * 100;

    thumbLeft.style.left = percent + "%";
    range.style.left = percent + "%";
    Dmin.innerHTML = "<span>"+_this.value+"</span>";

}
setLeftValue();

function setRightValue() {
    let _this = inputRight,
        min = parseInt(_this.min),
        max = parseInt(_this.max);

    _this.value = Math.max(parseInt(_this.value), parseInt(inputLeft.value) + 1);

    let percent = ((_this.value - min) / (max - min)) * 100;

    thumbRight.style.right = (100 - percent) + "%";
    range.style.right = (100 - percent) + "%";
    Dmax.innerHTML = "<span>"+_this.value+"</span>";
}
setRightValue();

inputLeft.addEventListener("input", setLeftValue);
inputRight.addEventListener("input", setRightValue);