var express = require('express');
var app = express();
var pg = require('pg');
app.set('view engine', 'jade');

app.set('port', (process.env.PORT || 5000));
app.use(express.static(__dirname + '/views/public'));

app.get('/', function(request, response) {
  response.render('middle');
});

app.get('/db', function (request, response) {
    pg.connect(process.env.DATABASE_URL, function(err, client, done) {
    client.query('SELECT * FROM test_table', function(err, result) {
      done();
      if (err)
       { console.error(err); response.send("Error " + err); }
      else
       { response.send(result.rows); }
    });
  });
})

app.listen(app.get('port'), function() {
  console.log("Node app is running at localhost:" + app.get('port'));
});
