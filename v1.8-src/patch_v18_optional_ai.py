from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

old="catch(e:any){setPreviewUri(photoUri);setNotice(e?.message||'AI preview is currently unavailable.');nav('preview',true)}"
new="catch(e:any){setPreviewUri('');setNotice(e?.message||'AI preview is currently unavailable. No generated after-image has been created.');nav('preview',true)}"
if old not in s:
    raise SystemExit('v1.8 optional-AI preview catch target not found')
s=s.replace(old,new,1)

old_img="<View style={styles.v15CompareCard}><Image source={{uri:preview||source}} style={styles.v15Contain}/><View style={styles.v15ImageTag}><Text style={styles.v15ImageTagText}>{busy?'Generating…':'After'}</Text></View></View>"
new_img="<View style={styles.v15CompareCard}>{preview?<Image source={{uri:preview}} style={styles.v15Contain}/>:<View style={styles.v18NoPreview}><Text style={styles.v18NoPreviewTitle}>AI preview unavailable</Text><Text style={styles.v18NoPreviewText}>No generated image has been created. Your original photo is not being presented as an AI result.</Text></View>}<View style={styles.v15ImageTag}><Text style={styles.v15ImageTagText}>{busy?'Generating…':preview?'After':'No result'}</Text></View></View>"
if old_img not in s:
    raise SystemExit('v1.8 optional-AI after card target not found')
s=s.replace(old_img,new_img,1)

idx=s.rfind('});')
if idx<0:
    raise SystemExit('v1.8 optional-AI stylesheet target not found')
extra="  v18NoPreview:{flex:1,alignItems:'center',justifyContent:'center',padding:18,backgroundColor:C.paper},v18NoPreviewTitle:{fontFamily:'serif',fontSize:18,color:C.ink,textAlign:'center'},v18NoPreviewText:{fontSize:10.5,lineHeight:16,color:C.muted,textAlign:'center',marginTop:7},\n"
s=s[:idx]+extra+s[idx:]

p.write_text(s)
print('Applied v1.8 optional AI / no fake preview behavior to',p)
