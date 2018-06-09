(function() {

function insertTextAtCursor(elem, text) {
	var pos = elem.selectionStart;
	elem.value = elem.value.substring(0, pos)
	           + text
	           + elem.value.substring(pos);

	elem.selectionEnd = pos + text.length;
	elem.focus();
}

var content = document.querySelector("[name='content']");

content.onkeydown = function(ev) {
	if (ev.keyCode === 9) {
		ev.preventDefault();
		insertTextAtCursor(content, "    ");
	}
};

content.onkeyup = function(ev) {
	if (ev.keyCode !== 13) {
		return;
	}

	var nl = [0, 0];
	var scanned = 0;
	var buf = "";

	for (var i = content.selectionStart; i >= 0 && scanned < 2; i--) {
		if (content.value[i] == "\n") {
			nl[scanned] = i;
			scanned++;
		}
	}

	for (var i = nl[1] + 1; i < nl[0]; i++) {
		if (content.value[i] === ' ' || content.value[i] === '\t') {
			buf += content.value[i];
		}
		else {
			break;
		}
	}

	insertTextAtCursor(content, buf);
}

})();