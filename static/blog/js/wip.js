"use strict"

var updateTime = 1000
var requestUrl = "/json/wip/" + slug

$(function() {
    setInterval(function() {
        console.log("Making request")
        console.log(requestUrl)
        $.get(requestUrl,
            function(data) {
                var article_html = data["html"]
                console.log(article_html)

                $("#article-html").html(article_html)
                $("#article-html pre code").each(function(i, block) {
                    hljs.highlightBlock(block)
                })
                // MathJax.Hub.Queue(["Typeset",MathJax.Hub])
            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.log("Failure\n"+textStatus + "\n" + errorThrown)
                console.log(jqXHR.responseText)
            })
    }, updateTime)
})
