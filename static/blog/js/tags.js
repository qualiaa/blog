"use strict"

/*
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
*/

var TAG_URL = "/blog/tags/"

function tagMod(buttonObject) {
    var activeTag = buttonObject.parentNode.id;
    var newTags = null;
    if (typeof(currentTags) !== "undefined") {
        if (currentTags.includes(activeTag)) {
            var index = currentTags.indexOf(activeTag);
            currentTags.splice(index,1);
            newTags = currentTags;
        } else {
            newTags = [activeTag].concat(currentTags)
        }
    } else {
        var newTags = [activeTag];
    }

    if (newTags.length > 0) {
        window.location=TAG_URL + newTags.join("+");
    } else {
        window.location="/blog/";
    }


    return false;
}
