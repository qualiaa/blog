function generateTOC(jObj) {
    function findChildHeaders(jObj, level=1) {
        console.log(jObj.text())
        if (level > 5) return;
        currentLevelTag = "h" + level
        nextLevelTag = "h" + (level + 1)
        nextLevelHeadings = jObj.nextUntil(nextLevelTag,currentLevelTag)
        return findChildHeaders(jObj, level=level+1)
    }

    for (var i = 1; i <= 5; ++i) {
        headerTag = "h" + i;
        headers = jObj.children(headerTag)
        if (headers.length != 0) {
            console.log("Found header at level " + i)
            return findChildHeaders(headers, level=i)
        }
    }
    console.log("Found no headers")
}
$(function(){addPermalinkToSections($(".article-html"))})
