/*
restore list of objects to show in content pane
*/
var resultLst = new Array();
/* added vu.ngo
status of Underbar screen : closed,open
*/
var state;
var stateClosed="close"; 
var stateOpened="open";

// default skin to use if none specified (blank ok)
var defaultSkin="";

// begin added by vu.ngo - 3/20/2012
var isLogo = true;
var hiddenColumns = 0;
var itemLength = 0;
var minimumColumnWidth = 0;
var numberColumns = 0;
// end added by vu.ngo - 3/20/2012

var curColumns = 0;
var totalColumnsInPage = 0;

var arrCols = new Array();

var scriptResources = [];
var jsLibCount = scriptResources.length;
var jsLibLoaded = 0;
var hidArrCols;

// var underbarServerURL = 'http://ifactory.formos.com:8080/oiUnderbar/';
var underbarServerURL = 'http://oi-underbar.oup.com/underbar/';
// var underbarServerURL = 'http://oi-dev.ifactory.com/oiUnderbar/';
//var underbarServerURL = 'http://oi-staging.ifactory.com/oiUnderbar/';
//var underbarServerURL = 'http://localhost:8080/oi-underbar/';

var resourceURL = underbarServerURL;

var relatedContentURL;
var prefixRelatedContentURL = 'http://oxfordindex.oup.com/search?';
// var prefixRelatedContentURL = 'http://oi-dev.ifactory.com/search?';
//var prefixRelatedContentURL = 'http://oi-staging.ifactory.com/search?';

//Tien end 28/03/2012
var prefixQuery = 'QS';
var searchQuery;
//Tien - save content type from server - 23/3/2012
var contentType;
//Tien end

var contentLoaded = false;
var contentLoading = false;
var cssLoaded = true;

var CONTEXT_DELIMITER = ':';
var CONTEXT_DELIMITER_ENCODED = encodeURIComponent(CONTEXT_DELIMITER);

// begin added by vu.ngo - 3/20/2012 - add more columns and widens Column width when the user widens browser window 

function reloadColumns(_open) {
	
	var additionalSpace = 18;
	var windowWidth = jQuery(window).width();	
	var slideContainerWidth = jQuery("#underbar-columns").width();
	var prevWidth = jQuery("#underbar-prev").width()*2;	
	var nextWidth = jQuery("#underbar-next").width()*2;
	var tempColumnWidth = 0;
	var columnWidth = jQuery(".underbar_slide").width();
	var arrowWidth = prevWidth + nextWidth;
	var underbarWidth = slideContainerWidth + arrowWidth;
	var extraSpace = (windowWidth - additionalSpace) - underbarWidth;
	var columnCount = Math.floor(extraSpace/minimumColumnWidth);
	
	var paddingColumn = parseInt(jQuery(".underbar-column").css("padding-left")) * 2;
	var paddingColumns_about = parseInt(jQuery(".underbar-about-columns").css("padding-left")) * 2;
	var paddingColumn_about = parseInt(jQuery(".underbar-about-column").css("padding-left")) * 2;
	var borderSize = 1;
	var position = jQuery("#slide-control").position();
	var controlWidth = jQuery("#slide-control").width();
	var remaingWidth;	
	if(position != null){
		remaingWidth = controlWidth + position.left;
	}	
		
	var additionalWidth = slideContainerWidth + (columnWidth*columnCount);
	
	if(jQuery( "#underbar_aboutDiv" ).css("display") != "none" || resultLst.length == 0){
		var about_columnWidth = jQuery(".underbar-about-column").width();
		tempColumnWidth = Math.floor((windowWidth - paddingColumns_about)/3);
		if(tempColumnWidth > minimumColumnWidth) {
			columnWidth = tempColumnWidth;
			jQuery("#underbar_aboutDiv").width(windowWidth);
			jQuery(".underbar-about-columns").width((columnWidth*3)+borderSize);
			jQuery(".underbar-about-column").width(columnWidth - paddingColumn_about - borderSize);
			jQuery(".underbar-column-noresult").width(columnWidth - paddingColumn_about - borderSize);
			jQuery("underbar-about-content").width(columnWidth - paddingColumn_about - borderSize);
		}
		return;
	}
	
	
	jQuery("#underbar-container-cover").css('min-width',(columnWidth*3) + arrowWidth + additionalSpace);
	
	if(columnCount < 0 && slideContainerWidth/columnWidth <= 3) {
		if(itemLength == 3) {
			tempColumnWidth = Math.floor((windowWidth - arrowWidth - additionalSpace)/itemLength);
			if(tempColumnWidth > minimumColumnWidth) {
				columnWidth = tempColumnWidth;
				jQuery("#underbar-columns").width(columnWidth*itemLength);
				jQuery("#slide-control").width(columnWidth*itemLength);		
				jQuery(".underbar_slide").width(columnWidth);
				jQuery(".underbar-column").width(columnWidth - paddingColumn - borderSize);
			}
		}
		curColumns = jQuery("#underbar-columns").width()/columnWidth;
		initArrCols(0);
		if(state == stateOpened){
			inactiveDots();
			if(jQuery( "#underbar_aboutDiv" ).css("display") == "none"){
				activeDots();
			}
		}
		return;
	}
	//alert(itemLength);
	// begin updated by vu.ngo - 3/21/2012 --- processing number of items are rendered less than 6
	if(itemLength < 6) {
		// if there are many columns created while widens browser window
		if(columnCount > 0){
			// if it is the first loading columns
			if(_open == "open") {
				// get column width at given time calculated by window width divided by item length
				tempColumnWidth = Math.floor((windowWidth - arrowWidth - additionalSpace)/itemLength);
				// if column width at given time > minimum column width
				if(tempColumnWidth > minimumColumnWidth) {
					columnWidth = tempColumnWidth;
					jQuery("#underbar-columns").width(columnWidth*itemLength);
					jQuery("#slide-control").width(columnWidth*itemLength);		
					jQuery(".underbar_slide").width(columnWidth);
					jQuery(".underbar-column").width(columnWidth - paddingColumn - borderSize);
				// if column width at given time <= minimum column width
				} else {
					jQuery("#underbar-columns").width(additionalWidth);
				}
			// if there are many columns removed while shortens browser window 
			// or there are many columns created while widens browser window and 
			} else if (columnCount < 0 || (columnCount > 0 && remaingWidth - slideContainerWidth >= columnWidth)){
				if(columnCount < 0){
					jQuery("#underbar-next").addClass("underbar-next-arrow-background");         			
	                jQuery("#underbar-next").removeClass("underbar-prev-blank-background");
				} else {
					numberColumns++;
					if(remaingWidth - slideContainerWidth == columnWidth) {
						jQuery("#underbar-next").removeClass("underbar-next-arrow-background");         			
		                jQuery("#underbar-next").addClass("underbar-prev-blank-background");		                
					}
				}				
				jQuery("#underbar-columns").width(additionalWidth);				
				hiddenColumns = 0;
			// width of item length <> width of showing columns
			} else if(controlWidth != slideContainerWidth && columnCount != 0){		
				if(additionalWidth <= controlWidth) {
					jQuery("#underbar-columns").width(additionalWidth);			
					var left = position.left + (columnWidth*columnCount);
					jQuery("#slide-control").css("left", left);	
					if(columnCount == 1){
						hiddenColumns = parseInt(jQuery("#hiddenColumns").val()) + 1;
						jQuery("#hiddenColumns").val(hiddenColumns);
					} else {			
						jQuery("#hiddenColumns").val(columnCount);
					}
					if(additionalWidth == controlWidth) {
						jQuery("#underbar-prev").removeClass("underbar-prev-arrow-background");         			
	                  	jQuery("#underbar-prev").addClass("underbar-prev-blank-background");
					}
					numberColumns++;			
				}	
			}
		} else if (columnCount < 0){
			tempColumnWidth = Math.floor((windowWidth - arrowWidth - additionalSpace)/itemLength);
			if(tempColumnWidth > minimumColumnWidth){		
				columnWidth = tempColumnWidth;		
				jQuery("#underbar-columns").width(columnWidth*itemLength);
				jQuery("#slide-control").width(columnWidth*itemLength);		
				jQuery(".underbar_slide").width(columnWidth);
				jQuery(".underbar-column").width(columnWidth - paddingColumn - borderSize);
			} else {
				jQuery("#underbar-columns").width(additionalWidth);
				if(numberColumns > 0)
					numberColumns--;
			}
			jQuery("#underbar-next").addClass("underbar-next-arrow-background");         			
            jQuery("#underbar-next").removeClass("underbar-prev-blank-background");
		} else {			
			if(numberColumns+3 == itemLength) {
				tempColumnWidth = Math.floor((windowWidth - arrowWidth - additionalSpace)/itemLength);
				if(tempColumnWidth > minimumColumnWidth) {
					columnWidth = tempColumnWidth;
					jQuery("#underbar-columns").width(columnWidth*itemLength);
					jQuery("#slide-control").width(columnWidth*itemLength);		
					jQuery(".underbar_slide").width(columnWidth);
					jQuery(".underbar-column").width(columnWidth - paddingColumn - borderSize);
				}		
			}
					
		}		
		// end updated by vu.ngo - 3/21/2012			
	} else {		
		if(columnCount < 0 || (columnCount > 0 && remaingWidth - slideContainerWidth >= columnWidth)) {
			if(columnCount < 0){
				jQuery("#underbar-next").addClass("underbar-next-arrow-background");         			
                jQuery("#underbar-next").removeClass("underbar-prev-blank-background");
			}				
			else if(remaingWidth - slideContainerWidth == columnWidth) {
				jQuery("#underbar-next").removeClass("underbar-next-arrow-background");         			
                jQuery("#underbar-next").addClass("underbar-prev-blank-background");
			}				
			jQuery("#underbar-columns").width(additionalWidth);
			hiddenColumns = 0;		
		} else if(controlWidth != slideContainerWidth && columnCount != 0){		
			if(additionalWidth <= controlWidth) {
				jQuery("#underbar-columns").width(additionalWidth);			
				var left = position.left + (columnWidth*columnCount);
				jQuery("#slide-control").css("left", left);								
				if(columnCount == 1){
					hiddenColumns = parseInt(jQuery("#hiddenColumns").val()) + 1;
					jQuery("#hiddenColumns").val(hiddenColumns);
				} else {			
					jQuery("#hiddenColumns").val(columnCount);
				}
				if(additionalWidth == controlWidth) {
					jQuery("#underbar-prev").removeClass("underbar-prev-arrow-background");         			
                  	jQuery("#underbar-prev").addClass("underbar-prev-blank-background");
				}					
			}	
		}	
	}
	jQuery("#underbar-container-cover").width(jQuery("#underbar-columns").width() + arrowWidth + additionalSpace).css('margin','0 auto');
	curColumns = jQuery("#underbar-columns").width()/columnWidth;
	initArrCols(0);
	if(state == stateOpened){
		inactiveDots();
		if(jQuery( "#underbar_aboutDiv" ).css("display") == "none"){
			activeDots();			
			if(curColumns == itemLength) {
				jQuery("#underbar-next").removeClass("underbar-next-arrow-background");         			
	        	jQuery("#underbar-next").addClass("underbar-prev-blank-background");
			}					
		}
	}
}
// end added by vu.ngo - 3/20/2012

