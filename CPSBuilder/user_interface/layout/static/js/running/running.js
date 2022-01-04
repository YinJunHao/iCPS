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