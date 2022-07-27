
$(document).ready(function(){

    // accordion for faq question and answer
    $('.faq_accordian').click(function(){
    // $(this).parent().find('.faq_arrow').toggleClass('arrow-animate');
      $(this).parent().find('.faq_answer').slideToggle(280);
    });

    // accordion for faq category
    $('.faq_categ_accordion').click(function() {
        $(this).parent().find('.faq_categ_inner').slideToggle(400);
    });

});