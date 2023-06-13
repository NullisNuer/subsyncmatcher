import subprocess
import os
import sys


def ffsubsync_cli(s_list, rename):
    for x in s_list:
        vid = x.vid.replace("/", "\\")
        sub = x.sub.replace("/", "\\")
        if rename:
            ffsubsync_args = [
                'ffsubsync',
                f'"{vid}"',
                '-i', f'"{sub}"',
                '-o', f'"{vid}.fsync.{x.extension}"'
            ]
            ffsubsync_command = ' '.join(ffsubsync_args)
        else:
            sync_path = os.path.join(x.folder, f'{x.filename}.fsync.{x.extension}').replace("/", "\\")
            ffsubsync_args = [
                'ffsubsync',
                f'"{vid}"',
                '-i', f'"{sub}"',
                '-o', f'"{sync_path}"'
            ]
            ffsubsync_command = ' '.join(ffsubsync_args)

        def run_command_with_progress(command):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            log_path = os.path.join('log', f'ffsubsync.{x.filename}.txt')
            log = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    sys.stdout.write(output)
                    log.append(output)
            with open(log_path, 'w') as fd:
                for line in log:
                    fd.write(line)
            return process.poll()

        print(x.filename)
        run_command_with_progress(ffsubsync_command)
        print('\n')
