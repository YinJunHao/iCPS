/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for "new_resource.html"
 * Written by Yin Jun Hao
 */


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

function populateOptions(physicalResource, number, resourceClass) {
  var no = number.substr(24, number.length-1);
  var populateID = "physical-resource-choice-" + no;
  var populateArea = document.getElementById(populateID);
  populateArea.innerHTML = "";
  var option = document.createElement("option");
  option.value = "";
  option.innerHTML = "";
  populateArea.appendChild(option);
  for (var i=0; i<physicalResource[resourceClass].length; i++) {
    var option = document.createElement("option");
    option.value = physicalResource[resourceClass][i]["ID"];
    option.innerHTML = physicalResource[resourceClass][i]["name"];
    populateArea.appendChild(option);
  }
}

function addPhysicalResource(list) {
  var table = document.getElementById("add-physical-resource");
  var newRow = document.createElement("tr");
  var td1 = document.createElement("td");
  var td2 = document.createElement("td");
  var dd1 = document.createElement("dd");
  var dd2 = document.createElement("dd");
  var select1 = document.createElement("select");
  var select2 = document.createElement("select");
  var optionList = ["", "robot", "hardware", "human"];
  var id = table.children[table.children.length-2].children[0].children[0].children[0].id;
  var number = parseInt(id.substr(24, id.length-1)) + 1;
  var deleteInput = document.createElement("ICON");
  deleteInput.className = "material-icons"
  deleteInput.classList.add("remove-variable");
  deleteInput.innerHTML = "remove_circle";
  deleteInput.setAttribute("onclick", "removeRow(this)");
  var deletetd = document.createElement("td");
  deletetd.appendChild(deleteInput);
  select1.className = "form-control";
  select1.name = "physical-resource-class";
  select1.setAttribute("onchange", "populateOptions("+JSON.stringify(list)+", this.id, this.value)")
  select1.id = "physical-resource-class-" + number.toString();
  for (var i = 0; i<optionList.length; i++)  {
    var option = document.createElement("option");
    option.value = optionList[i];
    option.innerHTML = optionList[i];
    select1.appendChild(option);
  }
  dd1.appendChild(select1);
  td1.appendChild(dd1);
  select2.className = "form-control";
  select2.name = "physical-resource-id";
  select2.id = "physical-resource-choice-" + number.toString();
  var option = document.createElement("option");
  option.value = "";
  option.innerHTML= "";
  select2.appendChild(option);
  dd2.appendChild(select2);
  td2.appendChild(dd2);
  newRow.appendChild(td1);
  newRow.appendChild(td2);
  newRow.appendChild(deletetd);
  table.insertBefore(newRow, table.children[table.children.length-1]);
  if (table.childElementCount == "3") {
    var deleteInput1 = deleteInput.cloneNode(true);
    table.children[0].children[2].appendChild(deleteInput1);
  }
}

function removeRow(button) {
    var row = button.parentElement.parentElement;
    var tbody = row.parentElement;
    tbody.removeChild(row);
     if (tbody.childElementCount == "2") {
      var deleteButton = tbody.children[0].children[2].children[0];
      tbody.children[0].children[2].removeChild(deleteButton);
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

