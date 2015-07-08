var gColMain, gCol2, gCol3, gIsMultiCol, gColTempResize;
var gColOrigHeights = { main: 0, col2: 0, col3: 0 };
var gColLows = { main: 0, col2: 0, col3: 0 };
var isIE6 = ($.browser.msie && ($.browser.version.substr(0,2) == '6.'));

/*['abstract','extract','excerpt']*/
var gSiteOptions = {
	popupViews: ["abstract"],
	popabsParam: "abspop=1",
	refPopupLinkTypes: ["medline"],
	refAbsPopupTimeout: 400,
	expandString: "+",
	contractString: "-",
	suppressDockedNav: false,
	suppressDockedSearchNav: true,
	enableCCIcons: false,
        dockedNavThisArticleLabel: "This Article",
	collapsibleLabels: ["h3","h4","span"],
	hasNewDockNav: false,
	isiLinkString: "Loading Web of Science citing article data...",
    'bam-ads': {
        'custom-css':
            {
            //'leaderboard': '/publisher/css/hw-publisher-leaderboard.css'
            }
    }
};
var gSiteOptionUnknown = 'UNKNOWN';

$(document).ready(function() {

	if ((typeof(gSmudge) == 'undefined') || (!gSmudge)) {
		smudge();
	}
        
	if ((typeof(gIsFrameset) == 'undefined') || (!gIsFrameset)) {
		if(top!= self) { top.location.href = self.location.href };
	}
	/* fix column heights */
	gColMain = $(getSiteOption('col1id', "#content-block"));
	gCol2 = $(getSiteOption('col2id', "#col-2"));
	gCol3 = $(getSiteOption('col3id',"#col-3"));
	gIsMultiCol = (gColMain.length && (gCol2.length || gCol3.length)) || ((gCol2.length && gCol3.length));
	gColTempResize = false;
	fixColHeights(0);
	/* force height recalc after 2 seconds because of unsize graphics elements */
	setTimeout("checkColHeights()", 2000);

	/* cleanup email addreses to replace with real mail2 links */
	$("span[class^='em']").add("span[id^='em']").each(
		function(i) {
			var spanClass = $(this).attr("class");
			var spanId = $(this).attr("id");
			/* allow em-link or em{\d+} */
			if ((spanClass != undefined) && (spanClass.match(/em((\d+)|(-link))/)) ||
					(spanId != undefined) && (spanId.match(/em\d+/)))
			{
				var addr;
				var addrEl = $(this).children(".em-addr");
				if (addrEl.length) {
					addr = addrEl.text().replace(/{at}/,'@');
				}
				else {
					addr = $(this).text().replace(/{at}/,'@');
				}
				var link = 'mailto:' + addr;
				var linkContents = $(this).attr("title");
				var newHtml = '';
				if ((linkContents == undefined) || !(linkContents.length)) {
					if ($(this).children("span.mail2-orig-content").length) {
						var tempSpan = $(this).children("span.mail2-orig-content");
						var classStr = '';

						var tempClassArr = tempSpan.attr("class").split(' ');
						if (tempClassArr.length > 1) {
							for (var i = 0; i < tempClassArr.length; i++) {
								if (tempClassArr[i] != 'mail2-orig-content') {
									classStr += (' ' + tempClassArr[i].replace(/^x-/,''));
								}
							}
						}
						linkContents = tempSpan.html().replace(/{at}/,'@');
						newHtml = '<a href="' + link + '"' +
							(classStr == '' ? '' : ('class="' + classStr + '"')) +
							'>' + linkContents + '</a>';
					}
					else {
						linkContents = addr;
					}
				}
				if (newHtml == '') {
					newHtml = '<a href="' + link + '">' + linkContents + '</a>';
				}
				$(this).replaceWith(newHtml);
			}
		}
	);
	handleccicons();
	
	/* make links with rel="external-nw" target a new window */
	$("a[rel*=external-nw]").each(
		function(i) {
			linkNewWin($(this), this);
		}
	);
	
	/* attach onFocus handlers to quick-search fields, to clear the
	   field when it receives focus IF it contains the default
	   value (such as "Search the site") */
	updateFormInput("#header-qs-search-label", "#header-qs-input", '', '');
	
	/* handle collapsing content-box areas, with user prefs */
	setupCollapsibles();
	
	/* handle "most" boxes */
	handleMostBoxes();
});


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

function setupCollapsibles() {
	// sites can override this if they want to target different elements
	prepCollapsibles("div.content-box div.collapsible");
}

