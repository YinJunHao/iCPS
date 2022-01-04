/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for the "processes" tab
 * Written by Yin Jun Hao
 */

/* filter from all the task list */
function filterTask () {
  var filter = document.getElementById('filter-input').value.toUpperCase();
  var tasks = document.getElementById('task-list');
  for (var i = 0; i < tasks.childElementCount; i++) {
    var keep = false;
    var task = tasks.children[i];
    var taskname = task.children[0].textContent.toUpperCase();
    if (taskname.indexOf(filter) > -1) {
      keep = true;
    }
    if (keep) {
      task.style.display = '';
    } else {
      task.style.display = 'none';
    }
  }
}

function seePreview (e) {
  e.parentNode.childNodes[1].style.display = 'none';
  e.parentNode.childNodes[3].style.display = 'block';
  e.style.color = 'black';
}

function closePreview (e) {
  e.parentNode.childNodes[1].style.display = 'block';
  e.parentNode.childNodes[3].style.display = 'none';
  e.style.color = 'white';
}

function moreDetails (el) {
  var content = el.parentElement.nextElementSibling;
  if (el.innerHTML == 'expand_more') {
    el.innerHTML = 'chevron_right';
    content.style.display = 'none';

  } else {
    el.innerHTML = 'expand_more';
    content.style.display = 'table';
  }
}

/* For adding additional content in the layers */
function addContent () {
  //create new div to house new objective
  var newDiv = document.createElement('div');
  //create of div elements
  var label = document.createElement('p');
  var newInput = document.createElement('input');
  //create layer button actions
  var layerButtons = document.createElement('div');
  var detailButton = document.createElement('button');
  var deleteButton = document.createElement('button');
  var deleteIcon = '<i class="material-icons">delete</i>';
  //create table for details
  var table = document.createElement('table');
  //search place of insert
  var tableTask = document.getElementById('table-task');
  var count = tableTask.childElementCount;
  var cont = document.getElementsByClassName("cont");
  if (cont.length == 0) {
    index = 0;
  }
  else {
     var index = parseInt(cont[cont.length-1].children[1].name) + 1;
  }
  newDiv.className = 'cont';
  newInput.className = 'form';
  label.innerHTML = '*New*';
  newInput.name = ["new", index.toString()];
  newInput.value = "";
  newInput.type = 'text';
  newInput.required = true;
  layerButtons.className = 'layer-buttons';
  detailButton.className = 'btn btn-outline-info';
  detailButton.name = 'details';
  detailButton.innerHTML = 'Details';
  //to set later
  detailButton.value = index.toString();
  deleteButton.className = 'btn btn-outline-danger';
  deleteButton.type = 'button';
  deleteButton.setAttribute('onclick', 'removeContent(this)');
  //append div
  newDiv.appendChild(label);
  newDiv.appendChild(newInput);
  layerButtons.appendChild(detailButton);
  deleteButton.innerHTML = deleteIcon;
  layerButtons.appendChild(deleteButton);
  newDiv.appendChild(layerButtons);
  tableTask.insertBefore(newDiv, tableTask.children[count - 1]);
}

function removeContent (e) {
  var layerButton = e.parentElement;
  var cont = layerButton.parentElement;
  var parent = cont.parentElement;
  parent.removeChild(cont);
}
/* For adding additional steps conditions */
function addSelect (e, options, name, set) {
  var cell = e.parentElement;
  var tbody = e.parentElement.parentElement.parentElement;
  var count = tbody.childElementCount;
  var select = document.createElement('select');
  var option = document.createElement('option');
  var newRow = tbody.insertRow(count - 1);
  var newCell1 = newRow.insertCell(0);
  var newCell2 = newRow.insertCell(1);
  var deleteConditionButton = document.createElement('button');
  deleteConditionButton.type = 'button';
  deleteConditionButton.innerHTML = '<i class="material-icons">delete</i>';
  deleteConditionButton.className = 'btn btn-outline-danger';
  deleteConditionButton.setAttribute('onclick', 'removeCondition(this)');
  select.name = set.toString()+","+name;
  select.className = 'form-control';
  select.classList.add(name);
  newCell1.appendChild(select);
  newCell2.appendChild(deleteConditionButton);
  option.value = 'none';
  select.appendChild(option);
  for (var i = 0; i < options.length; i++) {
    var option = document.createElement('option')
    option.value = options[i].index
    if (name == 'StepBlocker') {
      option.innerHTML = options[i].sentence
    }
    if (name == 'StateBlocker') {
      option.innerHTML = options[i].var
    }
    if (name == "isAchievedBy") {
      option.innerHTML = options[i].var
    }
    if (name=="isAchievedPreregstateset") {
      option.innerHTML = options[i].index
    }
    if (name == "isFailedByState") {
      option.innerHTML = options[i].var
    }
    if (name == "isFailedIf") {
      option.innerHTML = options[i].var
    }
    if (name=="isFailedPreregstateset") {
      option.innerHTML = options[i].index
    }
    if (name == "StepReturn") {
      option.innerHTML = options[i].sentence
    }
    select.add(option)
  }
}

