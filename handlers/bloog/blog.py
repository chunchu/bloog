# The MIT License
# 
# Copyright (c) 2008 William T. Katz
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

"""A simple RESTful blog/homepage app for Google App Engine

This simple homepage application tries to follow the ideas put forth in the
book 'RESTful Web Services' by Leonard Richardson & Sam Ruby.  It follows a
Resource-Oriented Architecture where each URL specifies a resource that
accepts HTTP verbs.

Rather than create new URLs to handle web-based form submission of resources,
this app embeds form submissions through javascript.  The ability to send
HTTP verbs POST, PUT, and DELETE is delivered through javascript within the
GET responses.  In other words, a rich client gets transmitted with each GET.

This app's API should be reasonably clean and easily targeted by other 
clients, like a Flex app or a desktop program.
"""
__author__ = 'William T. Katz'

import datetime
import string
import re
import os
import cgi
import urllib

import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.api import urlfetch

from handlers import restful
from utils import authorized
from utils import sanitizer
import captcha
import models
import view
import config

import legacy_aliases   # This can be either manually created or 
                        # autogenerated using the drupal_uploader utility

# Functions to generate permalinks depending on type of article
permalink_funcs = {
    'article': lambda title,date: get_friendly_url(title),
    'blog entry': lambda title,date: "%d/%02d/%s" % (date.year, date.month, get_friendly_url(title))
}

# We allow a mapping from some old url pattern to the current query 
#  using a regex's matched string.
def legacy_id_mapping(path, legacy_program):
    if legacy_program:
        legacy_id= None
        if legacy_program == 'Drupal':
            url_match = re.match('node/(\d+)/?$', path)
            if url_match: legacy_id= url_match.group(1)
        elif legacy_program == 'Serendipity':
            url_match = re.match('archives/(\d+)-.*\.html$', path)
            if url_match: legacy_id= url_match.group(1)
        elif legacy_program == 'Blogger':
            url_match = re.match('(\d+/\d+/[\w-]+).html$',path)
            if url_match: legacy_id= url_match.group(0)

        if legacy_id: return db.Query(models.blog.Article) \
            .filter('legacy_id =', legacy_id ).get()
    return None

# Module methods to handle incoming data
def get_datetime(time_string = None):
    if time_string:
        return datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    return datetime.datetime.now()

def get_format(format_string):
    if not format_string or format_string not in ['html', 'textile']:
        format_string = 'html'
    return format_string

def get_tag_key(tag_name):
    obj = models.blog.Tag.get_or_insert(tag_name)
    return obj.key()

def process_tag(tag_name, tags):
    # Check tag_name against all 'name' values in tags and coerce
    tag_name = tag_name.strip()
    lowercase_name = tag_name.lower()
    for tag in tags:
        if lowercase_name == tag['name'].lower():
            return tag['name']
    return tag_name

def get_tags(tags_string):
    logging.debug("get_tags: tag_string = %s", tags_string)
    if tags_string:
        from models.blog import Tag
        tags = Tag.list()
        logging.debug("  tags = %s", tags)
        return [process_tag(s, tags) 
                for s in tags_string.split(",") if s != '']
    return None
    
def get_friendly_url(title):
    return re.sub('-+', '-', re.sub('[^\w-]', '', 
                   re.sub('\s+', '-', title.strip().lower())))

def get_html(body, markup_type):
    if markup_type == 'textile':
        from utils.external.textile import textile
        return textile.textile(body)
    return body

def get_sanitizer_func(handler, **kwargs):
    match_obj = re.match(r'.*;\s*charset=(?P<charset>[\w-]+)',  
                         handler.request.headers['CONTENT_TYPE'])
    kwlist = {}
    kwlist.update(kwargs)
    if match_obj:
        kwlist.update({ 'encoding': match_obj.group('charset').lower() })
    logging.debug("Content-type: %s", handler.request.headers['CONTENT_TYPE'])
    logging.debug("In sanitizer: %s", kwlist)
    return lambda html : sanitizer.sanitize_html(html, **kwlist)

def do_sitemap_ping():
    form_fields = { "sitemap": "%s/sitemap.xml" % (config.BLOG['root_url'],) }
    urlfetch.fetch(url="http://www.google.com/webmasters/tools/ping",
                   payload=urllib.urlencode(form_fields),
                   method=urlfetch.GET)

