function loadCharacterDetails() {
    const tiles = document.getElementsByClassName("character");
    for (let i = 0; i < tiles.length; i++) {
        let tile = tiles[i];
        let request = new XMLHttpRequest();
        request.addEventListener("load", function() {
            if (this.status === 200) {
                tile.outerHTML = this.responseText;
            }
        });
        request.open("GET", "/dashboard/character/" + tile.dataset.characterid + "/", true);
        request.send();
    }
}