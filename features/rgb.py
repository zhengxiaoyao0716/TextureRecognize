#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
RGB特征
@author: zhengxiaoyao0716
"""

from functools import reduce

from .base import Feature


class RgbFarFeature(Feature):
    """（相对平均值）偏远度"""

    def __init__(self, width, height):
        super().__init__(width, height)
        self.sum = [0, 0, 0]

    def on_each_pix(self, rgb):
        """每个像素点回调"""
        red, green, blue = rgb
        self.sum[0] += red
        self.sum[1] += green
        self.sum[2] += blue

    def on_iter_end(self, pixs_len, pix_iter):
        """遍历结束后回调"""
        rgb_avg = tuple(sum / pixs_len for sum in self.sum)

        def distance(rgb):
            """计算欧式距离"""
            return (reduce(
                lambda l, r: l + (rgb[r] - rgb_avg[r])**2,
                range(3), 0
            ) / 3)**0.5
        pix_iter(lambda xy, rgb: self.point(xy, distance(rgb)))


class RgbRareFeature(Feature):
    """（相对众数）稀有度"""

    def __init__(self, width, height):
        super().__init__(width, height)
        self.counter = {}

    def on_each_pix(self, rgb):
        """每个像素点回调"""
        if rgb not in self.counter:
            self.counter[rgb] = 0
        self.counter[rgb] += 1

    def on_iter_end(self, pix_iter, ):
        """遍历结束后回调"""
        counter_list = [(self.counter[rgb], rgb) for rgb in self.counter]
        counter_list.sort(reverse=True)
        weight_map = {}
        size = len(self.counter)
        index = 0
        for _, rgb in counter_list:
            weight_map[rgb] = index / size
            index += 1
        pix_iter(lambda xy, rgb: self.point(
            xy, 255 * weight_map[rgb]))
