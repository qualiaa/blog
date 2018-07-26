"use strict"

function addPermalinkToSections(jObj) {
    jObj.find("h1, h2, h3, h4, h5").each(function(i,obj) {
        var id_attr = $(this).attr("id");
        if (typeof id_attr !== typeof undefined && id_attr != false) {
            $(this).text(" "+$(this).text());
            var permalink = $("<a>§</a>")
                .attr("href","#"+id_attr)
                .addClass("section-link");
            $(this).prepend(permalink);
        }
    });
}

function highlightCode(jObj) {
    jObj.find("pre code").each(function(i, block) {
        /* Need to move pandoc's <pre> classes to <code> tag for hljs */
        $(this).attr("class", $(this).parent().attr("class"));
        hljs.highlightBlock(block);
    })
}

$(function() { highlightCode($("article")) });
