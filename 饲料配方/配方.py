import numpy as np
from scipy.optimize import linprog

# —— 1. 价格字典（价格上涨后的值，元/kg DM） ——
price_dict = {
    # 0–2月龄
    '全脂牛奶': 7.2,  # 上涨20%
    '代乳粉': 10.2,  # 上涨20%
    '乳清粉': 7.5,  # 上涨25%
    '优质干草': 3.0,  # 上涨20%
    # 通用及已列主料
    '苜蓿': 3.75,  # 上涨25%
    '进口燕麦': 4.2,  # 上涨20%
    '压片玉米': 3.12,  # 上涨30%，关键原料
    '燕麦片': 4.32,  # 上涨20%
    '豆粕': 4.94,  # 上涨30%，关键蛋白源
    '燕麦草': 3.48,  # 上涨20%
    '小麦草': 0.84,  # 上涨20%
    '小麦麸皮': 2.64,  # 上涨20%
    '玉米青贮': 0.96,  # 上涨20%
    '豆粕(3–6)': 4.94,  # 上涨30%，关键蛋白源
    '菜粕': 3.75,  # 上涨25%
    '糖蜜': 1.32,  # 上涨10%
    '甜菜颗粒': 1.87,  # 上涨10%
    '钙磷预混料': 18.0,  # 上涨20%
    '盐砖': 0.55,  # 上涨10%
    # 7–13月龄
    '全株玉米青贮': 1.2,  # 上涨20%
    '羊草': 1.44,  # 上涨20%
    '大麦': 3.25,  # 上涨30%
    '棉籽粕': 3.84,  # 上涨20%
    'DDGS': 3.24,  # 上涨20%
    '苹果粕': 1.65,  # 上涨10%
    '啤酒糟': 2.2,  # 上涨10%
    '小苏打': 6.0,  # 上涨20%
    '氧化镁': 24.0,  # 上涨20%
    # 14–23月龄
    '苜蓿青贮': 1.2,  # 上涨20%
    '稻草': 0.88,  # 上涨10%
    '蒸汽压片高粱': 3.25,  # 上涨30%
    '甘薯渣': 1.1,  # 上涨10%
    '葵花粕': 3.6,  # 上涨20%
    '玉米蛋白粉': 8.45,  # 上涨30%
    '大豆皮': 1.8,  # 上涨20%
    'β-胡萝卜素': 96.0,  # 上涨20%
    '胆碱': 24.0,  # 上涨20%
    # 通用预混料
    '预混料': 14.4,  # 上涨20%
    # 添加可能缺失的原料
    '燕麦青干草': 3.0,  # 估计值
}

# —— 构造原料列表与价格向量 ——
ingredients = list(price_dict.keys())
prices = np.array([price_dict[i] for i in ingredients])

# —— 2. 营养成分字典（示例值：[ME, CP, Starch, NDF, Feed_NDF]） ——
nutr_val = {
    # 0–2月龄
    '全脂牛奶': [13.0, 25.0, 0.0, 0.0, 0.0],
    '代乳粉': [18.0, 22.0, 45.0, 0.0, 0.0],
    '乳清粉': [14.5, 12.0, 70.0, 0.0, 0.0],
    '优质干草': [8.0, 12.0, 1.0, 50.0, 50.0],
    # 通用及已列主料
    '苜蓿': [8.5, 18.0, 2.0, 42.0, 42.0],
    '进口燕麦': [14.0, 11.0, 30.0, 36.0, 36.0],
    '压片玉米': [15.5, 8.5, 72.0, 12.0, 12.0],
    '燕麦片': [15.8, 11.0, 40.6, 35.5, 35.5],
    '豆粕': [13.0, 48.0, 6.0, 8.0, 8.0],
    '燕麦草': [10.4, 6.9, 29.1, 44.3, 44.3],
    '小麦草': [7.0, 4.0, 1.0, 75.0, 75.0],
    '小麦麸皮': [11.0, 17.0, 15.0, 9.0, 9.0],
    '玉米青贮': [10.0, 7.0, 32.0, 44.0, 44.0],
    '豆粕(3–6)': [13.0, 48.0, 6.0, 8.0, 8.0],
    '菜粕': [11.5, 36.0, 5.0, 30.0, 30.0],
    '糖蜜': [9.6, 5.0, 0.0, 8.0, 8.0],
    '甜菜颗粒': [10.0, 9.0, 2.0, 47.0, 47.0],
    '钙磷预混料': [0.0, 0.0, 0.0, 0.0, 0.0],
    '盐砖': [0.0, 0.0, 0.0, 0.0, 0.0],
    # 7–13月龄
    '全株玉米青贮': [10.0, 7.0, 32.0, 44.0, 44.0],
    '羊草': [9.0, 12.0, 2.0, 55.0, 55.0],
    '大麦': [14.0, 12.0, 60.0, 10.0, 10.0],
    '棉籽粕': [13.0, 40.0, 5.0, 37.0, 37.0],
    'DDGS': [11.0, 30.0, 5.0, 30.0, 30.0],
    '苹果粕': [9.0, 6.0, 20.0, 30.0, 30.0],
    '啤酒糟': [8.5, 25.0, 5.0, 40.0, 40.0],
    '小苏打': [0.0, 0.0, 0.0, 0.0, 0.0],
    '氧化镁': [0.0, 0.0, 0.0, 0.0, 0.0],
    # 14–23月龄
    '苜蓿青贮': [10.0, 7.0, 32.0, 44.0, 44.0],
    '稻草': [5.0, 4.0, 1.0, 80.0, 80.0],
    '蒸汽压片高粱': [14.0, 9.0, 65.0, 15.0, 15.0],
    '甘薯渣': [7.5, 6.0, 10.0, 60.0, 60.0],
    '葵花粕': [11.0, 36.0, 1.0, 30.0, 30.0],
    '玉米蛋白粉': [15.0, 60.0, 0.0, 5.0, 5.0],
    '大豆皮': [9.0, 12.0, 5.0, 60.0, 60.0],
    'β-胡萝卜素': [0.0, 0.0, 0.0, 0.0, 0.0],
    '胆碱': [0.0, 0.0, 0.0, 0.0, 0.0],
    '预混料': [0.0, 0.0, 0.0, 0.0, 0.0],
    '燕麦青干草': [9.5, 8.0, 2.0, 52.0, 52.0],  # 估计值
}

