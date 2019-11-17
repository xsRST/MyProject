<!DOCTYPE  html>
<html xmlns="http://www.w3.org/1999/html">
<head>
    <meta charset="UTF-8">
    <META HTTP-EQUIV="pragma" CONTENT="no-cache">
    <META HTTP-EQUIV="Cache-Control" CONTENT="no-store, must-revalidate">
    <META HTTP-EQUIV="expires" CONTENT="0">
    <title>金纳算法--盘后分析</title>
    <link rel="stylesheet" type="text/css" href="easyui/themes/default/easyui.css">
    <link rel="stylesheet" type="text/css" href="easyui/themes/icon.css">
    <script type="text/javascript" src="easyui/jquery-1.10.2.min.js"></script>
    <script type="text/javascript" src="easyui/jquery.easyui.min.js"></script>
    <style type="text/css">
        body {
            background-color: azure;
        }

        table th {
            text-align: center;

        }

        table td {
            text-align: right;
        }

        td:first-child {
            text-align: center;
        }

        table.datagrid-btable tr:last-child {
            font-weight: bold;
        }

    </style>

</head>
<body>


<div style="margin:0 auto;width:1010px">
    <h2 style="text-align:center">金纳算法盘后分析(${updatetime})</h2>
    <table style="width: 100%">
        <tr>
            <td style="text-align: left">
                <input name="period" type="radio" value="year"/><label>本年</label>
                <input name="period" type="radio" value="quarter"/><label>本季度</label>
                <input name="period" type="radio" value="month"/><label>本月</label>
                <input name="period" type="radio" value="today"/><label>当日</label>
            </td>
            <td style="text-align: right">

                <span id="begin_time"></span>
                <span>--</span>
                <span id="end_time"></span>
            </td>

        </tr>


    </table>


    <div style="margin:20px 0;"></div>


    <table id="table_performance_strategy_summary" class="easyui-datagrid" title="算法性能分析--按策略" style="width:1010px;"
           collapsible="true" singleSelect="true">
        <thead>
        <tr>
            <th data-options="field:'策略名称',width:'125px',headAlign:'center',">策略名称</th>
            <th data-options="field:'母单个数',width:'125px',headAlign:'center',">母单个数</th>
            <th data-options="field:'成交股数',width:'125px',headAlign:'center',">成交股数</th>
            <th data-options="field:'成交金额',width:'125px',headAlign:'center',">成交金额</th>
            <th data-options="field:'相对表现到达价格',width:'125px',headAlign:'center',">相对表现<br/>(到达价格)</th>
            <th data-options="field:'标准方差到达价格',width:'125px',headAlign:'center',">标准方差<br/>(到达价格)</th>
            <th data-options="field:'相对表现VWAP',width:'125px',headAlign:'center',">相对表现<br/>(VWAP)</th>
            <th data-options="field:'标准方差VWAP',width:'125px',headAlign:'center',">标准方差<br/>(VWAP))</th>
        </tr>
        </thead>
    </table>
    <div style="margin:20px 0;"></div>

    <table id="table_performance_side_summary" class="easyui-datagrid" title="算法性能分析--按买卖方向" style="width:1010px;"
           collapsible="true" singleSelect="true">
        <thead>
        <tr>
            <th data-options="field:'买卖方向',width:'125px',headAlign:'center',">买卖方向</th>
            <th data-options="field:'母单个数',width:'125px',headAlign:'center',">母单个数</th>
            <th data-options="field:'成交股数',width:'125px',headAlign:'center',">成交股数</th>
            <th data-options="field:'成交金额',width:'125px',headAlign:'center',">成交金额</th>
            <th data-options="field:'相对表现到达价格',width:'125px',headAlign:'center',">相对表现<br/>(到达价格)</th>
            <th data-options="field:'标准方差到达价格',width:'125px',headAlign:'center',">标准方差<br/>(到达价格)</th>
            <th data-options="field:'相对表现VWAP',width:'125px',headAlign:'center',">相对表现<br/>(VWAP)</th>
            <th data-options="field:'标准方差VWAP',width:'125px',headAlign:'center',">标准方差<br/>(VWAP)</th>
        </tr>
        </thead>
    </table>
    <div style="margin:20px 0;"></div>

    <table id="table_performance_exchange_summary" class="easyui-datagrid" title="算法性能分析--按交易所" style="width:1010px;"
           collapsible="true" singleSelect="true">
        <thead>
        <tr>
            <th data-options="field:'交易所',width:'125px',headAlign:'center',">交易所</th>
            <th data-options="field:'母单个数',width:'125px',headAlign:'center',">母单个数</th>
            <th data-options="field:'成交股数',width:'125px',headAlign:'center',">成交股数</th>
            <th data-options="field:'成交金额',width:'125px',headAlign:'center',">成交金额</th>
            <th data-options="field:'相对表现到达价格',width:'125px',headAlign:'center',">相对表现<br/>(到达价格)</th>
            <th data-options="field:'标准方差到达价格',width:'125px',headAlign:'center',">标准方差<br/>(到达价格)</th>
            <th data-options="field:'相对表现VWAP',width:'125px',headAlign:'center',">相对表现<br/>(VWAP)</th>
            <th data-options="field:'标准方差VWAP',width:'125px',headAlign:'center',">标准方差<br/>(VWAP)</th>
        </tr>
        </thead>
    </table>
    <div style="margin:20px 0;"></div>

    <table id="table_performance_trader_summary" class="easyui-datagrid" title="算法性能分析--按交易员" style="width:1010px;"
           collapsible="true" singleSelect="true">
        <thead>
        <tr>
            <th data-options="field:'交易员',width:'125px',headAlign:'center',">交易员</th>
            <th data-options="field:'母单个数',width:'125px',headAlign:'center',">母单个数</th>
            <th data-options="field:'成交股数',width:'125px',headAlign:'center',">成交股数</th>
            <th data-options="field:'成交金额',width:'125px',headAlign:'center',">成交金额</th>
            <th data-options="field:'相对表现到达价格',width:'125px',headAlign:'center',">相对表现<br/>(到达价格)</th>
            <th data-options="field:'标准方差到达价格',width:'125px',headAlign:'center',">标准方差<br/>(到达价格)</th>
            <th data-options="field:'相对表现VWAP',width:'125px',headAlign:'center',">相对表现<br/>(VWAP)</th>
            <th data-options="field:'标准方差VWAP',width:'125px',headAlign:'center',">标准方差<br/>(VWAP)</th>
        </tr>
        </thead>
    </table>

    <div style="margin:20px 0;"></div>

    <table id="table_performance_symbol_summary" title="算法性能分析--按个股" style="width:1010px;" collapsible="true"
           singleSelect="true"
    >
        <thead>
        <tr>
            <th data-options="field:'证券代码',width:'120px',headAlign:'center',">证券代码</th>
            <th data-options="field:'母单个数',width:'120px',headAlign:'center',">母单个数</th>
            <th data-options="field:'成交股数',width:'120px',headAlign:'center',">成交股数</th>
            <th data-options="field:'成交金额',width:'120px',headAlign:'center',">成交金额</th>
            <th data-options="field:'相对表现到达价格',width:'120px',headAlign:'center',">相对表现<br/>(到达价格)</th>
            <th data-options="field:'标准方差到达价格',width:'120px',headAlign:'center',">标准方差<br/>(到达价格)</th>
            <th data-options="field:'相对表现VWAP',width:'120px',headAlign:'center',">相对表现<br/>(VWAP)</th>
            <th data-options="field:'标准方差VWAP',width:'120px',headAlign:'center',">标准方差<br/>(VWAP)</th>
        </tr>
        </thead>
    </table>


