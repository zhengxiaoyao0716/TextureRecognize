#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TextureRecognize
@author: zhengxiaoyao0716
"""

from threading import Thread
from functools import reduce
from sys import stdout, argv
from os import makedirs
from os.path import exists
from shutil import rmtree

import colorama
from PIL import Image, ImageDraw

from features.base import Feature
from features.pos import PosFeatures
from features.rgb import RgbFarFeature, RgbRareFeature
from weight_table import WEIGHT_TABLE


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
    if len(argv) > 1:
        path = argv[1]
        print(path)
        image = Image.open(path)
    else:
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
    far_pos_features = PosFeatures(width, height, pixs, tole=3)
    rare_pos_features = PosFeatures(width, height, pixs, tole=3)

    features = (
        rgb_far_feature,
        rgb_rare_feature,
        far_pos_features.group_num,
        far_pos_features.block_ratio,
        rare_pos_features.group_num,
        rare_pos_features.block_ratio,
    )
    path_index = path[
        max(1 + path.rindex('/') if '/' in path else 0,
            1 + path.rindex('\\') if '\\' in path else 0):
        path.rindex('.bmp') if '.bmp' in path else None
    ]
    main.outdir = 'out/%s/' % path_index

    def cal_feature():
        """计算特征值"""
        main.outdir = 'out/%s/' % path_index
        if len(argv) > 2:
            if argv[2] != '--use-cache':
                main.outdir = argv[2]
                if not main.outdir.endswith('/') and not main.outdir.endswith('\\'):
                    main.outdir += '/'
            if exists(main.outdir):
                for i in range(6):
                    features[i].weight_image = Image.open(
                        main.outdir + '%02d.jpg' % (1 + i))
                return

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
        print('基于RgbFarFeature')
        pix_iter(lambda xy, grey:
                 far_pos_features.find_connect(xy) if grey > 127 else None,
                 rgb_far_feature.weight_image.load())
        print_progress('OK')
        print('基于rgb_rare_feature')
        pix_iter(lambda xy, grey:
                 rare_pos_features.find_connect(xy) if grey > 127 else None,
                 rgb_rare_feature.weight_image.load())
        print_progress('OK')

        rmtree(main.outdir, ignore_errors=True)
        makedirs(main.outdir)
        feature_count = 0
        for feature in features:
            feature_count += 1
            feature.weight_image.save(
                main.outdir + '%02d.jpg' % feature_count)
    cal_feature()

    def mark_tags(weights):
        """标注全部目标选框"""
        new_image = image.copy()
        drawer = ImageDraw.Draw(new_image)
        print('\n标注目标选框：')
        final_weight = lambda xy: reduce(
            lambda l, r: l + weights[r] * features[r].weight(xy),
            range(len(features)), 0
        )
        cap = weights[6] if len(weights) > 6 else 0.5
        is_tag = lambda xy: final_weight(xy) > cap
        visited = {}

        def mark_tag(xy):
            """标注目标选框"""
            x0, y0, x1, y1 = xy[0], xy[1], xy[0], xy[1]
            count = 0
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
                for x in range(max(0, xy[0] - 10), min(width, xy[0] + 10)):
                    for y in range(max(0, xy[1] - 10), min(height, xy[1] + 10)):
                        if (x, y) not in visited and is_tag((x, y)):
                            count += 1
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
            # 去噪点
            if (x0 - x1) * (y0 - y1) < 1600 or count < 120:
                return
            # print(x0, y0, x1, y1)
            for ex in range(3):
                drawer.rectangle(
                    (x0 + ex, y0 + ex, x1 - ex, y1 - ex), outline='#f00')

        final_feature = Feature(width, height)

        def each_pix(xy, rgb):
            """每个像素点处理"""
            weight = final_weight(xy)
            if weight > cap and xy not in visited:
                final_feature.point(xy, 255)
                mark_tag(xy)
            else:
                final_feature.point(xy, 255 * weight)
            # if is_tag(xy) and xy not in visited:
            #     mark_tag(xy)
        pix_iter(each_pix)
        print_progress('OK')
        # Thread(target=new_image.show, name=path).start()
        new_image.save(main.outdir + 'result-marked.jpg')
        # final_feature.show()
        final_feature.weight_image.save(main.outdir + 'result-weight.jpg')

    default_weights = WEIGHT_TABLE.get(
        path_index) or (0.1, 0.1, 0.2, 0.2, 0.2, 0.2)
    weights_list = argv[3:]
    weights_list.reverse()
    while len(weights_list):
        weights_str = weights_list.pop()
        if weights_str == '--finish':
            return
        mark_tags(tuple(float(w) for w in weights_str.split(','))
                  if weights_str != '--default-weights' else default_weights)
    while True:
        line = input('\n请输入系数组（默认为%r）\n' % (default_weights,))
        if line == '':
            weights = default_weights
        else:
            try:
                weights = tuple(float(w.strip()) for w in line.split(','))
            except IOError:
                print('无效的输入')
        if len(weights) >= 6:
            print('当前系数组：%r' % (weights,))
            mark_tags(weights)
        else:
            print('系数组长度至少为6')


if __name__ == '__main__':
    main()
