/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for "edit_process.html"
 * Written by Yin Jun Hao
 */



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
function addContent (e) {
  //create new div to house new objective
  var newDiv = document.createElement('div');
  var emptyDiv = document.createElement("div");
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
  var tableTask = e.parentElement.parentElement;
  var count = tableTask.childElementCount;
  var lastcont = tableTask.children[count-3];
  console.log(count);
  var lastchildname = lastcont.children[1].name;
  var index = index_dict[lastchildname.split("-")[0]] + 1;
  index_dict[lastchildname.split("-")[0]] += 1;
  newDiv.className = 'cont';
  newInput.className = 'form';
  newInput.classList.add(lastchildname.split("-")[0] + "-" + index.toString());
  label.innerHTML = '*New*';
  newInput.name = lastchildname.split("-")[0] + "-name-"+ index.toString() + "-" + lastchildname.split("-")[3] + "-" + lastchildname.split("-")[4];
  newInput.value = "";
  newInput.type = 'text';
  newInput.required = true;
  newInput.setAttribute("onchange", "nameUpdate(this)");
  layerButtons.className = 'layer-buttons';
  detailButton.className = 'btn btn-outline-info';
  detailButton.name = 'details';
  detailButton.innerHTML = 'Details';
  //to set later
  detailButton.type = "button";
  detailButton.setAttribute("onclick", "showLayer(this.id)");
  detailButton.id = lastchildname.split("-")[0] + "-content-layer-" + index.toString();
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
  tableTask.insertBefore(emptyDiv, tableTask.children[count - 1])
  tableTask.insertBefore(newDiv, tableTask.children[count - 1]);
  if (lastchildname.split("-")[0] == "objective_layer_1"){
    var nextLayer = "step";
  } else {
    var nextIndex = parseInt(lastchildname.split("-")[0].split("_")[2]) - 1;
    var nextlayer = lastchildname.split("-")[0].split("_")[0] + "_" + lastchildname.split("-")[0].split("_")[0] + "_" + nextIndex.toString();
  }
  // Create new layer details
  var layerDetailsDiv = document.createElement('div');
  var p1 = document.createElement('p');
  var p2 = document.createElement('p');
  var p3 = document.createElement('p');
  var p4 = document.createElement('p');
  var layerDetailInput = document.createElement('input');
  layerDetailsDiv.className = "col layer-details";
  layerDetailsDiv.id = lastchildname.split("-")[0] + "-layer-details-" + index.toString();
  layerDetailInput.className = "form";
  layerDetailInput.classList.add(lastchildname.split("-")[0] + "-" + index.toString() +"-main");
  layerDetailInput.type= "text";
  layerDetailInput.name = lastchildname.split("-")[0] + "-name-" + index.toString();
  layerDetailInput.setAttribute("onchange", "nameUpdate(this)");
  p1.innerHTML = "Name: " + String(layerDetailInput.outerHTML);
  p2.innerHTML = "Layer: " + lastchildname.split("-")[0];
  p3.innerHTML = "Created By: Current User";
  p4.innerHTML = "Last Update: New Addition";
  layerDetailsDiv.appendChild(p1);
  layerDetailsDiv.appendChild(p2);
  layerDetailsDiv.appendChild(p3);
  layerDetailsDiv.appendChild(p4);
  var processPage = document.getElementById("process-page");
  var row = processPage.children[0].children[0];
  row.insertBefore(layerDetailsDiv, row.children[row.children.length -2]);

  //Create new tree
  var treeDiv = document.createElement('div');
  var treeButton = document.createElement('button');
  var treesvg = document.createElement('svg');
  var treeLine = document.createElement("line");
  treeDiv.className = "tree-detail";
  treeButton.type = "button";
  treeButton.id = lastchildname.split("-")[0] + "-tree-nav-" + index.toString();
  treeButton.setAttribute("onclick", "showLayer(this.id)");
  treesvg.className = "svg";
  treeLine.className = "line";
  treeLine.id = lastchildname.split("-")[3] + "-" + lastchildname.split("-")[4] + "," + lastchildname.split("-")[0] + "-" + index.toString();
  var treeRow = document.getElementById(lastchildname.split("-")[0]+"-tree-row");
  treesvg.appendChild(treeLine);
  treeDiv.appendChild(treeButton);
  treeRow.appendChild(treeDiv);
  treeRow.appendChild(treesvg);

  //Create new content
  var contentDiv = document.createElement('div');
  var backDiv = document.createElement('div');
  var back = document.createElement('a');
  var backIcon = document.createElement('i');
  var backSpan = document.createElement('span');
  contentDiv.id = lastchildname.split("-")[0] + "-content-details-" + index.toString();
  backDiv.className = "back";
  back.setAttribute("onclick", "showLayer(this.id)");
  back.id = lastchildname.split("-")[3] + "-previous-layer-" + lastchildname.split("-")[4];
  backSpan.className = "replace-underscore";
  backSpan.innerHTML = lastchildname.split("-")[3];
  back.appendChild(backIcon);
  back.appendChild(backSpan);
  backDiv.appendChild(back);
  contentDiv.appendChild(backDiv);
  if (lastchildname.split("-")[0] == "step") {
    contentDiv.className = "grid-task";
  } else {
    contentDiv.className = "table-task";
    var contentLayerDiv = document.createElement('div');
    var addLayerButton = document.createElement('button');
    var addContentDiv = document.createElement('div');
    // var addContentButton = document.createElement('button');
    addLayerButton.className = "btn btn-outline-info";
    addLayerButton.name = "add-layer-before";
    addLayerButton.innerHTML = "Add Layer Before";
    contentLayerDiv.className = "content-layer replace-underscore";
    contentLayerDiv.innerHTML = "content layer: " + nextLayer + String(addLayerButton.outerHTML);
    addContentDiv.innerHTML = '<button id="add-objective-button" type="button" class="btn btn-outline-info" onclick="addContent(this)"><i class="material-icons">add</i></button>';

    // var detailButton1 = document.createElement('button');
    // var deleteButton1 = document.createElement('button');
    // var deleteIcon1 = '<i class="material-icons">delete</i>';
    // var newDiv1 = document.createElement('div');
    // var label1 = document.createElement('p');
    // var newInput1 = document.createElement('input');
    // var index1 = index_dict[nextLayer] + 1;
    // newDiv1.className = 'cont';
    // index_dict[nextLayer] += 1;
    // newInput1.className = 'form';
    // newInput1.classList.add(nextLayer + "-" + index1.toString());
    // label1.innerHTML = '*New*';
    // newInput1.name = nextLayer + "-name-"+ index1.toString() + "-" + lastchildname.split("-")[0] + "-" + index.toString();
    // newInput1.value = "";
    // newInput1.type = 'text';
    // newInput1.required = true;
    // newInput1.setAttribute("onchange", "nameUpdate(this)");
    // detailButton1.className = 'btn btn-outline-info';
    // detailButton1.name = 'details';
    // detailButton1.innerHTML = 'Details';
    // //to set later
    // detailButton1.type = "button";
    // detailButton1.setAttribute("onclick", "showLayer(this.id)");
    // detailButton1.id = lastchildname.split("-")[0] + "-content-layer-" + index.toString();
    // deleteButton1.className = 'btn btn-outline-danger';
    // deleteButton1.type = 'button';
    // deleteButton1.setAttribute('onclick', 'removeContent(this)');
    // newDiv1.appendChild(label1);
    // newDiv1.appendChild(newInput1);
    contentDiv.appendChild(contentLayerDiv);
    // var newDiv2 = document.createElement('div');
    // contentDiv.appendChild(newDiv1);
    // contentDiv.appendChild(newDiv2);
    contentDiv.appendChild(addContentDiv);
  }

  var contentLayer = document.getElementById("content-layer");
  contentLayer.appendChild(contentDiv);
}

