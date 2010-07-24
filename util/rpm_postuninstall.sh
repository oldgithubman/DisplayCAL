#!/bin/sh

# Remove udev rules or hotplug scripts
if [ -L "/etc/udev/rules.d/55-Argyll.rules" ]; then
	rm -f "/etc/udev/rules.d/55-Argyll.rules"
fi
if [ -L "/etc/udev/rules.d/45-Argyll.rules" ]; then
	rm -f "/etc/udev/rules.d/45-Argyll.rules"
fi
if [ -L "/etc/hotplug/usb/Argyll" ]; then
	rm -f "/etc/hotplug/usb/Argyll"
fi
if [ -L "/etc/hotplug/usb/Argyll.usermap" ]; then
	rm -f "/etc/hotplug/usb/Argyll.usermap"
fi

# Update icon cache and menu
which xdg-desktop-menu > /dev/null 2>&1 && xdg-desktop-menu forceupdate || true
which xdg-icon-resource > /dev/null 2>&1 && xdg-icon-resource forceupdate || true
