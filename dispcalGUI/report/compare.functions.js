var p;

// Array methods
p=Array.prototype;
p.indexof = function(v, ignore_case) {
	for (var i=0; i<this.length; i++) if (ignore_case?(this[i]+"").toUpperCase()==(v+"").toUpperCase():this[i]==v) return i;
	return -1
};
if (!p.indexOf) p.indexOf = p.indexof;

// Object methods
p=Object.prototype;
p.clone = function() {
	var o = new this.constructor();
	for (var i in this) {
		if (this[i] != null && (this[i].constructor == Array || this[i].constructor == Object)) o[i] = this[i].clone();
		else o[i] = this[i]
	};
	return o
};
p.toString=function(){
	var str = "{";
	for (var i in this) {
		if (this[i] != this.constructor.prototype[i]) {
			if (str.length > 1) str += ",";
			str += i + ":" + (typeof this[i] == "string" ? "\"" + this[i] + "\"" : this[i])
		}
	};
	return str += "}"
};

// Number methods
p=Number.prototype;
p.accuracy = function(ln) {
	var n = Math.pow(10, ln || 0);
	return Math.round(this * n) / n
};
p.fill=function(ipart, fpart) {
	var i, v=(fpart!=null?this.toFixed(fpart):this+"");
	if ((i = v.indexOf(".")) > -1) ipart+=v.substr(i).length;
	while (v.length<ipart) v=0+v;
	return v
};
p.lead=function(ln) {
	var v=this+"";
	while (v.length<ln+1) v=0+v;
	return v
};

// String methods
p=String.prototype;
p.repeat = function(n) {
	var str="";
	for (var i=0; i<n; i++) str+=this;
	return str
};

// dataset Constructor
function dataset(src) {
	this.header = [];
	this.data_format = [];
	this.data = [];
	this.decimal = ".";
	this.id = "RGB";
	var e = document.forms['F_data'].elements;
	this.display = e['FF_display'].value;
	this.instrument = e['FF_instrument'].value;
	this.profile = e['FF_profile'].value;
	this.testchart = e['FF_testchart'].value;
	this.datetime = e['FF_datetime'].value;
	this.id = basename(splitext(this.testchart)[0]).toUpperCase();
	if (src) {
		this.src = src;
		src=cr2lf(src);
		var _data_format_regexp = /(^|\s)BEGIN_DATA_FORMAT\s+(.*?)\s+END_DATA_FORMAT(?=\s|$)/i,
			_data_regexp1 = /(^|\s)BEGIN_DATA\s+/i,
			_data_regexp2 = /\sEND_DATA(?=\s|$)/i,
			_header_regexp1 = /(^|\s)BEGIN_(\w+)\s+([\s\S]*?)\s+END_\2(?=\s|$)/gi,
			_header_regexp2 = /(^|\s)BEGIN_(\w+)\s+([\s\S]*?)\s+END_\2(?=\s|$)/i,
			data_format = src.match(_data_format_regexp),
			i,v;
		if (data_format && data_format[2]) {
			this.data_format = toarray(data_format[2], 1);
			while ((data_begin = src.search(_data_regexp1))>-1 && (data_end = src.search(_data_regexp2))>data_begin) {
				if (!this.data.length) { // 1st
					var header = lf2cr(src).substr(0, data_begin).replace(_data_format_regexp, "");
					if (v = header.match(_header_regexp1)) for (i=0; i<v.length; i++) {
						header = header.replace(_header_regexp2, "\r" + (v[i].replace(_header_regexp2, "$2 $3").replace(/\r/g, "\n")))
					};
					header=trim(header).split(/\r/);
					for (i=0; i<header.length; i++) {
						header[i] = trim(header[i]).replace(/\s+/, "\r").split("\r");
						this.header_set_field(header[i][0], header[i][1], "append")
					}
				};
				this.data = this.data.concat(toarray(src.substring(data_begin, data_end).replace(_data_regexp1, "").replace(_data_regexp2, "")));
				src = src.substr(data_end+9)
			}
		};
	};
	if (comparison_criteria[this.id]) {
		this.id = comparison_criteria[this.id].id;
	}
	else {
		if (this.data_format.indexOf('CMYK_C') > -1 && this.data_format.indexOf('CMYK_M') > -1 && this.data_format.indexOf('CMYK_Y') > -1 && this.data_format.indexOf('CMYK_K') > -1)
			this.id = 'CMYK';
		else
			this.id = 'RGB';
	};
	return src ? true : false
};

