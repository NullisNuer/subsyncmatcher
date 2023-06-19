import sys
import locale
import argparse
import os
import logging
import yaml

import tkinter as tk
from tkinter import filedialog

ascii_art = r"""
  __                  __                         
 (    /_/'_//_  _    (      _    /|/| __/_ / _ _ 
__)(/()// /((-_)    __)(//)(    /   |(//( /)(-/  
                       /                                           
     """
# http://www.network-science.de/ascii/ Format:doom
logger = logging.getLogger(__name__)
logger.error(f'{ascii_art}')

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_dir)
os.makedirs('log', exist_ok=True)
config_path = os.path.join('config', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)
video_extensions = config["videos_format"]
subs_extensions = config["subtitles_format"]
is_alass_mod = config["alass"]
is_ffsubsync_mod = config["ffsubsync"]
paths = None
is_order_mod = False
is_rename_mod = False


def select_files():
    global files
    files = list(filedialog.askopenfilenames())


def select_folders():
    global folders
    folders = [filedialog.askdirectory()]


def edit_config(alass, ffsubsync):
    if alass:
        config['alass'] = True
    else:
        config['alass'] = False
    if ffsubsync:
        config['ffsubsync'] = True
    else:
        config['ffsubsync'] = False
    with open(config_path, 'w') as f:
        yaml.safe_dump(config, f)
    select.destroy()