// Query Context
var qc_query = null;
var qc_defaultQuery = null;
var qc_preferredType = null;
var qc_productCode = null;


/*
accept the Query Context parameters and initialize client-side state variables
*/
function PF_initOIUnderbar(query, defaultQuery, preferredType, productCode){
	state = stateClosed;
	
	// Copy Query Context
	qc_query = query;
	qc_defaultQuery = defaultQuery;
	qc_preferredType = preferredType;
	qc_productCode = productCode;
			
	if (query == null || query == ""){
		searchQuery = checkPrefixKeyword(defaultQuery);
	}else {
		searchQuery = checkPrefixKeyword(query);
	}

    var url = underbarServerURL + "oiunderbarserver.initsearch";
    contentType = preferredType;
    
    // loadAllJs(function(){});//loadCss(resourceURL + 'css/pf_oiunderbar.css?foo2',function(){cssLoaded = true;});});
    
}

/*
receive data from server to init content for Underbar
*/
function callbackInitBar(data){
	jQuery( "#underbar-show" ).show();
	jQuery( "#underbar-wait" ).hide();	
	setResultLst(data);
	if (resultLst.length > 0){
		fncOnBlurRelatedURL();
	}
	
	contentLoaded = true;
	contentLoading = false;
	
    callbackReloadResult(data);
	
}

/*
set values for list of result to show in search content
resultLst will be a json array with approriated content types - Tien 23/3/2012
*/
function setResultLst(data){
	
	for (var key = 0; key < data.length; key ++){
		resultLst[key] = data[key];
		
		resultLst[key]
	}
	
	totalColumnsInPage = data.length;	
	
}

/*
Accept the optional width parameter and kick-off the process of rendering the OIUnderbar
*/
function openOIUnderbar(type){	
	if (isChromeBrowser())
	{		
		jQuery( "#underbar_aboutDiv" ).addClass("underbar_about-crome-Div");
		jQuery( "#underbar_noResultsDiv" ).addClass("underbar_result-crome-Div");
		jQuery( "#underbar-container" ).addClass("underbar-container-chrome");
	} else {
		jQuery( "#underbar_aboutDiv" ).removeClass("underbar_about-crome-Div");
		jQuery( "#underbar_noResultsDiv" ).removeClass("underbar_result-crome-Div");
		jQuery( "#underbar-container" ).removeClass("underbar-container-chrome");
	}
	if (type == 1){
		if(!contentLoaded) {
			if(!contentLoading){
				jQuery( "#underbar-show" ).hide();
				jQuery( "#underbar-wait" ).show();				
				callAjax(underbarServerURL + "oiunderbarserver.initsearch", qc_query, qc_defaultQuery, qc_preferredType, qc_productCode, callbackInitBar);
			}
		} else {
			state = stateOpened;
			showUnderbarContent();
		}	
	}else {
		if (state == stateClosed){
			// begin added by vu.ngo - 3/20/2012
			if(resultLst.length != 0) {
			// end added by vu.ngo - 3/20/2012
				state = stateOpened;
				showUnderbarContent();	
			}		
		}else {
			openOIUnderbar_About();
		}
	}	
	reloadColumns(stateOpened);
}

function showUnderbarContent(logoClicked){
	
	var hide = true;	
	if(state == stateOpened)
		hide = false;
	runEffect(hide, logoClicked);
}

function openOIUnderbar_About(){		
	if (isChromeBrowser())
	{		
		jQuery( "#underbar_aboutDiv" ).addClass("underbar_about-crome-Div");
		jQuery( "#underbar_noResultsDiv" ).addClass("underbar_result-crome-Div");
	} else {
		jQuery( "#underbar_aboutDiv" ).removeClass("underbar_about-crome-Div");
		jQuery( "#underbar_noResultsDiv" ).removeClass("underbar_result-crome-Div");
	}
	if (contentLoading) {
		return;
	}
	if(state == stateOpened && jQuery( "#underbar_aboutDiv" ).css("display") != "none"){
		closeOIUnderbar();
		return;
	}
	showUnderbarContent(isLogo);
	state = stateOpened;	
	reloadColumns();
}

function closeOIUnderbar(){
	if (contentLoading) {
		return;
	}
	if(state == stateClosed){
		return false;
	}
	state = stateClosed;	
	runEffect(true);
	inactiveDots();
}


function toURLParam(p){
	if(0 == null)
		p = "";
	while(p.indexOf("/") != -1)
		p = p.replace("/",":::");
	
	while(p.indexOf("+") != -1)
		p = p.replace("+",":0:");	
	
	return encodeURIComponent(p);
}

/*
accept the optional width parameter and kick-off the process of rendering the OIUnderbar
*/
function PF_doInsertOIUnderbar(width, skin){

	createLayout(skin);	
    runSlideShow();    
    createInitialDots()

    minimumColumnWidth = 250;//jQuery(".underbar_slide").width();	

	state = stateClosed;	
	var aligned = 'left';
	if(width > 0) {
		if(justify)
			aligned = 'left';
		else
			aligned = 'center';
	} else {
		width = '100%';
	}   
	jQuery( "#underbar-related" ).hide();
	jQuery( "#underbar-container" ).hide();		
	jQuery( "#hide-link" ).hide();
	jQuery( "#underbar-hide" ).hide();
	jQuery( "#underbar-wait" ).hide();
	jQuery( "#underbar-reveal-hide" ).hide();
	jQuery('#underbar_aboutDiv').hide();
	jQuery('#underbar-error').hide();
	jQuery('#underbar_noResultsDiv').hide();
	
	$dialog01 = jQuery('#underbar-wrapper')			
		.dialog({
			autoOpen: true,
			width: width,
			draggable: false,
			resizable: false,
			position: [aligned,'bottom']
		});			
	jQuery(".ui-dialog-titlebar").hide();	
	window.onresize = reloadColumns;
}

