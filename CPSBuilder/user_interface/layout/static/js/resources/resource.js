/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for the "resource.hmtl" tab
 * Written by Yin Jun Hao
 */

/* Filters the contents of the data in the table */
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

/** Sort alphabetically when clicked for the first time, reverse when clicked again */
function sortAlphabetically(clicked_id) {
  var table, rows, switching, i, x, y, shouldSwitch;
  table = document.getElementById("table");
  switching = true;
  var column = parseInt(clicked_id);
  if (document.getElementById(clicked_id).className == "sorted") {
    while (switching) {
      //start by saying: no switching is done:
      switching = false;
      rows = table.rows;
      /*Loop through all table rows (except the
      first, which contains table headers):*/
      for (i = 1; i < (rows.length - 1); i++) {
        //start by saying there should be no switching:
        shouldSwitch = false;
        /*Get the two elements you want to compare,
        one from current row and one from the next:*/
        x = rows[i].getElementsByTagName("td")[column];
        y = rows[i + 1].getElementsByTagName("td")[column];
        //check if the two rows should switch place:
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
      if (shouldSwitch) {
        /*If a switch has been marked, make the switch
        and mark that a switch has been done:*/
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
      }
    }
    document.getElementById(clicked_id).className = "";
  } else {
    while (switching) {
      //start by saying: no switching is done:
      switching = false;
      rows = table.rows;
      /*Loop through all table rows (except the
      first, which contains table headers):*/
      for (i = 1; i < (rows.length - 1); i++) {
        //start by saying there should be no switching:
        shouldSwitch = false;
        /*Get the two elements you want to compare,
        one from current row and one from the next:*/
        x = rows[i].getElementsByTagName("td")[column];
        y = rows[i + 1].getElementsByTagName("td")[column];
        //check if the two rows should switch place:
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
      if (shouldSwitch) {
        /*If a switch has been marked, make the switch
        and mark that a switch has been done:*/
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
      }
    }
    document.getElementById(clicked_id).className = "sorted";
  }
}

/* Sort numerically on the first click, reverse when clicked again */
function sortNumerically(clicked_id) {
  var table, rows, switching, i, x, y, shouldSwitch;
  table = document.getElementById("table");
  var column = parseInt(clicked_id);
  switching = true;
  if (document.getElementById(clicked_id).className == "sorted") {
    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
      //start by saying: no switching is done:
      switching = false;
      rows = table.rows;
      /*Loop through all table rows (except the
      first, which contains table headers):*/
      for (i = 1; i < (rows.length - 1); i++) {
        //start by saying there should be no switching:
        shouldSwitch = false;
        /*Get the two elements you want to compare,
        one from current row and one from the next:*/
        x = rows[i].getElementsByTagName("TD")[column];
        y = rows[i + 1].getElementsByTagName("TD")[column];
        //check if the two rows should switch place:
        if (Number(x.innerHTML) > Number(y.innerHTML)) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
      if (shouldSwitch) {
        /*If a switch has been marked, make the switch
        and mark that a switch has been done:*/
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
      }
    }
    document.getElementById(clicked_id).className = "";
  } else {
    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
      //start by saying: no switching is done:
      switching = false;
      rows = table.rows;
      /*Loop through all table rows (except the
      first, which contains table headers):*/
      for (i = 1; i < (rows.length - 1); i++) {
        //start by saying there should be no switching:
        shouldSwitch = false;
        /*Get the two elements you want to compare,
        one from current row and one from the next:*/
        x = rows[i].getElementsByTagName("TD")[column];
        y = rows[i + 1].getElementsByTagName("TD")[column];
        //check if the two rows should switch place:
        if (Number(x.innerHTML) < Number(y.innerHTML)) {
          //if so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
      if (shouldSwitch) {
        /*If a switch has been marked, make the switch
        and mark that a switch has been done:*/
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
      }
    }
    document.getElementById(clicked_id).className = "sorted";
  }
}

/* show more details of the individual resources */
function moreDetails(index, el) {
  var show = document.getElementById("_".concat(index.toString()));
  if (el.innerHTML == "expand_more") {
    el.innerHTML = "expand_less";
    show.style.display = "table-row";

  } else {
    el.innerHTML = "expand_more";
    show.style.display = "none";
  }
}
