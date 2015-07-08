function getQueryContext(){
        var query_context = new Array();
        var title = jQuery('meta[name="DC.Title"]').attr("content");
        if (title) {
            var search_title = title.replace(/[:\.,*]/g, "");
            search_title = search_title.replace(/\b(and|or|a|of|the|in|with|to|an|for|as)\b/gi, "");
            search_title = search_title.replace(/^\s/, "");
            search_title = search_title.replace(/\s+/g, " OR ");
            query_context.push(":TITLE:" + search_title);
        }
        
        if (window.taxonomies) {
	        //var subj_query = taxonomies.join(" OR ");
	        var subj_query = taxonomies[0];
	        query_context.push(":SUBJ:" + subj_query);
    	}
        
        return query_context;
}

function getJnlCode(){
        var doi = jQuery('meta[name="DC.Identifier"]').attr("content");
        var doi_elements = doi.split("/");
        return doi_elements[1];    
}