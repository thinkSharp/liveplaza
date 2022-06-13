/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
//Resolve Conflict Production Server

odoo.define('otp_auth.wk_otp', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    $(document).ready(function() {
        var ValidUser = 0;
        if ($('#otpcounter').get(0)) {
            $("#otpcounter").html("<center><a class='btn btn-link wk_send' href='#'>Send OTP</a></center>");
            $(".field-confirm_password").after("<p class='alert alert-info'>OTP will be sent to your registered Email or Phone number. Please Click Send OTP button and use OTP code in order to complete the registration. </p>");
//            $(":submit").attr("disabled", true);
            $(":submit").css("display", "none");
            $(".btn-sm").css("width", "100%");
            $("#otp").css("display","none");
//            $( ".oe_signup_form" ).wrapInner( "<div class='container' id='wk_container'></div>");
        }

        $('.wk_send').on('click', function(e) {
            if($(this).closest('form').hasClass('oe_reset_password_form')){
                ValidUser = 1;
            }
            var input = [];
            var input2 = [];
            var login =  $('input[name="radio-register"]:checked').val();
            var email = $('#login').val();
            var phone = $('#mobile').val();
            var name = $('#name').val();
            var country = $('#country_id').val();
            var pwd = $('#password').val();
            var confirm_pwd = $('#confirm_password').val();
            var empty_field_count = 0;
            var empty_field = "";
            var error = [];
            var required_field = [];

            if(login == "radioemail") {
                input.push(email, name, phone, country, pwd, confirm_pwd);
                input2.push("Email", "Name", "Mobile number", "Country", "Password", "Confirm Password");
            }
            else {
                input.push(email, name, country, pwd, confirm_pwd);
                input2.push("Mobile number", "Name", "Country", "Password", "Confirm Password");
                phone = email;
            }


            for(var i = 0 ; i < input.length; i++) {
                if(input[i] == "") {
                    empty_field = input2[i];
                    empty_field_count ++;
                }
            }

            if(empty_field_count > 1) {
                $('#wk_error').remove();
                $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please fill out all required fields!</p>");
            }
            else if (empty_field_count == 1) {
                $('#wk_error').remove();
                $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please fill out the required field '" + empty_field + "' </p>");
            }
            else if (phone.length < 9 || phone.length > 11) {
                $('#wk_error').remove();
                $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Phone number length must be between 9 and 11.</p>");
            }
            else {
                if(login == "radioemail")
                {
                    if (email) {
                        if(validateEmail(email)) {
                            if(pwd.length < 8) {
                                $('#wk_error').remove();
                                $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'> Password must have at least 8 characters! </p>");
                            }
                            else {
                                if(pwd == confirm_pwd)
                                    generateOtp(ValidUser);
                                else {
                                    $('#wk_error').remove();
                                    $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Passwords do not match</p>");
                                }
                            }
                        } else {
                            $('#wk_error').remove();
                            $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter a valid email address.</p>");
                        }
                    } else {
                        $('#wk_error').remove();
                        $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter an email address.</p>");
                    }
                }
                else {
                    phone = email;
                    if (phone) {
                        if(validatePhone(phone)) {
                            if(pwd.length < 8) {
                                $('#wk_error').remove();
                                $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'> Password must have at least 8 characters! </p>");
                            }
                            else {
                                if(pwd == confirm_pwd)
                                    generateOtp(ValidUser);
                                else {
                                    $('#wk_error').remove();
                                    $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Passwords do not match</p>");
                                }
                            }
                        } else {
                            $('#wk_error').remove();
                            $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter a valid phone number.</p>");
                        }
                    } else {
                        $('#wk_error').remove();
                        $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>Please enter a phone number.</p>");
                    }
                }
            }

        });
        $(this).on('click', '.wk_resend', function(e) {
            $(".wkcheck").remove();
            generateOtp(ValidUser);
        });
        verifyOtp();
    });

    function validateEmail(emailId) {
        var mailRegex = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
        return mailRegex.test(emailId);
    };

    function validatePhone(phone) {
        if(isNaN(phone))
            return false;
        else
            return true;
    }

    function getInterval(otpTimeLimit) {
        var countDown = otpTimeLimit;
        var x = setInterval(function() {
            countDown = countDown - 1;
            $("#otpcounter").html("OTP will expire in " + countDown + " seconds.");
            if (countDown < 0) {
                clearInterval(x);
                $("#otpcounter").html('');
                $("#otpcounter").append('<span>Otp is expire.Please Click on resend button</span>');
                $("#otpcounter").after("<center><a class='btn btn-link wk_resend' href='#'>Resend OTP</a></center>");
//                $(":submit").attr("disabled", true);
                $(":submit").click(function(ev){
                    $('#wk_error').remove();
                    $("#otpcounter").after("<p id='wk_error' class='alert alert-danger'>Please type the otp correctly!</p>");
                    ev.preventDefault();
                });
            }
        }, 1000);
    }

    function generateOtp(ValidUser) {
        var email = $('#login').val();
        var mobile = $('#mobile').val();
        var userName = $('#name').val();
        var country_id = $('#country_id').val();
        $("div#wk_loader").addClass('show');
        $('#wk_error').remove();
        $('.alert.alert-danger').remove();

        ajax.jsonRpc("/generate/otp", 'call', {'email':email, 'userName':userName, 'mobile':mobile, 'country':country_id,'validUser':ValidUser})
            .then(function (data) {
                if (data[0] == 1) {
                    $("div#wk_loader").removeClass('show');
                    $('.wk_send').remove();
                    $('.wk_resend').remove();
                    getInterval(data[2]);
                    $("#wkotp").after("<p id='wk_error' class='alert alert-success'>" +data[1] + "</p>");
                    $("#otp").css("display","");
                    $(":submit").css("display", "");
                    $("#otp").val("");
                    $('#otp').after($('#otpcounter'));
                } else {
                    $("div#wk_loader").removeClass('show');
                    $('#wk_error').remove();
                    $(".field-confirm_password").after("<p id='wk_error' class='alert alert-danger'>" +data[1] + "</p>");
                }
            });
    }

    function verifyOtp() {
        $('#otp').bind('input propertychange', function() {
            if ($(this).val().length == 6) {
                var otp = $(this).val();
                ajax.jsonRpc("/verify/otp", 'call', {'otp':otp})
                    .then(function (data) {
                        if (data) {
                            $(":submit").unbind('click');
                            $('#otp').after("<i class='fa fa-check-circle wkcheck' aria-hidden='true'></i>");
                            $(".wkcheck").css("color","#3c763d");
                            $('#wkotp').removeClass("form-group has-error");
                            $('#wkotp').addClass("form-group has-success");
                            $(":submit").removeAttr("disabled").find('.fa-refresh').addClass('d-none');
                        } else {
//                            $(":submit").attr("disabled", true);
                            $(":submit").click(function(ev){
                                $('#wk_error').remove();
                                $("#otpcounter").after("<p id='wk_error' class='alert alert-danger'>Please type the otp correctly!</p>");
                                ev.preventDefault();
                                ev.stopPropagation();
	    	                    ev.stopImmediatePropagation();
                            });
                            $('#otp').after("<i class='fa fa-times-circle wkcheck' aria-hidden='true'></i>");
                            $('#wkotp').removeClass("form-group has-success");
                            $(".wkcheck").css("color","#a94442");
                            $('#wkotp').addClass("form-group has-error");
                        }
                    });
            } else {
//                $(":submit").attr("disabled", true);
                $(":submit").click(function(ev){
                    $('#wk_error').remove();
                    $("#otpcounter").after("<p id='wk_error' class='alert alert-danger'>Please type the otp correctly!</p>");
                    ev.preventDefault();
                    ev.stopPropagation();
	    	        ev.stopImmediatePropagation();
                });
                $(".wkcheck").remove();
                $('#wkotp').removeClass("form-group has-success");
                $('#wkotp').removeClass("form-group has-error");
                $('#wkotp').addClass("form-group");
            }
        });
    }

})