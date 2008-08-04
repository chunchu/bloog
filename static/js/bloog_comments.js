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

YAHOO.bloog.initComments = function() {

    var showRTE = function(e) {
        YAHOO.bloog.commentEditor.setEditorHTML('<p>Comment goes here</p>');
        YAHOO.bloog.commentDialog.show();
    }

    var handleSubmit = function() {
        var html = YAHOO.bloog.commentEditor.get('element').value;
        var name = YAHOO.util.Dom.get('commentName').value;
        var email = YAHOO.util.Dom.get('commentEmail').value;
        var homepage = YAHOO.util.Dom.get('commentHomepage').value;
        var title = YAHOO.util.Dom.get('commentTitle').value;
        // Key needs to be transmitted because fragment doesn't seem to make
        //  it through webob request object.
        var postData = 'key=' + encodeURIComponent(YAHOO.bloog.action) + '&' +
                        'name=' + encodeURIComponent(name) + '&' +
                        'email=' + encodeURIComponent(email) + '&' +
                        'homepage=' + encodeURIComponent(homepage) + '&' +
                        'title=' + encodeURIComponent(title) + '&' +
                        'body=' + encodeURIComponent(html);
        var cObj = YAHOO.util.Connect.asyncRequest(
            'POST', 
            YAHOO.bloog.action, 
            { success: YAHOO.bloog.handleSuccess, 
              failure: YAHOO.bloog.handleFailure },
            postData);
    }

    YAHOO.bloog.commentDialog = new YAHOO.widget.Dialog(
        "commentDialog", {
            width: "550px",
            fixedcenter: true,
            visible: false,
            modal: true,
            constraintoviewpoint: true,
            buttons: [ { text: "Submit", handler: handleSubmit, 
                         isDefault:true },
                       { text: "Cancel", handler: YAHOO.bloog.handleCancel } ]
        });
    YAHOO.bloog.commentDialog.validate = function () {
        var data = this.getData();
        if (data.commentName == "") {
            alert("Please enter your name");
            return false;
        }
        return true;
    }
    YAHOO.bloog.commentDialog.callback = { success: YAHOO.bloog.handleSuccess, 
                                           failure: YAHOO.bloog.handleFailure };
    YAHOO.bloog.commentDialog.render();

    YAHOO.bloog.commentEditor = new YAHOO.widget.Editor(
        'commentBody', {
            height: '300px',
            width: '500px',
            dompath: true,
            animate: true
        });
    YAHOO.bloog.commentEditor.render();

    // Use event bubbling so we don't have to attach listeners to each reply
    Ojay('div#comments_wrapper').on('click', Ojay.delegateEvent({
        'a.replybtn': function(link, e) {
            //e.stopDefault();
            YAHOO.bloog.action = link.node.href;
            showRTE();
        }
    }))
}

YAHOO.util.Event.onDOMReady(YAHOO.bloog.initComments);