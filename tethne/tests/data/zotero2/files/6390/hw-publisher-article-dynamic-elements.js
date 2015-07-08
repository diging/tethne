$(document).ready(function(){
var termsUrl = "http://www.oxfordjournals.org/our_journals/" + encodeURIComponent(gJournalVars.oupcode) + "/terms.html";
 var anchorElement;
 anchorElement = document.createElement('a');
 anchorElement.setAttribute('href', termsUrl);
 anchorElement.setAttribute('class', 'terms');

 $('.copyright-statement').each(function(){
	if($('div#pageid-content.ios-device').length < 1)
	{
		 var selectedTagForCopyright = $(this);
		 selectedTagForCopyright.wrapInner(anchorElement);
	}
 });

 $('.license').each(function(){
 var selectedTagForLicense = $(this);
 selectedTagForLicense.wrap(anchorElement);
 });

 $('#cb-art-soc ol>li:first-child a').each(function(){
/*Removes 'Email this article' text in content box section 'Shared' */
 var EmailThisArticle = $(this).empty();

/*Adds hover text to email-friend icon that matches social bookmarking text */
 EmailThisArticle.attr('title', 'email this');
   
 });

   liElement = document.createElement('li');
   aElement = document.createElement('a');
   aElement.setAttribute('href', '#glossary-1');


   $('.glossary').each(function(){

        var selectedTagForText = $(this);
        var selectedTagForTextText = selectedTagForText.children("h2:first").text();
	var selectedTagForAbbr =  $('#cb-art-nav');         
	var olFirstChildTag = selectedTagForAbbr.children("ol:first");

        if (selectedTagForTextText.length) {
		aElement.appendChild(document.createTextNode(selectedTagForTextText))

	} else {
   		aElement.appendChild(document.createTextNode('Abbreviations'));
	}
              
	liElement.appendChild(aElement);
	olFirstChildTag.append(liElement);

 });

 var uniqueClass =  $('.slug-doi').text().replace(/\//g, "");
 $('#content-block').addClass(uniqueClass);

});


