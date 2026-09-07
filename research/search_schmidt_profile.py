"""Numerical fixed-Schmidt-parameter search; no certified upper bound."""
import sys as _sys

if _sys.flags.optimize:
    raise SystemExit("Run without -O: assertions in this file are certificate checks.")
import numpy as np
from scipy.optimize import minimize
from pathlib import Path
OUTPUT_DIR=Path(__file__).resolve().parent.parent/'build'
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

import json
from search_qubits import AC,BC,E
from search_qubits import evaluate
from scipy.optimize import differential_evolution
out=[]
for theta in np.linspace(0,np.pi/4,9):
 bounds=[(theta,theta),(0,np.pi),(0,0),(0,np.pi),(0,2*np.pi),(0,np.pi),(0,2*np.pi)]
 r=differential_evolution(lambda z:-evaluate(z,(0,0,0)),bounds,seed=702,popsize=18,maxiter=700,tol=1e-10,polish=True)
 out.append({'theta':float(theta),'value':float(-r.fun)})
 print(out[-1],flush=True)
(OUTPUT_DIR/'schmidt_profile.json').write_text(json.dumps(out,indent=2))
