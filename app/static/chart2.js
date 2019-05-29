/*
本例子的目的是为了演示通过 Dom 事件、Highcharts 事件、Highcharts API 来讲一个页面中的多个图表进行联动的。
本例通过循环创建类似的图表并绑定鼠标的滑动事件来对多个图表进行演示联动效果。
*/
$(function () {
    /**
     * 为了让多个图表的提示框即十字准星线能够联动，这里绑定多个图表的附件 dom 的鼠标事件进行联动
     */
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
            // 添加 X 数据
            alert(dataset)
            $('<div class="chart">')
                .appendTo('#container')
                .highcharts({
                chart: {
                    marginLeft: 40, // Keep all charts left aligned
                    spacingTop: 20,
                    spacingBottom: 20,
                    zoomType: 'x'
                },
                title: {
                    text: dataset.name,
                    align: 'left',
                    margin: 0,
                    x: 30
                },
                credits: {
                    enabled: false
                },
                legend: {
                    enabled: false
                },
                xAxis: {
                    crosshair: true,
                    events: {
                        setExtremes: syncExtremes
                    },
                    labels: {
                        format: '{value} km'
                    }
                },
                yAxis: {
                    title: {
                        text: null
                    }
                },
                tooltip: {
                    positioner: function () {
                        return {
                            x: this.chart.chartWidth - this.label.width, // right aligned
                            y: -1 // align to title
                        };
                    },
                    borderWidth: 0,
                    backgroundColor: 'none',
                    pointFormat: '{point.y}',
                    headerFormat: '',
                    shadow: false,
                    style: {
                        fontSize: '18px'
                    },
                    valueDecimals: dataset.valueDecimals
                },
                series: [{
                    data: dataset.data,
                    name: dataset.name,
                    type: dataset.type,
                    color: Highcharts.getOptions().colors[i],
                    fillOpacity: 0.3,
                    tooltip: {
                        valueSuffix: ' ' + dataset.unit
                    }
                }]
            });
        });
    });
});