p=dataset.prototype;
p.header_get = function() {
	var header=[], i, j, v;
	for (i=0; i<this.header.length; i++) {
		if (this.header[i][1] && this.header[i][1].indexOf("\n")>-1) {
			header.push(["BEGIN_"+this.header[i][0]]);
			v=this.header[i][1].split("\n");
			for (j=0; j<v.length; j++) header.push([v[j]]);
			header.push(["END_"+this.header[i][0]])
		}
		else header.push(this.header[i])
	};
	return fromarray(header)
};
p.header_set = function(header, mode) {
	for (var i=0; i<header.length; i++) {
		this.header_set_field(header[i][0], header[i][1], mode)
	}
};
p.header_set_date = function(mode) {
	var now=new Date();
	this.header_set_field("CREATED", "\"" + (now.getMonth()+1) + "/" + now.getDate() + "/" + now.getFullYear() + "\" # Time: " + now.getHours().fill(2) + ":" + now.getMinutes().fill(2), mode)
};
p.header_set_defaults = function(mode) {
	this.header_set_date(mode);
};
p.header_set_field = function(name, value, mode) {
	if (!name) return false;
	if (value != null) value += "";
	if (name.toUpperCase() == "NUMBER_OF_FIELDS" || name.toUpperCase() == "NUMBER_OF_SETS") return false;
	if (!this.header[name.toUpperCase()] || mode=="append" || name.toUpperCase() == "KEYWORD") {
		var header=[name];
		if(value!=null && value!=="") header.push(value);
		this.header.push(header);
		if (!this.header[name.toUpperCase()]) this.header[name.toUpperCase()]=[];
		this.header[name.toUpperCase()].push(this.header[this.header.length-1])
	}
	else if (mode=="overwrite") {
		for (var i=0; i<this.header[name.toUpperCase()].length; i++) {
			if (value==null || value==="") this.header[name.toUpperCase()][i].splice(1, 1);
			else this.header[name.toUpperCase()][i][1] = value
		}
	}
};
p.toString = function() {
	return (this.header.length?this.header_get()+"\n":"") + "NUMBER_OF_FIELDS\t" + this.data_format.length + "\nBEGIN_DATA_FORMAT\n" + fromarray(this.data_format, 1) + "\nEND_DATA_FORMAT\nNUMBER_OF_SETS\t" + this.data.length + "\nBEGIN_DATA\n" + decimal(fromarray(this.data), this.decimal == "." ? "\\," : "\\." , this.decimal) + "\nEND_DATA"
};
p.generate_report = function() {
	var f = document.forms,
		e = f['F_data'].elements,
		criteria = comparison_criteria[f['F_out'].elements['FF_criteria'].value],
		fields_match = window.fields_match, // criteria.fields_match,
		fields_extract_i = fields_match.slice().concat(criteria.fields_compare),
		rules = criteria.rules,
		result = [],
		delta,
		matched,
		target,
		target_rgb,
		actual,
		actual_rgb,
		actual_rgb_html,
		ct = 5000,
		dupes,
		dupescount = 0,
		n = 0,
		o = fields_match.length - 1, // offset for CIE values
		devlen = fields_match.length > 4 ? 2 : o, // length for device values, if RGB + CMYK, just use RGB
		missing_data,
		delta_calc_method = f['F_out'].elements['FF_delta_calc_method'].value,
		patch_number_html,
		target_rgb_html,
		warn_deviation = criteria.warn_deviation,
		no_Lab = (this.data_format.indexof("LAB_L", true) < 0
				|| this.data_format.indexof("LAB_A", true) < 0
				|| this.data_format.indexof("LAB_B", true) < 0),
		no_XYZ = (this.data_format.indexof("XYZ_X", true) < 0
				|| this.data_format.indexof("XYZ_Y", true) < 0
				|| this.data_format.indexof("XYZ_Z", true) < 0);
	
	this.report_html = [
		'	<h2>Profile Verification Report</h2>',
		'	<table class="info">',
		'		<tr>',
		'			<th>Device:</th>',
		'			<td>' + this.display + '</td>',
		'		</tr>',
		'		<tr>',
		'			<th>Instrument:</th>',
		'			<td>' + this.instrument + '</td>',
		'		</tr>',
		'		<tr>',
		'			<th>Profile:</th>',
		'			<td>' + this.profile + '</td>',
		'		</tr>',
		'		<tr>',
		'			<th>Testchart:</th>',
		'			<td>' + this.testchart + '</td>',
		'		</tr>',
		'		<tr>',
		'			<th>Evaluation criteria:</th>',
		'			<td>' + criteria.name + '</td>',
		'		</tr>',
		'		<tr>',
		'			<th>Date:</th>',
		'			<td>' + this.datetime + '</td>',
		'		</tr>',
		'	</table>'
	];
	var result_start = this.report_html.length;
	this.report_html = this.report_html.concat([
		'	<div class="summary">',
		'	<h3>Summary</h3>',
		'	<table>',
		'		<tr>',
		'			<th class="first-row">Criteria</th><th>Nominal</th><th>Recommended</th><th>#</th><th colspan="2">&#160;</th><th>Actual</th><th>&#160;</th><th>Result</th>',
		'		</tr>'
	]);
	for (var j=0; j<rules.length; j++) {
		this.report_html.push('		<tr>');
		this.report_html.push('			<td class="first-row' + (!rules[j][3] ? ' statonly' : '' ) + '">' + rules[j][0] + '</td><td>' + (rules[j][3] ? '&lt;= ' + rules[j][3] : '') + '</td><td>' + (rules[j][4] ? '&lt;= ' + rules[j][4] : '') + '</td><td class="patch">');
		result[j] = {
			E: [],
			L: [],
			C: [],
			H: [],
			matches: [],
			sum: null
		};
		patch_number_html = [];
		actual_rgb_html = [];
		target_rgb_html = [];
		if (rules[j][2].indexOf("_MAX") < 0) {
			for (var k=0; k<rules[j][1].length; k++) {
				patch_number_html.push('<div class="patch">&#160;</div>');
				if (rules[j][1][k].length == 4) // Assume CMYK
					target_rgb = jsapi.math.color.cmyk2rgb(rules[j][1][k][0] / 100, rules[j][1][k][1] / 100, rules[j][1][k][2] / 100, rules[j][1][k][3] / 100);
				else 
					target_rgb = [rules[j][1][k][0] * 2.55, rules[j][1][k][1] * 2.55, rules[j][1][k][2] * 2.55];
				target_rgb_html.push('<div class="patch" style="background-color: rgb(' + Math.round(target_rgb[0]) + ', ' + Math.round(target_rgb[1]) + ', ' + Math.round(target_rgb[2]) + ');">&#160;</div>');
				actual_rgb_html.push('<div class="patch" style="color: red; position: relative;"><span style="position: absolute;">\u2716</span>&#160;</div>');
			}
		};
		for (var i=0, n=0; i<this.data.length; i++) {
			dupes = this.data[i][fields_extract_indexes_i[o + 3] + 1];
			if (dupescount == dupes) {
				n++;
				target = this.data[i-dupes];
				actual = this.data[i];
				matched = false;
				if (rules[j][1].length) {
					for (var k=0; k<rules[j][1].length; k++) {
						var current = this.data[i].slice(fields_extract_indexes_i[0], fields_extract_indexes_i[o] + 1);
						if (fields_match.join(',').indexOf('RGB') == 0) 
							var current_rgb = current.slice(0, 3),
								current_cmyk = current.slice(3);
						else 
							var current_rgb = current.slice(4),
								current_cmyk = current.slice(0, 4);
						if ((rules[j][1][k].length == 3 && current_rgb.join(',') == rules[j][1][k].join(',')) || (rules[j][1][k].length == 4 && current_cmyk.join(',') == rules[j][1][k].join(','))) {
							if (rules[j][2].indexOf("_MAX") < 0) {
								if (rules[j][1].length || rules[j][2].indexOf('_MAX') > -1) patch_number_html[k] = ('<div class="patch">' + n.fill(String(number_of_sets).length) + '</div>');
								if (no_Lab && !no_XYZ) {
									target_rgb = jsapi.math.color.XYZ2rgb(target[fields_extract_indexes_i[o + 1]], target[fields_extract_indexes_i[o + 2]], target[fields_extract_indexes_i[o + 3]]);
									actual_rgb = jsapi.math.color.XYZ2rgb(actual[fields_extract_indexes_i[o + 1]], actual[fields_extract_indexes_i[o + 2]], actual[fields_extract_indexes_i[o + 3]]);
								}
								else {
									target_rgb = jsapi.math.color.Lab2rgb(target[fields_extract_indexes_i[o + 1]], target[fields_extract_indexes_i[o + 2]], target[fields_extract_indexes_i[o + 3]], ct);
									actual_rgb = jsapi.math.color.Lab2rgb(actual[fields_extract_indexes_i[o + 1]], actual[fields_extract_indexes_i[o + 2]], actual[fields_extract_indexes_i[o + 3]], ct);
								}
								target_rgb_html[k] = ('<div class="patch" style="background-color: rgb(' + target_rgb[0] + ', ' + target_rgb[1] + ', ' + target_rgb[2] + ');">&#160;</div>');
								actual_rgb_html[k] = ('<div class="patch" style="background-color: rgb(' + actual_rgb[0] + ', ' + actual_rgb[1] + ', ' + actual_rgb[2] + ');">&#160;</div>');
							};
							matched = true
						}
					}
				}
				else matched = true;
				if (matched) {
					target_Lab = [target[fields_extract_indexes_i[o + 1]], target[fields_extract_indexes_i[o + 2]], target[fields_extract_indexes_i[o + 3]]];
					actual_Lab = [actual[fields_extract_indexes_i[o + 1]], actual[fields_extract_indexes_i[o + 2]], actual[fields_extract_indexes_i[o + 3]]];
					if (no_Lab && !no_XYZ) {
						target_Lab = jsapi.math.color.XYZ2Lab(target_Lab[0], target_Lab[1], target_Lab[2]);
						actual_Lab = jsapi.math.color.XYZ2Lab(actual_Lab[0], actual_Lab[1], actual_Lab[2]);
					}
					delta = jsapi.math.color.delta(target_Lab[0], target_Lab[1], target_Lab[2], actual_Lab[0], actual_Lab[1], actual_Lab[2], rules[j][5]);
					result[j].E.push(delta.E);
					result[j].L.push(delta.L);
					result[j].C.push(delta.C);
					result[j].H.push(delta.H);
					if (rules[j][1].length || rules[j][2].indexOf('_MAX') > -1) result[j].matches.push([i-dupes, i, n])
				};
				dupescount = 0;
			}
			else dupescount++;
		};
		this.report_html = this.report_html.concat(patch_number_html);
		var number_of_sets = n;
		if (!rules[j][1].length || result[j].matches.length >= rules[j][1].length) switch (rules[j][2]) {
			case DELTA_E_MAX:
				result[j].sum = jsapi.math.absmax(result[j].E);
				break;
			case DELTA_E_AVG:
				result[j].sum = jsapi.math.avg(result[j].E);
				break;
			case DELTA_E_MED:
				result[j].sum = jsapi.math.median(result[j].E);
				break;
			case DELTA_E_MAD:
				result[j].sum = jsapi.math.mad(result[j].E);
				break;
			case DELTA_E_STDDEV:
				result[j].sum = jsapi.math.stddev(result[j].E);
				break;
				
			case DELTA_L_MAX:
				result[j].sum = jsapi.math.absmax(result[j].L);
				break;
			case DELTA_L_AVG:
				result[j].sum = jsapi.math.avg(result[j].L);
				break;
			case DELTA_L_MED:
				result[j].sum = jsapi.math.median(result[j].L);
				break;
			case DELTA_L_MAD:
				result[j].sum = jsapi.math.mad(result[j].L);
				break;
			case DELTA_L_STDDEV:
				result[j].sum = jsapi.math.stddev(result[j].L);
				break;
				
			case DELTA_C_MAX:
				result[j].sum = jsapi.math.absmax(result[j].C);
				break;
			case DELTA_C_AVG:
				result[j].sum = jsapi.math.avg(result[j].C);
				break;
			case DELTA_C_MED:
				result[j].sum = jsapi.math.median(result[j].C);
				break;
			case DELTA_C_MAD:
				result[j].sum = jsapi.math.mad(result[j].C);
				break;
			case DELTA_C_STDDEV:
				result[j].sum = jsapi.math.stddev(result[j].C);
				break;
				
			case DELTA_H_MAX:
				result[j].sum = jsapi.math.absmax(result[j].H);
				break;
			case DELTA_H_AVG:
				result[j].sum = jsapi.math.avg(result[j].H);
				break;
			case DELTA_H_MED:
				result[j].sum = jsapi.math.median(result[j].H);
				break;
			case DELTA_H_MAD:
				result[j].sum = jsapi.math.mad(result[j].H);
				break;
			case DELTA_H_STDDEV:
				result[j].sum = jsapi.math.stddev(result[j].H);
				break;
		};
		if (result[j].matches.length) {
			matched = false;
			for (var k=0; k<result[j].matches.length; k++) {
				target = this.data[result[j].matches[k][0]];
				actual = this.data[result[j].matches[k][1]];
				switch (rules[j][2]) {
					case DELTA_E_MAX:
						if (result[j].E[k] == result[j].sum) matched = true;
						break;
					case DELTA_L_MAX:
						if (result[j].L[k] == result[j].sum) matched = true;
						break;
					case DELTA_C_MAX:
						if (result[j].C[k] == result[j].sum) matched = true;
						break;
					case DELTA_H_MAX:
						if (result[j].H[k] == result[j].sum) matched = true;
						break;
				};
				if (matched) {
					result[j].finalmatch = result[j].matches[k];
					break;
				};
			};
			if (matched) {
				this.report_html.push('<div class="patch">' + result[j].finalmatch[2].fill(String(number_of_sets).length) + '</div>');
				if (no_Lab && !no_XYZ) {
					target_rgb = jsapi.math.color.XYZ2rgb(target[fields_extract_indexes_i[o + 1]], target[fields_extract_indexes_i[o + 2]], target[fields_extract_indexes_i[o + 3]]);
					actual_rgb = jsapi.math.color.XYZ2rgb(actual[fields_extract_indexes_i[o + 1]], actual[fields_extract_indexes_i[o + 2]], actual[fields_extract_indexes_i[o + 3]]);
				}
				else {
					target_rgb = jsapi.math.color.Lab2rgb(target[fields_extract_indexes_i[o + 1]], target[fields_extract_indexes_i[o + 2]], target[fields_extract_indexes_i[o + 3]], ct);
					actual_rgb = jsapi.math.color.Lab2rgb(actual[fields_extract_indexes_i[o + 1]], actual[fields_extract_indexes_i[o + 2]], actual[fields_extract_indexes_i[o + 3]], ct);
				}
				target_rgb_html.push('<div class="patch" style="background-color: rgb(' + target_rgb[0] + ', ' + target_rgb[1] + ', ' + target_rgb[2] + ');">&#160;</div>');
				actual_rgb_html.push('<div class="patch" style="background-color: rgb(' + actual_rgb[0] + ', ' + actual_rgb[1] + ', ' + actual_rgb[2] + ');">&#160;</div>');
			};
		}
		else if (!target_rgb_html.length) {
			target_rgb_html.push('<div class="patch">&#160;</div>');
			actual_rgb_html.push('<div class="patch">&#160;</div>');
		};
		this.report_html.push('			</td>');
		this.report_html.push('			<td class="patch">' + target_rgb_html.join('') + '</td>');
		this.report_html.push('			<td class="patch">' + actual_rgb_html.join('') + '</td>');
		var bar_html = [];
		if (result[j].sum != null) {
			if (!rules[j][3]) rgb = [204, 204, 204];
			else {
				var rgb = [0, 255, 0],
					step = 255 / (rules[j][3] + rules[j][3] / 2);
				if (Math.abs(result[j].sum) < rules[j][3]) {
					rgb[0] += Math.min(step * Math.abs(result[j].sum), 255);
					rgb[1] -= Math.min(step * Math.abs(result[j].sum), 255);
					var maxrg = Math.max(rgb[0], rgb[1]);
					rgb[0] *= (255 / maxrg);
					rgb[1] *= (255 / maxrg);
					rgb[0] = Math.round(rgb[0]);
					rgb[1] = Math.round(rgb[1]);
				}
				else rgb = [255, 0, 0];
			};
			for (var l = 0; l < actual_rgb_html.length; l ++) {
				bar_html.push('<span style="display: block; width: ' + (10 * Math.abs(result[j].sum).accuracy(2)) + 'px; background-color: rgb(' + rgb.join(', ') + '); border: 1px solid silver; border-top: none; border-bottom: none; padding: .125em .25em .125em 0;">&#160;</span>');
			};
		};
		if (!missing_data) missing_data = result[j].sum == null;
		this.report_html.push('			<td><span class="' + (result[j].sum != null && rules[j][3] ? (Math.abs(result[j].sum).accuracy(2) < rules[j][3] ? 'ok' : (Math.abs(result[j].sum).accuracy(2) == rules[j][3] ? 'warn' : 'ko')) : 'statonly') + '">' + (result[j].sum != null ? result[j].sum.accuracy(2) : '') + '</span></td><td style="padding: 0;">' + bar_html.join('') + '</td><td class="' + (result[j].sum != null && (!rules[j][3] || Math.abs(result[j].sum) <= rules[j][3]) ? ((Math.abs(result[j].sum).accuracy(2) < rules[j][3] ? 'ok">OK <span class="checkmark">✔</span>' : (result[j].sum != null && rules[j][3] ? 'warn">OK \u26a0' : 'na">')) + '<span class="' + (rules[j][4] && Math.abs(result[j].sum) <= rules[j][4] ? 'checkmark' : 'hidden') + (rules[j][4] ? '">✔' : '">')) : 'ko">' + (result[j].sum != null ? 'NOT OK' : '') + ' <span class="checkmark">\u2716') + '</span></td>');
		this.report_html.push('		</tr>');
	};
	this.report_html.push('	</table>');
	
	var pass, overachieve;
	for (var j=0; j<result.length; j++) {
		if (!rules[j][3] && !rules[j][4]) continue;
		if (missing_data || isNaN(result[j].sum) || Math.abs(result[j].sum) > rules[j][3]) pass = false;
		if (missing_data || isNaN(result[j].sum) || Math.abs(result[j].sum) > rules[j][4]) overachieve = false;
		if (rules[j][5] == delta_calc_method) for (var k=0; k<result[j].matches.length; k++) {
			if (rules[j][2].indexOf('_E_') > -1) {
				this.data[result[j].matches[k][1]].actual_DE = Math.abs(rules[j][2].indexOf('_MAX') < 0 ? result[j].sum : result[j].E[k]);
				this.data[result[j].matches[k][1]].tolerance_DE = rules[j][3];
			}
			else if (rules[j][2].indexOf('_L_') > -1) {
				this.data[result[j].matches[k][1]].actual_DL = Math.abs(rules[j][2].indexOf('_MAX') < 0 ? result[j].sum : result[j].L[k]);
				this.data[result[j].matches[k][1]].tolerance_DL = rules[j][3];
			}
			else if (rules[j][2].indexOf('_C_') > -1) {
				this.data[result[j].matches[k][1]].actual_DC = Math.abs(rules[j][2].indexOf('_MAX') < 0 ? result[j].sum : result[j].C[k]);
				this.data[result[j].matches[k][1]].tolerance_DC = rules[j][3];
			}
			else if (rules[j][2].indexOf('_H_') > -1) {
				this.data[result[j].matches[k][1]].actual_DH = Math.abs(rules[j][2].indexOf('_MAX') < 0 ? result[j].sum : result[j].H[k]);
				this.data[result[j].matches[k][1]].tolerance_DH = rules[j][3];
			}
		};
	};
	this.report_html.push('<div class="footer"><p><span class="' + (pass !== false ? 'ok"><span class="checkmark">✔</span> ' + criteria.passtext : 'ko"><span class="checkmark">\u2716</span> ' + (missing_data ? 'MISSING DATA' : criteria.failtext)) + '</span>' + ((overachieve !== false && criteria.passrecommendedtext) || (overachieve === false && criteria.failrecommendedtext) ? '<br /><span class="' + (overachieve !== false ? 'ok"><span class="checkmark">✔</span> ' + criteria.passrecommendedtext : 'info"><span class="checkmark">✘</span> ' + criteria.failrecommendedtext) + '</span>' : '') + '</p>');
	
	this.result_html = this.report_html.slice(result_start);
	this.report_html.push('	</div>');
	
	this.report_html.push('	<div class="overview">');
	this.report_html.push('	<h3>Overview</h3>');
	this.report_html.push('	<table>');
	this.report_html.push('		<tr>');
	this.report_html.push('			<th>#</th><th colspan="' + fields_match.slice(0, devlen + 1).length + '">Device Values</th><th colspan="3">Nominal Values</th><th colspan="2">&#160;</th><th colspan="3">Measured Values</th><th colspan="4">ΔE*' + delta_calc_method.substr(3) + '</th><th>&#160;</th>');
	this.report_html.push('		</tr>');
	this.report_html.push('		<tr>');
	this.report_html.push('			<th>&#160;</th><th>' + fields_match.slice(0, devlen + 1).join('</th><th>').replace(/\w+?_/g, '') + '</th><th>' + 'L*,a*,b*'.split(',').join('</th><th>') + '</th><th>&#160;</th><th>&#160;</th><th>' + 'L*,a*,b*'.split(',').join('</th><th>') + '</th><th>ΔL*</th><th>ΔC*</th><th>ΔH*</th><th>ΔE*</th><th>&#160;</th>');
	this.report_html.push('		</tr>');
	dupescount = 0;
	for (var i=0, n=0; i<this.data.length; i++) {
		dupes = this.data[i][fields_extract_indexes_i[o + 3] + 1];
		if (dupescount == dupes) {
			n++;
			target = this.data[i-dupes];
			actual = this.data[i];
			target_Lab = [target[fields_extract_indexes_i[o + 1]], target[fields_extract_indexes_i[o + 2]], target[fields_extract_indexes_i[o + 3]]];
			actual_Lab = [actual[fields_extract_indexes_i[o + 1]], actual[fields_extract_indexes_i[o + 2]], actual[fields_extract_indexes_i[o + 3]]];
			if (no_Lab && !no_XYZ) {
				target_Lab = jsapi.math.color.XYZ2Lab(target_Lab[0], target_Lab[1], target_Lab[2]);
				actual_Lab = jsapi.math.color.XYZ2Lab(actual_Lab[0], actual_Lab[1], actual_Lab[2]);
				target_rgb = jsapi.math.color.XYZ2rgb(target[fields_extract_indexes_i[o + 1]], target[fields_extract_indexes_i[o + 2]], target[fields_extract_indexes_i[o + 3]]);
				actual_rgb = jsapi.math.color.XYZ2rgb(actual[fields_extract_indexes_i[o + 1]], actual[fields_extract_indexes_i[o + 2]], actual[fields_extract_indexes_i[o + 3]]);
			}
			else {
				target_rgb = jsapi.math.color.Lab2rgb(target[fields_extract_indexes_i[o + 1]], target[fields_extract_indexes_i[o + 2]], target[fields_extract_indexes_i[o + 3]], ct);
				actual_rgb = jsapi.math.color.Lab2rgb(actual[fields_extract_indexes_i[o + 1]], actual[fields_extract_indexes_i[o + 2]], actual[fields_extract_indexes_i[o + 3]], ct);
			}
			delta = jsapi.math.color.delta(target_Lab[0], target_Lab[1], target_Lab[2], actual_Lab[0], actual_Lab[1], actual_Lab[2], delta_calc_method);
			this.report_html.push('		<tr>');
			var bar_html = [],
				rgb = [0, 255, 0];
			if (actual.tolerance_DE == null)
				actual.tolerance_DE = 5;
			if (actual.actual_DE == null)
				actual.actual_DE = delta.E;
			var step = 255 / (actual.tolerance_DE + actual.tolerance_DE / 2);
			if (actual.actual_DE < actual.tolerance_DE) {
				rgb[0] += Math.min(step * actual.actual_DE, 255);
				rgb[1] -= Math.min(step * actual.actual_DE, 255);
				var maxrg = Math.max(rgb[0], rgb[1]);
				rgb[0] *= (255 / maxrg);
				rgb[1] *= (255 / maxrg);
				rgb[0] = Math.round(rgb[0]);
				rgb[1] = Math.round(rgb[1]);
			}
			else rgb = [255, 0, 0];
			bar_html.push('<span style="display: block; width: ' + (10 * actual.actual_DE.accuracy(2)) + 'px; background-color: rgb(' + rgb.join(', ') + '); border: 1px solid silver; border-top: none; border-bottom: none; padding: .125em .25em .125em 0;">&#160;</span>');
			var device = target.slice(fields_extract_indexes_i[0], fields_extract_indexes_i[devlen] + 1);
			for (var j=0; j<device.length; j++) device[j] = device[j].accuracy(2);
			this.report_html.push('			<td>' + n.fill(String(number_of_sets).length) + '</td><td>' + device.join('</td><td>') + '</td><td>' + target_Lab[0].accuracy(2) + '</td><td>' + target_Lab[1].accuracy(2) + '</td><td>' + target_Lab[2].accuracy(2) + '</td><td class="patch"><div class="patch" style="background-color: rgb(' + target_rgb[0] + ', ' + target_rgb[1] + ', ' + target_rgb[2] + ');">&#160;</div></td><td class="patch"><div class="patch" style="background-color: rgb(' + actual_rgb[0] + ', ' + actual_rgb[1] + ', ' + actual_rgb[2] + ');">&#160;</div></td><td>' + actual_Lab[0].accuracy(2) + '</td><td>' + actual_Lab[1].accuracy(2) + '</td><td>' + actual_Lab[2].accuracy(2) + '</td><td class="' + (actual.actual_DL != null ? (actual.actual_DL.accuracy(2) < actual.tolerance_DL ? 'ok' : (actual.actual_DL.accuracy(2) == actual.tolerance_DL ? 'warn' : 'ko')) : 'info') + '">' + delta.L.accuracy(2) + '</td><td class="' + (actual.actual_DC != null ? (actual.actual_DC.accuracy(2) < actual.tolerance_DC ? 'ok' : (actual.actual_DC.accuracy(2) == actual.tolerance_DC ? 'warn' : 'ko')) : 'info') + '">' + delta.C.accuracy(2) + '</td><td class="' + (actual.actual_DH != null ? (actual.actual_DH.accuracy(2) < actual.tolerance_DH ? 'ok' : (actual.actual_DH.accuracy(2) == actual.tolerance_DH ? 'warn' : 'ko')) : 'info') + '">' + delta.H.accuracy(2) + '</td><td class="' + (actual.actual_DE != null ? (actual.actual_DE.accuracy(2) < actual.tolerance_DE ? 'ok' : (actual.actual_DE.accuracy(2) == actual.tolerance_DE ? 'warn' : 'ko')) : (delta.E < warn_deviation ? 'info' : 'warn')) + '">' + delta.E.accuracy(2) + '</td><td style="padding: 0;">' + bar_html.join('') + '</td>');
			this.report_html.push('		</tr>');
			dupescount = 0;
		}
		else dupescount++;
	};
	this.report_html.push('	</table>');
	this.report_html.push('	</div>');
	
	return [this.result_html.join('\n'), this.report_html.join('\n'), criteria]
};

