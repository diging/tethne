var filterAbbrv ;
var pageUrl ;

onload=function(){
if (document.getElementsByClassName == undefined) {

document.getElementsByClassName = function(cl) {
var retnode = [];
var myclass = new RegExp('\\b'+cl+'\\b');
var elem = this.getElementsByTagName('*');
for (var i = 0; i < elem.length; i++) {
var classes = elem[i].className;
if (myclass.test(classes)) retnode.push(elem[i]);
}
return retnode;
}
}
}
onload();
function bn_setmetaAttrs(tag){
	
	var metas = document.getElementsByTagName("meta");
	if (!metas) return;
	
	for (var i = 0; i < metas.length; i++) {
		if (!metas[i]) return;
			if (metas[i].name == "citation_doi") {
				var tempMetaContent = metas[i].content;
				var tempUrl = location.href;
				var strLoc = Math.max(tempUrl.indexOf("://")+3,tempUrl.indexOf("intl-")+5);
				var tempUrl2 = tempUrl.substr(strLoc);
				if(BaynoteAPI.isNotEmpty(tempMetaContent)) {
					tag.docAttrs.doi = tempMetaContent;
					tag.docAttrs.journal_abbr = tempUrl2.substr(0,tempUrl2.indexOf(".oxfordjournals"));
					tag.docAttrs.new_jrnl_abbr = tempUrl2.substr(0,tempUrl2.indexOf(".oxfordjournals"));
					filterAbbrv = tempUrl2.substr(0,tempUrl2.indexOf(".oxfordjournals"));
					tag.url = tempUrl.substr(0,tempUrl.indexOf(".oxfordjournals"))+".oxfordjournals.org/cgi/doi/"+tempMetaContent;
					pageUrl = tempUrl.substr(0,tempUrl.indexOf(".oxfordjournals"))+".oxfordjournals.org/cgi/doi/"+tempMetaContent;
					}
			} 
			else if (metas[i].name == "citation_journal_title") {
				var tempMetaContent = metas[i].content;
				if(BaynoteAPI.isNotEmpty(tempMetaContent)) {
					tag.docAttrs.journal_title = tempMetaContent;					
				}
			}
			else if (metas[i].name == "DC.Title") {
				var tempMetaContent = metas[i].content;
				if(BaynoteAPI.isNotEmpty(tempMetaContent)) {
					tag.title = tempMetaContent;								
					tag.docAttrs.article = tempMetaContent;					
				}
			}
			else if (metas[i].name == "DC.Language") {
				var tempMetaContent = metas[i].content;
				if(BaynoteAPI.isNotEmpty(tempMetaContent)) {
					tag.docAttrs.language = tempMetaContent;						
				}
			}
			else if (metas[i].name == "citation_date") {
				var tempMetaContent = metas[i].content;
				if(BaynoteAPI.isNotEmpty(tempMetaContent)) {
					tag.docAttrs.citation_date = tempMetaContent;						
				}
			}
			else if (metas[i].name == "citation_authors") {
				var tempMetaContent = metas[i].content;
				if(BaynoteAPI.isNotEmpty(tempMetaContent)) {
					tag.docAttrs.authors = tempMetaContent.substring(0,250);						
				}
			}
			else if (metas[i].name == "citation_fulltext_html_url") {
				var tempMetaContent = metas[i].content;
				if(BaynoteAPI.isNotEmpty(tempMetaContent)) {
					tag.docAttrs.html_url = tempMetaContent;						
				}
			}
	}
}

function bn_setClassAttrs(tag){
	var crumbs = document.getElementsByClassName("breadcrumb_subject");
	if (!crumbs) return;
	if (BaynoteAPI.isNotEmpty(crumbs)){
		for (var i = 0; i < crumbs.length; i++) {
			if (!crumbs[i]) return;
			var tempCrumbs = crumbs[i].innerHTML;
			if(BaynoteAPI.isNotEmpty(tempCrumbs) && BaynoteAPI.isNotEmpty(tag.docAttrs.subject)) {
				var tempcr = tag.docAttrs.subject;
				tag.docAttrs.subject = tempcr+", "+tempCrumbs;
			}
			else if(BaynoteAPI.isNotEmpty(tempCrumbs)) {
				tag.docAttrs.subject = tempCrumbs;
			}
		}
	}
	
	var keyword = document.getElementsByClassName("kwd-search");
	if (!keyword) return;
	if (BaynoteAPI.isNotEmpty(keyword)){
		for (var i = 0; i < keyword.length; i++) {
			if (!keyword[i]) return;
			var tempKeyword = keyword[i].innerHTML;
			if(BaynoteAPI.isNotEmpty(tempKeyword) && BaynoteAPI.isNotEmpty(temptag)) {
				var tempkw = temptag;
				var temptag = tempkw+", "+tempKeyword;
			}
			else if(BaynoteAPI.isNotEmpty(tempKeyword)) {
				var temptag = tempKeyword;
			}
		}
		if(BaynoteAPI.isNotEmpty(temptag)) {
			tag.docAttrs.keywords = temptag.substring(0,450);
		}
	}
}


function myPreHandler(tag) { 

	if (typeof tag != 'undefined' &&  typeof tag.type != 'undefined' && tag.type==bnConstants.OBSERVER_TAG)   {	
		
		bn_setmetaAttrs(tag);
		bn_setClassAttrs(tag);

	} // code that runs before the observer fires
	
	if (typeof tag != 'undefined' &&  typeof tag.type != 'undefined' && tag.type==bnConstants.GUIDE_TAG)   {

		if (typeof(pageUrl) != "undefined" && BaynoteAPI.isNotEmpty(pageUrl) && pageUrl != '') {
			tag.url = pageUrl;
		}

	/*	if (typeof(filterAbbrv) != "undefined" && BaynoteAPI.isNotEmpty(filterAbbrv) && filterAbbrv != '') {
			tag.attrFilter = "journal_abbr:\"" + filterAbbrv + "\"";
		}  */

	}
	
    return true;      
} 

function myPostHandler(tag) {
/*
	if (typeof tag != 'undefined' &&  typeof tag.type != 'undefined' && tag.type==bnConstants.GUIDE_TAG)   {	
		//do stuff after recs have loaded
		}
*/
	return true;
}

   // register the event handler
baynote_globals.onBeforeTagShow.push(myPreHandler);
baynote_globals.onTagShow.push(myPostHandler); 
bnResourceManager.registerResource(baynote_globals.ScriptResourceId); 