/* handle collapsing content-box areas, with optional user prefs */
function prepCollapsibles(parentJQueryEl, setPrefs) {
	if (typeof(setPrefs) == "undefined") {
		setPrefs = true;
	}
	var expandStr, contractStr;
	if (gSiteOptions == undefined) {
		expandStr = '+';
		contractStr = '-';
	}
	else {
		if (gSiteOptions.cbExpandString != undefined) {
			expandStr = gSiteOptions.cbExpandString;
		}
		else if (gSiteOptions.expandString != undefined) {
			expandStr = gSiteOptions.expandString;
		}
		else { expandStr = '+'; }
		if (gSiteOptions.cbContractString != undefined) {
			contractStr = gSiteOptions.cbContractString;
		}
		else if (gSiteOptions.contractString != undefined) {
			contractStr = gSiteOptions.contractString;
		}
		else { contractStr = '-'; }
	}
	$(parentJQueryEl).each(
		function(i) {
			var $this = $(this);
			var id = $this.attr("id");
			if (id != null) {
				var $labelElement, $label;
				for (var i = 0; i < gSiteOptions.collapsibleLabels.length; i++) {
					$labelElement = gSiteOptions.collapsibleLabels[i];
					$label = $this.find($labelElement);
					if ($label.length) {
						// get first one
						if ($label.length > 1) {
							$label = $label.eq(0);
						}
						break;
					}
				}

				// if there's already a toggle leave this as is
				var alreadyHasToggle = ($label.length && $label.find("a.collapse-toggle").length);
				if ($label.length) {
					if (!(alreadyHasToggle)) {
						var labelText = $label.html();
						$label.empty().append('<a href="#" class="collapse-toggle"><span class="view-more">' + contractStr + '</span> ' + labelText + '</a>');
					}
				}

				var isOpen = true;
				if (setPrefs) {
					var statePref = getPrefValue(id + "-state");
					if (statePref && ((statePref == 'open') || (statePref == 'closed'))) {
						if (statePref == 'closed') {
							isOpen = false;
						}
					}
					else {
						// no pref, or unknown value
						if ($this.hasClass('default-closed')) {
							isOpen = false;
						}
					}
				}
				else {
						if ($this.hasClass('default-closed')) {
							isOpen = false;
						}
				}
				var childListType;
				if ($this.children("ol").length) {
					childListType = "ol";
				}
				else {
					childListType = "ul";
				}
				if (!isOpen && !(alreadyHasToggle)) {
					toggleCollapse($this, childListType, ($labelElement + " a span.view-more"), expandStr, contractStr);
				}
				$this.find("a.collapse-toggle").eq(0).click(
					function(e) {
						// need to find first parent that is in either state...
//						$(this).parents(".collapsible, .collapsed").each(
						$(this).parents().each(
							function(i) {
								if ($(this).hasClass('collapsible') || $(this).hasClass('collapsed')) {
									var isCollapsed = $this.hasClass('collapsed');
									if (setPrefs) {
										var prefName = id + "-state";
										if (isCollapsed) {
											setPref(prefName, "open");
										}
										else {
											setPref(prefName, "closed");
										}
									}
									toggleCollapse($(this), childListType, ($labelElement + " a span.view-more"), expandStr, contractStr);
									fixColHeights(-1);
									return false;
								}
							}
						);
						e.preventDefault();
					}
				);
			}
		}
	);
}

function handleMostBoxes() {
	var hadMostBoxes = false;
	$("div.most-links-box").each(
		function(i) {
			var $this = $(this);
			modClass($this, '', 'js-marker');
			hadMostBoxes = true;
			// 1) get the <ul> child
			var $mostlist = $this.children("ul");
			// 2) build a new <ul> for the header, from <h4> child:
			var hasSelected = false;
			var mostHdrList = null;
			if ($mostlist.length) {
				var hasItems = false;
				var hdrList = '<ul class="most-headings">';
				var $mostli = $mostlist.children("li");
				if ($mostli.length) {
					hasItems = true;
					$mostli.each(
						function(i) {
							var $hdr = $(this).children("h4").html();
							if ($(this).hasClass("most-cur-sel")) {
								hasSelected = true;
								hdrList += '<li class="' + $(this).attr("class") + '"><a href="#">' + $hdr + '</a></li>';
							}
							else {
								hdrList += '<li><a href="#">' + $hdr + '</a></li>';
							}
						}
					);
				}
				hdrList += '</ul>';
				if (hasItems) {
					var header = $this.find("div.most-header h3");
					if (header.length) {
						header.after(hdrList);
					}
				}
				mostHdrList = $this.find("div.most-header ul");
			}
			// 3) if none of the items are selected, make the first one be
			if (((mostHdrList != null) && mostHdrList.length) && (!hasSelected)) {
				modClass(mostHdrList.find("li:first"), "most-cur-sel", "");
				modClass($this.children("ul").children("li:first"), "most-cur-sel", "");
			}
			// 4) bind a handler to each heading li a to toggle class="most-cur-sel" for 
			//    that item and its corresponding item in the list below
			if (((mostHdrList != null) && mostHdrList.length)) {
				mostHdrList.find("li a").click(
					function(e) {
						var curA = $(this);
						toggleMostSelection(e, $this, curA.text());
					}
				);
			}
		}
	);
	if (hadMostBoxes) {
		fixColHeights(-1);
	}
}

