from pathlib import Path
import re, sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

old_load="setFamilyId(x.familyId||'');setShadeId(x.shadeId||'');setPhotoUri(x.photoUri||'');setPreviewUri(x.previewUri||'');"
new_load="""setFamilyId(x.familyId||'');setShadeId(x.shadeId||'');setPhotoUri(x.photoUri||'');setPreviewUri(x.previewUri||'');setAnalysis(x.analysis||null);setFormula(x.formula||null);let restored=(['home','family','shade','photo','adjust','preview','saved','compare','more'].includes(x.screen)?x.screen:'home') as Screen;if((restored==='preview'||restored==='adjust')&&!x.photoUri)restored='photo';if((restored==='photo'||restored==='adjust'||restored==='preview')&&!x.shadeId)restored=x.familyId?'shade':'family';if(restored==='shade'&&!x.familyId)restored='family';setScreen(restored);"""
if old_load not in s:
    raise SystemExit('v1.8 exit-state hydration target not found')
s=s.replace(old_load,new_load,1)

old_effect="useEffect(()=>{if(!hydrated)return;AsyncStorage.setItem(SESSION,JSON.stringify({familyId,shadeId,photoUri,previewUri})).catch(()=>{})},[hydrated,familyId,shadeId,photoUri,previewUri]);"
new_effect="useEffect(()=>{if(!hydrated)return;AsyncStorage.setItem(SESSION,JSON.stringify({screen,familyId,shadeId,photoUri,previewUri,analysis,formula})).catch(()=>{})},[hydrated,screen,familyId,shadeId,photoUri,previewUri,analysis,formula]);"
if old_effect not in s:
    raise SystemExit('v1.8 exit-state session effect target not found')
s=s.replace(old_effect,new_effect,1)

s,n=re.subn(
    r"  async function writeSession\(nextPhoto:string,nextPreview:string\)\{[^\n]*\}\n",
    "  async function writeSession(nextPhoto:string,nextPreview:string,nextAnalysis:HairAnalysis|null=analysis,nextFormula:FormulaResult|null=formula,nextScreen:Screen=screen){if(!hydrated)return;await AsyncStorage.setItem(SESSION,JSON.stringify({screen:nextScreen,familyId,shadeId,photoUri:nextPhoto,previewUri:nextPreview,analysis:nextAnalysis,formula:nextFormula})).catch(()=>{})}\n",
    s,
    count=1,
)
if n!=1:
    raise SystemExit('v1.8 exit-state writeSession target not found')

s=s.replace("await writeSession('','');","await writeSession('','',null,null,screen);",1)
s=s.replace("await writeSession(durable,'');","await writeSession(durable,'',null,null,screen);")

s,n=re.subn(
    r"  function fullyExit\(\)\{[^\n]*\}",
    "  async function fullyExit(){setShowExit(false);if(hydrated){await AsyncStorage.multiSet([[SESSION,JSON.stringify({screen,familyId,shadeId,photoUri,previewUri,analysis,formula})],[SAVED,JSON.stringify(savedLooks)]]).catch(()=>{})}if(Platform.OS==='android'){const native=NativeModules.KubraExit;if(native?.exitApp){native.exitApp();return}BackHandler.exitApp()}}",
    s,
    count=1,
)
if n!=1:
    raise SystemExit('v1.8 exit-state fullyExit target not found')

p.write_text(s)
print('Applied v1.8 full exit-state persistence fix to',p)
