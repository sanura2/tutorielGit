let http = require('http');
let server = http.createServer(function(req, res) {
res.writeHead(200);
res.end('My Node JS server is running on port 3001!');
});
server.listen(3001);


