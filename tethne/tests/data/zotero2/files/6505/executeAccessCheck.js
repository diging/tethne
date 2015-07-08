$(document).ready(function() {
	var checker = new AccessCheck();
	var decorator = new AccessCheckDecorator();
        decorator.text.free = getSiteOption('free-text', 'Free');
        decorator.text.freeToYou = getSiteOption('free-to-you-text', 'Free to you');
	checker.setResourcesToCheck(decorator.scan());
	checker.subscribe('success', function (data){
		decorator.decorate(checker);
	});
	setTimeout(function(){checker.callAjax();}, 25);
});
