from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

for marker in ['function PhotoScreen','async function preview','const body']:
    i=s.find(marker)
    print('\n===== DIAGNOSTIC:', marker, 'at', i, '=====')
    if i >= 0:
        print(s[i:i+5000])

raise SystemExit('v1.7.2 diagnostic dump complete; stopping before build')
