#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Base Feature.
@author: zhengxiaoyao0716
"""

from threading import Thread
from PIL import Image, ImageDraw


class Feature(object):
    """基础特征模型"""

    def __init__(self, width, height):
        self.weight_image = Image.new('L', (width, height))
        self.weight_drawer = ImageDraw.Draw(self.weight_image)

    def point(self, xy, weight):
        """绘制权重点"""
        self.weight_drawer.point(xy, fill=int(weight))

    def show(self):
        """绘制权重等高图"""
        Thread(target=self.weight_image.show, name=str(self)).start()

    def weight(self, xy):
        """获取某点上的权重"""
        try:
            weight = self.weight_image.getpixel(xy)
        except IndexError:
            return 0
        return weight / 255