# —— 构造营养矩阵 nut_mat ——
ingredients = list(nutr_val.keys())  # 保证顺序一致
nut_mat = np.vstack([nutr_val[i] for i in ingredients]).T

# —— 营养索引 ——
nut_idx = {'ME': 0, 'CP': 1, 'Starch': 2, 'NDF': 3, 'Feed_NDF': 4}

# —— 各阶段原料池 & 放宽营养需求约束 ——
stage_ingredients = {
    '0-2月龄': ['全脂牛奶', '代乳粉', '乳清粉', '优质干草', '苜蓿', '进口燕麦', '压片玉米', '燕麦片', '豆粕', '燕麦草',
                '小麦草', '预混料'],
    '3-6月龄': ['玉米青贮', '燕麦青干草', '压片玉米', '小麦麸皮', '豆粕(3–6)', '菜粕', '糖蜜', '甜菜颗粒', '钙磷预混料',
                '盐砖'],
    '7-13月龄': ['全株玉米青贮', '羊草', '压片玉米', '大麦', '棉籽粕', 'DDGS', '苹果粕', '啤酒糟', '小苏打', '氧化镁'],
    '14-23月龄': ['苜蓿青贮', '稻草', '蒸汽压片高粱', '甘薯渣', '葵花粕', '玉米蛋白粉', '大豆皮', '甜菜颗粒',
                  'β-胡萝卜素', '胆碱', '预混料'],
}

# 放宽营养需求约束
stages_req = {
    '0-2月龄': {'ME': (14.5, None), 'CP': (18, 24), 'Starch': (18, 38), 'NDF': (None, None), 'Feed_NDF': (None, None)},
    '3-6月龄': {'ME': (11.5, None), 'CP': (14, 22), 'Starch': (12, 32), 'NDF': (22, 35), 'Feed_NDF': (17, 27)},
    '7-13月龄': {'ME': (8.5, None), 'CP': (14, 18), 'Starch': (8, None), 'NDF': (23, 35), 'Feed_NDF': (17, 27)},
    '14-23月龄': {'ME': (7.5, None), 'CP': (13, 17), 'Starch': (6, None), 'NDF': (23, 35), 'Feed_NDF': (17, 27)},
}

# 添加原料使用比例约束
max_ingredient_pct = {
    '0-2月龄': {'豆粕': 0.3, '压片玉米': 0.55, '预混料': 0.05},
    '3-6月龄': {'豆粕(3–6)': 0.25, '压片玉米': 0.35, '钙磷预混料': 0.03, '菜粕': 0.15},
    '7-13月龄': {'压片玉米': 0.25, '棉籽粕': 0.12, 'DDGS': 0.15, '小苏打': 0.02},
    '14-23月龄': {'玉米蛋白粉': 0.1, '预混料': 0.03, '蒸汽压片高粱': 0.15}
}

# 添加原料最小使用比例约束（确保某些原料必须使用）
min_ingredient_pct = {
    '0-2月龄': {'预混料': 0.01},
    '3-6月龄': {'钙磷预混料': 0.005, '糖蜜': 0.01},
    '7-13月龄': {'小苏打': 0.005},
    '14-23月龄': {'预混料': 0.005, 'β-胡萝卜素': 0.0005}
}

# 保存优化结果的字典
optimization_results = {}

# —— 线性规划优化并输出结果 ——
print("\n================ 饲料价格上涨情况下的优化配方 ================\n")

