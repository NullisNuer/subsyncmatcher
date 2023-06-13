import subprocess
import os
import re
import sys


def alass_cli(s_list, rename):
    for x in s_list:
        vid = x.vid.replace("/", "\\")
        sub = x.sub.replace("/", "\\")
        if rename:
            alass_args = [
                os.path.join("bin", "alass-cli").replace("/", "\\"),
                f'"{vid}"',
                f'"{sub}"',
                f'"{vid}.async.{x.extension}"'
            ]
            alass_command = ' '.join(alass_args)
        else:
            sync_path = os.path.join(x.folder, f'{x.filename}.async.{x.extension}').replace("/", "\\")
            alass_args = [
                os.path.join("bin", "alass-cli").replace("/", "\\"),
                f'"{vid}"',
                f'"{sub}"',
                f'"{sync_path}"'
            ]
            alass_command = ' '.join(alass_args)

        def run_command_with_progress(command):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True, encoding='utf8')
            progress_regex = re.compile(r'([\d.]+)\s%')
            log_pattern = r'[a-zA-Z]{2,}'
            log_path = os.path.join('log', f'alass.{x.filename}.txt')
            log = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    log.append(output)
                    progress_match = progress_regex.search(output)
                    if progress_match:
                        progress = float(progress_match.group(1))
                        print_progress_bar(progress)
            with open(log_path, 'w') as fd:
                count = 1
                for line in log:
                    match = re.match(log_pattern, line)
                    if match:
                        fd.write(f'{count}. {line}')
                        count += 1
            return process.poll()

        def print_progress_bar(progress, width=70):
            filled_width = int(width * progress / 100)
            bar = '>' * filled_width + '-' * (width - filled_width)
            sys.stdout.write(f'\r[{bar}] {progress}%')
            sys.stdout.flush()
        print(x.filename)
        run_command_with_progress(alass_command)
        print('\n')
