function generateTOC(jObj) {
    function findChildHeaders(level=1) {
        return function (index, domElement) {
            text = domElement.textContent
            console.log(domElement.nodeName)
            console.log(domElement.textContent)
            if (level > 5) return;
            currentLevelTag = "h" + level
            for (i = level+1; i <= 5; ++i) {
                nextLevelTag = "h" + i
                nextLevelHeadings = $(this).nextUntil(currentLevelTag, nextLevelTag)
                if (nextLevelHeadings.length > 0) {
                    return [text, nextLevelHeadings.map(findChildHeaders(i)).get()]
                }
            }
            return text
        }
    }

    for (var i = 1; i <= 5; ++i) {
        headerTag = "h" + i;
        headers = jObj.children(headerTag)
        if (headers.length != 0) {
            console.log("Found header at level " + i)
            console.log(headers.map(findChildHeaders(i)).get())
            return
        }
    }
    console.log("Found no headers")
}
$(function(){addPermalinkToSections($(".article-html"))})
