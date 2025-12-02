#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键运行脚本 - 直接双击运行
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入并运行主程序
from src.main import main

if __name__ == "__main__":
    print("=" * 60)
    print("校园供水系统智能管理系统 - 启动中...")
    print("=" * 60)

    try:
        main()
    except Exception as e:
        print(f"程序运行出错: {e}")
        print("\n请按Enter键退出...")
        input()