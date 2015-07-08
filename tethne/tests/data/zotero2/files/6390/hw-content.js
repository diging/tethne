/* jQuery javascript functions for content page */
var gIsFrameset = false;
var gIsOMContent;
var gAuthorAffilList = "div.article div.contributors p.affiliation-list-reveal a.view-more";
var gAuthorNotes = "div.article div.contributors p.author-notes-reveal a.view-more";
var gAuthorContributorList = "div.article div.contributors ol.contributor-list a[href^='#aff']";

$(document).ready(function() {

	var pgDiv = $("div#pageid-content");
	gIsOMContent = (pgDiv.length && pgDiv.hasClass("hwp-metaport-content"));
	
	if (!(getSiteOption("noAuthAffilCollapse") == true)) {
		handleAuthAffil(gAuthorAffilList,gAuthorNotes,gAuthorContributorList);
	}
	
	fixWackyReflinksMarkup();
	
	var defaultDockedNavRules = [
		'', '<div class="content-box" id="docked-cb"><div class="cb-contents"><h3>'+gSiteOptions.dockedNavThisArticleLabel+'</h3><div class="cb-section cb-slug"><ol id="docked-slug"><li></li></ol></div><div class="cb-section"><ol id="docked-nav-views"></ol></div></div></div>',
		'$(#col-2 #docked-nav-views)', '$(#article-cb-main .cb-section ol:has(li a[rel^="view-"]) > li)',
		'$(#col-2 #docked-nav #docked-slug li)', '$(#col-2 #slugline)',
		'', '$(#article-dyn-nav)'
	];

	if (!(getSiteOption("suppressDockedNav") == true)) {
		setupDockBlock(2, 'docked-nav', 'dockblock', defaultDockedNavRules);
	}
	
	if (!(getSiteOption("noPDFExtractExpand") == true)) {
		linkPDFExtImg();
		pdfExtOverlay();
	}
	
	var unloadedImgLookupRule = "div.article div.fig img";
	var numImagesToLoad = checkUnloadedImgs(unloadedImgLookupRule);

	/* ref rollover */
	if (!(getSiteOption("suppressRefPopups") == true)) {
		setTimeout("addRefPops()", 25);
	}
	
	/* fig-expansion in page */
	if (!(getSiteOption("noInlineFigExpand") == true) && (!gIsOMContent || (gIsOMContent && (getSiteOption("inlineFigExpandOMContent") == true)))) {
		setTimeout("figExpandInline()", 10);
	}
	
	/* if configured, open ref links in new windows */
	if (getSiteOption("refLinksNewWindow") == true) {
		setTimeout("refLinksNewWindowTarget()", 25);
	}

	/* 'new window' fig expansions */
	setTimeout("newWindowTargets()", 25);
	
	/* AJAX related article callbacks */
	setTimeout("getISIRelated()", 50);
	
	/* AJAX citing article callbacks */
	setTimeout("getHWCiting()", 50);
	setTimeout("getCiting('isi', gSiteOptions.isiLinkString, '', " + addISICiting + ",'rt=yes')", 50);
	setTimeout("getCiting('scopus','Loading Scopus citing article data...', 'callback/'," + addScopusCiting + ")", 50);
	
	/* AJAX Entrez Links callbacks */
	setTimeout("getEntrezLinks()", 50);
	
	/* Related content */
	setTimeout("getHWRelatedURLs()", 50);
	setTimeout("getPatientInformData()", 50);
	
	/* Fix col heights for images */
	setTimeout("fixHeightForImages(1" + "," + numImagesToLoad + ", '" + unloadedImgLookupRule + "')",1000);
	
	/* Social Bookmarking enhancement */
	setTimeout("updateSBLinks()", 100);
	
            /* Append Semantics Results for Similar Articles */
	if ((getSiteOption("hasSemanticsSearch") == true)) {
            getSimilarSemanticsArticles();
	}

	if ((getSiteOption("hasSemanticsSearch") == true)) {
          /* Append Semantics Results for Related Terms */
          getRelatedSemanticsTerms();
	}
            if ($('div[has-sidebar-videos="yes"]').length) {
                col2SidebarOnlyFixvideo();
            }

$('#content-block').prepend('<div id="print-slug" class="print-only"></div>');
var loc=location.hostname;
if (document.getElementsByName) {
  var metaArray = document.getElementsByName('citation_journal_title');
  for (var i=0; i<metaArray.length; i++) {
    $('<span class="jnl-title">'+ metaArray[i].content + '</span><span class="jnl-url">'+ loc + '</span>' ).appendTo('#print-slug');
  }
};

//prevent function from trying to fire if there is no relevant div
	if ((getSiteOption("hasSemanticsSearch") == true)) {
  if ($("div#semantics-similar-articles").length) {
    $("body").delegate("#semantics-similar-articles-content #similar-articles a#more-art", "click", function (e) {
      e.preventDefault();
      unHideRelatedSemanticsArticles(1);
    });
    $("body").delegate("#semantics-similar-articles-content #similar-articles a#less-art", "click", function (e) {
      e.preventDefault();
      unHideRelatedSemanticsArticles(0);
    });
  }
	}

$('div#col-2  div.cb-slug').clone().appendTo('#print-slug');

 fixvideo();   
}); //end of docready

