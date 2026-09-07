from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

old="next={()=>setScreen('adjust')}"
count=s.count(old)
if count==0:
    raise SystemExit("legacy adjust navigation target not found")

# The bug is only the first-tap route: Photo was still navigating to the legacy
# Adjust route, which renders another PhotoScreen. Replace that target directly
# with the existing preview handler and leave all preview logic unchanged.
s=s.replace(old,"next={preview}")

p.write_text(s)
print(f'Applied v1.7.2 direct Photo -> Preview route fix ({count} replacement(s)) to',p)
