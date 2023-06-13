import re
import os
import glob
import cn2an
import platform
import datetime

import tkinter as tk
from tkinter import filedialog
from difflib import SequenceMatcher

if platform.system():
    if platform.system().lower() == 'windows':
        from process.ffsubsync_win import ffsubsync_cli
        from process.alass_win import alass_cli
    else:
        from process.alass_linux import alass_cli
        from process.ffsubsync_linux import ffsubsync_cli
else:
    from process.alass_linux import alass_cli
    from process.ffsubsync_linux import ffsubsync_cli


class MatcherZH:
    def __init__(self, paths, video_extensions, subs_extensions, is_order_mod=None, is_rename_mod=None, is_alass_mod=None, is_ffsubsync_mod=None):
        self.paths = paths
        self.is_order_mod = is_order_mod
        self.is_rename_mod = is_rename_mod
        self.subs_extensions = subs_extensions
        self.video_extensions = video_extensions
        self.is_alass_mod = is_alass_mod
        self.is_ffsubsync_mod = is_ffsubsync_mod

    class Subtitle:
        def __init__(self, sub=None, vid=None, folder=None, filename=None, ep=None, year=None, season=None,
                     extension=None):
            self.sub = sub
            self.vid = vid
            self.season = season
            self.ep = ep
            self.year = year
            self.folder = folder
            self.filename = filename
            self.extension = extension

    @staticmethod
    def get_files(p, s_ext, v_ext):
        if os.path.isfile(p):
            s_files = [p]
            folder = os.path.dirname(p)
        else:
            folder = p
            s_files = []
            for ext in s_ext:
                s_files.extend(glob.glob(os.path.join(folder, f'*.{ext}')))

        v_files = []
        for ext in v_ext:
            v_files.extend(glob.glob(os.path.join(folder, f'*.{ext}')))
        return s_files, v_files, folder

    def order_mod(self, s_files, v_files, folder, s_ext):
        s_files = sorted(s_files)
        v_files = sorted(v_files)
        s_list = []
        if len(s_files) % len(v_files) == 0:
            pass
        else:
            print('\n字幕数量和视频数量不匹配，无法使用顺序模式')
            exit(1)
        multiple = int(len(s_files) / len(v_files))
        for s in s_files:
            filename, extension = self.match_subs(s, s_ext)
            s_list.append(self.Subtitle(
                sub=s,
                folder=folder,
                filename=filename,
                extension=extension
            ))
        s_list_group = {}
        for i in range(0, len(s_list), multiple):
            group = s_list[i:i+multiple]
            s_list_group.update({i: group})
        s_list = []
        for item, vd in zip(s_list_group.items(), v_files):
            for x in item[1]:
                x.vid = vd
                s_list.append(x)

        return s_list

    def add_item(self, s_files, v_files, folder, s_ext, v_ext):
        s_list = []
        nv_dict = {}
        for s in s_files:
            filename, extension = self.match_subs(s, s_ext)
            if filename:
                year = self.year_match(filename)
                season = self.season_match(filename)
                ep = self.ep_match(filename)
                video = self.match_videos(v_files, filename, year, season, ep, v_ext)
                if not video:
                    if filename not in nv_dict:

                        def select_video():
                            v = list(filedialog.askopenfilenames())
                            which_video.destroy()
                            if v:
                                return v[0]
                            return ''
                        try:
                            which_video = tk.Tk()
                            which_video.title("选择视频")
                            which_video.geometry("700x100")
                            w_space = tk.Label(which_video, text=" ")
                            w_space.pack()
                            w_tips = tk.Label(which_video, text=f"{filename}未匹配到视频，请选择，或点取消跳过")
                            w_tips.pack()
                            w_file_button = tk.Button(which_video, text="选择文件", command=select_video)
                            w_file_button.pack()
                            video = select_video()
                            which_video.mainloop()
                            if video:
                                nv_dict[filename] = video
                            else:
                                nv_dict[filename] = '跳过'
                        except tk.TclError:
                            nv_dict[filename] = '跳过'
                    else:
                        video = nv_dict[filename]

                if video:
                    s_list.append(self.Subtitle(
                        sub=s,
                        vid=video,
                        folder=folder,
                        filename=filename,
                        year=year,
                        season=season,
                        ep=ep,
                        extension=extension
                    ))

        return s_list, nv_dict

    @staticmethod
    def match_subs(sub, ext):
        ext_upper = [x.upper() for x in ext]
        pre_pattern = r'([\\/][^\\/]+)\.' + f'({"|".join(ext + ext_upper)})'
        pre_match = re.search(pre_pattern, sub)
        pattern = r'[\\/]([^\\/]+)\.' + f'({"|".join(ext + ext_upper)})'
        if not pre_match:
            return '', ''
        match = re.search(pattern, pre_match.group())
        if match:
            return match.group(1), match.group(2)
        return '', ''

    def match_videos(self, v_files, filename, year, season, ep, ext):
        ext_upper = [x.upper() for x in ext]
        pre_pattern = r'[\\/]([^\\/]+)\.' + f'({"|".join(ext + ext_upper)})'
        years = []
        for x in v_files:
            pre_match = re.search(pre_pattern, x)
            x_year = self.year_match(pre_match.group(1))
            if x_year:
                years.append(int(x_year))
        seasons = []
        for x in v_files:
            pre_match = re.search(pre_pattern, x)
            x_season = self.season_match(pre_match.group(1))
            if x_season:
                seasons.append(int(x_season))

        for v in v_files:
            pre_match = re.search(pre_pattern, v)
            match = pre_match.group(1)
            v_year = self.year_match(match)
            v_ep = self.ep_match(match)
            v_season = self.season_match(match)
            if len(v_files) == 1:
                return v
            elif filename == match:
                return v
            elif season and ep and v_season and v_ep:
                if int(season) == int(v_season) and float(ep) == float(v_ep):
                    return v
            elif season and ep and not v_season and v_ep:
                if float(ep) == float(v_ep) and int(season) not in seasons:
                    return v
            elif year and not season and ep and v_year and v_ep:
                if int(year) == int(v_year) and float(ep) == float(v_ep):
                    return v
            elif year and not season and ep and not v_year and v_ep:
                if float(ep) == float(v_ep) and int(year) not in years:
                    return v
            elif ep and not year and not season and not v_year and not v_season and v_ep:
                if float(ep) == float(v_ep):
                    return v
            elif ep and not year and not season and v_season and v_ep:
                if float(ep) == float(v_ep) and int(v_season) == 1:
                    return v
            elif ep and not year and not season and v_year and v_ep:
                if float(ep) == float(v_ep) and int(v_year) == min(years):
                    return v
            elif year and not season and not ep and v_year:
                if int(year) == int(v_year):
                    similarity = self.compute_similarity(match, filename, year)
                    if similarity >= 0.8:
                        return v
                    elif similarity < 0.8:
                        for x in v_files:
                            re_match = re.search(pre_pattern, x)
                            x_year = self.year_match(re_match.group(1))
                            if x_year:
                                similarity = self.compute_similarity(re_match.group(1), filename, year)
                                if int(x_year) == int(year) and similarity >= 0.8:
                                    v = x
                        return v
                    elif int(year) == int(v_year):
                        count = 0
                        for y in years:
                            if int(y) == int(year):
                                count += 1
                        if count == 1:
                            return v

    @staticmethod
    def ep_match(we):
        m_ep = ''
        match = re.search(r'(e|ep|episode)(\W|\.\s|)(\d{1,4}\.5)', we, flags=re.IGNORECASE)
        if match:
            m_ep = match.group(3)
        else:
            match = re.search(r'(e|ep|episode)(\W|\.\s|)(\d{1,4})', we, flags=re.IGNORECASE)
            if match:
                m_ep = match.group(3)
            else:
                match = re.search(
                    r'第(\d{1,4}\.5)[集话篇話編]',
                    we)
                if match:
                    m_ep = match.group(1)
                else:
                    match = re.search(
                        r'第([壹贰叁肆伍陆柒捌玖拾佰一二三四五六七八九十百零\d]{1,5})[集话篇話編]',
                        we)
                    if match:
                        try:
                            m_ep = str(int(cn2an.cn2an(match.group(1), "smart")))
                        except ValueError:
                            m_ep = ''.join(str(x) for x in map(ord, match.group(1)))
                    else:
                        match = re.search(
                            r'([上下前后後])[集话篇話編]',
                            we)
                        if match:
                            m_ep = ''.join(str(x) for x in map(ord, match.group(1)))
                        else:
                            match = re.search(
                                r'[\[{(（【_\s]([壹贰叁肆伍陆柒捌玖拾佰一二三四五六七八九十百零上下前后後]{1,5})[]})）】_\s]',
                                we)
                            if match:
                                try:
                                    m_ep = str(int(cn2an.cn2an(match.group(2), "smart")))
                                except ValueError:
                                    m_ep = ''.join(str(x) for x in map(ord, match.group(2)))
                            else:
                                match = re.match(r'\d+\.\d+', we)
                                if match:
                                    m_ep = match.group()
                                else:
                                    match = re.match(r'[壹贰叁肆伍陆柒捌玖拾佰一二三四五六七八九十百零\d]+', we)
                                    if match:
                                        m_ep = str(int(cn2an.cn2an(match.group(), "smart")))
                                    else:
                                        match = re.search(
                                            r'-\s(\d{1,4}\.5|\d{1,4})',
                                            we)
                                        if match:
                                            m_ep = match.group(1)
                                        else:
                                            match = re.findall(
                                                r'[\[{(（【_](\d{1,4}\.5|\d{1,4})[]})）】_]',
                                                we)
                                            if match:
                                                eps = []
                                                for m in match:
                                                    try:
                                                        fm = float(m)
                                                        if 1 < fm < 1888:
                                                            eps.append(fm)
                                                    except ValueError:
                                                        continue
                                                m_ep = str(min(eps))
        try:
            float(m_ep)
        except ValueError:
            return ''
        return m_ep

    @staticmethod
    def year_match(wy):
        m_year = ''
        match = re.findall(
            r'[^壹贰叁肆伍陆柒捌玖一二三四五六七八九零〇\d]([壹贰叁肆伍陆柒捌玖一二三四五六七八九零〇\d]{4})[^壹贰叁肆伍陆柒捌玖一二三四五六七八九零〇pP\d]',
            f'{wy}.')
        if match:
            years = []
            for m in match:
                if int(cn2an.cn2an(m, "smart")) >= 1888 and int(
                        cn2an.cn2an(m, "smart")) <= datetime.datetime.now().year:
                    years.append(int(cn2an.cn2an(m, "smart")))
            if years:
                m_year = str(years[0])

        return m_year

    @staticmethod
    def season_match(ws):
        m_season = ''
        match = re.search(r'(s|season|vol)(\W|\.\s|)(\d{1,3})', ws, flags=re.IGNORECASE)
        if match:
            m_season = match.group(3)
        else:
            match = re.search(r'第([壹贰叁肆伍陆柒捌玖拾佰一二三四五六七八九十百零\d]{1,5})[季巻卷]', ws)
            if match:
                m_season = str(int(cn2an.cn2an(match.group(1), "smart")))
        return m_season

    @staticmethod
    def compute_similarity(match, filename, year):
        filtered_match = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', match).replace(year, '').lower()
        filtered_filename = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', filename).replace(year, '').lower()
        if len(filtered_match) < 6 or len(filtered_filename) < 6:
            if len(filtered_match) > len(filtered_filename):
                return SequenceMatcher(None, filtered_match[:len(filtered_filename)], filtered_filename).ratio()
            else:
                return SequenceMatcher(None, filtered_match, filtered_filename[:len(filtered_match)]).ratio()
        else:
            return SequenceMatcher(None, filtered_match[:6], filtered_filename[:6]).ratio()

    def run(self):
        sub_list = []
        not_match_dict = {}
        for path in self.paths:
            a, b, c = self.get_files(path, self.subs_extensions, self.video_extensions)
            if self.is_order_mod:
                sub_list += self.order_mod(a, b, c, self.subs_extensions)
            else:
                d, e = self.add_item(a, b, c, self.subs_extensions, self.video_extensions)
                sub_list += d
                not_match_dict.update(e)
        print('\n待处理字幕：')
        for sl in sub_list:
            print(f'字幕：{sl.filename}\n视频：{sl.vid}\n年份{sl.year} 季数{sl.season} 集数{sl.ep} 格式{sl.extension}\n')
        print('\n')
        is_quit = input("请检查匹配列表，是否确认开始运行？(回车确认|输入q取消)")
        if is_quit == 'q' or is_quit == 'Q':
            exit(1)
        if self.is_alass_mod:
            alass_cli(sub_list, self.is_rename_mod)
        if self.is_ffsubsync_mod:
            try:
                ffsubsync_cli(sub_list, self.is_rename_mod)
            except FileNotFoundError:
                print("\n未找到ffsubsync，请先安装python和ffsubsync")
        print('\n本次运行手动选择视频或跳过的字幕：')
        for k, vl in not_match_dict.items():
            print(f'{k}：{vl}\n')