function unHideRelatedSemanticsArticles(num) {
  
  if (num) {
		// show citations greater than 2; index starts at 0
    $('#similar-articles .cit:gt(2)').show();
		// hide citations greater than than 10; index starts at 0
    $('#similar-articles .cit:gt(9)').hide();
    addAbsPops();
    $('#semantics-similar-articles-content #similar-articles a#more-art').hide();
    var lessThan = $('#semantics-similar-articles-content #similar-articles a#less-art');
    if (! lessThan.length) {
      $('#semantics-similar-articles-content #similar-articles').append('<a href="#" id="less-art">less...</a>');
    } else {
      $('#semantics-similar-articles-content #similar-articles a#less-art').show();
    }
  } else {
    $('#similar-articles .cit:gt(2)').hide();
    addAbsPops();
    $('#semantics-similar-articles-content #similar-articles a#more-art').show();
    var lessThan = $('#semantics-similar-articles-content #similar-articles a#less-art');
    if (lessThan.length) {
      $('#semantics-similar-articles-content #similar-articles a#less-art').hide();
    }
  }
  fixColHeights(-1);
}
function getSimilarSemanticsArticles() {

  var articleId = $('meta[name=citation_id_from_sass_path]').attr('content');
  // For Tom's service pass as '/', for spatel pass as '-'
  //var id = articleId.replace(/\//g, '-');
  var id = articleId;
  var host = document.location.protocol + "//" + document.location.host;
  var url = host + '/similar-articles?resource=' + id;
  
  //console.log("Get resource from ...." + url);
  
  var resultsDiv = '<div id="semantics-similar-articles" class="content-box"> \
  <div class="cb-contents"> \
  <h3 class="cb-contents-header"><span>Similar Articles</span></h3> \
  <div class="cb-section" id="semantics-similar-articles-content"><\div> \
  </div> \
  </div>';
  
 
  $(resultsDiv).appendTo('#col-2');
  $("#semantics-similar-articles-content").load(url, function (response, status, xhr) {
    
    if (status=="success") {
    $("#semantics-similar-articles").show();
    $('#similar-articles').removeAttr("xmlns");
    $('#similar-articles .cit:gt(2)').hide();
    $('#semantics-similar-articles-content #similar-articles #each-similar-articles .cit').each(function (index) {
      url = $(this).find('.cit-extra .first-item a[href]').attr('href');
      rel = $(this).find('.cit-extra .first-item a[rel]').attr('rel');
      $(this).find('.cit-title').wrapInner("<a href=" + url + " rel=" + rel + "/>");
      $(this).find('.cit-print-date').clone().appendTo(this);
		  $(this).find('.cit-secton').hide();
		  $(this).find('.cit-auth-list').hide();
		  $(this).find('.cit-extra').hide();
		  $(this).find('cite').hide();
    });
    	addAbsPops();
    	$('#semantics-similar-articles-content #similar-articles').append('<a href="#"  id="more-art">more...</a>');
    }
    if (status=="error") {

      $("#semantics-similar-articles").hide();
      //console.log("Error processing similar articles: " + xhr.status + " " + xhr.statusText);
    }
  //console.log("Done resource from ...." + url+ ' ' +status);
});
}

function getRelatedSemanticsTerms() {
  var id = $('meta[name=citation_id_from_sass_path]').attr('content');
  var host = document.location.protocol + "//" + document.location.host;
  var url = host + '/related-terms?resource=' + id;
  //console.log("Get terms from ...." + url);
  
  var resultsDiv = '<div id="semantics-related-terms" class="content-box"> \
  <div class="cb-contents"> \
  <h3 class="cb-contents-header"><span>Key Terms</span></h3> \
  <div class="cb-section" id="semantics-related-terms-content"><\div> \
  </div> \
  </div>';
  
  $(resultsDiv).appendTo('#col-2');
  $("#semantics-related-terms-content").load(url, function (response, status, xhr) {
    if (status=="success") {
      $("#semantics-related-terms").show();
      $('#related-terms').removeAttr("xmlns");
    //console.log('ok processing terms feed with url= ' + url);
    }
    
    if (status=="error") {
      $("#semantics-related-terms").hide();
      //console.log("Error processing related terms: " + xhr.status + " " + xhr.statusText);
    }
    //console.log('Done processing terms feed with id= ' + id);
  });
}


function handleAuthAffil(authorAffilList,authorNotes,authorContributorList) {
	var authAffilMatch = getSiteOption('authAffilMatch','div.article div.contributors ol.affiliation-list:has(li)');	
	var authAffil = (authAffilMatch != undefined) ? $(authAffilMatch) : '';
	var disableIfMultAffils = getSiteOption('authAffilDisableMultipleMatches',false);
	if (authAffil.length && ((authAffil.length <= 1) || (!disableIfMultAffils))) {
		var expandStr = getSiteOption('authExpandString', null);
		if (expandStr == null) {
			expandStr = getSiteOption('expandString', '+');
		}
		var contractStr = getSiteOption('authContractString', null);
		if (contractStr == null) {
			contractStr = getSiteOption('contractString', '-');
		}
		var newP = '<p class="affiliation-list-reveal"><a href="#" class="view-more">' + expandStr + '</a> Author Affiliations</p>';
		/* add auth affil show/hide p */
		//if this is a typical case, then we'll just put the expansion on the last div.contributors
		var contribLists = $("div.article div.contributors:last ol.contributor-list:has(li)");
		//unless we have sub-articles
		if ($('div.sub-article').length) {
		contribLists = $("div.article div.contributors ol.contributor-list:has(li)");
		}
		//unless it's an odd case where the last .contributors doesn't have li because of wacky markup
		if (!(contribLists.length)) {
			contribLists = $("div.article div.contributors ol.contributor-list:has(li)");
		}
		if (contribLists.length) {
			contribLists.after(newP);
		}
		/* hide author affiliations until requested */
		if (authAffil.length) {
			authAffil.each(
				function (i) {
					modClass(authAffil.eq(i),'hideaffil','showaffil');
				}
			);
		}
		$(authorAffilList).click(
			function(e) {
					AuthClickOnAffilButton(authorAffilList,authAffilMatch,expandStr,contractStr,e);
			}
		);
		/* show author affiliations when affil link is selected */
		$(authorContributorList).click(
			function(e) {
					AuthClickOnContribAffilLink(authorAffilList,authAffilMatch,expandStr,contractStr,e);
			}
		);
		/*expand author affil when markup different than expected*/
		$("div.contributors a.xref-aff").click(
			function(e) {
					AuthClickOnContribAffilLink(authorAffilList,authAffilMatch,expandStr,contractStr,e);
			}
		);

	var authNotesMatch = getSiteOption('authNotesMatch','div.article div.contributors ul.author-notes:has(li)');	
	var authNotes = (authNotesMatch != undefined) ? $(authNotesMatch) : '';
	var disableIfMultNotes = getSiteOption('authNotesDisableMultipleMatches',false);
	if (authNotes.length && ((authNotes.length <= 1) || (!disableIfMultNotes))) {
		var expandStr = getSiteOption('authExpandString', null);
		if (expandStr == null) {
			expandStr = getSiteOption('expandString', '+');
		}
		var contractStr = getSiteOption('authContractString', null);
		if (contractStr == null) {
			contractStr = getSiteOption('contractString', '-');
		}
        var authAffilList = $("div.article div.contributors ol.affiliation-list:has(li):last"); //get the affiliate-list
        var newNotesP = '<p class="author-notes-reveal"><a href="#" class="view-more">' + expandStr + '</a> Author Notes</p>';
		/* add auth notes show/hide p, and move author-notes after it */
	    authAffilList.addClass("has-authnotes").after(authNotes).after(newNotesP);
		/* hide author notes until requested */
		authNotes.each( //already checked if authNotes present
			function (i) {
				modClass(authNotes.eq(i),'hidenotes','shownotes');
			}
		);
		$(authorNotes).click(
			function(e) {
					AuthClickOnNotesButton(authorNotes,authNotesMatch,expandStr,contractStr,e);
			}
		);
    }
        fixColHeights(1);
	}
}

