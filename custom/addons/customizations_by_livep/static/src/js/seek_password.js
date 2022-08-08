

// $(document).ready(function(){
//  $("#seekPassword").click(function(){
//     var seekPassword = document.querySelector("#seekPassword");
//     var password = document.querySelector("#password");
//     var type = password.getAttribute("type") === "password" ? "text" : "password";
//     password.setAttribute("type", type);
//     // toggle the icon
//     //seekPassword.classList.toggle("fa-eye");
//     $('#seekPassword').toggleClass("fa-eye-slash fa-eye");

//     // prevent form submit
//     const form = document.querySelector("form");
//     form.addEventListener('submit', function (e) {
//         e.preventDefault();
//     });
//  });
// });

// $(document).ready(function() {

//     $("#seekPassword").click(function() {
  
//       var className = $("#icon").attr('class');
//       className = className.indexOf('slash') !== -1 ? 'fa fa-eye' : 'fa fa-eye-slash'
  
//       $("#icon").attr('class', className);
//       var input = $("#pass");
  
//       if (input.attr("type") == "text") {
//         input.attr("type", "password");
//       } else {
//         input.attr("type", "text");
//       }
//     });
  
//   });

  function mouseoverPass(obj) {
    var obj = document.getElementById('password');
    obj.type = "text";
  }
  function mouseoutPass(obj) {
    var obj = document.getElementById('password');
    obj.type = "password";
  }
