$(document).ready(function() {

/*Test for at least two levels*/
var TestHierarchy = $('.oup-collections .results').find('.coll-2').text();

if (TestHierarchy.length)
{
	$('.oup-collections .results').each(function(){
		$(this).addClass('arrows');
	});

	$('.oup-collections div.results>ul').each(function(){
		$(this).addClass('clicktarget');
	});

}

$('.oup-collections .clicktarget').click(function() {
	$(this).parent().toggleClass('contracted');
});


$('.hw-pub-sertitle-fasttrack').each(function(){
var selectedTagForIcon = $(this);
selectedTagForIcon.empty();
var whichGif = '/resource/image/fasttrack.png';
selectedTagForIcon.before('<img class="sertitle-gif-by-js" src="' + whichGif + '" \/>');
});

$('.sub-article-title').each(function(){
var selectedTagForBullet = $(this);
var whichBullet = '/publisher/img/bullet.gif';
selectedTagForBullet.before('<img class="sub-article-title-bullet-js" src="' + whichBullet + '" \/>');
});

var MathTocClass =  $('.math-toc').text();

if (MathTocClass.length) {
$('ol.results-cit-list').addClass('math-toc');
}


 $('#site-breadcrumbs').each(function(){
 var selectedTagForBreadcrumbs = $(this);
 var emptyBreadcrumbLi = selectedTagForBreadcrumbs.children("li:empty");
 emptyBreadcrumbLi.addClass('empty');
 });

$("li span.breadcrumb_subjects").append(' <span class="ampersand">&</span> ');
$("#site-breadcrumbs li span:last-child span.ampersand").empty();
$("#site-breadcrumbs .issue-value").prev().append('<span class="vol-issue-comma">,</span>');

var authorIndexLen = $("#pageid-authindex #content-block div.aindex-jump-list").nextAll().length;
if (authorIndexLen == 0) {
       $("#pageid-authindex #content-block div.aindex-jump-list").after('<p class="empty-data">No Data Available</p>');
}

 $('#pageid-pap-bycustom').each(function(){
 var selectedTagForMessage = $('#pap-header');
 var selectedTagForTest = $('.cit-metadata');

 if (!(selectedTagForTest.length))
 {
 selectedTagForMessage.append('There are currently no articles with special topics.');
 }
 });

 gSiteOptions.suppressDockedSearchNav=false;
  
  var content = $("div#content-block"),
    collAlertForm = ($('form', content).attr('action'))? $('form', content).attr('action').match('/cgi/alerts/collalert') : null; //$("form[action contains '/cgi/alerts/collalert']", content)
  if(typeof(collAlertForm) != "undefined" & collAlertForm != null) {
    if(collAlertForm.length > 0) {
      //alert('alert form exist');
      var checkboxes = $('input:checkbox', content);
      // include a selectbox to SELECT-ALL
      $('dl:first', content).before('<div class="selectallcheck"><input type="checkbox" class="selectall">SELECT ALL</input></div>');
    
      //Event Listener for the checkbox
      $('input[type=checkbox].selectall').click(function() {
        if($(this).is(':checked')) {
          //alert('select all');
          selectAll(true);
        } else {
          //alert('deselect all');
          selectAll(false);
        }

        function selectAll(flag) {
          checkboxes.each(function() {
            $(this).attr('checked',flag);
          });
        }
      });
    }
  };

$('ul.social-bookmark-links a').attr('TARGET','_BLANK');

});


