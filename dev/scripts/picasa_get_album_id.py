# see: http://code.google.com/apis/picasaweb/docs/1.0/developers_guide_python.html#PostPhotos
import gdata.photos
import gdata.photos.service
import pprint

user='tmnichols'
albumName='Technology' #'default'

client = gdata.photos.service.PhotosService()
feed = client.GetUserFeed(user=user)
album_id = None
for album in feed.entry:
  if album.name.text == albumName: album_id = album.gphoto_id.text

if album_id: print "Found album '%s', ID: %s" % (albumName, album_id)
else: print "Couldn't find any album named '%s' for user '%s'" % (albumName, user)

feed = client.GetFeed( '/data/feed/api/user/%s/albumid/%s?kind=photo' % (
        user, album_id))
for photo in feed.entry:
  print 'Photo title: %s, url: %s' % (photo.title.text, photo.content.src)
  #pprint.pprint( photo.__dict__ )
  #print

