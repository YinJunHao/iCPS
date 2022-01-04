/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for the "history" tab
 * Written by Yin Jun Hao
 */

/* filter table contents */
function filterTable() {
  var filter = document.getElementById("filter-input").value.toUpperCase();
  var rows = document.querySelector("#table tbody").rows;
  var columns = document.querySelector("#table tbody").rows[0].cells.length;
  // Looping through the rows of the table
  for (var i = 0; i < rows.length; i++) {
    // Assume all not included first
    var keep = false;
    // Loop through the columns
    for (var j = 0; j < columns; j++) {
      var firstCol = rows[i].cells[j].textContent.toUpperCase();
      if (firstCol.indexOf(filter) > -1) {
        keep = true;
      }
    }
    // If found to remove from display
    if (keep) {
      rows[i].style.display = "";
    } else {
      rows[i].style.display = "none";
    }
  }
}