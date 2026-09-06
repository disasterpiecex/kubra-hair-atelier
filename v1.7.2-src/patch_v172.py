from pathlib import Path
import re, sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

# The actual bug is routing: the Photo screen can still send the first tap to the
# legacy 'adjust' route, which renders another PhotoScreen. That creates the
# apparent reload and requires a second tap. Fix only that route.
pattern=r"(:screen==='photo'\?<PhotoScreen\b[^>]*?\bnext=)\{(?:\(\)=>setScreen\('adjust'\)|preview)\}(/>)"
m=re.search(pattern,s)
if not m:
    raise SystemExit('photo route not found for v1.7.2 patch')
# Force the photo screen to call preview directly on its first tap.
s=s[:m.start()]+re.sub(r"\bnext=\{[^}]+\}","next={preview}",m.group(0),count=1)+s[m.end():]

# Do not modify preview() timing/state behavior. Keep v1.7 behavior intact.
p.write_text(s)
print('Applied v1.7.2 direct Photo -> Preview route fix to',p)
