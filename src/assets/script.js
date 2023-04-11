function main() {
    var element = document.querySelector('#svgGraph');
    var instance = panzoom(element, {
        zoomSpeed: 0.065,
        filterKey: function(/* e, dx, dy, dz */) {return true;}
    });
    instance.pause();

    const checkbox = document.getElementById('svgCheckbox');

    checkbox.addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            instance.resume();
        } else {
            instance.pause();
        }
    });
}