function toggleMostSelection(e, mostItemDiv, groupName) {
	if (mostItemDiv.length) {
		var hdrItems = mostItemDiv.find("div.most-header ul li");
		if (hdrItems.length) {
			hdrItems.each(
				function() {
					var hdrName = $(this).text();
					var isChoice = (hdrName == groupName);
					if (isChoice) {
						modClass($(this), 'most-cur-sel', '');
					}
					else {
						modClass($(this), '', 'most-cur-sel');
					}
				}
			);
		}
		var listItems = mostItemDiv.children("ul").find("li");
		if (listItems.length) {
			listItems.each(
				function() {
					var itemName = $(this).children("h4").text();
					var isChoice = (itemName == groupName);
					if (isChoice) {
						modClass($(this), 'most-cur-sel', '');
					}
					else {
						modClass($(this), '', 'most-cur-sel');
					}
				}
			);
		}
	}
	fixColHeights(-1);
	e.preventDefault();
}

function toggleCollapse(collapsibleEl, hideTagExpr, modTextTagExpr, expandStr, contractStr) {
	if (typeof(expandStr) == "undefined") {
		expandStr = getSiteOption('expandString','+');
	}
	if (typeof(contractStr) == "undefined") {
		contractStr = getSiteOption('contractString','-');
	}

	var $this = collapsibleEl;
	var $toToggle = $this.find(hideTagExpr);
	if ($this.hasClass('collapsed')) {
		modClass($this, 'collapsible', 'collapsed');
		if ($toToggle.length) {
			$toToggle.eq(0).show();
		}
	}
	else if ($this.hasClass('collapsible')) {
		modClass($this, 'collapsed', 'collapsible');
		if ($toToggle.length) {
			$toToggle.eq(0).hide();
		}
	}
	var $rewrite = $this.find(modTextTagExpr);
	if ($rewrite.length) {
		$rewrite.eq(0).each(
			function(i, e) {
				var txt = $(e).text();
				if (txt == expandStr) {
					$(e).empty().append(contractStr);
				}
				else if (txt == contractStr) {
					$(e).empty().append(expandStr);
				}
			}
		);
	}
}

function setupDockBlock(col, dockId, dockClass, contentRules) {
	if ((col == 2) || (col == 3)) {
		var navOrigHeight = ((col == 2) ? gColOrigHeights.col2 : gColOrigHeights.col3);
		var gColNum = col;
		var gNav = ((col == 2) ? gCol2 : gCol3);
		var gNavHeight = ((gNav.length) ? navOrigHeight : 0);
		var gNavTopOffset =  (gNavHeight > 0 ? gNav.offset().top : 0);
		var gScrollPos = 0;
		var gNavDocked = false;
		/* this won't work in IE 6, so skip it */
		/* article navigation docking block */
		$(window).scroll(function () {
			if (gNavHeight > 0 && !isIE6) {
				var offsets = getPageOffset();
				var origHeight = ((gColNum == 2) ? gColOrigHeights.col2 : gColOrigHeights.col3);
				var navBottom = (gNavTopOffset + origHeight) - offsets.y;
				if (gScrollPos != offsets.y) {
					gScrollPos = offsets.y;
					if ((navBottom <= 0) && !gNavDocked) {
						/* dock the nav */
						gNavDocked = true;
						addDockBlock(col, dockId, dockClass, contentRules);
						addDockBlockCallback(dockId);
  $('ol#docked-nav-views a.pop-out-video').replaceWith('<a href="#pop-out-video-container" onclick="return fancybox(this)">Supplemental Media</a>');
					}
					else if (gNavDocked && (navBottom > 0)) {
						/* undock the nav */
						gNavDocked = false;
						removeDockBlock(col, dockId);
						removeDockBlockCallback(dockId);
					}
				}
			}
		});
	}
}
function addDockBlock(col, dockId, dockClass, contentRules) {
	// get direct children li elements only
	var colId = ("col-" + col);
	var newDiv = '<div' + ((dockId == '') ? '': (' id="' + dockId + '"')) + ((dockClass == '') ? '': (' class="' + dockClass + '"')) + '></div>';
	$("#" + colId).append(newDiv);
	$("#" + colId + " #" + dockId).hide();
	var newDivJQuery = $("#" + dockId);
	if (contentRules.length > 1) {
		for (var i = 0; i < (contentRules.length - 1); i = i + 2) {
			var addTo = processDockingRule(contentRules[i]);
			var add = processDockingRule(contentRules[i + 1]);
			var addTarget, addVal;
			if (addTo.ruleType == 'empty') {
				addTarget = newDivJQuery;
			}
			else if (addTo.ruleType == 'jQuery') {
				addTarget = $(addTo.rule);
			}
			if (add.ruleType = 'jQuery') {
				var addJQEl = $(add.rule);
				if (addJQEl.length) {
					addVal = addJQEl.clone();
				}
				else {
					addVal = '';
				}
			}
			else if (add.ruleType = 'html') {
				addVal = add.rule;
			}
			if (addTarget.length && !(addVal == '')) {
				addTarget.append(addVal);
			}
			else {
			}
		}
	}
	var newDockJQrule = "#" + colId + " #" + dockId;
	var newDock = $(newDockJQrule);
	var istoc = $(".hw-gen-page").attr("id").match (/toc/);
	if (newDock.length) {
		prepCollapsibles(newDockJQrule + " div.collapsible, " + newDockJQrule + " div.collapsed", false);
if (gSiteOptions.hasNewDockNav) {
		var issearchresults = $(".hw-gen-page").attr("id").match (/search-results/);
		if (!issearchresults) {
		if (istoc) {newDock.find ("#docked-cb").hide ();}
		newDock.prepend ($($(".sidebar-nav").get(0)).clone ());
}
}
		newDock.fadeIn(250);
	}
}

