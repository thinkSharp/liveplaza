

$(document).ready(function(){
 $("#seekPassword").click(function(){
    var seekPassword = document.querySelector("#seekPassword");
    var password = document.querySelector("#password");
    var type = password.getAttribute("type") === "password" ? "text" : "password";
    password.setAttribute("type", type);
    // toggle the icon
    seekPassword.classList.toggle("fa-eye");
//    $('#seekPassword').find("i").toggleClass("fa-eye-slash fa-trash");

    // prevent form submit
    const form = document.querySelector("form");
    form.addEventListener('submit', function (e) {
        e.preventDefault();
    });
 });
});


