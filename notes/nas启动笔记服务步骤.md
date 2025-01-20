#### 1、打开nas的终端ssh连接开关
2、进入笔记本项目目录
```cd /volume1/web/axure_lulunav_8222/biji```
3、启用Python虚拟环境
```source .venv/bin/activate```
4、使用 `flask run` 命令启动应用程序，并指定 --host 和 --port 参数，使用 `nohup` 命令使得程序在后台常驻
```nohup flask run --host=0.0.0.0 --port=5007 & ```
或者(即寻找当前路径下的app.py程序来运行)
```nohup flask --app app run --host=0.0.0.0 --port=5007 & ```
5、如果要终止web后台程序，执行以下命令，第一行命令会返回flask的PID（开头的三位数）：
```ps aux | grep flask```
```kill <PID>```
