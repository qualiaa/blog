"use strict"

$.fn.exists = function() {
    return this.length > 0 ? this : false;
}

function generateTOC(jObj) {
    function headerListToHTML(list) {
        let string = "<ul>";
        for (let el of list) {
            if (Array.isArray(el)) {
                string += headerListToHTML(el);
            } else {
                string += `
                        <li><a href="#${el.id}">${el.textContent}</a></li>
                    `;
            }
        }
        string += "</ul>";
        return string;
    }

    function findChildHeaders(level=1) {
        return function (index, domElement) {
            let text = domElement.textContent;
            let currentLevelTag = "h" + level;
            for (i = level+1; i <= 5; ++i) {
                let nextLevelTag = "h" + i;
                let nextLevelHeadings = $(this).nextUntil(currentLevelTag, nextLevelTag);
                if (nextLevelHeadings.length > 0) {
                    return [domElement, nextLevelHeadings.map(findChildHeaders(i)).get()];
                }
            }
            return domElement;
        }
    }

    let listOfHeaders = null;

    for (var i = 1; i <= 5; ++i) {
        let headerTag = "h" + i;
        let headers = jObj.children(headerTag);
        if (headers.length != 0) {
            listOfHeaders = headers.map(findChildHeaders(i)).get();
        }
    }

    if (listOfHeaders !== null) {
        ($("#toc").exists() ||
            $("<aside>").
                addClass("sidebar").
                prop("id","toc").
                appendTo("#side")
            ).html(`<h2>Contents</h2>
                ${headerListToHTML(listOfHeaders)}`
            );
    }

}
$(function() {
    let article = $(".article-html")
    generateTOC(article)
    addPermalinkToSections(article)
});

$(window).scroll(function() {
    let toc = $("#toc")
    if (toc.exists()) {
        let pos = window.scrollY + window.innerHeight/4;
        let headers = $(`.article-html h2,
           .article-html h3,
           .article-html h4,
           .article-html h5`)
            .map((i,el) => ({ el: el, offset: $(el).offset() }))
            .get();
        let closestHeader = null;

        for (let header of headers) {
            if (header.offset.top > pos) continue;
            if (closestHeader === null) {
                closestHeader = header;
            } else {
                if (closestHeader.offset.top < header.offset.top) {
                    closestHeader = header;
                }
            }
        }

        $("#toc a").removeClass("focused");
        if (closestHeader !== null) {
            $(`#toc a[href="#${closestHeader.el.id}"]`).addClass("focused");
        }
    }
});
