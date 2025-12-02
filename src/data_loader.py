"""
数据加载器 - 统一负责所有数据的读取和处理
"""

import pandas as pd
import warnings

warnings.filterwarnings('ignore')
from .config import get_data_path, DATA_CONFIG


class DataLoader:
    """数据加载器类"""

    def __init__(self):
        self.hierarchy_data = None
        self.main_data = None
        self.aux_data = None

    def load_hierarchy_data(self):
        """加载水表层级数据"""
        print("正在加载水表层级数据...")
        file_path = get_data_path(DATA_CONFIG['hierarchy_file'])
        self.hierarchy_data = pd.read_excel(file_path, engine='openpyxl')
        print(f"✓ 加载完成，形状: {self.hierarchy_data.shape}")
        return self.hierarchy_data

    def load_main_data(self):
        """加载主数据"""
        print("正在加载主数据...")
        file_path = get_data_path(DATA_CONFIG['main_data_file'])
        self.main_data = pd.read_csv(file_path)
        print(f"✓ 加载完成，形状: {self.main_data.shape}")
        return self.main_data

    def load_aux_data(self):
        """加载辅助数据"""
        print("正在加载辅助数据...")
        file_path = get_data_path(DATA_CONFIG['aux_data_file'])
        self.aux_data = pd.read_csv(file_path)
        print(f"✓ 加载完成，形状: {self.aux_data.shape}")
        return self.aux_data

    def preprocess_hierarchy_data(self, hierarchy_data):
        """预处理水表层级数据"""
        print("正在预处理水表层级数据...")

        # 获取水表名称 - 从前4列中找到第一个非空值
        hierarchy_data['name'] = hierarchy_data.iloc[:, :4].notnull().apply(
            lambda x: x.idxmax(), axis=1
        )

        # 获取水表编码 - 合并前4列的非空值
        hierarchy_data['code'] = hierarchy_data.iloc[:, :4].astype(str).apply(
            lambda x: ''.join(x).replace('nan', ''), axis=1
        )

        # 删除不需要的列
        columns_to_drop = ['一级表计编码', '二级表计编码', '三级表计编码', '四级表计编码', '水表名']
        existing_columns = [col for col in columns_to_drop if col in hierarchy_data.columns]
        if existing_columns:
            hierarchy_data = hierarchy_data.drop(existing_columns, axis=1, errors='ignore')

        print("✓ 预处理完成")
        return hierarchy_data

    def merge_data(self, main_data, hierarchy_data):
        """合并主数据和水表层级数据"""
        print("正在合并数据...")

        # 按水表号合并
        merged_data = pd.merge(main_data, hierarchy_data, on='水表号', how='left')

        # 转换时间格式
        merged_data['采集时间'] = pd.to_datetime(merged_data['采集时间'])

        # 添加时间特征
        merged_data['month'] = merged_data['采集时间'].dt.month
        merged_data['hours'] = merged_data['采集时间'].dt.hour
        merged_data['date'] = merged_data['采集时间'].dt.date
        merged_data['season'] = merged_data['采集时间'].dt.quarter
        merged_data['dayofyear'] = merged_data['采集时间'].dt.dayofyear

        print(f"✓ 合并完成，形状: {merged_data.shape}")
        return merged_data

    def add_teaching_activities(self, data, season_mapping):
        """添加教学活动列"""
        data['教学活动'] = data['month'].map(season_mapping)
        return data

    def load_and_prepare_all_data(self):
        """加载并准备所有数据（一站式服务）"""
        # 加载数据
        hierarchy_raw = self.load_hierarchy_data()
        main_raw = self.load_main_data()

        # 预处理
        hierarchy_processed = self.preprocess_hierarchy_data(hierarchy_raw)

        # 合并
        merged_data = self.merge_data(main_raw, hierarchy_processed)

        # 添加教学活动
        from .config import ANALYSIS_CONFIG
        final_data = self.add_teaching_activities(merged_data, ANALYSIS_CONFIG['season_mapping'])

        # 筛选有效数据
        valid_data = final_data[final_data['code'].notnull()].copy()
        print(f"✓ 有效数据行数: {len(valid_data)}")

        return valid_data