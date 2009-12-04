from google.appengine.ext import db
import models

class Image(models.SerializableModel):
  
  name = db.StringProperty(required=True)
  data = db.BlobProperty(required=True)
  mimeType = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  owner = db.UserProperty(auto_current_user_add=True)
