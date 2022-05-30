 $(function() {
   var print = function(msg) {
     alert(msg);
   };

   var setInvisible = function(scroll_x) {
     scroll_x.css('visibility', 'hidden');
   };
   var setVisible = function(scroll_x) {
     scroll_x.css('visibility', 'visible');
   };

   var scroll_x = $("#scroll_x");
   var items = scroll_x.children();

   // Inserting Buttons
   scroll_x.prepend('<div id="right-button" style="visibility: hidden;"><a class="arrow" style="color: red;"><</a></div>');
   scroll_x.append('  <div id="left-button"><a class="arrow" style="color: red;">></a></div>');

   // Inserting Inner
   items.wrapAll('<div id="inner" />');

   // Inserting Outer
   scroll_x.find('#inner').wrap('<div id="outer"/>');

   var outer = $('#outer');

   var updateUI = function() {
     var maxWidth = outer.outerWidth(true);
     var actualWidth = 0;
     $.each($('#inner >'), function(i, item) {
       actualWidth += $(item).outerWidth(true);
     });

     if (actualWidth >= maxWidth) {
       setVisible($('#left-button'));
     }
     else {
        setInvisible($('#left-button'));
     }
   };
   updateUI();



   $('#right-button').click(function() {
   setVisible($('#left-button'));
     var leftPos = outer.scrollLeft();
     outer.animate({
       scrollLeft: leftPos - 200
     }, 800, function() {
//       debugger;
       if ($('#outer').scrollLeft() <= 0) {
         setInvisible($('#right-button'));
       }
     });
   });

   $('#left-button').click(function(ev) {
     setVisible($('#right-button'));
     outer = =document.getElementById('outer') ;
     var leftPos = outer.scrollLeft();
     outer.animate({
       scrollLeft: leftPos + 200
     }, 800);
    var  width=outer.width();
    var scrollWidth = outer.get(0).scrollWidth;
    var scroll_left = $('#outer').scrollLeft();
    var result =  scrollWidth- scroll_left  -width;
     if (scrollWidth - $('#outer').scrollLeft() - width < 1) {
         setInvisible($('#left-button'));
       }
    ev.preventDefault();
   });

//   $(window).resize(function() {
//     updateUI();
//   });
 });
