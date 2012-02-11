#!/bin/sh

# Install udev rules or hotplug scripts
if [ -e "/etc/udev/rules.d" ]; then
	ls /dev/bus/usb/*/* > /dev/null 2>&1 && (
		# USB and serial instruments using udev, where udev already creates /dev/bus/usb/00X/00X devices
		if [ ! -e "/etc/udev/rules.d/55-Argyll.rules" ]; then
			ln -s "/usr/share/dispcalGUI/usb/55-Argyll.rules" "/etc/udev/rules.d/55-Argyll.rules"
		fi
	) || (
		# USB using udev, where there are NOT /dev/bus/usb/00X/00X devices
		if [ ! -e "/etc/udev/rules.d/45-Argyll.rules" ]; then
			ln -s "/usr/share/dispcalGUI/usb/45-Argyll.rules" "/etc/udev/rules.d/45-Argyll.rules"
		fi
	)
	# Reload udev rules
	if [ -e "/sbin/udevadm"]; then
		/sbin/udevadm control --reload-rules
	fi
else
	if [ -e "/etc/hotplug"]; then
		# USB using hotplug and Serial using udev (older versions of Linux)
		if [ ! -e "/etc/hotplug/usb/Argyll" ]; then
			ln -s "/usr/share/dispcalGUI/usb/Argyll" "/etc/hotplug/usb/Argyll"
		fi
		if [ ! -e "/etc/hotplug/usb/Argyll.usermap" ]; then
			ln -s "/usr/share/dispcalGUI/usb/Argyll.usermap" "/etc/hotplug/usb/Argyll.usermap"
		fi
	fi
fi

# Update icon cache and menu
which xdg-icon-resource > /dev/null 2>&1 && xdg-icon-resource forceupdate || true
which xdg-desktop-menu > /dev/null 2>&1 && xdg-desktop-menu forceupdate || true
