如README中所说的，Bug修正主要参考中译本.

注：《Python灰帽子》一书的页码以实体书为准

|章节|class|修正方法|[Python灰帽子](http://ishare.iask.sina.com.cn/f/35756656.html)|
|:------|:---------|:---------|:--------:|
|C3.1|load|`CreateProcessA`函数的第二个参数连着有四个None(原书只有一个)|P27|
|C3.1|attach|删除or注释掉 `self.run()`|P31|
|C3.1|open_process|`OpenProcess`函数最后两个参数反了，改为`OpenProcess(PROCESS_ALL_ACCESS, False, pid)`|P31|
|C3.2|enumerate_threads|`kernel32.CloseHandle(snapshot)` `return thread_list` 两行要和上面的 `while success:` 对齐(即减少缩进)|P38
|C3.4.1|exception_handler_breakpoint|原版以及两本中译本代码不全，请参考作者给出的源代码，否则无法实现书中的输出效果(后续代码尽可能参作者的源码包)\*\* **注意**用原作的代码段替换自己的代码时，要记得将`__init__`中的全局变量加上|P49|
|C3.4.2|exception_handler_single_step|需要在`defines`里加上`DBG_EXCEPTION_NOT_HANDLED = 0x80010001`|P53|
