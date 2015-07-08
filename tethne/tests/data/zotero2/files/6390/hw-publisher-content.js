
$(document).ready(function () {
    $(".fig, .fig-expansion").has(".fig-caption .fig-permissions").each(function (index) {
        var figureElement = $(this);
        var isFigureExpansion = $(this).hasClass("fig-expansion");

        $(this).find(".callout").has(".callout-links, .fig-services").hide();

        if (isFigureExpansion) {
            $("#power-point").hide();
        }

        $(this).delegate(".fig-inline", "contextmenu", function (event) {
            event.preventDefault();
        });

        $(this).delegate("img", "contextmenu", function (event) {
            event.preventDefault();
        });

        $(this).delegate("a:has(img)", "click", function (event) {
            event.preventDefault();
        });

        $(this).delegate("img", "mousedown", function (event) {
            var figureContainer = isFigureExpansion ? "img" : ".fig-inline";
            var figureImage = $(figureElement).find(figureContainer).get(0);
            var figureHeight = $(figureImage).innerHeight();
            var figureWidth = $(figureImage).innerWidth();
            var figurePosition = $(figureImage).offset();
            var figureCopyright = $(figureElement).find(".fig-caption .fig-permissions").text().replace(/\s+/g, " ");
            var figureCopyrightFontSize = $(figureElement).find(".fig-caption p").css("font-size");

            // CSS styles to control opacity in various browsers (order is important)
            var cssOpacity = "-ms-filter: \"progid:DXImageTransform.Microsoft.Alpha(Opacity=75)\"; " + // IE 8
                "filter: alpha(opacity=75); " + // IE 7
                "opacity: 0.75; "; // everything else

            event.preventDefault();

            if (isFigureExpansion) {
                var figureColor = $(figureElement).css("color");

                $(figureImage).after("<div class='image-copyright-overlay' style='background-color: #FFFFFF; color: " +
                    figureColor + "; font-size: " + figureCopyrightFontSize + "; height: " + figureHeight + "px; " +
                    cssOpacity + "overflow: hidden; position: absolute; text-align: center; top: " +
                    Math.round(figurePosition.top) + "px; width: " + figureWidth + "px;' title='" + figureCopyright +
                    "'><span style='position: relative; top: 10px;'>" + figureCopyright + "</span></div>");
            } else {
                var cssLeft = "";
                var cssMarginLeft = "";

                if ($("#content-toggle .expanded").length > 0) {
                    cssMarginLeft = "margin-left: -10px; ";
                } else {
                    cssLeft = "left: " + (Math.round(figurePosition.left) + 1) + "px; ";
                }

                $(figureImage).append("<div class='image-copyright-overlay' style='background-color: #FFFFFF; font-size: " +
                    figureCopyrightFontSize + "; height: " + figureHeight + "px; " + cssLeft + cssMarginLeft + cssOpacity +
                    "overflow: hidden; position: absolute; top: " + (Math.round(figurePosition.top) + 1) + "px; width: " +
                    figureWidth + "px;' title='" + figureCopyright + "'><span style='position: relative; top: 10px;'>" +
                    figureCopyright + "</span></div>");
            }
        });

        $(this).delegate(".image-copyright-overlay", "contextmenu", function (event) {
            event.preventDefault();
        });

        $(this).delegate(".image-copyright-overlay", "mousedown", function (event) {
            event.preventDefault();
            $(this).remove();
        });
    });
});

