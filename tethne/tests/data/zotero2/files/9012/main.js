
function redirect(targ,selObj,restore) {
    eval(targ + ".location='" + selObj.options[selObj.selectedIndex].value + "'");
    if (restore) selObj.selectedIndex=0;
}

function prepareErrorLinks() {
    if( ! document.getElementsByTagName ) return false;
    if( ! document.getElementById ) return false;
    if( ! document.getElementById( "validationerror" ) ) return false;
    var errorLinks = document.getElementById( "validationerror" ).getElementsByTagName( "a" );
    for( var i=0; i < errorLinks.length; i++ ) {
        errorLinks[i].onclick = function() {
            var objectId = this.href.substr( this.href.indexOf( "#" ) + 1 );
            if( document.getElementById(objectId) ) {
                document.getElementById(objectId).focus();
            }
        }
    }
}

window.onload = prepareErrorLinks;

var supported = ( document.layers || document.getElementById || document.all );

function encrypt(part1,part2,part3) {
    var all= 'mai'+'lto:'+part1+"@"+part2;
    if( part3 ) all += '?Sub'+'ject='+part3; document.location.href=eval('"'+all+'"');
}

function toggle_display( id ) {
    if( supported ) {
        if( document.layers && document.layers[id] ) {
            document.layers[id].display = ( document.layers[id].display == 'block' ? 'none' : 'block' );
        } else if( document.getElementById && document.getElementById(id) ) {
            document.getElementById(id).style.display = ( document.getElementById(id).style.display == 'block' ? 'none' : 'block' );
        } else if( document.all && document.all[id] ) {
            document.all[id].style.display = ( document.all[id].style.display == 'block' ? 'none' : 'block' );
        }
    }
}

function hide( id ) {
    if( supported ) {
        if( document.layers && document.layers[id] ) {
            document.layers[id].display = 'none';
        } else if( document.getElementById && document.getElementById(id) ) {
            document.getElementById(id).style.display = 'none';
        } else if( document.all && document.all[id] ) {
            document.all[id].style.display = 'none';
        }
    }
}

function unhide( id, display ) {
    // Default to display at block level
    if( ! display ) display = 'block';

    if( supported ) {
        // As IE does not support table-row, translate it to block
        if( navigator.appName == 'Microsoft Internet Explorer' && display == 'table-row' ) display = 'block';

        if( document.layers && document.layers[id] ) {
            document.layers[id].display = display;
        } else if( document.getElementById && document.getElementById(id) ) {
            document.getElementById(id).style.display = display;
        } else if( document.all && document.all[id] ) {
            document.all[id].style.display = display;
        }
    }
}

function visible( id ) {
     if( supported ) {
         if( document.layers && document.layers[id] ) {
             if( document.layers[id].display == 'none' ) return 0;
         } else if( document.getElementById && document.getElementById(id) ) {
             if( document.getElementById(id).style.display == 'none' ) return 0;
         } else if( document.all && document.all[id] ) {
             if( document.all[id].style.display == 'none' ) return 0;
         }
         return 1;
    }
    return 0;
}

function removeSpaces(string) {
     var tstring = "";
     string = '' + string;
     splitstring = string.split(" ");
     for(i = 0; i < splitstring.length; i++) tstring += splitstring[i];
     return tstring;
}

var selectItems = new Object();

function setOptions( listname, selectedItem, optionList ) {
     optionList.options.length = 0;
     optionList[0] = new Option( "Please select", "", true, false );

     if( selectItems[listname][selectedItem] ) {
        var newList = selectItems[listname][selectedItem];
        if( selectedItem != "" ) {
            for( var i = 0; i < newList.length; i++ ) {
                optionList.options[i+1] = new Option( newList[i].text, newList[i].value ? newList[i].value : newList[i].text );
            }
        }
    }
}

// Return the absolute Y position of an element on a page (from the top of the page, NOT visible screen)
function findPos(obj) {
        var curtop = 0;
        var bodyBorder=-document.body.offsetTop||document.body.clientTop;
        if (navigator.userAgent.indexOf("MSIE")!=-1) { curtop-=8 } 
        if (obj.offsetParent) {
                do {
                        curtop += obj.offsetTop;
                } while (obj = obj.offsetParent);
        }
        return curtop+bodyBorder;
}