function processDockingRule(rule) {
	var retObj = new Object();
	retObj.empty = (((rule != undefined) && (!(rule == ''))) ? false : true);
	if (rule == '') {
		retObj.ruleType = 'empty';
	}
	else if (/^\$\(.+\)$/.test(rule)) {
		retObj.ruleType = 'jQuery';
		retObj.rule = rule.replace(/^\$\((.+)\)$/,"$1");
	}
	else {
		retObj.ruleType = 'html';
		retObj.rule = rule;
	}
	return retObj;
}

function removeDockBlock(col, dockId) {
	var dockedNav = $("div#" + dockId);
	if(dockedNav.length) {
		dockedNav.fadeOut(250, function() { dockedNav.remove(); });
	}
}
// custom implementations can override this function to do something when a dockBlock is added
// they should return false if they want to stop any additional default handling
function customAddDockBlockCallback(dockId) {
	return true;
}
// this function should not be overridden
function addDockBlockCallback(dockId) {
	if (customAddDockBlockCallback(dockId) != false) {
		// no default handling, currently
	}
}
// custom implementations can override this function to do something when a dockBlock is removed
// they should return false if they want to stop any additional default handling
function customRemoveDockBlockCallback(dockId) {
	return true;
}
// this function should not be overridden
function removeDockBlockCallback(dockId) {
	if (customRemoveDockBlockCallback(dockId) != false) {
		// no default handling, currently
	}
}

function updateFormInput(labelMatchString, inputMatchString, defaultColorString, textColorString) {
	if ((defaultColorString == null) || (defaultColorString == '')) {
		defaultColorString = "#A0A0A0";
	}
	if ((textColorString == null) || (textColorString == '')) {
		textColorString = "black";
	}
	var label = $(labelMatchString);
	var input = $(inputMatchString);
	if (input.length) {
		if ((label.length) && (input.val() == '')) {
			input.val(label.text()).css("color",defaultColorString);
		}
		input.focus(
			function(e) {
				if ((label.length) &&  ($(this).val() == label.text())) {
					$(this).val('').css("color",textColorString);
				}
			}
		);
		input.blur(
			function(e) {
				if ((label.length) && ($(this).val() == '')) {
					$(this).val(label.text()).css("color",defaultColorString);
				}
			}
		);
	}
	var parentForm = label.parents("form").eq(0);
	if (parentForm.length) {
		parentForm.submit(
			function() {
				if ((label.length) && (input.length) && (input.val() == label.text())) {
					input.val('');
				}
				return true;
			}
		);
	}
}

function checkUnloadedImgs(lookupRule) {
	if (lookupRule == null) {
		lookupRule = "img";
	}
	var imageNum = -1;
	var images = $(lookupRule);
	if (images.length) {
		imageNum = 0;
		images.each(
			function() {
				//if ($(this).height() == 0) {
				if (this.offsetHeight == 0) {
					imageNum++;
				}
			}
		);
	}
	return imageNum;
}

