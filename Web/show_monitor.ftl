<!DOCTYPE  html>
<html>
<head>
    <meta charset="UTF-8">
    <META HTTP-EQUIV="pragma" CONTENT="no-cache">
    <META HTTP-EQUIV="Cache-Control" CONTENT="no-store, must-revalidate">
    <META HTTP-EQUIV="expires" CONTENT="0">
    <title>金纳算法--系统监控</title>
    <link rel="stylesheet" type="text/css" href="easyui/themes/black/easyui.css">
    <link rel="stylesheet" type="text/css" href="easyui/themes/icon.css">
    <script type="text/javascript" src="easyui/jquery-1.10.2.min.js"></script>
    <script type="text/javascript" src="easyui/jquery.easyui.min.js"></script>
    <style type="text/css">
        body {
            background-color: #999;
        }

        table th {
            text-align: center;

        }

        table td {
            text-align: center;
        }

        td:first-child {
            text-align: center;
        }


    </style>

</head>
<body>


<div style="margin:0 auto;width:1185px">
    <div id="updatetime" style="display: none">${updatetime}</div>
    <table style="width:885px;">
        <tr>
            <td style="width:600px;padding-left:200px; ">
                <h2 style="text-align:center;display: inline">金纳算法系统监控</h2>
            </td>
            <td style="width: 285px;text-align: right">
                欢迎您,${username}
            </td>
        </tr>
        <tr>
            <td style="width:600px;padding-left:200px; ">&nbsp;</td>
            <td style="text-align: right">
                <a href="logoutMonitor" type="button" style="padding-right: 5px;text-decoration:none">退出</a>
            </td>
        </tr>
        <tr>
            <td>&nbsp;</td>
        </tr>
    </table>

    <table id="table_java_monitor" class="easyui-datagrid" style="width:1185px;"
           data-options="singleSelect:true">
        <thead>
        <tr>
            <th data-options="field:'hostname',width:'125px',headAlign:'center',">Hostname</th>
            <th data-options="field:'ip',width:'125px',headAlign:'center',">IP</th>
            <th data-options="field:'target',width:'300px',headAlign:'center',align:'left'">
                监控对象
            </th>
            <th data-options="field:'cpu',width:'125px',headAlign:'center'," formatter='cpu_format'>CPU (Usage)</th>
            <th data-options="field:'memory',width:'125px',headAlign:'center'," formatter='memory_format'>Memory
                (Usage)
            </th>
            <th data-options="field:'disk',width:'125px',headAlign:'center'," formatter='disk_format'>Disk (Usage)</th>
            <th data-options="field:'status',width:'125px',headAlign:'center'">Status</th>
            <th data-options="field:'updatetime',width:'125px',headAlign:'center'" formatter='updatetime_format'>
                UpdateTime
            </th>
        </tr>
        </thead>
    </table>