for stage, req in stages_req.items():
    print(f"\n===== {stage} 优化配方 =====")

    # 获取当前阶段的原料列表
    stage_ings = stage_ingredients[stage]
    idxs = [ingredients.index(i) for i in stage_ings]
    c = np.array([price_dict[i] for i in stage_ings])
    M = nut_mat[:, idxs]

    # 构建约束
    A_eq = [np.ones(len(idxs))];
    b_eq = [1.0]  # 总和为1的约束
    A_ub, b_ub = [], []

    # 添加营养约束
    for nut, (low, high) in req.items():
        row = M[nut_idx[nut]]
        if high is not None:
            A_ub.append(row);
            b_ub.append(high)
        if low is not None:
            A_ub.append(-row);
            b_ub.append(-low)

    # 添加原料最大使用比例约束
    if stage in max_ingredient_pct:
        for ing, max_pct in max_ingredient_pct[stage].items():
            if ing in stage_ings:
                ing_idx = stage_ings.index(ing)
                row = np.zeros(len(idxs))
                row[ing_idx] = 1.0
                A_ub.append(row)
                b_ub.append(max_pct)

    # 添加原料最小使用比例约束
    if stage in min_ingredient_pct:
        for ing, min_pct in min_ingredient_pct[stage].items():
            if ing in stage_ings:
                ing_idx = stage_ings.index(ing)
                row = np.zeros(len(idxs))
                row[ing_idx] = -1.0
                A_ub.append(row)
                b_ub.append(-min_pct)

    # 求解线性规划
    res = linprog(c, A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, 1)] * len(idxs), method='highs',
                  options={'maxiter': 5000})

    # 保存结果
    optimization_results[stage] = {
        'success': res.success,
        'cost': res.fun if res.success else None,
        'message': res.message,
        'formulation': dict(zip(stage_ings, res.x * 100)) if res.success else None,
        'nutrition': {nut: M[nut_idx[nut]] @ res.x for nut in nut_idx} if res.success else None
    }

    # 打印结果
    if res.success:
        print(f"优化成功：成本 {res.fun:.2f} 元/kg DM")

        # 打印配方组成（按比例排序）
        sorted_ings = sorted(zip(stage_ings, res.x), key=lambda x: x[1], reverse=True)
        print("\n配方组成:")
        for ing, pct in sorted_ings:
            if pct > 0.001:  # 仅显示比例大于0.1%的原料
                print(f"  {ing:15s}: {pct * 100:6.2f}%")

        # 打印营养价值
        nutr_values = M @ res.x
        print("\n营养价值:")
        for nut, idx in nut_idx.items():
            print(f"  {nut:10s}: {nutr_values[idx]:6.2f}")

    else:
        print(f"优化失败: {res.message}")

# —— 对比典型配方 ——
print("\n\n================ 传统配方（价格上涨后）================\n")

# 典型配方定义
typical_formulations = {
    '0-2月龄': {
        '压片玉米': 50.0,
        '豆粕': 25.0,
        '燕麦片': 15.0,
        '苜蓿': 8.0,
        '预混料': 2.0
    },
    '3-6月龄': {
        '玉米青贮': 35.0,
        '压片玉米': 30.0,
        '豆粕(3–6)': 15.0,
        '小麦麸皮': 10.0,
        '糖蜜': 5.0,
        '钙磷预混料': 5.0
    },
    '7-13月龄': {
        '全株玉米青贮': 65.0,
        '压片玉米': 20.0,
        '棉籽粕': 8.0,
        'DDGS': 5.0,
        '小苏打': 2.0
    },
    '14-23月龄': {
        '苜蓿青贮': 70.0,
        '蒸汽压片高粱': 15.0,
        '葵花粕': 8.0,
        '大豆皮': 5.0,
        '预混料': 2.0
    }
}

# 计算并打印典型配方成本与营养价值
for stage, formulation in typical_formulations.items():
    print(f"\n===== {stage} 典型配方 =====")

    # 计算成本
    cost = sum(price_dict[ing] * (pct / 100) for ing, pct in formulation.items())
    print(f"成本: {cost:.2f} 元/kg DM")

    # 打印配方
    print("\n配方组成:")
    for ing, pct in formulation.items():
        print(f"  {ing:15s}: {pct:6.2f}%")

    # 计算营养价值
    nutrition = {nut: 0 for nut in nut_idx}
    for ing, pct in formulation.items():
        for nut, idx in nut_idx.items():
            nutrition[nut] += nutr_val[ing][idx] * (pct / 100)

    # 打印营养价值
    print("\n营养价值:")
    for nut, value in nutrition.items():
        print(f"  {nut:10s}: {value:6.2f}")

# —— 成本对比分析 ——
print("\n\n================ 成本对比分析 ================\n")
print("阶段\t\t优化配方成本\t典型配方成本\t节约百分比")
print("-------------------------------------------------------------")

for stage in stage_ingredients.keys():
    if optimization_results[stage]['success']:
        optimized_cost = optimization_results[stage]['cost']
        typical_cost = sum(price_dict[ing] * (pct / 100) for ing, pct in typical_formulations[stage].items())
        saving_pct = (typical_cost - optimized_cost) / typical_cost * 100

        print(f"{stage:10s}\t{optimized_cost:6.2f} 元/kg\t{typical_cost:6.2f} 元/kg\t{saving_pct:6.2f}%")
    else:
        print(f"{stage:10s}\t优化失败\t\t\t")

print("\n\n================ 结束 ================\n")