function PF_insertOIUnderbar(width, skin){
	var cssp_interval = setInterval( function() {
        // if(jsLibLoaded == jsLibCount && cssLoaded){
        	clearInterval( cssp_interval );
        	//alert("loaded!");
        	PF_doInsertOIUnderbar(width, skin);
        // }
    }, 50);		
	
}

/*
Tien 23/3/2012
common method to send data to server
url : method in server
f : callback funtion
*/
function callAjax(url, query, defaultQuery, preferredType, productCode, f){
	
	// don't make a trip to the server if we don't need to
	if (isUnderbarPassiveMode(query, defaultQuery)) {
		callbackInitBar({});
		return;
	}
	
	url += "?qc=" + toURLParam(convertUnderbarQueryArrayToString(query)) + "&dqc=" + toURLParam(defaultQuery) + "&pct=" + toURLParam(preferredType) + "&pid=" + toURLParam(productCode);
	//url = url + "/" + toURLParam(query) + "/" + toURLParam(defaultQuery) + "/pt" + toURLParam(preferredType) + "/" + toURLParam(productCode)
	contentLoading = true;
	jQuery.ajax({
         url: url,
         dataType: "jsonp",     
         jsonp : "callback",
         jsonpCallback: "callbackInitBar",
         type: "POST",
         crossDomain: true,
         async: false,
         error:function (xhr, ajaxOptions, thrownError){} 
     });
}

function convertUnderbarQueryArrayToString(query) {
	var flattened = query;
	if (jQuery.isArray(query)) {
		// += is faster, but these won't be big arrays and I find this more readable
		flattened = query.join("|,|");
	}
	return flattened;
}

/*
Tien 23/3/2012
check json object is empty or not
empty : true, not empty : false
*/
function isEmpty(obj) {
    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            return false;
    }
    return true;
}

/*
check invalid value in search textfield
*/
function checkInvalidSearch(){
	var value = jQuery("#underbar-search-oxford-index").val();
	if (value == '' || value == 'in Oxford Index'){
		return true;
	}
	return false;
}

/*
Tien - 23/3/2012
submit value in search text
send content type from init method to search method
*/
function submitSearch(){
	jQuery('.tooltip').remove();
	jQuery('#underbar-error').hide();
	if (checkInvalidSearch()){
		jQuery('#underbar-error').show();
		return false;
	}
	var searchStr = checkPrefixKeyword(jQuery("#underbar-search-oxford-index").val());
	searchQuery = searchStr;
	//Tien - open new tab for inputting search text box 28/03/2012
	/*var url = underbarServerURL + "oiunderbarserver.searchQueryContext";
	callAjax(url, searchStr, '', contentType, '02', callbackReloadResult);*/
	var url = prefixRelatedContentURL + "q=" + getURLfromPrefix();
	jQuery("#search-form").attr("action", url);
	return true;
	//Tien end 28/03/2012
}

/*
Tien - 23/3/2102
check search string has which prefix, if no prefix, the default is :QS:
return search string with prefix
*/
function checkPrefixKeyword(str){
	var searchStr = "";
	var chk = /^:[a-zA-Z]*:/.test(str);
	if (!chk){
		searchStr = ":QS:" + str;
	}else {
		searchStr = str;
	}
	return searchStr;
}

/*
Tien - 23/3/2012
get search value after prefix characters to send to server
*/
function getURLfromPrefix(){
	var str = checkPrefixKeyword(searchQuery);
	prefixQuery = str.substr(1,(str.substr(1,str.length)).indexOf(':'));
	var value = str.replace(":" + prefixQuery + ":","");
	return value;
}

/*
Tien - 23/3/2012
create error div to show error message when inputing invalid search textbox
*/
function createErrorDiv(){
	jQuery("<div></div>").attr('id', 'underbar-error').appendTo('#underbar-wrapper');
	jQuery('#underbar-error').insertBefore('#underbar-header');
	jQuery('#underbar-error').append("You must provide text in order to perform the search&nbsp;&nbsp;&nbsp;");
}

/*
Tien - 23/3/2012
after submit search text to server,reload search content
*/
function callbackReloadResult(data){
	resultLst = new Array();
	// begin added by vu.ngo - 3/20/2012
	itemLength = 0;
	// end added by vu.ngo - 3/20/2012
	if (isEmpty(data)){
		if(jQuery("#underbar-container").css('display') == 'none')
			runEffect(false);
		state = stateOpened;
		runSlideShow();		
		reloadColumns(stateOpened);
		initArrCols(1);
		inactiveDots();	
	} else {
		setResultLst(data);		
		// begin added by vu.ngo - 3/20/2012
		//jQuery("#resultList").val(JSON.stringify( resultLst ));
		// end added by vu.ngo - 3/20/2012
		if (resultLst.length > 0){
			fncOnBlurRelatedURL();
		}	
		createDotItems();
		createSearchItems();
		if(jQuery("#underbar-container").css('display') == 'none')
			runEffect(false);
		state = stateOpened;
		runSlideShow();		
		reloadColumns(stateOpened);
		initArrCols(1);
		inactiveDots();
		activeDots();		
	}		
}

/*
Tien - 23/3/2012
process for ENTER event on search textbox
*/
function fncKeyDownSearch(e){
	switch (e.keyCode){
		case 13:
			if (!submitSearch()){
			//Tien - prevent running to other event 27/03/2012
			e.returnValue = false;
			//Tien end 27/03/2012
			}
			break;
		default:
			break;
	}
}

/*
Tien - 23/3/2012
change URL base on search query in textbox to see related content in another page
28/03/2012 : change URL for DOI and SUBJ keyword
*/
function fncOnBlurRelatedURL(){
	var splitQuery = {
			query: new Array(),
			context: new Array()
	};
	if (jQuery.isArray(qc_query)) {
		splitQuery = underbar_splitQueryArray(qc_query);
	} else {
		splitQuery = underbar_splitQueryArray([ qc_query ]);
	}
	relatedContentURL = prefixRelatedContentURL;
	
	for (var i = 0; i < splitQuery.context.length; i++) {
		if (splitQuery.query[i].length > 0) {
			if (i != 0) {
				relatedContentURL = relatedContentURL + "&";
			}
			if ("DOI" == splitQuery.context[i]){
				relatedContentURL = relatedContentURL + "assoc=" + splitQuery.query[i];
			}
			if ("KEYW" == splitQuery.context[i]){
				relatedContentURL = relatedContentURL + "f_" + i +  "=keyword&q_" + i +  "=" + splitQuery.query[i];			
			}
			if ("SUBJ" == splitQuery.context[i]){
				relatedContentURL = relatedContentURL + "t" + i + "=" + splitQuery.query[i];
			}
			if ("QS" == splitQuery.context[i]){
				relatedContentURL = relatedContentURL + "q=" + splitQuery.query[i];
			}
			if ("AUTH" == splitQuery.context[i]){
				relatedContentURL = relatedContentURL + "f_" + i +  "=author&q_" + i +  "=" + splitQuery.query[i];
			}
			if ("TITLE" == splitQuery.context[i]){
				relatedContentURL = relatedContentURL + "f_" + i +  "=title&q_" + i +  "=" + splitQuery.query[i];
			}
		}
	}
	jQuery("a#underbar-related").attr('href', relatedContentURL);
}

/*
Tien - 23/3/2012
in case of no data in Content Panes, cant click 'See Related Contents' button
*/
function checkOpenURL(e){
    if (resultLst.length == 0){
    	//Tien - in case of clicking 'See all related contents' on IE, no supported e.preventDefault 27/03/2012
    	if(e.preventDefault){
    		e.preventDefault();
    	}else {
    		e.returnValue = false; //for IE
    	}
    	//Tien end 27/03/2012
    }
}

