class Task {
    constructor(uuid, pickup, drop, pkgid, status) {
        this.uuid = uuid;
        this.pickup = pickup;
        this.drop = drop;
        this.package = pkgid;
        this.status = status;
        console.log(this);
        this.addToTable();
    }

    assignTo(robot) {
        this.robot = robot;
        var tr = document.getElementById("ass" + this.uuid);
        console.log(tr);
        tr.innerHTML = "Robot #" + robot;
    }

    setStatus(status) {
        this.status = status;
        var tr = document.getElementById(this.uuid);
        tr.innerHTML = status;
        console.log(tr);
    }

    setPath(pickup, drop) {
        this.pickupPath = pickup;
        this.dropPath = drop;
        console.log([pickup, drop]);
    }

    addToTable() {
        var table = document.getElementById("tasks");
        var row = table.insertRow(1);
        var pickupcell = row.insertCell(0);
        var dropcell = row.insertCell(1);
        var packagecell = row.insertCell(2);
        var statuscell = row.insertCell(3);
        var assigncell = row.insertCell(4);
        statuscell.id = this.uuid;
        pickupcell.innerHTML = `${this.pickup["x"]}, ${this.pickup["y"]}`;
        dropcell.innerHTML = `${this.drop["x"]}, ${this.drop["y"]}`;
        packagecell.innerHTML = this.package["id"];
        statuscell.innerHTML = this.status;
        assigncell.innerHTML = "Pending";
        assigncell.id = "ass" + this.uuid;
    }

    drawPath(ctx) {
        if (this.pickupPath != null) {
            console.log(this.pickup, this.drop);
            this.pickupPath.forEach((point) => {
                ctx.beginPath();
                ctx.arc(point[0], point[1], 2, 0, 2 * Math.PI);
                ctx.fillStyle = "black";
                ctx.fill();
                //ctx.lineTo(point[0], point[1]);
                //ctx.strokeStyle = "black";
                //ctx.stroke();
            });
            this.dropPath.forEach((point) => {
                ctx.beginPath();
                ctx.arc(point[0], point[1], 2, 0, 2 * Math.PI);
                ctx.fillStyle = "black";
                ctx.fill();
                //ctx.lineTo(point[0], point[1]);
                //ctx.strokeStyle = "black";
                //ctx.stroke();
            });
            ctx.beginPath();
            ctx.arc(this.pickup["x"], this.pickup["y"], 5, 0, 2 * Math.PI);
            ctx.fillStyle = "red";
            ctx.fill();
            ctx.beginPath();
            ctx.arc(this.drop["x"], this.drop["y"], 5, 0, 2 * Math.PI);
            ctx.fillStyle = "green";
            ctx.fill();
        }
    }
}
