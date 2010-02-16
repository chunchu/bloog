# Install the GData python libraries if you want to use Picasa web albums 
# as your image store.  This script must be run from your bloog root directory, i.e.
# ~/bloog$ dev/gdata-install.sh
# All necessary dependencies are extracted to utils/external/

version=2.0.7
dir="gdata-$version/src/gdata"
file="gdata-$version.tar.gz"

wget "http://gdata-python-client.googlecode.com/files/$file"
tar -xzf $file

dest="utils/external/gdata"
mkdir $dest
cp -r $dir/photos $dir/geo $dir/media $dir/exif $dir/alt $dir/docs \
	$dir/oauth $dir/tlslite $dir/auth.py $dir/gauth.py $dir/service.py \
	$dir/urlfetch.py $dir/__init__.py $dest

dest="utils/external/atom"
mkdir $dest
dir="gdata-$version/src/atom"
cp $dir/__init__.py $dir/http.py $dir/http_core.py $dir/http_interface.py \
	$dir/service.py $dir/token_store.py $dir/url.py $dest

#clean up
rm -r "gdata-$version"
rm $file

#for ElementTreee
version="1.2.7-20070827-preview"
dir="elementtree-$version/elementtree"
file="elementtree-$version.zip"
wget "http://effbot.org/media/downloads/$file"
unzip $file

dest="utils/external/elementtree"
mkdir $dest
cp $dir/__init__.py $dir/ElementTree.py $dir/SimpleXMLTreeBuilder.py $dest
  
rm -r "elementtree-$version"
rm $file
