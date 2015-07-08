var OUP_AD_SIZE = function() {
    var TIMER_MAX = 40;   // 40 * 250ms = 10s
    var SIZES = { "default": { width:160, height:90 },
		"Top":	{ width:728, height:120 },
		"Top1":	{ width:728, height:120 },
		"Position1":	{ width:728, height:90 },
		"Bottom":	{ width:728, height:90 },
		"Right1":	{ width:160, height:630 }
	};
    
    return {
        addLoadEvent: function(func) { 
            if (window.addEventListener) {
                window.addEventListener('DOMContentLoaded', func, false);
            } else {
                // Thanks to Simon Willison, http://simonwillison.net/
                // Creates a "chain" of windows.onload calls where none so far exists.
                var oldonload = window.onload; 
                if (typeof window.onload != 'function') { 
                    window.onload = func; 
                } else { 
                    window.onload = function() { 
                      if (oldonload) { 
                        oldonload(); 
                      } 
                      func(); 
                    } 
                } 
            }
        },
        
        checkContent: function (iframe) {
                // this function makes visible non-zero adverts
	    var slot = iframe.src.replace(/.*p=/i,'').replace(/&.*/,'');
            if (!iframe.sizeinfo){
		iframe.sizeinfo = {timer_tocks:0, last_height: iframe.height, last_width: iframe.width };
		if(iframe.sizeinfo.last_height==0) iframe.sizeinfo.last_height= SIZES[slot].height || SIZES["default"].height;
		if(iframe.sizeinfo.last_width==0) iframe.sizeinfo.last_width= SIZES[slot].width || SIZES["default"].width;
            }
            var newwidth=0;
            var body;
            iframe.height=0;
            iframe.width=0;
            var newheight=0;
            var newwidth=0;
            var body;
	    var P = iframe.parentElement;
	    if(!P){
		P=iframe.parentNode;
	    }
            var currently = P.className;
	    P.className="ad_working";
            try {
                if (document.frames) { // Works for IE5+
                    body = document.frames[iframe.id].document.body;
                    newheight = body.scrollHeight || body.firstChild.scrollHeight;
                    newwidth = body.scrollWidth || body.firstChild.scrollWidth;
                } else if (iframe.contentWindow && iframe.contentWindow.scrollMaxX) {
                  // Firefox et al
                        newheight = iframe.contentWindow.scrollMaxY;
                        newwidth = iframe.contentWindow.scrollMaxX;
                } else if (iframe.contentDocument && iframe.contentDocument.body) {
                  // Chrome and others
                            newheight = iframe.contentDocument.body.scrollHeight;
                            newwidth = iframe.contentDocument.body.scrollWidth;
                }
                if(newheight > 25 && newwidth > 25){
                        currently="ad_unhidden";
                }
             }
	     catch(err) {
			// alert("error with sizing");
	     }
             iframe.height=iframe.sizeinfo.last_height;
             iframe.width=iframe.sizeinfo.last_width;
             P.className=currently;
             if(currently == 'ad_unhidden'){
			// done!
	     } else {
                    iframe.sizeinfo.timer_tocks += 1;
                    if (iframe.sizeinfo.timer_tocks < TIMER_MAX) {
                        // Reschedule this event to happen again in 250ms
                        var t = setTimeout(function(){OUP_AD_SIZE.checkContent(iframe);}, 250);
                    }
             }
        },

        checkOldContent: function (iframe) {
            // This function resizes an IFrame object
            // to fit its content.
            // For IE5+ The IFrame tag must have a unique ID attribute.
            //
            // Add a 'sizeinfo' object into the iframe, so we can handle more than one iframe in the 
            // document.
            if (!iframe.sizeinfo) iframe.sizeinfo = {timer_tocks:0, last_height: 0, last_width:0};
            
            var newheight=0;
            var newwidth=0;
            var body;
            var Tag = iframe.id;
            // iframe.height=0; // Set to zero, this will force the scrollwidths/heights to
            // iframe.width=0;  // reflect the whole document width.
            try {
                if (document.frames) { // Works for IE5+
                    body = document.frames[iframe.id].document.body;
                    newheight = body.scrollHeight || body.firstChild.scrollHeight;
                    newwidth = body.scrollWidth || body.firstChild.scrollWidth;
                } else if (iframe.contentWindow && iframe.contentWindow.scrollMaxX)
                    { // Firefox et al
                        newheight = iframe.contentWindow.scrollMaxY;
                        newwidth = iframe.contentWindow.scrollMaxX;
                    } else if (iframe.contentDocument && iframe.contentDocument.body)
                        { // Chrome and others
                            newheight = iframe.contentDocument.body.scrollHeight;
                            newwidth = iframe.contentDocument.body.scrollWidth;
                        }
                //
                if(newheight < 50){newheight=0;}
//		if(newheight > 60 && (Tag.match("top") || Tag.match("bottom") )){ newheight=60; }
//		if(newheight > 600 && Tag.match("right") ){ newheight=600; }
                if(newwidth < 50){newwidth=0;}
//		if(newwidth > 468 && (Tag.match("top") || Tag.match("bottom")) ){ newwidth=468; }
//		if(newwidth > 160 && Tag.match("right") ){ newwidth=160; }
                if ((newheight > iframe.sizeinfo.last_height) || (newwidth > iframe.sizeinfo.last_width)) {
                    // Its changed in size, so resize iframe and reset timer
                    iframe.height=newheight;
                    iframe.width=newwidth;
                    iframe.sizeinfo.last_width = newwidth;
                    iframe.sizeinfo.last_height = newheight;
		    if(newwidth>=160 && newheight >=60){
			    iframe.sizeinfo.timer_tocks = TIMER_MAX;
		    }
                } else {
                  if(iframe.sizeinfo.last_height>0){
                    iframe.height=iframe.sizeinfo.last_height; // restore this
                    iframe.width=iframe.sizeinfo.last_width;   //
                  }
                };
                var e = document.createElement('div');
                e.innerHTML = ""+iframe.sizeinfo.timer_tocks+" W"+iframe.width+"*H"+iframe.height;
                iframe.parentElement.appendChild(e);

            }
            catch(err) {
                // Theres been some error; maybe DOM isnt ready so just reset and carry on later
                if(iframe.sizeinfo.last_height>0){
                 iframe.height=iframe.sizeinfo.last_height; // restore this
                 iframe.width=iframe.sizeinfo.last_width;   //
                }
            };

            iframe.sizeinfo.timer_tocks += 1;
            if (iframe.sizeinfo.timer_tocks < TIMER_MAX) {
                // Reschedule this event to happen again in 250ms
                var t = setTimeout(function(x){ OUP_AD_SIZE.checkContent(x);} , 250, iframe);
            };// else alert("timed out!");
        }, 
        
        find_iframes: function() {
            // This function is for the benefit of IE. It looks for iframes that need resizing.
            var iframes = document.getElementsByTagName('iframe');
            for (var i=0; i<iframes.length; i++) {
                var iframe = iframes[i], classlist;
                if (iframe.classList) { //Firefox, Chrome
                    classlist = iframe.classList;
                } else { //IE...
                    classlist = iframe.className.split(' ');
                };
                for (var j=0; j<classlist.length; j++) {
                    if (classlist[j] == 'resize_ad') {
                        OUP_AD_SIZE.checkContent(iframe);
                        break;
                    };
                };
            };
        }
        
    }
}();
// Look for the iframes in the menu when the page has finished loading
// Call after an itsy-bitsy delay to allow the DOM to catch up on IE/Firefox.
OUP_AD_SIZE.addLoadEvent(function(){ setTimeout(OUP_AD_SIZE.find_iframes, 100);});

