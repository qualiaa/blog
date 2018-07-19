"use strict"
 
var jaxFinishedRendering = true
window.MathJax = {
    showProcessingMessages: false,
    messageStyle: "none",
    rmessageStyle: "none",
    "fast-preview": {
        disabled: true
    }
}

var updateTime = 1000
var requestUrl = "/json/wip/" + slug

$(function() {
    setInterval(function() {
        $.get(requestUrl,
            function(data) {
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

                if (!jaxFinishedRendering) {
                    return
                }
                var article_html = data["html"]
                
                function swapBuffers() {
                    var temp=$("div#article-html")
                    $("div#buffer").attr("id","article-html")
                    temp.attr("id","buffer")
                    jaxFinishedRendering = true
                }

                var buffer = $("#buffer")
                if (buffer.length == 0) {
                    buffer = $("<div id='buffer'></div>")
                    buffer.insertAfter("#article-html")
                    
                }
                buffer.html(article_html)
                buffer.find("pre code").each(function(i, block) {
                    hljs.highlightBlock(block)
                })
                jaxFinishedRendering = false
                MathJax.Hub.Queue(["Typeset",MathJax.Hub,buffer[0],swapBuffers])



            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.log("Failure\n"+textStatus + "\n" + errorThrown)
                console.log(jqXHR.responseText)
            })
    }, updateTime)
})

/*
 * MathJax attempts that didn't work:
 */
    /*
     * Attempt to process MathJax script elements and add the
     * processed elements to the page
     *
    var article_html = data["html"]
    var wrapper_object = $("<div>").append($(article_html))

    wrapper_object.find("script[type='math/tex']").html(function() {
        console.log(MathJax.HTML.Element("div",null,this.outerHTML).outerHTML)
        return MathJax.HTML.Element("div",null,this.outerHTML).outerHTML
    })
    $("#article-html").html(wrapper_object.html())
    */
    
    /*
     * Attempt to typeset the whole dom fragment before adding to
     * the page
     *
    var article_html = data["html"]
    var wrapper_object = $("<div>").append($(article_html))
    var domFragment = wrapper_object[0]

    console.log("MathJaxing")
    console.log(domFragment)
    var wrapper_object = $("<div>").append($(article_html))
    var domFragment = wrapper_object[0]
    MathJax.Hub.Queue(["Typeset",MathJax.Hub, domFragment, function(x) {
        console.log(domFragment === wrapper_object[0])
        console.log(domFragment)
        $("#article-html").html(wrapper_object.html())
        $("#article-html pre code").each(function(i, block) {
            hljs.highlightBlock(block)
        })
    }])
    */
