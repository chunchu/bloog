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

YAHOO.bloog.initAdmin = function() {

    var showRTE = function(e) {
        var hdr = $$('div#postDialog div.hd');
        YAHOO.bloog.http = {};
        switch (this.id) {
            case 'newarticle':
                hdr.setContent('Submit Article');
                YAHOO.bloog.http.action = '/';
                YAHOO.bloog.http.verb = 'POST';
                YAHOO.bloog.editor.setEditorHTML('<p>Article goes here</p>');
                YAHOO.bloog.postDialog.render();
                YAHOO.bloog.postDialog.show();
                break;
            case 'newblog':
                hdr.setContent('Submit Blog Entry');
                var today = new Date();
                var month = today.getMonth() + 1;
                var year = today.getFullYear();
                YAHOO.bloog.http.action = "/" + year + "/" + month;
                YAHOO.bloog.http.verb = 'POST';
                YAHOO.bloog.editor.setEditorHTML('<p>Blog entry goes here</p>');
                YAHOO.bloog.postDialog.render();
                YAHOO.bloog.postDialog.show();
                break;
            case 'editbtn':
                hdr.setContent('Submit Edit');
                YAHOO.bloog.http.action = '?_method=PUT';
                YAHOO.bloog.http.verb = 'POST';
                // Get the current article content and populate the dialog
                YAHOO.util.Connect.initHeader('Accept', 'application/json');
                YAHOO.util.Connect.asyncRequest('GET', '#', {
                    success: YAHOO.bloog.populateDialog,
                    failure: YAHOO.bloog.handleFailure
                }, null);
                break;
        }
    };

    YAHOO.bloog.populateDialog = function(o) {
        var article = o.responseText.parseJSON();
        $("postTitle").value = article.title;
        if (article.tags) $("postTags").value = article.tags.join(', ');
        $("postDate").value = article.published;
        $('legacyID').value = article.legacy_id;
        YAHOO.bloog.editor.setEditorHTML( article.body );
        YAHOO.bloog.postDialog.render();
        YAHOO.bloog.postDialog.show();
    };

    YAHOO.bloog.formatDate = function( date ) {
      var dtFormat = '';
      dtFormat += date.getFullYear() + '-' ;
      var v = (date.getMonth()+1);
      dtFormat += (v<10?'0':'') + v + '-' ;
      v = date.getDate();
      dtFormat += (v<10?'0':'') + v + ' ' ;
      v = date.getHours();
      dtFormat += (v<10?'0':'') + v + ':' ;
      v = date.getMinutes();
      dtFormat += (v<10?'0':'') + v + ':' ;
      v = date.getSeconds();
      dtFormat += (v<10?'0':'') + v;
      return dtFormat;
    };
    
    var handleSubmit = function() {
        YAHOO.bloog.editor.saveHTML();
        var html = YAHOO.bloog.editor.getEditorHTML();
        var postData = $$.Forms.getQueryString($('postDialogForm'));
        var cObj = YAHOO.util.Connect.asyncRequest(
            YAHOO.bloog.http.verb, 
            YAHOO.bloog.http.action, 
            { success: YAHOO.bloog.handleSuccess, 
              failure: YAHOO.bloog.handleFailure },
            postData);
    };

    YAHOO.bloog.postDialog = new YAHOO.widget.Dialog(
        "postDialog", {
            width: "520px",
            fixedcenter: true,
            visible: false,
            modal: true,
            constraintoviewpoint: true,
            buttons: [ { text: "Submit", handler: handleSubmit, 
                         isDefault:true },
                       { text: "Cancel", handler: YAHOO.bloog.handleCancel } ]
        });

    YAHOO.bloog.postDialog.validate = function() {
        var data = this.getData();
        if (data.postTitle == "") {
            alert("Please enter a title for this post.");
            return false;
        }
        return true;
    }
    YAHOO.bloog.postDialog.callback = { success: YAHOO.bloog.handleSuccess, 
                                        failure: YAHOO.bloog.handleFailure };

    YAHOO.bloog.editor = new YAHOO.widget.Editor('postBody', {
        height: '250px',
        width: '500px',
        dompath: true,
        animate: true,
        toolbar: {
            titlebar: '',
            draggable: true,
            buttonType: 'advanced',
            buttons: [
                { group: 'textstyle', label: 'Font Style',
                    buttons: [
                        { type: 'push', label: 'Bold CTRL + SHIFT + B', value: 'bold' },
                        { type: 'push', label: 'Italic CTRL + SHIFT + I', value: 'italic' },
                        { type: 'push', label: 'Underline CTRL + SHIFT + U', value: 'underline' },
                        { type: 'push', label: 'Code CTRL + SHIFT + C', value: 'code' },
                        { type: 'separator' },
                        { type: 'push', label: 'Subscript', value: 'subscript', disabled: true },
                        { type: 'push', label: 'Superscript', value: 'superscript', disabled: true },
                        { type: 'separator' },
                        { type: 'color', label: 'Font Color', value: 'forecolor', disabled: true },
                        { type: 'color', label: 'Background Color', value: 'backcolor', disabled: true },
                        { type: 'separator' },
                        { type: 'push', label: 'Remove Formatting', value: 'removeformat', disabled: true },
                        { type: 'push', label: 'Show/Hide Hidden Elements', value: 'hiddenelements' }
                    ]
                },
                { type: 'separator' },
                { group: 'alignment', label: 'Alignment',
                    buttons: [
                        { type: 'push', label: 'Align Left CTRL + SHIFT + [', value: 'justifyleft' },
                        { type: 'push', label: 'Align Center CTRL + SHIFT + |', value: 'justifycenter' },
                        { type: 'push', label: 'Align Right CTRL + SHIFT + ]', value: 'justifyright' },
                        { type: 'push', label: 'Justify', value: 'justifyfull' }
                    ]
                },
                { type: 'separator' },
                { group: 'parastyle', label: 'Paragraph Style',
                    buttons: [
                    { type: 'select', label: 'Normal', value: 'heading', disabled: true,
                        menu: [
                            { text: 'Normal', value: 'none', checked: true },
                            { text: 'Header 1', value: 'h1' },
                            { text: 'Header 2', value: 'h2' },
                            { text: 'Header 3', value: 'h3' },
                            { text: 'Header 4', value: 'h4' }
                        ]
                    }
                    ]
                },
                { type: 'separator' },
                { group: 'indentlist', label: 'Indenting',
                    buttons: [
                        { type: 'push', label: 'Indent', value: 'indent', disabled: true },
                        { type: 'push', label: 'Outdent', value: 'outdent', disabled: true },
                        { type: 'push', label: 'Create an Unordered List', value: 'insertunorderedlist' },
                        { type: 'push', label: 'Create an Ordered List', value: 'insertorderedlist' }
                    ]
                },
                { type: 'separator' },
                { group: 'insertcode', label: 'Insert Code',
                    buttons: [
                    { type: 'push', label: 'Python', value: 'python', disabled: false },
                    { type: 'push', label: 'Javascript', value: 'js', disabled: false },
                    { type: 'push', label: 'Groovy', value: 'groovy', disabled: false },
                    { type: 'push', label: 'XML/HTML', value: 'html', disabled: false },
                    { type: 'push', label: 'CSS', value: 'css', disabled: false }
                    ]
                },
                { type: 'separator' },
                { group: 'insertitem', label: 'Insert Item',
                    buttons: [
                        { type: 'push', label: 'HTML Link CTRL + SHIFT + L', value: 'createlink', disabled: true },
                        { type: 'push', label: 'Insert Image', value: 'insertimage' },
                        { type: 'push', label: 'Upload Image', value: 'uploadimage' },
                        { type: 'push', label: 'Edit raw HTML', value: 'editraw' }
                    ]
                }
            ]
        }
    });

    YAHOO.bloog.editor.on('toolbarLoaded', function() {

      this.toolbar.on('pythonClick', function(o) {
          this.execCommand('inserthtml', '<p></p><pre class="brush: python"># Python code here</pre><p></p>');
      }, this, true);
      this.toolbar.on('jsClick', function(o) {
          this.execCommand('inserthtml', '<p></p><pre class="brush: js">// Javascript code here</pre><p></p>');
      }, this, true);
      this.toolbar.on('groovyClick', function(o) {
          this.execCommand('inserthtml', '<p></p><pre class="brush: groovy">// Groovy code here</pre><p></p>');
      }, this, true);
      this.toolbar.on('cssClick', function(o) {
          this.execCommand('inserthtml', '<p></p><pre class="brush: css">/* CSS code here */</pre><p></p>');
      }, this, true);
      this.toolbar.on('htmlClick', function(o) {
          this.execCommand('inserthtml', '<p></p><pre class="brush: html">&lt;!-- XML/HTML code here --></pre><p></p>');
      }, this, true);
        
      this.toolbar.on('codeClick', function() { this.execCommand('code'); } );
      this.cmd_code = function() {
        if ( this._hasSelection() ) {
          var code = this._createCurrentElement('code');
          this._selectNode(this.currentElement[0]);
        }
        else this.execCommand('inserthtml', '<code>&nbsp;</code>');
        return [true];
      };
      this.toolbar.on('uploadimageClick', function() { 
        // override insertimage handling to allow our own image uploader!
        YAHOO.bloog.uploadPanel.show();
      });
        
      //Setup the button to be enabled, disabled or selected
      this.on('afterNodeChange', function() {     
        if ( this._hasSelection() ) {
          this.toolbar.disableButton(this.toolbar.getButtonByValue('python'));
          this.toolbar.disableButton(this.toolbar.getButtonByValue('groovy'));
          this.toolbar.disableButton(this.toolbar.getButtonByValue('html'));
          this.toolbar.disableButton(this.toolbar.getButtonByValue('css'));
          this.toolbar.disableButton(this.toolbar.getButtonByValue('js'));
        }
        var el = this._getSelectedElement();
        if ( ! el ) return;
        var val;
        if ( el.tagName == 'CODE' ) val = 'code';
        el = Ojay(el);
        if ( el.hasClass('brush:') ) {
          if ( el.hasClass('html') ) val = 'html';
          else if ( el.hasClass('python') ) val = 'python';
          else if ( el.hasClass('groovy') ) val = 'groovy';
          else if ( el.hasClass('java') ) val = 'java';
          else if ( el.hasClass('css') ) val = 'css';
        }
        if ( ! val ) return;
        this.toolbar.selectButton(this.toolbar.getButtonByValue(val));
      },this,true);
      
      this.state = 'on';
      
      this.on('afterRender', function() {
        var wrapper = this.get('editor_wrapper');
        wrapper.appendChild(this.get('element'));
        this.addClass('editor-hidden');
        this.setStyle('width', '100%');
        this.setStyle('height', '100%');
        this.setStyle('visibility', '');
        this.setStyle('top', '');
        this.setStyle('left', '');
        this.setStyle('position', '');
      }, this, true);

      this.toolbar.on('editrawClick', function() {
        var ta = $$(this.get('element')),
        iframe = $$(this.get('iframe').get('element'));

        if (this.state == 'off') {
          this.state = 'on';
          this.toolbar.set('disabled', false);
          this.setEditorHTML(ta.node.value);
          if (!this.browser.ie) this._setDesignMode('on');
          iframe.removeClass('editor-hidden');
          ta.addClass('editor-hidden');
          this.show();
          this._focusWindow();
        } else {
          this.state = 'off';
          this.cleanHTML();
          //ta.node.value = this.getEditorHTML;
          iframe.addClass('editor-hidden');
          ta.removeClass('editor-hidden');
          this.toolbar.set('disabled', true);
          this.toolbar.getButtonByValue('editraw').set('disabled', false);
          this.toolbar.selectButton('editraw');
          this.dompath.innerHTML = 'Editing HTML Code';
          this.hide();
        }
        return false;
      }, this, true);
      
      this.on('cleanHTML', function(ev) { 
        this.get('element').value = ev.html; 
      }, this, true);

    }, YAHOO.bloog.editor, true);
    YAHOO.bloog.editor.render();
    
    YAHOO.util.Dom.setStyle( YAHOO.bloog.postDialog.element, 'display', 'none' );
    YAHOO.bloog.postDialog.beforeShowEvent.subscribe( function() {
        YAHOO.bloog.postDialog.element.style.display='block'; },
      YAHOO.bloog.postDialog, true );
    YAHOO.bloog.postDialog.hideEvent.subscribe( function() {
        YAHOO.bloog.postDialog.element.style.display= 'none'; },
      YAHOO.bloog.postDialog, true );
      
    YAHOO.bloog.postDialog.showEvent.subscribe(
        YAHOO.bloog.editor.show, YAHOO.bloog.editor, true );
    YAHOO.bloog.postDialog.hideEvent.subscribe(
        YAHOO.bloog.editor.hide, YAHOO.bloog.editor, true );
    
    YAHOO.bloog.calendar = new YAHOO.widget.Calendar( 'cal1', 
      "postDateContainer", {close:true, title:"Choose a Date"} );
    YAHOO.bloog.calendar.render();
    YAHOO.bloog.calendarCloseHandler = function() {
      YAHOO.bloog.calendar.hide();
    };
    YAHOO.bloog.dateSelectHandler = function() {
      var dt = YAHOO.bloog.calendar.getSelectedDates()[0];
      $("postDate").value = YAHOO.bloog.formatDate(dt);
      YAHOO.bloog.calendar.hide();
    };

    YAHOO.bloog.calendar.selectEvent.subscribe( 
      YAHOO.bloog.dateSelectHandler, YAHOO.bloog.calendar, true );
    YAHOO.util.Event.addListener( 'postDate', 'click', 
      YAHOO.bloog.calendar.show, YAHOO.bloog.calendar, true );

    YAHOO.bloog.uploadPanel = new YAHOO.widget.SimpleDialog( 'imageUpload', 
      {close:true, visible:false, fixedcenter:true, width:'20em', modal:true} );
    YAHOO.bloog.uploadPanel.setHeader("Image Upload");
    YAHOO.bloog.uploadPanel.render();
    
    var handleDelete = function() {
        var cObj = YAHOO.util.Connect.asyncRequest( 'DELETE', '#', 
            { success: YAHOO.bloog.handleSuccess, 
              failure: YAHOO.bloog.handleFailure }
        );
    };
    YAHOO.bloog.deleteDialog = new YAHOO.widget.SimpleDialog(
        "confirmDlg", {
            width: "20em",
            effect: { effect:YAHOO.widget.ContainerEffect.FADE, duration:0.25 },
            fixedcenter: true,
            modal: true,
            visible: false,
            draggable: false,
            buttons: [ { text: "Delete!", handler: handleDelete },
                       { text: "Cancel", 
                         handler: function () { this.hide(); },
                         isDefault: true } ]
        });
    YAHOO.bloog.deleteDialog.setHeader("Warning");
    YAHOO.bloog.deleteDialog.setBody("Are you sure you want to delete this post?");
    YAHOO.bloog.deleteDialog.render(document.body);
    
    YAHOO.util.Event.on("newarticle", "click", showRTE);
    YAHOO.util.Event.on("newblog", "click", showRTE);
    YAHOO.util.Event.on("editbtn", "click", showRTE);
    YAHOO.util.Event.on("deletebtn", "click", function (e) { YAHOO.bloog.deleteDialog.show(); });
    
    $$('#imageUploadForm').on('submit',function(form,e) {
      form = form.node;
      YAHOO.util.Connect.setForm(form, true);
      YAHOO.util.Connect.asyncRequest( 'POST', form.action, { 
          upload: function(xhr) {
            YAHOO.bloog.editor.execCommand('inserthtml', xhr.responseText );
          }
      });
      e.stopDefault();
    });
    
    $$('#moreOptionsLink').on('click',function(link,e) {
      var moreOptions = $('moreOptionsContainer');
      moreOptions.style.display = ( moreOptions.style.display== 'none' ? 
        'block' : 'none' );
      e.stopDefault();
    });
};

Ojay.onDOMReady( YAHOO.bloog.initAdmin );
