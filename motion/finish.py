"""Mux original speech and require the same full-delivery checks as studio.py."""
import sys,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import imageio_ffmpeg
from verify_video import verify
out=Path(sys.argv[1]).resolve()
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-n','-i',str(out/'silent.mp4'),'-i',str(out/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out/'demo.mp4')],check=True)
print(verify(out))
subprocess.run([sys.executable,str(Path(__file__).with_name('review_page.py')),str(out)],check=True)
