from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()
old="require('./assets/v15-opening.jpg')"
new="require('./assets/v17-opening.png')"
if old not in s:
    raise SystemExit('v1.5 splash asset reference not found')
s=s.replace(old,new,1)
p.write_text(s)
print('Applied v1.7 splash asset change only to',p)
