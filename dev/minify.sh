# Run this from your bloog project base directory prior to uploading your project.
# Note that the live version of bloog is configured to use minified versions of code so 
# if you forget to re-minify before updating your application you won't see changes made to 
# CSS and JS files.
dev/scripts/cssmin.py static/default/style.css > static/default/style-min.css
dev/scripts/cssmin.py static/default/editor.css > static/default/editor-min.css

dev/scripts/jsmin.py static/default/js/bloog_base.js > static/default/js/bloog_base-min.js
dev/scripts/jsmin.py static/default/js/bloog_admin.js > static/default/js/bloog_admin-min.js
dev/scripts/jsmin.py static/default/js/bloog_comments.js > static/default/js/bloog_comments-min.js