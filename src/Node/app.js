/**
 * Import Modules
 */
let http = require('http');
let path = require('path');
let fs = require('fs');
const MongoClient = require('mongodb').MongoClient;

/**
 * DATABASE
 */
//Path to the config file
const pathToConfig = "./src/Python/config.json";
let client;
let realTimeDB, validateDB, rulesDB, dbName;
//Connect to the database using the config file
fs.readFile(pathToConfig, function (err, file) {
    if (err) throw err;
    const parsed = JSON.parse(file.toString());
    dbName = parsed.mongodb.db_name;
    realTimeDB = parsed.mongodb.collection_real_time_name;
    validateDB = parsed.mongodb.collection_valid_name;
    rulesDB = parsed.mongodb.collection_rules_name;
    client = new MongoClient("mongodb+srv://"+encodeURIComponent(parsed.mongodb.username)+":"+encodeURIComponent(parsed.mongodb.password)+"@"+encodeURIComponent(parsed.mongodb.address));
    client.connect();


    /**
     * HTTP server
     */
    const extensions = {
        ".html" : "text/html",
        ".css" : "text/css",
        ".js" : "application/javascript",
        ".woff2" : "font/woff2",
        ".ttf" : "font/ttf",
        ".png" : "image/png",
        ".gif" : "image/gif",
        ".jpg" : "image/jpeg"
    };

    const validFiles = [
        '/index.html',
        '/validation.html',
        '/styles/validation.css',
        '/styles/button.css',
        '/styles/main.css',
        '/styles/map.css',
        '/styles/range_slider.css',
        '/scripts/validation.js',
        '/scripts/main.js',
        '/scripts/interactions.js',
        '/scripts/port.js',
        '/assets/raleway.woff2',
        '/assets/Montserrat-Light.ttf',
        '/'
    ];

    //This part sends to the client the file it requests. not very secure but hey
    http.createServer(async function (req, res) {
        const request = req.url.split('/')
        let response;
        res.setHeader('Access-Control-Allow-Origin', '*');
        if(request.some(e => (/getTweets\?.*/).test(e))){
            let qurl = new URL("foo://bar.com"+req.url).searchParams;
            response=JSON.stringify(await getTweets(qurl.get('filter'), qurl.get('time') || "5m"));
        } else if(request.includes("getTweetsToValidate")){
            response=JSON.stringify(await getTweetsToValidate());
        } else if(request.includes("getRules")){
            response=JSON.stringify(await getRules());
        } else if(request.some(e => (/addRule\?.*/).test(e))){
            //get the id of the validated tweet, if it is off topic, the rule used and localisations
            let qurl = new URL("foo://bar.com"+req.url).searchParams;
            response=JSON.stringify(await addRule(qurl.get('rule')));
        } else if(request.some(e => (/validateTweet\?.*/).test(e))){
            //get the id of the validated tweet, if it is off topic, the rule used and localisations
            let qurl = new URL("foo://bar.com"+req.url).searchParams;
            if(qurl.has('id') && qurl.has('loc') && qurl.has('offTopic')) {
                response=JSON.stringify(await validateTweet(qurl.get('id'), qurl.get('loc'), qurl.get('offTopic'), qurl.has('rule')?qurl.get('rule'):null));
            }
        } else if(validFiles.indexOf(new URL("foo://bar.com"+req.url).pathname) !== -1) {
            let fileName = request.join('/') === '/' ? './src/WebInterface/index.html' : "./src/WebInterface"+new URL("foo://bar.com"+req.url).pathname, ext = path.extname(fileName) === "" ? "html" : path.extname(fileName);
            await fs.readFile(fileName, function (err, data) {
                if (err) {
                    console.log(err);
                    res.writeHead(404, {'Content-Type': 'text/html'});
                    return res.end("404 Not Found");
                }
                res.writeHead(200, {'Content-Type': extensions[ext]});
                res.write(data);
                return res.end();
            });
        } else {
            console.log("Invalid request to "+ request.join('/'));
            res.writeHead(404, {'Content-Type': 'text/html'});
            return res.end("404 Not Found");
        }
        if(response) {
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.write(response);
            return res.end();
        }
    }).listen(8080);

    async function getTweets(types, time) {
        types=types.split(',');
        switch (time) {
            case '5m': time=5; break;
            case '10m': time=10; break;
            case '15m': time=15; break;
            case '30m': time=30; break;
            case '60m': time=60; break;
            case '12h': time=12*60; break;
            case '24h': time=24*60; break;
        }
        try {
            const database = client.db(dbName);
            let query;
            if(types.length===1){
                query = {disasterType:types[0], date:{$gt:new Date(Date.now()-(time*60*1000))}};
            } else {
                query = {$or:[], date:{$gt:new Date(Date.now()-(time*60*1000))}};
                types.forEach(el => {query.$or.push({disasterType:decodeURIComponent(el)})});
            }
            return await database.collection(realTimeDB).find(query).sort({date:-1}).project({location: 1, url:1, _id: 0}).toArray();
        }catch(e){
            console.log(e);
        }
    }

    async function getTweetsToValidate() {
        try {
            const database = client.db(dbName);
            return await database.collection(validateDB).find({validated:false}).sort({date:-1}).project({locations : 1, text:1, _id: 1}).toArray();
        }catch(e){
            console.log(e);
        }
    }

    async function validateTweet(id, locations, offTopic, rule) {
        try {
            const database = client.db(dbName);
            return await database.collection(validateDB).updateOne({_id:id}, {$set: {validatedLocations:locations, validated:true, offTopic: offTopic, rule: rule}}).modifiedCount===1;
        }catch(e){
            console.log(e);
        }
    }

    async function getRules() {
        try {
            const database = client.db(dbName);
            return await database.collection(rulesDB).find({}).toArray();
        }catch(e){
            console.log(e);
        }
    }

    async function addRule(rule) {
        try {
            const database = client.db(dbName);
            return await database.collection(rulesDB).insertOne({rule: rule}).insertedId!=="undefined";
        }catch(e){
            console.log(e);
        }
    }
});