function trim(txt) {
	return txt.replace(/^\s+|\s+$/g, "")
};

function lf2cr(txt) {
	return txt.replace(/\r\n/g, "\r").replace(/\n/g, "\r")
};

function cr2lf(txt) {
	// CR LF = Windows
	// CR = Mac OS 9
	// LF = Unix/Linux/Mac OS X
	return txt.replace(/\r\n/g, "\n").replace(/\r/g, "\n")
};

function compact(txt, collapse_whitespace) {
	txt = trim(txt).replace(/\n\s+|\s+\n/g, "\n");
	return collapse_whitespace?txt.replace(/\s+/g, " "):txt
};

function comma2point(txt) {
	return decimal(txt)
};

function decimal(txt, sr, re) {
	if (!sr) sr = "\\,";
	if (!re) re = ".";
	return txt.replace(new RegExp("((^|\\s)\\-?\\d+)"+sr+"(\\d+(?=\\s|$))", "g"), "$1"+re+"$3")
};

function is_decimal(str) {
	str+="";
	if (str.search(/^[\+\-]/)>-1) str=str.substr(1);
	return str.search(/[^\d\.]/)<0
};

function toarray(txt, level) {
	txt=comma2point(compact(cr2lf(txt)));
	if (!txt) return [];
	if (level) {
		txt=txt.split(/\s/)
	}
	else {
		txt=txt.split("\n");
		for (var i=0; i<txt.length; i++) {
			txt[i]=txt[i].split(/\s+/);
			for (var j=0; j<txt[i].length; j++) if (is_decimal(txt[i][j])) {
				txt[i][j]=parseFloat(txt[i][j])
			}
		}
	};
	return txt
};

