/**
 The MIT License
 
 Copyright (c) 2008 William T. Katz
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to 
 deal in the Software without restriction, including without limitation 
 the rights to use, copy, modify, merge, publish, distribute, sublicense, 
 and/or sell copies of the Software, and to permit persons to whom the 
 Software is furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
 DEALINGS IN THE SOFTWARE.
**/
YAHOO.namespace('bloog');

YAHOO.bloog.handleSuccess = function (o) {
    var response = o.responseText;
    response = response.split("<!")[0];
    // Redirect to this new URL -- For some reason this has problems in Safari
    window.location.href = response;
};
YAHOO.bloog.handleFailure = function (o) {
    alert("Submission failed: " + o.status);
};
YAHOO.bloog.handleCancel = function () {
    this.cancel();
};


Ojay.changeAlias('$$'); // like Prototype.js
$ = function(id) { return Ojay.byId(id).node; };

Ojay.onDOMReady(function() {
  $$('#archiveLink').on('click', function(elem,e) {
    e.stopEvent();
    var archives = $('archives');
    archives.style.display = ( archives.style.display == 'none' ) ?
      archives.style.display = 'block' : archives.style.display= 'none';
  });
});

