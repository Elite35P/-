import os
import re
import pandas as pd
from docx import Document

# 1. 准备文件列表（自动去除多余空格）
files = [
    '2022年9月.docx', '2022年10月.docx',
    '2023年1月.docx', '2023年2月.docx', '2023年3月 .docx', '2023年5月 .docx',
    '2024年2月 .docx', '2024年3月.docx', '2024年4月.docx', '2024年5月.docx',
    '2022年8月.docx', '2022年7月.docx',
    '2022年4月.docx', '2022年3月.docx', '2021年12月.docx', '2021年6月.docx',
    '2021年4月.docx', '2021年3月.docx', '2020年12月.docx', '2020年11月.docx'
, '2020年10月.docx', '2020年5月.docx'
]
files = [f.strip() for f in files]
base_dir = r'C:\Users\18811\Desktop\比赛\出口'  # 根据实际路径修改

# 2. 定义要提取的正则模式
pattern_import = re.compile(r"共计进口各类乳制品\s*([\d\.]+)万吨.*?同比.*?([-\d\.]+)%", re.S)
pattern_feed   = re.compile(r"进口干草(?:累计)?([\d\.]+)万吨.*?同比.*?([-\d\.]+)%", re.S)
pattern_export = re.compile(r"共计出口各类乳制品\s*([\d\.]+)万吨.*?同比.*?([-\d\.]+)%", re.S)

# 3. 解析单份报告
def parse_report(path):
    text = "\n".join(p.text for p in Document(path).paragraphs)
    im = pattern_import.search(text)
    fm = pattern_feed.search(text)
    em = pattern_export.search(text)
    # 提取月份
    m = re.search(r'(\d{4})年.*?(\d{1,2})月', os.path.basename(path))
    month = f"{m.group(1)}-{int(m.group(2)):02d}"
    return {
        '月份': month,
        '乳制品进口量(万吨)': float(im.group(1)) if im else None,
        '进口量同比(%)': float(im.group(2)) if im else None,
        '饲料进口量(万吨)': float(fm.group(1)) if fm else None,
        '饲料同比(%)': float(fm.group(2)) if fm else None,
        '乳制品出口量(万吨)': float(em.group(1)) if em else None,
        '出口量同比(%)': float(em.group(2)) if em else None,
    }

# 4. 批量解析并汇总
records = []
for fname in files:
    fullpath = os.path.join(base_dir, fname)
    if os.path.exists(fullpath):
        records.append(parse_report(fullpath))
    else:
        print(f"文件未找到：{fullpath}")

df = pd.DataFrame(records)

# 5. 排序并输出
df['月份排序'] = pd.to_datetime(df['月份'], format='%Y-%m')
df = df.sort_values('月份排序').drop(columns='月份排序').reset_index(drop=True)

# 6. 打印 Markdown 格式的表格
print(df.to_markdown(index=False))
df.to_excel('汇总表.xlsx', index=False)