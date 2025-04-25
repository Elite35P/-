import numpy as np
from scipy.optimize import linprog

# —— 1. 价格字典（价格上涨后的值，元/kg DM） ——
price_dict = {
    # 0–2月龄
    '全脂牛奶':    4.50,   # 估计液态牛奶
    '代乳粉':      12.00,  # 市场乳粉约12元/kg
    '乳清粉':      8.65,   # 乳清粉平均价8.65元/kg
    '优质干草':    3.00,   # 保持原值

    # 通用及已列主料
    '苜蓿':        3.75,
    '进口燕麦':    4.20,
    '压片玉米':    2.26,   # 玉米约2258元/吨
    '燕麦片':      4.20,   # 与进口燕麦同价
    '豆粕':        3.95,   # 豆粕约3950元/吨
    '燕麦草':      3.48,
    '小麦草':      0.84,
    '小麦麸皮':    2.45,   # 小麦约2449元/吨
    '玉米青贮':    1.00,   # 饲料玉米青贮约1000元/吨

    # 3–6月龄专用
    '豆粕(3–6)':  3.95,
    '菜粕':        2.71,   # 菜粕约2705元/吨
    '糖蜜':        1.32,
    '甜菜颗粒':    1.87,
    '预混料':      14.40,
    '盐砖':        0.55,

    # 7–13月龄
    '全株玉米青贮':1.20,
    '羊草':        1.50,
    '大麦':        2.45,   # 参考小麦价
    '棉籽粕':      2.43,   # 棉粕约2425元/吨
    'DDGS':        2.25,   # DDGS约2251元/吨
    '苹果粕':      1.65,
    '啤酒糟':      2.20,
    '小苏打':      3.00,
    '氧化镁':      24.00,

    # 14–23月龄
    '苜蓿青贮':    1.20,
    '稻草':        0.88,
    '蒸汽压片高粱':2.45,   # 同精饲料水平
    '甘薯渣':      1.10,
    '葵花粕':      3.60,
    '玉米蛋白粉':  8.45,
    '大豆皮':      1.80,
    'β-胡萝卜素': 96.00,
    '胆碱':        24.00,

    # 过瘤胃脂肪粉
    '过瘤胃脂肪粉':20.00,

    # 其它补充
    '燕麦青干草':  3.00,
    '小麦':        2.45,
    '玉米秸秆':    1.00,
    '木薯渣':      1.50,
    '阴离子盐预混料':1.50,
    '苜蓿干草':    1.50,
}


# —— 构造原料列表与价格向量 ——
ingredients = list(price_dict.keys())
prices = np.array([price_dict[i] for i in ingredients])

