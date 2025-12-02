"""
关系模型分析器 - 从"关系模型的构建及误差分析.py"重构
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')
from .config import (
    get_figure_path, get_report_path,
    ANALYSIS_CONFIG, VISUALIZATION_CONFIG,
    DATA_CONFIG
)


class RelationshipAnalyzer:
    """关系模型分析器"""

    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.result = None

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = [VISUALIZATION_CONFIG['font_family']]
        plt.rcParams['axes.unicode_minus'] = False

    def prepare_data(self):
        """准备数据"""
        self.result = self.data_loader.load_and_prepare_all_data()

        # 添加6小时时间片
        self.result['6hour'] = pd.cut(
            x=self.result['hours'],
            bins=[-1, 6, 12, 18, 24],
            labels=[1, 2, 3, 4]
        ).astype(int) + (self.result['采集时间'].dt.dayofyear - 1) * 4

        return self.result

    def analyze_time_granularities(self):
        """分析不同时间粒度"""
        if self.result is None:
            print("请先准备数据")
            return

        print("开始分析不同时间粒度的用水关系...")

        # 1. 15分钟粒度
        try:
            tmp_15min = self.result.groupby(['name', '采集时间']).agg({'用量': 'sum'}).unstack()
            self.plot_time_granularity(tmp_15min, '15分钟', '水表关系模型图_15分钟.png')
        except Exception as e:
            print(f"15分钟粒度分析出错: {e}")

        # 2. 6小时粒度
        try:
            tmp_6hour = self.result.groupby(['name', '6hour']).agg({'用量': 'sum'}).unstack()
            self.plot_time_granularity(tmp_6hour, '6小时', '水表关系模型图_6小时.png')
        except Exception as e:
            print(f"6小时粒度分析出错: {e}")

        # 3. 1天粒度
        try:
            tmp_1day = self.result.groupby(['name', 'date']).agg({'用量': 'sum'}).unstack()
            self.plot_time_granularity(tmp_1day, '1天', '水表关系模型图_1天.png')
        except Exception as e:
            print(f"1天粒度分析出错: {e}")

    def plot_time_granularity(self, data, title_suffix, filename):
        """绘制特定时间粒度的图表"""
        if data.shape[1] == 0:
            print(f"{title_suffix}粒度: 数据不足")
            return

        available_names = data.columns.get_level_values(1).unique()
        selected_names = []

        # 选择一级和二级水表
        for level in ['一级表计编码', '二级表计编码']:
            if level in available_names:
                selected_names.append(level)

        if len(selected_names) >= 2:
            fig, ax = plt.subplots(figsize=VISUALIZATION_CONFIG['figure_size'])

            try:
                data.T.loc['用量', selected_names].plot.line(
                    ax=ax,
                    title=f'一级和二级水表关系模型图({title_suffix})',
                    ylabel='用水量',
                    alpha=0.7
                )
                ax.legend(selected_names)
                ax.grid(True, alpha=0.3)

                plt.tight_layout()
                plt.savefig(get_figure_path(filename), dpi=VISUALIZATION_CONFIG['dpi'])
                plt.close()
                print(f"✓ 已保存: {filename}")

            except Exception as e:
                print(f"绘制{title_suffix}图表失败: {e}")
                plt.close()
        else:
            print(f"{title_suffix}粒度: 一级或二级水表数据不足")

    def analyze_by_code_prefix(self):
        """按水表编码前缀分析"""
        print("\n开始按编码前缀分析...")

        # 创建编码前缀列
        self.result['code_3'] = self.result['code'].astype(str).str[:3]

        for code_prefix in ANALYSIS_CONFIG['target_codes']:
            print(f"分析编码前缀: {code_prefix}")

            result_code = self.result[self.result['code_3'] == code_prefix].copy()

            if len(result_code) > 0:
                available_names = result_code['name'].unique()
                selected_names = []

                for level in ['一级表计编码', '二级表计编码']:
                    if level in available_names:
                        selected_names.append(level)

                if len(selected_names) >= 2:
                    try:
                        tmp = result_code.groupby(['name', '采集时间']).agg({'用量': 'sum'}).unstack()
                        cumulative_data = tmp.T.loc['用量', selected_names].fillna(0).cumsum()

                        fig, ax = plt.subplots(figsize=VISUALIZATION_CONFIG['figure_size'])
                        cumulative_data.plot.line(
                            ax=ax,
                            title=f'水表关系模型图(15分钟)—{code_prefix}',
                            ylabel='累计用水量',
                            alpha=0.7
                        )
                        ax.legend(selected_names)
                        ax.grid(True, alpha=0.3)

                        plt.tight_layout()
                        plt.savefig(
                            get_figure_path(f'累计用水量关系_{code_prefix}.png'),
                            dpi=VISUALIZATION_CONFIG['dpi']
                        )
                        plt.close()
                        print(f"✓ 已保存: 累计用水量关系_{code_prefix}.png")

                    except Exception as e:
                        print(f"分析{code_prefix}失败: {e}")
                else:
                    print(f"编码前缀{code_prefix}的一级或二级水表数据不足")
            else:
                print(f"编码前缀{code_prefix}没有数据")

    def analyze_405_meters(self):
        """分析405水表"""
        print("\n开始分析405水表...")

        if 'code_3' not in self.result.columns:
            self.result['code_3'] = self.result['code'].astype(str).str[:3]

        result_405 = self.result[self.result['code_3'] == '405'].copy()

        if len(result_405) == 0:
            print("没有找到405水表数据")
            return

        # 检查是否有'水表名'列
        if '水表名' in result_405.columns:
            # 删除排除的建筑
            exclude_buildings = ANALYSIS_CONFIG['exclude_buildings']
            result_405_filtered = result_405[~result_405['水表名'].isin(exclude_buildings)].copy()

            # 绘制累计用水量关系
            try:
                tmp_405 = result_405_filtered.groupby(['name', '采集时间']).agg({'用量': 'sum'}).unstack()
                available_names = tmp_405.columns.get_level_values(1).unique()
                selected_names = []

                for level in ['一级表计编码', '二级表计编码']:
                    if level in available_names:
                        selected_names.append(level)

                if len(selected_names) >= 2:
                    cumulative_405 = tmp_405.T.loc['用量', selected_names].fillna(0).cumsum()

                    fig, ax = plt.subplots(figsize=VISUALIZATION_CONFIG['figure_size'])
                    cumulative_405.plot.line(
                        ax=ax,
                        title='405水表一级和二级水表关系模型图(15分钟)',
                        ylabel='累计用水量',
                        alpha=0.7
                    )
                    ax.legend(selected_names)
                    ax.grid(True, alpha=0.3)

                    plt.tight_layout()
                    plt.savefig(get_figure_path('405水表分析.png'), dpi=VISUALIZATION_CONFIG['dpi'])
                    plt.close()
                    print("✓ 已保存: 405水表分析.png")

            except Exception as e:
                print(f"分析405水表失败: {e}")
        else:
            print("结果中没有'水表名'列")

    def error_analysis(self):
        """误差分析"""
        print("\n开始误差分析...")

        # 排除特定建筑
        exclude_buildings = ANALYSIS_CONFIG['exclude_buildings']
        result_filtered = self.result[~self.result['水表名'].isin(exclude_buildings)].copy()

        for code_prefix in ANALYSIS_CONFIG['target_codes']:
            if 'code_3' not in result_filtered.columns:
                result_filtered['code_3'] = result_filtered['code'].astype(str).str[:3]

            if code_prefix in result_filtered['code_3'].unique():
                result_error = result_filtered[result_filtered['code_3'] == code_prefix].copy()

                if len(result_error) > 0:
                    try:
                        # 计算各级别总用水量
                        tmp = result_error.groupby('name').agg({'用量': 'sum'})

                        if '一级表计编码' in tmp.index and '二级表计编码' in tmp.index:
                            primary_usage = tmp.loc['一级表计编码', '用量']
                            secondary_usage = tmp.loc['二级表计编码', '用量']

                            # 计算误差
                            error = (secondary_usage - primary_usage) / primary_usage
                            print(f"{code_prefix} 误差分析:")
                            print(f"  一级水表总用水量: {primary_usage:.2f}")
                            print(f"  二级水表总用水量: {secondary_usage:.2f}")
                            print(f"  误差率: {error * 100:.2f}%")
                        else:
                            print(f"{code_prefix} 缺少一级或二级水表数据")
                    except Exception as e:
                        print(f"计算{code_prefix}误差失败: {e}")
                else:
                    print(f"{code_prefix} 没有数据")

    def run_analysis(self):
        """运行完整分析流程"""
        print("=" * 60)
        print("关系模型分析开始")
        print("=" * 60)

        # 1. 准备数据
        self.prepare_data()

        # 2. 分析不同时间粒度
        self.analyze_time_granularities()

        # 3. 按编码前缀分析
        self.analyze_by_code_prefix()

        # 4. 分析405水表
        self.analyze_405_meters()

        # 5. 误差分析
        self.error_analysis()

        print("=" * 60)
        print("关系模型分析完成")
        print("=" * 60)