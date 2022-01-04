function changeUnderscore() {
  var area = document.getElementsByClassName("replace-underscore");
  for (var i=0; i< area.length; i++) {
    var text = area[i].innerHTML;
    var new_text = text.replace(/_/g, " ");
    area[i].innerHTML = new_text;
  }
}
window.onload = changeUnderscore();
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
    console.log(str[0]);
    console.log(str[1]);
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

window.onload = drawline();

function seeOptions(e) {
  e.children[0].style.display = 'none';
  e.children[1].style.display = 'block';
  e.children[2].style.display = 'block';
}

function closeOptions(e) {
  e.children[0].style.display = 'block';
  e.children[1].style.display = 'none';
  e.children[2].style.display = 'none';
}