# TextureRecognize
## 模式识别大作业

***
### 理论设计

本次大作页里，我从每个像素的RGB、该像素点相对周边像素的关系两方面，选择了几个基础的特征，分别计算该特征方面某个像素点的“权重”。在此基础上，通过组合这些权重构造出一个，描述某个像素点属于目标的概率的表达式。通过调整这个表达式中各特征占比，找到最佳的检测出对象目标的系数组。

其实这是参考了机器学习的神经网络概念，理论上说，如果有足够的样本点给我拿来训练，有足够的时间给我将这些基本特征进行各种随机的组合，就可以将系数调整到最佳，得到非常高的准确率。但这里只是参考了这个概念，因为没有训练样本，并没有实现这个神经网络，特征的组合和各特征参与计算的系数是我自己随便调的。

具体来说，颜色方面，对于每个像素点，我提取了`RgbFar`与`RgbRare`两个特征，另一方面，根据每个像素点与周围像素点的关系，我提取了`GroupNum`与`BlockRare`两个特征，下面将详细解释：
1. RgbFar:

    与某个像素的RGB点到整张图平均RGB的欧式距离正比，当最终系数组里这个特征的系数增大时，与背景纹理的色彩差距最大像素将更可能被选择。

2. RgbRare:

    与某个像素的RGB在整张图上出现的频数成反比，这个特征系数的提高将会使得整张图里最少出现的像素被更多的选择。

3. GroupNum:

    对于某个点，这个特征取决于，与其色值相近的、连通的像素点的数量。这个特征系数与最终被选择的目标的大小关系紧密。

4. BlockRare:

    当某个点与周边的点连成一片后，将会有一些“边境点”，而这个特征描述了这些边境点与组内的点的比例。该特征的系数与目标的形状有关系。

以上4个基本的特征，分别从一个方面描述了一个点属于目标的概率。这4个特征里，1、2特征与3、4特征应该算是正交的吧，但1与2、3与4之间有一定的交叉，不过也是可以构成一个特征的投影平面的。另外，为了节省运算，实际代码里3、4特征的计算是基于1、2基础上的，也就是说实际运行时的系数组长度为6，分别是1、2特征、3-1、3-2、4-1、4-2特征组（这可能就是为什么对于有些图片检测效果非常差的原因，3、4特征一定程度上被1、2限制了）。其实之后还应该有更多交叉互组，形成多层神经元，但同样没时间做了。

以上四个特征里其实还嵌套了许多系数因子，比如，GroupNum的数量与像素点是目标的概率之间就不是简单的线性关系，硬要说的话，根据我简单统计，应该类似高斯分布，num分布在60~300之间时是目标的概率较大。显然，这里的期望值与标准差应该也可以通过样本训练来自动调优的。类似的，BlockRare里，边境点的比例也不是越高或越低就越好，较高时目标形状类似树形，较低时则偏向于一个圆形，而我们要的，面积大概50~300像素的长方形对应是多少呢？我同样是简单统计了一下填了个0.5~1。其它类似的地方，如果仔细调整的话，准确率会得到很大的提升。

说实话这是个半成品，最后完成的结果说实话不尽人意，识别率有点糟糕。主要问题还是特征之间的组合太少，也没有足够的时间慢慢调整系数，而且另一方面，现在各个特征之间其实只简单组合了一层，没有多层神经元之间的繁杂组合，最终判别也是一个简单的一次方程组，实际上各特征与目标的关系也有可能是次方甚至指数关系等，这些都没有纳入考虑，所以效果很差。综上，我觉得我的这个设计本身还是不错的，如果能有足够的训练样本和时间的话。。。


### 成果展示

各中间特征等高图详见`out`目录

01
![01](./out/01/result-weight.jpg)
![01](./out/01/result-marked.jpg)

02
![02](./out/02/result-weight.jpg)
![02](./out/02/result-marked.jpg)

03
![03](./out/03/result-weight.jpg)
![03](./out/03/result-marked.jpg)

04
![04](./out/04/result-weight.jpg)
![04](./out/04/result-marked.jpg)

05
![05](./out/05/result-weight.jpg)
![05](./out/05/result-marked.jpg)

06
![06](./out/06/result-weight.jpg)
![06](./out/06/result-marked.jpg)

07
![07](./out/07/result-weight.jpg)
![07](./out/07/result-marked.jpg)

08
![08](./out/08/result-weight.jpg)
![08](./out/08/result-marked.jpg)

09
![09](./out/09/result-weight.jpg)
![09](./out/09/result-marked.jpg)

10
![10](./out/10/result-weight.jpg)
![10](./out/10/result-marked.jpg)

11
![11](./out/11/result-weight.jpg)
![11](./out/11/result-marked.jpg)

12
![12](./out/12/result-weight.jpg)
![12](./out/12/result-marked.jpg)

13
![13](./out/13/result-weight.jpg)
![13](./out/13/result-marked.jpg)


### 结论及验证

`RgbFar`与`RgbRare`特征的表述能力对比：

03.bmp中，可以看到`RgbFar`对于上方的那个目标不太敏感，但对于右下方目标十分敏感。相反，`RgbRare`对于上方目标很敏感，对于下方那个完全不行。
![RgbFar](./out/03/01.jpg)
![RgbRare](./out/03/02.jpg)

在06.bmp中，`RgbRare`的有效度近乎为0：
![RgbFar](./out/06/01.jpg)
![RgbRare](./out/06/02.jpg)

反之，在09.bmp中，`RgbFar`的有效度近乎为0：
![RgbFar](./out/09/01.jpg)
![RgbRare](./out/09/02.jpg)

以上，经过这些对比可以得出，`RgbFar`与`RgbRare`经过一定比例的叠加，可以更为有效的描述目标

`GroupNum`与`BlockRare`特征的表述能力对比：

综合所有图片提取的特征的分析，可以发现，`GroupNum`得到的权重等高图普遍更为“干净”，但经常性的出现目标的部分乃至整体缺失。
`BlockRare`得到的图噪点较多，但相对来说出现遗漏的情况也更少。这表明，`GroupNum`与`BlockRare`特征的比例调和，可以得到一个最佳的目标检测的中间值。

下面以分类效果较好的`04.bmp`为例，展示具体效果：

推导过程
![推导过程](./screenshuts/推导过程.png)

权重等高图：
![权重等高图：](./out/04/result-weight.jpg)

检测目标标示：
![检测目标标示](./out/04/result-marked.jpg)
