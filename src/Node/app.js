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
let realTimeDB,dbName;
//Connect to the database using the config file
fs.readFile(pathToConfig, function (err, file) {
    if (err) throw err;
    const parsed = JSON.parse(file.toString());
    dbName = parsed.mongodb.db_name;
    realTimeDB = parsed.mongodb.collection_real_time_name;
    client = new MongoClient("mongodb+srv://"+encodeURIComponent(parsed.mongodb.username)+":"+encodeURIComponent(parsed.mongodb.password)+"@"+encodeURIComponent(parsed.mongodb.address));
    client.connect();
});

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

//This part sends to the client the file it requests. not very secure but hey
http.createServer(async function (req, res) {
    if(req.url.includes("getTweets")){
        //get the query string
        let qurl = new URL("foo://bar.com"+req.url).search.substring(1).split('+');
        //make sure we don't have url stuff
        qurl.forEach(el => {el=decodeURI(el)});
        res.writeHead(200, {'Content-Type': 'application/json'});
        res.write(JSON.stringify(await getTweets(qurl)));
        return res.end();
    } else if(req.url.includes("WebInterface") || req.url === '/') {
        var fileName = req.url === '/' ? './src/WebInterface/index.html' : './src/WebInterface' + req.url, ext = path.extname(fileName) === "" ? "html" : path.extname(fileName);
        fs.readFile(fileName, function (err, data) {
            if (err) {
                res.writeHead(404, {'Content-Type': 'text/html'});
                return res.end("404 Not Found");
            }
            res.writeHead(200, {'Content-Type': extensions[ext]});
            res.write(data);
            return res.end();
        });
    } else {
        console.log("Invalid request to "+ req.url);
    }
}).listen(8080);

async function getTweets(types) {
    try {
        const database = client.db(dbName);
        let query;
        if(types.length===1){
            query = {disasterType:types[0]}
        } else {
            query = {$or:[]}
            types.forEach(el => {query.$or.push({disasterType:el})})
        }
        return await database.collection(realTimeDB).find(query).project({location: 1, text:1, _id: 0}).toArray();
    }catch{}
}