function fromarray(array, level) {
	array = array.clone();
	if (level) return array.join("\t");
	for (var i=0; i<array.length; i++) array[i]=array[i].join("\t");
	return array.join("\n")
};

function analyze(which) {
	var f=document.forms,
		fields_extract_selected=[],
		fields_header_selected=[],
		e=f['F_out'].elements,fv,i,v,s;
	
	if (!trim(f["F_data"].elements["FF_data_in"].value) || !trim(f["F_data"].elements["FF_data_ref"].value)) return;
	
	if (!get_data(which)) {
		if (which == "r" || !which) {
			if (trim(f['F_data'].elements['FF_data_ref'].value)) {
				if (!data_ref.data_format.length) set_status("Reference data: No or invalid data format.");
				else if (!data_ref.data.length) set_status("Reference data: No or invalid values.")
			};
		};
		if (which == "i" || !which) {
			if (trim(f['F_data'].elements['FF_data_in'].value)) {
				if (!data_in.data_format.length) set_status("Measurement data: No or invalid data format.");
				else if (!data_in.data.length) set_status("Measurement data: No or invalid values.")
			};
		}
	};
	
	var _criteria = [], fields_match = [];
	for (var id in comparison_criteria) {
		if (comparison_criteria[id] && comparison_criteria[id].name && _criteria.indexOf(comparison_criteria[id]) < 0) {
			for (var i=0; i<comparison_criteria[id].fields_match.length; i++) {
				if (data_ref.data_format.indexOf(comparison_criteria[id].fields_match[i]) < 0) 
					break;
				else if (fields_match.indexOf(comparison_criteria[id].fields_match[i]) < 0)
					fields_match.push(comparison_criteria[id].fields_match[i]);
			};
			if (i == comparison_criteria[id].fields_match.length) {
				_criteria.push(comparison_criteria[id])
			}
		}
	};
	window.fields_match = fields_match;
	for (var i=0; i<_criteria.length; i++) {
		e['FF_criteria'].options[i] = new Option(_criteria[i].name, _criteria[i].id, data_ref.id == _criteria[i].id, data_ref.id == _criteria[i].id)
	};
	
	var criteria = comparison_criteria[e['FF_criteria'].value],
		fields_extract_i = fields_match.slice().concat(criteria.fields_compare);
	
	for (i=0; i<data_ref.header.length; i++) {
		v=compact(fromarray(data_ref.header[i], 1), true).replace(/\n/g, " ");
		if (!fields_header[v]) {
			fields_header.push(fields_header[v]=data_ref.header[i]);
		}
	};
	for (i=0; i<data_in.header.length; i++) {
		v=compact(fromarray(data_in.header[i], 1), true).replace(/\n/g, " ");
		if (!fields_header[v]) {
			fields_header.push(fields_header[v]=data_in.header[i]);
		}
	};
	
	if (data_in.data.length && data_ref.data.length) {
		duplicates = 'first';
		var _data_in = extract();
		data_in = data_ref;
		data_ref = extract();
		data_in = _data_in;
		if (data_in.data.length != data_ref.data.length) {
			alert("Different amount of sets in measurements and reference data.");
			return false
		};
	};
	var data_in_format_missing_fields = [], data_ref_format_missing_fields = [], errortxt = "";
	for (i = 0; i < fields_extract_i.length; i ++) {
		if (data_in.data_format.indexof(fields_extract_i[i]) < 0) data_in_format_missing_fields.push(fields_extract_i[i]);
		if (data_ref.data_format.indexof(fields_extract_i[i]) < 0) data_ref_format_missing_fields.push(fields_extract_i[i]);
	};
	if (data_in_format_missing_fields.length) {
		errortxt += "Measurement data is missing the following fields: " + data_in_format_missing_fields.join(", ") + ".\n"
	}
	if (data_ref_format_missing_fields.length) {
		errortxt += "Reference data is missing the following fields: " + data_ref_format_missing_fields.join(", ") + ".\n"
	};
	if (errortxt) {
		alert(errortxt + "Measurements and reference data must contain atleast: " + fields_extract_i.join(", "));
		return
	};
	data_in.data = data_ref.data.concat(data_in.data);
	
	if (data_ref.data_format.length && data_ref.data.length && data_in.data_format.length && data_in.data.length) {
		compare();
	};
};

