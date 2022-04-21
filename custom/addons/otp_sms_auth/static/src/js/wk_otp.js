/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('otp_sms_auth.wk_otp', function (require) {
    "use strict";
    
    var otp_auth = require('otp_auth.wk_otp');
    var ajax = require('web.ajax');
    $(document).ready(function() {
        if (!$(this).find('#wkmobile label[for=mobile], input#mobile').text()) {
            $('label[for=mobile], input#mobile').hide();
        }
        $('input:radio[name="radio-login"]').change(function() {
            if ($(this).val() == 'radiemail') {
                $('label[for=login], input#login').show();
                $('label[for=mobile], input#mobile').hide();
            } else if ($(this).val() == 'radiomobile') {
                $('label[for=mobile], input#mobile').show();
                $('label[for=login], input#login').hide();
            }
        });

        $('input:radio[name="radio-register"]').change(function() {
            document.getElementById('login').value = "";
            if ($(this).val() == 'radioemail') {
                $('label[for=login]').show();
                $('label[for=phone]').hide();
                $('input#mobile').prop("readonly", false);
                document.getElementById('login').value = "";
                document.getElementById('mobile').value = "";
                if($('input#mobile').val() == "") {
                    $('input#login').change(function() {
                        $('input#mobile').val("");
                    });
                }

            } else if ($(this).val() == 'radiomobile') {
                $('label[for=phone]').show();
                $('label[for=login]').hide();
                $('input#mobile').prop("readonly", true);
                document.getElementById('login').value = "";
                document.getElementById('mobile').value = "";
                $('input#login').change(function() {
                    $('input#mobile').val($('input#login').val());
                });
            }
        });

        $('.wk_next_btn').on('click', function(e) {
            $(".field-login-option").hide();
            $(".field-mobile").hide();
            var radioVal = $('input[name=radio-otp]:checked').val();
            if ($("#smsotp").css("display") == 'none') {
                $('#smsotp').show();
                getUserData();
            } else {
                if (radioVal == 'radiotp') {
                    getUserEmail();
                }
                if (radioVal == 'radiotp') {
                    generateSMSLoginOtp();
                } else {
                    if ($('label[for=mobile], input#mobile').css('display') == 'none') {
                        $('label[for=mobile], input#mobile').val('');
                    } else {
                        if ($('label[for=login], input#login').css('display')) {
                            $('label[for=login], input#login').val('');
                        }
                    }
                }
            }
        });
        $('.wk_back_btn').on('click', function(e) {
            if ($(".field-otp-option").css("display") == 'none') {
                $(".field-login-option").show();
                $(".field-mobile").show();
            }
        });
        $(this).on('click', '.wk_login_resend', function(e) {
            generateSMSLoginOtp();
        });

        $('.wk_send').on('click', function(e) {
            var mobile = $('#mobile').val();
            if (!mobile) {
                alert(mobile+"Please enter a mobile number");
                $('#wk_error').remove();
                $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter a mobile no </p>");
            }
        });
    });

    function generateSMSLoginOtp() {
        var mobile = $('#mobile').val();
        var otp_type = $('.otp_type').val();
        // $("div#wk_loader").addClass('show');
        var loginType = $('input:radio[name="radio-login"]:checked').val();
        // if (loginType == 'radiomobile') {
        //     ajax.jsonRpc("/send/sms/otp", 'call', {'mobile':mobile})
        //         .then(function (data) {
        //             if (data[0] == 1) {
        //                 $("div#wk_loader").removeClass('show');
        //                 $('#wk_error').remove();
        //                 if (data[3]) {
        //                     $('label[for=login], input#login').val(data[3]);
        //                 }
        //                 getSMSLoginInterval(data[2]);
        //                 $(".field-password").show();
        //                 $("#passwogenerateSMSSignUpOtprd").attr('placeholder', 'Enter OTP');
        //                 if (otp_type == '4') {
        //                     $("#password").attr("type", "text");
        //                 }
        //                 $(".field-password").after("<p id='wk_error' class='alert alert-success'>" +data[1] + "</p>");
        //                 $(":submit").show();
        //                 $(".wk_next_btn").hide();
        //                 $(".field-otp-option").css("display","none");
        //             } else {
        //                 $("div#wk_loader").removeClass('show');
        //                 $('#wk_error').remove();
        //                 $(".field-otp-option").after("<p id='wk_error' class='alert alert-danger'>" +data[1] + "</p>");
        //             }
        //         }).fail(function (error){
        //             console.log(error)
        //         });
        // } else {
        //     $("div#wk_loader").removeClass('show');
        // }
        
    }

    function getUserEmail() {
        var mobile = $('#mobile').val();
        var login = $('#login').val();
        $("div#wk_loader").addClass('show');
        var loginType = $('input:radio[name="radio-login"]:checked').val();
        if (loginType) {
            ajax.jsonRpc("/get/user/email", 'call', {'mobile':mobile, 'login':login})
                .then(function (data) {
                    if (data.status == 1) {
                        $("div#wk_loader").removeClass('show');
                        $('#wk_error').remove();
                        if (mobile) {
                            $('label[for=login], input#login').val(data.login);
                        } else {
                            $('label[for=mobile], input#mobile').val(data.mobile);
                        }
                        $(".field-password").show();
                        $(":submit").show();
                        $(".wk_next_btn").hide();
                        $(".field-otp-option").css("display","none");
                    } else {
                        $("div#wk_loader").removeClass('show');
                        $('#wk_error').remove();
                        $(".field-otp-option").after("<p id='wk_error' class='alert alert-danger'>" +data.message + "</p>");
                    }
                });
        }        
    }

    function getUserData() {
        var mobile = $('#mobile').val();
        var login = $('#login').val();
        var loginType = $('input:radio[name="radio-login"]:checked').val();
        if (loginType) {
            ajax.jsonRpc("/get/user/email", 'call', {'mobile':mobile, 'login':login})
                .then(function (data) {
                    if (data.status == 1) {
                        if (mobile) {
                            $('label[for=login], input#login').val(data.login);
                        } else {
                            $('label[for=mobile], input#mobile').val(data.mobile);
                        }
                    }
                });
        }
    }

    function getSMSLoginInterval(otpTimeLimit) {
        var countDown = otpTimeLimit;
        var x = setInterval(function() {
            countDown = countDown - 1;
            $("#otplogincounter").html("OTP will expire in " + countDown + " seconds.");
            if (countDown < 0) {
                clearInterval(x);
                $('#wk_error').remove();
                $("#otplogincounter").html("<a class='btn btn-link pull-right wk_login_resend' href='#'>Resend OTP</a>");
            }
        }, 1000);
        // session.setCounterInterval(x);
    }
});
