/**
 * Program title: iCPS
 * Project title: CPS Builder
 * This script governs all the user interface for "edit_resource.html"
 * Written by Yin Jun Hao
 */

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