function get_data(which) {
	var f=document.forms;
	
	if (which == "r" || !which) {
		data_ref=new dataset(f["F_data"].elements["FF_data_ref"].value)
	};
	if (which == "i" || !which) {
		data_in=new dataset(f["F_data"].elements["FF_data_in"].value)
	};
	
	if (which == "r" || !which) {
		if (!data_ref.data_format.length) return false;
		if (!data_ref.data.length) return false
	};
	if (which == "i" || !which) {
		if (!data_in.data_format.length) return false;
		if (!data_in.data.length) return false
	};
	
	return true
};

function compare() {
	form_elements_set_disabled(null, true);
	duplicates = 'list';
	window.data_out = extract();
	var fe = document.forms["F_out"].elements, fe2 = document.forms["F_data"].elements;
	if (fe2["FF_variables"]) try {
		eval(fe2["FF_variables"].value);
		window.comparison_criteria = comparison_criteria;
		if (window.location.href.indexOf("?debug")>-1) alert("Comparsion criteria: " + (comparison_criteria.toSource ? comparison_criteria.toSource() : comparison_criteria))
	}
	catch (e) {
		alert("Error parsing variable:\n" + e + "\nUsing default values.")
	};
	var report = data_out.generate_report();
	document.getElementById('result').innerHTML = report[1];
	document.getElementById('report').style.display = "block";
	form_elements_set_disabled(null, false);
	return true
};

