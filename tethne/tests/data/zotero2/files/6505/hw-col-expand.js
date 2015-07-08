var gViewportW = 0;
var gDockedBoxLeft = 515;
var gDockedBoxNoColsLeft = 950;
var gColExpandDocked = false;
var gHeaderScrollPos = 0;
var gSuppressColExpand = false;

$(document).ready(function() {
	if (!(gSuppressColExpand)) {
		var isIE6 = ($.browser.msie && ($.browser.version.substr(0,2) == '6.'));
	
		$("div#content-block").prepend('<div id="content-option-box" title="Expand this column"><ul><li id="content-toggle"><a href="#"><span class="descr">Expand</span><span>+<\/span><\/a><\/li><\/ul><\/div>');
	
		if (isIE6) {
			$("div#content-option-box li#content-toggle a").css("display","inline");
		}
	
		$("div#content-option-box li#content-toggle a").click(
			function(e) {
				var pageDiv = $("div.hw-gen-page");
				if (pageDiv.length) {
					var optionbox = $("div#content-option-box");
					var colsHidden = pageDiv.hasClass("hide-cols");
					if (colsHidden) {
						// show all columns
						modClass(pageDiv,'','hide-cols');
						modClass($(this),'','expanded');
						$("div#cols-min").remove();
						gIsMultiCol = true;
						if (optionbox.length) {
							optionbox.attr("title","Expand this column");
							optionbox.find("span.descr").text("Expand");
						}
						checkDockedColExpandLoc(true, 0);
						fixColHeights(-1);
					}
					else {
						// hide sidebar columns
						gIsMultiCol = false;
						modClass(pageDiv,'hide-cols','');
						modClass($(this),'expanded','');
						if (optionbox.length) {
							optionbox.attr("title","Show all columns");
							optionbox.find("span.descr").text("Minimize");
						}
						checkDockedColExpandLoc(true, 0);
						var colDivs = '<div id="cols-min">';
						for (var i=3; i>=2; i--) {
							var col = $("div#col-" + i);
							if (col.length) {
								colDivs = colDivs + '<div id="col-' + i + '-min"><span class="view-more"> <\/span><\/div>';
							}
						}
						colDivs = colDivs + '<\/div>';
						$("div#content-block").before(colDivs);
						var mincol, mincolspan;
						for (var j = 2; j <= 3; j++) {
							mincol = $("div#col-" + j + "-min");
							mincolspan = $("div#col-" + j + "-min span.view-more");
							if (mincol.length && mincolspan.length) {
								
								// call publisher cleanup function
								if (typeof localColMinF == 'function') {
									localColMinF(mincol, j);
								}
								var x = j;
								//var colid = "col-" + x;
								mincolspan.hover(
									function() {
										var parentid = $(this).parent().attr("id");
										//var closebox = "<div id='col-hover-close'><a href='#'>x</a></div>";
										if (parentid != null) {
											var colstr = "div#" + parentid.substring(0,parentid.indexOf('-min'));
											var col = $(colstr);
											if (col.length) {
												//col.prepend(closebox);
												var header = $("#header");
												var headerHeight = (header.length ? getObjHeight(header) : 0);
												var leaderboard = $("div.leaderboard-ads");
												var leaderboardHeight = (leaderboard.length ? getObjHeight(leaderboard) : 0);
												var totalHeight = headerHeight + leaderboardHeight;
												col.css("top", '' + totalHeight + "px");
												modClass(col,"palette","");
												col.css("height","auto");
												/*
												$("#col-hover-close a").click(
													function(e) {
														var ancestors = $(this).parents();
														modClass(ancestors.eq(1), "", "palette");
														$("#col-hover-close").remove();
														e.preventDefault();
													}
												);
												*/
												col.hover(
													function() {},
													function() {
														modClass($(this),"","palette");
														//$("#col-hover-close").remove();
														$(this).css("top",'');
	
													}
												);
											}
										}
									},
									function() {}
								);
							}
							else {
							}
						}
						gColTempResize = true;
						fixColHeights(-1);
						gColTempResize = false;
					}
				}
				e.preventDefault();
			}
		);

		if ($("#force-col-expand").length) {
			$("div#content-option-box li#content-toggle a").click();
		}
			
		/* article navigation docking block */
		/* this won't work in IE 6, so skip it */
		if (!isIE6) {
			gViewportW = getViewportDim().x;
			checkDockedColExpandLoc(true, 2000);
			checkColExpandDocking();
			$(window).scroll(function() { checkColExpandDocking(); });
		}
	}
});

function checkColExpandDocking() {
	var header = $("#header");
	var headerTopOffset = (header.length ? header.offset().top : 0);
	var headerHeight = (header.length ? getObjHeight(header) : 0);
	if (headerHeight > 0) {
		var offsets = getPageOffset();
		var headerBottom = (headerTopOffset + headerHeight) - offsets.y + 50;
		if (gHeaderScrollPos != offsets.y) {
			gHeaderScrollPos = offsets.y;
			if ((headerBottom <= 0) && !gColExpandDocked) {
				/* dock the col expand button */
				gColExpandDocked = true;
				addDockedColExpand();
				checkDockedColExpandLoc(true, 0);
			}
			else if (gColExpandDocked && (headerBottom > 0)) {
				/* undock the col expand button */
				gColExpandDocked = false;
				removeDockedColExpand();
			}
		}
	}
}
function addDockedColExpand() {
	var optionbox = $("div#content-option-box");
	if (optionbox.length) {
		optionbox.hide().addClass('option-box-docked').fadeIn(250);
	}
}
function checkDockedColExpandLoc(forceLocate, timerLen) {
	if (gColExpandDocked) {
		var newViewportW = getViewportDim().x;
		if (forceLocate || (newViewportW != gViewportW)) {
			var dockedExpand = $("div#content-option-box");
			if (dockedExpand.length) {
				var newLeft = $("#content-block").offset().left +
					(gIsMultiCol ? gDockedBoxLeft : gDockedBoxNoColsLeft);
				if ((newViewportW - 50) < newLeft) {
					newLeft = (newViewportW - 50);
				}
				dockedExpand.css("left", ('' + newLeft + 'px'));
			}
			gViewportW = newViewportW;
		}
	}
	if (timerLen && (timerLen > 0)) {
		checkColExpandDocking();
		setTimeout("checkDockedColExpandLoc("+ forceLocate + "," + timerLen + ")", timerLen);
	}
}

function removeDockedColExpand() {
	var optionbox = $("div#content-option-box");
	if (optionbox.length) {
		optionbox.removeClass('option-box-docked');
	}
}
