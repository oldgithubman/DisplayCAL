#!/bin/sh

function createpreset() {
	local root="`dirname \"$0\"`/.."
	echo "$1"
	colprof  -ql -aG -C "Created with dispcalGUI and Argyll CMS" -D "dispcalGUI calibration preset: $1" "$root/misc/ti3/$2"
	mv -i "$root/misc/ti3/$2".ic? "$root/dispcalGUI/presets/$2.icc" && python "$root/util/update_presets.py" "$2"
	echo ""
}

createpreset "Laptop"       "laptop"
createpreset "madVR"        "madVR"
createpreset "Office & Web" "office_web"
createpreset "Photo"        "photo"
createpreset "Prepress"     "prepress"
createpreset "Resolve"      "resolve"
createpreset "Softproof"    "softproof"
createpreset "sRGB"         "sRGB"
createpreset "Video"        "video"