function addParam (e) {
  var input = document.createElement('input');
  var select = document.createElement('select');
  var choices = ['', 'string', 'boolean', 'int'];
  var tbody = e.parentElement.parentElement.parentElement;
  var count = tbody.childElementCount;
  var newRow = tbody.insertRow(count - 1);
  var newCell1 = newRow.insertCell(0);
  var newCell2 = newRow.insertCell(1);
  var newCell3 = newRow.insertCell(2);
  input.type = 'text';
  input.name = 'param';
  input.className = 'form-control';
  select.name = 'type';
  select.className = 'form-control';
  for (var i = 0; i < choices.length; i++) {
    var option = document.createElement('option');
    option.value = choices[i];
    option.innerHTML = choices[i];
    select.add(option);
  }
  newCell1.appendChild(input);
  newCell2.appendChild(select);
  newCell3.innerHTML = '<button type="button" class="btn btn-outline-danger" onclick="removeCondition(this)"><i class="material-icons">delete</i></button>';
}

function addSet (e, options, name) {
  var table = e.parentElement.parentElement.parentElement.parentElement;
  var tbody = document.createElement('tbody');
  var select = document.createElement('select');
  var option = document.createElement('option');
  var addButton = document.createElement('button');
  var removeSetButton = document.createElement('button');
  var count = table.childElementCount;
  var row = tbody.insertRow(0);
  var row1 = tbody.insertRow(1);
  var cell1 = row.insertCell(0);
  var cell2 = row.insertCell(1);
  var cell3 = row.insertCell(2);
  var cell4 = row.insertCell(3);
  var cella = row1.insertCell(0);
  var cellb = row1.insertCell(1);
  var cellc = row1.insertCell(2);
  var celld = row1.insertCell(3);
  var optionList = JSON.stringify(options);
  if (table.childElementCount == 2) {
    var setno = 1;
  } else {
    var setno = parseInt(table.children[count - 2].rows[0].cells[1].innerHTML) + 1;
  }
  select.className = "form-control";
  select.name = setno.toString()+","+name.toString();
  option.value = "none";
  select.appendChild(option);
  for (var i = 0; i < options.length; i++) {
    var option = document.createElement('option');
    option.value = options[i].index;
    if (name == "hasPrerequisiteStep") {
      option.innerHTML = options[i].sentence;
    }
    if (name == "hasPrerequisiteState") {
      option.innerHTML = options[i].var;
    }
    select.add(option)
  }
  removeSetButton.type = 'button'
  removeSetButton.className = 'btn btn-outline-danger'
  removeSetButton.innerHTML = '<i class="material-icons">delete</i>'
  removeSetButton.setAttribute('onclick', 'removeSet(this,"' + name + '",' + setno.toString() + ')')
  cell1.appendChild(removeSetButton)
  cell2.innerHTML = setno.toString()
  cell3.appendChild(select)
  addButton.className = 'btn btn-outline-info';
  addButton.type = 'button'
  addButton.innerHTML = '<i class="material-icons">add</i>'
  if (name == "hasPrerequisiteState") {
    addButton.setAttribute("onclick", 'addSelectSet(this, ' + optionList + ', "hasPrerequisiteState",' + setno.toString() +')');
    var selectList = document.getElementsByClassName("Preregstateset");
    for (var j = 0; j <selectList.length; j++) {
      var option = document.createElement('option');
      option.value = setno;
      option.innerHTML = setno;
      selectList[j].appendChild(option);
    }
  } else if (name == "hasPrerequisiteStep") {
    addButton.setAttribute("onclick", 'addSelectSet(this, ' + optionList + ', "hasPrerequisiteStep",' + setno.toString() +')');
  }
  cellc.appendChild(addButton);
  cell4.innerHTML = '<button type="button" class="btn btn-outline-danger"\n' +
    '                                                    onclick="removeCondition(this)"><i class="material-icons">delete</i>\n' +
    '                                            </button>';
  table.insertBefore(tbody, table.children[count - 1]);
}

