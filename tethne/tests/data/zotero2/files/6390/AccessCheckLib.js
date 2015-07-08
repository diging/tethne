function AccessCheckResource(mjid, views){
	this.resid = mjid;
	this.views = views || [];
	this.statusByView = {};
	
}

AccessCheckResource.alwayFreeViews = ['abstract','extract'];
AccessCheckResource.version = 0.1;

AccessCheckResource.prototype.toString = function(){
	var string = this.resid;
	for (var i = 0; i < this.views.length; i++){
		string += ' '+ this.views[i];
	}
	return string;
}

AccessCheckResource.prototype.toXML = function(){
	var xml ='';
	for (var i = 0; i < this.views.length; i++){
		if($.inArray(this.views[i],AccessCheckResource.alwayFreeViews) === -1)
		xml += "<check-resource resid='" + this.resid + "' views='" + this.views[i] + "' ><\/check-resource>"
	}	
	return xml;
}

AccessCheckResource.prototype.addView =function(view){
	if($.inArray(view, this.views) === -1 && $.inArray(view, AccessCheckResource.alwayFreeViews) === -1){
		this.views.push(view);
	}
}

AccessCheckResource.prototype.addViews =function(views){
	for(var i = 0; i < views.length; i++){
		this.addView(views[i]);
	}
}

AccessCheckResource.prototype.setStatusForView = function(view,status){
	this.statusByView[view] = status;
}

AccessCheckResource.prototype.getStatusForView = function(view){
	return ($.inArray(view, AccessCheckResource.alwayFreeViews) > -1)?'free':this.statusByView[view];
}

AccessCheckResource.prototype.isFree = function(view){
	if(view){
		return ($.inArray(view, AccessCheckResource.alwayFreeViews) >  -1 || this.statusByView[view] === 'free')
	}else{
		for(var i = 0; i < this.views.length; i++){
			if (this.statusByView[this.views[i]] === 'free') return true;
		}
		return false;
	}
}

AccessCheckResource.prototype.isAvailable = function(view){
	if(view){
		return ($.inArray(view, AccessCheckResource.alwayFreeViews) >  -1 || this.statusByView[view] === 'free' || this.statusByView[view] === 'free-to-you' )
	}else{
		for(var i = 0; i < this.views.length; i++){
			if (this.statusByView[this.views[i]] === 'free' || this.statusByView[this.views[i]] === 'free-to-you' ) return true;
		}
		return false;
	}	
}

function AccessCheck(){
	this.ajaxUrl =  document.location.protocol + "//" + document.location.host + '/authn-callback';
	this.ajaxContentType = 'text/xml';
	this.ajaxDataType =  'xml';
	this.ajaxType = 'POST';
	this.ajaxProcessData =  false;
	this.listeners = {};

}

AccessCheck.version = 0.1;

AccessCheck.prototype.setResourcesToCheck = function(rtc){
	this.resourcesToCheck = rtc;
}

AccessCheck.prototype.addResourceToCheck = function(mjid, views){
	this.resourcesToCheck = this.resourcesToCheck || {};
    if(this.resourcesToCheck[mjid]){
    	this.resourcesToCheck[mjid].addViews(views); 
	}else{
		this.resourcesToCheck[mjid] = new AccessCheckResource(mjid, views);
	}
}

AccessCheck.prototype.setResourceViewStatus = function(mjid, view, status){
	if(!this.resourcesToCheck[mjid]){
		this.resourcesToCheck[mjid] = new AccessCheckResource(mjid, [view]);
	}
	this.resourcesToCheck[mjid].setStatusForView(view, status);
}

AccessCheck.prototype.getCheckRequestData = function(){
	if(!this.checkRequest){
		this.checkRequest = "<accesscheck>";
		for(resource in this.resourcesToCheck){
			this.checkRequest +=  this.resourcesToCheck[resource].toXML();
		}
		this.checkRequest += "</accesscheck>";
	}
	return this.checkRequest;
}

AccessCheck.prototype.callAjax = function (){
    if($('check-resource',this.checkRequest)){
    	var self = this;
        $.ajax({
	        url: this.ajaxUrl,
	        contentType: this.ajaxContentType,
	        data: this.getCheckRequestData(),
	        dataType: this.ajaxDataType,
	        type: this.ajaxType,
	        processData: this.ajaxProcessData,
	        error: this.errorHandler,
	        success: function(xmlData) {self.successHandler(xmlData)},
	        complete: this.completeHandler
    });
}
}

AccessCheck.prototype.successHandler = function (xmlData) {
	var checkResponse = $('check-resource', xmlData);
	for(var i = 0; i < checkResponse.length; i++){
		var resid = checkResponse.eq(i).attr('resid');
		var view = checkResponse.eq(i).attr('view');
		var status = checkResponse.eq(i).attr('add-class');
		this.setResourceViewStatus(resid, view, status);
	}
	this._notify('success');
}

