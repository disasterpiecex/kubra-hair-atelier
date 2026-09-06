from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()
old="async function preview(){if(!photoUri||!shade)return;setBusy(true);setNotice('');try{const r=await generateHairPreview(photoUri,shade);setPreviewUri(r.previewDataUrl||photoUri);if(r.provider==='mock-local')setNotice('Live AI is not connected in this build yet. Your original photo is shown instead.');setScreen('preview')}catch(e:any){setPreviewUri(photoUri);setNotice(e?.message||'AI preview is currently unavailable.');setScreen('preview')}finally{setBusy(false)}}"
new="async function preview(){if(!photoUri||!shade)return;setBusy(true);setNotice('');setScreen('preview');try{const r=await generateHairPreview(photoUri,shade);setPreviewUri(r.previewDataUrl||photoUri);if(r.provider==='mock-local')setNotice('Live AI is not connected in this build yet. Your original photo is shown instead.')}catch(e:any){setPreviewUri(photoUri);setNotice(e?.message||'AI preview is currently unavailable.')}finally{setBusy(false)}}"
if old not in s:
    raise SystemExit('preview function shape not found for v1.7.1 patch')
s=s.replace(old,new,1)
p.write_text(s)
print('Applied v1.7.1 immediate preview navigation fix to',p)
