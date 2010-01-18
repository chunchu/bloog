# The MIT License
# 
# Copyright (c) 2009 Tom Nichols
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

"""A RESTful BLOB image store handler. 
See http://code.google.com/appengine/docs/python/images/usingimages.html
Supports: 
 * uploading & fetching images
 * image listing to HTML or JSON
 * downloading as attachment
 * deleting via HTTP DELETE
To Do:
 * Memcache recently fetched images? (esp if resized on GET)
 * Dynamically resize? (on upload or as GET params?)
"""
__author__ = 'Thomas Nichols'

import logging
import re
import gdata.photos, gdata.photos.service, gdata.alt.appengine
from google.appengine.ext import webapp
from utils import authorized
from models.image import Image
import config


urlBase = '/imgstore/%s'

class ImageHandler(webapp.RequestHandler):
  
  def get(self,id):
    if not id: # perform 'list' function if no ID given.
      limit = int(self.request.get('limit','10'))
      if limit > 50: limit = 50 #enforce max
      offset = int(self.request.get('offset','0'))
      images = Image.all().order("-created").fetch(limit,offset)
      acceptType = self.request.accept.best_match( listRenderers.keys() )
      # TODO handle unknown accept type
      self.response.headers['Content-Type'] = acceptType
      listRenderers[acceptType](self.response.out, images)
      return

    logging.debug("ImagestoreHandler#get for file: %s", id)
    try:
      img = Image.get( id )
      if not img: raise "Not found"
    except:
      self.error(404)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write( "Could not find image: '%s'" % id )
      return
      
    logging.debug( "Found image: %s, mime type: %s", img.name, img.mimeType )
    
    dl = self.request.get('dl') # optionally download as attachment
    if dl=='1' or dl=='true':
      self.response.headers['Content-Disposition'] = 'attachment; filename="%s"' % str(img.name)
        
    self.response.headers['Content-Type'] = str(img.mimeType)
    self.response.out.write( img.data )

  @authorized.role("admin")
  def post(self,id):
    logging.info("ImagestoreHandler#post %s", self.request.path)
    fileupload = self.request.POST.get("file",None)
    if fileupload is None : return self.error(400)
    
    # it doesn't seem possible for webob to get the Content-Type header for the 
    # individual part, so we'll infer it from the file name.
    contentType = getContentType( fileupload.filename )
    if contentType is None: 
      self.error(400)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write( "Unsupported image type: " + fileupload.filename )
      return
    logging.debug( "File upload: %s, mime type: %s", fileupload.filename, contentType )
    
    try:
      (img_name, img_url) = self._store_image(
        fileupload.filename, fileupload.file, contentType )
      self.response.headers['Location'] = img_url
      ex=None
    except Exception, err:
      logging.exception( "Error while storing image" )
      self.error(400)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write("Error uploading image: " + str(err))
      return
    #self.redirect(urlBase % img.key() )  #dummy redirect is acceptable for non-AJAX clients,
    # location header should be acceptable for true REST clients, however AJAX requests 
    # might not be able to access the location header so we'll write a 200 response with 
    # the new URL in the response body:
    
    acceptType = self.request.accept.best_match( listRenderers.keys() )
    out = self.response.out
    if acceptType == 'application/json':
      self.response.headers['Content-Type'] = 'application/json'
      out.write( '{"name":"%s","href":"%s"}' % ( img_name, img_url ) )
    elif re.search( 'html|xml', acceptType ):
      self.response.headers['Content-Type'] = 'text/html'
      out.write( '<a href="%s">%s</a>' % ( img_url, img_name) )
    
  def _store_image(self, name, file, content_type):
    """POST handler delegates to this method for actual image storage; as
    a result, alternate implementation may easily override the storage
    mechanism without rewriting the same content-type handling. 
        
    This method returns a tuple of file name and image URL."""
        
    img = Image( name=name, data=file.read(), mimeType=content_type )
    img.put()
    logging.info("Saved image to key %s", img.key() ) 
    return ( str(img.name), urlBase % img.key() )
  
  
  @authorized.role("admin")
  def delete(self,id):
    logging.info( "ImagestoreHandler#DELETE file: %s", id )
    
    img = None
    try:
      img = Image.get( id )
      if not img: raise "Not found"
    except:
      self.error(404)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write( "Could not find image: '%s'" % id )
      return
    
    img.delete()

class PicasaImageHandler(ImageHandler):
  """
  Upload photos to Picasa instead of the Appengine data store.  Note that 
  GET requests are not handled by this handler, since the images are hosted on 
  Picasa's servers.
  See: http://code.google.com/apis/picasaweb/docs/1.0/developers_guide_python.html#PostPhotos
  """
  
  def __init__(self):
    # ElementTree uses expat which is not available on GAE; it is used by gdata's atom 
    # module to parse the response.  The solution is to replace the built-in 
    # ElementTree.XMLTreeBuilder with the SimpleXMLTreeBuilder implementation.
    from xml.etree import ElementTree
    import utils.external.elementtree.SimpleXMLTreeBuilder as SimpleXML
    ElementTree.XMLTreeBuilder = SimpleXML.TreeBuilder 
  
    client = gdata.photos.service.PhotosService()
    gdata.alt.appengine.run_on_appengine(client)
    auth = config.BLOG['picasa_auth']
    # TODO this could be a non-gmail account (if using Google hosted apps):
    client.email = auth['user'] + "@gmail.com" 
    client.password = auth['password']
    client.ProgrammaticLogin()
    self.client = client
    self.auth = auth

  def _store_image(self, name, file, content_type):
    #logging.debug( "Storing image '%s' on Picasa", name )
    raise Exception("Big oops!")
    album_url = '/data/feed/api/user/%s/albumid/%s' % ( self.auth['user'], self.auth['album'] )
    photo = self.client.InsertPhotoSimple( album_url, name, 
      'Uploaded using the Bloog!', file, content_type=content_type )
    logging.debug( "Uploaded photo to Picasa at %s", photo.content.src )
    return ( photo.title.text, photo.content.src )


  #def get(self,id): pass # TODO look up image and redirect to Picasa?
    # Maybe this shouldn't be implemented, that way if a user moves from local image store
    # to Picasa, they will still have access to local images when requested from a blog entry

  #def delete(self,id): pass # TODO implement Picasa delete?


def renderJsonList(out,imgList):
  out.write('[')
  for img in imgList:
    out.write('{"href":"%s","name":"%s","mimeType":"%s"},' % 
      ( urlBase % img.key(), str(img.name), str(img.mimeType) ) )
  out.write(']')

def renderHtmlList(out,imgList):
  out.write('<ul>')
  for img in imgList:
    out.write('<li><img src="%s" alt="%s" /></li>' % ( urlBase % img.key(), str(img.name) ))
  out.write('</ul>')

listRenderers = { 'application/json': renderJsonList, 
    'application/xhtml+xml': renderHtmlList, 'application/xml': renderHtmlList, 
    'text/html': renderHtmlList }
  
def getContentType( filename ): # lists and converts supported file extensions to MIME type
  ext = filename.split('.')[-1].lower()
  if ext == 'jpg' or ext == 'jpeg': return 'image/jpeg'
  if ext == 'png': return 'image/png'
  if ext == 'gif': return 'image/gif'
  if ext == 'svg': return 'image/svg+xml'
  return None