AccessCheck.prototype.errorHandler = function (req, msg, e) {}
AccessCheck.prototype.completeHandler = function(req, msg) {}

AccessCheck.prototype.subscribe = function(event,fn){
	if(!this.listeners[event]){
		this.listeners[event] = [];
	}
	this.listeners[event].push(fn);
}

AccessCheck.prototype._notify = function(event,data){
	if(this.listeners[event]){
		for(var i = 0; i < this.listeners[event].length; i++){
			 this.listeners[event][i].call(data);
		}
	}
}

AccessCheck.prototype.getResource = function(mjid){
	return this.resourcesToCheck[mjid];
}


function AccessCheckDecorator(target){
	this.target = target || $('body');
	this.text = {
			free :  'Free',
			freeToYou :  'Free to you'
	};
}

AccessCheckDecorator.version = 0.1;
AccessCheckDecorator.freeClass = 'free';
AccessCheckDecorator.availableClass = 'free-to-you';

AccessCheckDecorator.prototype.scan = function(){
	this.itemsToDecorate = $('span.accesscheck,span.viewspecificaccesscheck',this.target);
	var resourcesToCheck = {};
	for (var i = 0; i < this.itemsToDecorate.length; i++) {
	    var checkstring = this.itemsToDecorate.eq(i).attr('class');
	    var checkdata = checkstring.split(/\s+/);
		if (checkdata.length === 3) {
			if(resourcesToCheck[checkdata[1]]){
				resourcesToCheck[checkdata[1]].addViews(checkdata[2].split(','));
			}else{
				resourcesToCheck[checkdata[1]] = new AccessCheckResource(checkdata[1],checkdata[2].split(','));
			}
		}
	}
	return resourcesToCheck;
}

AccessCheckDecorator.prototype.decorate = function(checker){
	for (var i = 0; i < this.itemsToDecorate.length; i++) {
	    var checkstring = this.itemsToDecorate.eq(i).attr('class');
	    var checkdata = checkstring.split(/\s+/);
	       if(checkstring.indexOf('accesscheck') === 0){
	           this.decorateResourceElement(this.itemsToDecorate.eq(i),checker.getResource( checkdata[1]));
	       }else if (checkstring.indexOf('viewspecificaccesscheck') === 0){
	           this.decorateViewElement(this.itemsToDecorate.eq(i),checker.getResource( checkdata[1]),checkdata[2]);
	       }
	}
}

AccessCheckDecorator.prototype.decorateResourceElement = function(element,resource){
	if(resource.isFree()){
		this.decorateResourceElementFree(element,resource);
	}else if (resource.isAvailable()){
		this.decorateResourceElementAvailable(element,resource);
	}else{
		this.decorateResourceElementUnavailable(element,resource);
	}
}

AccessCheckDecorator.prototype.decorateViewElement = function(element,resource, view){
	if(resource.isFree(view)){
		this.decorateViewElementFree(element,resource, view);
	}else if (resource.isAvailable(view)){
		this.decorateViewElementAvailable(element,resource, view);
	}else{
		this.decorateViewElementUnavailable(element,resource, view);
	}
}

AccessCheckDecorator.prototype.decorateResourceElementFree = function(element,resource){
    var targetParent = element.parents('.cit').eq(0);
    if(targetParent.length){
        var ft = targetParent.find("ul.cit-views li:first");
        if (ft.length) {
        	var li = $('<li>').addClass(AccessCheckDecorator.freeClass);
        	ft.append(li.append(this.text.free));
        }
    }
}

AccessCheckDecorator.prototype.decorateResourceElementAvailable = function(element,resource){
    var targetParent = element.parents('.cit').eq(0);
    if(targetParent.length){
        var ft = targetParent.find("ul.cit-views li:first");
        if (ft.length) {
        	var li = $('<li>').addClass(AccessCheckDecorator.availableClass);
        	ft.append(li.append(this.text.freeToYou));
        }
    }
}

AccessCheckDecorator.prototype.decorateResourceElementUnavailable = function(element, resource){
}

AccessCheckDecorator.prototype.decorateViewElementFree = function(element,resource,view){
   	element.append(this.text.free);
    element.addClass(AccessCheckDecorator.freeClass);	
}

AccessCheckDecorator.prototype.decorateViewElementAvailable = function(element,resource,view){
   	element.append(this.text.freeToYou);
    element.addClass(AccessCheckDecorator.availableClass);	
}

AccessCheckDecorator.prototype.decorateViewElementUnavailable = function(element,resource, view){
}
