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

BLOG = {
    "bloog_version": "0.8",
    "html_type": "text/html",
    "charset": "utf-8",
    "title": "Medi@rcade!",
    "author": "Tom Nichols",
    # This must be the email address of a registered administrator for the 
    # application due to mail api restrictions.
    "email": "tmnichols@gmail.com",
    "description": "Technology is evolution outside the gene pool",
    "root_url": "http://mediarcade.appspot.com",
    "master_atom_url": "/feeds/atom.xml",
    # By default, visitors can comment on article for this many days.
    # This can be overridden by setting article.allow_comments
    "days_can_comment": 60,
    # You can override this default for each page through a handler's call to 
    #  view.ViewPage(cache_time=...)
    "cache_time": 0 if DEBUG else 3600,

    # Use the default YUI-based theme.
    # If another string is used besides 'default', calls to static files and
    #  use of template files in /views will go to directory by that name.
    "theme": ["default"],
    
    # Display gravatars alongside user comments?
    "use_gravatars": True,
    
    # Do you want to be emailed when new comments are posted?
    "send_comment_notification": True,

    # If you want to use legacy ID mapping for your former blog platform,
    # define it here and insert the necessary mapping code in the
    # legacy_id_mapping() function in ArticleHandler (blog.py).
    # Currently only "Drupal" is supported.
    "legacy_blog_software": None,
    #"legacy_blog_software": "Drupal",
    #"legacy_blog_software": "Serendipity",
    
    # If you want imported legacy entries _not_ mapped in the file above to
    # redirect to their new permanent URL rather than responding on their
    # old URL, set this flag to True.
    "legacy_entry_redirect": False,
}

PAGE = {
    "title": BLOG["title"],
    "articles_per_page": 5,
    "yui_version":'2.8.0r4',
    "navlinks": [
        { "title": "Articles", "description": "Bits of Info", 
          "url": "/articles"},
        { "title": "Contact", "description": "Send me a note", 
          "url": "/contact"},
    ],
    "featuredMyPages": {
        "title": "About Me",
        "description": """I'm a software Engineer living near Providence, RI. &nbsp;
          I code for work, freelance, and when an idea strikes me, sometimes 
          just for fun.""",
        "entries": [
            { "title": "On Twitter", 
              "url": "http://twitter.com/tom_nichols", 
              "description": "Twitter Feed" },
            { "title": "On GitHub", 
              "url": "http://github.com/tomstrummer", 
              "description": "Projects hosted on Github" },
            { "title": "HTTP Builder", 
              "url": "http://groovy.codehaus.org/modules/http-builder", 
              "description": "One of my more significant open-source contributions" },
            { "title": "My Google Reader Feed", 
              "url": "https://www.google.com/reader/shared/00209487153858041827", 
              "description": "Interesting articles worth passing along" }
        ]
    },
    "featuredOthersPages": {
        "title": "Additional Links",
        "description": "Miscellaneous Resources",
        "entries": [
            { "title": "Google App Engine", 
              "url": "http://code.google.com/appengine/", 
              "description": "The mothership" },
            { "title": "Groovy", 
              "url": "http://groovy.codehaus.org", 
              "description": "Programming language of choice" }
        ]
    },
}