function fixHeightForImages(iter, numImagesToLoad, lookupRule) {
	if (lookupRule == null) {
		lookupRule = "img";
	}
	if (numImagesToLoad > 0) {
		var lastNumImagesToLoad = numImagesToLoad;
		var newNumImagesToLoad = checkUnloadedImgs(lookupRule);
		if (newNumImagesToLoad < lastNumImagesToLoad) {
			fixColHeights(1);
			if ((newNumImagesToLoad > 0) && (iter < 10)) {
				setTimeout("fixHeightForImages(" + (iter+1) + "," + newNumImagesToLoad + ",'" + lookupRule + "')", 1000);
			}
		}
	}
}
function getColInfo(colJQEl) {
	var colInfo = { valid: false, height: 0, bottom: 0, lastElBottom: 0, extra: 0, fix: false };
	if (colJQEl.length) {
		var c = colJQEl.children();
		if (c.length) {
			colInfo.height = getObjHeight(colJQEl);
			colInfo.bottom = colJQEl.offset().top + colInfo.height;
			var last = c.eq(c.length - 1);
			colInfo.lastElBottom = last.offset().top + getObjHeight(last);
			colInfo.extra = colInfo.bottom - colInfo.lastElBottom;
			colInfo.valid = true;
		}
	}
	return colInfo;
}
function checkColHeights() {
	var colToFix = 0;
	if ((gIsMultiCol || gColTempResize) && ((gColOrigHeights.main + gColOrigHeights.col2 + gColOrigHeights.col3) > 0)) {
		var colMainInfo = getColInfo(gColMain);
		var col2Info = getColInfo(gCol2);
		var col3Info = getColInfo(gCol3);
		if (colMainInfo.valid && (gColLows.main == 0)) { gColLows.main = colMainInfo.lastElBottom; }
		if (col2Info.valid && (gColLows.col2 == 0)) { gColLows.col2 = col2Info.lastElBottom; }
		if (col3Info.valid && (gColLows.col3 == 0)) { gColLows.col3 = col3Info.lastElBottom; }
		// check if low point in any column has changed
		if ((colMainInfo.valid) && (colMainInfo.lastElBottom != gColLows.main)) {
			colMainInfo.fix = true;
		}
		if ((col2Info.valid) && (col2Info.lastElBottom != gColLows.col2)) {
			col2Info.fix = true;
		}
		if ((col3Info.valid) && (col3Info.lastElBottom != gColLows.col3)) {
			col3Info.fix = true;
		}
		// check for columns not having same bottom points
		if ((colMainInfo.valid) &&
			  (((col2Info.valid) && (colMainInfo.height < col2Info.height)) ||
			   ((col3Info.valid) && (colMainInfo.height < col3Info.height)))) {
			colMainInfo.fix = true;
		}
		if ((col2Info.valid) &&
			  (((colMainInfo.valid) && (col2Info.height < colMainInfo.height)) ||
			   ((col3Info.valid) && (col2Info.height < col3Info.height)))) {
			col2Info.fix = true;
		}
		if ((col3Info.valid) &&
			  (((colMainInfo.valid) && (col3Info.height < colMainInfo.height)) ||
			   ((col2Info.valid) && (col3Info.height < col2Info.height)))) {
			col3Info.fix = true;
		}
		
		if (colToFix > -1) {
			if (colMainInfo.valid && colMainInfo.fix) {
				if ((col2Info.valid && col2Info.fix) || (col3Info.valid && col3Info.fix)) {
					colToFix = -1;
				}
				else { colToFix = 1; }
			}
			else if (col2Info.valid && col2Info.fix) {
				if (col3Info.valid && col3Info.fix) {
					colToFix = -1;
				}
				else { colToFix = 2; }
			}
			else if (col3Info.valid && col3Info.fix) {
				colToFix = 3;
			}
		}
		
		if (colToFix != 0) {
			fixColHeights(colToFix);
		}
		if (colMainInfo.valid) { gColLows.main = colMainInfo.lastElBottom; }
		if (col2Info.valid) { gColLows.col2 = col2Info.lastElBottom; }
		if (col3Info.valid) { gColLows.col3 = col3Info.lastElBottom; }
	}
	setTimeout("checkColHeights()", 5000);
}
function fixColHeights(colChanged) {
	if ((gIsMultiCol || gColTempResize) && getSiteOption('setColSizes', true)) {
		var setAll = false;
		if (colChanged == 1) {
			if (gColMain.length) {
				setObjHeight(gColMain,'auto');
				gColOrigHeights.main = getObjHeight(gColMain);
			}
		}
		else if (colChanged == 2) {
			if (gCol2.length) {
				setObjHeight(gCol2,'auto');
				gColOrigHeights.col2 = getObjHeight(gCol2);
			}
		}
		else if (colChanged == 3) {
			if (gCol3.length) {
				setObjHeight(gCol3,'auto');
				gColOrigHeights.col3 = getObjHeight(gCol3);
			}
		}
		else {
			if (colChanged == -1) {
				// force resize all 3
				if (gColMain.length) { setObjHeight(gColMain,'auto'); }
				if (gCol2.length) { setObjHeight(gCol2,'auto'); }
				if (gCol3.length) { setObjHeight(gCol3,'auto'); }
			}
			gColOrigHeights.main = ((gColMain.length) ? (getObjHeight(gColMain)) : 0);
			gColOrigHeights.col2 = ((gCol2.length) ? (getObjHeight(gCol2)) : 0);
			gColOrigHeights.col3 = ((gCol3.length) ? (getObjHeight(gCol3)) : 0);
			setAll = true;
		}
		if ((gColOrigHeights.main + gColOrigHeights.col2 + gColOrigHeights.col3) > 0) {
			var colInfo;
			var maxH = Math.max(Math.max(gColOrigHeights.main, gColOrigHeights.col2), gColOrigHeights.col3);
			if ((gColMain.length) && ((gColOrigHeights.main < maxH) || (getObjHeight(gColMain) > maxH) || setAll)) {
				setObjHeight(gColMain, maxH);
				colInfo = getColInfo(gColMain);
				if (colInfo.valid) { gColLows.main = colInfo.lastElBottom; }
			}
			if ((gCol2.length) && ((gColOrigHeights.col2 < maxH) || (getObjHeight(gCol2) > maxH) || setAll)) {
				setObjHeight(gCol2, maxH);
				colInfo = getColInfo(gCol2);
				if (colInfo.valid) { gColLows.col2 = colInfo.lastElBottom; }
			}
			if ((gCol3.length) && ((gColOrigHeights.col3 < maxH) || (getObjHeight(gCol3) > maxH) || setAll)) {
				setObjHeight(gCol3, maxH);
				colInfo = getColInfo(gCol3);
				if (colInfo.valid) { gColLows.col3 = colInfo.lastElBottom; }
			}
		}
	}
}

