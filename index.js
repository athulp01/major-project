const socket = io()
socket.on("path", showPath);
socket.on("updateStatus", updateStatus);
socket.on("test", test);
var ctx;
var canvas;
var pickup = false;

function test(data){
    console.log(data)
}
window.onload = function () {
    canvas = document.getElementById("img");
    ctx = canvas.getContext("2d")
    var img = document.getElementById("base")
    ctx.drawImage(img, 0, 0)
    canvas.addEventListener('click', updatePoint, false)
    fillStatusTable()
}


function fillStatusTable() {
    var table = document.getElementById("tasks");
    axios.get("/getTasks").then((resp) => {
        for (task in resp.data) {
            table.innerHTML += `<tr><th>${resp.data[task]["pickup"]["x"]}, ${resp.data[task]["pickup"]["y"]}</th><th>${resp.data[task]["drop"]["x"]}, ${resp.data[task]["drop"]["y"]}</th><th>${resp.data[task]["package"]["id"]}</th><th id=${resp.data[task]["uuid"]}>${resp.data[task]["status"]}</th`;
        }
    })
}

function updateStatus(data) {
    console.log(data)
    var th = document.getElementById(data["uuid"])
    console.log({data, th})
    th.innerText = data["status"]
}

function showPath(data) {
    var enc = new TextDecoder("utf-8");
    var image = new Image();
    console.log(enc.decode(data))
    image.src = 'data:image/jpeg;base64,' + enc.decode(data)
    document.body.appendChild(image);
}

function submitPoint() {
    var table = document.getElementById("tasks");
    var data = {
        "pickup": {
            "x": parseInt(document.getElementById("pickx").value),
            "y": parseInt(document.getElementById("picky").value),
        },
        "drop": {
            "x": parseInt(document.getElementById("dropx").value),
            "y": parseInt(document.getElementById("dropy").value),
        },
        "package": {
            "id": document.getElementById("pkgid").value
        },
        "uuid": Math.random() * 1000000,
        "status": "Queued"
    };
    table.innerHTML += `<tr><th>${data["pickup"]["x"]}, ${data["pickup"]["y"]}</th><th>${data["drop"]["x"]}, ${data["drop"]["y"]}</th><th>${data["package"]["id"]}</th><th id=${data["uuid"]}>${data["status"]}</th`;
    socket.emit("addTask", data)

}

function updatePoint(event) {
    console.log(canvas)
    const rect = canvas.getBoundingClientRect()
    var data = {
        "position": {
            "x": event.clientX - rect.x,
            "y": event.clientY - rect.y
        }
    }
    if (pickup == false) {
        document.getElementById("pickx").value = data["position"]["x"]
        document.getElementById("picky").value = data["position"]["y"]
        ctx.beginPath();
        ctx.arc(data["position"]["x"], data["position"]["y"], 5, 0, 2 * Math.PI)
        ctx.fillStyle = "red";
        ctx.fill();
        ctx.fillStyle = "black";
        ctx.font = "15px Georgia";
        ctx.fillText("Pickup Point", data["position"]["x"] + 10, data["position"]["y"] + 10);
        pickup = true;
    } else {
        document.getElementById("dropx").value = data["position"]["x"]
        document.getElementById("dropy").value = data["position"]["y"]
        ctx.beginPath();
        ctx.arc(data["position"]["x"], data["position"]["y"], 5, 0, 2 * Math.PI)
        ctx.fillStyle = "green";
        ctx.fill();
        ctx.fillStyle = "black";
        ctx.font = "15px Georgia";
        ctx.fillText("Drop Point", data["position"]["x"] + 10, data["position"]["y"] + 10);
    }
    console.log(data)
}

function updatePos() {
    axios.get('/getPos').then((resp) => {
        ctx.beginPath();
        ctx.arc(resp.data["x"], resp.data["y"], 5, 0, 2 * Math.PI)
        ctx.stroke();
    })
}

$(document).ready(function () {
    $('#tabs li').on('click', function () {
        var tab = $(this).data('tab');

        $('#tabs li').removeClass('is-active');
        $(this).addClass('is-active');

        $('#tab-content div').removeClass('is-active');
        $('div[data-content="' + tab + '"]').addClass('is-active');
    });
});

