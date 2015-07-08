(function( $ ) {
  var linkMap = {};
  $('meta[name ^= "citation"][name $= "url"]').each(function (i){linkMap[this.name.match("citation_(.*?)(_html)?_url")[1]] = this.content;});
  if(linkMap['pdf']){
    linkMap['pdf+html'] = linkMap['pdf'] + '+html';
  }
  $.fn.addVariantLink = function(options) {
    console.log(this);
    var settings = $.extend( {}, $.fn.addVariantLink.defaults, options);
    var link = $('<a>').attr('href', linkMap[settings.variant]).append(settings.contents);
    if(settings.classes){
        link.attr('class',settings.classes);
    }
    if(settings.id){
        link.attr('id',settings.id);
    }
    if(this.length == 0){
        return link;
    } 
    else if(settings.mode === 'append'){
        return this.append(link);
    }else if(settings.mode === 'prepend'){
        return this.prepend(link);
    }else{
        $.error('unsupported addVariantLink mode ' + settings.mode);
    }
  };
  $.fn.addVariantLink.defaults = {mode : 'append'};
})( jQuery );