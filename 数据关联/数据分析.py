import pandas as pd
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
from statsmodels.tsa.api import VAR
from statsmodels.tools.sm_exceptions import InfeasibleTestError
from sklearn.preprocessing import StandardScaler
import dowhy
from dowhy import CausalModel

# —— 0. 中文字体设置（可选，但推荐） ——
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# —— 0.1 变量名映射 ——
var_zh = {
    'MilkPrice': '奶价',
    'DairyImport': '乳制品进口量',
    'CornPrice': '玉米价格',
    'PerCapitaConsumption': '人均消费量',
    'FeedImport': '饲料进口量',
    'DairyExport': '乳制品出口量',
    'ImportDetailVolume': '品类进口总量',
    'TradeImportValueUSD': '进口金额(USD)',
    'TradeImportQtyT': '进口数量(吨)',
    'TradeExportValueUSD': '出口金额(USD)',
    'TradeExportQtyT': '出口数量(吨)',
    'WhiteMilkSales': '常温白奶销量',
    'WhiteMilkGrowth': '常温白奶增长率(%)',
    'CowCount': '奶牛存栏量',
    'YieldPerCow': '单头产奶量',
    'MilkOutput': '牛奶产量',
    'SoymealPrice': '豆粕价格',
    'ProcessImport': '加工端进口额'
}

