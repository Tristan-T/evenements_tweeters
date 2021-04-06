let nextTweet = 0;
window.addEventListener('load', function (e) {
    //firstly get all the tweets to evaluate from the database, should be light enough
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            //reset then add the tweet to the markerLocations and description array and redraw them
            console.log(JSON.parse(this.responseText))
            markersLocation = [];
            markersTweets = [];
            markersId = [];
            JSON.parse(this.responseText).forEach(el=>{
                //store tweets and location
                if (typeof el.location !== 'undefined') {
                    let temp = el.location[0];
                    el.location[0] = el.location[1];
                    el.location[1] = temp;
                    markersLocation.push(el.location);
                }
                markersTweets.push(el.url);
                markersId.push(el._id);
            });
            drawAll();
        }
    };
    let url = window.location.href;
    if(window.location.port===''){
        url = window.location.href.replace(window.location.origin, window.location.origin+':8080');
    } else if(window.location.port!==''){
        url = window.location.href.replace(window.location.port, '8080');
    }
    url = url.split('/');
    url.pop();
    url.push('getTweetsToValidate')
    url = url.join('/');
    xhttp.open("GET", url, true);
    xhttp.send();
});

function nextValidation() {
    //Display the tweet to validate
    displayTweet(markersTweets[nextTweet]);
    const container = document.getElementById('selectors_wrapper');
    //Clear the choice
    container.innerHTML= '';

}