/*
generate layout for underbar screen
*/
function createLayout(skin){		
	
	if (skin == null || skin.trim() == '') {
		skin = defaultSkin;
	}

	//***create content for search Screen***
	jQuery("<div></div>").attr('id','underbar-wrapper').attr('class', skin).appendTo('body');	
	jQuery('#underbar-wrapper').append("<input type='hidden' id='hiddenColumns'/>");
	jQuery('#underbar-wrapper').append("<input type='hidden' id='hidArrCols'/>");
	jQuery('#underbar-wrapper').append("<input type='hidden' id='hidTotalColumns'/>");	
	// begin added by vu.ngo - 3/20/2012
	//jQuery('#underbar-wrapper').append("<input type='hidden' id='resultList'/>");
	// end added by vu.ngo - 3/20/2012
	jQuery('#underbar-wrapper').append("<a href='" + relatedContentURL + "' target='_blank' id='underbar-related' onclick='checkOpenURL(event);'>See all related content</a>");
	
	createErrorDiv();
		
	jQuery("<div></div>").attr('id', 'underbar-header').appendTo('#underbar-wrapper');
	jQuery("#underbar-header").attr('class', 'underbar-header'); 
	jQuery("<div></div>").attr('id', 'underbar-logo-cover').appendTo('#underbar-header');	
	//Tien - change arrow icon, add text 09/04/2012
	jQuery('#underbar-logo-cover').append("<img src='" + resourceURL + "images/oi-logo.gif' alt='oi-logo' width='92' height='25' class='underbar-logoIndex'/>");
	if (isChromeBrowser()){
		jQuery('#underbar-logo-cover').append("<label for='about the index' class='underbar-aboutLbl-chrome'>About the Index</label>");
		jQuery('#underbar-logo-cover').append("<input type='button' id='underbar-reveal-hide' class='underbar-about-reveal' name='underbar-reveal-hide' value='hide me' onClick='closeOIUnderbar();'/>");
		jQuery('#underbar-logo-cover').append("<input type='button' id='underbar-reveal-show' class='underbar-about-reveal' name='underbar-reveal-show' value='show me' onClick='openOIUnderbar_About();'/>");	// On click was: openOIUnderbar(" + 0 + ");
	}else {
		jQuery('#underbar-logo-cover').append("<label for='about the index' class='underbar-aboutLbl'>About the Index</label>");
		jQuery('#underbar-logo-cover').append("<input type='button' id='underbar-reveal-hide' name='underbar-reveal-hide' value='hide me' onClick='closeOIUnderbar();'/>");
		jQuery('#underbar-logo-cover').append("<input type='button' id='underbar-reveal-show' name='underbar-reveal-show' value='show me' onClick='openOIUnderbar_About();'/>");	// On click was: openOIUnderbar(" + 0 + ");
	}
	//Tien end
	
	jQuery("<div></div>").attr('id', 'underbar-controls-cover').appendTo('#underbar-header');	
		
	jQuery("<div></div>").attr('id','underbar-controls').appendTo('#underbar-controls-cover'); 
	
	jQuery("<div></div>").attr('id','underbar-counter').appendTo('#underbar-controls');		
	//createDotItems();
	jQuery("<div></div>").attr('id','underbar-hide-div').appendTo('#underbar-controls');
	jQuery('#underbar-hide-div').append("<span id='hide-link'>Hide related links</span>");
	//jQuery('#underbar-hide-div').append("<a href='#' onClick='openOIUnderbar(" + 1 + ");' style='text-decoration: none'><span id='show-link'>Show related links</span></a>");
	jQuery('#underbar-hide-div').append("<span id='show-link'>Show related links</span>");
	jQuery('#underbar-hide-div').append("<input type='button' id='underbar-hide' name='underbar-hide' value='hide me' onClick='closeOIUnderbar();'/>");
	jQuery('#underbar-hide-div').append("<input type='button' id='underbar-show' name='underbar-show' value='show me' onClick='openOIUnderbar(" + 1 + ");'/>");
	jQuery('#underbar-hide-div').append("<input type='button' id='underbar-wait' name='underbar-wait' value='loading'/>");
	//jQuery('#underbar-hide-div').append("<img src='" + resourceURL + "images/ajax-loader.gif' id='please-wait' name='please-wait' width='16' height='16'/>");
			
	//***search section - form***
	jQuery("<div></div>").attr('id','underbar-search').appendTo('#underbar-controls-cover'); 
	jQuery("#underbar-search").attr('class','underbar-search');
	//Tien - create form to submit 28/03/2012
	var form = "<form action='' method='post' id='search-form' target='_blank'>";
	form += "<label for='underbar-search-oxford-index'>Search across all sources</label>";	
	form += "<input type='text' class='underbar-search-oxford-index underbar-search-text-color' id='underbar-search-oxford-index' value='in Oxford Index' onClick='removeDefaultText();' onkeydown='fncKeyDownSearch(event);'/>";
	form += "&nbsp;<input id='underbar-search-oxford-index-btn' type='submit' class='underbar-submit underbar-logo' id='underbar-submit' onClick='return submitSearch();' onkeydown='fncKeyDownSearch(event);'/>";
	form += "</form>"
	//Tien end 28/03/2012
	jQuery('#underbar-search').append(form);
	
	jQuery("<div></div>").attr('id','underbar-container').appendTo('#underbar-wrapper'); 
	jQuery("<div></div>").attr('id','underbar-container-cover').appendTo('#underbar-container'); 	
	
	// START_ADD QUY.HUYNH 3/27/2012 OI Underbar Fix TextBox Hint
	jQuery('#underbar-search-oxford-index').blur(function() {
  		if (jQuery("#underbar-search-oxford-index").val() == "") {
  			jQuery( "#underbar-search-oxford-index" ).addClass("underbar-search-text-color");
			jQuery("#underbar-search-oxford-index").val("in Oxford Index"); 
		}
	});
	// END_ADD QUY.HUYNH 3/27/2012 OI Underbar Fix TextBox Hint
	
	//***content of searching item***
	//createSearchItems();	
	//***create content for About Screen***
	jQuery("<div></div>").attr('id','underbar_aboutDiv').appendTo('#underbar-wrapper');  
	showInfoAboutAndNoResults("#underbar_aboutDiv", 0);
	jQuery("<div></div>").attr('id','underbar_noResultsDiv').appendTo('#underbar-wrapper');  
	showInfoAboutAndNoResults("#underbar_noResultsDiv", 1);	
	
	// Tooltip only Text
    jQuery('#underbar-reveal-hide').hover(function(){
            // Hover over code
            var title = "About The Oxford Index";
            jQuery(this).data('tipText', title).removeAttr('title');			
            jQuery('<p class="tooltip"></p>').text(title).css(
			{display: 'block', 
			'z-index': '10000', 
			position: 'absolute',
			'background-color':'#ffffe1',
			color: '#000',
			border: '1px solid #333',
			padding: '1px 2px 1px 2px',
			'font-size': '11px',
			'font-family': 'Tahoma'
			})
            .appendTo('body')
            .fadeIn('slow');	
    }, function() {
            // Hover out code
            //jQuery(this).attr('title', jQuery(this).data('tipText'));
            jQuery('.tooltip').remove();
    }).mousemove(function(e) {
            var mousex = e.pageX + 20; //Get X coordinates
            var mousey = e.pageY + 10; //Get Y coordinates
            jQuery('.tooltip')
            .css({ top: mousey - 30, left: mousex})
    });
	
	jQuery('#underbar-reveal-show').hover(function(){
            // Hover over code
            var title = "About The Oxford Index";
            jQuery(this).data('tipText', title).removeAttr('title');
            jQuery('<p class="tooltip"></p>').text(title).css(
			{display: 'block', 
			'z-index': '10000', 
			position: 'absolute',
			'background-color':'#ffffe1',
			color: '#000',
			border: '1px solid #333',
			padding: '1px 2px 1px 2px',
			'font-size': '11px',
			'font-family': 'Tahoma'
			})
            .appendTo('body')
            .fadeIn('slow');
    }, function() {
            // Hover out code
            //jQuery(this).attr('title', jQuery(this).data('tipText'));
            jQuery('.tooltip').remove();
    }).mousemove(function(e) {
            var mousex = e.pageX + 20; //Get X coordinates
            var mousey = e.pageY + 10; //Get Y coordinates
            jQuery('.tooltip')
            .css({ top: mousey - 30, left: mousex })
    });
	
	jQuery('#underbar-search-oxford-index-btn').hover(function(){
            // Hover over code
            var title = 'Search Oxford Index';
            jQuery(this).data('tipText', title).removeAttr('title');
            jQuery('<p class="tooltip"></p>').text(title).css(
			{display: 'block', 
			'z-index': '10000', 
			position: 'absolute',
			'background-color':'#ffffe1',
			color: '#000',
			border: '1px solid #333',
			padding: '1px 2px 1px 2px',
			'font-size': '11px',
			'font-family': 'Tahoma'
			})
            .appendTo('body')
            .fadeIn('slow');			
    }, function() {
            // Hover out code
            //jQuery(this).attr('title', jQuery(this).data('tipText'));
            jQuery('.tooltip').remove();
    }).mousemove(function(e) {
            var mousex = e.pageX + 20; //Get X coordinates
            var mousey = e.pageY + 10; //Get Y coordinates
            jQuery('.tooltip')
            .css({ top: mousey - 40, left: mousex - 130 })
    });	
	
}

