# notifer2

## 这是什么

之前用asyncio实现了邮件收发逻辑（[this](https://github.com/mstrTurtle/notifer)），但水平不够显得很蹩脚。现在重新写。

可以部署在服务器上实现定时发邮件（或者发通知）的功能，因为用协程实现所以会更加轻量级。

这次用了一些组合的语义来让代码更加succinct。可以作为asyncio的使用示例。毕竟asyncio坑点有点多。

## 结构

用shelve定义了持久层。

用asyncio定义了一个核心的模块，是常驻运行的。其中用asyncio.Future实现优雅Cancel。利用协程实现计算任务的可组合性。

用FastAPI构建了一组Restful风格的API。

## 待完成的任务

接下来需要把FastAPI的协程服务器的协程Loop和自己这个模块的协程Loop融合一下。让两个线程能够完美退出。
