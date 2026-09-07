"""Negative tests for positivity and the exact sharp polynomial identity."""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
from pathlib import Path
from fractions import Fraction
import tempfile,subprocess,shutil,json,sys
p=Path(__file__).resolve().parent.parent/'proofs'
for label,mutation in [
 ('negative reduced Gram diagonal',lambda c:c['reduced_gram'][0].__setitem__(0,'-1')),
 ('positive diagonal perturbation breaks exact identity',lambda c:c['reduced_gram'][0].__setitem__(0,str(Fraction(c['reduced_gram'][0][0])+Fraction(1,10**20))))]:
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);shutil.copy(p/'verify_sharp_qubit.py',d/'verify_sharp_qubit.py')
  c=json.loads((p/'sharp_qubit_certificate.json').read_text());mutation(c);(d/'sharp_qubit_certificate.json').write_text(json.dumps(c))
  r=subprocess.run([sys.executable,str(d/'verify_sharp_qubit.py')],capture_output=True,text=True)
  if r.returncode==0 or 'SHARP CERTIFICATE VALID' in r.stdout:raise SystemExit('FAIL '+label)
  if label.startswith('positive') and 'PASS 70x70' not in r.stdout:raise SystemExit('Did not isolate polynomial check')
  print('PASS rejected '+label,flush=True)
r=subprocess.run([sys.executable,'-O',str(p/'verify_sharp_qubit.py')],capture_output=True,text=True)
if r.returncode==0:raise SystemExit('FAIL optimized execution accepted')
print('PASS optimized execution rejected')
