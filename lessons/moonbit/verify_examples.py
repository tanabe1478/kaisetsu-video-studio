"""Run every lesson example and compare its stdout to the authored expectation."""
import json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
expected={3:'Hello, MoonBit!',4:'54',5:'4',6:'8.5\ntrue\nscore',7:'score = 9\n9',8:'13',9:'warm',10:'10',12:'6',13:'9\n4',14:'10\n5',15:'12',16:'2',17:'',18:'done',19:'0',20:'21\nhello',21:'9',22:'learner',23:'learner',24:'true\nfalse',25:'negative',26:'0',27:'0',28:'13'}
report=[]
for p in sorted((root/'examples').glob('*.mbtx')):
    r=subprocess.run(['moon','run',str(p),'--target','wasm-gc'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90)
    ok=r.returncode==0 and r.stdout.strip()==expected[int(p.stem)]
    report.append({'example':p.name,'passed':ok,'stdout':r.stdout.strip(),'diagnostics':r.stderr.replace(str(root),'<lesson>')})
    print(p.name,'PASS' if ok else 'FAIL',flush=True)
r=subprocess.run(['moon','test','--target','wasm-gc'],cwd=root/'checks',capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
report.append({'test_suite_passed':r.returncode==0,'stdout':r.stdout,'stderr':r.stderr.replace(str(root),'<lesson>')})
(root/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(r.stdout,r.stderr)
if not all(x.get('passed',x.get('test_suite_passed')) for x in report):raise SystemExit(1)