function figExpandInline() {
	var figlinks = $("div.fig-inline:not(.video-inline) a[href*='expansion']");
	if (figlinks.length) {
		figlinks.each(
			function() {
				var $this = $(this);
				var classAttr = $this.attr("class");
				if (!(classAttr && ((classAttr == 'in-nw') || (classAttr == 'ppt-landing')))) {
                
                    $this.addClass("fig-inline-link");
                    
					if ($this.text().indexOf('n this window') >= 0) {
						$this.text("In this page");
					}
					var parentDiv = $this.parents("div.fig-inline");
					var href = $this.attr("href");
					$(this).click(
						function(e) {
							swapFig(e, href, parentDiv);
                            parentDiv.find('a.fig-inline-link, a.in-nw-vis').unbind('click');
						}
					);
				}
			}
		);
	}
}




function swapFig(e, href, figWrapperEl) {
	var host = document.location.protocol + "//" + document.location.host;
	var path = document.location.pathname;
	var pathseg = path.substring(0, path.lastIndexOf('/'));
	//var baseAjaxUrl = host + pathseg + '/' + href;
	var baseAjaxUrl;
	if (href.indexOf('http:' == 0)) {
		baseAjaxUrl = href;
	}
	else {
		baseAjaxUrl = host + pathseg + '/' + href;
	}
	var ajaxUrl = baseAjaxUrl + ((href.indexOf('?') >= 0) ? '&' : '?') + 'baseURI=' + ((baseAjaxUrl.indexOf('?') > 0) ? baseAjaxUrl.substring(0, baseAjaxUrl.indexOf('?')): baseAjaxUrl);
	//var ajaxUrl = baseAjaxUrl + ((href.indexOf('?') >= 0) ? '&' : '?') + 'baseURI=' + baseAjaxUrl;
	$.ajax({
		url: ajaxUrl,
		dataType: "html",
		type: "GET",
		error: ajaxErr,
		beforeSend: addFigHeaders,
		success: function(xhtml) {
			addFig(xhtml, figWrapperEl);
		},
		complete: ajaxComplete
	});
    
    
	e.preventDefault();
}
function addFigHeaders(req) {
	addCommonHeaders(req);
	addPartHeaders(req);
}

function addFig(xhtmlData, figWrapperEl) {
	if (xhtmlData && !(xhtmlData.indexOf('<html') >= 0)) {
        figWrapperEl.addClass("inline-expansion");
        
        // pick the replacement image out of the div we get back - there should be only one
        largerImage = $("img", xhtmlData).filter(":first");
        largerImage.addClass("replaced-figure");
        
        // get the current image, mark it and hide it
        previousImage = $("img", figWrapperEl).filter(":first");
        previousImage.addClass("previous-figure");
        previousImage.hide();
        
        // swap previous image out for larger image
        largerImage.appendTo(previousImage.parent());
        
        // Remove link to "display in this window" by looking for the link and hiding it's parent
        figWrapperEl.find(".callout .callout-links a.fig-inline-link").parent('li').hide();
        
		newWindowTargets();
		var lookupRule = "div.article div.fig img";
		var numImagesToLoad = checkUnloadedImgs(lookupRule);
		setTimeout("fixHeightForImages(1" + "," + numImagesToLoad + ",'" + lookupRule + "')", 1000);
		gColTempResize = true;
		fixColHeights(1);
		gColTempResize = false;
	}
}

function refLinksNewWindowTarget() {  
	$("div.ref-list div.cit-extra a").each(
		function(i) {
			var origTitle = $(this).attr("title");
			var newTitle = '';
			if ((origTitle == undefined) || (!origTitle)) {
				origTitle = '';
			}
			else {
				newTitle = origTitle + ' ';
			}
			newTitle += '[opens in a new window]';
			$(this).attr("target", "_blank").attr("title", newTitle);
		}
	);
}

function addRefPops() {
        var numMissed = 0;
        var maxToSkip = getSiteOption('refPopsMaxToSkip', 10);
        var maxGap = getSiteOption('refPopsGapTolerance', 2);
        var i = 1;
        var j = 1;
        var idroot = "#xref-ref-";
        var el = $(idroot + i + "-" + j);
        while (numMissed < maxToSkip) {
                if (!el.length) {
                        var refFound = 0;
                        var last = j + maxGap;
                        while (!refFound && j < last) {
                                j++;
                                el = $(idroot + i + "-" + j);
                                if (el.length) {
                                        refFound = 1;
                                }
                        }
                        if (!refFound) {
                                if (j == (maxGap + 1)) {
                                        numMissed++;
                                }
                                i++;
                                j = 1;
                                el = $(idroot + i + "-" + j);
                        }
                } else {
                        numMissed = 0;
                        el.hover(dispRef, hideRef);
                        if ((getSiteOption("isIosRefPops") == true)) {
                                //Also set the ios version of the function
                                el.hover(iosdispRef, hideRef);
                        }
                        j++;
                        el = $(idroot + i + "-" + j);
                }
        }
}