function showInfoAboutAndNoResults(id, mode){
	if (mode == 0){
		jQuery("<div></div>").attr({id: 'underbar-container-about' + mode}).appendTo(id);
		jQuery("#underbar-container-about" + mode).attr('class', 'underbar-container-about');
		jQuery("<div></div>").attr('id','underbar-about-columns' + mode).appendTo('#underbar-container-about' + mode);
		jQuery("#underbar-about-columns" + mode).attr('class', 'underbar-about-columns');
		//column 1 :		
		jQuery("<div></div>").attr({id: 'underbar-about-column_0' + mode}).appendTo('#underbar-about-columns' + mode);
		jQuery("#underbar-about-column_0" + mode).attr('class', 'underbar-about-column');
		jQuery("<div></div>").attr({id: 'underbar-about-content_0' + mode}).appendTo('#underbar-about-column_0' + mode);
		jQuery("#underbar-about-content_0" + mode).attr('class', 'underbar-about-content');
		jQuery("#underbar-about-content_0" + mode).append("<h3>"+ "About the Oxford Index" + "</h3>");
		var ulContent = "";
		ulContent += "<ul>";
	    ulContent += "<li>";
	    ulContent += "<div class='alignAbout'>A free search and discovery service, the Index helps users begin their research by providing a single, convenient search portal for trusted scholarship from Oxford and our partners.</div>";
	    ulContent += "</li>";
	    ulContent += "</ul>";
		jQuery('#underbar-about-content_0' + mode).append(ulContent);
		//column 2 :
		jQuery("<div></div>").attr({id: 'underbar-about-column_1' + mode}).appendTo('#underbar-about-columns' + mode);
		jQuery("#underbar-about-column_1" + mode).attr('class', 'underbar-about-column');
		jQuery("<div></div>").attr({id: 'underbar-about-content_1' + mode}).appendTo('#underbar-about-column_1' + mode);
		jQuery("#underbar-about-content_1" + mode).attr('class', 'underbar-about-content');
		jQuery("#underbar-about-content_1" + mode).append("<h3>"+ "Related Content from Oxford University Press" + "</h3>");
		var ulContent = "";
		ulContent += "<ul>";
	    ulContent += "<li>";
	    ulContent += "<div class='alignAbout'>More than just a search tool, the Index provides smart recommendations for related content - from journal articles and scholarly monographs, to reference content, primary sources, and more - based on your research interests.</div>";
	    ulContent += "</li>";
	    ulContent += "</ul>";
		jQuery('#underbar-about-content_1' + mode).append(ulContent);
		//column 3 :
		jQuery("<div></div>").attr({id: 'underbar-about-column_2' + mode}).appendTo('#underbar-about-columns' + mode);
		jQuery("#underbar-about-column_2" + mode).attr('class', 'underbar-about-column underbar-about-column-end');
		jQuery("<div></div>").attr({id: 'underbar-about-content_2' + mode}).appendTo('#underbar-about-column_2' + mode);
		jQuery("#underbar-about-content_2" + mode).attr('class', 'underbar-about-content');
		jQuery("#underbar-about-content_2" + mode).append("<h3>"+ "Search across All Books and Journals from Oxford" + "</h3>");
		var ulContent = "";
		ulContent += "<ul>";
	    ulContent += "<li>";
	    ulContent += "<div class='alignAbout'>The Oxford Index brings together, for the first time, the best of reference, journals, and scholarly works - one search delivers seamless discovery of all Oxford University Press online content.<br /><br />";
	    ulContent += "Just enter your search term(s) in the box at the bottom right of your browser, and click the search icon to view your results in a new tab or window.</div>";
	    ulContent += "</li>";
	    ulContent += "</ul>";
		jQuery('#underbar-about-content_2' + mode).append(ulContent);
	}else {
		jQuery("<div></div>").attr({id: 'underbar-container-about' + mode}).appendTo(id);
		jQuery("#underbar-container-about" + mode).attr('class', 'underbar-container-noresult');
		jQuery("<div></div>").attr('id','underbar-about-columns' + mode).appendTo('#underbar-container-about' + mode);
		jQuery("#underbar-about-columns" + mode).attr('class', 'underbar-about-columns');
		//column 1 :		
		jQuery("<div></div>").attr({id: 'underbar-about-column_0' + mode}).appendTo('#underbar-about-columns' + mode);
		jQuery("#underbar-about-column_0" + mode).attr('class', 'underbar-column-noresult');
		jQuery("<div></div>").attr({id: 'underbar-about-content_0' + mode}).appendTo('#underbar-about-column_0' + mode);
		jQuery("#underbar-about-content_0" + mode).attr('class', 'underbar-about-content');
		jQuery("#underbar-about-content_0" + mode).append("<h3>" + "</h3>");
		var ulContent = "";
		ulContent += "<ul>";
	    ulContent += "<li>";
	    ulContent += "<div class='alignAbout'></div>";
	    ulContent += "</li>";
	    ulContent += "</ul>";
		jQuery('#underbar-about-content_0' + mode).append(ulContent);
		//column 2 :
		jQuery("<div></div>").attr({id: 'underbar-about-column_1' + mode}).appendTo('#underbar-about-columns' + mode);
		jQuery("#underbar-about-column_1" + mode).attr('class', 'underbar-column-noresult');
		jQuery("<div></div>").attr({id: 'underbar-about-content_1' + mode}).appendTo('#underbar-about-column_1' + mode);
		jQuery("#underbar-about-content_1" + mode).attr('class', 'underbar-about-content');
		jQuery("#underbar-about-content_1" + mode).append("<h3>"+ "NO RELATED LINKS DETECTED" + "</h3>");
		var ulContent = "";
		ulContent += "<ul>";
	    ulContent += "<li>";
	    ulContent += "<div class='alignAbout'>We can detect no related content links based on the main page you are currently viewing.<br /><br />";
	    ulContent += "Related links from the Oxford Index will often be shown here when you are viewing search results or actual content pages on this site.<br><br>";
	    ulContent += "Check back here again when viewing other pages to see how the Oxford Index can help you navigate through online content from Oxford University Press and our publishing partners.</div>";
	    ulContent += "</li>";
	    ulContent += "</ul>";
		jQuery('#underbar-about-content_1' + mode).append(ulContent);
		//column 3 :
		jQuery("<div></div>").attr({id: 'underbar-about-column_2' + mode}).appendTo('#underbar-about-columns' + mode);
		jQuery("#underbar-about-column_2" + mode).attr('class', 'underbar-column-noresult underbar-about-column-end');
		jQuery("<div></div>").attr({id: 'underbar-about-content_2' + mode}).appendTo('#underbar-about-column_2' + mode);
		jQuery("#underbar-about-content_2" + mode).attr('class', 'underbar-about-content');
		jQuery("#underbar-about-content_2" + mode).append("<h3>"+ "YOU CAN ALWAYS SEARCH THE INDEX DIRECTLY" + "</h3>");
		var ulContent = "";
		ulContent += "<ul>";
	    ulContent += "<li>";
	    ulContent += "<div class='alignAbout'>Use the search box on the right of the Oxford Index bar to search across all book and journal content available from Oxford University Press and our publishing partners.<br /><br />";
	    ulContent += "Results will open in a new browser window or tab, so you can keep your place on this site while you explore related material.</div>";
	    ulContent += "</li>";
	    ulContent += "</ul>";
		jQuery('#underbar-about-content_2' + mode).append(ulContent);
	}
}

/*
Tien 23/3/2012
create series of dots with size = the number of content types
*/
function createDotItems(){
	jQuery('#underbar-counter').html("");
	var html = "";
	for (var i = 0; i < totalColumnsInPage; i ++){
		html += "<img src='" + resourceURL + "images/dot-inactive.png' id='underbar-dot-" + i + "' width='10' height='10'/>";
	}
	jQuery('#underbar-counter').append(html);
}

