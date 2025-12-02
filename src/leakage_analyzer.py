"""
漏损分析器 - 从"供水管网漏损分析.py"重构
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')
from .config import (
    get_figure_path, get_report_path,
    VISUALIZATION_CONFIG
)


class LeakageAnalyzer:
    """漏损分析器"""

    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.result = None

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = [VISUALIZATION_CONFIG['font_family']]
        plt.rcParams['axes.unicode_minus'] = False

    def prepare_data(self):
        """准备数据"""
        print("正在加载辅助数据...")

        # 加载辅助数据
        aux_data = self.data_loader.load_aux_data()
        aux_data['采集时间'] = pd.to_datetime(aux_data['采集时间'])

        # 检查必要的列
        if 'code' not in aux_data.columns:
            print("警告: 数据中没有'code'列，尝试查找...")
            # 查找编码相关列
            code_columns = [col for col in aux_data.columns if 'code' in col.lower() or '编码' in col]
            if code_columns:
                print(f"找到编码列: {code_columns[0]}")
                aux_data['code'] = aux_data[code_columns[0]]
            else:
                print("错误: 未找到编码列")
                return None

        if '用户名' not in aux_data.columns:
            print("警告: 数据中没有'用户名'列，尝试查找...")
            # 查找用户相关列
            user_columns = [col for col in aux_data.columns if '用户' in col or '名' in col]
            if user_columns:
                print(f"找到用户名列: {user_columns[0]}")
                aux_data['用户名'] = aux_data[user_columns[0]]
            else:
                print("错误: 未找到用户名列")
                return None

        # 筛选有效数据
        self.result = aux_data[aux_data['code'].notnull()].copy()
        print(f"✓ 有效数据行数: {len(self.result)}")

        return self.result

    def analyze_40404T(self):
        """分析40404T水表"""
        print("\n分析40404T水表...")

        if self.result is None:
            print("请先准备数据")
            return

        if '40404T' in self.result['code'].values:
            result_40404T = self.result[self.result['code'] == '40404T'].copy()

            if len(result_40404T) > 0:
                # 设置时间索引
                result_40404T.set_index("采集时间", inplace=True)

                # 计算每15分钟的用量和
                sum_40404T = result_40404T['用量'].resample('15min').sum()

                # 可视化
                fig, ax = plt.subplots(figsize=VISUALIZATION_CONFIG['figure_size'])
                sum_40404T.plot.line(
                    ax=ax,
                    title='40404T水表用水量时间序列（15分钟间隔）'
                )
                ax.set_xlabel('采集时间')
                ax.set_ylabel('用水量')
                ax.grid(True, alpha=0.3)

                plt.tight_layout()
                plt.savefig(get_figure_path('40404T_用水量时间序列.png'), dpi=VISUALIZATION_CONFIG['dpi'])
                plt.close()
                print("✓ 已保存: 40404T_用水量时间序列.png")

                # 漏水分析
                same_consumption = (sum_40404T.diff().resample('3h').mean() == 0).sum()
                zero_consumption = (sum_40404T.resample('3h').mean() == 0).sum()

                if len(sum_40404T) > 0:
                    leakage_ratio = (same_consumption - zero_consumption) * 12 / len(sum_40404T)
                    print(f"40404T水表漏水比例: {leakage_ratio:.2%}")
            else:
                print("40404T水表数据为空")
        else:
            print("数据中没有找到40404T水表")

    def calculate_leakage_rates(self):
        """计算所有水表的漏水率"""
        print("\n计算所有水表的漏水率...")

        if self.result is None:
            print("请先准备数据")
            return None

        res_rate = {}

        for username in self.result['用户名'].unique():
            result_tmp = self.result[self.result['用户名'] == username].copy()

            if len(result_tmp) > 0:
                try:
                    result_tmp.set_index("采集时间", inplace=True)

                    if len(result_tmp) > 1:
                        sum_tmp = result_tmp['用量'].resample('15min').sum()

                        if len(sum_tmp) > 0:
                            same_consumption = (sum_tmp.diff().resample('3h').mean() == 0).sum()
                            zero_consumption = (sum_tmp.resample('3h').mean() == 0).sum()

                            if len(sum_tmp) > 0:
                                leakage_ratio = (same_consumption - zero_consumption) * 12 / len(sum_tmp)
                                res_rate[username] = leakage_ratio
                except Exception as e:
                    print(f"计算用户{username}漏水率失败: {e}")

        # 转换为DataFrame
        if res_rate:
            res = pd.DataFrame({'code': list(res_rate.keys()), 'rate': list(res_rate.values())})
            res['rate'] = (res['rate'] * 100).round(2)
            res_sorted = res.sort_values('rate', ascending=False)

            return res_sorted
        else:
            return None

    def visualize_leakage_rates(self, leakage_rates):
        """可视化漏水率"""
        if leakage_rates is None or len(leakage_rates) == 0:
            print("没有漏水率数据可可视化")
            return

        print(f"共分析 {len(leakage_rates)} 个水表的漏水率")

        # 漏水率分布直方图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        ax1.hist(leakage_rates['rate'], bins=20, edgecolor='black', alpha=0.7)
        ax1.set_xlabel('漏水率 (%)')
        ax1.set_ylabel('水表数量')
        ax1.set_title('漏水率分布')
        ax1.grid(True, alpha=0.3)

        # 漏水率排名条形图
        top_n = min(15, len(leakage_rates))
        top_data = leakage_rates.head(top_n)

        ax2.barh(range(len(top_data)), top_data['rate'])
        ax2.set_yticks(range(len(top_data)))
        ax2.set_yticklabels(top_data['code'])
        ax2.set_xlabel('漏水率 (%)')
        ax2.set_title(f'漏水率排名前{top_n}')
        ax2.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig(get_figure_path('漏水率分析.png'), dpi=VISUALIZATION_CONFIG['dpi'])
        plt.close()
        print("✓ 已保存: 漏水率分析.png")

        # 显示分析结果
        print("\n漏水率排名前10:")
        print(leakage_rates.head(10))

        print("\n详细分析:")
        print(f"平均漏水率: {leakage_rates['rate'].mean():.2f}%")
        print(f"中位数漏水率: {leakage_rates['rate'].median():.2f}%")
        print(f"最高漏水率: {leakage_rates['rate'].max():.2f}%")
        print(f"最低漏水率: {leakage_rates['rate'].min():.2f}%")

    def save_leakage_results(self, leakage_rates):
        """保存漏水率结果"""
        if leakage_rates is not None and len(leakage_rates) > 0:
            output_path = get_report_path("leakage_rate.xlsx")
            leakage_rates.to_excel(output_path, index=False)
            print(f"✓ 漏水率结果已保存到: {output_path}")

    def run_analysis(self):
        """运行完整漏损分析"""
        print("=" * 60)
        print("漏损分析开始")
        print("=" * 60)

        # 1. 准备数据
        self.prepare_data()

        # 2. 分析40404T水表
        self.analyze_40404T()

        # 3. 计算漏水率
        leakage_rates = self.calculate_leakage_rates()

        # 4. 可视化结果
        if leakage_rates is not None:
            self.visualize_leakage_rates(leakage_rates)

            # 5. 保存结果
            self.save_leakage_results(leakage_rates)
        else:
            print("没有计算到任何漏水率数据")

        print("=" * 60)
        print("漏损分析完成")
        print("=" * 60)