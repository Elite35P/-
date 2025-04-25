import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

# 设置 matplotlib 使用中文字体（以 Windows 常见的“微软雅黑”为例）
matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# === 1. 读取数据 ===
df_inventory = pd.read_excel("全国奶牛存栏量、平均单产、305奶量.xlsx")
df_production = pd.read_excel("全国牛奶产量.xlsx")
df_feed = pd.read_excel("全国饲料价格.xlsx")
df_pred = pd.read_excel("全国主产省生鲜乳价格.xlsx")

# === 2. 数据处理 ===
df_inventory.rename(columns={"年度": "年份"}, inplace=True)
df_production.rename(columns={"年度": "年份", "牛奶产量（万吨）": "牛奶产量"}, inplace=True)
df_feed.rename(columns={"年度": "年份"}, inplace=True)
df_pred.rename(columns={ "奶价（元/千克）":"奶价","年度": "年份"}, inplace=True)

df_feed_avg = df_feed.groupby("年份")[["玉米（元/公斤）", "豆粕（元/公斤）"]].mean().reset_index()

df_merge = pd.merge(df_inventory, df_production[["年份", "牛奶产量"]], on="年份", how="left")
df_all = pd.merge(df_merge, df_feed_avg, on="年份", how="left")
df_all = pd.merge(df_pred, df_all, how="left")
# === 3. 计算相关性矩阵 ===
cols_to_analyze = [
    "奶牛存栏量（万头）",
    "平均单产（千克）",
    "305奶量（千克）",
    "牛奶产量",
    "玉米（元/公斤）",
    "豆粕（元/公斤）",
    "奶价"
]
df_corr = df_all[cols_to_analyze]
corr_matrix = df_corr.corr(method="pearson")

# === 4. 绘制热力图 ===
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", square=True)
plt.title("奶牛养殖关键指标相关性热力图", fontsize=14)
plt.tight_layout()
plt.show()