function createInitialDots(){
	jQuery('#underbar-counter').html("");
	var html = "";
	for (var i = 0; i < 7; i ++){
		html += "<img src='" + resourceURL + "images/dot-inactive.png' id='underbar-dot-" + i + "' width='10' height='10'/>";
	}
	jQuery('#underbar-counter').append(html);
}

/*
Tien 23/3/2012
array contain active dots for init
mod : 26/03/2012 - display correct dots for resizing browser
*/
function initArrCols(mode){
	var i;
	var last;
	//in case of clicking search icon
	if (mode == 1){
		i = 0; 
		last = curColumns;
	}
	//in case of initialiazion
	if (mode == 0){
		if (arrCols.length == 0){ // in case of no resizing browser
			i = 0;
			last = curColumns;
		} else { // in case of resizing browser
			i = arrCols[0];
			if (i + curColumns > totalColumnsInPage){
				i = i - ((i + curColumns) - totalColumnsInPage);
				last = totalColumnsInPage;
			}else {
				last = curColumns + i;
			}
		}
	}
	arrCols = new Array();
	var index = 0;
	//Tien - in case IE increase current column auto 28/03/2012
	if (i < 0){
		i = 0;
	}
	//Tien end 28/03/2012
	for (var j = i; j < last; j ++){
		arrCols[index] = j;
		index ++;
	}
	createArrColsHidden();
}

/*
Tien 23/3/2012
hidden array to send values to jcarousellite.js
*/
function createArrColsHidden(){
	hidArrCols = arrCols.join();
	jQuery("#hidArrCols").val(hidArrCols);
	jQuery("#hidTotalColumns").val(totalColumnsInPage);
}

/*
Tien 23/3/2012
active dots in active columns array
*/
function activeDots(){
	for (var i = 0; i < arrCols.length; i ++){
		var srcInactive = jQuery('#underbar-dot-' + arrCols[i]).attr("src").replace("-inactive", "-active");
        jQuery('#underbar-dot-' + arrCols[i]).attr("src", srcInactive);
	}
}

/*
Tien 23/3/2012
inactive all dots
*/
function inactiveDots(){
	for (var i = 0; i < totalColumnsInPage; i ++){
		var srcInactive = jQuery('#underbar-dot-' + i).attr("src").replace("-active", "-inactive");
        jQuery('#underbar-dot-' + i).attr("src", srcInactive);
	}
}

// START_ADD QUY.HUYNH 3/23/2012 OI Underbar.3.19 - Ticket #688 - 1.3.2 Truncate Titles
function truncateObj(str, length, isAuthor) {
	if (str != null && jQuery.trim(str) != "") {
		
		if (!isAuthor) {		
			if (str.length >= (length+3)) {
				
				// Count the number of uppercase characters.  Subtract a character for every 10 uppercase 
				var numUppercase = 0;
				
				for(c=0;c<length;c++){
					if(str.charAt(c) == str.charAt(c).toUpperCase()){
						numUppercase++;
					}
				}
						
				var subFromLower = numUppercase / 10;
				
				length = length - subFromLower;
				
				// If the last character is a space, remove it.
				if(str.charAt(length-1) == ' ')
					length--;
				
				str = str.substring(0, length) + "...";
			
			}
		} else {
			// truncate for author
			var idxEndOfStr = 0;
			if (str.indexOf(",") != -1) {				
				for (i = 0; i < str.length; i++) {					
					if (str.charAt(i) == ',') {
						idxEndOfStr++;
						if (idxEndOfStr == 2) {
							str = str.substring(0, i + 1) + "...";
							break;
						}						
					}
				}
			}
		}
	}	
	return str;
}

function processTitleMarkup(str) {
	//var start = str.indexOf("in=\"");
	//start = start + 4;
	//var end = str.indexOf("\">")
	
	var start = str.indexOf("\">");
	start = start + 2;	
	var end = str.indexOf("<\/dc:title>")	
	
	var startStr = str.substring(0, start);
	var middleStr = str.substring(start, end);
	var endStr = str.substring(end);	
	
	str = truncateObj(middleStr, 50);
	
	str = (startStr.concat(str)).concat(endStr);
	
	return str;
}
// END_ADD QUY.HUYNH 3/23/2012 OI Underbar.3.19 - Ticket #688 - 1.3.2 Truncate Titles

/*
Tien 23/3/2012
create search section to display data
loop on resultLst to get each JSON object
properties in IndexCards will be shown in IndexCardSearchResults.indexCards
*/
function createSearchItems(){
	var morContentTypeLink;
	var titleTemp;
	jQuery("#underbar-container-cover").html("");
	// begin added by vu.ngo - 3/20/2012
	if(resultLst.length == 0) {
		jQuery("<li></li>").attr('id','slide').appendTo('#slide-control');
		jQuery("#slide").attr('class', 'underbar_slide');
		jQuery("<div></div>").attr('id', 'col').appendTo('#slide');
		jQuery("<div></div>").attr({id: 'content'}).appendTo('#col');
		jQuery("#content").attr('class', 'underbar-content');
		return;
	}
	// end added by vu.ngo - 3/20/2012	
	jQuery('#underbar-container-cover').append("<button id='underbar-prev' class='underbar-prev underbar-prev-blank-background'>prev</button>");		
	jQuery("<div></div>").attr('id','underbar-columns').appendTo('#underbar-container-cover'); 
	jQuery("#underbar-columns").attr('class','underbar-slide-container');
	jQuery("<ul></ul>").attr('id','slide-control').appendTo('#underbar-columns');		
	jQuery.each(resultLst, function (i){
		jQuery("<li></li>").attr('id','slide' + i).appendTo('#slide-control');
		jQuery("#slide" + i).attr('class', 'underbar_slide');
		jQuery("<div></div>").attr('id', 'col' + i).appendTo('#slide' + i);
		jQuery("#col" + i).attr('class', 'underbar-column');  
		jQuery("<div></div>").attr({id: 'content' + i}).appendTo('#col' + i);
		jQuery("#content" + i).attr('class', 'underbar-content');		

		// START_EDIT QUY.HUYNH 3/23/2012 OI Underbar.3.18 - Ticket #687 - 1.3.2 Display content type name
		jQuery('#content' + i).append("<h3>"+ displayContentType(resultLst[i].contentType) +"</h3>");
		// END_EDIT QUY.HUYNH 3/23/2012 OI Underbar.3.18 - Ticket #687 - 1.3.2 Display content type name
		
		//Tien - check JSON is an object or an array 28/03/2012
		if (resultLst[i].IndexCardSearchResults != ""){		
			//in case indexCards JSON has only 1 item - an object not an array
			if (resultLst[i].IndexCardSearchResults.indexCards.length == undefined){
				setContentColumns(resultLst[i].IndexCardSearchResults.indexCards, resultLst[i].contentType, i, 0);
			//in case indexCards JSON is an array
			}else {
				jQuery.each(resultLst[i].IndexCardSearchResults.indexCards, function(index, value) {		
					setContentColumns(value, resultLst[i].contentType, i, 1, index);
				});		
			}	
			//Tien end 28/03/2012
			// START_EDIT QUY.HUYNH 3/23/2012 OI Underbar.3.16 - Ticket #685 - 1.3.2.2 Link to more by content type
			var contentTypeParameter = resultLst[i].contentType.toLowerCase().replace(/ /g,'');

			// OI ticket #1055, type Article relabelled as Review Article in search.xml breaks this. Do hacky rewrite.
			if (contentTypeParameter === 'article') {
				contentTypeParameter = 'reviewarticle';
			} else if (contentTypeParameter === 'authority') {
				contentTypeParameter = 'overview';
			}

			morContentTypeLink = relatedContentURL + "&type_0=" + contentTypeParameter;
						
			jQuery('#col' + i).append("<a href='" + morContentTypeLink + "' target='_blank' onclick='checkOpenURL(event);' style='text-decoration: none'><span class='underbar-more'>More "+ plural(displayContentType(resultLst[i].contentType)) +" &raquo;</span></a>");			
			// END_EDIT QUY.HUYNH 3/23/2012 OI Underbar.3.16 - Ticket #685 - 1.3.2.2 Link to more by content type			
		}
		itemLength++;
		if(itemLength == 8) {
		 	return false;
		} else if (itemLength > 8){
			return false;
		}
	});	
	jQuery('#underbar-container-cover').append("<button id='underbar-next' class='underbar-next underbar-next-arrow-background'>next</button>");
}

