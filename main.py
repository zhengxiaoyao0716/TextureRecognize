#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TextureRecognize - GUI
@author: zhengxiaoyao0716
"""

from functools import reduce
from sys import stdout

import colorama
from PIL import Image, ImageDraw

from features.pos import PosFeatures
from features.rgb import RgbFarFeature, RgbRareFeature


colorama.init()


def print_progress(percent):
    """打印进度条"""
    percent = int(100 * percent) if isinstance(percent, float) else percent
    if percent == 'OK':
        print(' : %s=> OK! |' % ''.join('=' for _ in range(100)))
    else:
        stdout.write(' : %s=> %s%02d%% |\r' % (
            ''.join('=' for _ in range(percent)),
            ''.join(' ' for _ in range(percent, 100)),
            percent
        ))


def is_ok():
    """确认是否可以"""
    line = input('这样可以吗？')
    return not ('否' in line or '不' in line or 'N' in line or 'n' in line)


def main():
    """Entrypoint"""
    # 载入资源
    default_path = './assets/03.bmp'
    while True:
        path = input('请输入图片路径：(%s)\n' % default_path) or default_path
        try:
            image = Image.open(path)
        except IOError:
            print('读取图片失败，请检查图片路径')
        else:
            break
    # 提取特征
    width, height = image.size
    pixs = image.load()

    def pix_iter(each_pix, pixs=pixs):
        """像素遍历器"""
        for x in range(width):
            print_progress(x / width)
            for y in range(height):
                each_pix((x, y), pixs[x, y])

    rgb_far_feature = RgbFarFeature(width, height)
    rgb_rare_feature = RgbRareFeature(width, height)

    def each_pix(xy, rgb):
        """每个像素回调"""
        rgb_far_feature.on_each_pix(rgb)
        rgb_rare_feature.on_each_pix(rgb)
    print('\n扫描图片：')
    pix_iter(each_pix)
    print_progress('OK')

    print('\n提取颜色特征：')
    print('RgbFarFeature')
    rgb_far_feature.on_iter_end(width * height, pix_iter)
    print_progress('OK')
    print('RgbRareFeature')
    rgb_rare_feature.on_iter_end(pix_iter)
    print_progress('OK')

    print('\n提取位置特征：')
    far_pos_features = PosFeatures(width, height, pixs, tole=3)
    rare_pos_features = PosFeatures(width, height, pixs, tole=3)
    print('基于RgbFarFeature')
    pix_iter(lambda xy, grey:
             far_pos_features.find_connect(xy) if grey > 127 else None,
             rgb_far_feature.weight_image.load())
    print_progress('OK')
    far_pos_features.show()
    print('基于rgb_rare_feature')
    pix_iter(lambda xy, grey:
             rare_pos_features.find_connect(xy) if grey > 127 else None,
             rgb_rare_feature.weight_image.load())
    print_progress('OK')
    rare_pos_features.show()

    def mark_tags(weights):
        """标注全部目标选框"""
        drawer = ImageDraw.Draw(image)
        print('\n标注目标选框：')
        features = [
            rgb_far_feature,
            rgb_rare_feature,
            far_pos_features.group_num,
            far_pos_features.block_ratio,
            rare_pos_features.group_num,
            rare_pos_features.block_ratio,
        ]
        is_tag = lambda xy: reduce(
            lambda l, r: l + weights[r] * features[r].weight(xy),
            range(len(features)), 0
        ) > 0.5
        visited = {}

        def mark_tag(xy):
            """标注目标选框"""
            x0, y0, x1, y1 = xy[0], xy[1], xy[0], xy[1]
            stack = [xy]
            while len(stack):
                xy = stack.pop()
                visited[xy] = True
                if xy[0] < x0:
                    x0 = xy[0]
                elif xy[0] > x1:
                    x1 = xy[0]
                if xy[1] < y0:
                    y0 = xy[1]
                elif xy[1] > y1:
                    y1 = xy[1]
                # 向附近延展
                for x in range(max(0, xy[0] - 30), min(width, xy[0] + 30)):
                    for y in range(max(0, xy[1] - 30), min(height, xy[1] + 30)):
                        if (x, y) not in visited and is_tag((x, y)):
                            visited[(x, y)] = True
                            stack.append((x, y))
                        visited[(x, y)] = True

            x0, y0, x1, y1 = (
                max(0, x0 - 10),
                max(0, y0 - 10),
                min(width, x1 + 10),
                min(height, y1 + 10),
            )
            for x in range(x0, x1):
                for y in range(y0, y1):
                    visited[(x, y)] = True
            # print(x0, y0, x1, y1)
            for ex in range(3):
                drawer.rectangle(
                    (x0 + ex, y0 + ex, x1 - ex, y1 - ex), outline='#f00')

        pix_iter(lambda xy, rgb: mark_tag(xy) if
                 is_tag(xy) and xy not in visited else None)
        print_progress('OK')
    mark_tags(weights=[0.1, 0.1, 0.4, 0.4, 0, 0])
    image.show()

if __name__ == '__main__':
    main()
