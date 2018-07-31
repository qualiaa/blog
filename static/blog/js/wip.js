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
var requestUrl = "/blog/json/wip/" + slug
var mtime = 0


// code from 
// https://docs.djangoproject.com/en/2.0/ref/csrf/#setting-the-token-on-the-ajax-request
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(function() {
    setInterval(function() {
        $.post(requestUrl,
            {"mtime": mtime},
            function(data) {
                if (data === undefined) {
                    return;
                }
                /* Update the page metadata first */
                if (data.hasOwnProperty("title")) {
                    var title = data["title"]
                    $("h1.article-title").text(title)
                }
                if (data.hasOwnProperty("tags")) {
                    $("span.tags").text("Tags: "+ data.tags.map(function(s) {
                            return s[0].toUpperCase() + s.slice(1)
                        }).join(", "))
                } else {
                    $("span.tags").text("Tags: None")
                }

                if (data.hasOwnProperty("mtime")) {
                    mtime = data["mtime"]
                }

                /* If we're still rendering the previous MathJax then skip */
                if (!jaxFinishedRendering) {
                    return
                }

                /* Update the article HTML */
                var article_html = data["html"]
                
                function swapBuffers() {
                    $("div.article-html").toggleClass("buffer")
                    jaxFinishedRendering = true
                }

                /* If a buffer element doesn't exist, create it */
                var buffer = $(".buffer")
                if (buffer.length == 0) {
                    buffer = $("<div></div>")
                        .addClass("article-html")
                        .addClass("buffer")
                    buffer.insertAfter(".article-html")
                }

                /* Set the buffer HTML */
                buffer.html(article_html)

                /* Process article */
                highlightCode(buffer)
                addPermalinkToSections(buffer)

                /* Queue a MathJax typeset job */
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