function addSelectSet (e, options, name, set) {
  var tbody = e.parentElement.parentElement.parentElement;
  var count = tbody.childElementCount;
  var select = document.createElement('select');
  var option = document.createElement('option');
  var newRow = tbody.insertRow(count - 1);
  var newCell1 = newRow.insertCell(0);
  var newCell2 = newRow.insertCell(1);
  var newCell3 = newRow.insertCell(2);
  var newCell4 = newRow.insertCell(3);
  var deleteConditionButton = document.createElement('button');
  deleteConditionButton.type = 'button';
  deleteConditionButton.innerHTML = '<i class="material-icons">delete</i>';
  deleteConditionButton.className = 'btn btn-outline-danger';
  deleteConditionButton.setAttribute('onclick', 'removeCondition(this)');
  select.name = set.toString()+","+name;
  select.className = 'form-control';
  newCell3.appendChild(select);
  newCell4.appendChild(deleteConditionButton);
  option.value = 'none';
  select.appendChild(option);
  for (var i = 0; i < options.length; i++) {
    var option = document.createElement('option');
    option.value = options[i].index;
    if (name == "hasPrerequisiteStep") {
      option.innerHTML = options[i].sentence;
    }
    if (name == 'hasPrerequisiteState') {
      option.innerHTML = options[i].var;
    }
    select.add(option)
  }
}

function addSetCorrect (e, options, options1) {
  var table = e.parentElement.parentElement.parentElement.parentElement;
  var tbody = document.createElement('tbody');
  var select = document.createElement('select');
  var addButton = document.createElement("button");
  var addButton1 = document.createElement("button");
  var count = table.childElementCount;
  var row = tbody.insertRow(0);
  var row1 = tbody.insertRow(1);
  var row2 = tbody.insertRow(2);
  var cell1 = document.createElement("th");
  var cell2 = document.createElement("th");
  var cella = document.createElement("th");
  var cellb = document.createElement("th");
  var cellc = document.createElement("th");
  var celld = document.createElement("th");
  var cell3 = row2.insertCell(0);
  var cell4 = row2.insertCell(1);
  var table1 = document.createElement('table');
  var table2 = document.createElement('table');
  var table1Row1 = table1.insertRow(0);
  var table1Row2 = table1.insertRow(1);
  var table2Row1 = table2.insertRow(0);
  var table2Row2 = table2.insertRow(1);
  var table1Row2Cell1 = table1Row2.insertCell(0);
  var table2Row2Cell1 = table2Row2.insertCell(0);
  var setno = count - 1;
  var optionList = JSON.stringify(options);
  var optionList1 = JSON.stringify(options1);
  cell1.innerHTML = "Set " + setno.toString();
  cell1.colSpan = 3;
  cell2.innerHTML = '<button type="button" class="btn btn-outline-danger" onclick="removeSet(this)"><i class="material-icons">delete</i></button>';
  cella.innerHTML = "Prerequisite States Set";
  cellc.innerHTML = "Correct States";
  cell3.colSpan = 2;
  cell4.colSpan = 2;
  table1.className = "table table-borderless";
  table2.className = "table table-borderless";
  addButton.className = "btn btn-outline-info";
  addButton.type = 'button';
  addButton.innerHTML = '<i class="material-icons">add</i>';
  addButton1.className = "btn btn-outline-info";
  addButton1.type = 'button';
  addButton1.innerHTML = '<i class="material-icons">add</i>';
  addButton.setAttribute("onclick", 'addSelect(this, ' + optionList + ', "isAchievedPreregstateset",' + setno.toString() +')');
  addButton1.setAttribute("onclick", 'addSelect(this, ' + optionList1 + ', "isAchievedBy",' + setno.toString() +')');
  table2Row2Cell1.appendChild(addButton1);
  table1Row2Cell1.appendChild(addButton);
  row.appendChild(cell1);
  row.appendChild(cell2);
  row1.appendChild(cella);
  row1.appendChild(cellb);
  row1.appendChild(cellc);
  row1.appendChild(celld);
  cell3.appendChild(table1);
  cell4.appendChild(table2);
  table.insertBefore(tbody, table.children[count - 1]);
}

