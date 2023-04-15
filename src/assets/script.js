// function main() {
//     var element = document.querySelector('#svgGraph');
//     var instance = panzoom(element, {
//         zoomSpeed: 0.065,
//         filterKey: function(/* e, dx, dy, dz */) {return true;}
//     });
//     instance.pause();
//     const checkbox = document.getElementById('svgCheckbox');
//     checkbox.addEventListener('change', (event) => {
//         if (event.currentTarget.checked) {
//             instance.resume();
//         } else {
//             instance.pause();
//         }
//     });
// }

function openTab(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}
