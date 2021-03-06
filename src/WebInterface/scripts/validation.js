let nextTweet = 0;
let rules = [];
let advancedMode = false;
window.addEventListener('load', function (e) {
    //firstly get all the tweets to evaluate from the database, should be light enough
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            //reset then add the tweet to the markerLocations and description array and redraw them
            console.log(JSON.parse(this.responseText))
            markersLocations = [];
            markersTweets = [];
            markersId = [];
            JSON.parse(this.responseText).forEach(el=>{
                //store tweets and location
                markersLocations.push(el.locations);
                markersTweets.push(el.text);
                markersId.push(el._id);
            });
            nextValidation();
            updateRules();
        }
    };
    let url = window.location.href;
    if(window.location.port===''){
        url = window.location.href.replace(window.location.origin, window.location.origin+':8080');
    } else if(window.location.port!==''){
        url = window.location.href.replace(window.location.port, '8080');
    }
    url = url.split('/');
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
    container.innerHTML='';
    markersLocations[nextTweet].forEach((el) => {

        container.innerHTML+='<div class="checkbox">\n' +
            '        <input class="custom_checkbox_2 location_checkbox" type="checkbox" name="checkbox1" id="' + encodeURIComponent(el) + '" value="' + encodeURIComponent(el) + '">\n' +
            '        <label for="' + encodeURIComponent(el) + '"> ' + el + '</label><br>\n' +
            '    </div>';
    })
    container.innerHTML+='<div class="checkbox">\n' +
        '        <input class="custom_checkbox_2 location_checkbox" type="checkbox" name="checkbox1" id="none" value="none">\n' +
        '        <label for="none">Non localisable</label><br>\n' +
        '    </div>';
    container.innerHTML+='<div class="checkbox">\n' +
        '        <input class="custom_checkbox_2 location_checkbox" type="checkbox" name="checkbox1" id="notProposed" value="notProposed">\n' +
        '        <label for="notProposed">Localisation non proposée</label><br>\n' +
        '    </div>';
    container.innerHTML+='<div class="checkbox">\n' +
        '        <input class="custom_checkbox_2" type="checkbox" name="checkbox1" id="offTopic" value="offTopic">\n' +
        '        <label for="offTopic">Hors sujet</label><br>\n' +
        '    </div>';
    container.innerHTML+='<div style="'+ (advancedMode?'':'display: none') +'" class="checkbox" id="ruleDiv"><textarea id="addRule"></textarea><button onclick="addRule()">Add rule</button><select id="rule"></select></div>';
    container.innerHTML+='<button id="button_next" onclick="sendAndNext()">Suivant</button>';
}

function sendAndNext() {
    //If at least one of the locations is checked (including "none" or "not proposed")
    if(Array.from(document.getElementsByClassName(' location_checkbox')).some(e => e.checked)){
        let checkboxes = document.getElementsByClassName('custom_checkbox_2');
        let query = [];
        let offtopic = false;
        for (const check of checkboxes) {
            if (check.checked) {
                if (check.value === "offTopic") {
                    offtopic = true;
                } else {
                    query.push(encodeURI(check.value));
                }
            }
        }
        query = query.join(',');
        query = (query.length > 0 ? 'loc=' + query + '&' : query);
        query += 'id=' + markersId[nextTweet];
        query += '&offTopic=' + offtopic;
        query += '&rule=' + document.getElementById('rule').value;
        let xhttp = new XMLHttpRequest();
        let url = window.location.href;
        if (window.location.port === '') {
            url = window.location.href.replace(window.location.origin, window.location.origin + ':8080');
        } else if (window.location.port !== '') {
            url = window.location.href.replace(window.location.port, '8080');
        }
        url = url.split('/');
        url.pop();
        url = url.join('/');
        xhttp.open("GET", url + '/validateTweet?' + query, true);
        xhttp.send();
        nextTweet++;
        nextValidation();
        updateRules();
    } else {
        Array.from(document.getElementsByClassName(' location_checkbox')).forEach(e => negativeFeedback(e.parentElement));
    }
}

function updateRules() {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            //reset then add the tweet to the markerLocations and description array and redraw them
            rules=JSON.parse(this.responseText);
            document.getElementById('rule').innerHTML='';
            rules.forEach(el => {
                document.getElementById('rule').innerHTML+='<option value="'+ el._id+'">'+  el.rule.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;') +'</option>';
            });
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
    url.push('getRules')
    url = url.join('/');
    xhttp.open("GET", url, true);
    xhttp.send();
}

function addRule() {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            //reset then add the tweet to the markerLocations and description array and redraw them
            document.getElementById('addRule').value='';
            updateRules();
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
    url.push('addRule?rule='+encodeURIComponent(document.getElementById('addRule').value));
    url = url.join('/');
    xhttp.open("GET", url, true);
    xhttp.send();
}

function toggleRules() {
    if (document.getElementById('ruleDiv').style.display === "none") {
        document.getElementById('ruleDiv').style.display = '';
        advancedMode = true;
    } else {
        document.getElementById('ruleDiv').style.display = "none";
        advancedMode = false;
    }
}

function displayTweet(txt){
    document.getElementById("tweets_body").innerHTML = "<p>" + txt + "</p>";
}

function negativeFeedback(el) {
    el.classList.add('negativeFeedback');
    const removeClass = function() {
        el.classList.remove('negativeFeedback');
        el.removeEventListener("animationend", removeClass);
    };
    el.addEventListener("animationend", removeClass);
}