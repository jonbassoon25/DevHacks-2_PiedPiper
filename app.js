//NPM Imports

const express = require('express');

const session = require('express-session');
const passport = require('passport');

const app = express();

const http = require('http').Server(app);

const io = require('socket.io')(http);

const path = require('path');

const fs = require('fs');

require('dotenv').config();

// OAuth routes
const authRoutes = require('./auth');

//------------------------------------------------------------------------------------//
//File loads & Variables

const LocationDatabase = require(__dirname + "/location_database.json"); // { row number: [...row] }
var UserDatabase = {};

if (fs.existsSync(__dirname + "/user_database.json")) {
	UserDatabase = require(__dirname + "/user_database.json");
}

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


async function getMLResponse(args = [__dirname + "/Python_ML/DQN.py"]) {
	//console.log(""+args)
	const spawn = require("child_process").spawn;
	const pythonProcess = spawn(__dirname + '/Python_ML/bin/python', args);
	//console.log("Waiting");

	return new Promise(function(resolve, reject) {
		pythonProcess.stdout.on('data', (data) => {
			let response = data.toString().trim();
			if (response == "keep") {
				resolve("keep");
			} else {
				resolve("next");
			}
		});
	});
}

let connections;
io.on('connection', (socket) => {
	//Print current connections
	connections = io.engine.clientsCount;
	console.log("\nConnected Users: " + connections.toString());

	socket.on("user-info", (user) => {
		//console.log(user);
		
	});

	socket.on("request_next_entries", async (data) => {
		let count = 6
		if ("count" in Object.keys(data)) {
			count = data["count"];
		}
		let id = data["id"];
		let location = data["location"]
		//console.log(data);
		let payload = []
		while (payload.length < count) {
			// Randomly select a entry (TODO: stop from recommending previous recommendations)
			let entryIndex = Object.keys(LocationDatabase)[Math.trunc(Math.random() * Object.keys(LocationDatabase).length)];
			let randomEntry = LocationDatabase[entryIndex];

			if (!(location == '' || randomEntry[6].toLowerCase().includes(location.trim().toLowerCase()))) {
				continue;
			}
			
			// Check with the ML to decide if this entry will be kept
			console.log(__dirname + "/Python_ML/DQN.py" + " " + __dirname + "/user_models/" + id + ".pkl" + " " +  "-d" + " " +  "" + entryIndex);
			const response = await getMLResponse([__dirname + "/Python_ML/DQN.py", __dirname + "/user_models/" + id + ".pkl", "-d", "" + entryIndex]);
			console.log(response);
			if (response == "keep") {
				// Format and add the entry, if applicable
				randomEntry = {
					"ID": randomEntry[0],
					"Name": randomEntry[1],
					"Rating": randomEntry[2],
					"Reviews": randomEntry[3],
					"URL": randomEntry[4],
					"Description": randomEntry[5],
					"Location": randomEntry[6]
				}
				payload.push(randomEntry);
			}
			console.log(payload.length + '/' + count);
		}
		// return selected database entries as a list [ {database row}, {database row}, ... ]
		socket.emit("next_entries", payload);
	});

	socket.on("user_feedback", (data) => {
		let liked = data["action"] == 'like';
		let entry = data["place"];
		let id = data["id"];
		
		console.log(entry);
		console.log(liked);
		// Update the q-values of the network based on the response of the liked/disliked entry
		let entryIndex = entry["ID"];
		let reward;
		if (liked) {
			reward = 1;
		} else {
			reward = 0;
		}
		getMLResponse([__dirname + "/Python_ML/DQN.py", __dirname + "/user_models/" + id + ".pkl", "-u", "" + entryIndex, "like", "" + reward]);
	});

	socket.on("agent_submit", (data) => {
		const spawn = require('child_process').spawn;
		const pyProcess = spawn('python', [__dirname + '/fetcher.py', data["query"]]);
		pyProcess.stdout.on('data', (data) => {
			let response = data.toString();
			socket.emit("agent_response", {"response": response});
		});
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

