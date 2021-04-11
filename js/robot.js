class Robot {
    constructor(id, x, y, angle) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.angle = angle;
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 10, 0, 2 * Math.PI);
        ctx.fillStyle = "white";
        ctx.fill();
        ctx.beginPath();
        ctx.arc(this.x, this.y, 10, 0, 2 * Math.PI);
        ctx.strokeStyle = "black";
        ctx.stroke();
        ctx.fillStyle = "black";
        ctx.textBaseline = "middle";
        ctx.font = "15px Georgia";
        ctx.textAlign = "center";
        ctx.fillText(this.id, this.x, this.y);
    }

    setPos(x, y) {
        this.x = x;
        this.y = y;
    }
}
