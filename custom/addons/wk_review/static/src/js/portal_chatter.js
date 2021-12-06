odoo.define("wk_review.portal_chatter", function(require){
  "use strict";

  var portalChatter = require("portal.chatter");
  var PortalChatter = portalChatter.PortalChatter

  var publicWidget = require('web.public.widget');
  var portalChatterWidget = publicWidget.registry.portalChatter;

  var ajax = require("web.ajax");
  var core = require("web.core");
  var qweb = core.qweb;

  ajax.loadXML("/wk_review/static/src/xml/charts.xml",core.qweb);
  // ajax.loadXML("/wk_review/static/src/xml/read_more.xml",core.qweb);
  // ajax.loadXML("/wk_review/static/src/xml/filters.xml",core.qweb);

  PortalChatter.include({

    events: _.extend({}, portalChatter.PortalChatter.events, {
      'click #lazy_load_chatter': '_onClickLoader',
      'click .chart-dropdown .dropdown-menu a': 'selectChart',
      'click .read_more': 'expand_message',
      'click .filter-dropdown .dropdown-menu a': 'selectFilter',
    }),

    init: function(parent, options){
      this._super.apply(this, arguments);
      Chart.defaults.global.legend.position = 'right';
      this.page_counter = 1
    },

    start: function(){
      this._super.apply(this,arguments)
      this._removeReadMore();
      this._setInitialChart();
      // if ($(this.el).find("#lazy_load_chatter").length == 0){
      //   _.bindAll(this, 'detect_scroll');
      //   $(window).scroll(this.detect_scroll);
      // }
    },

    isUser: function(partner_id, like_ids){
      return like_ids.includes(partner_id)
    },

    preprocessMessages: function(messages){
      var messages = this._super.apply(this,arguments)
      var self = this
      _.each(messages, function (m) {
        m['isUser'] = self.isUser;
      });
      this.messages = messages;
      return messages;
    },

    _setInitialChart: function(){
      var dataStars = {}
      $(this.$el).find(".o_website_rating_select").each(function(){
        dataStars[$(this).data('star')+' Stars'] = parseInt($(this).find(".o_rating_progressbar").attr('aria-valuenow'))
      })
      this.dataStars = dataStars
      _.values(this.dataStars).reduce((a, b) => a + b) > 0 ? $(this.$el).find(".o_website_rating_progress_bars .dropdown .dropdown-menu").removeAttr("style") : $(this.$el).find(".o_website_rating_progress_bars .dropdown .dropdown-menu").hide();
        this.config = {
        type: 'pie',
        data: {
          datasets: [{
            label: _.keys(this.dataStars),
            data: _.values(this.dataStars).reduce((a, b) => a + b) > 0 ? _.values(this.dataStars):[0,0,0,0,1],
            backgroundColor: _.values(this.dataStars).reduce((a, b) => a + b) > 0 ? [
              'rgba(64, 91, 254, 1)',
              'rgba(68, 190, 252, 1)',
              'rgba(48, 230, 241, 1)',
              'rgba(151, 153, 248, 1)',
              'rgba(2, 231, 149, 1)',
            ] : '#d2dee2',
            borderWidth: 0
          }]
        },
      }
      this.changeChart('pie');
      // $(this.el).find('.o_portal_chatter_footer').hide();
    },

    _removeReadMore: function(){
      $(this.$el).find(".o_portal_chatter_messages .o_portal_chatter_message .media-body").each(function(){
        if($(this).height() < 150){
          $(this).find(".read_more").hide();
        }
      })
    },

    selectChart: function(ev){
      ev.preventDefault()
      $(document).find('.chart-dropdown #selected').text($(ev.currentTarget).text());
      this.changeChart($(ev.currentTarget).data('value'));
    },

    changeChart: function(type){
      var ctx = document.getElementById('charts').getContext('2d');
      if (this.myChart) {
        this.myChart.destroy();
      }

      var temp = jQuery.extend(true, {}, this.config);
      temp.type = type;
      var axis_value = {
        suggestedMin: 0,
        suggestedMax: 100,
        stepSize: 20,
      }

      if (type=='bar' || type=='horizontalBar'){
        temp.data['labels'] = _.keys(this.dataStars)
        temp.data.datasets[0].label = "Stars"
        temp['options'] = {
          scales: {
            yAxes: [{
              ticks: axis_value
            }]
          }
        }
        if(type == 'horizontalBar'){
          temp['options'] = {
            scales: {
              xAxes: [{
                ticks: axis_value
              }]
            }
          }
        }
      }
      else{
        temp.data['labels'] = _.keys(this.dataStars)
        delete temp['options']
      }
      this.myChart = new Chart(ctx, temp);
    },

    inViewPort: function(){
      var docViewTop = $(window).scrollTop();
      var docViewBottom = docViewTop + $(window).height();
      if ($(this.$el).find(".o_portal_chatter_message:last-child()").length > 0){
        var elemTop = $(this.$el).find(".o_portal_chatter_message:last-child()").offset().top;
        var elemBottom = elemTop + $(this.$el).find(".o_portal_chatter_message:last-child()").height();
      }
      if((elemBottom <= docViewBottom) && (elemTop >= docViewTop)){
        return true
      }
      else{
        return false
      }
    },

    detect_scroll: function(){
      if(this.inViewPort()){
        this.lazyLoadScroll();
      }
    },

    _renderMessages: function () {
      var self = this
      // console.log("this.messages", this.messages);
      if (this.messages.length < this.options['pager_step']){
        $(this.el).find("#lazy_load_chatter").attr("disabled", true);
      }
      this.sortByRating();
      var render = $(qweb.render("portal.chatter_messages", {widget: this}))
      // console.log("messagesae",this.messages);
      if (render.children().length > 0){
        self.$('.o_portal_chatter_messages').append(
          render
          .children()
          .each(function(){
            $(this).html();
          })
        );
      }
      this._removeReadMore();
    },

    sortByRating: function(){
      console.log("messages",this.messages);
    },

    _onClickLoader: function(ev){
      ev.preventDefault();
      this.page_counter++;
      this._changeCurrentPage(this.page_counter);
    },

    lazyLoadScroll: function(){
      this.page_counter++;
      this._changeCurrentPage(this.page_counter);
    },

    expand_message: function(ev){
      ev.preventDefault();
      $(ev.currentTarget).parent('.media-body').css({
        "max-height":"unset",
        "overflow":"unset",
      })
      $(ev.currentTarget).hide();
    },

    selectFilter: function(ev){
      ev.preventDefault();
      $(document).find('.filter-dropdown #selected').text($(ev.currentTarget).text());
      // var domain = [['rating_value', '>', 1]];
      // this._setFilterDomain(domain);
    },

    _setFilterDomain: function(domain){
      this.$('.o_portal_chatter_messages').empty();
      this._changeCurrentPage(1, domain);
    },
  });


  return portalChatterWidget.include({
    start: function () {
      var self = this;
      var defs = [];
      var chatter = new PortalChatter(this, this.$el.data());
      defs.push(chatter.appendTo(this.$el));
      return Promise.all(defs).then(function () {
        var dataStars = {}
        $(document).find(".o_website_rating_select").each(function(){
          dataStars[$(this).data('star')+' Stars'] = parseInt($(this).find(".o_rating_progressbar").attr('aria-valuenow'))
        })
        if (window.location.hash === '#' + self.$el.attr('id')) {
          $('html, body').scrollTop(self.$el.offset().top);
        }
      });
    },
  });
})
