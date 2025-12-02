"""
主程序入口 - 整合所有分析
"""

import warnings

warnings.filterwarnings('ignore')

# 导入配置文件
from .config import create_directories

# 导入各个分析器
from .data_loader import DataLoader
from .relationship_analyzer import RelationshipAnalyzer
from .leakage_analyzer import LeakageAnalyzer
from .area_analyzer import AreaAnalyzer


def main_menu():
    """显示主菜单"""
    print("=" * 60)
    print("校园供水系统智能管理系统")
    print("=" * 60)
    print("1. 完整分析（运行所有分析）")
    print("2. 关系模型分析")
    print("3. 漏损分析")
    print("4. 功能区分析")
    print("5. 退出")
    print("=" * 60)


def run_full_analysis():
    """运行完整分析"""
    print("\n" + "=" * 60)
    print("开始完整分析")
    print("=" * 60)

    # 创建数据加载器
    data_loader = DataLoader()

    # 1. 关系模型分析
    print("\n>>> 第1部分：关系模型分析")
    relation_analyzer = RelationshipAnalyzer(data_loader)
    relation_analyzer.run_analysis()

    # 2. 漏损分析
    print("\n>>> 第2部分：漏损分析")
    leakage_analyzer = LeakageAnalyzer(data_loader)
    leakage_analyzer.run_analysis()

    # 3. 功能区分析
    print("\n>>> 第3部分：功能区分析")
    area_analyzer = AreaAnalyzer(data_loader)
    area_analyzer.run_analysis()

    print("\n" + "=" * 60)
    print("完整分析完成！")
    print(f"所有结果已保存到: outputs/ 目录")
    print("=" * 60)


def run_relationship_analysis():
    """运行关系模型分析"""
    print("\n" + "=" * 60)
    print("开始关系模型分析")
    print("=" * 60)

    data_loader = DataLoader()
    analyzer = RelationshipAnalyzer(data_loader)
    analyzer.run_analysis()

    print("\n关系模型分析完成！")


def run_leakage_analysis():
    """运行漏损分析"""
    print("\n" + "=" * 60)
    print("开始漏损分析")
    print("=" * 60)

    data_loader = DataLoader()
    analyzer = LeakageAnalyzer(data_loader)
    analyzer.run_analysis()

    print("\n漏损分析完成！")


def run_area_analysis():
    """运行功能区分析"""
    print("\n" + "=" * 60)
    print("开始功能区分析")
    print("=" * 60)

    data_loader = DataLoader()
    analyzer = AreaAnalyzer(data_loader)
    analyzer.run_analysis()

    print("\n功能区分析完成！")


def main():
    """主函数"""
    # 创建必要的目录
    create_directories()

    while True:
        main_menu()

        try:
            choice = input("请选择分析类型 (1-5): ").strip()

            if choice == '1':
                run_full_analysis()
            elif choice == '2':
                run_relationship_analysis()
            elif choice == '3':
                run_leakage_analysis()
            elif choice == '4':
                run_area_analysis()
            elif choice == '5':
                print("感谢使用，再见！")
                break
            else:
                print("无效选择，请重新输入")

            # 询问是否继续
            if choice != '5':
                continue_choice = input("\n是否继续分析？(y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("感谢使用，再见！")
                    break

        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"程序运行出错: {e}")


if __name__ == "__main__":
    main()