# —— 2. 营养成分字典（[ME, CP, Starch, NDF, Feed_NDF]） ——
nutr_val = {
    '苜蓿干草': [8.39, 19.1, 6.1, 36.7, 36.7],
    '木薯渣': [12.38, 2.5, 71.6, 8.4, 8.4],
    '阴离子盐预混料': [0.0, 0.0, 0.0, 0.0, 0.0],
    '玉米秸秆': [3.97, 4.0, 2.8, 81.0, 81.0],
    '小麦': [8.13, 13.1, 54.6, 13.3, 13.3],
    '全脂牛奶': [10.64, 24.0, 0.0, 0.0, 0.0],
    '代乳粉': [18.0, 26.0, 0.0, 0.0, 0.0],
    '乳清粉': [14.5, 12.0, 0.0, 0.0, 0.0],
    '优质干草': [7.5, 8.0, 3.0, 50.0, 50.0],
    '苜蓿': [7.8, 17.5, 2.5, 45.0, 45.0],
    '进口燕麦': [8.0, 11.5, 50.0, 15.0, 15.0],
    '压片玉米': [8.49, 8.5, 70.0, 10.0, 10.0],
    '燕麦片': [7.95, 13.0, 55.0, 20.0, 20.0],
    '豆粕': [7.89, 48.0, 1.0, 11.0, 11.0],
    '燕麦草': [7.1, 12.0, 5.0, 55.0, 55.0],
    '小麦草': [7.0, 10.0, 4.0, 60.0, 60.0],
    '小麦麸皮': [7.1, 16.0, 3.0, 22.0, 22.0],
    '玉米青贮': [6.7, 8.1, 29.5, 47.0, 47.0],
    '豆粕(3–6)': [7.85, 44.0, 1.5, 12.0, 12.0],
    '菜粕': [8.25, 36.0, 4.5, 15.0, 15.0],
    '糖蜜': [9.9, 7.5, 70.0, 0.0, 0.0],
    '甜菜颗粒': [8.5, 7.0, 45.0, 15.0, 15.0],
    '钙磷预混料': [0.0, 0.0, 0.0, 0.0, 0.0],
    '盐砖': [0.0, 0.0, 0.0, 0.0, 0.0],
    '全株玉米青贮': [6.85, 7.5, 25.0, 50.0, 50.0],
    '羊草': [7.2, 14.0, 2.0, 48.0, 48.0],
    '大麦': [8.2, 12.0, 58.0, 10.0, 10.0],
    '棉籽粕': [7.6, 42.0, 2.0, 14.0, 14.0],
    'DDGS': [8.0, 30.0, 35.0, 35.0, 35.0],
    '苹果粕': [7.0, 4.0, 15.0, 25.0, 25.0],
    '啤酒糟': [7.1, 20.0, 5.0, 15.0, 15.0],
    '小苏打': [0.0, 0.0, 0.0, 0.0, 0.0],
    '氧化镁': [0.0, 0.0, 0.0, 0.0, 0.0],
    '苜蓿青贮': [7.6, 16.0, 3.0, 45.0, 45.0],
    '稻草': [3.5, 3.0, 0.5, 85.0, 85.0],
    '蒸汽压片高粱': [8.15, 10.0, 60.0, 15.0, 15.0],
    '甘薯渣': [10.5, 2.0, 80.0, 5.0, 5.0],
    '葵花粕': [7.8, 30.0, 1.0, 25.0, 25.0],
    '玉米蛋白粉': [8.5, 60.0, 2.0, 5.0, 5.0],
    '大豆皮': [6.9, 10.0, 20.0, 50.0, 50.0],
    'β-胡萝卜素': [0.0, 0.0, 0.0, 0.0, 0.0],
    '胆碱': [0.0, 0.0, 0.0, 0.0, 0.0],
    '预混料': [0.0, 0.0, 0.0, 0.0, 0.0],
    '燕麦青干草': [7.3, 14.0, 2.0, 52.0, 52.0],
    '过瘤胃脂肪粉': [0.0, 0.0, 0.0, 0.0, 0.0],
}


# —— 构造营养矩阵 nut_mat ——
ingredients = list(nutr_val.keys())
nut_mat = np.vstack([nutr_val[i] for i in ingredients]).T
nut_idx = {'ME':0,'CP':1,'Starch':2,'NDF':3,'Feed_NDF':4}

# —— 阶段原料池与需求约束 ——
# —— 阶段原料池与需求约束（已对照经典配方修正，并增加围产期前后） ——
stage_ingredients = {
    # 生长阶段
    '0-2月龄':    ['全脂牛奶','代乳粉','乳清粉','压片玉米','燕麦片','豆粕','苜蓿','燕麦草','优质干草','预混料'],
    '3-6月龄':    ['玉米青贮','燕麦青干草','压片玉米','小麦麸皮','豆粕(3–6)','菜粕','糖蜜','甜菜颗粒','预混料'],
    '7-13月龄':   ['全株玉米青贮','羊草','压片玉米','大麦','棉籽粕','DDGS','苹果粕','啤酒糟','小苏打'],
    '14-23月龄':  ['苜蓿青贮','稻草','蒸汽压片高粱','甘薯渣','葵花粕','玉米蛋白粉','大豆皮','预混料'],

    # 围产期细分
    '围产产前21天': ['苜蓿青贮','羊草','压片玉米','甜菜颗粒','豆粕','小苏打','预混料'],
    '围产产后21天': ['玉米青贮','压片玉米','豆粕','过瘤胃脂肪粉','预混料'],

    # 泌乳期
    '泌乳早期':   ['玉米青贮','蒸汽压片高粱','豆粕','棉籽粕','糖蜜','苜蓿','过瘤胃脂肪粉','预混料'],
    '泌乳中期':   ['玉米青贮','小麦麸皮','DDGS','菜粕','甜菜颗粒','苹果粕','预混料'],
    '泌乳后期':   ['玉米秸秆','小麦麸皮','葵花粕','木薯渣','预混料'],

    # 干奶期
    '干奶前期':   ['苜蓿干草','玉米青贮','小麦麸皮','预混料'],
    '干奶后期':   ['玉米青贮','燕麦草','大麦','阴离子盐预混料']
}

