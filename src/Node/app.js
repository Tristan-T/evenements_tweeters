/**
 * Import Modules
 */
let http = require('http');
let path = require('path');
let fs = require('fs');
const url = require('url');
const MongoClient = require('mongodb').MongoClient;
let loca;

/**
 * HTTP server
 */
const extensions = {
    ".html" : "text/html",
    ".css" : "text/css",
    ".js" : "application/javascript",
    ".woff2" : "font/woff2",
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
    }else {
        var fileName = req.url === '/' ? './src/WebInterface/index.html' : './src/WebInterface' + req.url,
            ext = path.extname(fileName) === "" ? "html" : path.extname(fileName);
        fs.readFile(fileName, function (err, data) {
            if (err) {
                res.writeHead(404, {'Content-Type': 'text/html'});
                return res.end("404 Not Found");
            }
            res.writeHead(200, {'Content-Type': extensions[ext]});
            res.write(data);
            return res.end();
        });
    }
}).listen(8080);

/**
 * DATABASE
 */
// Replace the uri string with your MongoDB deployment's connection string.
const uri = "mongodb+srv://terL3:" + encodeURIComponent("terL3TWEET3R/") + "@dbtweet.fakza.mongodb.net/DBTweet";
const client = new MongoClient(uri);
client.connect();
async function run() {
    try {
        const database = client.db('DBTweet');
        const query = {disasterType:'Storm'};
        loca = await database.collection('real_time').find(query).project({location: 1, _id: 0}).toArray();
    } catch {
    }
}

async function getTweets(types) {
    try {
        const database = client.db('DBTweet');
        let query;
        if(types.length===1){
            query = {disasterType:types[0]}
        } else {
            query = {$or:[]}
            types.forEach(el => {query.$or.push({disasterType:el})})
        }

        return await database.collection('real_time').find(query).project({location: 1, text:1, _id: 0}).toArray();
    }catch{}
}