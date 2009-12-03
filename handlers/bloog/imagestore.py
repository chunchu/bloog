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
from google.appengine.ext import webapp
from google.appengine.api import memcache
from utils import authorized
from models.image import Image

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

    logging.info("ImagestoreHandler#get for file: %s", id)
    img = None
    try:
      img = Image.get( id )
      if not img: raise "Not found"
    except:
      self.error(404)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write( "Could not find image: '%s'" % id )
      return
      
    logging.info( "Found image: %s, mime type: %s", img.name, img.mimeType )
    
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
    
    # it doesn't seem possible for webob to get the Content-Type header for the individual part, 
    # so we'll infer it from the file name.
    contentType = getContentType( fileupload.filename )
    if contentType is None: 
      self.error(400)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write( "Unsupported image type: " + fileupload.filename )
      return
    logging.info( "File upload: %s, mime type: %s", fileupload.filename, contentType )
    
    img = Image( name=fileupload.filename, data= fileupload.file.read(), 
        mimeType=contentType )
    img.put()
    logging.info("Saved image to key %s", img.key() ) 
    #self.redirect(urlBase % img.key() )  #dummy redirect is acceptable for non-AJAX clients,
    # location header should be acceptable for true REST clients, however AJAX requests will likely not be able to access
    # the location header so we'll write a 200 response with the new URL in the response body:
    self.response.headers['Location'] = urlBase % img.key()
    
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