# —— 1. 加载并年度聚合各表 ——
def load_and_agg():
    df1 = pd.read_excel('汇总表.xlsx')
    df1['年份'] = df1['月份'].astype(str).str[:4].astype(int)
    df1 = df1.groupby('年份').agg({
        '乳制品进口量(万吨)': 'sum',
        '饲料进口量(万吨)':   'sum',
        '乳制品出口量(万吨)': 'sum'
    }).rename(columns={
        '乳制品进口量(万吨)': 'DairyImport',
        '饲料进口量(万吨)':   'FeedImport',
        '乳制品出口量(万吨)': 'DairyExport'
    }).reset_index()

    df2 = pd.read_excel('品类进口明细汇总_标准整理.xlsx')
    df2['年份'] = pd.to_datetime(df2['月份']).dt.year
    df2 = df2.groupby('年份')['进口量(万吨)']\
             .sum().reset_index()\
             .rename(columns={'进口量(万吨)': 'ImportDetailVolume'})

    df3 = pd.read_excel('全国奶类进出口数据.xlsx')
    df3['年份'] = (df3['时间'] // 100).astype(int)
    df3 = df3.groupby('年份').agg({
        '当月进口金额（美元）': 'sum',
        '当月进口数量（吨':   'sum',
        '当月出口金额（美元）': 'sum',
        '当月出口数量（吨）':  'sum'
    }).rename(columns={
        '当月进口金额（美元）': 'TradeImportValueUSD',
        '当月进口数量（吨':   'TradeImportQtyT',
        '当月出口金额（美元）': 'TradeExportValueUSD',
        '当月出口数量（吨）':  'TradeExportQtyT'
    }).reset_index()

    df4 = pd.read_excel('常温白奶.xlsx')
    df4 = df4.rename(columns={
        '销售量 (万吨)':    'WhiteMilkSales',
        '销售量增长率 (%)':'WhiteMilkGrowth'
    })[['年份','WhiteMilkSales','WhiteMilkGrowth']]

    df5 = pd.read_excel('全国奶牛存栏量、平均单产、305奶量.xlsx')
    df5 = df5.rename(columns={
        '年度':            '年份',
        '奶牛存栏量（万头）':'CowCount',
        '平均单产（千克）':   'YieldPerCow'
    })[['年份','CowCount','YieldPerCow']]

    df6 = pd.read_excel('全国牛奶产量.xlsx')
    df6 = df6.rename(columns={
        '年度':          '年份',
        '牛奶产量（万吨）':'MilkOutput'
    })[['年份','MilkOutput']]

    df7 = pd.read_excel('全国饲料价格.xlsx')
    df7 = df7.rename(columns={
        '玉米（元/公斤）': 'CornPrice',
        '豆粕（元/公斤）': 'SoymealPrice'
    })
    df7 = df7.groupby('年度')[['CornPrice','SoymealPrice']]\
             .mean().rename_axis('年份').reset_index()

    df8 = pd.read_excel('人均消费奶量.xlsx')
    df8['年份'] = df8['时间'].astype(str).str[:4].astype(int)
    df8 = df8.rename(columns={'全国居民人均（千克）':'PerCapitaConsumption'})\
             [['年份','PerCapitaConsumption']]

    df9 = pd.read_excel('全国主产省生鲜乳价格（已补充最新数据）.xlsx')
    df9 = df9[df9['地区']=='全国'].copy()
    df9['年份'] = df9['年度'].astype(int)
    df9['MilkPrice'] = pd.to_numeric(df9['奶价（元/千克）'], errors='coerce')
    df9 = df9.groupby('年份')['MilkPrice'].mean().reset_index()

    df10 = pd.read_excel('加工端乳制品.xlsx')
    df10 = df10.rename(columns={'总计':'ProcessImport'})[['年份','ProcessImport']]

    return [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10]

tables = load_and_agg()
df_all = reduce(lambda a, b: pd.merge(a, b, on='年份', how='outer'), tables)
df_all = df_all.sort_values('年份').set_index('年份')

# —— 2. 缺失值插补 ——
df_clean = (df_all
    .fillna(method='ffill')
    .fillna(method='bfill')
    .interpolate()
)

# —— 3. ADF 检验 & 差分 ——
adf_p = {col: adfuller(df_clean[col])[1] for col in df_clean.columns}
if sum(p > 0.05 for p in adf_p.values()) > len(adf_p)/2:
    df_proc = df_clean.diff().dropna()
else:
    df_proc = df_clean.copy()

# —— 4. 标准化 ——
scaler = StandardScaler()
df_scaled = pd.DataFrame(
    scaler.fit_transform(df_proc),
    index=df_proc.index,
    columns=df_proc.columns
)
nobs = df_scaled.shape[0]

# —— 5. Granger 因果检验 ——
maxlag_allowed = max(1, nobs // 3)
pair = ['MilkPrice','DairyImport']
try:
    best_lag = int(VAR(df_scaled[pair]).select_order(maxlags=maxlag_allowed).aic)
except ValueError:
    best_lag = 1

for cause, effect in [('DairyImport','MilkPrice'), ('MilkPrice','DairyImport')]:
    try:
        grangercausalitytests(
            df_scaled[[effect, cause]],
            maxlag=best_lag,
            verbose=True
        )
    except InfeasibleTestError:
        pass

# —— 6. VAR 建模 & IRF ——
vars_sel = ['MilkPrice','DairyImport','CornPrice','PerCapitaConsumption']
try:
    lag_aic = int(VAR(df_scaled[vars_sel]).select_order(maxlags=maxlag_allowed).aic)
except ValueError:
    lag_aic = 1
res = VAR(df_scaled[vars_sel]).fit(lag_aic)
irf = res.irf(10)

# 先画出默认的 IRF 图
fig = irf.plot(orth=False)

# 批量替换子图标题与坐标轴标签
n = len(vars_sel)
for i, resp in enumerate(vars_sel):
    for j, imp in enumerate(vars_sel):
        ax = fig.axes[i * n + j]
        ax.set_title(f'{var_zh[resp]} 对 {var_zh[imp]} 冲击的响应',
                     fontproperties='SimHei', fontsize=10)
        ax.set_xlabel('期数', fontproperties='SimHei')
        ax.set_ylabel('响应值', fontproperties='SimHei')

fig.suptitle('脉冲响应函数（IRF）', fontproperties='SimHei', fontsize=14)
plt.tight_layout()
plt.show()

# —— 7. DoWhy 因果推断（线性回归） ——
data = df_clean.reset_index().rename(columns={'index':'年份'})
causal = CausalModel(
    data=data,
    treatment='DairyImport',
    outcome='MilkPrice',
    common_causes=['CornPrice','PerCapitaConsumption','MilkOutput']
)
identified = causal.identify_effect()
estimate = causal.estimate_effect(
    identified,
    method_name="backdoor.linear_regression"
)
print("DoWhy 线性回归估计：", estimate)
print("DoWhy 反驳测试：", causal.refute_estimate(
    identified, estimate, method_name="random_common_cause"
))

# —— 8. 相关性热力图 ——
corr = df_clean.corr()
plt.figure(figsize=(12,10))
sns.heatmap(
    corr, annot=True, fmt=".2f", cmap='coolwarm',
    linewidths=0.5, square=True,
    xticklabels=[var_zh.get(c, c) for c in corr.columns],
    yticklabels=[var_zh.get(r, r) for r in corr.index]
)
plt.title('各变量间皮尔逊相关系数热力图',
          fontproperties='SimHei', fontsize=16)
plt.xticks(rotation=45, ha='right', fontproperties='SimHei')
plt.yticks(rotation=0, fontproperties='SimHei')
plt.tight_layout()
plt.show()
