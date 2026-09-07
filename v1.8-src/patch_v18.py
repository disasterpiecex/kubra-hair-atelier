from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()
print('===== V1.8 GENERATED APP START =====')
print(s)
print('===== V1.8 GENERATED APP END =====')
raise SystemExit('v1.8 source diagnostic complete; stopping before build')
