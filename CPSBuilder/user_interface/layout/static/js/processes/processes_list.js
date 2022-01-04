/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for "processes_list.html"
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