# —— 调整后的营养需求约束 ——
#   • 适当下调 ME 下限，放宽高纤维阶段的 NDF 上限
#   • 保持 CP、Starch、Feed_NDF 区间基本不变
stages_req = {
    '0-2月龄': {
        'ME':      (8.00,  8.03),
        'CP':      (18,    24),
        'Starch':  (18,    43.70),
        'NDF':     (14.35, 15),
        'Feed_NDF':(14.35, 15),
    },
    '3-6月龄': {
        'ME':      (7.28,  7.28),
        'CP':      (14,    22),
        'Starch':  (12,    35.28),
        'NDF':     (22,    37),
        'Feed_NDF':(17,    29),
    },
    '7-13月龄': {
        'ME':      (7.16,  7.16),
        'CP':      (11.44, 18),
        'Starch':  (8,     32.16),
        'NDF':     (23,    38),
        'Feed_NDF':(17,    37.37),
    },
    '14-23月龄': {
        'ME':      (7.00,  7.51),
        'CP':      (13,    17),
        'Starch':  (6,     12.18),
        'NDF':     (23,    38.25),
        'Feed_NDF':(17,    38.25),
    },
    '干奶后期': {
        'ME':      (6.30,  6.30),
        'CP':      (8.85,  17),
        'Starch':  (8,     22.05),
        'NDF':     (22,    41.00),
        'Feed_NDF':(17,    41.00),
    },
    '干奶前期': {
        'ME':      (7.00,  7.83),
        'CP':      (14,    18),
        'Starch':  (10,    20),
        'NDF':     (20,    38.32),
        'Feed_NDF':(16,    38.32),
    },
    '泌乳早期': {
        'ME':      (7.03,  7.03),
        'CP':      (15.48, 22),
        'Starch':  (20,    34.51),
        'NDF':     (20,    36),
        'Feed_NDF':(15,    28),
    },
    '泌乳中期': {
        'ME':      (7.02,  7.02),
        'CP':      (13.00, 19),
        'Starch':  (10,    32.44),
        'NDF':     (22,    37),
        'Feed_NDF':(16,    35.41),
    },
    '泌乳后期': {
        'ME':      (5.00,  5.00),
        'CP':      (8.27,  16),
        'Starch':  (4.66,  20),
        'NDF':     (20,    62.75),
        'Feed_NDF':(15,    62.75),
    },
}



# —— 最大配比约束 ——
max_ingredient_pct = {
    '0-2月龄':    {'豆粕':0.30,     '压片玉米':0.55,    '预混料':0.05},
    '3-6月龄':    {'豆粕(3–6)':0.25,'压片玉米':0.35,    '钙磷预混料':0.03,'菜粕':0.15},
    '7-13月龄':   {'压片玉米':0.25, '棉籽粕':0.12,     'DDGS':0.15,    '小苏打':0.02},
    '14-23月龄':  {'玉米蛋白粉':0.10,'预混料':0.03,     '蒸汽压片高粱':0.15},

    # 围产前21天（沿用干奶后期原料池）
    '围产产前21天':{'玉米青贮':0.60,'燕麦草':0.40,      '大麦':0.20,    '阴离子盐预混料':0.10},

    # 围产后21天（沿用泌乳早期原料池，并放宽脂肪粉）
    '围产产后21天':{'玉米青贮':0.50,'蒸汽压片高粱':0.50,'豆粕':0.25,  '过瘤胃脂肪粉':0.10,'预混料':0.03},

    '泌乳早期':   {'玉米青贮':0.50,'蒸汽压片高粱':0.50,'豆粕':0.25,  '过瘤胃脂肪粉':0.10,'预混料':0.03},
    '泌乳中期':   {'玉米青贮':0.70,'小麦':0.30,        'DDGS':0.15,    '菜粕':0.10,      '预混料':0.03},
    '泌乳后期':   {'玉米秸秆':0.80,'小麦麸皮':0.20,    '葵花粕':0.15,  '木薯渣':0.10,    '预混料':0.03},

    '干奶前期':   {'苜蓿干草':0.80,'玉米青贮':0.30,    '小麦麸皮':0.06,'预混料':0.02},
    '干奶后期':   {'玉米青贮':0.70,'燕麦草':0.40,      '大麦':0.20,    '阴离子盐预混料':0.10},
}

