from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

old=":screen==='photo'?<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={()=>nav('adjust',true)}/>"
new=":screen==='photo'?<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={preview}/>"
if old not in s:
    raise SystemExit('confirmed v1.7 photo route shape not found')

s=s.replace(old,new,1)
p.write_text(s)
print('Applied v1.7.2 confirmed one-tap Photo -> Preview route fix to',p)
