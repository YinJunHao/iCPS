/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for "process.html"
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
    var div1 = document.getElementById(div1ID)
    var div2IDList = str[1].split("-");
    var div2ID = div2IDList[0] + "-tree-nav-" + div2IDList[1];
    var div2 = document.getElementById(div2ID)
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
// window.onload = drawline();