</div>
<div style="clear:both ;height:125px;"></div>
<script type="text/javascript">
    period = "${period}";
    data_year =${year};
    data_quarter =${quarter};
    data_month =${month};
    data_today =${today};

    period_year =${period_year};
    period_quarter =${period_quarter};
    period_month =${period_month};
    period_today =${period_today};

    period_detail = [];
    begin_time = "";
    end_time = "";
    data_choose = [];

    $(function () {
        $("body").hide();
        $("input:radio[name='period'][value=" + period + "]").prop("checked", true);
        choose_period(period);
        $("body").show();
        choose_data(period);
    });

    $("input:radio[name='period']").change(function () {
        var period_selected = $("input:radio[name='period']:checked").val();
        choose_period(period_selected);
        choose_data(period_selected);
    });

    function choose_period(period_selected) {
        switch (period_selected) {
            case "year":
                begin_time = period_year[0];
                end_time = period_year[1];
                break;
            case "quarter":
                begin_time = period_quarter[0];
                end_time = period_quarter[1];
                break;

            case "month":
                begin_time = period_month[0];
                end_time = period_month[1];
                break;
            case "today":
                begin_time = period_today[0];
                end_time = period_today[1];
                break;
            default:
                break;
        }
        $("#begin_time").html(begin_time);
        $("#end_time").html(end_time);
    }

    function choose_data(period) {

        switch (period) {
            case "year":
                data_choose = data_year;
                break;
            case "quarter":
                data_choose = data_quarter;
                break;

            case "month":
                data_choose = data_month;
                break;
            case "today":
                data_choose = data_today;
                break;
            default:
                break;
        }
        update();

    }

    function update() {
        $('#table_performance_strategy_summary').datagrid({

            data: data_choose["table_performance_strategy_summary"]
        });
        $('#table_performance_side_summary').datagrid({
            data: data_choose["table_performance_side_summary"]
        });
        $('#table_performance_exchange_summary').datagrid({
            data: data_choose["table_performance_exchange_summary"]
        });
        $('#table_performance_trader_summary').datagrid({
            data: data_choose["table_performance_trader_summary"]
        });

        var symbol_data = [];
        symbol_data = data_choose["table_performance_symbol_summary"];
        $("#table_performance_symbol_summary").datagrid({
            data: symbol_data.slice(0, 50),
            multiSort: true,
            rownumbers: true,
            pagination: true,
            pageList: [50, 100, 500, 9999999],
            pageSize: 50
        });

        var pager = $("#table_performance_symbol_summary").datagrid("getPager");

        pager.pagination({
            total: symbol_data.length,
            onSelectPage: function (pageNo, pageSize) {
                var start = (pageNo - 1) * pageSize;
                var end = start + pageSize;

                $("#table_performance_symbol_summary").datagrid("loadData", symbol_data.slice(start, end));
                pager.pagination('refresh', {
                    total: symbol_data.length,
                    pageNumber: pageNo
                });
            }
        });
    }


</script>
</body>
</html>