def process_embedded_code(article):
    # TODO -- Check for embedded code, escape opening triangular brackets
    # within code, and set article embedded_code strings so we can
    # use proper javascript.
    from utils import codehighlighter
    article.html, languages = codehighlighter.process_html(article.html)
    article.embedded_code = languages

def process_article_edit(handler, permalink):
    # For http PUT, the parameters are passed in URIencoded string in body
    body = handler.request.body
    params = cgi.parse_qs(body)
    for key,value in params.iteritems():
        params[key] = value[0]
    property_hash = restful.get_sent_properties(params.get,
        ['title',
         ('body', get_sanitizer_func(handler, trusted_source=True)),
         ('format', get_format),
         ('updated', get_datetime),
         ('published', get_datetime),
         'legacy_id',
         ('tags', get_tags),
         ('html', get_html, 'body', 'format')])

    if property_hash:
        if 'tags' in property_hash:
            property_hash['tag_keys'] = [get_tag_key(name) 
                                         for name in property_hash['tags']]
        article = db.Query(models.blog.Article).filter('permalink =', permalink).get()
        before_tags = set(article.tag_keys)
        for key,value in property_hash.iteritems():
            setattr(article, key, value)
        after_tags = set(article.tag_keys)
        for removed_tag in before_tags - after_tags:
            db.get(removed_tag).counter.decrement()
        for added_tag in after_tags - before_tags:
            db.get(added_tag).counter.increment()
        process_embedded_code(article)
        article.put()
        restful.send_successful_response(handler, '/' + article.permalink)
        view.invalidate_cache()
    else:
        handler.error(400)

def process_article_submission(handler, article_type):
    property_hash = restful.get_sent_properties(handler.request.get, 
        ['title',
         ('body', get_sanitizer_func(handler, trusted_source=True)),
         'legacy_id',
         ('format', get_format),
         ('published', get_datetime),
         ('updated', get_datetime),
         ('tags', get_tags),
         ('html', get_html, 'body', 'format'),
         ('permalink', permalink_funcs[article_type], 'title', 'published')])

    if property_hash:
        if 'tags' in property_hash:
            property_hash['tag_keys'] = [get_tag_key(name) 
                                         for name in property_hash['tags']]
        property_hash['format'] = 'html'   # For now, convert all to HTML
        property_hash['article_type'] = article_type
        article = models.blog.Article(**property_hash)
        article.set_associated_data(
            {'relevant_links': handler.request.get('relevant_links'),
             'amazon_items': handler.request.get('amazon_items')})
        process_embedded_code(article)
        article.put()
        for key in article.tag_keys:
            db.get(key).counter.increment()
        do_sitemap_ping()
        restful.send_successful_response(handler, '/' + article.permalink)
        view.invalidate_cache()
    else:
        handler.error(400)

