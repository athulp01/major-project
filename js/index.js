const socket = io();
socket.on("updateStatus", updateStatus);
socket.on("path", updatePath);
socket.on("UpdateRobotPos", updateRobotPos);
socket.on("assignTo", assignTo);
socket.on("newTask", newTask);
var ctx;
var canvas;
var tasks = [];
var robots = [];
var curPick = null;
var curDrop = null;

window.onload = function () {
    canvas = document.getElementById("img");
    ctx = canvas.getContext("2d");
    canvas.addEventListener("click", updateCurPoint, false);
    getTasks();
    getRobotsPos();
};

function cancelCurPoints(event) {
    curPick = null;
    curDrop = null;
    draw(ctx);
}

function updateRobotPos(data) {
    console.log(data);
    robots.forEach((robot) => {
        if (robot.id == data["id"]) {
            robot.setPos(data["x"], data["y"]);
        }
    });
    draw(ctx);
}

function drawPoint(ctx, x, y, color) {
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
}

function drawText(ctx, x, y, color, text) {
    ctx.fillStyle = color;
    ctx.font = "15px Georgia";
    ctx.fillText(text, x, y);
}

function drawCurPoints(ctx) {
    if (curPick != null) {
        drawPoint(ctx, curPick[0], curPick[1], "red");
        drawText(
            ctx,
            curPick[0] + 10,
            curPick[1] + 10,
            "black",
            "Pickup Point"
        );
    }
    if (curDrop != null) {
        drawPoint(ctx, curDrop[0], curDrop[1], "green");
        drawText(ctx, curDrop[0] + 10, curDrop[1] + 10, "black", "Drop Point");
    }
}
function draw(ctx) {
    var img = document.getElementById("base");
    ctx.drawImage(img, 0, 0);
    drawCurPoints(ctx);
    tasks.forEach((task) => {
        if (task["status"] != "Finished") {
            task.drawPath(ctx);
        }
    });
    console.log(robots);
    robots.forEach((robot) => {
        robot.draw(ctx);
    });
}

function getRobotsPos() {
    axios.get("/getRobotsPos").then((resp) => {
        console.log(resp.data);
        resp.data.forEach((data) => {
            var robot = new Robot(
                data["id"],
                data["x"],
                data["y"],
                data["angle"]
            );
            console.log(robot);
            robots.push(robot);
            robot.draw(ctx);
        });
    });
}
function getTasks() {
    axios.get("/getTasks").then((resp) => {
        for (i in resp.data) {
            task = new Task(
                resp.data[i]["uuid"],
                resp.data[i]["pickup"],
                resp.data[i]["drop"],
                resp.data[i]["package"],
                resp.data[i]["status"]
            );
            tasks.push(task);
        }
        draw(ctx);
    });
}

function assignTo(data) {
    console.log(data);
    for (i in tasks) {
        if (tasks[i]["uuid"] == data["uuid"]) {
            tasks[i].assignTo(data["robot"]);
            break;
        }
    }
}

function updateStatus(data) {
    for (i in tasks) {
        if (tasks[i]["uuid"] == data["uuid"]) {
            tasks[i].setStatus(data["status"]);
            if (data["status"] == "Finished") {
                robots.forEach((robot) => {
                    if (robot.id == tasks[i].robot) {
                        robot.setPos(tasks[i].drop["x"], tasks[i].drop["y"]);
                    }
                });
            }
            draw(ctx);
            break;
        }
    }
}

function updatePath(data) {
    for (i in tasks) {
        if (tasks[i]["uuid"] == data["uuid"]) {
            tasks[i].setPath(data["pickup"], data["drop"]);
            draw(ctx);
            break;
        }
    }
}

function addTask() {
    var pickup = {
        x: parseInt(document.getElementById("pickx").value),
        y: parseInt(document.getElementById("picky").value),
    };
    var drop = {
        x: parseInt(document.getElementById("dropx").value),
        y: parseInt(document.getElementById("dropy").value),
    };
    var package = {
        id: document.getElementById("pkgid").value,
    };
    var task = new Task(
        Math.random() * 1000000,
        pickup,
        drop,
        package,
        "Queued"
    );
    console.log(task);
    tasks.push(task);
    cancelCurPoints();
    socket.emit("addTask", JSON.stringify(task));
}

function newTask(data) {
    console.log([data, tasks]);
    var exist = false;
    tasks.forEach((task) => {
        if (task["uuid"] == data["uuid"]) {
            console.log("found");
            exist = true;
            return;
        }
    });
    if (exist) {
        return;
    }
    console.log("adding");
    var task = new Task(
        data["uuid"],
        data["pickup"],
        data["drop"],
        data["package"]["id"],
        data["status"]
    );
    tasks.push(task);
}

function updateCurPoint(event) {
    const rect = canvas.getBoundingClientRect();
    if (curPick == null) {
        curPick = [event.clientX - rect.x, event.clientY - rect.y];
        document.getElementById("pickx").value = parseInt(curPick[0]);
        document.getElementById("picky").value = parseInt(curPick[1]);
        drawCurPoints(ctx);
    } else if (curDrop == null) {
        curDrop = [event.clientX - rect.x, event.clientY - rect.y];
        document.getElementById("dropx").value = parseInt(curDrop[0]);
        document.getElementById("dropy").value = parseInt(curDrop[1]);
        drawCurPoints(ctx);
    }
}

function updateMap(event) {
    curPick = [
        document.getElementById("pickx").value,
        document.getElementById("picky").value,
    ];
    curDrop = [
        document.getElementById("dropx").value,
        document.getElementById("dropy").value,
    ];
    draw(ctx);
}

function updatePos() {
    axios.get("/getPos").then((resp) => {
        ctx.beginPath();
        ctx.arc(resp.data["x"], resp.data["y"], 5, 0, 2 * Math.PI);
        ctx.stroke();
    });
}

$(document).ready(function () {
    $("#tabs li").on("click", function () {
        var tab = $(this).data("tab");

        $("#tabs li").removeClass("is-active");
        $(this).addClass("is-active");

        $("#tab-content div").removeClass("is-active");
        $('div[data-content="' + tab + '"]').addClass("is-active");
    });
});
