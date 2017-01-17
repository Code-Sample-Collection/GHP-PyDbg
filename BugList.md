如README中所说的，Bug修正主要参考以下两种中译本，表格中的页码分别对应两个版本的相应页数.   
若未明确标注，则所有错误均为《Python灰帽子》中的，《灰帽Python之旅》一般为正确的代码

|章节|class|修正方法|[Python灰帽子](http://ishare.iask.sina.com.cn/f/35756656.html)|[灰帽Python之旅](http://ishare.iask.sina.com.cn/f/36096027.html)|
|:------|:---------|:---------|:--------:|:--------:|
|C3.1|load|CreateProcessA函数的第二个参数连着有四个None(原书只有一个)|P41|P27|
|C3.1|attach|删除or注释掉 `self.run()`|P45|*P29|
|C3.2|enumerate_threads|`kernel32.CloseHandle(snapshot)
return thread_list` 两行要和上面的 `while success:` 对齐(即减少缩进)|P52|P34|