def process_comment_submission(handler, article):
    sanitize_comment = get_sanitizer_func(handler,
                                          allow_attributes=['href', 'src'],
                                          blacklist_tags=['img', 'script'])
    property_hash = restful.get_sent_properties(handler.request.get, 
        [('name', cgi.escape),
         ('email', cgi.escape),
         ('homepage', cgi.escape),
         ('title', cgi.escape),
         ('body', sanitize_comment),
         ('key', cgi.escape),
         'thread',    # If it's given, use it.  Else generate it.
         'recaptcha_challenge_field',
         'recaptcha_response_field',
         ('published', get_datetime)])

    # If we aren't administrator, abort if bad captcha
    if not users.is_current_user_admin():
        cap_challenge = property_hash.get('recaptcha_challenge_field')
        cap_response = property_hash.get('recaptcha_response_field')
        
        cap_validation = captcha.RecaptchaResponse(False)
        if cap_challenge and cap_response:
          cap_validation = captcha.submit( cap_challenge, cap_response, 
            config.BLOG['recap_private_key'], handler.request.remote_addr )
        
        if not cap_validation.is_valid: 
          logging.info( "Invalid captcha: %s", cap_validation.error_code )
          handler.error(401)      # Unauthorized
          return
          
    if 'key' not in property_hash and 'thread' not in property_hash:
        handler.error(401)
        return

    # Generate a thread string.
    if 'thread' not in property_hash:
        matchobj = re.match(r'[^#]+#comment-(?P<key>[\w-]+)', 
                            property_hash['key'])
        if matchobj:
            logging.debug("Comment has parent: %s", matchobj.group('key'))
            comment_key = matchobj.group('key')
            # TODO -- Think about GQL injection security issue since 
            # it can be submitted by public
            parent = models.blog.Comment.get(db.Key(comment_key))
            thread_string = parent.next_child_thread_string()
        else:
            logging.debug("Comment is off main article")
            comment_key = None
            thread_string = article.next_comment_thread_string()
        if not thread_string:
            handler.error(400)
            return
        property_hash['thread'] = thread_string
        del property_hash['key']

    # Get and store some pieces of information from parent article.
    # TODO: See if this overhead can be avoided
    if not article.num_comments: article.num_comments = 1
    else: article.num_comments += 1
    property_hash['article'] = article.put()

    try:
        comment = models.blog.Comment(**property_hash)
        comment.put()
    except:
        logging.debug("Bad comment: %s", property_hash)
        handler.error(400)
        return
        
    # Notify the author of a new comment (from matteocrippa.it)
    if config.BLOG['send_comment_notification'] and not users.is_current_user_admin():
        recipient = "%s <%s>" % (config.BLOG['author'], config.BLOG['email'])
        body = ("A new comment has just been posted on %s/%s by %s:\n\n%s"
                % (config.BLOG['root_url'], article.permalink, comment.name, comment.body))
        mail.send_mail(sender=config.BLOG['email'],
                       to=recipient,
                       subject="New comment by %s" % (comment.name),
                       body=body)

    # Render just this comment and send it to client
    view_path = view.find_file(view.templates, "bloog/blog/comment.html")
    response = template.render(
        os.path.join("views", view_path),
        { 'comment': comment, "use_gravatars": config.BLOG["use_gravatars"] },
        debug=config.DEBUG)
    handler.response.out.write(response)
    view.invalidate_cache()

def render_article(handler, path):
    # Handle precomputed legacy aliases
    # TODO: Use hash for case-insensitive lookup
    for alias in legacy_aliases.redirects:
        if path.lower() == alias.lower():
            self.redirect(legacy_aliases.redirects[alias])
            return

    # Test if client prefers JSON, so we can do fast-path cache if not.  Since the 
    # cache key does not include content-type (maybe it should?) We have to check 
    # this manually so that a cached HTML response isn't rendered when the client 
    # actually wanted JSON.
    json_type = 'application/json'
    client_wants_json = ( json_type == handler.request.accept.first_match(
      ['text/html', 'application/xhtml+xml', json_type] ) )
    if not client_wants_json and view.render_if_cached( handler ) : return

    article = db.Query(models.blog.Article).filter('permalink =', path).get()

    if not article:
        # This lets you map arbitrary URL patterns like /node/3
        #  to article properties, e.g. 3 -> legacy_id property
        article = legacy_id_mapping(path, config.BLOG["legacy_blog_software"])
        if article and config.BLOG["legacy_entry_redirect"]:
            handler.redirect('/' + article.permalink)
            return
        else: # not found.  Could do --> handler.redirect('/404.html')
            handler.error(404)
            view.ViewPage(cache_time=36000).render(handler, 
                {'module_name': 'blog', 'handler_name': 'notfound'})
            return

    # Check if client is requesting javascript
    if client_wants_json:
        handler.response.headers['Content-Type'] = json_type
        handler.response.out.write(article.to_json())
        return
    else:
        two_columns = article.two_columns
        if two_columns is None:
            two_columns = article.is_big()
        allow_comments = article.allow_comments
        if allow_comments is None:
            age = (datetime.datetime.now() - article.published).days
            allow_comments = (age <= config.BLOG['days_can_comment'])
        title = "%s :: %s" %  ( article.title, config.BLOG['title'] )
        view.ViewPage().render(handler, { "two_columns": two_columns,
                               "allow_comments": allow_comments,
                               "article": article,
                               "title": title,
                               "taglist": ', '.join(article.tags),
                               "captcha": config.BLOG['recap_public_key'],
                               "use_gravatars": config.BLOG['use_gravatars']
        })


class NotFoundHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        view.ViewPage(cache_time=36000).render(self)

class UnauthorizedHandler(webapp.RequestHandler):
    def get(self):
        self.error(403)
        view.ViewPage(cache_time=36000).render(self)

class RootHandler(restful.Controller):
    def get(self):
        logging.debug("RootHandler#get")
        if view.render_if_cached( self ): return  # quick cache path
        view.ViewPage().render_query(
            self, 'articles', 
            db.Query(models.blog.Article). \
               filter('article_type =', 'blog entry').order('-published'))

    @authorized.role("admin")
    def post(self):
        logging.debug("RootHandler#post")
        process_article_submission(handler=self, article_type='article')

class ArticlesHandler(restful.Controller):
    def get(self):
        logging.debug("ArticlesHandler#get")
        if view.render_if_cached( self ) : return
        page = view.ViewPage()
        page.render_query(
            self, 'articles',
            db.Query(models.blog.Article). \
               filter('article_type =', 'article').order('title'),
            num_limit=20)

# Articles are off root url
class ArticleHandler(restful.Controller):
    def get(self, path):
        logging.debug("ArticleHandler#get on path (%s)", path)
        render_article(self, path)

    @restful.methods_via_query_allowed    
    def post(self, path):
        logging.debug('Comment for article: %s', path)
        article = db.Query(models.blog.Article).filter('permalink =', path).get()
        if article: process_comment_submission(self, article)
        else:
          logging.warning( 'No article found for comment %s', path )
          self.error(400)

    @authorized.role("admin")
    def put(self, path):
        logging.debug("ArticleHandler#put")
        process_article_edit(self, permalink = path)

    @authorized.role("admin")
    def delete(self, path):
        """
        By using DELETE on /Article, /Comment, /Tag, you can delete the first 
         entity of the desired kind.
        This is useful for writing utilities like clear_datastore.py.  
        """
        # TODO: Add DELETE for articles off root like blog entry DELETE.
        model_class = path.lower()
        logging.debug("ArticleHandler#delete on %s", path)

        def delete_entity(query):
            target = query.get()
            if target:
                if hasattr(target, 'title'):
                    title = target.title
                elif hasattr(target, 'name'):
                    title = target.name
                else:
                    title = ''
                logging.debug('Deleting %s %s', model_class, title)
                target.delete()
                self.response.out.write('Deleted %s %s' % (model_class, title))
                view.invalidate_cache()
            else:
                self.response.set_status(204, 'No more %s entities' % (model_class,))
                
        if model_class == 'article':
            query = models.blog.Article.all()
            delete_entity(query)
        elif model_class == 'comment':
            query = models.blog.Comment.all()
            delete_entity(query)
        elif model_class == 'tag':
            query = models.blog.Tag.all()
            delete_entity(query)
        else:
            article = db.Query(models.blog.Article). \
                         filter('permalink =', path).get()
            for key in article.tag_keys:
                db.get(key).counter.decrement()
            article.delete()
            view.invalidate_cache()
            restful.send_successful_response(self, "/")

# Blog entries are dated articles
class BlogEntryHandler(restful.Controller):
    def get(self, year, month, perm_stem):
        logging.debug("BlogEntryHandler#get for year %s, "
                      "month %s, and perm_link %s", 
                      year, month, perm_stem)
        render_article( self, '%s/%s/%s' % (year, month, perm_stem) )

    @restful.methods_via_query_allowed    
    def post(self, year, month, perm_stem):
        logging.debug("Adding comment for blog entry %s", self.request.path)
        permalink = '%s/%s/%s' % (year, month, perm_stem)
        article = db.Query(models.blog.Article). \
                     filter('permalink =', permalink).get()
        if article:
            process_comment_submission(self, article)
        else: # no article found for comment
            logging.warning("No article found for comment to %s", permalink)
            self.error(400)

    @authorized.role("admin")
    def put(self, year, month, perm_stem):
        logging.debug("BlogEntryHandler#put")
        process_article_edit(self, 
          permalink = '%s/%s/%s' % (year, month, perm_stem))

    @authorized.role("admin")
    def delete(self, year, month, perm_stem):
        permalink = year + '/' + month + '/' + perm_stem
        logging.debug("Deleting blog entry %s", permalink)
        article = db.Query(models.blog.Article). \
                     filter('permalink =', permalink).get()
        for key in article.tag_keys:
            db.get(key).counter.decrement()
        article.delete()
        view.invalidate_cache()
        restful.send_successful_response(self, "/")

