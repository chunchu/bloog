# Script to download locally-hosted versions of the YUI libraries for use 
# during development.  In production, the app uses Yahoo's CDN-hosted and minified
# versions of the scripts. 

version='2.8.0r4'
file="yui_$version.zip"

wget "http://yuilibrary.com/downloads/yui2/$file"
unzip $file "yui/build/*"

dest='static/hosted/yui'
mkdir -p $dest

libs=(animation assets button calendar connection container dom 
  editor element json menu selector yahoo-dom-event)
for lib in "${libs[@]}" ; do
  echo "Copying yui_$version/$lib to $dest/"
  cp -r yui/build/$lib $dest
done

# clean up:
echo "Cleaning up..."
rm -r $file yui/

echo "Done"