function getObjHeight(obj) {
	if (obj instanceof jQuery) {
		return obj.get(0).offsetHeight;
	}
	else if (obj instanceof Array) {
		return obj[0].offsetHeight;
	}
	else {
		return obj.offsetHeight;
	}
}
function getObjWidth(obj) {
	if (obj instanceof jQuery) {
		return obj.get(0).offsetWidth;
	}
	else if (obj instanceof Array) {
		return obj[0].offsetWidth;
	}
	else {
		return obj.offsetWidth;
	}
}
function setObjHeight(obj, h) {
	if (typeof(h) == 'number') {
		h = "" + h + "px";
	}
	if (obj instanceof jQuery) {
		obj.get(0).style.height = h;
	}
	else if (obj instanceof Array) {
		obj[0].style.height = h;
	}
	else {
		obj.style.height = h;
	}
}
function setObjWidth(obj, w) {
	if (typeof(w) == 'number') {
		w = "" + w + "px";
	}
	if (obj instanceof jQuery) {
		obj.get(0).style.width = w;
	}
	else if (obj instanceof Array) {
		obj[0].style.width = w;
	}
	else {
		obj.style.width = w;
	}
}

/* num pixels top of page has been scrolled offscreen */
function getPageOffset() {
	var offset = new Object();
  if( typeof( window.pageXOffset ) == 'number' ) {
    offset.x = window.pageXOffset;
    offset.y = window.pageYOffset;
  } else if( document.body && ( document.body.scrollTop ) ) {
    offset.x = document.body.scrollLeft;
    offset.y = document.body.scrollTop;
  } else if( document.documentElement && ( document.documentElement.scrollTop ) ) {
    offset.x = document.documentElement.scrollLeft;
    offset.y = document.documentElement.scrollTop;
  }
  if (typeof(offset.x)=="undefined") { offset.x = 0; }
  if (typeof(offset.y)=="undefined") { offset.y = 0; }
  return offset;
}
function getViewportDim() {
	var dim = new Object();
	// non-IE
	if (typeof window.innerWidth != 'undefined') {
		dim.x = window.innerWidth;
		dim.y = window.innerHeight;
	}
	// IE6 in standards compliant mode
	else if (typeof document.documentElement != 'undefined'
		&& typeof document.documentElement.clientWidth !=
		'undefined' && document.documentElement.clientWidth != 0) {
		dim.x = document.documentElement.clientWidth;
		dim.y = document.documentElement.clientHeight;
	}
	// older versions of IE
	else {
		dim.x = document.getElementsByTagName('body')[0].clientWidth;
		dim.y = document.getElementsByTagName('body')[0].clientHeight;
	}
	return dim;
}

function newWindowTargets() {
	var newWins = $("a.in-nw");
	if (newWins.length) {
		newWins.each(
			function() {
				var $this = $(this);
				$this.attr("target", "_blank");
				modClass($this, 'in-nw-vis', 'in-nw');
			}
		);
	}
}

function getSiteOption(optionName, defaultVal) {
	if (typeof(defaultVal) == "undefined") {
		defaultVal = gSiteOptionUnknown;
	}
	if (gSiteOptions == undefined) {
		return defaultVal;
	}
	else if (gSiteOptions[optionName] == undefined) {
		return defaultVal;
	}
	else {
		return gSiteOptions[optionName];
	}
}

function addPartHeaders(req) {
	req.setRequestHeader('Accept', 'application/xhtml+xml');
	req.setRequestHeader('Range', 'part=variant-contents');
}
function addCommonHeaders(req) {
	if (typeof(callbackToken) != 'undefined') {
		req.setRequestHeader('X-Token', callbackToken);
	}
}
function allowsCookies() {
	if (hasTestCookie()) {
		return true;
	}
	else {
		setTestCookie();
		return hasTestCookie();
	}
}
function setTestCookie() {
	setCookie('cks','allowed',7,'/',null,null);
}
function hasTestCookie() {
	var ckVal = getCookie('cks');
	if ((ckVal != null) && (ckVal == 'allowed')) {
		return true;
	}
	else {
		return false;
	}
}

