window.addEventListener("beforeunload", function () {
    document.getElementById("loader").style.display = "flex";
});

window.addEventListener("load", function () {
    document.getElementById("loader").style.display = "none";
});