function addSetFail (e, options, options1, options2) {
  var table = e.parentElement.parentElement.parentElement.parentElement;
  var tbody = document.createElement('tbody');
  var select = document.createElement('select');
  var addButton = document.createElement("button");
  var addButton1 = document.createElement("button");
  var addButton2 = document.createElement("button");
  var addButton3 = document.createElement("button");
  var count = table.childElementCount;
  var row = tbody.insertRow(0);
  var row1 = tbody.insertRow(1);
  var row2 = tbody.insertRow(2);
  var cell1 = document.createElement("th");
  var cell2 = document.createElement("th");
  var cella = document.createElement("th");
  var cellb = document.createElement("th");
  var cellc = document.createElement("th");
  var celld = document.createElement("th");
  var celle = document.createElement("th");
  var cellf = document.createElement("th");
  var cellg = document.createElement("th");
  var cellh = document.createElement("th");
  var cell3 = row2.insertCell(0);
  var cell4 = row2.insertCell(1);
  var cell5 = row2.insertCell(2);
  var cell6 = row2.insertCell(3);
  var table1 = document.createElement('table');
  var table2 = document.createElement('table');
  var table3 = document.createElement('table');
  var table4 = document.createElement('table');
  var table1Row1 = table1.insertRow(0);
  var table1Row2 = table1.insertRow(1);
  var table2Row1 = table2.insertRow(0);
  var table2Row2 = table2.insertRow(1);
  var table3Row1 = table3.insertRow(0);
  var table3Row2 = table3.insertRow(1);
  var table4Row1 = table4.insertRow(0);
  var table4Row2 = table4.insertRow(1);
  var table1Row2Cell1 = table1Row2.insertCell(0);
  var table2Row2Cell1 = table2Row2.insertCell(0);
  var table3Row2Cell1 = table3Row2.insertCell(0);
  var table4Row2Cell1 = table4Row2.insertCell(0);
  var setno = count - 1;
  var optionList = JSON.stringify(options);
  var optionList1 = JSON.stringify(options1);
  var optionList2 = JSON.stringify(options2);
  cell1.innerHTML = "Set " + setno.toString();
  cell1.colSpan = 6;
  cell2.colSpan = 2;
  cell2.innerHTML = '<button type="button" class="btn btn-outline-danger" onclick="removeSet(this)"><i class="material-icons">delete</i></button>';
  cella.innerHTML = "Prerequisite States Set";
  cellc.innerHTML = "Failed States";
  celle.innerHTML = "Correct States";
  cellg.innerHTML = "Return to Step";
  cell3.colSpan = 2;
  cell4.colSpan = 2;
  cell5.colSpan = 2;
  cell6.colSpan = 2;
  table1.className = "table table-borderless";
  table2.className = "table table-borderless";
  table3.className = "table table-borderless";
  table4.className = "table table-borderless";
  addButton.className = "btn btn-outline-info";
  addButton.type = 'button';
  addButton.innerHTML = '<i class="material-icons">add</i>';
  addButton1.className = "btn btn-outline-info";
  addButton1.type = 'button';
  addButton1.innerHTML = '<i class="material-icons">add</i>';
  addButton2.className = "btn btn-outline-info";
  addButton2.type = 'button';
  addButton2.innerHTML = '<i class="material-icons">add</i>';
  addButton3.className = "btn btn-outline-info";
  addButton3.type = 'button';
  addButton3.innerHTML = '<i class="material-icons">add</i>';
  addButton.setAttribute("onclick", 'addSelect(this, ' + optionList + ', "isFailedPreregstateset",' + setno.toString() +')');
  addButton1.setAttribute("onclick", 'addSelect(this, ' + optionList1 + ', "isFailedByState",' + setno.toString() +')');
  addButton2.setAttribute("onclick", 'addSelect(this, ' + optionList1 + ', "isFailedIf",' + setno.toString() +')');
  addButton3.setAttribute("onclick", 'addSelect(this, ' + optionList2 + ', "StepReturn",' + setno.toString() +')');
  table1Row2Cell1.appendChild(addButton);
  table2Row2Cell1.appendChild(addButton1);
  table3Row2Cell1.appendChild(addButton2);
  table4Row2Cell1.appendChild(addButton3);
  row.appendChild(cell1);
  row.appendChild(cell2);
  row1.appendChild(cella);
  row1.appendChild(cellb);
  row1.appendChild(cellc);
  row1.appendChild(celld);
  row1.appendChild(celle);
  row1.appendChild(cellf);
  row1.appendChild(cellg);
  row1.appendChild(cellh);
  cell3.appendChild(table1);
  cell4.appendChild(table2);
  cell5.appendChild(table3);
  cell6.appendChild(table4);
  table.insertBefore(tbody, table.children[count - 1]);
}
function removeSet (e, name, value) {
  var table = e.parentElement.parentElement.parentElement.parentElement;
  var tbody = e.parentElement.parentElement.parentElement;
  table.removeChild(tbody);
  if (name == "hasPrerequisiteState") {
    var selectList = document.getElementsByClassName("Preregstateset");
    for (var i = 0; i <selectList.length; i++) {
      for (var j = 0; j <selectList[i].length; j++) {
        if (selectList[i].children[j].value == value) {
            selectList[i].removeChild(selectList[i].children[j])
        }
      }
    }
  }
}