class TagHandler(restful.Controller):
    def get(self, encoded_tag):
        if view.render_if_cached( self ) : return
        tag =  re.sub('(%25|%)(\d\d)', 
                      lambda cmatch: chr(string.atoi(cmatch.group(2), 16)),                 
                      encoded_tag)   # No urllib.unquote in AppEngine?
        view.ViewPage().render_query(
            self, 'articles', 
            db.Query(models.blog.Article).filter('tags =',        
                                                 tag).order('-published'), 
                                                {'tag': tag})

class SearchHandler(restful.Controller):
    def get(self):
        if view.render_if_cached( self ) : return
        from google.appengine.api import datastore_errors
        search_term = self.request.get("s")
        query_string = 's=' + urllib.quote_plus(search_term) + '&'
        page = view.ViewPage()
        try:
            page.render_query( self, 'articles', 
                models.blog.Article.all().search( search_term,
                    properties=['title','body'] ).order('-published'), 
                {'search_term': cgi.escape(search_term),
                    'query_string': query_string} )
        except datastore_errors.NeedIndexError:
            page.render(self, {'search_term': cgi.escape(search_term),
                               'search_error_message': """
                               Sorry, full-text searches are currently limited
                               to single words until a later AppEngine update.
                               """})

class YearHandler(restful.Controller):
    def get(self, year):
        logging.debug("YearHandler#get for year %s", year)
        start_date = datetime.datetime(string.atoi(year), 1, 1)
        end_date = datetime.datetime(string.atoi(year)+1, 1, 1)
        view.ViewPage().render_query(
            self, 'articles', 
            db.Query(models.blog.Article).order('-published'). \
               filter('published >=', start_date). \
               filter('published <', end_date), 
            {'title': 'Articles for ' + year, 'year': year})

class MonthHandler(restful.Controller):
    def get(self, year, month):
        logging.info("MonthHandler#get for year %s, month %s", year, month)
        iyear = string.atoi(year)
        imonth = string.atoi(month)
        start_date = datetime.datetime(iyear, imonth, 1)
        if imonth==12: iyear+=1 ; imonth=0
        end_date = datetime.datetime(iyear, imonth+1, 1)
        view.ViewPage().render_query( self, 'articles', 
            db.Query(models.blog.Article).order('-published'). \
               filter('published >=', start_date). \
               filter('published <', end_date), 
            {'title': 'Articles for ' + month + '/' + year, 
             'year': year, 'month': month} )

    @authorized.role("admin")
    def post(self, year, month):
        """ Add a blog entry. Since we are POSTing, the server handles 
            creation of the permalink url. """
        logging.debug("MonthHandler#post on date %s, %s", year, month)
        process_article_submission(handler=self, article_type='blog entry')
        
class AtomHandler(webapp.RequestHandler):
    def get(self):
        if self.request.path == config.BLOG['legacy_atom_url']:
            self.redirect(config.BLOG['master_atom_url'],permanent=True)
            return
        
        logging.debug("ATOM feed")
        self.response.headers['Content-Type'] = 'application/atom+xml'
        if view.render_if_cached( self ): return  # quick cache path

        articles = db.Query(models.blog.Article). \
                      filter('article_type =', 'blog entry'). \
                      order('-published').fetch(limit=10)
        updated = ''
        if articles: updated = articles[0].rfc3339_updated()
        
        try: full_content= self.request.params['full'] in ['1','true','True']
        except: full_content= False
        view.ViewPage().render(self, {"blog_updated_timestamp": updated, 
                           "articles": articles, "ext": "xml",
                           'full_content': full_content })

class SitemapHandler(webapp.RequestHandler):
  def get(self):
    logging.debug("Sending Sitemap")
    self.response.headers['Content-Type'] = 'text/xml'
    if view.render_if_cached( self ): return  # quick cache path
    articles = db.Query(models.blog.Article).order('-published').fetch(1000)
    if articles:
      view.ViewPage().render(self, {
          "articles": articles,
          "ext": "xml",
          "root_url": config.BLOG['root_url']
      })
