		var domain = "http://global.oup.com";
		//var domain = "http://global.uat.oup.com";
		//var domain = "http://global.edt.uk.oup.com";
		var cookieWsUrl = domain+"/cookiealert";
		var cookiePolicyUrl = domain+"/cookiepolicy/";
		var version = "/0";
		var cookieDate = "/01-01-2000";
		var preferredLanguage = "";
		var cookieName = "oup-cookie";
		var databaseVersion = "0";
		var cookieOlderThanSpecificDays = true;

		var ie6Message = "<div id=\"oupcookiepolicy_message\" class=\"cookiepolicyimplied\"><div class=\"cookiepolicytext\">We use cookies to enhance your experience on our website. By clicking 'continue' or by continuing to use our website, you are agreeing to our use of cookies. You can change your cookie settings at any time.</div><ul class=\"cookiepolicylinks\"><li><a href=\"#\" onClick=\"window.location.reload( true );\" class=\"cookiepolicycontinue\" title=\"Close this message\">Continue</a></li><li><a href=\"http://global.oup.com/cookiepolicy/\" target=\"_blank\" class=\"cookiepolicymore\" title=\"How we use cookies on this site\">Find out more</a></li></ul><div class=\"cookiepolicyend\"></div></div>";

		try {
			var _cookiepolicy = jQuery;                     
		} catch(e) {
		try {
			var _cookiepolicy = $;                         
		} catch(e) {
			}
		}   
		//_cookiepolicy = _cookiepolicy.noConflict();		
		//alert('pointing to : '+domain);		
		//alert(' variable conflict. =====>  :'+_cookiepolicy +'    cookiePolicyUrl :'+cookiePolicyUrl+'   oupcookiepolicy_messagetype :'+oupcookiepolicy_messagetype);

		// uncomment the below line for testing with implied consent.

		//oupcookiepolicy_messagetype='explicit';

		_cookiepolicy(document).ready(function() {

		writeTheElements();
		getTheCookie();

		if(oupcookiepolicy_messagetype == 'explicit'){

			if (typeof _cookiepolicy.oupcookiepolicy_fancybox == 'function') {
				//alert('allready loaded');
				_cookiepolicy("a#cookiepolicy_link").oupcookiepolicy_fancybox({
					'hideOnContentClick': false,
					'hideOnOverlayClick':false
				});
				_cookiepolicy("a.group").oupcookiepolicy_fancybox({
					'transitionIn'	:	'elastic',
					'transitionOut'	:	'elastic',
					'speedIn'		:	600, 
					'speedOut'		:	200, 
					'overlayShow'	:	false
				});							
			} else {
				//alert('fancybox object not available.');
			}
		}

			try{
				if(cookieOlderThanSpecificDays){
					checkForAlertMessage();
				}else{
				}
			}catch(e){
				var keyword= '/cookiepolicy/';
				alertMessageToDisplay=htmlDecode(ie6Message);
				if(alertMessageToDisplay.indexOf(keyword) != -1) {
						var alertMessageToDisplay1= alertMessageToDisplay.substring(0, alertMessageToDisplay.indexOf(keyword));
						var alertMessageToDisplay2= alertMessageToDisplay.substring(alertMessageToDisplay.indexOf(keyword)+keyword.length, alertMessageToDisplay.length);
						alertMessageToDisplay = alertMessageToDisplay1+keyword+"?siteid="+oupcookiepolicy_siteid+alertMessageToDisplay2;
				}
				var p = document.createElement("div");
				p.innerHTML = alertMessageToDisplay;
				document.body.insertBefore(p, document.body.firstChild);
				saveCookie(1);
			}
		});	
		
		function writeTheElements(){
			var element = document.createElement("div");
			element.innerHTML = "<div id=\"cookiepolicy_div\"><a id=\"cookiepolicy_link\" href=\"#cookiepolicy_data\"></a><div id=\"cookiepolicy_parent\"style=\"display:none\"><div id=\"cookiepolicy_data\"></div></div></div>";
			document.body.insertBefore(element, document.body.firstChild);
		}
		
		
		function getTheCookie(){
			var  browserLanguage = window.navigator.userLanguage;
			if(browserLanguage==undefined){
				browserLanguage = window.navigator.language;
			}		
			browserLanguage = browserLanguage.substring(0,2); 
			//preferredLanguage = "/"+browserLanguage;
			var metaLanguage = metaKeywords();
			if(oupcookiepolicy_preferredlanguage != '' && oupcookiepolicy_preferredlanguage != ' ' && oupcookiepolicy_preferredlanguage != "undefined" && oupcookiepolicy_preferredlanguage.length > 0)	{
				preferredLanguage = "/"+oupcookiepolicy_preferredlanguage;
				//alert('oupcookiepolicy_preferredlanguage :'+preferredLanguage);				
			} else if(metaLanguage != '' && metaLanguage != "undefined") {
				metaLanguage = metaLanguage.substring(0,2); 			
				preferredLanguage = "/"+metaLanguage;
				//alert('metaLanguage :'+preferredLanguage);				
			} else if(browserLanguage != '' && browserLanguage != "undefined") {
				browserLanguage = browserLanguage.substring(0,2); 
				preferredLanguage = "/"+browserLanguage;
				//alert('browserLanguage :'+preferredLanguage);
			}
			if(preferredLanguage == '' || preferredLanguage =='undefined') {
				preferredLanguage = '/en';
			}
			//alert('final preferredLanguage :'+preferredLanguage);

			var allcookies = document.cookie; 
			//alert('The Cookies ' + allcookies);
			cookiearray  = allcookies.split(';');
		    for(var i=0; i<cookiearray.length; i++){				  
				var name = cookiearray[i].split('=')[0];
				var value = cookiearray[i].split('=')[1];
				if(name.indexOf(cookieName) != -1)
				{	
					if(value.split('_')[0] == ""){
						version = "/0";
					}else{
					version = "/"+ value.split('_')[0]; 
					}
					var deviceCookieDate = value.split('_')[1];
					var deviceCookieDateString = constructDateString(deviceCookieDate); 
					var deviceDate = new Date(deviceCookieDateString);
					var currentDate = new Date(); 
					var difference = currentDate - deviceDate; 
					if(difference > 90*24*60*60*1000){						
						cookieOlderThanSpecificDays = true;
					}else{										
						cookieOlderThanSpecificDays = false;
					}
					cookieDate = "/"+ value.split('_')[1];
				}
		   }
		}
		
		function metaKeywords() { 
			var metaLang = '';
			metaCollection = document.getElementsByTagName('meta'); 

			for (i=0;i<metaCollection.length;i++) { 
				nameAttribute = metaCollection[i].name.search(/language/);
				if (nameAttribute!= -1) { 
					metaLang = metaCollection[i].content;
					//alert(metaCollection[i].content); 
				} 
			} 
			return metaLang;
		} 
			
		function constructDateString(date){
			try{
				var day = date.split('-')[0];
				var month = date.split('-')[1];
				var year = date.split('-')[2];
				return (year+","+month+","+day);
			}catch(e){
				
			}
		}
		

		function checkForAlertMessage(){
			var request1 = null;
			var wsresponse = false;
			request1 = createCORSRequest("GET",cookieWsUrl + preferredLanguage + version + cookieDate,true);
			//alert('checkForAlertMessage request2 after : '+request1);
			if (typeof XDomainRequest != "undefined") {
				//alert('XDomainRequest 1 : '+XDomainRequest);
				request1.onprogress = function () { };
				request1.ontimeout = function () { };
				request1.onerror = function () { };
				
				request1.onload=function()	{
						wsresponse = request1.responseText;
						//alert(' wsresponse XDomainRequest 12 : '+wsresponse);
						if(wsresponse == 'true'){
							getAlertMessage();						
						} else {
						}
				};
				setTimeout(function () {
					request1.send();
				}, 0);
			} 
			else if(window.ActiveXObject) // for IE 7, 8 
			{
				//alert('inside checkForAlertMessage else window.ActiveXObject request1.readyState :'+request1);
				request1.onreadystatechange=function() {
					//alert('request1.readyState 213 :'+request1.readyState);
					//alert('request1.status 123:'+request1.status);					
					if (request1.readyState==4 && request1.status== 200 ) {
						wsresponse = request1.responseText;
						//alert(' wsresponse XDomainRequest 123456 : '+wsresponse);
						if(wsresponse == 'true') {
							getAlertMessage();						
						} else {
						}
					}
				};
				request1.send();	
			} else {
				try	{
					request1.onreadystatechange=function()	{
						//alert('5 request2.readyState :'+request1.readyState);
						//alert('5 request2.status :'+request1.status);					
						if (request1.readyState==4  ) {    
							wsresponse = request1.responseText;
							//alert(' 5 wsresponse XDomainRequest 123 : '+wsresponse);
							if(wsresponse == 'true'){
								getAlertMessage();						
							}else{ 
							}
						}
					};
					request1.send();	
				} catch(e) {
				//alert('5 Exception : '+e);
				}
			}
			
		}
		
		function getAlertMessage(){	
			var request2 = null;
			var response = "";
			var isMessagePrinted= false;
			request2 = createCORSRequest("GET",cookieWsUrl + preferredLanguage +"/"+ oupcookiepolicy_messagetype ,true);
			//alert('getAlertMessage request2 after 123: '+request2);
			 
			if (typeof XDomainRequest != "undefined"){
				//alert('XDomainRequest : '+XDomainRequest);
				request2.onload = function()
				{
					if (!isMessagePrinted)
					{
						isMessagePrinted = true;
						response = request2.responseText;
						//alert('response 1 1 :'+response);
						generateAlertMessage(response);
					}
				};
				request2.send();
			}  else	if(window.ActiveXObject) // for IE 7, 8 
			{
				//alert('getAlertMessage with window.ActiveXObjec 123:'+request2);
				request2.onreadystatechange=function()	{			
					if (request2.readyState==4 && request2.status== 200 )
					{
						isMessagePrinted = true;
						response = request2.responseText;
						//alert('response 1 2 :'+response);
						generateAlertMessage(response);
					}
				};
				request2.send();
			}
			else {
				request2.onreadystatechange=function()
				{
					//alert('request2.readyState :'+request2.readyState);
					//alert('request2.status :'+request2.status);
					if (request2.readyState==4 && request2.status == 200 && !isMessagePrinted)
					{
						isMessagePrinted = true;
						response = request2.responseText;
						//alert('response 1 3 :'+response);
						generateAlertMessage(response);
					}
				};
				request2.send();
			}
			//request2.send();
		}
		
		// The funciton to generate CROS request
		function createCORSRequest(method, url){
			var version = navigator.userAgent;	
			var xhr = new XMLHttpRequest();
			if ("withCredentials" in xhr) {	// For Chrome/ Firefox
				//alert('withCredentials 3');
				xhr.open(method, url, true);
			} else if (typeof XDomainRequest != "undefined") {    // IE8, 
				try{
					xhr = new XDomainRequest();
					//alert(' else if in try with 2 :'+xhr);
					xhr.open(method, url);
				}catch(e){	
					xhr = new XMLHttpRequest();	
					//alert(' else catch in try with  2:'+xhr);
					xhr.open(method, url, true);
				}
			} else if(window.ActiveXObject) // for IE 7, 8 
			{
				//alert(' testing inside last  with :'+xhr);
				try {
					xhr = new ActiveXObject("Msxml2.XMLHTTP");
					//xhr = new ActiveXObject("Microsoft.XMLHTTP");
					//alert(' with xhr changed inside last ELSE WITH TRY BLOCK WITH  Microsoft.XMLHTTP Msxml2.XMLHTTP 456 :'+xhr);
					xhr.open(method, url);
					//alert('testing 1');					
					} catch(e) {
					try {
					xhr = new ActiveXObject("Microsoft.XMLHTTP");
					//alert('Exception 1: '+e.message);
					xhr.open(method, url);
					} catch(e1) {
						//Something went wrong
						//alert('Exception :2 '+e1.message);
						//xhr = new XMLHttpRequest();
						xhr.open(method, url, true);
						//alert("Your browser broke 2!");
					}
				}
			} else 	{
				try{
					xhr = new XDomainRequest();
					//alert(' else if in try with 2 :'+xhr);
					xhr.open(method, url);
				}catch(e){	
					xhr = new XMLHttpRequest();	
					//alert(' else catch in try with  2:'+xhr);
					//alert(' exception  2:'+e);
					xhr.open(method, url, true);
				}
			}			
			return xhr;
		}
				

		// The funciton to display Alert Message to the Browser
		function generateAlertMessage(alertMessage){
			var keyword= '/cookiepolicy/';
			var messageSeperatorkeyword= '____';
			var langSeperator=",";
			var dbCookieVersion ='1';
			//var dbCookieVersion = alertMessage.substring(0, alertMessage.indexOf('|'));
			var languages = preferredLanguage.substring(1,preferredLanguage.length);
			var lLangArry = languages.split(",");
			//alert('lLangArry  :'+lLangArry);
			var lLangCounter =0;
			var lFinalMessage='';

			var lDisplayCookieMessage='';

			//alert('generateAlertMessage '+ alertMessage);
			
			if(alertMessage.length && alertMessage.length > 0){
				var lLangArrLength = lLangArry.length;
				
				if(alertMessage.indexOf(messageSeperatorkeyword) != -1){
					var lCookieMessagePart = alertMessage.split(messageSeperatorkeyword);
					//alert('lCookieMessagePart : '+lCookieMessagePart);					
					var lCookieMessageLength = lCookieMessagePart.length-1;
					//alert('lCookieMessageLength : '+lCookieMessageLength);					
					
					for(var lCounter =0; lCounter < lCookieMessageLength; lCounter++ ) {
							//alert('cookie message : '+lCookieMessagePart[lCounter])
							var dbCookieVersionJS = lCookieMessagePart[lCounter].substring(0, alertMessage.indexOf('|'));
							//alert('dbCookieVersionJS :'+dbCookieVersionJS);
							lFinalMessage = lCookieMessagePart[lCounter].substring(lCookieMessagePart[lCounter].indexOf('|')+1, lCookieMessagePart[lCounter].length );
							//alert('lFinalMessage :'+lFinalMessage);
							var langCountryCode = FindNewLangWithCountryCode(lLangArry[lLangCounter++]);
							//alert(lCounter + ' : ' +langCountryCode);
							var lCookieMessagePartMain = lFinalMessage.split(keyword);
							//alert('lCookieMessagePartMain :'+lCookieMessagePartMain);
							var lCookieMessageLengthMain = lCookieMessagePartMain.length;
							//alert('lCookieMessageLengthMain :'+lCookieMessageLengthMain);
							var tempCookieMessage = '';
							
							for(var lCounter1 =0; lCounter1 < lCookieMessageLengthMain; lCounter1++ ) {
								//alert('testing : '+lCookieMessagePartMain[lCounter1]);
								if(lCounter1 != 0) {
									if(oupcookiepolicy_messagetype == 'explicit') {
										tempCookieMessage = tempCookieMessage + keyword + "?siteid="+oupcookiepolicy_siteid+"&lang="+langCountryCode + lCookieMessagePartMain[lCounter1]+ "<br/>" ;							
									} else {
										tempCookieMessage = tempCookieMessage + keyword + "?siteid="+oupcookiepolicy_siteid+"&lang="+langCountryCode + lCookieMessagePartMain[lCounter1];
									}
								} else {
									tempCookieMessage = lCookieMessagePartMain[lCounter1];									
								}
								//alert('tempCookieMessage :'+tempCookieMessage);
							}
							tempCookieMessage = tempCookieMessage.replace('dbCookieVersion',dbCookieVersionJS);
							lDisplayCookieMessage = lDisplayCookieMessage +tempCookieMessage;
							//alert('final tempCookieMessagewith version :'+tempCookieMessage);
					}
				} else {
					if(alertMessage.length && alertMessage.length > 0) {
						if(alertMessage.indexOf('|') != -1) {
							var dbCookieVersionJS = alertMessage.substring(0, alertMessage.indexOf('|'));
							//alert('else dbCookieVersionJS :'+dbCookieVersionJS);
							lFinalMessage = alertMessage.substring(alertMessage.indexOf('|')+1, alertMessage.length );
							//alert('else lFinalMessage :'+lFinalMessage);				
							lDisplayCookieMessage = lFinalMessage;
						}
					}
				}
				if(dbCookieVersion == '' || dbCookieVersion ==' '){
					dbCookieVersion = '1';
				}	
				alertMessageToDisplay = lDisplayCookieMessage;
				//alert('alertMessageToDisplay  :'+alertMessageToDisplay);				
				
				if(oupcookiepolicy_messagetype == 'implied'){
					alertMessageToDisplay=htmlDecode(alertMessageToDisplay);
					//alert('alertMessageToDisplay  :'+alertMessageToDisplay);	
					
					var p = document.createElement("div");
					p.innerHTML = alertMessageToDisplay;
					document.body.insertBefore(p, document.body.firstChild);
					saveCookie(dbCookieVersion);
				}else{
					//alertMessageToDisplay = alertMessageToDisplay+"<a id='cookie_accpt_button' href='javascript:saveCookie("+dbCookieVersion+")'>I accept</a>";
					document.getElementById('cookiepolicy_data').innerHTML = alertMessageToDisplay;
					//alert('alertMessageToDisplay  : '+alertMessageToDisplay);
					try{
						document.getElementById('cookiepolicy_link').click();							
					}catch(e){
						_cookiepolicy('#cookiepolicy_link').click();
					}
				}
			}
		}		
		
		function cookiePolicy(){
			var cookieWindow = window.open(cookiePolicyUrl,'_blank');
		}
		
		function saveCookie(version){
			var currentDate = new Date(); 
			var expiryDate = new Date();
			expiryDate.setDate( expiryDate.getDate() +365 );
			var savedDate = currentDate.getDate()+"-"+(currentDate.getMonth()+1)+"-"+currentDate.getFullYear();
			var expiryDateUtc = expiryDate.toGMTString();
			
		//	var cookieToSave = cookieName+","+version+","+savedDate+", expires="+expiryDateUtc;
		//	var cookieToSave = "name="+cookieName+"; value= version:"+version+",date:"+savedDate+"; expires="+expiryDateUtc;
			var cookieToSave = cookieName+"="+version+"_"+savedDate+"; expires="+expiryDateUtc+"; path="+oupcookiepolicy_documentroot ;
			var domainName = document.domain;

			if(oupcookiepolicy_siteid != null && oupcookiepolicy_siteid !='' && oupcookiepolicy_siteid =='journals')
			{
				if(domainName != null  && domainName != 'undefine' && domainName != '')
				{
					var containsDot =".";
					var firstPart='';
					var secondPart='';
					var domainToSetCookie='';
					//alert(domainName);
					if(domainName.indexOf(containsDot) !=  -1)
					{
						var str_array = domainName.split(containsDot);
						if(str_array.length > 2)
						{
							domainToSetCookie = '.'+str_array[str_array.length-2] +'.'+str_array[str_array.length-1]
						}
						//alert('contains dot '+domainToSetCookie);
						cookieToSave = cookieToSave +"; "+"domain="+domainToSetCookie;				
					} else {
						//alert('does not contains.');	
					}				
				}
			}
			document.cookie=cookieToSave;
			//alert(_cookiepolicy.oupcookiepolicy_fancybox);
			if(_cookiepolicy.oupcookiepolicy_fancybox){
				//alert('close it :'+_cookiepolicy.oupcookiepolicy_fancybox);
				_cookiepolicy.oupcookiepolicy_fancybox.close();
			}
			/*
			if(oupcookiepolicy_style == 'desktop'){
				_cookiepolicy.oupcookiepolicy_fancybox.close();
			}
			if(oupcookiepolicy_style == 'mobile'){
				document.location.reload(true);
			}
			*/
		}
		
		function closeImplied(){
			document.location.reload(true);
		}	
		
		_cookiepolicy(document).keydown(function(e) {
			if (e.keyCode == 27) {
			if (e.keyCode == 27 && !e.disableEscape) {
			return false;
				//$(document).unbind("keydown");
		}}});
		
		// Start Decode Functions
		/*
		Credit for htmlDecode goes to author  2a6a325068cf by Doug Fritz <dougfr...@google.com> on May 12, 2011   Diff tech
		Referred from : http://code.google.com/r/jimboyeah-3dreams/source/browse/deploy/tech/js/encoder.js?r=2a6a325068cf0aaf720bdba1acc2266449042e38
		*/
		function htmlDecode(s){
			var c,m,d = s;		
			if(this.isEmpty(d)) return "";

			// convert HTML entites back to numerical entites first
			d = this.HTML2Numerical(d);
		
			// look for numerical entities &#34;
			arr=d.match(/&#[0-9]{1,5};/g);			
			// if no matches found in string then skip
			if(arr!=null){
				for(var x=0;x<arr.length;x++){
					m = arr[x];
					c = m.substring(2,m.length-1); //get numeric part which is refernce to unicode character
					// if its a valid number we can decode
					if(c >= -32768 && c <= 65535){
						// decode every single match within string
						d = d.replace(m, String.fromCharCode(c));
					}else{
						d = d.replace(m, ""); //invalid so replace with nada
					}
				}			
			}	
			return d;
		}
		
		function isEmpty  (val){
			if(val){
				return ((val===null) || val.length==0 || /^\s+$/.test(val));
			}else{
				return true;
			}
		}
		
		function HTML2Numerical(s){
			return swapArrayVals(s,this.arr1,this.arr2);
		}
		
		// arrays for conversion from HTML Entities to Numerical values
		var arr1 = ['&nbsp;','&iexcl;','&cent;','&pound;','&curren;','&yen;','&brvbar;','&sect;','&uml;','&copy;','&ordf;','&laquo;','&not;','&shy;','&reg;','&macr;','&deg;','&plusmn;','&sup2;','&sup3;','&acute;','&micro;','&para;','&middot;','&cedil;','&sup1;','&ordm;','&raquo;','&frac14;','&frac12;','&frac34;','&iquest;','&Agrave;','&Aacute;','&Acirc;','&Atilde;','&Auml;','&Aring;','&AElig;','&Ccedil;','&Egrave;','&Eacute;','&Ecirc;','&Euml;','&Igrave;','&Iacute;','&Icirc;','&Iuml;','&ETH;','&Ntilde;','&Ograve;','&Oacute;','&Ocirc;','&Otilde;','&Ouml;','&times;','&Oslash;','&Ugrave;','&Uacute;','&Ucirc;','&Uuml;','&Yacute;','&THORN;','&szlig;','&agrave;','&aacute;','&acirc;','&atilde;','&auml;','&aring;','&aelig;','&ccedil;','&egrave;','&eacute;','&ecirc;','&euml;','&igrave;','&iacute;','&icirc;','&iuml;','&eth;','&ntilde;','&ograve;','&oacute;','&ocirc;','&otilde;','&ouml;','&divide;','&oslash;','&ugrave;','&uacute;','&ucirc;','&uuml;','&yacute;','&thorn;','&yuml;','&quot;','&amp;','&lt;','&gt;','&OElig;','&oelig;','&Scaron;','&scaron;','&Yuml;','&circ;','&tilde;','&ensp;','&emsp;','&thinsp;','&zwnj;','&zwj;','&lrm;','&rlm;','&ndash;','&mdash;','&lsquo;','&rsquo;','&sbquo;','&ldquo;','&rdquo;','&bdquo;','&dagger;','&Dagger;','&permil;','&lsaquo;','&rsaquo;','&euro;','&fnof;','&Alpha;','&Beta;','&Gamma;','&Delta;','&Epsilon;','&Zeta;','&Eta;','&Theta;','&Iota;','&Kappa;','&Lambda;','&Mu;','&Nu;','&Xi;','&Omicron;','&Pi;','&Rho;','&Sigma;','&Tau;','&Upsilon;','&Phi;','&Chi;','&Psi;','&Omega;','&alpha;','&beta;','&gamma;','&delta;','&epsilon;','&zeta;','&eta;','&theta;','&iota;','&kappa;','&lambda;','&mu;','&nu;','&xi;','&omicron;','&pi;','&rho;','&sigmaf;','&sigma;','&tau;','&upsilon;','&phi;','&chi;','&psi;','&omega;','&thetasym;','&upsih;','&piv;','&bull;','&hellip;','&prime;','&Prime;','&oline;','&frasl;','&weierp;','&image;','&real;','&trade;','&alefsym;','&larr;','&uarr;','&rarr;','&darr;','&harr;','&crarr;','&lArr;','&uArr;','&rArr;','&dArr;','&hArr;','&forall;','&part;','&exist;','&empty;','&nabla;','&isin;','&notin;','&ni;','&prod;','&sum;','&minus;','&lowast;','&radic;','&prop;','&infin;','&ang;','&and;','&or;','&cap;','&cup;','&int;','&there4;','&sim;','&cong;','&asymp;','&ne;','&equiv;','&le;','&ge;','&sub;','&sup;','&nsub;','&sube;','&supe;','&oplus;','&otimes;','&perp;','&sdot;','&lceil;','&rceil;','&lfloor;','&rfloor;','&lang;','&rang;','&loz;','&spades;','&clubs;','&hearts;','&diams;'];
		var arr2 = ['&#160;','&#161;','&#162;','&#163;','&#164;','&#165;','&#166;','&#167;','&#168;','&#169;','&#170;','&#171;','&#172;','&#173;','&#174;','&#175;','&#176;','&#177;','&#178;','&#179;','&#180;','&#181;','&#182;','&#183;','&#184;','&#185;','&#186;','&#187;','&#188;','&#189;','&#190;','&#191;','&#192;','&#193;','&#194;','&#195;','&#196;','&#197;','&#198;','&#199;','&#200;','&#201;','&#202;','&#203;','&#204;','&#205;','&#206;','&#207;','&#208;','&#209;','&#210;','&#211;','&#212;','&#213;','&#214;','&#215;','&#216;','&#217;','&#218;','&#219;','&#220;','&#221;','&#222;','&#223;','&#224;','&#225;','&#226;','&#227;','&#228;','&#229;','&#230;','&#231;','&#232;','&#233;','&#234;','&#235;','&#236;','&#237;','&#238;','&#239;','&#240;','&#241;','&#242;','&#243;','&#244;','&#245;','&#246;','&#247;','&#248;','&#249;','&#250;','&#251;','&#252;','&#253;','&#254;','&#255;','&#34;','&#38;','&#60;','&#62;','&#338;','&#339;','&#352;','&#353;','&#376;','&#710;','&#732;','&#8194;','&#8195;','&#8201;','&#8204;','&#8205;','&#8206;','&#8207;','&#8211;','&#8212;','&#8216;','&#8217;','&#8218;','&#8220;','&#8221;','&#8222;','&#8224;','&#8225;','&#8240;','&#8249;','&#8250;','&#8364;','&#402;','&#913;','&#914;','&#915;','&#916;','&#917;','&#918;','&#919;','&#920;','&#921;','&#922;','&#923;','&#924;','&#925;','&#926;','&#927;','&#928;','&#929;','&#931;','&#932;','&#933;','&#934;','&#935;','&#936;','&#937;','&#945;','&#946;','&#947;','&#948;','&#949;','&#950;','&#951;','&#952;','&#953;','&#954;','&#955;','&#956;','&#957;','&#958;','&#959;','&#960;','&#961;','&#962;','&#963;','&#964;','&#965;','&#966;','&#967;','&#968;','&#969;','&#977;','&#978;','&#982;','&#8226;','&#8230;','&#8242;','&#8243;','&#8254;','&#8260;','&#8472;','&#8465;','&#8476;','&#8482;','&#8501;','&#8592;','&#8593;','&#8594;','&#8595;','&#8596;','&#8629;','&#8656;','&#8657;','&#8658;','&#8659;','&#8660;','&#8704;','&#8706;','&#8707;','&#8709;','&#8711;','&#8712;','&#8713;','&#8715;','&#8719;','&#8721;','&#8722;','&#8727;','&#8730;','&#8733;','&#8734;','&#8736;','&#8743;','&#8744;','&#8745;','&#8746;','&#8747;','&#8756;','&#8764;','&#8773;','&#8776;','&#8800;','&#8801;','&#8804;','&#8805;','&#8834;','&#8835;','&#8836;','&#8838;','&#8839;','&#8853;','&#8855;','&#8869;','&#8901;','&#8968;','&#8969;','&#8970;','&#8971;','&#9001;','&#9002;','&#9674;','&#9824;','&#9827;','&#9829;','&#9830;'];

		
		function swapArrayVals (s,arr1,arr2){
		if(this.isEmpty(s)) return "";
		var re;
		if(arr1 && arr2){
				//ShowDebug("in swapArrayVals arr1.length = " + arr1.length + " arr2.length = " + arr2.length)
				// array lengths must match
				if(arr1.length == arr2.length){
					for(var x=0,i=arr1.length;x<i;x++){
						re = new RegExp(arr1[x], 'g');
						s = s.replace(re,arr2[x]); //swap arr1 item with matching item from arr2	
					}
				}
			}
		return s;
		}
		
		// End Decode Functions

		// Function to find country code respective to language to match OUP countryCodeTag functionality
		function FindNewLangWithCountryCode(lLangCode)	{
			//alert('Inside FindNewLangWithCountryCode function');
			var lRowCount=10;
			var lColCount=2;
			var lDefaultLang='en';
			var bLangMatchFound=false;
			var lCountryCode='GB';
			var LangCountryArray = new Array(lRowCount);

			LangCountryArray [0] = new Array(lColCount);

			LangCountryArray [0][0] = "ja";

			LangCountryArray [0][1] = "JP";

			LangCountryArray [1] = new Array(lColCount);

			LangCountryArray [1][0] = "en";

			LangCountryArray [1][1] = "GB";

			LangCountryArray [2] = new Array(lColCount);

			LangCountryArray [2][0] = "zh";

			LangCountryArray [2][1] = "TW";

			LangCountryArray [3] = new Array(lColCount);

			LangCountryArray [3][0] = "de";

			LangCountryArray [3][1] = "DE";

			LangCountryArray [4] = new Array(lColCount);

			LangCountryArray [4][0] = "fr";

			LangCountryArray [4][1] = "FR";
			
			LangCountryArray [5] = new Array(lColCount);

			LangCountryArray [5][0] = "es";

			LangCountryArray [5][1] = "ES";
			
			LangCountryArray [6] = new Array(lColCount);

			LangCountryArray [6][0] = "nl";

			LangCountryArray [6][1] = "NL";
			
			LangCountryArray [7] = new Array(lColCount);

			LangCountryArray [7][0] = "it";

			LangCountryArray [7][1] = "IT";
			
			LangCountryArray [8] = new Array(lColCount);

			LangCountryArray [8][0] = "pt";

			LangCountryArray [8][1] = "PT";
			
			LangCountryArray [9] = new Array(lColCount);

			LangCountryArray [9][0] = "sk";

			LangCountryArray [9][1] = "SK";
			
			var arrayRow='';
			var countryCode='';
			for (var i=0;i<10; i++) {
				for (var j=0;j<2; j++) {
					//alert(LangCountryArray[i][j]);
					arrayRow='Array['+i+', '+j+']:= '+'\"'+LangCountryArray[i][j]+'\" ';
					if(j == 0 && LangCountryArray[i][j] == lLangCode)	{
						//alert(LangCountryArray[i][j+1]);
						lCountryCode = LangCountryArray[i][j+1];
						lLangCode = lLangCode +'_'+lCountryCode;
						bLangMatchFound = true;
						break;
					}
					//alert(arrayRow);
				}
			}
			// Match Found for language
			if(bLangMatchFound) {
				//alert('Matched Language Code : '+lLangCode);
			} else {
				lLangCode = lDefaultLang +'_'+lCountryCode;
			}
			return lLangCode;
		}