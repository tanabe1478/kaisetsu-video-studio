import copy, unittest
from PIL import ImageChops
import board_motion, presentation, server

def fixture():
    return {'title':'動き','speed':1,'scenes':[{'chapter':'説明','heading':'分類する',
        'narration':[{'text':'最初の説明','speech':'最初の説明'},{'text':'次の説明','speech':'次の説明'}],
        'boardAnimation':{'version':1,'intent':'物を左から右へ移す',
          'narration':['最初の説明','次の説明'],
          'elements':[{'id':'object','type':'box','text':'構造','frames':[
            {'line':1,'x':0,'y':30,'w':140,'h':60},
            {'line':2,'x':500,'y':30,'w':140,'h':60}]}]}}]}

class MotionTests(unittest.TestCase):
    def test_roundtrip_and_retiming_do_not_depend_on_voice_duration(self):
        p=fixture();presentation.validate_presentation(p)
        self.assertEqual(server.script(server.import_script(p)),p)
        e=p['scenes'][0]['boardAnimation']['elements'][0]
        self.assertEqual(board_motion.state(e,1.5)['x'],250)
        self.assertEqual(board_motion.state(e,2.5)['x'],500)
        self.assertEqual(board_motion.state(e,.5)['opacity'],0)

    def test_actual_frames_change_only_inside_board(self):
        p=fixture();s=p['scenes'][0]
        a=presentation.backdrop(p,s,motion_position=1)
        b=presentation.backdrop(p,s,motion_position=1.5)
        bounds=ImageChops.difference(a,b).getbbox()
        self.assertIsNotNone(bounds)
        self.assertGreaterEqual(bounds[0],290);self.assertLessEqual(bounds[2],990)
        self.assertGreaterEqual(bounds[1],220);self.assertLessEqual(bounds[3],500)
        self.assertIsNone(ImageChops.difference(b,presentation.backdrop(p,s,motion_position=1.5)).getbbox())

    def test_text_edit_or_reorder_requires_replanning_but_can_be_saved(self):
        p=fixture();p['scenes'][0]['narration'].reverse()
        presentation.validate_presentation(p)
        with self.assertRaisesRegex(ValueError,'再調整'):board_motion.validate_alignment(p['scenes'][0])

    def test_rejects_invalid_positions_references_and_nonfinite_values(self):
        base=fixture()['scenes'][0]['boardAnimation']
        for change in [{'x':690},{'line':9},{'opacity':float('nan')},{'at':-1}]:
            a=copy.deepcopy(base);a['elements'][0]['frames'][0].update(change)
            with self.assertRaises(ValueError):board_motion.validate(a)
        a=copy.deepcopy(base);a['elements'][0]['type']='javascript'
        with self.assertRaises(ValueError):board_motion.validate(a)

if __name__=='__main__':unittest.main()
