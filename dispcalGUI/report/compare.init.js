if (jsapi.useragent.opera && jsapi.useragent.opera < 8) alert("Your version of Opera is too old. Please upgrade to Opera 8 or newer.");
else if (jsapi.useragent.msie && jsapi.useragent.mac) alert("Internet Explorer is not supported under Mac OS. Please use a different browser like Mozilla Firefox or Safari.");
		
var data_ref, data_in,
	fields_extract_indexes_i = [],
	fields_extract_indexes_r = [],
	fields_match = [];
		
window.onload = function() {
	if (document.all) {
		labels = document.getElementsByTagName('label');
		for (var i = 0; i < labels.length; i ++) {
			labels[i].onmouseup = function () {
				setTimeout(compare, 50);  // needed to trigger onchange for IE
			};
			document.getElementById(jsapi.dom.attribute(labels[i], 'for')).onchange = null;
			document.getElementById(jsapi.dom.attribute(labels[i], 'for')).onmouseup = function () {
				setTimeout(compare, 50);  // needed to trigger onchange for IE
			};
		};
	};
	analyze()
};