function dispRef(e) {
	var link = $(this).attr("href");
	 //Added to support ref-popups in expansion pages
	 if (!link.match(/^#/) ) 
	 {
		 link=link.substr(link.indexOf("#"));
	 }
	if($("div#hovering-ref").length) {
		$("div#hovering-ref").remove();
		//alert("hovering-ref div removed on new hover!");
	}
	var linkEl = $(link);
	if (linkEl.length) {
		var citHtml = linkEl.next("div").children("div.cit-metadata");
		if (!(citHtml.length)) {
			citHtml = linkEl.parent().next("div").children("div.cit-metadata");
		}
		if (citHtml.length) {
			var newDiv = '<div id="hovering-ref">' + (citHtml.clone().html()) + '</div>';
			$("body").append(newDiv);
			var elH = getObjHeight($("div#hovering-ref"));
			if ((getSiteOption("isIosRefPops") == true)) {
				$("div#hovering-ref").css("left", 10).css("top", e.pageY-elH).css("position", "absolute");
			}
			else {
				$("div#hovering-ref").css("left", e.pageX ).css("top", e.pageY-elH).css("position", "absolute");
				var hh = $("#hovering-ref").height ();
				var ntop =(e.pageY - elH -hh > window.scrollY)?e.pageY - elH -hh:e.pageY + 25;
				$("#hovering-ref").css("top", ntop);
			}
		}
	}
}

function hideRef(e) {
	if($("div#hovering-ref").length) {
		$("div#hovering-ref").remove();
	}
}

function getHWCiting() {
	var citingA = $("#cb-hw-citing-articles");
	if (citingA.length) {
		var newA = '<a id="cb-loading-hw-cited" href="#">Loading citing article data...</a>';
		citingA.replaceWith(newA);
		var href = citingA.attr("href");
		var id = '';
		if (href && (href.indexOf('?') > 0)) {
			var args = href.substring(href.indexOf('?') + 1).split('&');
			for (var i = 0; i < args.length; i++) {
				if (args[i].toLowerCase().indexOf('legid=') == 0) {
					id = args[i].substring(args[i].indexOf('=') + 1);
					if (id.indexOf('#') > 0) {
						id = id.substring(0, id.indexOf('#'));
					}
				}
			}
			if (!(id == '')) {
				var host = document.location.protocol + "//" + document.location.host;
				var ajaxUrl = host + '/cited-by/' + id.replace(/;/,'/');
				$.ajax({
					url: ajaxUrl,
					dataType: "html",
					type: "GET",
					error: ajaxErr,
					success: addHWCiting,
					complete: ajaxCompleteCitedBy
				});

			}
		}
	}
}
function getHWRelatedURLs() {
	var relatedURLsA = $("#cb-related-urls");
	var relatedURLsMsg = getSiteOption('relatedWebPageLoadingText','Loading related web page data...');	
	if (relatedURLsA.length) {
		var newA = '<a id="cb-loading-related-urls" href="#">' + relatedURLsMsg + '</a>';
		relatedURLsA.replaceWith(newA);
		var href = relatedURLsA.attr("href");
		var id = '';
		if (href && (href.indexOf('?') > 0)) {
			var args = href.substring(href.indexOf('?') + 1).split('&');
			for (var i = 0; i < args.length; i++) {
				if (args[i].toLowerCase().indexOf('legid=') == 0) {
					id = args[i].substring(args[i].indexOf('=') + 1);
					if (id.indexOf('#') > 0) {
						id = id.substring(0, id.indexOf('#'));
					}
				}
			}
			if (!(id == '')) {
				var host = document.location.protocol + "//" + document.location.host;
				var ajaxUrl = host + '/related-web-pages/' + id.replace(/;/,'/');
				$.ajax({
					url: ajaxUrl,
					dataType: "html",
					type: "GET",
					error: ajaxErr,
					success: addRelatedURLs,
					complete: ajaxComplete
				});

			}
		}
	}
}
function getPatientInformData() {
	var pInformA = $("#cb-patientinform");
	if (pInformA.length) {
		var newA = '<a id="cb-loading-patientinform" href="#">Loading <em>patient</em>INFORMation...</a>';
		pInformA.replaceWith(newA);
		var href = pInformA.attr("href");
		var id = '';
		if (href && (href.indexOf('?') > 0)) {
			var args = href.substring(href.indexOf('?') + 1).split('&');
			for (var i = 0; i < args.length; i++) {
				if (args[i].toLowerCase().indexOf('legid=') == 0) {
					id = args[i].substring(args[i].indexOf('=') + 1);
					if (id.indexOf('#') > 0) {
						id = id.substring(0, id.indexOf('#'));
					}
				}
			}
			if (!(id == '')) {
				var host = document.location.protocol + "//" + document.location.host;
				var ajaxUrl = host + '/related-web-pages/patientinform/' + id.replace(/;/,'/');
				$.ajax({
					url: ajaxUrl,
					dataType: "html",
					type: "GET",
					error: ajaxErr,
					success: addPatientInform,
					complete: ajaxComplete
				});

			}
		}
	}
}
function getISIRelated() {
	var relatedA = $("#cb-isi-similar-articles");
	if (relatedA.length) {
		var newA = '<a id="cb-isi-similar-articles" href="#">Loading Web of Science article data...</a>';
		relatedA.replaceWith(newA);
		var href = relatedA.attr("href");
		var id = '';
		if (href) {
			var hrefDec = decodeURI(href);
			if ((hrefDec.indexOf('?') > 0)) {
				var args = hrefDec.substring(hrefDec.indexOf('?') + 1).split('&');
				for (var i = 0; i < args.length; i++) {
					var argDec = decodeURIComponent(args[i]);
					if (argDec.toLowerCase().indexOf('access_num=') == 0) {
						id = argDec.substring(argDec.indexOf('=') + 1);
						if (id.indexOf('#') > 0) {
							id = id.substring(0, id.indexOf('#'));
						}
					}
				}
				if (!(id == '')) {
					var host = document.location.protocol + "//" + document.location.host;
					var ajaxUrl = host + '/isi-links/has-related/' + id.replace(/;/,'/');
					$.ajax({
						url: ajaxUrl,
						dataType: "html",
						type: "GET",
						error: ajaxErr,
						success: addISIRelated,
						complete: ajaxComplete
					});
				}
			}
		}
	}
}
function getCiting(service, msg, pathseg, successFn, addlParamString) {
	if (typeof(addlParamString) == "undefined") {
		addlParamString = '';
	}
	var citingA = $("#cb-" + service + "-citing-articles");
	if (citingA.length) {
		var newA = '<a id="cb-loading-' + service + '-cited" href="#">' + msg + '</a>';
		citingA.replaceWith(newA);
		var href = citingA.attr("href");
		var id = '';
		if (href) {
			var hrefDec = decodeURI(href);
			if ((hrefDec.indexOf('?') > 0)) {
				var args = hrefDec.substring(hrefDec.indexOf('?') + 1).split('&');
				for (var i = 0; i < args.length; i++) {
					var argDec = decodeURIComponent(args[i]);
					if (argDec.toLowerCase().indexOf('access_num=') == 0) {
						id = argDec.substring(argDec.indexOf('=') + 1);
						if (id.indexOf('#') > 0) {
							id = id.substring(0, id.indexOf('#'));
						}
					}
				}
				if (!(id == '')) {
					var host = document.location.protocol + "//" + document.location.host;
					var ajaxUrl = host + '/' + service + '-links/' + pathseg + id.replace(/;/,'/') + (addlParamString != '' ? '?' + addlParamString : '');
					$.ajax({
						url: ajaxUrl,
						dataType: "html",
						type: "GET",
						error: ajaxErr,
						success: successFn,
						complete: ajaxComplete
					});
				}
			}
		}
	}
}

function getISICiting() {
	var citingA = $("#cb-isi-citing-articles");
	if (citingA.length) {
		var newA = '<a id="cb-loading-isi-cited" href="#">Loading Web of Science citing article data...</a>';
		citingA.replaceWith(newA);
		var href = citingA.attr("href");
		var id = '';
		if (href) {
			var hrefDec = decodeURI(href);
			if ((hrefDec.indexOf('?') > 0)) {
				var args = hrefDec.substring(hrefDec.indexOf('?') + 1).split('&');
				for (var i = 0; i < args.length; i++) {
					var argDec = decodeURIComponent(args[i]);
					if (argDec.toLowerCase().indexOf('access_num=') == 0) {
						id = argDec.substring(argDec.indexOf('=') + 1);
						if (id.indexOf('#') > 0) {
							id = id.substring(0, id.indexOf('#'));
						}
					}
				}
				if (!(id == '')) {
					var host = document.location.protocol + "//" + document.location.host;
					var ajaxUrl = host + '/isi-links/' + id.replace(/;/,'/');
					$.ajax({
						url: ajaxUrl,
						dataType: "html",
						type: "GET",
						error: ajaxErr,
						success: addISICiting,
						complete: ajaxComplete
					});
				}
			}
		}
	}
}
function getEntrezLinks() {
	var entrezDiv = $("#cb-entrez-links-placeholder");
	if (entrezDiv.length) {
		var entrezA = entrezDiv.children("a");
		if (entrezA) {
			var host = document.location.protocol + "//" + document.location.host;
			var ajaxUrl = host + entrezA.attr("href");
			$.ajax({
				url: ajaxUrl,
				dataType: "html",
				type: "GET",
				error: ajaxErr,
				success: addEntrezLinks,
				complete: ajaxComplete
			});
		}
	}
}

function ajaxErr(req, msg, e) {
}
function ajaxComplete(req, msg) {
}
function ajaxCompleteCitedBy(req, msg) {
}

function updateCBItem(cbItem, newHTML, hasData) {
	var parentItem = cbItem.parents("li").eq(0);
	cbItem.replaceWith(newHTML);
	if (!hasData) {
		// hide the parent li
		if (parentItem.length) {
			modClass(parentItem,"nodata","");
			// check if there are any siblings still being displayed
			var otherItems = parentItem.siblings();
			var allItemsEmpty;
			if (otherItems.length) {
				if (otherItems.length == otherItems.filter(".nodata").length) {
					allItemsEmpty = true
				}
				else {
					allItemsEmpty = false;
				}
			}
			else {
				allItemsEmpty = true;
			}
			if (allItemsEmpty) {
				var cbsection = parentItem.parents("div.cb-section").eq(0);
				if (cbsection.length) {
					modClass(cbsection,"nodata","");
				}
				// do we need to look further?
				if (parentItem.parents("div.cb-section").length > 1) {
					var cbSectionSibs =  cbsection.siblings("div.cb-section");
					if (cbSectionSibs.length) {
						if (cbSectionSibs.length == cbSectionSibs.filter(".nodata").length) {
							allItemsEmpty = true
						}
						else {
							allItemsEmpty = false;
						}
					}
					else {
						allItemsEmpty = true;
					}
					if (allItemsEmpty) {
						var cbgrandsection = parentItem.parents("div.cb-section").eq(1);
						if (cbgrandsection.length) {
							modClass(cbgrandsection,"nodata","");
						}
					}
				}
			}
		}
	}
	// in frameset fix targets on child links, forms
	fixFrameLinks(parentItem.find("a,form"));
	fixColHeights(2);
}
function fixFrameLinks(jqItems) {
	if ((gIsFrameset != null) && gIsFrameset) {
		jqItems.each(
			function(i) {
				var href = $(this).attr("href");
				var action = $(this).attr("action"); // if form
				if ((href != null) || (action != null)) {
					var inFrameAnchor = ((href != null) && (((/frameset=/.test(href)) && (/#/.test(href))) || (href.substring(0,1) == '#')));
					if ((!inFrameAnchor) || (action != null)) {
						if ((navigator.userAgent.indexOf("Firefox") >= 0) && ($(this).hasClass("pdf-direct-link"))) {
							$(this).attr("target", "_blank");
						} else if (getSiteOption("hasFrameLinkTargetFunction", false)) {
							$(this).attr("target", setFrameLinkTarget($(this)));
						} else {
							$(this).attr("target", "_top");
						}
					}
				}
			}
		);
	}
}
function addRelatedURLs(xhtmlData) {
	var cbA = $("#cb-loading-related-urls");
	if (gIsFrameset) {
		if (cbA.length) {
			updateCBItem(cbA, '<div id="cb-loaded-related-urls-none">Not available in this view</div>', false);
		}
	}
	else if (xhtmlData && !(xhtmlData.indexOf('<span') >= 0)) {
		$("#related-urls").replaceWith(xhtmlData);
		var relatedWebPagesLabel = getSiteOption('relatedWebPagesLabel', 'Related Web Pages');
		fixColHeights(1);
		if (cbA.length) {
			updateCBItem(cbA, '<a href="#related-urls">' + relatedWebPagesLabel + '</a>', true);
		}
	}
	else {
		if (cbA.length) {
			updateCBItem(cbA, '<div id="cb-loaded-related-urls-none">No related web pages</div>', false);
		}
	}
}
function addPatientInform(xhtmlData) {
	var cbA = $("#cb-loading-patientinform");
	if (gIsFrameset) {
		if (cbA.length) {
			updateCBItem(cbA, '<div id="cb-loaded-patientinform-none">Not available in this view</div>', false);
		}
	}
	else if (xhtmlData && !(xhtmlData.indexOf('<span') >= 0)) {
		$("#patientinform-links").replaceWith(xhtmlData);
		fixColHeights(1);
		if (cbA.length) {
			updateCBItem(cbA, '<a href="#patientinform-links"><em>patient</em>INFORMation</a>', true);
		}
	}
	else {
		if (cbA.length) {
			updateCBItem(cbA, '<div id="cb-loaded-patientinform-none">No <em>patient</em>INFORMation available for this article</div>', false);
		}
	}
}
function addHWCiting(xhtmlData) {
	var cbA = $("#cb-loading-hw-cited");
	if (gIsFrameset) {
		if (cbA.length) {
			updateCBItem(cbA, '<div id="cb-loaded-hw-cited-none">Not available in this view</div>', false);
		}
	}
	else if (xhtmlData) {
		$("#content-block").append(xhtmlData);
		var hwCitingLabel = getSiteOption('hwCitingLabel', 'View citing article information');
		
		fixColHeights(1);
		if (cbA.length) {
            if (!(getSiteOption("includeHWCitingTitle") == true)) {
                updateCBItem(cbA, '<a href="#cited-by">' + hwCitingLabel + '</a>', true);
            }
            else {
                updateCBItem(cbA, '<a href="#cited-by" title="HighWire Press-hosted articles citing this article">' + hwCitingLabel + '</a>', true);

            }
		}
	}
	else {
if (cbA.length) {
		updateCBItem(cbA, '<div id="cb-loaded-hw-cited-none">No citing articles</div>', false);
	    $("#cb-art-cited").addClass("no-citations");
	}
	}
}


function addISIRelated(xhtmlData) {
	var cbA = $("#cb-isi-similar-articles");
	if (xhtmlData && !(xhtmlData.indexOf('<span') >= 0)) {
		if (cbA.length) {
			updateCBItem(cbA, xhtmlData, true);
		}
	}
	else {
		if (cbA.length) {
			updateCBItem(cbA, '<div id="cb-loaded-isi-related-none">No Web of Science related articles</div>', false);
		}
	}
}
function addISICiting(xhtmlData) {
	var cbA = $("#cb-loading-isi-cited");
	if (xhtmlData && !(xhtmlData.indexOf('<span') >= 0)) {
		if (cbA.length) {
			updateCBItem(cbA, xhtmlData, true);
		}
	}
	else {
		if (cbA.length) {
			updateCBItem(cbA, '<div id="cb-loaded-isi-cited-none">No Web of Science citing articles</div>', false);
		}
	}
}
function addScopusCiting(xhtmlData) {
	var cbA = $("#cb-loading-scopus-cited");
	if (xhtmlData && (xhtmlData.indexOf('<a ') >= 0)) {
		if (cbA.length) {
			updateCBItem(cbA, xhtmlData, true);
		}
	}
	else {
		if (cbA.length) {
			updateCBItem(cbA, '<div id="cb-loaded-scopus-cited-none">No Scopus citing articles</div>', false);
		}
	}
}
function addEntrezLinks(xhtmlData) {
	var entrezDiv = $("#cb-entrez-links-placeholder");

	if (xhtmlData && (xhtmlData.indexOf('<a ') >= 0)) {
		if (entrezDiv.length) {
			updateCBItem(entrezDiv, xhtmlData, true);
			$(entrezDiv).parent('li').addClass('has-data');
		}
	}
	else {
		if (entrezDiv.length) {
			updateCBItem(entrezDiv, '<div id="cb-entrez-links-none">No NCBI links</div>', false);
		}
	}
}

function updateSBLinks() {

	var fbLink = $("a.sb-facebook");
	if (fbLink.length) {
		fbLink.click(
			function(e) {
				window.open(this.href, 'sharer', 'toolbar=0,status=0,width=626,height=436');
				e.preventDefault();
			}
		);
	}
    
    updateGPlus();
    
}

function updateGPlus() {

    var  gPlus = $("ul.social-bookmark-links li.social-bookmarking-item-googleplus");
    /*
                See instructions here if you want to see how to change this:
                http://www.google.com/webmasters/+1/button/
            */
    /*
    	running a test here to check for MSIE < v8, in the interest of avoiding odd display when code returned by google fails.
    */
    var suppressGPlus = false;
    if (($.browser.msie)&&(parseInt($.browser.version, 10)<8)) {
    	suppressGPlus = true;
    }
    if (suppressGPlus) {
    	$('.social-bookmarking-item-googleplus').hide();
    } else {
		if (gPlus.length) {
	        var gPlusSize         = getSiteOption("googlePlusSize", 'small');
	        var gPlusDisplayCount = getSiteOption("googlePlusDisplayCount", 'false');
	        var gPlusURL          = $('head meta[name=citation_public_url]').filter(':first').attr('content') || document.location;

	        //gPlus.prepend('<g:plusone size="' + gPlusSize + '" count="' + gPlusDisplayCount + '" href="' + gPlusURL +'" callback="gPlusCallback"></g:plusone>');
	        gPlus.prepend('<div class="g-plusone" data-size="' + gPlusSize + '" data-count="' + gPlusDisplayCount + '" data-href="' + gPlusURL +'" data-callback="gPlusCallback"></div>');
        
	        $('a', gPlus).hide();  // remove anchor tag, we'll need it later for clicktracking
        
	        $('body').append('<script type="text/javascript" src="https://apis.google.com/js/plusone.js"></script>');
		};
	}
}

function gPlusCallback() {
    var gPlusLoggerURL = $("ul.social-bookmark-links li.social-bookmarking-item-googleplus a").filter(':first').attr('href');
   
   // silently log the successful click
   if (gPlusLoggerURL.length) {
    $.get(gPlusLoggerURL);
   }
    
}

function addDockedNav() {
	var slugEl = $("#col-2 #slugline");
	// get direct children li elements only
	var artViews = $("#article-cb-main .cb-section ol:has(li a[rel^='view-']) > li").clone();
	var newDiv = '<div id="docked-nav"></div>';
	$("#col-2").append(newDiv);
	$("#col-2 #docked-nav").hide();
	var newDivJQuery = $("#docked-nav");
	newDivJQuery.append('<div class="content-box"><div class="cb-contents"><h3>'+gSiteOptions.dockedNavThisArticleLabel+'</h3><div class="cb-section cb-slug"><ol id="docked-slug"><li></li></ol></div><div class="cb-section"><ol id="docked-nav-views"></ol></div></div></div>');
	$("#col-2 #docked-nav-views").append(artViews); /*.append(artSupp);*/
	$("#col-2 #docked-nav #docked-slug li").append(slugEl.clone());
	newDivJQuery.append($("#article-dyn-nav").clone());
	$("#col-2 #docked-nav").fadeIn(250);
}


function removeDockedNav() {
	var dockedNav = $("div#docked-nav");
	if(dockedNav.length) {
		dockedNav.fadeOut(250, function() { dockedNav.remove(); });
	}
}

function fixWackyReflinksMarkup() {
    // There's whitespace between the <li> tags, need to remove to avoid ugly spaces between words.


    $("div.ref-list ol.cit-auth-list,div.ref-list ol.cit-ed-list").each(
		function(i) {
			var original_html = $(this).html();
			var whitespace_stripped_html;

            //Multiple spaces into one, remove trailing spaces after </li>
            whitespace_stripped_html = original_html.replace(/\s+/g,' ');
            whitespace_stripped_html = whitespace_stripped_html.replace(/<\/li>\s+/gi,'</li>');
            whitespace_stripped_html = whitespace_stripped_html.replace(/<\/span>\s+<\/li>/gi,'</span></li>');
			$(this).html(whitespace_stripped_html);
		}
	);

}

function linkPDFExtImg() {
	var pdfExtImg = $("#content-block div.extract-view img.pdf-extract-img");
	if (pdfExtImg.length) {
		pdfExtImg.before(
			'<p class="pdf-extract-click-text">' +
			getSiteOption('pdfExtractExpandText','Click image below to view at full size.') +
			'<\/p>'
		);
		pdfExtImg.wrap('<a class="pdf-extract-click" href="#"></a>');
	}
}
function createOverlay() {
	var imgPdfExt = $(".article.extract-view a.pdf-extract-click").html();
	var newDiv = '<div id="bg-hovering-img"></div><div id="hovering-img"><a class="boxclose" id="boxclose"></a>' + (imgPdfExt) + '</div>';
	$("body").delay(800).append(newDiv).fadeIn('fast',function(){
		$('#hovering-img').fadeIn('fast');
	});
	$('#boxclose').click(function(){ $('#hovering-img').remove(); $('#bg-hovering-img').remove()});
	$('#bg-hovering-img').click (function(){$('#hovering-img').remove();$('#bg-hovering-img').remove();});
}
function pdfExtOverlay(){
if ($(".pdf-extract-img").length && !(window.SupressInitPdfExpandExtract)) {
	createOverlay();
};
$("div.article.extract-view .pdf-extract-click img").click(function () {
  createOverlay();    
});
	$(document).keyup(function(e) {
	var KEYCODE_ESC = 27;
	  if (e.keyCode === KEYCODE_ESC) { 
	     $('#hovering-img').remove();
	     $('#bg-hovering-img').remove();
		}
	});
}
function AuthClickOnAffilButton(authorAffilList,authAffilMatch,expandStr,contractStr,e)
{
	var allViewMores = $(authorAffilList);
	var authAffils = $(authAffilMatch);
	if (($(authorAffilList).filter(':first')).text() == contractStr) {
		/* hide the affil list */
		allViewMores.empty().append(expandStr);
		authAffils.each(
			function(i) {
				modClass(authAffils.eq(i),'hideaffil','showaffil');
			}
		);
	}
	else {
		allViewMores.empty().append(contractStr);
		authAffils.each(
			function(i) {
				modClass(authAffils.eq(i),'showaffil','hideaffil');
			}
		);
	}
	fixColHeights(1);
	e.preventDefault();
}

function AuthClickOnNotesButton(authorNotes,authNotesMatch,expandStr,contractStr,e)
{
	var allViewMores = $(authorNotes);
	var authNotes = $(authNotesMatch);
	if (($(authorNotes).filter(':first')).text() == contractStr) {
		/* hide the affil list */
		allViewMores.empty().append(expandStr);
		authNotes.each(
			function(i) {
				modClass(authNotes.eq(i),'hidenotes','shownotes');
			}
		);
	}
	else {
		allViewMores.empty().append(contractStr);
		authNotes.each(
			function(i) {
				modClass(authNotes.eq(i),'shownotes','hidenotes');
			}
		);
	}
	fixColHeights(1);
	e.preventDefault();
}

function AuthClickOnContribAffilLink(authorAffilList,authAffilMatch,expandStr,contractStr,e)
{
	$(authorAffilList).each(
		function() {
			if ($(this).text() == expandStr) {
				$(this).empty().append(contractStr);
				var authAffils = $(authAffilMatch);
				if (authAffils.length) {
					authAffils.each(
						function(i) {
							modClass(authAffils.eq(i),'showaffil','hideaffil');
						}
					);
				}
				fixColHeights(1);
			}
		}
	);
}
function col2SidebarOnlyFixvideo() {
    $("div.col2-video-label").bind("click",
    function (e) {
        resid = $(this).attr("resid");
        parentDiv = $(this);
        if (videoGetCookie('login') || (hasVideosAccess(resid) == true)) {
            displayVideo(parentDiv);
        } else {
            loginForm = '<div class="popup-login-form" style="border:1px solid #ccc;"><form id="video-widget-login-form" method="post" action=""><p id="video-widget-login-error" style="background-color:red;">Username, password not correct</p><p><label for="login_name">Login: </label><input type="text" id="login_name" name="login_name" size="30" /></p><p><label for="login_pass">Password: </label><input type="password" id="login_pass" name="login_pass" size="30" /></p><p><input type="submit" value="Login" /></p><p><em>Leave empty so see resizing</em></p></form></div>';
            $("#video-widget-login-error").hide();
            $.fancybox(loginForm, {
                'scrolling': 'no',
                'titleShow': true,
                autoDimensions: false,
                width: 250,
                height: 200,
                'onClosed': function () {
                    $("#video-widget-login-error").hide();
                }
            });
            $("#video-widget-login-error").hide();
            $("#video-widget-login-form").bind("submit", function () {
                var doc = "<accesscheck>";
                var checkviews = 'vidsonly';
                doc = doc + '<check-resource resid="' + resid + '" views="' + checkviews + '" user="' + $('#login_name').val() + '" pwd="' + $('#login_pass').val() + '" ><\/check-resource>';
                doc = doc + "<\/accesscheck>";
                var ajaxUrl = document.location.protocol + "//" + document.location.host + '/authn-callback-videos';
                
                var xmlResponse = $.ajax({
                    url: ajaxUrl,
                    contentType: 'text/xml',
                    data: doc,
                    dataType: "xml",
                    type: "POST",
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader("expect", "");
                    },
                    async: false, //important to be not async
                    processData: false
                });
                
                var ret = - 1;
                xmlResponse.done(function (jqXHR) {
                    $(jqXHR).find('check-resource').each(
                    function (i) {
                        var resid = $(this).attr('resid');
                        var view = $(this).attr('view');
                        var access = $(this).attr('add-class');
                        var myCookie = $(this).attr('cookie');
                        var domain = $(this).attr('domain');
                        
                        if (access == 'free') {
                            ret = 1;
                            videoSetCookie("login", myCookie, null, "/", false, false);
                            displayVideo(parentDiv);
                        } else {
                            ret = 0;
                        }
                    });
                });
                xmlResponse.fail(function (jqXHR, textStatus) {
                    ret = 0;
                });
                
                if ($("#login_name").val().length < 1 || $("#login_pass").val().length < 1 || ret == 0) {
                    $("#video-widget-login-error").fadeOut("slow");
                    $("#video-widget-login-error").fadeIn();
                    $.fancybox.resize();
                    return false;
                }
                $.fancybox.showActivity();
                return false;
            });
        }
    });
}
function displayVideo(thisEl) {
    var width = thisEl.attr("width");
    var height = thisEl.attr("height");
    var data = thisEl.attr("data");
    var catalogclass = thisEl.attr("catalogclass");
    var classid = thisEl.attr("classid");
    var ast = thisEl.attr("autostart");
    var playerType = thisEl.attr("playertype");
    var playerID = thisEl.attr("playerid");
    var playerKey = thisEl.attr("playerkey");
    var videohost = thisEl.attr("video-host-js");
    
    playerTemplate = '<div id="pop-out-sidebar-example"><object id="myExperience" class="BrightcoveExperience"><param name="bgcolor" value="#000" /><param name="width" value="' + width + '" /><param name="height" value="' + height + '" /><param name="playerID" value="' + playerID + '" /><param name="playerType" value="videoPlayer" /><param name="playerKey" value="' + playerKey + '" /><param name="isVid" value="true" /><param name="isUI" value="true" /><param name="autoStart" value="true" /><param name="dynamicStreaming" value="true" /><param name="@videoPlayer" value="' + data + '"/></object></div>';
    
    $.fancybox(playerTemplate, {
        'scrolling': 'no',
        'titleShow': true,
        overlayShow: true,
        onClosed: function () {
        },
        autoDimensions: false,
        width: width,
        height: height
    });
    
    // instantiate the player
    brightcove.createExperiences();
    return true;
}
function videoSetCookie(name, value, expires, path, domain, secure) {
    var today = new Date();
    today.setTime(today.getTime());
    if (expires) {
        expires = expires * 1000 * 60 * 60 * 24;
    }
    var expires_date = new Date(today.getTime() + (expires));
    
    document.cookie = name + '=' + value +
    ((expires)? ';expires=' + expires_date.toGMTString(): '') +
    ((path)? ';path=' + path: '') +
    ((domain)? ';domain=' + domain: '') +
    ((secure)? ';secure': '');
    return true;
}

function videoGetCookie(name) {
    var start = document.cookie.indexOf(name + "=");
    var len = start + name.length + 1;
    if (((! start) && (name != document.cookie.substring(0, name.length))) || (start == - 1)) {
        return null;
    }
    var end = document.cookie.indexOf(';', len);
    if (end == - 1) end = document.cookie.length;
    return unescape(document.cookie.substring(len, end));
}
function hasVideosAccess(resid) {
    var doc = "<accesscheck>";
    var checkviews = 'vidsonly';
    doc = doc + '<check-resource resid="' + resid + '" views="' + checkviews + '" ><\/check-resource>';
    doc = doc + "<\/accesscheck>";
    //alert(doc);
    var ajaxUrl = document.location.protocol + "//" + document.location.host + '/authn-callback-videos';
    
    var xmlResponse = $.ajax({
        url: ajaxUrl,
        contentType: 'text/xml',
        data: doc,
        dataType: "xml",
        type: "POST",
        beforeSend: function (xhr) {
            xhr.setRequestHeader("expect", "");
        },
        async: false, //important to be not async
        processData: false
    });
    
    var ret = - 1;
    xmlResponse.done(function (jqXHR) {
        $(jqXHR).find('check-resource').each(
        function (i) {
            var resid = $(this).attr('resid');
            var view = $(this).attr('view');
            var access = $(this).attr('add-class');
            var myCookie = $(this).attr('cookie');
            var domain = $(this).attr('domain');
            
            if (access == 'free') {
                ret = 1;
                return true;
            } else {
                ret = 0;
                return false;
            }
        });
    });
    xmlResponse.fail(function (jqXHR, textStatus) {
        ret = 0;
        return false;
    });
    if (ret == 1) {
        return true;
    }
    if (ret == 0) {
        return false;
    }
}

function fixvideo() {
  flag = $("div.video-info-for-popout");
  if (flag.length) {
    $("div.video-info-for-popout img.pop-out-video").bind("click",
    function (e) {
      resid = $(this).parent().attr("resid");
      parentDiv = $(this).parent();
      //alert('parentid: ' + parentDiv);
      //alert('resid: ' + resid);
      displayVideo(parentDiv);
      e.preventDefault();
    });
    $("div.video-info-for-popout a.pop-out-video").bind("click",
    function (e) {
      resid = $(this).parent().attr("resid");
      parentDiv = $(this).parent();
      //alert('parentid: ' + parentDiv);
      var w = $(this).attr("width");
      //alert('width:'+ w);
      displayVideo(parentDiv);
      e.preventDefault();
    });
  }
}