/**
Tien - separate function to show properties for Content Pane 28/03/2012
value : json object
contentType : content type value in json object
i : index of json array - resultLst
mode : 0 - in case indexCards has 1 item , 1 - in case indexCards have more 1 item
index : index of indexCards in case of having one more
*/
function setContentColumns(value, contentType, i, mode, index){	
	var ulContent = "";
    ulContent += "<ul>";
    ulContent += "<li>";
	var visible = 0;
	if(value.primaryContributor == "undefined" || value.primaryContributor == null) {
		visible = 1;
		value.primaryContributor ="";
	}					
	if(value.publicationDate == "undefined" || value.publicationDate == null) {
		visible = 2;
		value.publicationDate ="";
	}					
	if(value.source == "undefined" || value.source == null) {
		visible = 3;
		value.source ="";
	}					
	if(value.title == "undefined" || value.title == null) {
		visible = 4;
		value.title ="";
	}
	if(contentType == "Journal") {		
		titleTemp = truncateObj(value.title, 34, false);				
	    ulContent += "<a title='"+encodeTitle(value.title)+"' href='http://oxfordindex.oup.com/view/" + value.doi + "' target='_blank'>" + titleTemp + "</a>";
	    ulContent += yearOnly(value.publicationDate);
	} else if(contentType == "Book" || contentType == "Research Guide") {
		titleTemp = truncateObj(value.title, 34, false);				
	    ulContent += "<a title='"+encodeTitle(value.title)+"' href='http://oxfordindex.oup.com/view/" + value.doi + "' target='_blank'>" + titleTemp + "</a>";
	  		if(visible != 1)					 				
	    	ulContent += truncateObj(value.primaryContributor, 0, true) + "; ";
	    ulContent += yearOnly(value.publicationDate);
	}  else if(contentType == "Journal Article" || contentType == "Chapter" || contentType == "Article") {
		titleTemp = truncateObj(value.title, 34, false);				
	    ulContent += "<a title='"+encodeTitle(value.title)+"' href='http://oxfordindex.oup.com/view/" + value.doi + "' target='_blank'>" + titleTemp + "</a>";
		if(contentType != "Reference Entry" && visible != 1)		    		 				
	   		ulContent += truncateObj(value.primaryContributor, 0, true) + "<br>";
	   	if(visible != 3)
	   		ulContent += truncateObj(value.source, 29, false) + "; ";
	    ulContent += yearOnly(value.publicationDate);
	}  else if(contentType == "Reference Entry") {
		titleTemp = truncateObj(value.title, 34, false);				
	    ulContent += "<a title='"+encodeTitle(value.title)+"' href='http://oxfordindex.oup.com/view/" + value.doi + "' target='_blank'>" + titleTemp + "</a>";	    
	   	if(visible != 3)
	   		ulContent += truncateObj(value.source, 29, false);
	} else if(contentType == "Authority") {
		titleTemp = truncateObj(value.title, 34, false);				
	    ulContent += "<a title='"+encodeTitle(value.title)+"' href='http://oxfordindex.oup.com/view/" + value.doi + "' target='_blank'>" + titleTemp + "</a>";
	    if (value.subjects != "undefined" &&  value.subjects != null) {
	    	ulContent += truncateObj(value.subjects, 0, true) + "<br>";
	    }
	   	if(visible != 3)
	   		ulContent += truncateObj(value.source, 29, false);
	} else if(contentType == "Primary Text") {		
		titleTemp = truncateObj(value.title, 34, false);				
	    ulContent += "<a title='"+encodeTitle(value.title)+"' href='http://oxfordindex.oup.com/view/" + value.doi + "' target='_blank'>" + titleTemp + "</a>";
		if(contentType != "Reference Entry" && visible != 1)		    		 				
	   		ulContent += truncateObj(value.primaryContributor, 0, true) + "<br>";
	   	if(visible != 3)
	   		ulContent += truncateObj(value.source, 29, false) + "; ";
	    ulContent += yearOnly(value.publicationDate);
	} else {	
		titleTemp = truncateObj(value.title, 34, false);				
	    ulContent += "<a title='"+encodeTitle(value.title)+"' href='http://oxfordindex.oup.com/view/" + value.doi + "' target='_blank'>" + titleTemp + "</a>";
		if(contentType != "Reference Entry" && visible != 1)		    		 				
	   		ulContent += truncateObj(value.primaryContributor, 0, true) + "<br>";
	   	if(visible != 3)
	   		ulContent += truncateObj(value.source, 29, false) + "; ";
	    ulContent += yearOnly(value.publicationDate);
	}				
	   ulContent += "</li>";
	   ulContent += "</ul>";
	jQuery('#content' + i).append(ulContent); 
	if (mode == 1){	
		if(index == 2)
			return false;
	}
}

function yearOnly(publicationDate){
 if(publicationDate.indexOf("-") != -1){
   return publicationDate.substring(0,publicationDate.indexOf("-"));
 }
 return "";
}

function plural(word){
  if(word.charAt(word.length-1) == 'y'){
  	return word.substring(0,word.length-1) + "ies";
  }
  return word + "s";
}

function runEffect(hide, logoClicked) {
	// get effect type from 
	var selectedEffect = "blind";

	// most effect types need no options passed by default
	var options = {};
	// some effects have required parameters
	if ( selectedEffect === "scale" ) {
		options = { percent: 100 };
	} else if ( selectedEffect === "size" ) {
		options = { to: { width: 280, height: 185 } };
	}
	// run the effect
	if(logoClicked) {
		if ((state == stateClosed && (checkInvalidSearch() || resultLst.length == 0)) || state == stateOpened){
			jQuery( "#underbar-container" ).hide();			
			if(state == stateClosed)
				jQuery("#underbar_aboutDiv").show(selectedEffect, options, 400 );
			else			
				jQuery("#underbar_aboutDiv").show();				
			jQuery( "#underbar-related" ).hide();	
			jQuery( "#hide-link" ).hide();	
			jQuery( "#underbar-hide" ).hide();	
			jQuery( "#show-link" ).show();
			jQuery( "#underbar-show" ).show();
			jQuery( "#underbar-controls" ).removeClass("underbar-controls-background");
			inactiveDots();
		} else if(state == stateClosed && !checkInvalidSearch() && !resultLst.length == 0) {
			jQuery( "#underbar-container" ).show( selectedEffect, options, 400 );	
			jQuery( "#underbar-related" ).show();	
			jQuery( "#underbar-controls" ).show();
			jQuery( "#show-link" ).hide();
			jQuery( "#underbar-show" ).hide();
			jQuery( "#hide-link" ).show();	
			jQuery( "#underbar-hide" ).show();		
			jQuery( "#underbar-controls" ).addClass("underbar-controls-background");
			inactiveDots();
			activeDots();
			jQuery("#underbar_aboutDiv").hide();
		}
		//jQuery( "#underbar-reveal" ).hide();
		jQuery( "#underbar-reveal-hide" ).show();
		jQuery( "#underbar-reveal-show" ).hide();
		jQuery('#underbar_noResultsDiv').hide();
	} else {
		// Hide Show related links
		if(hide) {
			if(jQuery( "#underbar_aboutDiv" ).css("display") == "none"){
				jQuery( "#underbar-container" ).hide( selectedEffect, options, 400 );	
			} else {
				jQuery( "#underbar_aboutDiv" ).hide( selectedEffect, options, 400 );
			}			
			jQuery( "#underbar-related" ).hide();
			jQuery( "#hide-link" ).hide();
			jQuery( "#underbar-hide" ).hide();	
			jQuery( "#underbar-controls" ).removeClass("underbar-controls-background");
			jQuery( "#show-link" ).show();	
			jQuery( "#underbar-show" ).show();			
			jQuery( "#underbar-reveal-show" ).show();
			jQuery( "#underbar-reveal-hide" ).hide();	
			jQuery('#underbar_noResultsDiv').hide();			
		} else {
			// Open Show related links
			if (resultLst.length == 0){
				
				if (jQuery( "#underbar_aboutDiv" ).css("display") == "none"){
					jQuery('#underbar_noResultsDiv').show(selectedEffect, options, 400 );
				} else {					
					jQuery('#underbar_noResultsDiv').show();
				}
				jQuery("#underbar_aboutDiv").hide();				
				jQuery( "#underbar-controls" ).show();
				jQuery( "#underbar-controls" ).addClass("underbar-controls-background");
				jQuery( "#underbar-search" ).show();				
				jQuery( "#underbar-reveal-hide" ).hide();
				jQuery( "#underbar-reveal-show" ).show();
				jQuery( "#show-link" ).hide();
				jQuery( "#underbar-show" ).hide();
				jQuery( "#hide-link" ).show();	
				jQuery( "#underbar-hide" ).show();
				jQuery( "#underbar-related" ).hide();
			}else {	
				if (jQuery( "#underbar_aboutDiv" ).css("display") == "none"){
					jQuery( "#underbar-container" ).show( selectedEffect, options, 400 );	
					jQuery( "#underbar-related" ).show();	
					jQuery( "#underbar-controls" ).show();
					jQuery( "#underbar-controls" ).addClass("underbar-controls-background");
					jQuery( "#underbar-search" ).show();				
					jQuery( "#underbar-reveal-hide" ).hide();
					jQuery( "#underbar-reveal-show" ).show();
					jQuery( "#show-link" ).hide();
					jQuery( "#underbar-show" ).hide();
					jQuery( "#hide-link" ).show();	
					jQuery( "#underbar-hide" ).show();
				}else {
					jQuery("#underbar_aboutDiv").hide();			   
					jQuery( "#underbar-container" ).show();	
					jQuery( "#underbar-related" ).show();	
					jQuery( "#underbar-controls" ).show();
					jQuery( "#show-link" ).hide();
					jQuery( "#underbar-show" ).hide();
					jQuery( "#hide-link" ).show();	
					jQuery( "#underbar-hide" ).show();	
					jQuery( "#underbar-reveal-hide" ).hide();
					jQuery( "#underbar-reveal-show" ).show();	
					jQuery( "#underbar-controls" ).addClass("underbar-controls-background");
					inactiveDots();
					activeDots();
				}
				jQuery('#underbar_noResultsDiv').hide();
			}
		}		
	}
	jQuery('#underbar-error').hide();	
}

