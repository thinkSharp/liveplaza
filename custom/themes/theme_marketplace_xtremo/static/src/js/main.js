$(document).ready(function(){
  var href = window.location.pathname;
  if (href.includes("/seller") == true){
    $('.js_sale').addClass('xt-market-place');
  }
  if (href.includes('/seller/profile/')){
    $('#wrap').addClass('xt-seller-profile');
  }
  if (href.includes('/seller/shop/')){
    $('#wrap').addClass('xt-seller-shop');
  }
})
