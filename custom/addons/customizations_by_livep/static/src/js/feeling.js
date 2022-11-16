$(document).ready(function () {
  $('.feeling-carousel').owlCarousel({
    margin: 10,
    nav: false,
    dots: true,
    loop: false,
    responsive: {
      0: {
        items: 2,
      },
      480: {
        items: 3,
      },
      786: {
        items: 5,
      },
      1024: {
        items: 6,
      },
    }
  })
})
