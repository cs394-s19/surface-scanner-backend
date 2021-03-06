let {PythonShell} = require('python-shell')
const WebSocket = require('ws');
const uuidv4 = require('uuid/v4');
var fs = require('fs');

const connections_waiting = [];
const connections = {};
let pic_data = [];

PythonShell.run('deflectomotery.py', null, function (err) {
    if (err) throw err;
    console.log('finished');
});

// When running on Heroku's servers, they dynamically decide which port ot allocate to this process via the
// process.env.PORT process variable. When running heroku locally, it uses port 5000 as default.
// To run locally, first install Heroku's CLI, then do "heroku local web" on the terminal in the root of this project.
let port = process.env.PORT;
if (port == null || port == "") {
    port = 5000;
}


const wss = new WebSocket.Server({
    perMessageDeflate: false,
    port: port
});

wss.on('connection', (ws, req) => {
    console.log("New connection from " + req.connection.remoteAddress);

    connections_waiting.push(ws);

    ws.on('message', incoming);
});

const incoming = function(raw_data) {
    const { action, data } = JSON.parse(raw_data);
    console.log("New action: " + action);
    

    switch (action) {
        case "set_party": {
            console.log("Connection setting party...");
            if (!connections_waiting.includes(this)) {
                this.terminate();
                return;
            }

            const { party } = data;

            console.log("Setting party to " + party);
            if (party === "control") {
                const { uuid } = data;
                
                if (connections[uuid] == null) {
                    console.log("There is no scanning device for connection " + uuid + ". Closing.");
                    this.terminate();
                    return;
                }

                connections[uuid].control = this;
                connections_waiting.splice(connections_waiting.indexOf(this), 1);

                connections[uuid].scan.send(JSON.stringify({
                    action: "control_connected"
                }));

                console.log("Controller for connection " + uuid + " connected.");
            } else if (party === "scan") {
                const uuid = uuidv4();

                connections[uuid] = {control: null, scan: this};

                this.send(JSON.stringify({
                    action: "set_uuid",
                    data: {
                        uuid: uuid
                    }
                }));

                console.log("Connection UUID: " + uuid);
            }

            break;
        }
        case "send_photo": {
            const { data: photo_data, uuid } = data;

            const control = connections[uuid].control;

            if (control === null)
                return;

            control.send(JSON.stringify({
                action: "send_photo",
                data: photo_data
            }));


            break;
        }
        case "end_scan": {
            const { data: photo_data, uuid } = data;
            const control = connections[uuid].control;
            
            PythonShell.run('deflectomotery.py', null, function (err) {
                if (err) throw err;
                console.log('finished');
            });

            // var base64String = base64Encode('./normal.png');
            
            var base64String = base64Encode('./Superman-Logo.png');
            
            if (control === null)
                return;

            control.send(JSON.stringify({
                action: "end_scan",
                data: base64String
            }));

            break;
        }
        case "send_control_info": {
            const { uuid } = data;
            const scan = connections[uuid].scan;

            scan.send(JSON.stringify({
                action: action,
                data: data
            }));

            break;
        }
        case "start_scan": {
            const { uuid } = data;
            const scan = connections[uuid].scan;

            scan.send(JSON.stringify({
                action: action
            }));

            break;
        }
        case 'send_scan_photo':{
            const { data: photo_data, index: photo_index} = data;
            pic_data.push({data:photo_data, index: photo_index})
            console.log('index', photo_index)
            break;
            
        } 
    }
};

function base64Encode(file) {
    var body = fs.readFileSync(file);
    return body.toString('base64');
}