</div>
<div style="clear:both ;height:100px;"></div>
<script type="text/javascript">
    timegap =${timegap};
    timegap = parseInt(timegap) * 1000;
    timeinterval =${timeinterval};
    timeinterval = parseInt(timeinterval) * 1000;
    cpu_threshold =${cpu_threshold};
    memory_threshold =${memory_threshold};
    disk_threshold =${disk_threshold};
    $(function () {
        showTime();

    });

    function showTime() {
        var readtime = getNowFormatDate();
        // $("#updatetime").html(readtime);

        loadMonitor();
        setTimeout("showTime()", timeinterval);

    }

    function target_format(value, record, index) {
        var pattern_from_genus = new RegExp("Genus.*->");
        var pattern_to_genus = new RegExp("->Genus");

        if (value.match(pattern_from_genus) != null) {
            return '<span style="background-color:#638c5c;">' + value + '</span>';
        } else if (value.match(pattern_to_genus) != null) {
            return '<span style="background-color:#878854;">' + value + '</span>';
        } else {
            return '<span >' + value + '</span>';
        }
    }

    function cpu_format(value, record, index) {
        var pattern = new RegExp("^\\d+-{1}(\\d{2}:{1}){2}");
        var r = value.match(pattern);
        if (r != null) {
            var readtime = strToDate($("#updatetime").html());
            var updatetime = strToDate(value);
            if (Math.abs(updatetime - readtime) > 60 * 1000) {
                return '<span style="color:red;font-weight: bold">' + value + '</span>';
            } else {

                return '<span >' + value + '</span>';
            }

        } else if (parseFloat(value.substring(0, value.length - 1)) > cpu_threshold) {
            return '<span style="color:red;font-weight: bold">' + value + '</span>';
        } else {

            return '<span >' + value + '</span>';
        }

    }

    function memory_format(value, record, index) {
        if (parseFloat(value.substring(0, value.length - 1)) > memory_threshold) {
            return '<span style="color:red;font-weight: bold">' + value + '</span>';
        } else {

            return '<span >' + value + '</span>';
        }

    }

    function disk_format(value, record, index) {
        if (parseFloat(value.substring(0, value.length - 1)) > disk_threshold) {
            return '<span style="color:red;font-weight: bold">' + value + '</span>';
        } else {

            return '<span >' + value + '</span>';
        }

    }

    function updatetime_format(value, record, index) {
        var readtime = strToDate($("#updatetime").html());
        var updatetime = strToDate(value);
        if (Math.abs(updatetime - readtime) > timegap) {
            return '<span style="color:red;font-weight: bold">' + value + '</span>';
        } else {

            return '<span >' + value + '</span>';
        }

    }

    function getNowFormatDate() {
        var date = new Date();
        var seperator1 = "-";
        var seperator2 = ":";
        var month = date.getMonth() + 1;
        var strDate = date.getDate();
        var hour = date.getHours();
        var minute = date.getMinutes();
        var second = date.getSeconds();

        if (month >= 1 && month <= 9) {
            month = "0" + month;
        }
        if (strDate >= 0 && strDate <= 9) {
            strDate = "0" + strDate;
        }
        if (hour >= 0 && hour <= 9) {
            hour = "0" + hour;
        }
        if (minute >= 0 && minute <= 9) {
            minute = "0" + minute;
        }
        if (second >= 0 && second <= 9) {
            second = "0" + second;
        }


        var currentdate = date.getFullYear() + month + strDate
            + seperator1 + hour + seperator2 + minute
            + seperator2 + second;
        return currentdate;
    }


    function strToDate(datestr) {
        //yyyymmdd-HH:MM:SS
        var myDate = new Date();
        myDate.setFullYear(datestr.substring(0, 4));
        myDate.setMonth((parseInt(datestr.substring(4, 6)) - 1).toString());
        myDate.setDate(datestr.substring(6, 8));
        myDate.setHours(datestr.substring(9, 11));
        myDate.setMinutes(datestr.substring(12, 14));
        myDate.setSeconds(datestr.substring(15, 17));
        return myDate;

    }

    function loadMonitor() {
        $.ajax({
            type: "GET",
            url: "JMonitorJSON",
            dataType: "json",
            cache: false,
            async: false,

            beforeSend: ajaxLoading(),
            success: function (json) {
                $("#table_java_monitor").datagrid("loadData", json);

                $("table.datagrid-btable div.datagrid-cell-c1-status").each(
                    function () {

                        if ($(this).html() == "Up") {
                            $(this).css(
                                {
                                    "color": "cyan"
                                });
                        } else if ($(this).html() == "Down") {
                            $(this).css(
                                {
                                    "color": "red",
                                    "font-weight": "bold"

                                });
                        }
                    }
                );


                ajaxLoadEnd();
            },
            complete: function () {
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {

                $("table.datagrid-btable div.datagrid-cell-c1-status").html("Down");
                $("table.datagrid-btable div.datagrid-cell-c1-status").css(
                    {
                        "color": "red",
                        "font-weight": "bold"

                    }
                );
                $(".datagrid-mask-msg").html("无法连接后台");
                alert("后台程序无响应，请登录服务器检查应用程序运行状况。");
            }

        });
    }

    function ajaxLoading() {
        $(".datagrid-mask").remove();
        $(".datagrid-mask-msg").remove();
        $("<div class=\"datagrid-mask\"></div>").css({
            position: "fixed",
            display: "block",
            width: "100%",
        }).appendTo("body");
        $("<div class=\"datagrid-mask-msg\"></div>").html("正在处理，请稍候。。。").appendTo("body").css({
            position: "fixed",
            display: "block",
            left: ($(document.body).outerWidth(true) - 190) / 2,
            top: ($(window).height() - 45) / 2
            // font-size:20px,
            //font-weight:bold
        });
    }

    function ajaxLoadEnd() {
        $(".datagrid-mask").remove();
        $(".datagrid-mask-msg").remove();
    }

</script>
</body>
</html>
