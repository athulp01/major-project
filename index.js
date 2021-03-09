const socket = io()
socket.on("path", showPath);
var ctx;
var canvas; 
var pickup = false;

window.onload = function () {
    canvas = document.getElementById("img");
    ctx = canvas.getContext("2d")
    var img = document.getElementById("base")
    ctx.drawImage(img, 0, 0)
    canvas.addEventListener('click', updatePoint, false)

}

function showPath(data) {
    var enc = new TextDecoder("utf-8");
    var image = new Image();
    console.log(enc.decode(data))
    image.src = 'data:image/jpeg;base64,' + enc.decode(data)
    document.body.appendChild(image);
}

function updatePoint(event) {
    console.log(canvas)
    const rect = canvas.getBoundingClientRect()
    var data = {
        "position":{
            "x": event.clientX - rect.x,
            "y": event.clientY - rect.y 
        }
    }
    if(pickup == false) {
        document.getElementById("pickx").value = data["position"]["x"]
        document.getElementById("picky").value = data["position"]["y"]
        ctx.beginPath();
        ctx.arc(data["position"]["x"], data["position"]["y"], 5, 0, 2*Math.PI)
        ctx.fillStyle = "red";
        ctx.fill();
        ctx.fillStyle = "black";
        ctx.font = "15px Georgia";
        ctx.fillText("Pickup Point", data["position"]["x"] + 10, data["position"]["y"] + 10);
        pickup = true;
    }else {
        document.getElementById("dropx").value = data["position"]["x"]
        document.getElementById("dropy").value = data["position"]["y"]
        ctx.beginPath();
        ctx.arc(data["position"]["x"], data["position"]["y"], 5, 0, 2*Math.PI)
        ctx.fillStyle = "green";
        ctx.fill();
        ctx.fillStyle = "black";
        ctx.font = "15px Georgia";
        ctx.fillText("Drop Point", data["position"]["x"] + 10, data["position"]["y"] + 10);
    }
        console.log(data)
    //socket.emit("addTask", data)
}

function updatePos(){
    axios.get('/getPos').then((resp)=>{
        ctx.beginPath();
        ctx.arc(resp.data["x"], resp.data["y"], 5, 0, 2*Math.PI)
        ctx.stroke();
    })
}

$(document).ready(function() {
  $('#tabs li').on('click', function() {
    var tab = $(this).data('tab');

    $('#tabs li').removeClass('is-active');
    $(this).addClass('is-active');

    $('#tab-content div').removeClass('is-active');
    $('div[data-content="' + tab + '"]').addClass('is-active');
  });
});

