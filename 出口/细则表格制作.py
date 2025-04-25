import os
import re
import pandas as pd
from docx import Document

# 1. Report file list (adjust base_dir if necessary)
files = [
    # '2022年9月.docx', '2022年10月.docx', '2023年1月.docx', '2023年2月.docx', '2023年3月 .docx', '2023年5月 .docx',
    # '2024年2月 .docx', '2024年3月.docx', '2024年4月.docx', '2024年5月.docx',
    # '2022年8月.docx', '2022年7月.docx', '2022年4月.docx', '2022年3月.docx',
    # '2021年12月.docx', '2021年6月.docx',
    '2021年4月.docx', '2021年3月.docx', '2020年12月.docx', '2020年11月.docx',
    '2020年10月.docx', '2020年5月.docx'
]
files = [f.strip() for f in files]
base_dir = r'C:\Users\18811\Desktop\比赛\出口'  # Adjust based on your actual directory

# 2. Regex pattern: Adjusted to match the new format from your example
pattern = re.compile(
    r"(大包粉|婴配粉|奶\s*酪|奶\s*油|乳\s*清|炼\s*乳|蛋白类|包装牛奶|稀奶油)"
    r".*?进口\s*([\d\.]+)\s*万吨.*?同比\s*([+\-]?[0-9\.]+)%"
    r".*?进口额\s*([\d\.]+)\s*亿美元.*?同比\s*([+\-]?[0-9\.]+)%"
    # r".*?平均价格\s*([\d\.]+)\s*美元\s*/\s*吨.*?同比\s*([+\-]?[0-9\.]+)%"
    r".*?主要来自([^。]+)。",
    re.S
)

# 3. Batch processing for the reports
records = []
for fname in files:
    print(fname)
    path = os.path.join(base_dir, fname)
    if not os.path.exists(path):
        print(f"[警告] 未找到文件：{path}")
        continue
    text = "\n".join(p.text for p in Document(path).paragraphs)

    # Extract month and year, modify the pattern slightly to cover 2020 and 2021
    m = re.search(r'(\d{4})年.*?(\d{1,2})月', fname)
    if m:
        month = f"{m.group(1)}-{int(m.group(2)):02d}"
    else:
        # Handle cases where the filename format might not match exactly
        print(f"[警告] 文件名无法提取月份: {fname}")
        continue

    # Extract all matching rows
    for cat, vol, vol_yoy, val, val_yoy, sources in pattern.findall(text):
        print("====================")
        records.append({
            '月份': month,
            '品类': cat.strip(),
            '进口量(万吨)': float(vol),
            '进口量同比(%)': float(vol_yoy),
            '进口额(亿元)': float(val) * 10,  # Convert亿美元 to亿元
            '进口额同比(%)': float(val_yoy),
            # '均价(美元/吨)': float(price),
            # '均价同比(%)': float(price_yoy),
            '主要来源及占比': sources.strip()
        })

# 4. Create DataFrame and sort
df = pd.DataFrame(records)
df['排序键'] = pd.to_datetime(df['月份'], format='%Y-%m')
df = df.sort_values(['排序键', '品类']).drop(columns='排序键').reset_index(drop=True)

# 5. Output the results to Markdown table or save to file
print(df.to_markdown(index=False))  # Print the Markdown table
df.to_csv('品类进口明细汇总-1.csv', index=False)  # Save as CSV file
