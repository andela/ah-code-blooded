function auto_grow(element) {
    element.style.height = "5px";
    element.style.height = (element.scrollHeight) + "px";
}

$(document).ready(function () {
    $('.chips').chips();
    $('.chips-placeholder').chips({
        placeholder: "Enter a tag",
        secondaryPlaceholder: '+Tag'
    });
    $('.modal').modal();
    $('.dropdown-trigger').dropdown({
        alignment : 'center',
        constrainWidth: false,
        coverTrigger: false
    });
});
