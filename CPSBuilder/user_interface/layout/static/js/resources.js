/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for the "resources" tab
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

/* add either new param or state when creating new*/
function addVariable(type) {
  var addInputPlace = document.getElementById(type);
  var newInputdd =  document.createElement("DD");
  var newDiv = document.createElement("Div");
  var newInput = document.createElement("Input");
  var deleteInput = document.createElement("ICON");
  newDiv.className = "new-variable";
  newInput.className = "form-control";
  newInput.classList.add(type);
  newInput.type = "text";
  if (type == "states") {
    newInput.name = "state";
  }
  if (type == "params") {
    newInput.name = "param";
  }
  deleteInput.className = "material-icons"
  deleteInput.classList.add("remove-variable");
  deleteInput.innerHTML = "remove_circle";
  deleteInput.setAttribute("onclick", "removeElement(this)");
  newInputdd.appendChild(newInput);
  newDiv.appendChild(newInputdd);
  newDiv.appendChild(deleteInput);
  addInputPlace.appendChild(newDiv);
  //  Add delete button once more than 1 variable
  if (addInputPlace.childElementCount == "3") {
    var deleteInput1 = deleteInput.cloneNode(true);
    addInputPlace.children[1].appendChild(deleteInput1);
  }
}

/* removes the newly added param or state */
function removeElement(e) {
    var element = e.parentNode;
    var parent = element.parentNode;
    parent.removeChild(element);
    // Remove the delete button if reaches 1 variable
    if (parent.childElementCount == "2") {
      var deleteButton = parent.children[1].children[1];
      parent.children[1].removeChild(deleteButton);
    }
}


/* combine the param or states when on click */
// Not needed
function combineVariables() {
  var param = document.getElementById("param");
  var state = document.getElementById("state");
  var otherParams = document.getElementsByClassName("params");
  var otherStates = document.getElementsByClassName("states");
  var i;
  var params = [param.value];
  var states = [state.value];
  for (i=0; i< otherParams.length; i++ ) {
    params.push(otherParams[i].value);
  }
  for (i=0; i< otherStates.length; i++ ) {
    states.push(otherStates[i].value);
  }
  param.value = params;
  state.value = states;
  console.log(params)
}

/* For editing software resource */
function removeVariable(e) {
    var element = e.parentNode;
    var parent = element.parentNode;
    var line = parent.parentNode.parentNode;
    console.log(line);
    parent.removeChild(element);
    // Remove the delete button if reaches 1 variable
    if (parent.childElementCount == "2") {
      var deleteButton = parent.children[1].children[1];
      parent.children[1].removeChild(deleteButton);
    }
}