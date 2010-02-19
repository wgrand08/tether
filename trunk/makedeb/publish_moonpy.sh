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
cd ..
rm -fr ./moonpy-$version*
mkdir ./moonpy-$version
echo creating multi-arch archive moonpy-all-$version
cp -r ./client ./moonpy-$version
cp -r ./common ./moonpy-$version
cp -r ./data ./moonpy-$version
cp -r ./server ./moonpy-$version
cp -r ./translations ./moonpy-$version
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
cd ..
tar -czvf ./moonpy-all-$version.tar.gz ./moonpy-$version
echo "finished creating multi-arch archive"
echo "starting creation of deb package"
cd moonpy-$version
echo "optimizing code for debian"
rm -fr ./zope
rm -fr ./twisted
cd ..
tar -czvf ./moonpy-$version.tar.gz ./moonpy-$version
echo "sandboxing source code"
mkdir ./sandbox
mv ./moonpy-$version ./sandbox/
mv ./moonpy-$version.tar.gz ./sandbox/moonpy-$version
cd sandbox/moonpy-$version
echo "creating dh_make files for moonpy, please choose 's'"
dh_make -e project-tether@googlegroups.com -c gpl3 -f moonpy-$version.tar.gz
cd ..
rm -fr ./moonpy-$version.tar.gz
cd ..
echo "copying prebuilt package config files"
cp ./makedeb/control ./sandbox/moonpy-$version/debian
cp ./makedeb/rules ./sandbox/moonpy-$version/debian
cp ./makedeb/dir ./sandbox/moonpy-$version/debian
cp ./makedeb/copyright ./sandbox/moonpy-$version/debian
cd moonpy-$version/debian
echo "removing unnecessary package config files"
rm *.ex
rm *.EX
cd ..
echo "root access is required by dpkg to continue"
sudo dpkg-buildpackage
echo "debian packaging complete, converting to rpm"
cd ..
sudo alien --to-rpm
cd ..
echo "rpm packaging complete, cleaning up..."
cp ./sandbox/moonpy-$version*.deb ./
cp ./sandbox/moonpy-$version*.rpm ./
sudo rm -fr ./sandbox
echo "finished packaging MoonPy $version"
