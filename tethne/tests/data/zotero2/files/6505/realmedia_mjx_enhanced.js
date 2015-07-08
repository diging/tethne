// Run OAS code as immediate function to restrict scope
// If used within an iframe this file should be included in the page body
//(function () {
    var OAS_url = 'http://oas.oxfordjournals.org.ezproxy1.lib.asu.edu/RealMedia/ads/',
    
    // All possible positions - will be filtered based on placeholders on page or iframe query string
    OAS_listpos = 'Top,Top1, Bottom,Right1',
    
    OAS_query = '?',
    
    // URL will be replace by address in query string if within iframe
    OAS_sitepage = location.hostname + location.pathname,
    
    OAS_rns = (Math.random() + '').substring(2, 11),
    
    OAS_LIB = {
        // This method sets the OAS variables for the page and inserts the external RealMedia script into the DOM
        init: function (e) {
            var headNode = document.getElementsByTagName('head')[0],
            scriptNode = document.createElement('script'),
            searchTerm = OAS_LIB.getSearchTerm(location.href) || OAS_LIB.getSearchTerm(document.referrer),
            urlValues,
            oasScriptUrl,
            stateChanged = function (e) {
                if (scriptNode.readyState === 'complete' || scriptNode.readyState === 'loaded') {
                    OAS_LIB.replacePlaceholders();
                }
            };
            
            // If running outside of an iframe
            if (window === window.top) {
                if (OAS_LIB.isHomePage()) {
                    // H2.0
                    if (document.getElementById('h20_page')) {
                        OAS_sitepage = location.hostname + '/site/index.xhtml';
                    // H1.0
                    } else {
                        OAS_sitepage = location.hostname + '/index.dtl';
                    }
                }
                
                // Search term targetting
                if (searchTerm) {
                    OAS_query = '?' + searchTerm.replace(' ', '&');
                }
                
                OAS_listpos = OAS_LIB.getAdPositions().join(',');
            // Running within an iframe
            } else {
                urlValues = OAS_LIB.getAdUrlValues(location.href);
                // u is the page URL and p the advert position
                if (urlValues.u && urlValues.p) {
                    OAS_sitepage = urlValues.u;
                    OAS_listpos = urlValues.p;
                }
            }
            
            // Remove leading http://
            OAS_sitepage = OAS_sitepage.replace('http://', '');
			
            // Categorize URL
            if (window.categorize) {
                OAS_sitepage = window.categorize(OAS_sitepage);
            }
            
            // Search term targetting
            if (searchTerm) {
                OAS_query = '?' + searchTerm.replace(' ', '&');
            }
            
            oasScriptUrl = OAS_url + 'adstream_mjx.ads/' + OAS_sitepage + '/1' + OAS_rns + '@' + OAS_listpos + OAS_query;
            
            // If running outside of an iframe
            if (window === window.top) {
                // Insert RealMedia script into DOM and insert banners
                scriptNode.setAttribute('src', oasScriptUrl);
                scriptNode.setAttribute('type', 'text/javascript');
                // Wait until OAS_RICH() has loaded from RealMedia
                if (window.addEventListener) {
                    scriptNode.addEventListener('readystatechange', stateChanged, false);
                    scriptNode.addEventListener('load', OAS_LIB.replacePlaceholders, false);
                } else if (window.attachEvent) {
                    scriptNode.attachEvent('onreadystatechange', stateChanged);
                    scriptNode.attachEvent('onload', OAS_LIB.replacePlaceholders);
                }
                headNode.appendChild(scriptNode);
            // Running within an iframe
            } else {
                // Insert RealMedia script into DOM and insert banners
                document.write('<script type="text/javascript" src="' + oasScriptUrl + '"></script>');
                //OAS_LIB.insertAd(null, OAS_listpos);
            }
        },
        
        // OAS_NORMAL() replacement
        // This method inserts a normal advert for the given position inside the placeholder node
        insertNormal: function (placeholderNode, position) {
            var anchorNode = document.createElement('a'),
            imageNode = document.createElement('img');
            
            anchorNode.setAttribute('href', OAS_url + 'click_nx.ads/' + OAS_sitepage + '/1' + OAS_rns + '@' + OAS_listpos + '!' + position + OAS_query);
            
            imageNode.setAttribute('src', OAS_url + 'adstream_nx.ads?' + OAS_sitepage + '/1' + OAS_rns + '@' + OAS_listpos + '!' + position + OAS_query);
            imageNode.style.borderWidth = 0;
            
            anchorNode.appendChild(imageNode);
            placeholderNode.appendChild(anchorNode);
        },
        
        // OAS_RICH() replacement
        // This method inserts a rich media advert for the given position inside the placeholder node
        insertRich: function (placeholderNode, position) {
            var capturedText = '',
            capturedScriptText = '',
            origFunction = document.write,
            captureFunction = function (text) {
                capturedText += text;
            },
            capturedTextContainer = document.createElement('div'),
            // Execute any embedded code or externally linked scripts
            executeScripts = function (capturedText) {
                var externalScripts = /<script[^>]+?(?:id=["']([^"']+))?[^>]+?src=["']([^"']+)/gi,
                headNode = document.getElementsByTagName('head')[0],
                scriptNode,
                divNode = document.createElement('div'),
                embeddedScripts = /<script[^>]*>\s*(?:<!--)?\s*([\s\S]*?)\s*(?:\/\/\s*-->)?\s*<\/script>/gi,
                match,
                answer = 0;
                
                // Insert externally linked scripts
                while (match = externalScripts.exec(capturedText)) {
                    scriptNode = document.createElement('script');
                    scriptNode.setAttribute('src', match[2]);
                    if (match[1]) {
                        scriptNode.setAttribute('id', match[1]);
                    }
                    scriptNode.setAttribute('type', 'text/javascript');
                    headNode.appendChild(scriptNode);
                    answer = 1;
                }
                
                // RealMedia looks for an element called 'FinContent[Position]1' for SWF ads
                // Firefox creates this correctly through the eval below, but IE needs a push
                divNode.setAttribute('id', 'FinContent' + position + '1');
                placeholderNode.appendChild(divNode);
                
                // Execute embedded scripts
                while (match = embeddedScripts.exec(capturedText)) {
                    eval(match[1]);
                    answer = 1;
                }
                
                return answer;
            };
            
            document.write = captureFunction;
            
            if (OAS_RICH) {
                OAS_RICH(position);
            }
            
            do {
                capturedScriptText = capturedText;
                capturedText = '';
            } while (executeScripts(capturedScriptText));
            
            document.write = origFunction;
            
            placeholderNode.innerHTML = capturedScriptText;
        },
        
        // OAS_AD() replacement
        // This method inserts a banner advert for the given position inside the placeholder node
        insertAd: function (placeholderNode, position) {
            if (placeholderNode) {
                OAS_LIB.insertRich(placeholderNode, position);
            } else {
                if (window.OAS_RICH !== undefined) {
                    OAS_RICH(position);
                }
            }
        },
        
        // Home page check
        // This method returns true if the visitor is currently viewing a home page, otherwise false
        isHomePage: function () {
            var bodyElement = document.getElementsByTagName('body')[0];
            
            return (bodyElement.className.indexOf('homepage') >= 0);
        },
        
        // Placeholder nodes
        // This method returns the placeholder nodes as an object keyed by position name
        // Placeholder nodes should have IDs of "oas_[position]" and be initially displayed as empty containers with dimensions set through CSS to prevent page jumping
        getPlaceholderNodes: function () {
            var idPrefix = 'oas_',
            positions = OAS_listpos.split(','),
            totalPositions = positions.length,
            placeholderNode,
            placeholderNodes = {},
            i = 0;
            
            for (i = 0; i < totalPositions; i++) {
                placeholderNode = document.getElementById(idPrefix + positions[i].toLowerCase());
                
                if (placeholderNode) {
                    placeholderNodes[positions[i]] = placeholderNode;
                }
            }
            
            return placeholderNodes;
        },
        
        // Ad positions
        // This method returns an array of ad positions based on the placeholders present on the page
        getAdPositions: function () {
            var placeholderNodes = OAS_LIB.getPlaceholderNodes(),
            position,
            adPositions = [];
            
            for (position in placeholderNodes) {
                if (!placeholderNodes.hasOwnProperty(position)) {
                    continue;
                }
                
                adPositions.push(position);
            }
            
            return adPositions;
        },
        
        // Placeholder replacement
        // This method replaces any empty placeholder nodes with banner adverts
        replacePlaceholders: function () {
            var placeholderNodes = OAS_LIB.getPlaceholderNodes(),
            position;
            
            for (position in placeholderNodes) {
                if (!placeholderNodes.hasOwnProperty(position)) {
                    continue;
                }
                
                OAS_LIB.insertAd(placeholderNodes[position], position);
            }
        },
        
        // Search terms
        // This method returns the search terms used within URL specified
        // Currently supports the Journals HighWire and Google search pages
        getSearchTerm: function (url) {
            // Example: http://services.oxfordjournals.org.ezproxy1.lib.asu.edu/cgi/searchresults?fulltext=test
            var hwSearch = /^http:\/\/services\.oxfordjournals\.org\/cgi\/searchresults.*?[?&](?:fulltext|title|titleabstract|author\d)=([^&#]+)/,
            // Example: http://www.google.co.uk/search?q=test
            googleSearch = /^http:\/\/(?:[^.]+\.)?google[^\/]+\/search.*?[?&]q=([^&#]+)/,
            matches = url.match(hwSearch) || url.match(googleSearch);
            
            if (matches) {
                return window.unescape(matches[1]);
            }
            
            return '';
        },
        
        // Ad URL values
        // This method returns an object containing the page's query string values
        // These values are used to configure OAS ads when used within iframes
        getAdUrlValues: function (url) {
            var queryStringPosition = url.indexOf('?'),
            queryStrings = [],
            totalQueryStrings,
            queryStringParts,
            values = {},
            i;
            
            if (queryStringPosition === -1) {
                return values;
            }
            
            queryStrings = url.substring(queryStringPosition + 1).split('&');
            totalQueryStrings = queryStrings.length;
            
            for (i = 0; i < totalQueryStrings; i++) {
                queryStringParts = queryStrings[i].split('=');
                if (queryStringParts.length >= 2) {
                    values[queryStringParts[0]] = queryStringParts[1];
                }
            }
            
            return values;
        }
    };
    
    // If running outside of an iframe
    if (window === window.top) {
        if (window.addEventListener) {
            window.addEventListener('load', OAS_LIB.init, false);
        } else if (window.attachEvent) {
            window.attachEvent('onload', OAS_LIB.init);
        }
    // Running within an iframe
    } else {
        OAS_LIB.init();
    }
//}());