# —— 最小配比约束 ——
min_ingredient_pct = {
    '0-2月龄':    {'预混料':0.02},
    '3-6月龄':    {'钙磷预混料':0.005,'糖蜜':0.01},
    '7-13月龄':   {'小苏打':0.005},
    '14-23月龄':  {'预混料':0.005,'β-胡萝卜素':0.0005},

    '围产产前21天':{'阴离子盐预混料':0.05},
    '围产产后21天':{'过瘤胃脂肪粉':0.02,'预混料':0.02},

    '泌乳早期':   {'过瘤胃脂肪粉':0.03,'预混料':0.02},
    '泌乳中期':   {'预混料':0.02},
    '泌乳后期':   {'预混料':0.02},

    '干奶前期':   {'预混料':0.01},
    '干奶后期':   {'阴离子盐预混料':0.05},
}



optimization_results = {}

print("\n================ 饲料价格上涨情况下的优化配方 ================\n")
for stage, req in stages_req.items():
    print(f"\n===== {stage} 优化配方 =====")
    stage_ings = stage_ingredients[stage]
    idxs = [ingredients.index(i) for i in stage_ings]
    c = np.array([price_dict[i] for i in stage_ings])
    M = nut_mat[:, idxs]

    A_eq = [np.ones(len(idxs))]
    b_eq = [1.0]
    A_ub, b_ub = [], []

    for nut, (low, high) in req.items():
        row = M[nut_idx[nut]]
        if high is not None:
            A_ub.append(row); b_ub.append(high)
        if low is not None:
            A_ub.append(-row); b_ub.append(-low)

    for ing, mx in max_ingredient_pct.get(stage, {}).items():
        if ing in stage_ings:
            i = stage_ings.index(ing)
            row = np.zeros(len(idxs)); row[i] = 1
            A_ub.append(row); b_ub.append(mx)
    for ing, mn in min_ingredient_pct.get(stage, {}).items():
        if ing in stage_ings:
            i = stage_ings.index(ing)
            row = np.zeros(len(idxs)); row[i] = -1
            A_ub.append(row); b_ub.append(-mn)

    res = linprog(c, A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0,1)]*len(idxs), method='highs')

    optimization_results[stage] = res
    if res.success:
        print(f"成本 {res.fun:.2f} 元/kg DM")
        for ing, pct in sorted(zip(stage_ings, res.x), key=lambda x:-x[1]):
            if pct>1e-3: print(f"  {ing:8s}: {pct*100:6.2f}%")
        vals = M @ res.x
        print("营养价值:", {nut: vals[nut_idx[nut]] for nut in nut_idx})
    else:
        print("优化失败:", res.message)

# （后续可添加典型配方对比等）
# —— 对比典型配方 ——

print("\n\n================ 传统配方（价格上涨后）================\n")

# 典型配方定义
typical_formulations = {
    # —— 生长阶段，保持不变 ——
    '0-2月龄':    {'压片玉米':50,'豆粕':25,'燕麦片':15,'苜蓿':8,'预混料':2},
    '3-6月龄':    {'玉米青贮':35,'压片玉米':30,'豆粕':15,'小麦麸皮':10,'糖蜜':5,'预混料':5},
    '7-13月龄':   {'全株玉米青贮':65,'压片玉米':20,'棉籽粕':8,'DDGS':5,'小苏打':2},
    '14-23月龄':  {'苜蓿青贮':70,'蒸汽压片高粱':15,'葵花粕':8,'大豆皮':5,'预混料':2},

    # —— 泌乳、干奶阶段，按叙述修正 ——
    # 围产前21天（干奶后期）
    '干奶后期':  {'玉米青贮':50,'燕麦草':30,'大麦':10,'阴离子盐预混料':10},
    # 干奶前期（产前60-21天）
    '干奶前期':  {'苜蓿干草':70,'玉米青贮':25,'小麦麸皮':4,'预混料':1},
    # 产后21天（泌乳早期第一子阶段，可合并到泌乳早期）
    '泌乳早期':  {'玉米青贮':35,'蒸汽压片高粱':40,'豆粕':18,'过瘤胃脂肪粉':4,'预混料':3},
    # 泌乳中期（产后101-200天）
    '泌乳中期':  {'玉米青贮':60,'小麦':20,'DDGS':10,'菜粕':7,'预混料':3},
    # 泌乳后期（产后201至干奶）
    '泌乳后期':  {'玉米秸秆':70,'小麦麸皮':15,'葵花粕':10,'木薯渣':3,'预混料':2},
}


