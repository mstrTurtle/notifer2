# notifer2

## 这是什么

https://github.com/mstrTurtle/notifer

这个东西的优化版。可以部署在服务器上实现定时发邮件（或者发通知）的功能。

由于没精力实现得太好，使用者需要手动改代码。

## 结构

用shelve定义了持久层。

用asyncio定义了一个核心的模块，是常驻运行的。其中用asyncio.Future实现优雅Cancel。利用协程实现计算任务的可组合性。

用FastAPI构建了一组Restful风格的API。

## 待完成的任务

接下来需要把FastAPI的协程服务器的协程Loop和自己这个模块的协程Loop融合一下。