// Update the floating help window. Leave htext blank to hide again.
function help_window(htext,field){
 var hw = document.getElementById("help_window");
 if(hw != undefined ){
   if(htext == ''){
     hw.className="hidden";
   } else {
        hw.innerHTML=htext;
        hw.className="help_window";
        hw.style.top=findPos(field)+"px";
   }
 }
}

//Archive list interactivity functions
var tick_archive=new Array("Humanities", "Law", "Medicine", "Science", "Social Sciences");
var tick_archive_x=new Array(true, true, true, true, true);
var tick_year=new Array();
var tick_year_x=new Array();
var tick_status=new Array("I", "E", "L");
var tick_status_x=new Array(true, true, true);
var line_id=new Array();
var line_archives=new Array();
var line_year_joined=new Array();
var line_status=new Array();
var year_count=-1;
var line_count=-1;

function add_year(year_to_add) {
  year_count+=1;
  tick_year[year_count]=year_to_add;
  tick_year_x[year_count]=true;
}

function filter() {
  for(var i=0; i<=line_count; i++) {
    var ok="";
	for(var j=0; j<tick_archive.length; j++) {
	  var s=line_archives[i].split(", ");
	  for(var a=0; a<s.length; a++) {
		if((s[a] == tick_archive[j]) && (tick_archive_x[j] == true)) { ok="a"; }
	  }
	}
	for(var j=0; j<tick_year.length; j++) {
	  if((line_year_joined[i] == tick_year[j]) && (tick_year_x[j] == true)) { ok+="y"; }
	} 
	for(var j=0; j<tick_status.length; j++) {
	  if((line_status[i] == tick_status[j]) && (tick_status_x[j] == true)) { ok+="s"; }
	}
	var r=document.getElementById("row"+line_id[i]);
	if(ok == "ays") {
		if(navigator.appName == 'Microsoft Internet Explorer') { 
			r.style.display = 'block';
		} else {
			r.style.display = 'table-row';
		}
	} else {
	  r.style.display="none"; 
	}
  }
}


function tickbox_change(tickbox) {
  var name=tickbox.name;
  var value=tickbox.value;
  var checked=tickbox.checked;
  switch(name) {
  	case "Archive": tick_archive_x[value]=checked; break;
	case "Year"   : tick_year_x[value]=checked; break;
	case "Status" : tick_status_x[value]=checked;
  }
  filter();
}

function archive_line(id, archives, year_joined, status) {
  line_count++;
  line_id[line_count]=id;
  line_archives[line_count]=archives;
  line_year_joined[line_count]=year_joined;
  line_status[line_count]=status;
}

//Site help page
var helpC = new Array();
var helpQ = new Array();
var helpA = new Array();
var helpK = new Array();
var xmlDoc;

function loadXML() {
try //Internet Explorer
  {
  xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
  }
catch(e)
  {
  try //Firefox, Mozilla, Opera, etc.
    {
    xmlDoc=document.implementation.createDocument("","",null);
    }
  catch(e)
    {
    alert(e.message);
    return;
    }
  }
  xmlDoc.async=false;
  xmlDoc.load("/resource/xml/qa.xml");
  var i=0;
  for(var c=0; c<xmlDoc.getElementsByTagName("category").length; c++) {
    var category=xmlDoc.getElementsByTagName("category")[c];
	for(var q=0; q<category.getElementsByTagName("question").length; q++) {
      var question=category.getElementsByTagName("question")[q];
	  helpC[helpC.length]=category.getElementsByTagName("title")[0].childNodes[0].nodeValue;
	  helpQ[helpQ.length]=question.getElementsByTagName("text")[0].childNodes[0].nodeValue
	  try {
	  helpK[helpK.length]=" "+question.getElementsByTagName("text")[0].childNodes[0].nodeValue+
	    " "+question.getElementsByTagName("keywords")[0].childNodes[0].nodeValue+" ";
	  } catch(e) {}
	  helpA[helpA.length]=question.getElementsByTagName("answer")[0].childNodes[0].nodeValue;
	}
  }
}

