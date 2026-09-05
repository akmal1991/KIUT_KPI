var homeSlider = $('#homeSlider').owlCarousel({
    loop: true,
    lazyLoad: true,
    margin: 0,
    dots: true,
    nav: false,
    autoplay: true,
    autoplayTimeout: 5000,
    smartSpeed: 1200,
    autoplayHoverPause: false,
    animateIn: 'fadeIn',
    animateOut: 'fadeOut',
    items: 1
});
// $('.customNextBtn').click(function() {
//     homeSlider.trigger('next.owl.carousel');
//   });
// $('.customPreviousBtn').click(function() {
//     homeSlider.trigger('prev.owl.carousel');
// });

$('#reviewsSlider').owlCarousel({
    loop: true,
    lazyLoad: true,
    margin: 30,
    dots: true,
    nav: false,
    autoplay: true,
    autoplayTimeout: 6000,
    smartSpeed: 1200,
    autoplayHoverPause: true,
    animateIn: 'fadeIn',
    animateOut: 'fadeOut',
    items: 1
});

$('#employees').owlCarousel({
    loop: true,
    lazyLoad: true,
    margin: 22,
    dots: false,
    nav: true,
    navText: [
        '<i class="fa fa-angle-left" aria-hidden="true"></i>',
        '<i class="fa fa-angle-right" aria-hidden="true"></i>'
    ],
    autoplay: true,
    autoplayTimeout: 4000,
    smartSpeed: 800,
    autoplayHoverPause: true,
    items: 4,
    responsive: {
        0: {
            items: 1,
            margin: 22
        },
        481: {
            items: 2,
            margin: 15
        },
        577: {
            items: 3,
            margin: 15
        },
        768: {
            items: 4,
            margin: 15
        },
        992: {
            items: 4,
            margin: 22
        }
    }
});


$(document).ready(function() {
    // Add minus icon for collapse element which is open by default
    $(".collapse.show").each(function() {
        $(this).prev(".card-header").children("h5").children("button").find(".myfa").addClass("icon-minus-circular-button").removeClass("icon-add-circular-outlined-button");

    });

    // Toggle plus minus icon on show hide of collapse element
    $(".collapse").on('show.bs.collapse', function() {
        $(this).prev(".card-header").find(".myfa").removeClass("icon-add-circular-outlined-button").addClass("icon-minus-circular-button");
    }).on('hide.bs.collapse', function() {
        $(this).prev(".card-header").find(".myfa").removeClass("icon-minus-circular-button").addClass("icon-add-circular-outlined-button");
    });
});

// $("document").ready(function($){
//     var nav = $('.header');
//     var top = $('.wrapper');
//     $(window).scroll(function () {
//         if ($(this).scrollTop() > 80) {
//             nav.addClass("fixed");
//             top.addClass("fixed");
//         } else {
//             nav.removeClass("fixed");
//             top.removeClass("fixed");
//         }
//     });
    
// });