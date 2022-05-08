var express = require('express');
var router = express.Router();
var ws = require('ws').WebSocketServer
var mysql = require("mysql");
const wss = new ws({ port: 8080 });

var pool = mysql.createPool({
  connectionLimit : 100,
  host     : HOST,
  port     :  3306,
  user     : USERNAME,
  password : PASS,
  database : DATABASE,
  });

  

wss.on('connection', function connection(ws) {
  console.log("Client connected")
});

router.post('/', function(req, res, next) 
{
  res.sendStatus(200);

  pool.getConnection(function(err, con) {
    if (err) throw err;
    con.query("SELECT * FROM tweets ORDER BY id DESC LIMIT 1;", function (err, result, fields) {
      if (err) throw err;
      //console.log(result[0].body);
      
      wss.clients.forEach(function each(client) {
        client.send(JSON.stringify(result));
      });
    });
  });
  
});

router.get('/', function(req, res, next)
{
  res.send("Server is running")
});

module.exports = router;