function searchHelp() {
  var keywords=document.getElementById("keywords").value;
  if(keywords.length>0) {
    var keyword=keywords.split(" ");
	//score keyword search results;
    var scores = new Array();
	var qid = new Array();
	for(var qa=0; qa<helpK.length; qa++) {
	   scores[qa]=0;
	   for(var k=0; k<keyword.length; k++) {
              if(keyword[k].length > 3) {
	         if(helpK[qa].toLowerCase().match(keyword[k])) {
		  scores[qa]+=1;
		  qid[qa]=qa;
	 	 }
              }
	   }
	}
	//sort results by score
	for(var s1=0; s1<scores.length; s1++) {
	  for(var s2=0; s2<scores.length; s2++) {
	    if(scores[s1]>scores[s2]) {
	      var temp_score=scores[s1];
		  var temp_qid=qid[s1];
		  scores[s1]=scores[s2];
		  qid[s1]=qid[s2];
		  scores[s2]=temp_score;
		  qid[s2]=temp_qid;
		}
	  }
	}
	//build results and display
	var results="";
	for(var qa=0; qa<(qid.length<10 ? qid.length : 9); qa++) {
	  if(scores[qa]>0) {
	    results+="<p><strong><a href=\"javascript:toggle('q"+qa+"');\">"+helpQ[qid[qa]]+"</a></strong><br />";
		results+='<div id="q'+qa+'" style="display:none">'+helpA[qid[qa]]+'<br /><br /></div></p>';
	  }
	}
	if(results==0) { 
	  results="<p>We didn't find any answers for your question.</p>";
	}
	results+="<p>Can't find what you're looking for? <a href=\"javascript:show('contact');\">Contact us</a></p>";
	document.getElementById("qa_results").innerHTML=results;
  }
}

function categoryList() {
  var lastVal="";
  for(var c=0; c<helpC.length; c++) {
    if(helpC[c]!=lastVal) {
	  document.write("<option value=\""+helpC[c]+"\">"+helpC[c]+"</option>");
	  lastVal=helpC[c];
	}
  }
}

function browseQuestions(question) {
  var results="";
  if(question!="...") {
	for(var c=0; c<helpC.length; c++) {
	  if(helpC[c]==question) {
	    results+="<p><strong><a href=\"javascript:toggle('b"+c+"');\">"+helpQ[c]+"</a></strong><br />";
		results+='<div id="b'+c+'" style="display:none">'+helpA[c]+'<br /><br /></div></p>';
	  }
	}
  }
  document.getElementById("browse_results").innerHTML=results;
}

function toggle(divID) {
  var e=document.getElementById(divID);
  e.style.display=(e.style.display=="none"?"block":"none");
}

function show(tab) {
  var showhideTabs = new Array("ask", "browse", "contact");
  for(var a=0; a<showhideTabs.length; a++) {
    document.getElementById(showhideTabs[a]).style.display=(tab==showhideTabs[a]?"block":"none");
  }
}

//Cookie Policy Plugin Variables
// 31 Jan 2013 - The cookie policy plugin has been deployed using implied consent only.
// The scripts for explicit consent have not been fully tested.
// A switch to explicit consent will require full UAT testing of the fancybox scripts that have been
// ommitted from this implementation.
var oupcookiepolicy_siteid = 'journals';	  			// the website id 	
var oupcookiepolicy_messagetype = 'implied';				// type of alert message e.g, implied / explicit
var oupcookiepolicy_preferredlanguage = 'en';				// preferred language of the website
var oupcookiepolicy_impliedmessageclass = 'cookiepolicyimplied';	// the css class for implied alert message
var oupcookiepolicy_documentroot='/';	  				// the document root the cookie is set to

function linkNewWin(jQEl) {
	var id = jQEl.attr("id");
	var targetName = "_blank";
	var config = null;
	if ((id != undefined) && id && !(id == '') &&
		!(gSiteOptions.openWindowDetails == undefined)) {
		var newLinkOptions = gSiteOptions.openWindowDetails[id];
		if ((newLinkOptions != undefined) && newLinkOptions) {
			var overrideTarget = newLinkOptions.target;
			var overrideConfig = newLinkOptions.config;
			if ((overrideTarget != undefined) && overrideTarget && (overrideTarget.length > 0)) {
				targetName = overrideTarget;
			}
			if ((overrideConfig != undefined) && overrideConfig && (overrideConfig.length > 0)) {
				config = overrideConfig;
			}
		}
	}
	var origTitle = jQEl.attr("title");
	var newTitle = '';
	if ((origTitle == undefined) || (!origTitle)) {
		origTitle = '';
	}
	else {
		newTitle = origTitle + ' ';
	}
	newTitle += '[opens in a new window]';
	jQEl.attr("target", targetName).attr("title", newTitle);
	if (config != null) {
		jQEl.click(function() {
			window.open(jQEl.attr("href"), targetName, config);
			return false;
		});
	}
}