function extract() {
	
	set_status("Extracting... 0%");
	
	var f=document.forms,
		e=f['F_out'].elements,
		data_out = [],
		debug = false,
		decimal_comma = false,
		duplicates_count = true,
		indexfield,
		fields_extract_r = [],
		fields_extract_indexes_r = [],
		fields_match_indexes_i = [],
		fields_match_indexes_r = [],
		t1 = new Date().getTime(),
		t2,
		i,j,k,m,v,tmp;
	
	var criteria = comparison_criteria[e['FF_criteria'].value],
		fields_match = window.fields_match,
		fields_extract_i = fields_match.slice().concat(criteria.fields_compare);
	
	fields_extract_indexes_i = [];
	
	var _data_out = new dataset();
	
	for (i=0; i<fields_extract_i.length; i++) {
		for (j=0; j<data_in.data_format.length; j++) {
			if (data_in.data_format[j]==fields_extract_i[i]) {
				fields_extract_indexes_i.push(j);
				break
			}
		}
	};
	for (i=0; i<fields_extract_r.length; i++) {
		for (j=0; j<data_ref.data_format.length; j++) {
			if (data_ref.data_format[j]==fields_extract_r[i]) {
				fields_extract_indexes_r.push(j);
				break
			}
		}
	};
	
	for (i=0; i<fields_match.length; i++) {
		for (j=0; j<data_in.data_format.length; j++) {
			if (data_in.data_format[j].toUpperCase()==fields_match[i].toUpperCase()) {
				fields_match_indexes_i.push(j);
				break
			}
		}
	};
	for (i=0; i<fields_match.length; i++) {
		for (j=0; j<data_ref.data_format.length; j++) {
			if (data_ref.data_format[j].toUpperCase()==fields_match[i].toUpperCase()) {
				fields_match_indexes_r.push(j);
				break
			}
		}
	};
	
	for (i=0; i<data_ref.data.length; i++) { // rows in data_ref.data
		if (fields_match.length) for (j=0; j<data_in.data.length; j++) { // rows in data_in.data
			for (k=0; k<fields_match.length; k++) {
				if (data_in.data[j][fields_match_indexes_i[k]]!=data_ref.data[i][fields_match_indexes_r[k]]) break
			};
			if (k==fields_match.length) { // hit
				m = data_out_add(m, data_out, fields_extract_indexes_r, i, data_ref, indexfield, _data_out, fields_extract_indexes_i, data_in, j);
				if (duplicates == "first" && !duplicates_count) break
			}
		}
		else {
			m = data_out_add(m, data_out, fields_extract_indexes_r, i, data_ref, indexfield, _data_out, fields_extract_indexes_i, data_in, i);
			data_out[i]=fromarray(data_out[i])
		};
			
		t2 = new Date().getTime();
		if (t2 - t1 > 500) {
			t1 = t2;
			set_progress("Extracting... ", i + 1, data_ref.data.length * 2)
		}
	};
	
	if (fields_match.length) for (i=0; i<data_out.length; i++) {
		if (data_out[i].length) {
			if (duplicates=="list") {
				for (j=0; j<data_out[i].length; j++) { // rows
					if (duplicates_count) data_out[i][j].push(data_out[i].length-1)
				};
			}
			else {
				if (duplicates=="average") {
					v=[];
					for (j=0; j<data_out[i].length; j++) { // rows
						for (k=0; k<_data_out.data_format.length; k++) { // columns
							if (!is_decimal(data_out[i][j][k]) || _data_out.data_format[k]==indexfield) {
								if (!v[k]) v[k]=data_out[i][j][k]
							}
							else {
								tmp = parseFloat(data_out[i][j][k]);
								if (!v[k]) v[k]=0;
								v[k] += tmp
							}
						};
					};
					for (k=0; k<_data_out.data_format.length; k++) if (is_decimal(v[k]) && _data_out.data_format[k]!=indexfield) {
						v[k]=(v[k]/data_out[i].length).accuracy(10)
					}
				}
				else v=data_out[i][duplicates=="last"?data_out[i].length-1:0];
				if (duplicates_count) v.push(data_out[i].length-1);
				data_out[i]=[v]
			}
		};
		data_out[i]=fromarray(data_out[i]);
			
		t2 = new Date().getTime();
		if (t2 - t1 > 500 || i == data_out.length - 1) {
			t1 = t2;
			set_progress("Extracting... ", data_ref.data.length + i + 1, data_ref.data.length * 2)
		}
	};
	
	if (duplicates_count) {
		_data_out.header_set_field("KEYWORD", "\"DUPLICATES\"", "append");
		_data_out.data_format.push("DUPLICATES")
	};
	
	_data_out.data = toarray(data_out.join("\n"));
	_data_out.decimal = decimal_comma?",":".";
	
	set_status("");
	
	return _data_out
};

