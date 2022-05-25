var express = require('express');
var router = express.Router();
var ws = require('ws').WebSocketServer
var mysql = require("mysql");
const wss = new ws({ port: 8080 });

var pool = mysql.createPool({
  connectionLimit : 100,
  host     :  process.env.DB_HOST,
  port     :  3306,
  user     :  process.env.DB_USER,
  password :  process.env.DB_PASS,
  database :  process.env.DB_NAME,
  });

  

router.post('/hatecoffee', function(req, res, next) //pokud někdo dá post na /hatecoffee (1)
{
  //res.sendStatus(200);

  pool.getConnection(function(err, con) { //připojení do databáze 
    if (err) {
      wss.clients.forEach(function each(client) {client.send(JSON.stringify(err));}); //pokud chyba pošle error na displej rpi
      res.sendStatus(400)
      return false;
    }
    con.query("SELECT * FROM `test-oracle3` ORDER BY id DESC LIMIT 1;", function (err, result, fields) { //(2) vezmi z databáze poslední tweet, data co mu přijdou (3) si uloží do proměnné result
      if (err) {
        wss.clients.forEach(function each(client) {client.send(JSON.stringify(err));});
        res.sendStatus(400)
        return false;
      }

      res.sendStatus(200)

      if (JSON.parse(result[0]["hate"])["top_class"] == "hate_speech")
      {
        console.log("found hate")
        wss.clients.forEach(function each(client) { //(4) poslat tweet na rpi
          client.send(JSON.stringify(result));
        });
      }
    });
  });
  
});

module.exports = router;
