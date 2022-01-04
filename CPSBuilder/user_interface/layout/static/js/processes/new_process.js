/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for "new_process.html"
 * Written by Yin Jun Hao
 */


/* Remove underscores from the objective layer */
function changeUnderscore() {
  var area = document.getElementsByClassName("replace-underscore");
  for (var i=0; i< area.length; i++) {
    var text = area[i].innerHTML;
    var new_text = text.replace(/_/g, " ");
    area[i].innerHTML = new_text;
  }
}
window.onload = changeUnderscore();
// Giving the placeholder of the upload file
function changePlaceHolder(e){
  var fileName = document.getElementById("file").files[0].name;
  var nextSibling = e.nextElementSibling
  nextSibling.innerText = fileName
}