# 计算并打印典型配方成本与营养价值
for stage, formulation in typical_formulations.items():
    print(f"\n===== {stage} 典型配方 =====")
    cost = sum(price_dict[ing] * (pct / 100) for ing, pct in formulation.items())
    print(f"成本: {cost:.2f} 元/kg DM")
    print("\n配方组成:")
    for ing, pct in formulation.items():
        print(f"  {ing:15s}: {pct:6.2f}%")
    nutrition = {nut: 0 for nut in nut_idx}
    for ing, pct in formulation.items():
        for nut, idx in nut_idx.items():
            nutrition[nut] += nutr_val[ing][idx] * (pct / 100)
    print("\n营养价值:")
    for nut, value in nutrition.items():
        print(f"  {nut:10s}: {value:6.2f}")

# —— 成本对比分析 ——

print("\n\n================ 成本对比分析 ================\n")
print("阶段\t\t优化配方成本\t典型配方成本\t节约百分比")
print("-------------------------------------------------------------")

for stage in stage_ingredients.keys():
    res = optimization_results.get(stage)
    if res and res.success:
        optimized_cost = res.fun
        typ = typical_formulations.get(stage, {})
        typical_cost = sum(price_dict[ing] * (pct / 100) for ing, pct in typ.items())
        saving_pct = (typical_cost - optimized_cost) / typical_cost * 100 if typical_cost else 0.0
        print(f"{stage:10s}\t{optimized_cost:6.2f} 元/kg\t{typical_cost:6.2f} 元/kg\t{saving_pct:6.2f}%")
    else:
        print(f"{stage:10s}\t优化失败\t\t\t")

print("\n\n================ 结束 ================\n")
nutrients = ['ME', 'CP', 'Starch', 'NDF', 'Feed_NDF']

# —— 下面这两行是新加的 ——
typical_formulations['围产产前21天'] = typical_formulations['干奶后期'].copy()
typical_formulations['围产产后21天'] = typical_formulations['泌乳早期'].copy()
import pulp
import numpy as np
def diagnose_stage(stage):
    pool = typical_formulations[stage]
    ingr = list(pool.keys())
    # 构建 LP 问题，只用来做可行性／极值分析
    prob = pulp.LpProblem('diag', pulp.LpStatusOptimal)
    x = pulp.LpVariable.dicts('x', ingr, lowBound=0)
    # 混合比例和为 1
    prob += pulp.lpSum([x[i] for i in ingr]) == 1

    # 先添加最小／最大配比约束（如果你有 max_ingredient_pct/min_ingredient_pct，也可加上）
    # e.g. prob += x['过瘤胃脂肪粉'] <= 0.10

    # 针对每个营养素，分别求最大和最小
    results = {}
    for nut in nutrients:
        # 先求最小值
        prob_min = prob.copy()
        prob_min += pulp.lpSum([nutr_val[i][nutrients.index(nut)] * x[i] for i in ingr])
        prob_min.sense = pulp.LpMinimize
        prob_min.solve(pulp.PULP_CBC_CMD(msg=False))
        min_val = pulp.value(pulp.lpSum([nutr_val[i][nutrients.index(nut)] * x[i] for i in ingr]))
        # 再求最大值
        prob_max = prob.copy()
        prob_max += pulp.lpSum([nutr_val[i][nutrients.index(nut)] * x[i] for i in ingr])
        prob_max.sense = pulp.LpMaximize
        prob_max.solve(pulp.PULP_CBC_CMD(msg=False))
        max_val = pulp.value(pulp.lpSum([nutr_val[i][nutrients.index(nut)] * x[i] for i in ingr]))
        results[nut] = (min_val, max_val)
    return results


# 对所有无解阶段运行诊断
for st in ['围产产前21天', '围产产后21天', '泌乳早期', '泌乳中期', '泌乳后期', '干奶前期', '干奶后期']:
    res = diagnose_stage(st)
    req = stages_req[st]
    print(f"--- {st} ---")
    for nut, (low, high) in req.items():
        got_min, got_max = res[nut]
        print(f"{nut:8s}  needs [{low},{high}]  achievable [{got_min:.2f},{got_max:.2f}]")
    print()