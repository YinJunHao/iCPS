// Do next time
function doubleConfirm(text, el) {
    if (confirm(text)) {
        el.submit();
    } else {
        el.preventDefault();
    }
}

function passwordConfirm(text, el) {
    var Text = prompt(text);
    if (prompt(Text) === "yes") {
        el.submit()
    } else {
        return false;
    }
}