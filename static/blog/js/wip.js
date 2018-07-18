"use strict"

var updateTime = 1000
var requestUrl = "/json/wip/" + slug

$(function() {
    setInterval(function() {
        $.get(requestUrl,
            function(data) {
                var article_html = data["html"]
                if (data.hasOwnProperty("title")) {
                    var title = data["title"]
                    $("h1#title").text(title)
                }
                if (data.hasOwnProperty("tags")) {
                    $("p.tags").text("Tags: "+ data.tags.map(function(s) {
                            return s[0].toUpperCase() + s.slice(1)
                        }).join(", "))
                } else {
                    $("p.tags").text("Tags: None")
                }

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
