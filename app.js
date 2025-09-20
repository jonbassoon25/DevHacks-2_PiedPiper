//NPM Imports

const express = require('express');

const app = express();

const http = require('http').Server(app);

const io = require('socket.io')(http);

//------------------------------------------------------------------------------------//
//App Commands

//Mark clientFiles folder as static so it can be accessed by the client
app.use(express.static(path.join(__dirname, 'Client-Files')));

//Send user index.html when they load the url
app.get('/', function(req, res){
	res.sendFile(__dirname + 'Client-Files/index.html');
});

//------------------------------------------------------------------------------------//
//Websocket Commands

let connections;
io.on('connection', (socket) => {
	//Print current connections
	connections = io.engine.clientsCount;
	console.log("\nConnected Users: " + connections.toString());

	// When a user has disconnected
	socket.on('disconnect', () => {
		connections = io.engine.clientsCount;
		console.log("\nConnected Users: " + connections.toString());
	});
});

//------------------------------------------------------------------------------------//
//Host server on port 8000

http.listen(8000, () => {
   console.log('App Started on port 8000');
});