function removeCondition (e) {
  var row = e.parentElement.parentElement
  var tbody = e.parentElement.parentElement.parentElement
  if (tbody.childElementCount == 2) {
    removeSet(e)
  } else {
    tbody.removeChild(row)
  }
}

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

// For tree
function showTree () {
  var tree = document.getElementById("tree-nav");
  var content = document.getElementById("content-layer");
  var button = document.getElementById("tree-nav-button");
  tree.style.display = 'block';
  content.style.display = 'none';
  button.setAttribute("onclick", "closeTree()");
  drawline();
}

function closeTree () {
  var tree = document.getElementById('tree-nav');
  var content = document.getElementById('content-layer');
  var button = document.getElementById("tree-nav-button");
  tree.style.display = 'none';
  content.style.display = 'block';
  button.setAttribute("onclick", "showTree()");
}

function sortItems() {
  var items = document.getElementsByClassName('tosort');
  for (var j = 0, k = items.length; k < l; j++) {
    var toSort = items[j].children;
    toSort = Array.prototype.slice.call(toSort, 0);

    toSort.sort(function (a, b) {
      var aord = +a.id.split('-')[1];
      var bord = +b.id.split('-')[1];
      // two elements never have the same ID hence this is sufficient:
      return aord > bord ? 1 : -1;
    })
    var parent = items[j]
    parent.innerHTML = '';

    for (var i = 0, l = toSort.length; i < l; i++) {
      parent.appendChild(toSort[i]);
    }
  }
}

// window.onload = sortItems();

function drawline () {
  var items = document.getElementsByClassName("line");
  for (var i = 0, l = items.length; i < l; i++) {
    var str = items[i].id.split(",");
    var line = document.getElementById(items[i].id);
    var div1 = document.getElementById(str[0]);
    var div2 = document.getElementById(str[1]);
    // var x1 = rect1.left + ((rect1.right - rect1.left) / 2);
    // var y1 = rect1.bottom;
    // var x2 = rect2.left + ((rect2.right - rect2.left) / 2);
    // var y2 = rect2.top;

    var x1 = div1.offsetLeft + (div1.offsetWidth / 2)
    var y1 = div1.offsetTop + div1.offsetHeight
    var x2 = div2.offsetLeft + (div2.offsetWidth / 2)
    var y2 = div2.offsetTop
    console.log(x1)
    console.log(y1)
    line.setAttribute('x1', x1)
    line.setAttribute('y1', y1)
    line.setAttribute('x2', x2)
    line.setAttribute('y2', y2);
  }
}

// window.onload = drawline();
