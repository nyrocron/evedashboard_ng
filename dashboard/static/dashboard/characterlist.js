function tileLoad() {
    console.log("tile loaded: " + this.responseText);
}

function loadCharacterDetails() {
    const tiles = document.getElementsByClassName("character");
    for (let i = 0; i < tiles.length; i++) {
        let tile = tiles[i];
        let request = new XMLHttpRequest();
        request.addEventListener("load", function() {
            tile.outerHTML = this.responseText;
        });
        request.open("GET", "/dashboard/character/" + tile.dataset.characterid + "/", true);
        request.send();
    }
}