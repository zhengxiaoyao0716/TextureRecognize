# TextureRecognize
## 模式识别大作业
***

> 成品二进制包及文档请查看[gh-pages分支](https://github.com/zhengxiaoyao0716/TextureRecognize/tree/gh-pages)，点这里查看[文档及展示](https://zhengxiaoyao0716.github.io/TextureRecognize/)

***
展示作业1：

问题描述：将纹理背景中的目标检测/分类出来，一共13张图片，第一幅图片中不含有任何目标，仅含有背景，其余12幅图像中各含有一种目标，需要将图片中的目标和背景区分开。

附件中一共两个文件夹：原图、标注，每个文件夹中有13幅图像；
其中，1. ‘标注’文件夹显示了目标的真实类别，是类别真值文件夹，只是为了显示图像中有哪些目标需要被分类出来；
    2. ‘原图’文件夹包含大家需要处理的图像，需要把每幅图像中的目标都检测/分类出来，其中，第一幅图像仅是背景，不含有任何目标。

要求：
1. 至少将7种以上的目标和背景区分开，即至少成功完成7张图的2类目标分类问题；
2. 分析正确分类与错误分类的原因；
3. 展示时间5分钟以内；
4. 将最后展示报告传到公邮箱内，时间待通知。
5. 2-3人一组，自由组队。

附：
1. 对每类目标（即，每张图像）处理可以采用不同的方法；
2. 尽量依据多变量Baysian分类器，Fisher分类器；也可以考虑其他方法，方法不限。

***
### 一、环境与运行
第一步：安装Python3并配置好环境变量之类的，略

第二步：搭建运行环境
``` bash
# Windows
py -3 -m venv .env
# Linux
python3 -m venv .env
# Linux请将'Scripts'替换成'bin'，下同
.env\Scripts\pip install -r requirements.txt
```

第三步：运行
``` bash
# 运行主程
.env\Scripts\python main.py
```

### 二、编译与打包
第一步：安装开发环境依赖
``` bash
.env\Scripts\pip install -r requirements_dev.txt
```

第二步：打包
``` bash
.env\Scripts\pyinstaller TextureRecognize.spec

# Windows系统输出目录结构如下：
# - dist/
#   -- assets/...
#   -- TextureRecognize.exe
```
