//NPM Imports

const express = require('express');

const session = require('express-session');
const passport = require('passport');

const app = express();

const http = require('http').Server(app);

const io = require('socket.io')(http);

const path = require('path');

require('dotenv').config();

// OAuth routes
const authRoutes = require('./auth');

//------------------------------------------------------------------------------------//
//File loads

const LocationDatabase = require(__dirname + "/location_database.json"); // { row number: [...row] }

// ------------------
// Session and Passport Setup  (ADD BELOW FILE LOADS)
// ------------------
app.use(session({
    secret: process.env.SESSION_SECRET, 
    resave: false,
    saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

// ------------------
// Mount OAuth routes (ADD BELOW PASSPORT INIT)
// ------------------
app.use('/', authRoutes);

//------------------------------------------------------------------------------------//
//App Commands

//Mark clientFiles folder as static so it can be accessed by the client
app.use(express.static(path.join(__dirname, 'Client-Files')));

//Send user index.html when they load the url
app.get('/', function(req, res){
	res.sendFile(path.join(__dirname, 'Client-Files', 'index.html'));
});

//------------------------------------------------------------------------------------//
//Websocket Commands

let connections;
io.on('connection', (socket) => {
	//Print current connections
	connections = io.engine.clientsCount;
	console.log("\nConnected Users: " + connections.toString());


	socket.on("request_next_entries", (data) => {
		let count = 10
		if ("count" in Object.keys(data)) {
			count = data["count"];
		}
		console.log(data);
		// TODO: return selected database entries as a list [ [database row], [database row], ... ]
	});

	socket.on("user_feedback", (data) => {
		let liked = data["liked"] == true;
		let entry = data["place"];
		console.log(data);
	});

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