jQuery(function ($) {

    //toggle sidebar
    $("#toggle-sidebar").click(function () {
        $(".page-wrapper").toggleClass("toggled");
    });
    //Pin sidebar
    $("#pin-sidebar").click(function () {
        if ($(".page-wrapper").hasClass("pinned")) {
            // unpin sidebar when hovered
            $(".page-wrapper").removeClass("pinned");
            $("#sidebar").unbind( "hover");
        } else {
            $(".page-wrapper").addClass("pinned");
            $("#sidebar").hover(
                function () {
                    console.log("mouseenter");
                    $(".page-wrapper").addClass("sidebar-hovered");
                },
                function () {
                    console.log("mouseout");
                    $(".page-wrapper").removeClass("sidebar-hovered");
                }
            )

        }
    });


    //toggle sidebar overlay
    $("#overlay").click(function () {
        $(".page-wrapper").toggleClass("toggled");
    });


    //custom scroll bar is only used on desktop
    if (!/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        $(".sidebar-content").mCustomScrollbar({
            axis: "y",
            autoHideScrollbar: true,
            scrollInertia: 300
        });
        $(".sidebar-content").addClass("desktop");

    }

    $('.dropdown-menu li').click(function(){
        $(this).parent().closest('div').find('.response-name-label').text($(this).text());
        var dataId= $(this).data('responseInfo');
        var requestId= $(this).data('requestInfo');

        $(".formatted-requests[data-request-id=" + requestId + "]").hide();
        $(".formatted-requests[data-id=" + dataId + "]").show();
    });

    $('.is-expandable').click(function () {
        var modal = $('#snippetModal');
        var current = $(this);
        $("#snippetModal .modal-header .title").empty().text(current.data('title'));

        $("#snippetModal code").text($(this).text());
        modal.toggle('.modal-open');
        modal.show();
    })

    $('.close').click(function () {
        var modal = $('#snippetModal');
        modal.toggle('.modal-open');
        modal.hide();
    })
});





