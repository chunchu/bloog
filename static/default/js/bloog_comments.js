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

    var showRTE = function(link) {
        $$('#commentDialog').removeClass('initialHide');
        YAHOO.bloog.commentEditor.setEditorHTML('<p>Enter your comments here.</p>');
        $('commentTitle').value = "Re: " + ( (link.hash.length > 1) ?
          $$(link.hash).descendants('.comment_meta .subject').node.innerHTML
          : $('blogtitle').innerHTML );
        if ( typeof( Recaptcha ) != 'undefined' ) // only loaded if not admin
          Recaptcha.create( $('recaptcha_pub_key').innerHTML, 
            'recaptcha_container', { theme: "clean" } );
        YAHOO.bloog.commentDialog.render();
        YAHOO.bloog.commentDialog.show();
        YAHOO.bloog.commentEditor.show();
    }

    var handleSuccess = function(parent_id,o) {
        console.debug("Parent id:", parent_id);
        var response = o.responseText;
        // Insert the comment into the appropriate place then hide dialog.
        if ( ! parent_id ) // Should be inserted at the bottom
            $$('#commentslist').insert(response, 'bottom');
        else $$('#' + parent_id).insert(response, 'after');

        var num_comments = String(Number($('num_comments').innerHTML) + 1);
        $$('#num_comments').setContent(num_comments);
        $$('#article .comments a').setContent(num_comments);
        YAHOO.bloog.commentEditor.hide();
        YAHOO.bloog.commentDialog.hide();

        $$(YAHOO.bloog.commentDialog.defaultHtmlButton) // re-enable submit btn
          .removeClass('yui-button-disabled')
          .descendants('button').set( { disabled : false } )
          .setContent("Submit!");
    }
    var handleFailure = function(o) {
        var msg = o.statusText ? o.statusText : 
          o.status ? o.status : "Unknown error: " + o;
        alert("Error saving your comment!\n" + msg );
        // re-enable submit btn in event of failure:
        $$(YAHOO.bloog.commentDialog.defaultHtmlButton)
          .removeClass('yui-button-disabled')
          .descendants('button').set( { disabled : false } )
          .setContent("Submit!");
    }
    var handleSubmit = function() {
        // disable submit button to prevent double submission:
        $$(YAHOO.bloog.commentDialog.defaultHtmlButton)
          .addClass('yui-button-disabled')
          .descendants('button').set( { disabled : true } )
          .setContent("Submitting...");
        try {
            YAHOO.bloog.commentEditor.saveHTML();
            var form = $('commentDialogForm')
            var postData = $$.Forms.getQueryString(form);
            var action = form.action.split('#'); //get parent ID if it exists
            var cObj = YAHOO.util.Connect.asyncRequest(
                'POST', action[0], 
                { success: handleSuccess.partial(action[1]), failure: handleFailure },
                postData );
        }
        catch( ex ) { handleFailure( ex ); }
    }
    
    YAHOO.bloog.commentDialog = new YAHOO.widget.Dialog(
        "commentDialog", {
            width: "520px",
            fixedcenter: true,
            visible: false,
            modal: true,
            constraintoviewpoint: true,
            buttons: [ { text: "Submit!", handler: handleSubmit, 
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
    };

    YAHOO.bloog.commentEditor = new YAHOO.widget.SimpleEditor(
        'commentBody', {
            height: '150px',
            width: '500px',
            dompath: false,
            animate: true,
            toolbar: {
                titlebar: '',
                buttons: [
                    { group: 'fontstyle', label: 'Font Style',
                        buttons: [
                            { type: 'push', label: 'Bold', value: 'bold' },
                            { type: 'push', label: 'Italic', value: 'italic' },
                            { type: 'push', label: 'Underline', value: 'underline' }
                        ]
                    },
                    { type: 'separator' },
                    { group: 'indentlist', label: 'Lists',
                        buttons: [ 
                            { type: 'push', label: 'Create an Unordered List', value: 'insertunorderedlist' }, 
                            { type: 'push', label: 'Create an Ordered List', value: 'insertorderedlist' } 
                        ]
                    },
                    { type: 'separator' },
                    { group: 'insertitem', label: 'Insert Item',
                        buttons: [ 
                            { type: 'push', label: 'HTML Link CTRL + SHIFT + L', value: 'createlink' }, 
                            { type: 'push', label: 'Insert Image', value: 'insertimage', disabled: true },
                            { type: 'push', label: 'Insert <pre> block', value: 'insertpre' }
                        ]
                    }
                ]
            }
        });
    YAHOO.bloog.commentEditor.render();
    YAHOO.bloog.commentDialog.showEvent.subscribe(YAHOO.bloog.commentEditor.show, YAHOO.bloog.commentEditor, true);
    YAHOO.bloog.commentDialog.hideEvent.subscribe(YAHOO.bloog.commentEditor.hide, YAHOO.bloog.commentEditor, true);
    
    YAHOO.bloog.commentEditor.on('toolbarLoaded', function() {
        this.toolbar.on('insertpreClick', function() {
            this.execCommand('inserthtml', '<pre># insert code here</pre><p></p>');
        }, YAHOO.bloog.commentEditor, true);
    });

    // Use event bubbling so we don't have to attach listeners to each reply
    $$('div#comments_wrapper').on('click', Ojay.delegateEvent({
        'a.replybtn': function(link, e) {
            e.stopDefault();
            $('commentDialogForm').action = link.node.href;
            //$('commentKey').value = link.node.href;
            showRTE(link.node);
        }
    }));

};

Ojay.onDOMReady(YAHOO.bloog.initComments);