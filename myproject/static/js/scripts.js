$(document).ready(function () {
  /******************* */
  /* メニュー表示*/
  /******************* */
  $(window).on("scroll", function () {
    if ($(this).scrollTop() > 0) {
      $("header").addClass("active");
      $("#toTop").addClass("active");
    } else {
      $("header").removeClass("active");
      $("#toTop").removeClass("active");
    }
  });

  /******************* */
  /* トップへ戻る*/
  /******************* */
  $("#toTop").on("click", function () {
    $("html, body").animate({ scrollTop: 0 }, 250); // 500msでスクロール
  });

  /******************* */
  /* ハンバーガーメニュー*/
  /******************* */
  $("#js-hamburger-menu").on("click", function () {
    $(".sp-nav").toggleClass("active");
    $(".hamburger-menu").toggleClass("hamburger-menu--open");
  });


  $('#top-slider').slick({
    autoplay: true,
    autoplaySpeed: 5000,
  });
});