if __name__ == '__main__':
    system_language, _ = locale.getdefaultlocale()
    if 'zh' in system_language:
        from core.matcher import MatcherZH
        print("__________________________________________________________________________________")
        print("\n1. 视频和字幕需在同一文件夹")
        print("\n2. 无法匹配的字幕将会在运行中要求手选")
        print("\n3. 目前支持alass、ffsubsync")
        print("__________________________________________________________________________________\n")

        if len(sys.argv) > 1 and '-p' not in sys.argv and '-h' not in sys.argv and '--path' not in sys.argv and '--help' not in sys.argv:
            paths = sys.argv[1:]

        else:
            parser = argparse.ArgumentParser()
            parser.add_argument('-p', '--path', type=str, help='字幕路径，可以是文件夹或文件，用|隔开')
            parser.add_argument('-s', '--syncer', type=str, help='使用的同步程序，用|隔开')
            parser.add_argument('-om', '--order-mode', action='store_true',
                                help='顺序模式，字幕数需为视频的整数倍，且按文件名排序顺序一致')
            parser.add_argument('-rm', '--rename-mode', action='store_true', help='重命名字幕使其与视频一致')
            additional_info = 'additional information: 若命令行中未输入-p或--path则为窗口选择模式'
            parser.epilog = additional_info
            args = parser.parse_args()
            paths = args.path
            parser.print_help()
            print("__________________________________________________________________________________\n")
            if paths:
                paths = paths.split("|")
                is_order_mod = args.order_mode
                is_rename_mod = args.rename_mode
                for s in args.syncer.split("|"):
                    if 'alass' in s.lower():
                        is_alass_mod = True
                    if 'ffsubsync' in s.lower():
                        is_ffsubsync_mod = True

            else:
                files = []
                folders = []

                try:
                    select = tk.Tk()
                    select.title("请选择字幕")
                    select.geometry("350x350")
                    space = tk.Label(select, text=" ")
                    space.pack()
                    file_button = tk.Button(select, text="选择字幕文件", command=select_files)
                    file_button.pack()
                    space = tk.Label(select, text=" ")
                    space.pack()
                    folder_button = tk.Button(select, text="选择文件夹", command=select_folders)
                    folder_button.pack()
                    space = tk.Label(select, text=" ")
                    space.pack()
                    is_order_v = tk.IntVar()
                    is_rename_v = tk.IntVar()
                    is_alass_v = tk.IntVar()
                    is_alass_v.set(is_alass_mod)
                    is_ffsubsync_v = tk.IntVar()
                    is_ffsubsync_v.set(is_ffsubsync_mod)
                    tips = tk.Label(select, text="勾选顺序模式需保证视频和对应字幕按文件名排序顺序一致")
                    tips.pack()
                    is_order = tk.Checkbutton(select, text="顺序模式", variable=is_order_v, onvalue=1, offvalue=0)
                    is_order.pack()
                    is_rename = tk.Checkbutton(select, text="重命名字幕", variable=is_rename_v, onvalue=1, offvalue=0)
                    is_rename.pack()
                    space = tk.Label(select, text=" ")
                    space.pack()
                    tips = tk.Label(select, text="请选择要使用的字幕同步程序，可多选")
                    tips.pack()
                    is_alass = tk.Checkbutton(select, text="alass", variable=is_alass_v, onvalue=1, offvalue=0)
                    is_alass.pack()
                    if is_alass_mod:
                        is_alass.select()
                    is_ffsubsync = tk.Checkbutton(select, text="ffsubsync", variable=is_ffsubsync_v, onvalue=1, offvalue=0)
                    is_ffsubsync.pack()
                    if is_ffsubsync_mod:
                        is_ffsubsync.select()
                    ok_button = tk.Button(select, text="确认", command=lambda: edit_config(is_alass_v.get(), is_ffsubsync_v.get()))
                    ok_button.pack()
                    select.mainloop()
                    is_order_mod = is_order_v.get()
                    is_rename_mod = is_rename_v.get()
                    is_alass_mod = is_alass_v.get()
                    is_ffsubsync_mod = is_ffsubsync_v.get()
                    paths = files + folders
                except tk.TclError:
                    print('\n无法创建GUI界面，请使用命令行模式')
                    sys.exit(1)

                if not paths:
                    print('\n未输入有效路径或无字幕文件，程序退出...')
                    sys.exit(1)

        MatcherZH(paths, video_extensions, subs_extensions, is_order_mod, is_rename_mod, is_alass_mod, is_ffsubsync_mod).run()
    else:
        from core.matcher import MatcherEN

        if len(sys.argv) > 1 and '-p' not in sys.argv and '-h' not in sys.argv and '--path' not in sys.argv and '--help' not in sys.argv:
            paths = sys.argv[1:]
        else:
            print("_______________________________________________________________________________________________________________")
            print("\n1. Videos and subtitles should be in the same folder.")
            print("\n2. Subtitles that can't be matched will require manual selection during runtime.")
            print("\n3. alass, ffsubsync supported for now")
            print("_______________________________________________________________________________________________________________\n")

            parser = argparse.ArgumentParser()
            parser.add_argument('-p', '--path', type=str, help='subtitles or folders path, separated by |')
            parser.add_argument('-s', '--syncer', type=str, default="alass", help='choose syncer, separated by |')
            parser.add_argument('-om', '--order-mode', action='store_true',
                                help='subtitles must be an int multiple of videos and they are in the same order by filename')
            parser.add_argument('-rm', '--rename-mode', action='store_true', help='rename subtitles to be same as videos')
            additional_info = 'additional information: if no -p or --path entered in command line, will be window selection mode'
            parser.epilog = additional_info
            args = parser.parse_args()
            paths = args.path
            parser.print_help()
            print("_______________________________________________________________________________________________________________\n")

            if paths:
                paths = paths.split("|")
                is_order_mod = args.order_mode
                is_rename_mod = args.rename_mode

            else:
                files = []
                folders = []

                try:
                    select = tk.Tk()
                    select.title("Subtitles Selection")
                    select.geometry("800x350")
                    space = tk.Label(select, text=" ")
                    space.pack()
                    file_button = tk.Button(select, text="Select Subtitles", command=select_files)
                    file_button.pack()
                    space = tk.Label(select, text=" ")
                    space.pack()
                    folder_button = tk.Button(select, text="Select Folders", command=select_folders)
                    folder_button.pack()
                    space = tk.Label(select, text=" ")
                    space.pack()
                    is_order_v = tk.IntVar()
                    is_rename_v = tk.IntVar()
                    is_alass_v = tk.IntVar()
                    is_alass_v.set(is_alass_mod)
                    is_ffsubsync_v = tk.IntVar()
                    is_ffsubsync_v.set(is_ffsubsync_mod)
                    tips = tk.Label(select,
                                    text="Ensure subtitles must be an int multiple of videos and they are in the same order by filename before checking order mode")
                    tips.pack()
                    is_order = tk.Checkbutton(select, text="Order Mode", variable=is_order_v, onvalue=1, offvalue=0)
                    is_order.pack()
                    is_rename = tk.Checkbutton(select, text="Rename Subtitles", variable=is_rename_v, onvalue=1,
                                               offvalue=0)
                    is_rename.pack()
                    space = tk.Label(select, text=" ")
                    space.pack()
                    tips = tk.Label(select, text="Choose the syncers will be used")
                    tips.pack()
                    is_alass = tk.Checkbutton(select, text="alass", variable=is_alass_v, onvalue=1, offvalue=0)
                    is_alass.pack()
                    if is_alass_mod:
                        is_alass.select()
                    is_ffsubsync = tk.Checkbutton(select, text="ffsubsync", variable=is_ffsubsync_v, onvalue=1,
                                                  offvalue=0)
                    is_ffsubsync.pack()
                    if is_ffsubsync_mod:
                        is_ffsubsync.select()
                    ok_button = tk.Button(select, text="confirm",
                                          command=lambda: edit_config(is_alass_v.get(), is_ffsubsync_v.get()))
                    ok_button.pack()
                    select.mainloop()
                    is_order_mod = is_order_v.get()
                    is_rename_mod = is_rename_v.get()
                    is_alass_mod = is_alass_v.get()
                    is_ffsubsync_mod = is_ffsubsync_v.get()
                    paths = files + folders
                except tk.TclError:
                    print('\nUnable to create a GUI interface, please use command line mode')
                    sys.exit(1)

                if not paths:
                    print('\nNo valid path or no subtitles is selected, exiting...')
                    sys.exit(1)

        MatcherEN(paths, video_extensions, subs_extensions, is_order_mod, is_rename_mod, is_alass_mod, is_ffsubsync_mod).run()
