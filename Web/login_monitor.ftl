<!DOCTYPE  html>
<html xmlns="http://www.w3.org/1999/html">
<head>
    <meta charset="UTF-8">
    <META HTTP-EQUIV="pragma" CONTENT="no-cache">
    <META HTTP-EQUIV="Cache-Control" CONTENT="no-store, must-revalidate">
    <META HTTP-EQUIV="expires" CONTENT="0">
    <title>金纳算法可视化--登录界面</title>
    <link rel="stylesheet" type="text/css" href="easyui/themes/black/easyui.css">
    <link rel="stylesheet" type="text/css" href="easyui/themes/icon.css">
    <script type="text/javascript" src="easyui/jquery-1.10.2.min.js"></script>
    <script type="text/javascript" src="easyui/jquery.easyui.min.js"></script>
    <style type="text/css">
        body {
            background-color: #999;
        }

        td {
            padding: 5px;
        }

    </style>
</head>
<body>

<h2 style="text-align:center;margin-top: 100px;margin-bottom: 200px;">金纳算法可视化平台--登录界面</h2>
<div id="main_div " style="margin:0 auto;width:500px;border: 1px solid darkseagreen">
    <form id="authenticate" method="post" style="text-align: center;padding: 30px;" action="index.html">

        <table style="width: 100%">

            <tr>
                <td style="font-weight: bold;text-align: right;width:40%;">
                    <label>用户名:</label>
                </td>

                <td style="font-weight: bold;text-align: left">
                    <input name="username" class="easyui-validatebox" required="true"
                           style="width:150px;">
                </td>
            </tr>

            <tr>

                <td style="font-weight: bold;text-align: right">
                    <label style="font-weight: bold">密&emsp;码:</label>
                </td>
                <td style="font-weight: bold;text-align: left">
                    <input name="password" type="password" class="easyui-validatebox"
                           required="true" style="width:150px;">
                </td>

            </tr>

            <tr>
                <td style="font-weight: bold;text-align: center;" colspan="2">
                    <input type="submit" style="width:80px;font-weight: bold;margin: 5px;" value="提交"/>
                    <input type="reset" style="width:80px;font-weight: bold;margin: 5px;" value="重置"/>
                </td>

            </tr>

        </table>
        <input type="hidden" name="token" value="${token}">
    </form>

</div>

<script type="text/javascript">

    $(function () {
        if (window.history && window.history.pushState) {
            history.pushState(null, null, document.URL);
            window.addEventListener('popstate', forbidBack);
        }
    });

    /**
     * 禁止回退按钮
     */
    function forbidBack() {
        appUtils.mobileConfirm("确定放弃?", function () {//yes
            window.removeEventListener('popstate', forbidBack);
        }, function () {//no
            //防止页面后退
            history.pushState(null, null, document.URL);
        });
    }

</script>


</body>

</html>
