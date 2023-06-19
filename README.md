# subsyncmatcher
    # Automaticlly match videos and subtitles for sync tools like alass and ffsubsync.
    # Supporting Windows, and possibly supporting Linux, I didn't test.
  # Usage 1
    # Download windows version from https://github.com/NullisNuer/subsyncmatcher/releases
    # if you want to use with ffsubsync:
        # install python
        pip install ffsubsync
  # Usage 2
    # install python
    pip install -r requirements.txt
    # Download ffmpeg from https://ffmpeg.org/
    # Add ffmpeg\bin to PATH
    # Put alass-cli.exe or alass-linux in subsyncmatcher\bin\
    python subsyncmatcher.py -h

![20230614000006](https://github.com/NullisNuer/subsyncmatcher/assets/135815308/a7f8a7bc-67fd-4f79-b542-b776c705d7fe)

![20230614000140](https://github.com/NullisNuer/subsyncmatcher/assets/135815308/0d944c8c-cf1b-488e-a553-2a1133734091)
  
  # Credits
    * https://github.com/kaegi/alass
    * https://github.com/dyphire/alass
    * https://github.com/smacke/ffsubsync
    * ffmpeg
    * ffprobe
    * All python libraries used