/*
Tien 23/3/2012
when search textbox contains default value, click it, remove this value
*/
function removeDefaultText(){
	if (jQuery( "#underbar-error" ).css("display") != "none"){
		jQuery('#underbar-error').hide();
	}
	if(jQuery("#underbar-search-oxford-index").val() == "in Oxford Index"){
		jQuery( "#underbar-search-oxford-index" ).removeClass("underbar-search-text-color");
		jQuery("#underbar-search-oxford-index").val("");
	}
}

function truncateStr(_str, length) {
	var str = "";
	str = _str;
	if (str != null && jQuery.trim(str) != "") {
			if (str.length >= length) {
				str = str.substring(0, length - 2) + "...";
			}
	} else {
		str = "no result is available";
	}
	return str;
}

// begin added by vu.ngo - 3/20/2012
function runSlideShow(){
	jQuery(".underbar-slide-container").jCarouselLite({
        btnNext: ".underbar-next",
        btnPrev: ".underbar-prev",
        circular: false,
        visible: 3
    });
}
// end added by vu.ngo - 3/20/2012

function loadjs(url, callback){
    var script = document.createElement("script")
    script.type = "text/javascript";

    if (script.readyState){  //IE
        script.onreadystatechange = function(){
            if (script.readyState == "loaded" ||
                    script.readyState == "complete"){
                script.onreadystatechange = null;
                callback();
            }
        };
    } else {  //Others
        script.onload = function(){
            callback();
        };
    }

    script.src = url;
    document.getElementsByTagName("head")[0].appendChild(script);
}

function loadAllJs(callback){
	if(jsLibLoaded == scriptResources.length) {
		callback();
	} else {
		loadjs(resourceURL + scriptResources[jsLibLoaded], function(){jsLibLoaded++; loadAllJs(callback);});
	}
}

function loadCss( path, fn){
   var head = document.getElementsByTagName( 'head' )[0], // reference to document.head for appending/ removing link nodes
       link = document.createElement( 'link' );           // create the link node
   link.setAttribute( 'href', path );
   link.setAttribute( 'rel', 'stylesheet' );
   link.setAttribute( 'type', 'text/css' );

   var sheet, cssRules;
// get the correct properties to check for depending on the browser
   if ( 'sheet' in link ) {
      sheet = 'sheet'; cssRules = 'cssRules';
   }
   else {
      sheet = 'styleSheet'; cssRules = 'rules';
   }

   var timeout_id = setInterval( function() {                     // start checking whether the style sheet has successfully loaded
          try {
             if ( link[sheet] && link[sheet][cssRules] ) { // SUCCESS! our style sheet has loaded  (length)
                clearInterval( timeout_id );                      // clear the counters
                clearTimeout( timeout_id );
                cssLoaded = true;
                //fn.call( scope || window, true, link );           // fire the callback with success == true
             }
          } catch( e ) {} finally {}
       }, 10 ),                                                   // how often to check if the stylesheet is loaded
       timeout_id = setTimeout( function() {       // start counting down till fail
          clearInterval( timeout_id );             // clear the counters
          clearTimeout( timeout_id );
          head.removeChild( link );                // since the style sheet didn't load, remove the link node from the DOM
          //fn.call( scope || window, false, link ); // fire the callback with success == false
       }, 15000 );                                 // how long to wait before failing

   head.appendChild( link );  // insert the link node into the DOM and start loading the style sheet

   return link; // return the link node;
}
function  isChromeBrowser() {
	var  flag =  false;
    var  val =  navigator.userAgent.toLowerCase();		
	if(val.indexOf("chrome")  >  -1) {
		flag =  true;
	}
	return  flag;
}

// START QUY_HUYNH ADD_NEW 04/19/12
var targetCharArr = new Array('\'', '\"');
var encodeCharArr = new Array('&#39;', '&#34;');
function encodeTitle(str) {
	if (str != null && str != '') {		
		for (var key = 0; key < targetCharArr.length; key ++){
			str = str.replace(new RegExp(targetCharArr[key], 'g'), encodeCharArr[key]);			
		}		
	}
	return str;
}
// END QUY_HUYNH ADD_NEW 04/19/12


	// takes a query and splits it into context and query parts. 
	// works if the : is encoded or not. preserves :'s in the query. 
	function underbar_splitQueryString(q) {
		var retObj = {
			context: '',
			query: ''
		}
		if (q.charAt(0) === CONTEXT_DELIMITER) {
			var delimiter = CONTEXT_DELIMITER;
		} else if (q.substring(0,3) === CONTEXT_DELIMITER_ENCODED) {
			var delimiter = CONTEXT_DELIMITER_ENCODED;
		} 
		if (delimiter) {
			var splitQuery = q.split(delimiter);
			// string starts with delimiter, pretend it's a 1-indexed array below
			if (splitQuery.length > 1) {
				retObj.context = splitQuery[1];
				for (var i = 2; i < splitQuery.length; i++) {
					retObj.query = retObj.query + splitQuery[i];
					if (i < splitQuery.length - 1) {
						retObj.query = retObj.query + delimiter;
					}
				}
			}
		}
		return retObj;
	}
	
	function underbar_splitQueryArray(q) {
		var split = null;
		var retObj = {
			context: new Array(),
			query: new Array()
		};
		for (var i = 0; i < q.length; i++) {
			split = underbar_splitQueryString(q[i]);
			retObj.context.push(split.context);
			retObj.query.push(split.query);
		}
		return retObj;
	}

	function displayContentType(str) {
		if (str != null && str != '' && str == "Authority") {		
			return "Overview";	
		}
		return str;
	}
	
	// check if we have an empty query, or some variant thereof. 
	// this is "passive mode" and we can return no results without making a trip to the server. 
	// used to kick off a short circuit in callAjax
	function isUnderbarPassiveMode(query, defaultQuery) {
		var splitQueryArray = null;
		var splitQuery = null;
		if (jQuery.isArray(query)) {
			splitQueryArray = underbar_splitQueryArray(query);
		} else {
			splitQuery = underbar_splitQueryString(query);
		}
		var splitDefaultQuery = underbar_splitQueryString(defaultQuery);
		
		if (splitQueryArray !== null && splitQueryArray.query.length > 0 && splitQueryArray.query[0] !== '') {
			return false;
		}
		
		if (splitQuery !== null && splitQuery.query !== '') {
			return false;
		}
		
		if (splitDefaultQuery !== null && splitDefaultQuery.query !== '' && splitDefaultQuery.query !== 'default') {
			return false;
		}
		
		return true;
	}