function removeContent (e) {
  var layerButton = e.parentElement;
  var cont = layerButton.parentElement;
  var parent = cont.parentElement;
  parent.removeChild(cont);
  var details = cont.nextElementSibling;
  parent.removeChild(details);
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
  if (name != "Stepblocker" || name != "StateBlocker") {
    select.name = set.toString() + "," + name;
  }
  else {
    select.name = set.toString();
  }
  select.className = 'form-control';
  select.classList.add(name);
  newCell1.appendChild(select);
  newCell2.appendChild(deleteConditionButton);
  option.value = 'none';
  select.appendChild(option);
  for (var i = 0; i < options.length; i++) {
    var option = document.createElement('option');
    if (name== "location_id") {
      option.value = options[i];
      option.innerHTML = options[i];
    }
    else
      {
        option.value = options[i].index;
      }
    if (name == 'StepBlocker') {
      option.innerHTML = options[i].sentence;
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
  var row = e.parentElement.parentElement;
  var tbody = e.parentElement.parentElement.parentElement;
  if (tbody.childElementCount == 2) {
    removeSet(e);
  } else {
    tbody.removeChild(row);
  }
}

function removeSelection (e) {
  var row = e.parentElement.parentElement;
  var tbody = e.parentElement.parentElement.parentElement;
  tbody.removeChild(row);
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
    var div1IDList = str[0].split("-");
    var div1ID = div1IDList[0] + "-tree-nav-" + div1IDList[1];
    var div1 = document.getElementById(div1ID);
    var div2IDList = str[1].split("-");
    var div2ID = div2IDList[0] + "-tree-nav-" + div2IDList[1];
    var div2 = document.getElementById(div2ID);
    // var x1 = rect1.left + ((rect1.right - rect1.left) / 2);
    // var y1 = rect1.bottom;
    // var x2 = rect2.left + ((rect2.right - rect2.left) / 2);
    // var y2 = rect2.top;

    var x1 = div1.offsetLeft + (div1.offsetWidth / 2);
    var y1 = div1.offsetTop + div1.offsetHeight;
    var x2 = div2.offsetLeft + (div2.offsetWidth / 2);
    var y2 = div2.offsetTop;
    console.log(x1);
    console.log(y1);
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
  }
}

// window.onload = drawline();
function displayForm(robotResource, hardwareResource, humanResource, softwareResource, physicalResourceList) {
  var selectedResource = document.getElementById("resource-class").value.toLowerCase();
  console.log(selectedResource);
  var physicalResource = ["hardware", "human", "robot"];
  var addPage = document.getElementById("resource-form");
  addPage.innerHTML = "";
  // var formID = selectedResource + "-resource-form";
  // var form = document.getElementById(formID);
  // console.log(form);
  // addPage.appendChild(form);
  // form.style.display = "block";
  // addPage.innerHTML=selectedResource;
  if (physicalResource.includes(selectedResource)) {
    console.log("physical");
    addPage.innerHTML = '<div id="robot-resource-form" class="add-resource-form">' +
        '<dt><label for="name">Name</label>' +
        '</dt><dd><input class="form-control" id="name" name="name" required="" type="text" value=""></dd>' +
        '<div class="form-row">' +
        '<div class="col">' +
        '<dt><label for="type">Type</label>' +
        '</dt><dd><select class="form-control" id="type" name="type">' +
        '</select></dd></div>' +
        '<div class="col">' +
        '<dt><label for="type_new">If the desired type is not found</label>' +
        '</dt><dd><input class="form-control" id="type_new" name="type_new" type="text" value=""></dd>' +
        '</div>' +
        '</div>' +
        '<div class="form-row">' +
        '<div class="col">' +
        '<dt><label for="position_sensor_tag">Position Sensor Tag</label>' +
        '</dt><dd><input class="form-control" id="position_sensor_tag" name="position_sensor_tag" type="text" value=""></dd>' +
        '</div>' +
        '<div class="col">' +
        '<dt><label for="status">Status</label>'+
        '</dt><dd><select class="form-control" id="status" name="status"><option value="1">Active</option><option value="0">Inactive</option></select>'+
        '</dd></div>' +
        '</div>' +
        '<p class="label-header">Position</p>' +
        '<div class="form-inline">' +
        '<label class="sub-label" for="position_x">x</label>' +
        '<input class="form-control" id="position_x" name="position_x" type="text" value="">' +
        '<label class="sub-label" for="position_y">y</label>' +
        '<input class="form-control" id="position_y" name="position_y" type="text" value="">' +
        '<label class="sub-label" for="position_z">z</label>' +
        '<input class="form-control" id="position_z" name="position_z" type="text" value="">' +
        '</div>';
  } else {
    console.log("software");
    addPage.innerHTML = '<div id="software-resource-form" class="add-resource-form">' +
        '<dt><label for="name">Name</label>' +
        '</dt><dd><input class="form-control" id="name" name="name" required="" type="text" value=""></dd>' +
        '<div class="form-row">' +
        '<div class="col">' +
        '<dt><label for="type">Type</label>' +
        '</dt><dd><select class="form-control" id="type" name="type"></select></dd></div>' +
        '<div class="col">' +
        '<dt><label for="type_new">If desired type not found, enter here</label>' +
        '</dt><dd><input class="form-control" id="type_new" name="type_new" type="text" value=""></dd></div></div>' +
        '<div class="form-row">' +
        '<div class="col">' +
        '<div id="params">' +
        '<dt><label for="param">Parameters</label></dt>' +
        '<div class="new-variable">' +
        '<dd><input class="form-control" id="param" name="param" type="text" value=""></dd></div></div>' +
        '<i class="material-icons add-variable" id="add-param-button">add_circle</i></div>' +
        '<div class="col">' +
        '<div id="states">' +
        '<dt><label for="state">States</label></dt>' +
        '<div class="new-variable">' +
        '<dd><input class="form-control" id="state" name="state" type="text" value=""></dd></div></div>' +
        '<i class="material-icons add-variable" id="add-state-button">add_circle</i></div></div></div>' +
        '<div class="physical-resource-for-software" id="physical-resource-for-software">' +
        '<dt>' +
        '<label for="physical_resource">Software for Following Physical Resource/s</label>' +
        '</dt>' +
        '<table class="table" id="table">' +
        '<thead>' +
        '<tr>' +
        '<th>Class</th>' +
        '<th>Name</th>' +
        '<th class="delete-column"></th>' +
        '</tr>' +
        '</thead>' +
        '<tbody id="add-physical-resource">' +
        '<tr>' +
        '<td>' +
        '<dd>' +
        '<select class="form-control" name="physical-resource-class" id="1,physical-resource-class">' +
        '<option value=""></option>' +
        '<option value="robot">robot</option>' +
        '<option value="hardware">hardware</option>' +
        '<option value="human">human</option>' +
        '</select>' +
        '</dd>' +
        '</td>' +
        '<td>' +
        '<dd>' +
        '<select class="form-control" name="physical-resource-id" id="1,physical-resource-choice">' +
        '<option value=""></option>' +
        '</select></dd>' +
        '</td>' +
        '<td></td>' +
        '</tr>' +
        '<tr>' +
        '<td colspan="2"><i class="material-icons add-variable" id="add-physical-cyber">add_circle</i></td>' +
        '</tr>' +
        '</tbody>' +
        '</table>' +
        '</div>';
        var softwareOption = document.getElementById("1,physical-resource-class");
        softwareOption.setAttribute("onchange", "populateOptions("+JSON.stringify(physicalResourceList)+", this.id, this.value, 'none')");
        var addPhysical = document.getElementById("add-physical-cyber");
        addPhysical.setAttribute("onclick", "addPhysicalResource("+JSON.stringify(physicalResourceList)+")");
  }
  var typeForm = document.getElementById("type");
  var option = document.createElement("option");
  option.value = "";
  typeForm.add(option);
  switch (selectedResource) {
    case "robot":
       var locationForm = document.getElementById("location_id");
  var option1 = document.createElement("option");
  option1.value = "";
  locationForm.add(option1);
      for (var i = 0; i < robotResource["type_choices"].length; i++) {
        var option = document.createElement('option');
        option.value = robotResource["type_choices"][i];
        option.innerHTML = robotResource["type_choices"][i];
        typeForm.add(option);
      }
      for (var j = 0; j < robotResource["location_id_choices"].length; j++) {
        var option1 = document.createElement("option");
        option1.value = robotResource["location_id_choices"][j];
        option1.innerHTML = robotResource["location_id_choices"][j];
        typeForm.add(option);
      }
      break;
    case "hardware":
      var locationForm = document.getElementById("location_id");
      var option1 = document.createElement("option");
      option1.value = "";
      locationForm.add(option1);
      for (var i = 0; i < hardwareResource["type_choices"].length; i++) {
        var option = document.createElement('option');
        option.value = hardwareResource["type_choices"][i];
        option.innerHTML = hardwareResource["type_choices"][i];
        typeForm.add(option);
      }
      for (var j = 0; j < hardwareResource["location_id_choices"].length; j++) {
        var option1 = document.createElement("option");
        option1.value = hardwareResource["location_id_choices"][j];
        option1.innerHTML = hardwareResource["location_id_choices"][j];
        typeForm.add(option);
      }
      break;
    case"human":
      var locationForm = document.getElementById("location_id");
      var option1 = document.createElement("option");
      option1.value = "";
      locationForm.add(option1);
      for (var i = 0; i < humanResource["type_choices"].length; i++) {
        var option = document.createElement('option');
        option.value = humanResource["type_choices"][i];
        option.innerHTML = humanResource["type_choices"][i];
        typeForm.add(option);
      }
      for (var j = 0; j < humanResource["location_id_choices"].length; j++) {
        var option1 = document.createElement("option");
        option1.value = humanResource["location_id_choices"][j];
        option1.innerHTML = humanResource["location_id_choices"][j];
        typeForm.add(option);
      }
      break;
    case"software":
      var paramButton = document.getElementById("add-param-button");
      var stateButton = document.getElementById("add-state-button");
      paramButton.setAttribute("onclick", "addVariable('params')");
      stateButton.setAttribute("onclick","addVariable('states')");
      break;
  }
}

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

function populateOptions(physicalResource, number, resourceClass, index) {
  var no = number.split(",")[0];
  if (index == "none") {
    var populateID = no +",physical-resource-choice";
  }
    else {
      var populateID = no + ",state-exec-physical-name-"+index.toString();
  }
    console.log(populateID);
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

function populateOptionsCyber(cyberResource, number, resourceID, index) {
  var no = number.split(",")[0];
  var populateID = no + ",state-exec-software-name-"+index.toString();
  var populateArea = document.getElementById(populateID);
  populateArea.innerHTML = "";
  var option = document.createElement("option");
  option.value = "";
  option.innerHTML = "";
  populateArea.appendChild(option);
  console.log(resourceID);
  console.log(cyberResource);
  for (var i=0; i<cyberResource.length; i++) {
    if (cyberResource[i]["physical_resource_id"].includes(resourceID)) {
        var option = document.createElement("option");
        option.value = cyberResource[i]["ID"];
        option.innerHTML = cyberResource[i]["name"];
        populateArea.appendChild(option);
    }
  }
}

function populateOptionsClass(stateclass, number, type) {
  var no = number.split(",")[0];
  console.log(no);
  var populateID = no + ",state-exec-class";
  var populateArea = document.getElementById(populateID);
  populateArea.innerHTML = "";
  var option = document.createElement("option");
  option.value = "";
  option.innerHTML = "";
  populateArea.appendChild(option);
  for (var i=0; i<stateclass[type].length; i++) {
      var option = document.createElement("option");
      option.value = stateclass[type][i];
      option.innerHTML = stateclass[type][i];
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
  var number = parseInt(id.split(",")[0]) + 1;
  var deleteInput = document.createElement("ICON");
  deleteInput.className = "material-icons"
  deleteInput.classList.add("remove-variable");
  deleteInput.innerHTML = "remove_circle";
  deleteInput.setAttribute("onclick", "removeRow(this)");
  var deletetd = document.createElement("td");
  deletetd.appendChild(deleteInput);
  select1.className = "form-control";
  select1.name = "physical-resource-class";
  select1.setAttribute("onchange", "populateOptions("+JSON.stringify(list)+", this.id, this.value, 'none')");
  select1.id = number.toString() + ",physical-resource-class";
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
  select2.id = number.toString() + ",physical-resource-choice";
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

function addStateExec(stateClass, physicalResource, softwareResource) {
  var typeList = ["", "resource", "job", "task"];
  var physicalList = ["", "robot", "hardware", "human"];
  var table = document.getElementById("state-executors");
  console.log(table.children.length);
  if (table.children.length > 2) {
    var lastChild = table.children[table.children.length - 3];
    var number = lastChild.id.split(",")[0];
    var newNumber = parseInt(number) + 1;
  } else {
    var newNumber = 1;
  }
  var newTbody = document.createElement("tbody");
  var newRow1 = document.createElement("tr");
  var row1Head = document.createElement("th");
  var row1td = document.createElement("td");
  var row1delete = document.createElement("td");
  var nameInput = document.createElement("input");
  var newRow2 = document.createElement("tr");
  var newRow3 = document.createElement("tr");
  var row3td1 = document.createElement("td");
  var stateExecType = document.createElement("select");
  var row3td2 = document.createElement("td");
  var stateExecClass = document.createElement("select");
  var row3td3 = document.createElement("td");
  var stateExecClassNew = document.createElement("input");
  var newRow4 = document.createElement("tr");
  var newRow5 = document.createElement("tr");
  var row5td1 = document.createElement("td");
  var stateExecPhysicalClass = document.createElement("select");
  var row5td2 = document.createElement("td");
  var stateExecPhysicalName = document.createElement("select");
  var row5td3 = document.createElement("td");
  var newRow6 = document.createElement("tr");
  var row6td1 = document.createElement("td");
  var row6td2 = document.createElement("td");
  var row6td3 = document.createElement("td");
  var row6button = document.createElement("button");
  var stateExecSoftwareName = document.createElement("select");
  newTbody.id = newNumber.toString()+',state-executor';
  nameInput.name = newNumber.toString() + ',state-exec-setname';
  nameInput.className = "form-control name-col";
  row1Head.innerHTML = "Name: "
  row1delete.innerHTML = '<button type="button" class="btn btn-outline-danger" onclick="removeStateExec(this)"><i class="material-icons">delete</i></button>';
  row1td.appendChild(nameInput);
  newRow1.appendChild(row1Head);
  newRow1.appendChild(row1td);
  newRow1.appendChild(row1delete);
  newRow2.innerHTML = '<tr><th>type</th><th colspan="2">class</th></tr>';
  stateExecType.name = newNumber.toString() +  ",state-exec-type";
  stateExecType.className = "form-control name-col option";
  stateExecType.id = newNumber.toString() + ",state-exec-type-";
  stateExecType.setAttribute("onchange", "populateOptionsClass("+JSON.stringify(stateClass)+", this.id, this.value)");
  for (var i=0; i<typeList.length; i++) {
    var option = document.createElement("option");
    option.value = typeList[i];
    option.innerHTML = typeList[i];
    stateExecType.appendChild(option);
  }
  stateExecClass.name = newNumber.toString() + ',state-exec-class';
  stateExecClass.id = newNumber.toString() + ',state-exec-class';
  stateExecClass.className = "form-control name-col option";
  var option = document.createElement("option");
  option.value = "";
  option.innerHTML = "";
  stateExecClass.appendChild(option);
  stateExecClassNew.className = "form-control name-col option";
  stateExecClassNew.placeholder = "new class";
  stateExecClassNew.name = newNumber.toString() + ',state-exec-class-diff';
  row3td1.appendChild(stateExecType);
  row3td2.appendChild(stateExecClass);
  row3td3.appendChild(stateExecClassNew);
  newRow3.appendChild(row3td1);
  newRow3.appendChild(row3td2);
  newRow3.appendChild(row3td3);
  newRow4.innerHTML = '<th>Executor Class</th><th>Executor Name</th><th>Executor Software</th>';
  stateExecPhysicalClass.id = newNumber.toString() + ',state-exec-physical-class-1';
  stateExecPhysicalClass.name = newNumber.toString() + ',state-exec-physical-class';
  stateExecPhysicalClass.className = "form-control name-col option";
  stateExecPhysicalClass.setAttribute("onchange", "populateOptions("+JSON.stringify(physicalResource)+", this.id, this.value, 1)");
  for (var j=0; j<physicalList.length; j++) {
    var option = document.createElement("option");
    option.value = physicalList[j];
    option.innerHTML = physicalList[j];
    stateExecPhysicalClass.appendChild(option);
  }
  stateExecPhysicalName.id = newNumber.toString() + ',state-exec-physical-name-1';
  stateExecPhysicalName.name = newNumber.toString() + ',state-exec-physical-name';
  stateExecPhysicalName.className = "form-control name-col option";
  stateExecPhysicalName.setAttribute("onchange", "populateOptionsCyber("+JSON.stringify(softwareResource)+", this.id, this.value, 1)");
  stateExecSoftwareName.id = newNumber.toString() + ',state-exec-software-name-1';
  stateExecSoftwareName.name = newNumber.toString() + ',state-exec-software-name';
  stateExecSoftwareName.className = "form-control name-col option";
  row5td1.appendChild(stateExecPhysicalClass);
  row5td2.appendChild(stateExecPhysicalName);
  row5td3.appendChild(stateExecSoftwareName);
  row6button.innerHTML = '<i class="material-icons">add</i>';
  row6button.className = 'btn btn-outline-info';
  row6button.type = "button";
  row6button.setAttribute("onclick", "addExecutors("+newNumber.toString()+","+JSON.stringify(physicalResource)+","+JSON.stringify(softwareResource)+")");
  row6td3.appendChild(row6button);
  newRow6.appendChild(row6td1);
  newRow6.appendChild(row6td2);
  newRow6.appendChild(row6td3);
  newRow5.appendChild(row5td1);
  newRow5.appendChild(row5td2);
  newRow5.appendChild(row5td3);
  newTbody.appendChild(newRow1);
  newTbody.appendChild(newRow2);
  newTbody.appendChild(newRow3);
  newTbody.appendChild(newRow4);
  newTbody.appendChild(newRow5);
  newTbody.appendChild(newRow6);
  table.insertBefore(newTbody, table.children[table.children.length-2]);
  if (table.childElementCount == "5") {
    var deletetd = document.createElement("td");
    deletetd.innerHTML = '<button type="button" class="btn btn-outline-danger" onclick="removeStateExec(this)"><i class="material-icons">delete</i></button>';
    lastChild.children[0].appendChild(deletetd);
  }
}

function removeStateExec(button) {
    var tbody = button.parentElement.parentElement.parentElement;
    var table = document.getElementById("state-executors");
    table.removeChild(tbody);
     if (table.childElementCount == "4") {
      var deleteButton = table.children[1].children[0].children[2];
      table.children[1].children[0].removeChild(deleteButton);
    }
}

function addExecutors(number, physicalResource, softwareResource) {
  var physicalList = ["", "robot", "hardware", "human"];
  var bodyID = number.toString() + ",state-executor";
  var tbody = document.getElementById(bodyID);
  var newRow = document.createElement("tr");
  var td1 = document.createElement("td");
  var stateExecPhysicalClass = document.createElement("select");
  var td2 = document.createElement("td");
  var stateExecPhysicalName = document.createElement("select");
  var td3 = document.createElement("td");
  var stateExecSoftwareName = document.createElement("select");
  var count = tbody.children.length;
  var newIndex = count - 3;
  stateExecPhysicalClass.id = number.toString() + ',state-exec-physical-class-'+newIndex.toString();
  stateExecPhysicalClass.name = number.toString() + ',state-exec-physical-class';
  stateExecPhysicalClass.className = "form-control name-col option";
  stateExecPhysicalClass.setAttribute("onchange", "populateOptions("+JSON.stringify(physicalResource)+", this.id, this.value, "+newIndex.toString()+")");
  for (var j=0; j<physicalList.length; j++) {
    var option = document.createElement("option");
    option.value = physicalList[j];
    option.innerHTML = physicalList[j];
    stateExecPhysicalClass.appendChild(option);
  }
  stateExecPhysicalName.id = number.toString() + ',state-exec-physical-name-'+newIndex.toString();
  stateExecPhysicalName.name = number.toString() + ',state-exec-physical-name';
  stateExecPhysicalName.className = "form-control name-col option";
  stateExecPhysicalName.setAttribute("onchange", "populateOptionsCyber("+JSON.stringify(softwareResource)+", this.id, this.value, "+newIndex.toString()+")");
  stateExecSoftwareName.id = number.toString() + ',state-exec-software-name-'+newIndex.toString();
  stateExecSoftwareName.name = number.toString() + ',state-exec-software-name';
  stateExecSoftwareName.className = "form-control name-col option";
  td1.appendChild(stateExecPhysicalClass);
  td2.appendChild(stateExecPhysicalName);
  td3.appendChild(stateExecSoftwareName);
  newRow.appendChild(td1);
  newRow.appendChild(td2);
  newRow.appendChild(td3);
  tbody.insertBefore(newRow, tbody.children[tbody.children.length - 1]);
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

window.onbeforeunload = function redirectPrompt() {
  return "Are you sure";
}


function showLayer(e) {
  var layerDetailsList = document.getElementsByClassName("layer-details");
  var layer = e.split("-")[0];
  var index = e.split("-")[3];
  var treeNavCheck = e.split("-")[1];
  var tableTaskList = document.getElementsByClassName("table-task");
  var gridTaskList = document.getElementsByClassName("grid-task");
  var contentDetailsID = layer + "-content-details-" + index;
  var layerDetailsID = layer + "-layer-details-"+ index;
  var contentDetails = document.getElementById(contentDetailsID);
  var layerDetails = document.getElementById(layerDetailsID);
  var contentDetails = document.getElementById(contentDetailsID);
  var treeNavID = layer + "-tree-nav-" + index;
  var treeNav = document.getElementById(treeNavID);
  var glowItem = document.getElementsByClassName("glow");
  for (var i = 0; i < layerDetailsList.length; i++) {
    if (layerDetailsList[i].style.display == "block") {
      layerDetailsList[i].style.display = "none";
    }
  }
  for (var j = 0; j < tableTaskList.length; j++) {
    if (tableTaskList[j].style.display == "block") {
      tableTaskList[j].style.display = "none";
    }
  }
  for (var k = 0; k < gridTaskList.length; k++) {
    if (gridTaskList[k].style.display == "grid") {
      gridTaskList[k].style.display = "none";
    }
  }
  if (treeNavCheck=="tree") {
    closeTree();
  }
  glowItem[0].className = "";
  treeNav.className = "glow";
  if (layer=="step") {
   contentDetails.style.display = "grid";
  } else {
    contentDetails.style.display = "block";
  }
  layerDetails.style.display = "block";
}

function nameUpdate(e) {
  var classList = e.classList[1];
  console.log(e.value);
  var treeID = classList.split("-")[0] + "-tree-nav-" + classList.split("-")[1];
  var tree = document.getElementById(treeID);
  tree.innerHTML = e.value;
  if (e.id.includes("task") == false) {
    if (classList.includes("main")) {
      var str = classList.split("-");
      var change = str[0] + "-" + str[1];
      var changeArea = document.getElementsByClassName(change);
      changeArea[0].value = e.value;
      changeArea[0].innerHTML = e.value;
      console.log(changeArea);
    } else {
      var change = classList + "-main";
      var changeArea = document.getElementsByClassName(change);
      changeArea[0].value = e.value;
      changeArea[0].innerHTML = e.value;
      console.log(changeArea);
    }
  }

}