var UIPrefsCk={
	name: "UIPrefs",
	expDays: 3652,
	path: '/'
};

function prefDefined(name) {
	var val = getPrefValue(name);
	if (val == null) {
		return false;
	}
	else {
		return true;
	}
}
function getPrefValue(name) {
	var prefArray = getPrefArray();
	if (prefArray) {
		name = convertPrefString(name);
		var match = name + ":";
		for (var i = 0; i < prefArray.length; i++) {
			if (prefArray[i].indexOf(match) == 0) {
				return prefArray[i].substring(match.length);
			}
			else if (prefArray[i] == name) {
				// name only, no value, return boolean true
				return true;
			}
		}
	}
	return null;
}
function convertPrefString(str) {
	if (str) {
		return str.replace(/[,:=]/g,"");
	}
	return str;
}
function removePref(name) {
	var prefArray = getPrefArray();
	name = convertPrefString(name);
	if (prefDefined(name)) {
		var newArray = new Array(prefArray.length - 1);
		var match = name + ":";
		var newArrIndex = 0;
		for (var i = 0; i < prefArray.length; i++) {
			if (!((prefArray[i].indexOf(match) == 0) || (prefArray[i] == name))) {
				newArray[newArrIndex++] = prefArray[i];
			}
		}
		setPrefCookie(newArray);
		if (prefArray.length == 1) {
			return null;
		}
		else {
			return newArray;
		}
	}
	else {
		return prefArray;
	}
}

function setPref(name, value) {
	if (typeof(value) == "undefined") {
		value = null;
	}
	if (name) {
		name = convertPrefString(name);
		var prefArray = removePref(name);
		if (prefArray == null) {
			prefArray = new Array;
		}
		var newArray = new Array(prefArray.length + 1);
		var newPref = name + (((value != null) && (value != '')) ? (':' + value) : '');
		newArray[0] = newPref;
		for (var i = 0; i < prefArray.length; i++) {
			newArray[i+1] = prefArray[i];
		}
		setPrefCookie(newArray);
		return newArray;
	}
	else {
		return getPrefArray();
	}
}
function setPrefCookie(prefs) {
	if (prefs && (prefs.length > 0)) {
		var prefString;
		if (typeof(prefs) == 'string') {
			prefString = prefs;
		}
		else {
			if (prefs.length == 1) {
				prefString = prefs[0];
			}
			else {
				prefString = prefs.join(',');
			}
		}
		setCookie(UIPrefsCk.name, prefString, UIPrefsCk.expDays, UIPrefsCk.path, false, false);
	}
	else {
		deleteCookie(UIPrefsCk.name, UIPrefsCk.path, false);
	}
}
// individual pref items in the cookie are separated by ',' and
// nv pref pairs are joined by ':', i.e. n1:v1,n2:v2,n3:v3,etc.
// values are optional. (i.e. "n1,n2:v2,n3" is ok)
function getPrefArray() {
	var cookieVal = getCookie(UIPrefsCk.name);
	if (cookieVal != null) {
		return cookieVal.split(',');
	}
	return null;
}

// http://www.dustindiaz.com/top-ten-javascript/
function getCookie( name ) {
	var start = document.cookie.indexOf( name + "=" );
	var len = start + name.length + 1;
	if (((!start ) && (name != document.cookie.substring( 0, name.length ))) || (start == -1)) {
		return null;
	}
	var end = document.cookie.indexOf( ';', len );
	if ( end == -1 ) end = document.cookie.length;
	return unescape( document.cookie.substring( len, end ) );
}
function setCookie( name, value, expires, path, domain, secure ) {
	var today = new Date();
	today.setTime( today.getTime() );
	if ( expires ) {
		expires = expires * 1000 * 60 * 60 * 24;
	}
	var expires_date = new Date( today.getTime() + (expires) );
	document.cookie = name+'='+escape( value ) +
		( ( expires ) ? ';expires='+expires_date.toGMTString() : '' ) +
		( ( path ) ? ';path=' + path : '' ) +
		( ( domain ) ? ';domain=' + domain : '' ) +
		( ( secure ) ? ';secure' : '' );
}

