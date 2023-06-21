import argparse
from charset_mnbvc import api

"""
本工具目的是帮助快速浏览文件夹下文件的头和尾，以便于快速定位文件头和文件尾部的干扰信息
"""


class TextViewer:
    def __init__(self, folder, head, tail, mode=2):
        _, self.files_info = api.from_dir(folder, mode)
        self.head = head
        self.tail = tail

    def view(self, file, enc):
        if not enc:
            print(f"Error: {file} encode error")
            return
        try:
            with open(file, "r", encoding=enc) as f:
                lines = f.readlines()
        except (ValueError, LookupError):
            print(f"Error: {file} encode error")
            return
        striped_lines = []
        for raw_line in lines:
            lstriped = raw_line.strip()
            if lstriped:
                striped_lines.append(lstriped)
        print(f"{file:-^80}")
        for idx, line in enumerate(striped_lines[:self.head]):
            print(idx, line)
        print(f"{'分割线':=^80}")
        for idx, line in enumerate(striped_lines[-self.tail:]):
            print(idx, line)
        print(f"{'结束':-^80}")

    def run(self):
        for file, enc in self.files_info:
            self.view(file, enc)
            input("请按回车键继续...(ctrl+c退出))")

def parse_args():
    parser = argparse.ArgumentParser(
        prog="textviewer",
        description="帮助快速浏览文件夹下文件的头和尾",
    )
    parser.add_argument("-F", "--folder", type=str, required=True, help="目标文件夹")
    parser.add_argument("--head", type=int, default=10, help="查看前多少行")
    parser.add_argument("--tail", type=int, default=10, help="查看尾多少行")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    et = TextViewer(args.folder, args.head, args.tail)
    et.run()
