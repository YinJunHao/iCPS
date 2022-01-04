/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for the "start" tab
 * Written by Yin Jun Hao
 */

/* adds the selected task to the job list */
function addTask() {
    var table = document.getElementById("table").getElementsByTagName('tbody')[0];
    var selectedTask = document.getElementById("avail-task");
    if (selectedTask.value != " ") {
        var row = table.insertRow(-1);
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        if (table.rows.length==1) {
            cell1.innerHTML = '1';
        } else {
            var num = parseInt(table.rows[table.rows.length-2].cells[0].innerHTML) + 1;
            cell1.innerHTML = num.toString();
        }
        cell2.innerHTML = selectedTask.options[selectedTask.selectedIndex].text;
        cell2.value = selectedTask.options[selectedTask.selectedIndex].value;
        cell3.innerHTML = "<button class='btn btn-outline-danger' onclick='deleteRow(this)'><i class='material-icons'>delete</i></button>";
    }
}

/* consolidates the tasks selected */
function jobList() {
    var table = document.getElementById("table").getElementsByTagName('tbody')[0];
    var i;
    var list= [];
    for (i=0; i< table.rows.length; i++) {
        list.push(table.rows[i].cells[1].value);
    }
    document.getElementById("continue").value = list;
}

/* delete the task selected */
function deleteRow(e) {
    var row = e.parentNode.parentNode.rowIndex;
    var table = document.getElementById("table")
    table.deleteRow(row);
    var i;
    for (i=row; i<table.rows.length; i++) {
        var newNum = parseInt(table.rows[i].cells[0].innerHTML) - 1;
        table.rows[i].cells[0].innerHTML = newNum.toString();
    }
}

/* show a preview of the task selected */
function displayDetails() {
    var selectedTask = document.getElementById("avail-task").value;
    var displayTask = document.getElementById(selectedTask);
    var details = document.getElementById("avail-task-details").firstElementChild;
    details.style.display = "none";
    if (selectedTask != " ") {
        displayTask.style.display = "block";
    }
}