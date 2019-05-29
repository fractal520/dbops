/*
本例子的目的是为了演示通过 Dom 事件、Highcharts 事件、Highcharts API 来讲一个页面中的多个图表进行联动的。
本例通过循环创建类似的图表并绑定鼠标的滑动事件来对多个图表进行演示联动效果。
*/
$(function () {
    /**
     * 为了让多个图表的提示框即十字准星线能够联动，这里绑定多个图表的附件 dom 的鼠标事件进行联动
     */
    alert('a2');
    alert(check_id);
    alert('b2');
    alert(db_id);
    $('#container').bind('mousemove touchmove touchstart', function (e) {
        var chart,
            point,
            i,
            event;
        for (i = 0; i < Highcharts.charts.length; i = i + 1) {
            chart = Highcharts.charts[i];
            event = chart.pointer.normalize(e.originalEvent); // Find coordinates within the chart
            point = chart.series[0].searchPoint(event, true); // Get the hovered point
            if (point) {
                point.highlight(e);
            }
        }
    });
    /**
     * 重写内部的方法， 这里是将提示框即十字准星的隐藏函数关闭
     */
    Highcharts.Pointer.prototype.reset = function () {
        return undefined;
    };
    /**
     * 高亮当前的数据点，并设置鼠标滑动状态及绘制十字准星线
     */
    Highcharts.Point.prototype.highlight = function (event) {
        this.onMouseOver(); // 显示鼠标激活标识
        this.series.chart.tooltip.refresh(this); // 显示提示框
        this.series.chart.xAxis[0].drawCrosshair(event, this); // 显示十字准星线
    };
    /**
     * 同步缩放效果，即当一个图表进行了缩放效果，其他图表也进行缩放
     */
    function syncExtremes(e) {
        var thisChart = this.chart;
        if (e.trigger !== 'syncExtremes') {
            Highcharts.each(Highcharts.charts, function (chart) {
                if (chart !== thisChart) {
                    if (chart.xAxis[0].setExtremes) {
                        chart.xAxis[0].setExtremes(e.min, e.max, undefined, false, { trigger: 'syncExtremes' });
                    }
                }
            });
        }
    }
    // 获取 JSON 数据，数据文件地址：
    //https://github.com/highcharts/highcharts/blob/master/samples/data/activity.json
    $.getJSON('/chart/getdata', {check_id:check_id, db_id:db_id}, function (activity) {
        $.each(activity.datasets, function (i, dataset) {
            $('<div class="chart">')
                .appendTo('#container')
                .highcharts({
                chart: {
                    renderTo : 'container'
                },
                rangeSelector: {
                    allButtonsEnabled: true,
                    inputEnabled: $('#container').width() > 480,
                    buttons: [{
                        type:'day',
                        count:1,
                        text:'1d'
                    },{
                        type:'hour',
                        count:3,
                        text:'3h'
                    },{
                        type:'hour',
                        count:1,
                        text:'1h'
                    },{
                        type:'minute',
                        count:30,
                        text:'0.5h'
                    },{
                        type:'minute',
                        count:10,
                        text:'10m'
                    },{
                        type:'minute',
                        count:1,
                        text:'1m'
                    },{
                        type:'all',
                        text:'all'
                    }],
                    inputBoxWidth: 80,
                    inputDateFormat: '%m-%d %H:%M',
                    inputEditDateFormat:'%m-%d %H:%M',
                    selected: 2
                },
                tooltip: {
                    dateTimeLabelFormats: {
                        millisecond: '%H:%M:%S.%L',
                        second: '%H:%M:%S',
                        minute: '%H:%M',
                        hour: '%H:%M',
                        day: '%m-%d',
                        week: '%m-%d',
                        month: '%Y-%m',
                        year: '%Y'
                    }
                },
                exporting:{
                    enabled:true
                },
                title : {
                    text : dataset.check_name
                },
                subtitle:{
                    text: dataset.dbname
                },
                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: {
                        millisecond: '%H:%M:%S.%L',
                        second: '%H:%M:%S',
                        minute: '%H:%M',
                        hour: '%H:%M',
                        day: '%m-%d',
                        week: '%m-%d',
                        month: '%Y-%m',
                        year: '%Y'
                    },
                    title:{
                        text:null
                    }
                },
                yAxis: {
                    crosshair: true,
                    max: dataset.max_num,
                    title: {
                        text: null
                    },
                    plotLines: [{
                        value: dataset.max_num*0.9,
                        color:'red',
                        width: 2,
                        dashStyle: 'shortdash',
                        label: {
                            text: 'the 90%'
                        }
                    },{
                        value: dataset.max_num*0.8,
                        color:'orange',
                        width: 2,
                        dashStyle: 'shortdash',
                        label: {
                            text: 'the 80%'
                        }
                    }]
                },
                series: [{
                    name: dataset.check_name,
                    data : dataset.data,
                    type: 'spline',
                    dataGrouping: {
                        dateTimeLabelFormats: {
                            millisecond: ['%Y-%m-%d %H:%M:%S.%L', '%Y-%m-%d %H:%M:%S.%L', '~%H:%M:%S.%L'],
                            second: ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '~%H:%M:%S'],
                            minute: ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M', '~%H:%M'],
                            hour: ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M', '~%H:%M'],
                            day: ['%Y-%m-%d', '%Y-%m-%d', '~%m-%d'],
                            week: ['%Y-%m-%d', '%Y-%m-%d', '~%m-%d'],
                            month: ['%Y-%m', '%Y-%m', '~%Y-%m'],
                            year: ['%Y', '%Y', '~%Y']
                        }
                    }
                }]
            });
        });
    });
});
