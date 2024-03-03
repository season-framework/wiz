Array.prototype.remove = function () {
    var what, a = arguments,
        L = a.length,
        ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};

Array.prototype.up = function (item) {
    let i = this.indexOf(item);
    if (i < 1) return;
    tmp = this[i];
    this.splice(i, 1);
    this.splice(i - 1, 0, tmp);
}

Array.prototype.down = function (item) {
    let i = this.indexOf(item);
    tmp = this[i];
    this.splice(i, 1);
    this.splice(i + 1, 0, tmp);
}