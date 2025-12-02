"""
功能区分析器 - 从"不同功能区的用水规律特征分析.py"重构
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')
from .config import (
    get_figure_path, get_report_path,
    DATA_CONFIG, VISUALIZATION_CONFIG,
    ANALYSIS_CONFIG
)


class AreaAnalyzer:
    """功能区分析器"""

    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.result = None

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = [VISUALIZATION_CONFIG['font_family']]
        plt.rcParams['axes.unicode_minus'] = False

        # 功能区映射
        self.area2place = DATA_CONFIG['area_mapping']
        self.place2area = self._create_reverse_mapping()

    def _create_reverse_mapping(self):
        """创建反向映射"""
        place2area = {}
        for area, places in self.area2place.items():
            for place in places:
                place2area[place.strip()] = area
        return place2area

    def prepare_data(self):
        """准备数据"""
        print("正在准备功能区分析数据...")

        # 加载并准备数据
        self.result = self.data_loader.load_and_prepare_all_data()

        # 映射功能区
        self.result['area'] = self.result['水表名'].map(self.place2area)

        # 检查未映射的水表
        unmapped = self.result[self.result['area'].isnull()]['水表名'].unique()
        if len(unmapped) > 0:
            print(f"注意: 有 {len(unmapped)} 个水表未映射到功能区")
            if len(unmapped) <= 10:
                print(f"未映射的水表: {unmapped}")

        print(f"✓ 数据准备完成，已映射到 {len(self.result['area'].unique())} 个功能区")
        return self.result

    def save_area_mapping(self):
        """保存功能区映射"""
        area_df = pd.DataFrame({
            '功能区': list(self.area2place.keys()),
            '水表所属区域名称': list(self.area2place.values())
        })

        output_path = get_report_path('area2place.xlsx')
        area_df.to_excel(output_path, index=False)
        print(f"✓ 功能区映射已保存到: {output_path}")

    def analyze_area_daily_usage(self):
        """分析功能区每日用水量"""
        print("\n分析功能区每日用水量...")

        if self.result is None or 'area' not in self.result.columns:
            print("请先准备数据")
            return

        try:
            # 按日期和功能区分组
            area_daily = self.result.groupby(['area', 'date']).agg({'用量': 'sum'}).reset_index()

            # 获取所有功能区
            areas = sorted(self.result['area'].dropna().unique())

            if len(areas) > 0:
                # 创建子图
                fig, axes = plt.subplots(len(areas), 1, figsize=(15, 5 * len(areas)))

                # 如果只有一个功能区，axes不是数组
                if len(areas) == 1:
                    axes = [axes]

                for i, area in enumerate(areas):
                    area_data = area_daily[area_daily['area'] == area]

                    if not area_data.empty:
                        area_data = area_data.sort_values('date')
                        axes[i].plot(area_data['date'], area_data['用量'], marker='o', linewidth=2)
                        axes[i].set_title(f'{area}区 - 每日用水量')
                        axes[i].set_xlabel('日期')
                        axes[i].set_ylabel('用水量')
                        axes[i].tick_params(axis='x', rotation=45)
                        axes[i].grid(True, alpha=0.3)

                plt.tight_layout()
                plt.savefig(get_figure_path('不同功能区用水量.png'), dpi=VISUALIZATION_CONFIG['dpi'])
                plt.close()
                print("✓ 已保存: 不同功能区用水量.png")
        except Exception as e:
            print(f"分析功能区每日用水量失败: {e}")

    def analyze_seasonal_patterns(self):
        """分析季节性用水模式"""
        print("\n分析季节性用水模式...")

        if self.result is None:
            print("请先准备数据")
            return

        for area in self.result['area'].dropna().unique():
            try:
                data_tmp = self.result[self.result['area'] == area]

                if len(data_tmp) > 0:
                    # 按季度和小时分析
                    seasonal_data = data_tmp.groupby(['season', 'hours']).agg({'用量': 'sum'}).unstack().fillna(0)

                    if not seasonal_data.empty:
                        fig, ax = plt.subplots(figsize=VISUALIZATION_CONFIG['figure_size'])
                        seasonal_data.T.loc['用量', :].plot.line(
                            ax=ax,
                            title=f'{area}功能区用水量的变化趋势图（按季度）'
                        )
                        ax.set_xlabel('小时')
                        ax.set_ylabel('用水量')
                        ax.grid(True, alpha=0.3)

                        plt.tight_layout()
                        plt.savefig(get_figure_path(f'{area}_季度用水趋势.png'), dpi=VISUALIZATION_CONFIG['dpi'])
                        plt.close()

                        print(f"✓ 已保存: {area}_季度用水趋势.png")
            except Exception as e:
                print(f"分析{area}季节性模式失败: {e}")

    def analyze_teaching_activity_patterns(self):
        """分析教学活动用水模式"""
        print("\n分析教学活动用水模式...")

        if self.result is None or '教学活动' not in self.result.columns:
            print("请先准备数据")
            return

        for area in self.result['area'].dropna().unique():
            try:
                data_tmp = self.result[self.result['area'] == area]

                if len(data_tmp) > 0:
                    # 按教学活动和小时分析
                    activity_data = data_tmp.groupby(['教学活动', 'hours']).agg({'用量': 'sum'}).unstack().fillna(0)

                    if not activity_data.empty:
                        fig, ax = plt.subplots(figsize=VISUALIZATION_CONFIG['figure_size'])
                        activity_data.T.loc['用量', :].plot.line(
                            ax=ax,
                            title=f'{area}功能区用水量的变化趋势图（按教学活动）'
                        )
                        ax.set_xlabel('小时')
                        ax.set_ylabel('用水量')
                        ax.grid(True, alpha=0.3)

                        plt.tight_layout()
                        plt.savefig(get_figure_path(f'{area}_教学活动用水趋势.png'), dpi=VISUALIZATION_CONFIG['dpi'])
                        plt.close()

                        print(f"✓ 已保存: {area}_教学活动用水趋势.png")
            except Exception as e:
                print(f"分析{area}教学活动模式失败: {e}")

    def analyze_seasonal_hourly_usage(self):
        """分析每季度的小时用水量"""
        print("\n分析每季度的小时用水量...")

        if self.result is None:
            print("请先准备数据")
            return

        # 按水表名、季度和小时分组
        tmp = self.result.groupby(['水表名', 'season', 'hours']).agg({'用量': 'sum'}).unstack().fillna(0)
        water_names = self.result['水表名'].unique()

        # 只绘制前10个水表，避免过多图形
        for n in water_names[:10]:
            try:
                if n in tmp.index:
                    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
                    fig.suptitle(f'{n} - 每季度小时用水量', fontsize=16)

                    for i, season in enumerate(sorted(tmp.loc[n, '用量'].columns.get_level_values(0).unique())):
                        ax = axes[i // 2, i % 2]
                        season_data = tmp.loc[n, '用量'][season]
                        season_data.plot(kind='line', ax=ax, title=f'第{season}季度')
                        ax.set_xlabel('小时')
                        ax.set_ylabel('用水量')
                        ax.grid(True, alpha=0.3)

                    plt.tight_layout()
                    plt.savefig(get_figure_path(f'{n}_季度用水量.png'), dpi=VISUALIZATION_CONFIG['dpi'])
                    plt.close()
                    print(f"✓ 已保存: {n}_季度用水量.png")
            except Exception as e:
                print(f"绘制{n}的季度用水量图失败: {e}")

    def analyze_teaching_activity_hourly_usage(self):
        """分析不同教学活动每小时平均用水量"""
        print("\n分析不同教学活动每小时平均用水量...")

        if self.result is None or '教学活动' not in self.result.columns:
            print("请先准备数据")
            return

        # 按水表名、教学活动和小时分组
        tmp = self.result.groupby(['水表名', '教学活动', 'hours']).agg({'用量': 'mean'}).unstack().fillna(0)
        water_names = self.result['水表名'].unique()

        # 只绘制前10个水表
        for n in water_names[:10]:
            try:
                if n in tmp.index:
                    activities = sorted(tmp.loc[n, '用量'].columns.get_level_values(0).unique())

                    if len(activities) > 0:
                        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
                        fig.suptitle(f'{n} - 不同教学活动小时平均用水量', fontsize=16)

                        for i, activity in enumerate(activities):
                            if i < 4:  # 最多显示4个子图
                                ax = axes[i // 2, i % 2]
                                activity_data = tmp.loc[n, '用量'][activity]
                                activity_data.plot(kind='line', ax=ax, title=activity)
                                ax.set_xlabel('小时')
                                ax.set_ylabel('平均用水量')
                                ax.grid(True, alpha=0.3)

                        plt.tight_layout()
                        plt.savefig(get_figure_path(f'{n}_教学活动用水量.png'), dpi=VISUALIZATION_CONFIG['dpi'])
                        plt.close()
                        print(f"✓ 已保存: {n}_教学活动用水量.png")
            except Exception as e:
                print(f"绘制{n}的教学活动用水量图失败: {e}")

    def run_analysis(self):
        """运行完整的功能区分析"""
        print("=" * 60)
        print("功能区分析开始")
        print("=" * 60)

        # 1. 准备数据
        self.prepare_data()

        # 2. 保存功能区映射
        self.save_area_mapping()

        # 3. 分析每日用水量
        self.analyze_area_daily_usage()

        # 4. 分析季节性模式
        self.analyze_seasonal_patterns()

        # 5. 分析教学活动模式
        self.analyze_teaching_activity_patterns()

        # 6. 分析每季度小时用水量
        self.analyze_seasonal_hourly_usage()

        # 7. 分析教学活动小时用水量
        self.analyze_teaching_activity_hourly_usage()

        print("=" * 60)
        print("功能区分析完成")
        print("=" * 60)