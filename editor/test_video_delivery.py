import json, subprocess, tempfile, unittest
from pathlib import Path
import imageio_ffmpeg
from verify_video import verify
class Delivery(unittest.TestCase):
 def test_missing_artifact_invalidates_stale_success(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'delivery.json').write_text('{}')
   with self.assertRaises(ValueError):verify(p)
   self.assertFalse((p/'delivery.json').exists())
 def test_full_and_missing_or_truncated_tracks(self):
  for video_seconds,audio_seconds,audio in [(1,1,'sine=frequency=440:sample_rate=24000'),(.5,1,'sine=frequency=440:sample_rate=24000'),(1,.5,'sine=frequency=440:sample_rate=24000'),(1,1,'anullsrc=r=24000:cl=mono'),(1,0,None)]:
   with self.subTest(video_seconds=video_seconds,audio_seconds=audio_seconds,audio=audio),tempfile.TemporaryDirectory() as d:
    p=Path(d);cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-f','lavfi','-i',f'color=c=blue:s=64x64:r=24:d={video_seconds}']
    if audio:cmd+=['-f','lavfi','-t',str(audio_seconds),'-i',audio]
    subprocess.run(cmd+['-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(p/'demo.mp4')],check=True)
    (p/'timeline.json').write_text(json.dumps([{'start':0,'end':1,'frames':24,'scene':{'chapter':'テスト'},'captions':[{'start':0,'end':1}]}]))
    (p/'subtitles.srt').write_text('1\n00:00:00,000 --> 00:00:01,000\nテスト\n')
    (p/'chapters.txt').write_text('00:00:00 テスト');(p/'CREDITS.txt').write_text('Generated test tone')
    if video_seconds==audio_seconds==1 and audio.startswith('sine'):
     self.assertEqual(verify(p)['status'],'verified')
     (p/'subtitles.srt').write_text('1\n00:00:00,000 --> 00:00:00,500\nテスト\n')
     with self.assertRaisesRegex(ValueError,'SRT'):verify(p)
     self.assertFalse((p/'delivery.json').exists())
     (p/'subtitles.srt').write_text('1\n00:00:00,000 --> 00:00:01,000\nテスト\n')
     (p/'chapters.txt').write_text('00:00:01 テスト')
     with self.assertRaisesRegex(ValueError,'章'):verify(p)
    else:
     with self.assertRaises(ValueError):verify(p)
     self.assertFalse((p/'delivery.json').exists())
if __name__=='__main__':unittest.main()