function form_element_set_disabled(form_element, disabled) {
	if (!form_element || form_element.readOnly || form_element.type == "hidden" || form_element.type == "file" || jsapi.dom.attributeHasWord(form_element, "class", "fakefile") || jsapi.dom.attributeHasWord(form_element, "class", "save") || jsapi.dom.attributeHasWord(form_element, "class", "delete")) return;
	disabled = disabled ? "disabled" : "";
	form_element.disabled=disabled;
	if (disabled && !jsapi.dom.attributeHasWord(form_element, "class", "disabled")) jsapi.dom.attributeAddWord(form_element, "class", "disabled");
	else if (!disabled && jsapi.dom.attributeHasWord(form_element, "class", "disabled")) jsapi.dom.attributeRemoveWord(form_element, "class", "disabled");
	var labels = document.getElementsByTagName("LABEL");
	for (var i=0; i<labels.length; i++) if (labels[i].getAttribute("for") == form_element.id) labels[i].className=disabled
};

function form_elements_set_disabled(form, disabled) {
	disabled = disabled ? "disabled" : "";
	if (form) for (var j=0; j<form.elements.length; j++) form_element_set_disabled(form.elements[j], disabled);
	else {
		for (var i=0; i<document.forms.length; i++) {
			for (var j=0; j<document.forms[i].elements.length; j++) form_element_set_disabled(document.forms[i].elements[j], disabled)
		}
	}
};

