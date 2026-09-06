from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()
needle="async function preview(){if(!photoUri||!shade)return;"
if needle not in s:
    raise SystemExit('preview function entry not found for v1.7.1 patch')
replacement=needle+"setScreen('preview');"
s=s.replace(needle,replacement,1)
p.write_text(s)
print('Applied v1.7.1 immediate preview navigation fix to',p)
