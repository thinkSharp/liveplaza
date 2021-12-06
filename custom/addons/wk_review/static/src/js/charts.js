odoo.define("wk_review.charts", function(require){
  "use strict";

  var publicWidget = require('web.public.widget');

  var ajax = require("web.ajax");
  var core = require("web.core");

  ajax.loadXML("/wk_review/static/src/xml/charts.xml",core.qweb);

  publicWidget.registry.charts = publicWidget.Widget.extend({
    selector: "#reviewId",

    events: {
      'click .chart-dropdown .dropdown-menu a': 'selectChart',
    },

    init: function(parent, options){
      this._super.apply(this, arguments);
      Chart.defaults.global.legend.position = 'right';
    },

    start: function(){
      this._super.apply(this,arguments)
      if($(this.$el).find("#star_data").length != 0){
        this._setInitialChart();
      }
    },

    _setInitialChart: function(){
      var star_data = JSON.parse($(this.$el).find("#star_data").html().replace(/'/g, '"'))
      this.config = {
        type: 'pie',
        data: {
          labels: _.keys(star_data),
          datasets: [{
            label: "Total number of stars",
            data: _.values(star_data),
            backgroundColor: _.values(star_data).reduce((a, b) => a + b) > 0 ? [
              'rgba(64, 91, 254, 1)',
              'rgba(68, 190, 252, 1)',
              'rgba(48, 230, 241, 1)',
              'rgba(151, 153, 248, 1)',
              'rgba(2, 231, 149, 1)',
            ] : '#d2dee2',
            borderWidth: 0
            }]
          },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          },
      }
      this.changeChart('pie');
    },

    selectChart: function(ev){
      ev.preventDefault()
      $(document).find('.chart-dropdown #selected').text($(ev.currentTarget).text());
      this.changeChart($(ev.currentTarget).data('value'));
    },

    changeChart: function(type){
      var ctx = document.getElementById('wk_charts').getContext('2d');
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

      var star_data = JSON.parse($(this.$el).find("#star_data").html().replace(/'/g, '"'))

      if (type=='bar' || type=='horizontalBar'){
        temp.data['labels'] = _.keys(star_data)
        temp.data.datasets[0].label = "Stars"
        temp['options'] = {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            yAxes: [{
              ticks: axis_value
            }]
          },
        }
        if(type == 'horizontalBar'){
          temp['options'] = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              xAxes: [{
                ticks: axis_value
              }]
            },
          }
        }
      }
      else{
        temp.data['labels'] = _.keys(star_data)
        // delete temp['options']
      }
      this.myChart = new Chart(ctx, temp);
    },
  })
})