function deleteCookie( name, path, domain ) {
	if ( getCookie( name ) ) document.cookie = name + '=' +
			( ( path ) ? ';path=' + path : '') +
			( ( domain ) ? ';domain=' + domain : '' ) +
			';expires=Thu, 01-Jan-1970 00:00:01 GMT';
}
function modClass(jQueryEl, addClass, removeClass) {
	if (jQueryEl.length) {
		var exClass = jQueryEl.attr("class");
		var classArr = new Array;
		if ((exClass != undefined) && (exClass != '')) {
			classArr = exClass.split(' ');
		}
		var newClass = '';
		var addClassExisted = false;
		for (var i = 0; i < classArr.length; i++) {
			var classPart = classArr[i];
			if (classPart != '') { 
				if (classPart != removeClass) {
					if (classPart == addClass) {
						addClassExisted = true;
					}
					newClass = addToDelimString(newClass, classPart, ' ');
				}
			}
		}
		if (!addClassExisted) {
			newClass = addToDelimString(newClass, addClass, ' ');
		}
		jQueryEl.attr("class",newClass);
	}
}
function addToDelimString(origString, newPart, delim) {
	var newString;
	if ((origString == undefined) || (origString == '')) {
		newString = newPart;
	}
	else {
		newString = origString + delim + newPart;
	}
	return newString;
}
function debugOut(msg) {
	if(window.console) {
		window.console.log(msg);
	} 
	/*
	else {
		alert(msg);
	}
	*/
}

    function is_defined( variable)
    {
        return (typeof(window[variable]) == "undefined")?  false: true;
    }

function fancybox(elem) {
elem = $(elem);
if (!elem.data("fancybox")) {
    elem.fancybox({
        'overlayColor' : '#000',
        'overlayOpacity' : 0.5
    });
    elem.fancybox().trigger('click');
    elem.data("fancybox", true);
}
return false; 
}
function handleccicons() {
 if (gSiteOptions.enableCCIcons == true) {
 var allCits = $("li.cit");
 var contentpage = $("span.ccv");
 var allpapCits = $("div.cit");
        if (!(allCits.length)) {
  allCits = allpapCits;
 }
 if (allCits.length) {
  allCits.each(
   function(i) {
    var permissionsLink;
    var $thisCit = allCits.eq(i);
    var creativeCommonsArticle = $thisCit.hasClass("creative-commons");
    var creativeCommonsLicenseClass = $thisCit.attr("class");

    var creativeCommonsLicenseValue = creativeCommonsLicenseClass.match(/creative-commons-\S+/);
    var creativeCommonsLicenseNumber;
    if (creativeCommonsLicenseValue != undefined && creativeCommonsLicenseValue.length)
    {
     creativeCommonsLicenseNumber = creativeCommonsLicenseValue[0].replace(/creative-commons-/, '');
    }
    var openAccessArticle = $thisCit.hasClass("openaccess");
     if (creativeCommonsArticle || openAccessArticle){
      if (creativeCommonsLicenseNumber != "" || creativeCommonsLicenseNumber != undefined)
      {
      cciconslink= '<a href="http://creativecommons.org/licenses/' + creativeCommonsLicenseNumber + '" class="creative-commons-js in-nw"><img src="http://i.creativecommons.org/l/' + creativeCommonsLicenseNumber + '/80x15.png" /></a>';
      cciconslinkOther = '<div class="cc-icons-link"><a href="http://creativecommons.org/licenses/' + creativeCommonsLicenseNumber + '" class="creative-commons-js in-nw"><img src="http://i.creativecommons.org/l/' + creativeCommonsLicenseNumber + '/80x15.png" /></a></div>';

      if ($thisCit.find("span.cit-flags").length > 0) {
       $thisCit.find("span.cit-flags").append(cciconslink);
      }
       else {
       $thisCit.find("div.cit-extra").append(cciconslinkOther);
      }
     }
   }
  });
  }
 if (contentpage.length) {
    var permissionsLink;
    var $thisCit = contentpage;
    var creativeCommonsArticle = $thisCit.hasClass("ccv");
    var creativeCommonsLicenseClass = $thisCit.attr("class");

    var creativeCommonsLicenseValue = creativeCommonsLicenseClass.match(/cc-version-\S+/);
    var creativeCommonsLicenseNumber;
    if (creativeCommonsLicenseValue != undefined && creativeCommonsLicenseValue.length)
    {
     creativeCommonsLicenseNumber = creativeCommonsLicenseValue[0].replace(/cc-version-/, '');
    }
    var openAccessArticle = $thisCit.hasClass("openaccess");
     if (creativeCommonsArticle || openAccessArticle){
      if (creativeCommonsLicenseNumber != "" || creativeCommonsLicenseNumber != undefined)
      {
      cciconslink= '<a href="http://creativecommons.org/licenses/' + creativeCommonsLicenseNumber + '" class="creative-commons-js in-nw"><img src="http://i.creativecommons.org/l/' + creativeCommonsLicenseNumber + '/80x15.png" /></a>';
      cciconslinkOther = '<div class="cc-icons-link"><a href="http://creativecommons.org/licenses/' + creativeCommonsLicenseNumber + '" class="creative-commons-js in-nw"><img src="http://i.creativecommons.org/l/' + creativeCommonsLicenseNumber + '/80x15.png" /></a></div>';

      if ($thisCit.length > 0) {
       $thisCit.append(cciconslink);
      }
     }
    }
   }
 }
}

function smudge() {
    var fp1 = new Fingerprint().get();
    if (fp1 != null) {
        $.ajax({
          'type' : "GET",
          'url' : '/smudge',
          'data' : {'ub' : fp1},
          success: function(data) { }
          });
    }
}
