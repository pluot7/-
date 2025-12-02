"""
配置文件 - 集中管理所有路径和参数
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据路径配置
DATA_CONFIG = {
    # 数据文件路径
    'data_dir': PROJECT_ROOT / "data",  # 存放原始数据

    # 具体文件
    'hierarchy_file': '附件_水表层级.xlsx',  # 水表层级文件
    'main_data_file': 'data.csv',  # 主数据文件
    'aux_data_file': 'data2.csv',  # 辅助数据文件

    # 功能区映射
    'area_mapping': {
        '宿舍': ['XXX第一学生宿舍', 'XXX第二学生宿舍', 'XXX第三学生宿舍', 'XXX第四学生宿舍', 'XXX第五学生宿舍', 'XXX第八学生宿舍',
               'XXX第七学生宿舍', 'XXX第九学生宿舍', '养鱼组临工宿舍+', '留学生楼（新）', '养殖馆附房保卫处宿舍+', 'XXXS宾馆',
               '新留学生楼', 'XXX8舍热泵', 'XXX4舍热泵热水', 'XXX5舍热泵热水', 'XXX3舍热泵热水', ],
        '食堂': ['XXX第五食堂', 'XXX第二食堂', 'XXX第一食堂', 'XXXK酒店', ],
        '教学': ['XXX种子楼', 'XXXK楼', 'XXX干训楼', 'XXX成教院XXX分院', 'XXX图书馆', 'XXXT馆后平房', 'XXX国际纳米研究所\t', '纳米楼3楼+',
               '纳米楼4.5楼+', '纳米楼厕所+', 'XXX大楼厕所东', 'XXX大楼厕所西', 'XXX航空航天', 'XXX科学楼', 'XXX西大楼', 'XXX东大楼',
               'XXXL楼', 'XXX老五楼', 'XXX老六楼', '老七楼', 'XXX教学大楼总表', ],
        '办公': ['司法鉴定中心', '离退休活动室', '东大门温室', '老医务楼2.3楼+', '危险品仓库+', '车队+', 'XXX毒物研究所', ],
        '后勤保障': ['XXX后勤楼', 'XXX校医院', 'XXX老医务室楼', '体育馆网球场值班室', '新大门传达室+', '东大门传达室+', '物业',
                 '消防', '校管中心种子楼东+', '高配房+', 'XXX中心水池', 'XXX污水处理', 'XXX锅炉房', 'XXX中心大楼泵房', ],
        '文娱服务': ['XXX游泳池', 'XXX体育馆', '理发店+', '书店+', '茶园+', '教育超市+', 'XXX田径场厕所', '浴室',
                 'XXXS馆', 'XXXL馆', 'XXXM馆', ],
        '绿化养殖': ['养殖馆+', '养殖馆附房一楼厕所+', '养殖馆附房二楼厕所+', '养殖馆公共厕所+', '农业试验站大棚+',
                 '养鱼组厕所+', 'XXX植物园', '养殖队+', '东大门大棚+', ],
    }
}

# 输出路径配置
OUTPUT_CONFIG = {
    'output_dir': PROJECT_ROOT / "outputs",
    'figures_dir': PROJECT_ROOT / "outputs" / "figures",
    'reports_dir': PROJECT_ROOT / "outputs" / "reports",
    'logs_dir': PROJECT_ROOT / "outputs" / "logs"
}

# 分析参数配置
ANALYSIS_CONFIG = {
    # 水表编码前缀
    'target_codes': ['401', '403', '405'],

    # 要排除的建筑
    'exclude_buildings': ['XXXS馆'],

    # 教学活动映射
    'season_mapping': {
        1: '寒假', 2: '寒假',  # 1-2月
        3: '春季学期', 4: '春季学期', 5: '春季学期', 6: '春季学期',  # 3-6月
        7: '暑假', 8: '暑假',  # 7-8月
        9: '秋季学期', 10: '秋季学期', 11: '秋季学期', 12: '秋季学期'  # 9-12月
    }
}

# 可视化配置
VISUALIZATION_CONFIG = {
    'font_family': 'SimHei',
    'figure_size': (12, 8),
    'dpi': 300
}


def create_directories():
    """创建所有需要的目录"""
    dirs_to_create = [
        DATA_CONFIG['data_dir'],
        OUTPUT_CONFIG['output_dir'],
        OUTPUT_CONFIG['figures_dir'],
        OUTPUT_CONFIG['reports_dir'],
        OUTPUT_CONFIG['logs_dir']
    ]

    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)

    print("✓ 目录结构已创建")


def get_data_path(filename):
    """获取数据文件完整路径"""
    return DATA_CONFIG['data_dir'] / filename


def get_figure_path(filename):
    """获取图表保存路径"""
    return OUTPUT_CONFIG['figures_dir'] / filename


def get_report_path(filename):
    """获取报告保存路径"""
    return OUTPUT_CONFIG['reports_dir'] / filename