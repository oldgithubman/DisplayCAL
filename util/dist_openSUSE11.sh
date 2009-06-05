#!/bin/sh

dist=openSUSE11

platform=`uname -i`
version=`python -c "from dispcalGUI import meta;print meta.version"`

# Python 2.5 RPM
/usr/bin/python2.5 setup.py bdist_rpm --cfg=$dist --use-distutils 2>&1 | tee dispcalGUI-$version-py2.5-$dist.$platform.bdist_rpm.log
mv -f dist/dispcalGUI-$version-1.$platform.rpm dist/dispcalGUI-$version-py2.5-$dist-1.$platform.rpm
mv -f dist/dispcalGUI-$version-1.src.rpm dist/dispcalGUI-$version-py2.5-$dist-1.src.rpm

# Python 2.6 RPM
/usr/bin/python2.6 setup.py bdist_rpm --cfg=$dist --use-distutils 2>&1 | tee dispcalGUI-$version-py2.6-$dist.$platform.bdist_rpm.log
mv -f dist/dispcalGUI-$version-1.$platform.rpm dist/dispcalGUI-$version-py2.6-$dist-1.$platform.rpm
mv -f dist/dispcalGUI-$version-1.src.rpm dist/dispcalGUI-$version-py2.6-$dist-1.src.rpm