function data_out_add(m, data_out, fields_extract_indexes_r, i, data_ref, indexfield, _data_out, fields_extract_indexes_i, data_in, j) {
	var k, n, v;
	if (m!=i) {
		m=i;
		data_out.push([])
	};
	data_out[data_out.length-1][data_out[data_out.length-1].length]=[];
	for (k=0; k<fields_extract_indexes_r.length; k++) {
		v=data_ref.data[i][fields_extract_indexes_r[k]];
		if ((n=data_ref.data_format[fields_extract_indexes_r[k]])==indexfield) {
			if (_data_out.data_format.length<fields_extract_indexes_r.length+fields_extract_indexes_i.length) _data_out.data_format.unshift(n);
			data_out[data_out.length-1][data_out[data_out.length-1].length-1].unshift(v)
		}
		else {
			if (_data_out.data_format.length<fields_extract_indexes_r.length+fields_extract_indexes_i.length) _data_out.data_format.push(n);
			data_out[data_out.length-1][data_out[data_out.length-1].length-1].push(v)
		}
	};
	for (k=0; k<fields_extract_indexes_i.length; k++) {
		v=data_in.data[j][fields_extract_indexes_i[k]];
		if ((n=data_in.data_format[fields_extract_indexes_i[k]])==indexfield) {
			if (_data_out.data_format.length<fields_extract_indexes_r.length+fields_extract_indexes_i.length) _data_out.data_format.unshift(n);
			data_out[data_out.length-1][data_out[data_out.length-1].length-1].unshift(v)
		}
		else {
			if (_data_out.data_format.length<fields_extract_indexes_r.length+fields_extract_indexes_i.length) _data_out.data_format.push(n);
			data_out[data_out.length-1][data_out[data_out.length-1].length-1].push(v)
		}
	};
	return m
};

function set_status(str, append) {
	if (append) window.status += str;
	else window.status = str
};

function set_progress(str, cur_num, max_num) {
	p = Math.ceil(100 / max_num * cur_num);
	set_status(str + p + "% " + "|".repeat(p / 2))
};

function basename(path) {
	return path.split(/[\/\\]/).pop()
};

function splitext(path) {
	return path.match(/(^.+?)(\.\w+)?$/).slice(1)
};

function plaintext(which) {
	var e = document.forms['F_data'].elements;
	if (which == 'ref') 
		var f = 'FF_data_ref';
	else
		var f = 'FF_data_in';
	var win = window.open();
	win.document.open('text/plain');
	win.document.write(e[f].value);
	win.document.close();
};
