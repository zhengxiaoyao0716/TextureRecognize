#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
位置特征
@author: zhengxiaoyao0716
"""

from functools import reduce

from .base import Feature


class PosFeatures(object):
    """相对位置相关的特征集合"""

    def __init__(self, width, height, pixs, tole=30, capa=1000):
        self.pixs = pixs
        self.tole = tole
        self.capa = capa
        self.in_range = lambda xy: xy[0] >= 0 and xy[1] >= 0 \
            and xy[0] < width and xy[1] < height
        # 连通组内的像素点数量的特征
        self.group_num_feature = Feature(width, height)
        # 边界点数量与组内数量比例特征
        self.block_ratio_feature = Feature(width, height)
        if isinstance(self.pixs[0, 0], int):
            # 灰度
            self.distance = lambda level, compare: abs(level - compare)
        else:
            # RGB
            # reduce(
            #     lambda l, r: l + abs(rgb[r] - compare[xy][r]),
            #     range(3), 0
            # )
            self.distance = lambda rgb, compare: (reduce(
                lambda l, r: l + (rgb[r] - compare[r])**2,
                range(3), 0
            ) / 3)**0.5

    def find_connect(self, xy):
        """查找连通集"""
        if self.group_num_feature.weight(xy) > 0.5 or self.block_ratio_feature.weight(xy) > 0.5:
            return
        rgb = self.pixs[xy]
        stack = [xy]
        visited = {}
        connect_pixs = []
        # distance_sum = 0
        block_pixs = []
        # xs = []
        # ys = []
        while len(stack):
            xy = stack.pop()
            d = self.distance(rgb, self.pixs[xy])
            if d > self.tole:
                block_pixs.append(xy)
                # 超过容差，跳过
                continue
            # rgb = tuple(
            #     map(lambda i: (rgb[i] + self.pixs[xy][i]) / 2, range(3)))
            connect_pixs.append(xy)
            # distance_sum += d
            # xs.append(xy[0])
            # ys.append(xy[1])
            if len(stack) > self.capa:
                # 超过容量，结束
                break
            for xy in [
                    (xy[0] + 1, xy[1]), (xy[0] - 1, xy[1]),
                    (xy[0], xy[1] + 1), (xy[0], xy[1] - 1)
            ]:
                if xy not in visited and self.in_range(xy):
                    visited[xy] = True
                    stack.append(xy)
        # print(len(connect_pixs))
        # # print(distance_sum / len(connect_pixs))
        # print(len(block_pixs))
        group_num = len(connect_pixs)
        # 简单统计，数量60~300之间是目标的概率很大，简单的模拟高斯分布
        group_num_weight = (
            0 if group_num < 30 else
            (group_num / 30 - 1) ** 3 if group_num < 60 else
            1 if group_num < 300 else
            (group_num / 300 - 1) ** 3 if group_num < 600 else
            0
        )
        if group_num_weight > 0:
            point_group_num = lambda xy: \
                self.group_num_feature.point(
                    xy, max(255 * group_num_weight, self.group_num_feature.weight(xy)))
        else:
            point_group_num = lambda xy: None
        block_ratio = len(block_pixs) / group_num
        # 简单统计，比例0.5~1左右是目标，比例0.1基本上不是
        block_ratio_weight = (
            1 if block_ratio > 0.5 else
            (block_ratio / 0.5) ** 3
        )
        if group_num_weight > 0:
            point_block_ratio = lambda xy: \
                self.block_ratio_feature.point(
                    xy, max(255 * block_ratio_weight, self.block_ratio_feature.weight(xy)))
        else:
            point_block_ratio = lambda xy: None
        # 对连通的点进行标记
        for xy in connect_pixs:
            point_group_num(xy)
            point_block_ratio(xy)
        # import numpy as np
        # r = np.polyfit(xs, ys, 1)
        # line = np.poly1d(r)
        # print(r)
        # print(line)

    @property
    def group_num(self):
        """连通组内的像素点数量的特征"""
        return self.group_num_feature

    @property
    def block_ratio(self):
        """边界点数量与组内数量比例特征"""
        return self.block_ratio_feature

    def show(self):
        """绘制权重等高图"""
        self.group_num_feature.show()
        self.block_ratio_feature.show()
