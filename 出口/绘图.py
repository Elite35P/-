#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def configure_fonts():
    """
    配置中文字体 & 负号正常显示。
    根据系统实际可用字体，修改 font_name。
    """
    font_name = 'Microsoft YaHei'  # Windows 系统常见中文字体；Linux 下可用 'WenQuanYi Zen Hei'
    plt.rcParams['font.sans-serif'] = [font_name]
    plt.rcParams['axes.unicode_minus'] = False

def load_and_prepare(csv_path, desired_cats):
    """
    读取 CSV、筛选品类、合并重复、计算占比，返回可用品类及透视表
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"找不到文件：{csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    df['月份'] = pd.to_datetime(df['月份'], format='%Y-%m')

    actual = set(df['品类'].unique())
    available = [c for c in desired_cats if c in actual]
    missing   = [c for c in desired_cats if c not in actual]

    print("可用品类：", available)
    if missing:
        print("缺失品类，请检查：", missing)
    if not available:
        raise ValueError("没有可用品类，退出。")

    df = df[df['品类'].isin(available)]
    df = df.groupby(['月份','品类'], as_index=False).agg({'进口量(万吨)': 'sum'})
    total = df.groupby('月份')['进口量(万吨)'].sum().rename('当月总量')
    df = df.merge(total, on='月份')
    df['占比(%)'] = df['进口量(万吨)'] / df['当月总量'] * 100

    vol_pivot = df.pivot(index='月份', columns='品类', values='进口量(万吨)')
    pct_pivot = df.pivot(index='月份', columns='品类', values='占比(%)')
    return available, vol_pivot, pct_pivot

def plot_small_multiples(available, vol_pivot):
    """
    小多图模式：每个品类单独折线图，并在 x 轴显示每月标签
    """
    n = len(available)
    ncols = 2
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 4 * nrows), sharey=True)
    axes = axes.flatten()

    # 设置每月格式化：每隔 1 个月显示一次
    locator = mdates.MonthLocator(interval=1)
    formatter = mdates.DateFormatter('%Y-%m')

    for ax, cat in zip(axes, available):
        ax.plot(vol_pivot.index, vol_pivot[cat], marker='o', linewidth=2)
        ax.set_title(cat)
        ax.grid(True, linestyle='--', linewidth=0.5)
        # 格式化 x 轴
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')

    # 隐藏多余的子图
    for ax in axes[n:]:
        ax.axis('off')

    fig.suptitle('各品类进口量月度趋势（万吨）', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def plot_stacked_bar(available, pct_pivot):
    """
    堆叠柱状图：按月展示各品类占比
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = [0] * len(pct_pivot)
    labels = pct_pivot.index.strftime('%Y-%m')
    for cat in available:
        vals = pct_pivot[cat].values
        ax.bar(labels, vals, bottom=bottom, label=cat)
        bottom = (bottom + vals).tolist()

    ax.set_xlabel('月份')
    ax.set_ylabel('占比 (%)')
    ax.set_title('各品类月度进口占比（%）')
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def main():
    configure_fonts()
    csv_file = '品类进口明细汇总.csv'
    desired_cats = [
        '乳清类','包装牛奶','大包粉','奶油类','奶酪类',
        '婴配粉','炼乳','稀奶油','蛋白类','酸奶类'
    ]

    available, vol_pivot, pct_pivot = load_and_prepare(csv_file, desired_cats)
    plot_small_multiples(available, vol_pivot)
    plot_stacked_bar(available, pct_pivot)

if __name__ == '__main__':
    main()
