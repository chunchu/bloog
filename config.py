import os
import logging

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# If we're debugging, turn the cache off, etc.
# Set to true if we want to have our webapp print stack traces, etc
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
logging.info("Starting application in DEBUG mode: %s", DEBUG)

# Don't change default_blog or default_page to prevent conflicts when merging 
#  Bloog source code updates.
# Do change blog or page dictionaries at the bottom of this config module.

# This is used for django to find the custom templatetags:
INSTALLED_APPS = ('utils')

BLOG = {
    "bloog_version": "0.8",
    "html_type": "application/xhtml+xml",
    "charset": "utf-8",
    "title": "Thom Nichols",
    "author": "Thom Nichols",
    # This must be the email address of a registered administrator for the 
    # application due to mail api restrictions.
    "email": "tmnichols@gmail.com",
    "tagline": "Technology is evolution outside the gene pool",
    "description": """I'm a Software Engineer living near Providence, RI. 
          I code for work, freelance, and when an idea strikes me, sometimes 
          just for fun.""",
    "root_url": "http://blog.thomnichols.org",
    "master_atom_url": "/feeds/atom.xml",
    # if you had users following your old blog's atom feed, but want to use a different feed going forward:
    "legacy_atom_url": '/feeds/posts/default',
    # By default, visitors can comment on article for this many days.
    # This can be overridden by setting article.allow_comments
    "days_can_comment": 60,
    # You can override this default for each page through a handler's call to 
    #  view.ViewPage(cache_time=...)
    "cache_time": 0 if DEBUG else 3600,
    #"cache_time":  3600,

    # Use the default YUI-based theme.
    # If another string is used besides 'default', calls to static files and
    #  use of template files in /views will go to directory by that name.
    "theme": ["default"],
    
    # Display gravatars alongside user comments?
    "use_gravatars": True,
    
    # reCAPTCHA settings.  See http://recaptcha.net/api/getkey
    "recap_public_key": "CHANGEME",
    "recap_private_key": "CHANGEME",
    
    # Do you want to be emailed when new comments are posted?
    "send_comment_notification": True,

    # If you want to use legacy ID mapping for your former blog platform,
    # define it here and insert the necessary mapping code in the
    # legacy_id_mapping() function in ArticleHandler (blog.py).
    # Currently only "Drupal" is supported.
    "legacy_blog_software": None,
    #"legacy_blog_software": "Drupal",
    #"legacy_blog_software": "Blogger",
    
    # If you want imported legacy entries _not_ mapped in the file above to
    # redirect to their new permanent URL rather than responding on their
    # old URL, set this flag to True.
    "legacy_entry_redirect": True,
    
    "picasa_image_store": False, # if false, will use local datastore for uploaded images
    "gdata": { 'user':'CHANGEME', 
        'password':'CHANGEME',  # your google accounts password :(
        'source' : 'tomstrummer-bloog-v0.8', #tells Google what app is using the service
        #this must be an ID or 'default' (not album name); see dev/scripts/picasa_get_album_id.py
        'album':'default' } #this must be 'default' or an ID (not name); see dev/scripts/picasa_get_album_id.py
}

PAGE = {
    "title": BLOG["title"],
    "articles_per_page": 5,
    "yui_version": '2.8.0r4',
    "author_name": 'Thom',
    "author_email": BLOG['email'],
    "ga_tracker": "UA-10492632-1", # Google Analytics tracker code
    "navlinks": [
        { "title": "Articles", "description": "Bits of Info", 
          "url": "/articles"},
        { "title": "Contact", "description": "Send me a note", 
          "url": "/contact"},
    ],
    "featuredMyPages": {
        "title": "About Me",
        "description": BLOG['description'],
        "entries": [
            { "title": "Portfolio", 
              "url": BLOG['root_url']+'/portfolio', 
              "description": "Work I've done" },
            { "title": "Profile", 
              "url": BLOG['root_url']+'/+', 
              "description": "on Google+" },
            { "title": "On Twitter", 
              "url": "http://twitter.com/thom_nic", 
              "description": "Twitter Feed" },
            { "title": "On GitHub", 
              "url": "http://github.com/tomstrummer", 
              "description": "Projects on Github" }
        ]
    },
    "featuredOthersPages": {
        "title": "Additional Links",
        "description": "Miscellaneous Resources",
        "entries": [
            { "title": "Marco Polo", 
              "url": "http://marcopolo.thomnichols.org", 
              "description": "Explore your social network!" },
            { "title": "HTTP Builder", 
              "url": "http://groovy.codehaus.org/modules/http-builder", 
              "description": "HTTP/ REST client API for Groovy" },
            { "title": "Python Web Console", 
              "url": "http://pythonwebconsole.thomnichols.org", 
              "description": "Run Python from your browser" },
            { "title": "Bloog", 
              "url": "http://bloog.billkatz.com/", 
              "description": "Customize your own blog" }
        ]
    },
}