class MatcherEN:
    def __init__(self, paths, video_extensions, subs_extensions, is_order_mod=None, is_rename_mod=None, is_alass_mod=None, is_ffsubsync_mod=None):
        self.paths = paths
        self.is_order_mod = is_order_mod
        self.is_rename_mod = is_rename_mod
        self.subs_extensions = subs_extensions
        self.video_extensions = video_extensions
        self.is_alass_mod = is_alass_mod
        self.is_ffsubsync_mod = is_ffsubsync_mod

    class Subtitle:
        def __init__(self, sub=None, vid=None, folder=None, filename=None, ep=None, year=None, season=None,
                     extension=None):
            self.sub = sub
            self.vid = vid
            self.season = season
            self.ep = ep
            self.year = year
            self.folder = folder
            self.filename = filename
            self.extension = extension

    @staticmethod
    def get_files(p, s_ext, v_ext):
        if os.path.isfile(p):
            s_files = [p]
            folder = os.path.dirname(p)
        else:
            folder = p
            s_files = []
            for ext in s_ext:
                s_files.extend(glob.glob(os.path.join(folder, f'*.{ext}')))

        v_files = []
        for ext in v_ext:
            v_files.extend(glob.glob(os.path.join(folder, f'*.{ext}')))
        return s_files, v_files, folder

    def order_mod(self, s_files, v_files, folder, s_ext):
        s_files = sorted(s_files)
        v_files = sorted(v_files)
        s_list = []
        if len(s_files) % len(v_files) == 0:
            pass
        else:
            print("\nThe amount of subtitles doesn't match the amount of videos, can't use order mode.")
            exit(1)
        multiple = int(len(s_files) / len(v_files))
        for s in s_files:
            filename, extension = self.match_subs(s, s_ext)
            s_list.append(self.Subtitle(
                sub=s,
                folder=folder,
                filename=filename,
                extension=extension
            ))
        s_list_group = {}
        for i in range(0, len(s_list), multiple):
            group = s_list[i:i+multiple]
            s_list_group.update({i: group})
        s_list = []
        for item, vd in zip(s_list_group.items(), v_files):
            for x in item[1]:
                x.vid = vd
                s_list.append(x)

        return s_list

    def add_item(self, s_files, v_files, folder, s_ext, v_ext):
        s_list = []
        nv_dict = {}
        for s in s_files:
            filename, extension = self.match_subs(s, s_ext)
            if filename:
                year = self.year_match(filename)
                season = self.season_match(filename)
                ep = self.ep_match(filename)
                video = self.match_videos(v_files, filename, year, season, ep, v_ext)
                if not video:
                    if filename not in nv_dict:

                        def select_video():
                            v = list(filedialog.askopenfilenames())
                            which_video.destroy()
                            if v:
                                return v[0]
                            return ''
                        try:
                            which_video = tk.Tk()
                            which_video.title("Video Selection")
                            which_video.geometry("700x100")
                            w_space = tk.Label(which_video, text=" ")
                            w_space.pack()
                            w_tips = tk.Label(which_video,
                                              text=f"{filename}: No video matched, please select, or click cancel to skip")
                            w_tips.pack()
                            w_file_button = tk.Button(which_video, text="Select Video", command=select_video)
                            w_file_button.pack()
                            video = select_video()
                            which_video.mainloop()
                            if video:
                                nv_dict[filename] = video
                            else:
                                nv_dict[filename] = 'skip'
                        except tk.TclError:
                            nv_dict[filename] = 'skip'
                    else:
                        video = nv_dict[filename]

                if video:
                    s_list.append(self.Subtitle(
                        sub=s,
                        vid=video,
                        folder=folder,
                        filename=filename,
                        year=year,
                        season=season,
                        ep=ep,
                        extension=extension
                    ))

        return s_list, nv_dict

    @staticmethod
    def match_subs(sub, ext):
        ext_upper = [x.upper() for x in ext]
        pre_pattern = r'([\\/][^\\/]+)\.' + f'({"|".join(ext + ext_upper)})'
        pre_match = re.search(pre_pattern, sub)
        pattern = r'[\\/]([^\\/]+)\.' + f'({"|".join(ext + ext_upper)})'
        if not pre_match:
            return '', ''
        match = re.search(pattern, pre_match.group())
        if match:
            return match.group(1), match.group(2)
        return '', ''

    def match_videos(self, v_files, filename, year, season, ep, ext):
        ext_upper = [x.upper() for x in ext]
        pre_pattern = r'[\\/]([^\\/]+)\.' + f'({"|".join(ext + ext_upper)})'
        years = []
        for x in v_files:
            pre_match = re.search(pre_pattern, x)
            x_year = self.year_match(pre_match.group(1))
            if x_year:
                years.append(int(x_year))
        seasons = []
        for x in v_files:
            pre_match = re.search(pre_pattern, x)
            x_season = self.season_match(pre_match.group(1))
            if x_season:
                seasons.append(int(x_season))

        for v in v_files:
            pre_match = re.search(pre_pattern, v)
            match = pre_match.group(1)
            v_year = self.year_match(match)
            v_ep = self.ep_match(match)
            v_season = self.season_match(match)
            if len(v_files) == 1:
                return v
            elif filename == match:
                return v
            elif season and ep and v_season and v_ep:
                if int(season) == int(v_season) and float(ep) == float(v_ep):
                    return v
            elif season and ep and not v_season and v_ep:
                if float(ep) == float(v_ep) and int(season) not in seasons:
                    return v
            elif year and not season and ep and v_year and v_ep:
                if int(year) == int(v_year) and float(ep) == float(v_ep):
                    return v
            elif year and not season and ep and not v_year and v_ep:
                if float(ep) == float(v_ep) and int(year) not in years:
                    return v
            elif ep and not year and not season and not v_year and not v_season and v_ep:
                if float(ep) == float(v_ep):
                    return v
            elif ep and not year and not season and v_season and v_ep:
                if float(ep) == float(v_ep) and int(v_season) == 1:
                    return v
            elif ep and not year and not season and v_year and v_ep:
                if float(ep) == float(v_ep) and int(v_year) == min(years):
                    return v
            elif year and not season and not ep and v_year:
                if int(year) == int(v_year):
                    similarity = self.compute_similarity(match, filename, year)
                    if similarity >= 0.8:
                        return v
                    elif similarity < 0.8:
                        for x in v_files:
                            re_match = re.search(pre_pattern, x)
                            x_year = self.year_match(re_match.group(1))
                            if x_year:
                                similarity = self.compute_similarity(re_match.group(1), filename, year)
                                if int(x_year) == int(year) and similarity >= 0.8:
                                    v = x
                        return v
                    elif int(year) == int(v_year):
                        count = 0
                        for y in years:
                            if int(y) == int(year):
                                count += 1
                        if count == 1:
                            return v

    @staticmethod
    def ep_match(we):
        m_ep = ''
        match = re.search(r'(e|ep|episode)(\W|\.\s|)(\d{1,4}\.5)', we, flags=re.IGNORECASE)
        if match:
            m_ep = match.group(3)
        else:
            match = re.search(r'(e|ep|episode)(\W|\.\s|)(\d{1,4})', we, flags=re.IGNORECASE)
            if match:
                m_ep = match.group(3)
            else:
                match = re.search(
                    r'第(\d{1,4}\.5)[集话篇話編]',
                    we)
                if match:
                    m_ep = match.group(1)
                else:
                    match = re.search(
                        r'第([壹贰叁肆伍陆柒捌玖拾佰一二三四五六七八九十百零\d]{1,5})[集话篇話編]',
                        we)
                    if match:
                        try:
                            m_ep = str(int(cn2an.cn2an(match.group(1), "smart")))
                        except ValueError:
                            m_ep = ''.join(str(x) for x in map(ord, match.group(1)))
                    else:
                        match = re.search(
                            r'([上下前后後])[集话篇話編]',
                            we)
                        if match:
                            m_ep = ''.join(str(x) for x in map(ord, match.group(1)))
                        else:
                            match = re.search(
                                r'[\[{(（【_\s]([壹贰叁肆伍陆柒捌玖拾佰一二三四五六七八九十百零上下前后後]{1,5})[]})）】_\s]',
                                we)
                            if match:
                                try:
                                    m_ep = str(int(cn2an.cn2an(match.group(2), "smart")))
                                except ValueError:
                                    m_ep = ''.join(str(x) for x in map(ord, match.group(2)))
                            else:
                                match = re.match(r'\d+\.\d+', we)
                                if match:
                                    m_ep = match.group()
                                else:
                                    match = re.match(r'[壹贰叁肆伍陆柒捌玖拾佰一二三四五六七八九十百零\d]+', we)
                                    if match:
                                        m_ep = str(int(cn2an.cn2an(match.group(), "smart")))
                                    else:
                                        match = re.search(
                                            r'-\s(\d{1,4}\.5|\d{1,4})',
                                            we)
                                        if match:
                                            m_ep = match.group(1)
                                        else:
                                            match = re.findall(
                                                r'[\[{(（【_](\d{1,4}\.5|\d{1,4})[]})）】_]',
                                                we)
                                            if match:
                                                eps = []
                                                for m in match:
                                                    try:
                                                        fm = float(m)
                                                        if 1 < fm < 1888:
                                                            eps.append(fm)
                                                    except ValueError:
                                                        continue
                                                m_ep = str(min(eps))
        try:
            float(m_ep)
        except ValueError:
            return ''
        return m_ep

    @staticmethod
    def year_match(wy):
        m_year = ''
        match = re.findall(
            r'[^壹贰叁肆伍陆柒捌玖一二三四五六七八九零〇\d]([壹贰叁肆伍陆柒捌玖一二三四五六七八九零〇\d]{4})[^壹贰叁肆伍陆柒捌玖一二三四五六七八九零〇pP\d]',
            f'{wy}.')
        if match:
            years = []
            for m in match:
                if int(cn2an.cn2an(m, "smart")) >= 1888 and int(
                        cn2an.cn2an(m, "smart")) <= datetime.datetime.now().year:
                    years.append(int(cn2an.cn2an(m, "smart")))
            if years:
                m_year = str(years[0])

        return m_year

    @staticmethod
    def season_match(ws):
        m_season = ''
        match = re.search(r'(s|season|vol)(\W|\.\s|)(\d{1,3})', ws, flags=re.IGNORECASE)
        if match:
            m_season = match.group(3)
        else:
            match = re.search(r'第([壹贰叁肆伍陆柒捌玖拾佰一二三四五六七八九十百零\d]{1,5})[季巻卷]', ws)
            if match:
                m_season = str(int(cn2an.cn2an(match.group(1), "smart")))
        return m_season

    @staticmethod
    def compute_similarity(match, filename, year):
        filtered_match = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', match).replace(year, '').lower()
        filtered_filename = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', filename).replace(year, '').lower()
        if len(filtered_match) < 6 or len(filtered_filename) < 6:
            if len(filtered_match) > len(filtered_filename):
                return SequenceMatcher(None, filtered_match[:len(filtered_filename)], filtered_filename).ratio()
            else:
                return SequenceMatcher(None, filtered_match, filtered_filename[:len(filtered_match)]).ratio()
        else:
            return SequenceMatcher(None, filtered_match[:6], filtered_filename[:6]).ratio()

    def run(self):
        sub_list = []
        not_match_dict = {}
        for path in self.paths:
            a, b, c = self.get_files(path, self.subs_extensions, self.video_extensions)
            if self.is_order_mod:
                sub_list += self.order_mod(a, b, c, self.subs_extensions)
            else:
                d, e = self.add_item(a, b, c, self.subs_extensions, self.video_extensions)
                sub_list += d
                not_match_dict.update(e)
        print('\nPending list：')
        for sl in sub_list:
            print(
                f'Subtitles：{sl.filename}\nVideo：{sl.vid}\nYear {sl.year} Season {sl.season} Episode {sl.ep} Format {sl.extension}\n')
        print('\n')
        is_quit = input(
            "Please check the matching list, are you sure to start running? (Enter to confirm | Enter q to cancel)")
        if is_quit == 'q' or is_quit == 'Q':
            exit(1)
        if self.is_alass_mod:
            alass_cli(sub_list, self.is_rename_mod)
        if self.is_ffsubsync_mod:
            try:
                ffsubsync_cli(sub_list, self.is_rename_mod)
            except FileNotFoundError:
                print("\nffsubsync not found, please install python and ffsubsync first")
        print('\nManually selected videos or skipped subtitles for this run：')
        for k, vl in not_match_dict.items():
            print(f'{k}：{vl}\n')
