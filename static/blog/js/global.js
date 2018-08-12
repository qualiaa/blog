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
    jObj.find("code.hl").each(function(i, block) {
        /* Need to move pandoc's <pre> classes to <code> tag for hljs */
        $(this).html(hljs.highlightAuto($(this).text()).value);
    })
}

// from https://stackoverflow.com/a/9744104/1905448
function isExternal(index) {
    var url = this.getAttribute("href");
    var domain = function(url) {
        return url.replace('http://','').replace('https://','').split('/')[0];
    };

    return domain(location.href) !== domain(url);
}

function decorateExterns() {
    $("a[href^=http]").filter(isExternal).addClass("extern");
}

function decorateGithubLinks() {
    $("a[href*=github]").addClass("github").removeClass("extern");
}

function pageInit() {
    highlightCode($("article"));
    decorateExterns();
    decorateGithubLinks();
}

$(pageInit);


