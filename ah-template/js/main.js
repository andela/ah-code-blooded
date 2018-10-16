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
        alignment: 'center',
        constrainWidth: false,
        coverTrigger: false
    });

    $("select").formSelect();

    let buttons = $(".following-button");
    buttons.on('mouseover', function () {
        $(this).removeClass("teal");
        $(this).addClass("red");
        $(this).html("UNFOLLOW");
    });

    buttons.on("mouseout", function () {
        $(this).removeClass("red");
        $(this).addClass("teal");
        $(this).html("FOLLOWING");
    })

    $(".favourite-button").click(function () {
        $(this).toggleClass("red-text");
        if ($(this).html() === "favorite_border") {
            $(this).html("favorite")
        } else {
            $(this).html("favorite_border")
        }
    });
});
