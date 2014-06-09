#!/bin/bash


#Copyright 2009:
#    Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


#this script is used for automating the process of creating 
#archives and debfiles for publishing and distributing MoonPy

echo "Welcome to the MoonPy packaging and distribution script,"
echo "please enter version of MoonPy to package"
read version
echo "Should this version be uploaded onto googlecode after packaging?"
echo "y/n"
read upload
if [ "$upload" == "y" ]; then
    echo "Please enter googlecode username"
    read username
    echo "Please enter googlecode password"
    read password
fi
cd ..
echo "this script uses sudo to continue; please enter admin password"
sudo rm -fr ./moonpy-$version*
sudo rm -fr ./moonpy*.deb
sudo rm -fr ./moonpy*.rpm
sudo rm -fr ./sandbox
echo "finished cleaning old package files"
mkdir ./moonpy-$version
echo "creating source archive"
cp -r ./client ./moonpy-$version
cp -r ./common ./moonpy-$version
cp -r ./data ./moonpy-$version
cp -r ./server ./moonpy-$version
cp -r ./twisted ./moonpy-$version
cp -r ./zope ./moonpy-$version
cp -r ./AUTHORS.txt ./moonpy-$version
cp -r ./COPYING.txt ./moonpy-$version
cp -r ./moon.py ./moonpy-$version
cp -r ./README.txt ./moonpy-$version
cd moonpy-$version
echo "cleaning system and subversion files"
find . -name .svn -exec rm -rf {} \;
find . -name *.pyc -exec rm -rf {} \;
find . -name *~ -exec rm -rf {} \;
cd ..
tar -czvf ./moonpy-$version-source.tar.gz ./moonpy-$version
echo "finished creating source archive"
echo "starting creation of osX package"
zip -r -9 ./moonpy-$version-osX.zip ./moonpy-$version
echo "starting creation of windows package"
cp ./makedeb/MoonPy.exe ./moonpy-$version
zip -r -9 ./moonpy-$version-win32.zip ./moonpy-$version
cd moonpy-$version
echo "optimizing code for debian"
rm -fr ./MoonPy.exe
rm -fr ./zope
rm -fr ./twisted
cp ../makedeb/moonpy.desktop ./moonpy.desktop
cp ../makedeb/run_moonpy.sh ./run_moonpy.sh
tar -czvf ./moonpy-$version-package-source.tar.gz ./*
cd ..
mv ./moonpy-$version/moonpy-$version-package-source.tar.gz ./
rm -fr ./moonpy-$version
echo "sandboxing source code"
mkdir ./sandbox
mkdir ./sandbox/moonpy-$version
cp ./moonpy-$version-package-source.tar.gz ./sandbox/moonpy-$version/moonpy-$version.tar.gz
cd sandbox/moonpy-$version
tar -xzvf ./moonpy-$version.tar.gz
echo "creating dh_make files for moonpy" | dh_make -s -e project-tether@googlegroups.com -c gpl3 -f moonpy-$version.tar.gz
cd ..
rm -fr ./moonpy_$version.orig.tar.gz
cd ..
echo "copying prebuilt package config files"
cp ./makedeb/control ./sandbox/moonpy-$version/debian
cp ./makedeb/rules ./sandbox/moonpy-$version/debian
cp ./makedeb/dirs ./sandbox/moonpy-$version/debian
cp ./makedeb/copyright ./sandbox/moonpy-$version/debian
cd sandbox/moonpy-$version/debian
echo "removing unnecessary package config files"
rm -fr *.ex
rm -fr *.EX
cd ..
#dpkg-buildpackage -S -sa -rfakeroot
dpkg-buildpackage -rfakeroot
echo "debian packaging complete, converting to rpm"
cd ..
sudo chown $USERNAME ./moonpy*.deb
mv ./moonpy*_amd64.deb ../moonpy-$version.deb
cd ..
sudo alien --to-rpm ./moonpy-$version.deb
sudo chown $USERNAME ./moonpy*.rpm
mv ./moonpy*.rpm ./moonpy-$version.rpm
echo "rpm packaging complete, cleaning up..."
sudo rm -fr ./sandbox
sudo rm -fr ~/rpmbuild
echo "finished packaging MoonPy $version"
if [ "$upload" == "y" ]; then
    echo "Uploading packages to googlecode"
    ./makedeb/googlecode_upload.py -s "MoonPy $version source archive for packaging" -p tether -u $username -w $password -l Type-Source,OpSys-All ./moonpy-$version-package-source.tar.gz
    ./makedeb/googlecode_upload.py -s "MoonPy $version source for all OS's" -p tether -u $username -w $password -l Type-Source,OpSys-All ./moonpy-$version-source.tar.gz
    ./makedeb/googlecode_upload.py -s "MoonPy $version for osX" -p tether -u $username -w $password -l Featured,Type-Archive,OpSys-osX ./moonpy-$version-osX.zip
    ./makedeb/googlecode_upload.py -s "MoonPy $version for windows" -p tether -u $username -w $password -l Featured,Type-Archive,OpSys-Windows ./moonpy-$version-win32.zip
    ./makedeb/googlecode_upload.py -s "MoonPy $version for rpm based linux" -p tether -u $username -w $password -l Featured,Type-Package,OpSys-Linux ./moonpy-$version.rpm
    ./makedeb/googlecode_upload.py -s "MoonPy $version for debian based linux" -p tether -u $username -w $password -l Featured,Type-Package,OpSys-Linux ./moonpy-$version.deb
fi
echo "MoonPy packaging and distribution script finished"
