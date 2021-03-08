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