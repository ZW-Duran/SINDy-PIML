import subprocess
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# 配置专业级别的日志输出格式
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_task(step_name: str, script_path: Path, args: Optional[List[str]] = None) -> None:
    """
    Run a Python script as a subprocess with robust error handling.
    """
    print(f"\n{'='*35}\n🚀 Execute: {step_name}\n{'='*35}")

    # 将 pathlib 对象解析为绝对路径字符串
    cmd = [sys.executable, str(script_path.resolve())]
    if args:
        cmd.extend(args)
    
    try:
        # check=True: 如果子进程返回非 0 状态码，会自动抛出 CalledProcessError 异常
        subprocess.run(cmd, check=True)
        logging.info(f"✅ {step_name} Finished!")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Failed at {step_name} with exit code {e.returncode}.")
        sys.exit(1)
    except FileNotFoundError:
        logging.error(f"❌ Script not found: {script_path}")
        sys.exit(1)

def main() -> None:
    # 1. 采用 argparse 构建专业的命令行接口 (CLI)
    parser = argparse.ArgumentParser(
        description="Run the SINDy vehicle dynamics identification pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "filepath", 
        nargs="?", 
        type=Path, 
        help="Path to the raw MoTeC CSV file. If omitted, uses the newest .csv in ./data"
    )
    
    args_cli = parser.parse_args()
    
    # 2. 使用现代的 pathlib 处理目录与文件
    data_dir = Path("data")
    processed_dir = Path("processed_data")
    
    if args_cli.filepath:
        raw_file_path = args_cli.filepath
        if not raw_file_path.exists():
            logging.error(f"File not found: {raw_file_path}")
            sys.exit(1)
    else:
        # 默认行为：安全地寻找 ./data 下的最新文件
        if not data_dir.exists():
            logging.error("Directory './data' does not exist.")
            sys.exit(1)
            
        csv_files = list(data_dir.glob('*.csv'))
        if not csv_files:
            logging.error("No .csv files found in ./data/")
            sys.exit(1)
            
        # 使用 pathlib 的 stat().st_mtime 获取修改时间
        raw_file_path = max(csv_files, key=lambda p: p.stat().st_mtime)

    logging.info(f"Target Raw File: {raw_file_path}")

    # 3. 动态生成清理后的文件路径
    # .stem 获取文件名(不含后缀)，.suffix 获取后缀(.csv) -> 非常优雅！
    cleaned_file_name = f"{raw_file_path.stem}_cleaned{raw_file_path.suffix}"
    cleaned_file_path = processed_dir / cleaned_file_name

    # 4. 定义并执行任务流
    tasks = [
        ("Data Parsing & SG Filter", Path("src/process_data.py"), [str(raw_file_path)]),
        ("SINDy Modeling", Path("src/run_sindy.py"), [str(cleaned_file_path)])
    ]

    for step_name, script_path, task_args in tasks:
        run_task(step_name, script_path, task_args)

    logging.info("🎉 All pipelines executed successfully!")

if __name__ == "__main__":
    main()