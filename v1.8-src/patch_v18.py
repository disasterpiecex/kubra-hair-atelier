from pathlib import Path
import re, sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

def must_replace(old,new,count=1):
    global s
    if old not in s:
        raise SystemExit(f'v1.8 patch target not found: {old[:120]!r}')
    s=s.replace(old,new,count)

def block(start,end,replacement):
    global s
    a=s.find(start)
    if a<0: raise SystemExit(f'v1.8 block start not found: {start}')
    b=s.find(end,a)
    if b<0: raise SystemExit(f'v1.8 block end not found: {end}')
    s=s[:a]+replacement.rstrip()+'\n\n'+s[b:]

must_replace("import * as ImagePicker from 'expo-image-picker';", "import * as ImagePicker from 'expo-image-picker';\nimport * as ImageManipulator from 'expo-image-manipulator';\nimport * as FileSystem from 'expo-file-system/legacy';")
must_replace("import { generateHairPreview } from './api';", "import { analyzeHair, generateFormula, generateHairPreview, HairAnalysis, FormulaResult } from './api';")
must_replace("type SavedLook = { id:string; shadeId:string; previewUri:string; sourceUri:string; createdAt:number };", "type SavedLook = { id:string; shadeId:string; previewUri:string; sourceUri:string; createdAt:number; analysis?:HairAnalysis; formula?:FormulaResult };")
must_replace("const SESSION = 'kha:v1.2:session';\nconst SAVED = 'kha:v1.2:savedLooks';", "const SESSION = 'kha:v1.8:session';\nconst LEGACY_SESSION = 'kha:v1.2:session';\nconst SAVED = 'kha:v1.2:savedLooks';")

marker="const fill = { position:'absolute' as const, left:0, right:0, top:0, bottom:0 };"
helpers=r'''
const MEDIA_DIR = `${FileSystem.documentDirectory||''}kha-media/`;
async function ensureMediaDir(){if(!FileSystem.documentDirectory)throw new Error('Persistent app storage is unavailable.');await FileSystem.makeDirectoryAsync(MEDIA_DIR,{intermediates:true})}
function mediaExtension(uri:string){if(uri.startsWith('data:image/png'))return 'png';return uri.split('?')[0].toLowerCase().endsWith('.png')?'png':'jpg'}
async function persistImage(uri:string,prefix:string){
  if(!uri)return '';
  await ensureMediaDir();
  const ext=mediaExtension(uri);const dest=`${MEDIA_DIR}${prefix}-${Date.now()}-${Math.random().toString(36).slice(2,8)}.${ext}`;
  if(uri.startsWith('data:image/')){const comma=uri.indexOf(',');if(comma<0)throw new Error('Invalid generated image data.');await FileSystem.writeAsStringAsync(dest,uri.slice(comma+1),{encoding:FileSystem.EncodingType.Base64})}
  else if(/^https?:\/\//.test(uri))await FileSystem.downloadAsync(uri,dest);
  else await FileSystem.copyAsync({from:uri,to:dest});
  return dest;
}
async function safeDelete(uri:string){if(uri&&MEDIA_DIR&&uri.startsWith(MEDIA_DIR))await FileSystem.deleteAsync(uri,{idempotent:true}).catch(()=>{})}
'''
must_replace(marker,marker+'\n'+helpers)

block('function AdjustScreen','function PreviewScreen',r'''function AdjustScreen({photoUri,shade,onApply}:{photoUri:string;shade?:Shade;onApply:(uri:string)=>Promise<void>}){
  const [rotation,setRotation]=useState(0);const [zoom,setZoom]=useState(1);const [applying,setApplying]=useState(false);const [error,setError]=useState('');
  const zoomOut=()=>setZoom(x=>Math.max(1,Math.round((x-.1)*10)/10));const zoomIn=()=>setZoom(x=>Math.min(2,Math.round((x+.1)*10)/10));const fit=()=>setZoom(1);const reset=()=>{setRotation(0);setZoom(1);setError('')};
  async function apply(){
    if(applying)return;setApplying(true);setError('');
    try{
      const size=await new Promise<{width:number;height:number}>((resolve,reject)=>Image.getSize(photoUri,(width,height)=>resolve({width,height}),reject));
      const actions:any[]=[];if(rotation)actions.push({rotate:rotation});const rw=rotation%180?size.height:size.width;const rh=rotation%180?size.width:size.height;
      if(zoom>1.001){const width=Math.max(1,Math.floor(rw/zoom));const height=Math.max(1,Math.floor(rh/zoom));actions.push({crop:{originX:Math.max(0,Math.floor((rw-width)/2)),originY:Math.max(0,Math.floor((rh-height)/2)),width,height}})}
      const result=await ImageManipulator.manipulateAsync(photoUri,actions,{compress:.95,format:ImageManipulator.SaveFormat.JPEG});const durable=await persistImage(result.uri,'active-adjusted');await onApply(durable);
    }catch(e:any){setError(e?.message||'Could not apply the photo adjustment.');setApplying(false)}
  }
  return <View><View style={styles.v15CenterHead}><Text style={styles.v15Title}>Adjust Your Photo</Text><Text style={styles.v15SubCenter}>Rotate, zoom or return to the full frame. Your changes are applied before AI generation.</Text></View>
    <View style={styles.v18AdjustStage}><Image source={{uri:photoUri}} style={[styles.v18AdjustImage,{transform:[{rotate:`${rotation}deg`},{scale:zoom}]}]}/><View pointerEvents="none" style={styles.v18Frame}/><View style={styles.v18AdjustTag}><View style={[styles.v18Dot,{backgroundColor:shade?.hex||C.rose}]}/><Text style={styles.v18AdjustTagText}>{shade?.name||'Selected shade'}</Text></View></View>
    <View style={styles.v18EditorRow}><Pressable onPress={()=>setRotation(x=>(x+90)%360)} style={styles.v18EditorButton}><Text style={styles.v18EditorIcon}>↻</Text><Text style={styles.v18EditorLabel}>Rotate</Text></Pressable><Pressable onPress={zoomOut} style={styles.v18EditorButton}><Text style={styles.v18EditorIcon}>−</Text><Text style={styles.v18EditorLabel}>Zoom</Text></Pressable><View style={styles.v18ZoomReadout}><Text style={styles.v18ZoomText}>{Math.round(zoom*100)}%</Text></View><Pressable onPress={zoomIn} style={styles.v18EditorButton}><Text style={styles.v18EditorIcon}>+</Text><Text style={styles.v18EditorLabel}>Zoom</Text></Pressable><Pressable onPress={fit} style={styles.v18EditorButton}><Text style={styles.v18EditorIcon}>□</Text><Text style={styles.v18EditorLabel}>Fit</Text></Pressable></View>
    <Pressable onPress={reset} style={styles.v18Reset}><Text style={styles.v18ResetText}>Reset adjustments</Text></Pressable>{error?<View style={styles.notice}><Text style={styles.noticeText}>{error}</Text></View>:null}
    <Pressable disabled={applying} onPress={apply} style={[styles.v15Primary,applying&&{opacity:.55}]}><Text style={styles.v15PrimaryText}>{applying?'Applying…':'Use Photo & Generate  →'}</Text></Pressable>
  </View>
}''')

block('function PreviewScreen','function SavedScreen',r'''function PreviewScreen({source,preview,shade,notice,busy,retry,save,saved,analysis,formula,insightBusy,insightNotice}:{source:string;preview:string;shade?:Shade;notice:string;busy:boolean;retry:()=>void;save:()=>void;saved:boolean;analysis:HairAnalysis|null;formula:FormulaResult|null;insightBusy:boolean;insightNotice:string}){
  return <View><View style={styles.v15CenterHead}><Text style={styles.v15Title}>Your Preview</Text><Text style={styles.v15SubCenter}>Hair-only recoloring with your full framing preserved.</Text></View>
    <View style={styles.v15CompareRow}><View style={styles.v15CompareCard}><Image source={{uri:source}} style={styles.v15Contain}/><View style={styles.v15ImageTag}><Text style={styles.v15ImageTagText}>Before</Text></View></View><View style={styles.v15CompareCard}><Image source={{uri:preview||source}} style={styles.v15Contain}/><View style={styles.v15ImageTag}><Text style={styles.v15ImageTagText}>{busy?'Generating…':'After'}</Text></View></View></View>
    <View style={styles.v15ShadeSummary}><View style={[styles.v15Swatch,{backgroundColor:shade?.hex||C.taupe}]}/><View style={{flex:1}}><Text style={styles.v15SummaryTitle}>{shade?.level||'—'}.0 {shade?.name||'Your shade'}</Text><Text style={styles.v15SummarySub}>{shade?.tone||'Selected tone'} · {shade?.saturation||''}</Text></View><Text style={styles.v15SummaryHeart}>{saved?'♥':'♡'}</Text></View>
    {notice?<View style={styles.notice}><Text style={styles.noticeText}>{notice}</Text><Pressable onPress={retry}><Text style={styles.noticeLink}>{busy?'Generating…':'Try preview again'}</Text></Pressable></View>:null}
    <View style={styles.v18InsightCard}><Text style={styles.v18InsightKicker}>CURRENT HAIR ANALYSIS</Text>{analysis?<><View style={styles.v18MetricRow}><View style={styles.v18Metric}><Text style={styles.v18MetricValue}>L{analysis.currentLevel}</Text><Text style={styles.v18MetricLabel}>Estimated level</Text></View><View style={styles.v18Metric}><Text style={styles.v18MetricValue}>{analysis.undertone}</Text><Text style={styles.v18MetricLabel}>Undertone</Text></View></View><Text style={styles.v18InsightText}>Porosity: {analysis.porosity} · Condition: {analysis.condition}</Text><Text style={styles.v18InsightText}>Grey: ~{analysis.greyPercent}% · Confidence: {Math.round(analysis.confidence*100)}%</Text>{analysis.notes?.slice(0,3).map((x,i)=><Text key={i} style={styles.v18Bullet}>• {x}</Text>)}</>:<Text style={styles.v18InsightText}>{insightBusy?'Analyzing your current hair…':insightNotice||'Analysis will appear here when the AI service is connected.'}</Text>}</View>
    <View style={styles.v18InsightCard}><Text style={styles.v18InsightKicker}>COLOR ROUTE & FORMULA</Text>{formula?<><Text style={styles.v18FormulaTitle}>{formula.route}</Text><Text style={styles.v18InsightText}>{formula.mix}</Text><View style={styles.v18FormulaMeta}><Text style={styles.v18Pill}>{formula.liftRequired?'Lift required':'Deposit / tone'}</Text><Text style={styles.v18Pill}>{formula.developer}</Text></View>{formula.steps?.map((x,i)=><Text key={i} style={styles.v18Step}>{i+1}. {x}</Text>)}{formula.warnings?.map((x,i)=><Text key={`w${i}`} style={styles.v18Warning}>⚠ {x}</Text>)}</>:<Text style={styles.v18InsightText}>{insightBusy?'Building the color route…':insightNotice||'Formula guidance will appear after current-hair analysis.'}</Text>}</View>
    <Pressable disabled={!preview||busy} onPress={save} style={[styles.v15Primary,(!preview||busy)&&{opacity:.45}]}><Text style={styles.v15PrimaryText}>{saved?'♥ Saved permanently':'Save Result'}</Text></Pressable>
  </View>
}''')

must_replace("  const [busy,setBusy]=useState(false);", "  const [busy,setBusy]=useState(false);\n  const [hydrated,setHydrated]=useState(false);\n  const [analysis,setAnalysis]=useState<HairAnalysis|null>(null);\n  const [formula,setFormula]=useState<FormulaResult|null>(null);\n  const [insightBusy,setInsightBusy]=useState(false);\n  const [insightNotice,setInsightNotice]=useState('');")

old_effects="""  useEffect(()=>{(async()=>{try{const x=JSON.parse(await AsyncStorage.getItem(SESSION)||'{}');setFamilyId(x.familyId||'');setShadeId(x.shadeId||'');setPhotoUri(x.photoUri||'');setPreviewUri(x.previewUri||'');setSavedLooks(JSON.parse(await AsyncStorage.getItem(SAVED)||'[]'))}catch{}})()},[]);\n  useEffect(()=>{AsyncStorage.setItem(SESSION,JSON.stringify({familyId,shadeId,photoUri,previewUri})).catch(()=>{})},[familyId,shadeId,photoUri,previewUri]);\n  useEffect(()=>{AsyncStorage.setItem(SAVED,JSON.stringify(savedLooks)).catch(()=>{})},[savedLooks]);"""
new_effects="""  useEffect(()=>{(async()=>{try{const currentRaw=await AsyncStorage.getItem(SESSION);let x:any=currentRaw?JSON.parse(currentRaw):null;if(!x){const legacy=JSON.parse(await AsyncStorage.getItem(LEGACY_SESSION)||'{}');x={familyId:legacy.familyId||'',shadeId:legacy.shadeId||'',photoUri:'',previewUri:''};await AsyncStorage.setItem(SESSION,JSON.stringify(x))}setFamilyId(x.familyId||'');setShadeId(x.shadeId||'');setPhotoUri(x.photoUri||'');setPreviewUri(x.previewUri||'');const rawLooks=JSON.parse(await AsyncStorage.getItem(SAVED)||'[]') as SavedLook[];const migrated:SavedLook[]=[];for(const look of rawLooks){let sourceUri=look.sourceUri||'';let previewUri=look.previewUri||'';try{if(sourceUri&&!sourceUri.startsWith(MEDIA_DIR))sourceUri=await persistImage(sourceUri,'saved-source-migrated')}catch{}try{if(previewUri&&!previewUri.startsWith(MEDIA_DIR))previewUri=await persistImage(previewUri,'saved-preview-migrated')}catch{}migrated.push({...look,sourceUri,previewUri})}setSavedLooks(migrated);if(JSON.stringify(migrated)!==JSON.stringify(rawLooks))await AsyncStorage.setItem(SAVED,JSON.stringify(migrated))}catch{}finally{setHydrated(true)}})()},[]);\n  useEffect(()=>{if(!hydrated)return;AsyncStorage.setItem(SESSION,JSON.stringify({familyId,shadeId,photoUri,previewUri})).catch(()=>{})},[hydrated,familyId,shadeId,photoUri,previewUri]);\n  useEffect(()=>{if(!hydrated)return;AsyncStorage.setItem(SAVED,JSON.stringify(savedLooks)).catch(()=>{})},[hydrated,savedLooks]);"""
must_replace(old_effects,new_effects)

must_replace("  function chooseFamily(id:string){setFamilyId(id);setShadeId('');setPreviewUri('');setNotice('');setTimeout(()=>nav('shade',true),90)}", "  function chooseFamily(id:string){setFamilyId(id);setShadeId('');setPreviewUri('');setNotice('');setAnalysis(null);setFormula(null);setInsightNotice('');setTimeout(()=>nav('shade',true),90)}")
must_replace("  function chooseShade(id:string){setShadeId(id);setPreviewUri('');setNotice('');setTimeout(()=>nav('photo',true),90)}", "  function chooseShade(id:string){setShadeId(id);setPreviewUri('');setNotice('');setAnalysis(null);setFormula(null);setInsightNotice('');setTimeout(()=>nav('photo',true),90)}")

start="  function removePhoto(){setPhotoUri('');setPreviewUri('');setNotice('')}";end="  function fullyExit()";a=s.find(start);b=s.find(end,a)
if a<0 or b<0:raise SystemExit('v1.8 app media function block not found')
replacement=r'''  async function writeSession(nextPhoto:string,nextPreview:string){if(!hydrated)return;await AsyncStorage.setItem(SESSION,JSON.stringify({familyId,shadeId,photoUri:nextPhoto,previewUri:nextPreview})).catch(()=>{})}
  async function removePhoto(){const oldPhoto=photoUri,oldPreview=previewUri;setPhotoUri('');setPreviewUri('');setNotice('');setAnalysis(null);setFormula(null);setInsightNotice('');await writeSession('','');await safeDelete(oldPhoto);if(oldPreview!==oldPhoto)await safeDelete(oldPreview)}
  async function setNewActivePhoto(uri:string){const durable=await persistImage(uri,'active-photo');const oldPhoto=photoUri,oldPreview=previewUri;setPhotoUri(durable);setPreviewUri('');setNotice('');setAnalysis(null);setFormula(null);setInsightNotice('');await writeSession(durable,'');if(oldPhoto!==durable)await safeDelete(oldPhoto);if(oldPreview&&oldPreview!==oldPhoto)await safeDelete(oldPreview)}
  async function pick(){const r=await ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:false});if(!r.canceled&&r.assets?.[0]?.uri)await setNewActivePhoto(r.assets[0].uri)}
  async function take(){const p=await ImagePicker.requestCameraPermissionsAsync();if(!p.granted)return;const r=await ImagePicker.launchCameraAsync({quality:.95,allowsEditing:false});if(!r.canceled&&r.assets?.[0]?.uri)await setNewActivePhoto(r.assets[0].uri)}
  async function applyAdjusted(uri:string){const oldPhoto=photoUri,oldPreview=previewUri;setPhotoUri(uri);setPreviewUri('');setNotice('');setAnalysis(null);setFormula(null);setInsightNotice('');await writeSession(uri,'');if(oldPhoto!==uri)await safeDelete(oldPhoto);if(oldPreview&&oldPreview!==oldPhoto)await safeDelete(oldPreview);await preview(uri)}
  async function preview(sourceUri=photoUri){
    if(!sourceUri||!shade)return;nav('preview',true);setBusy(true);setInsightBusy(true);setNotice('');setInsightNotice('');setPreviewUri('');setAnalysis(null);setFormula(null);
    const [previewResult,analysisResult]=await Promise.allSettled([generateHairPreview(sourceUri,shade),analyzeHair(sourceUri)]);
    if(previewResult.status==='fulfilled'){try{const durable=await persistImage(previewResult.value.previewDataUrl,'active-preview');setPreviewUri(durable);await writeSession(sourceUri,durable)}catch(e:any){setNotice(e?.message||'The generated preview could not be saved locally.')}}else setNotice((previewResult.reason as any)?.message||'AI hair recoloring is currently unavailable.');
    if(analysisResult.status==='fulfilled'){setAnalysis(analysisResult.value);try{setFormula(await generateFormula(analysisResult.value,shade))}catch(e:any){setInsightNotice(e?.message||'Formula generation is currently unavailable.')}}else setInsightNotice((analysisResult.reason as any)?.message||'Current-hair analysis is currently unavailable.');
    setBusy(false);setInsightBusy(false);
  }
  async function saveCurrent(){if(!shade||!previewUri)return;if(savedLooks.some(x=>x.shadeId===shade.id&&x.sourceUri===photoUri))return;const sourceCopy=await persistImage(photoUri,'saved-source');const previewCopy=await persistImage(previewUri,'saved-preview');const look:SavedLook={id:`${shade.id}-${Date.now()}`,shadeId:shade.id,previewUri:previewCopy,sourceUri:sourceCopy,createdAt:Date.now(),analysis:analysis||undefined,formula:formula||undefined};const next=[look,...savedLooks];setSavedLooks(next);await AsyncStorage.setItem(SAVED,JSON.stringify(next))}
  async function removeSavedLook(id:string){const doomed=savedLooks.find(x=>x.id===id);const next=savedLooks.filter(x=>x.id!==id);setSavedLooks(next);setSelectedSaved(x=>x.filter(y=>y!==id));setPendingDeleteId('');await AsyncStorage.setItem(SAVED,JSON.stringify(next));if(doomed){await safeDelete(doomed.sourceUri);if(doomed.previewUri!==doomed.sourceUri)await safeDelete(doomed.previewUri)}}
  const isSaved=!!(shade&&savedLooks.some(x=>x.shadeId===shade.id&&x.sourceUri===photoUri));
'''
s=s[:a]+replacement+s[b:]

must_replace("    :screen==='photo'?<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={preview}/>\n    :screen==='adjust'?<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={preview}/>\n    :screen==='preview'?<PreviewScreen source={photoUri} preview={previewUri||photoUri} shade={shade} notice={notice} busy={busy} retry={preview} save={saveCurrent} saved={isSaved}/>", "    :screen==='photo'?<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={()=>nav('adjust',true)}/>\n    :screen==='adjust'?<AdjustScreen photoUri={photoUri} shade={shade} onApply={applyAdjusted}/>\n    :screen==='preview'?<PreviewScreen source={photoUri} preview={previewUri} shade={shade} notice={notice} busy={busy} retry={()=>preview()} save={saveCurrent} saved={isSaved} analysis={analysis} formula={formula} insightBusy={insightBusy} insightNotice={insightNotice}/>")
old_open="onOpen={look=>{const sh=shades.find(x=>x.id===look.shadeId);if(sh){setFamilyId(sh.family);setShadeId(sh.id);setPhotoUri(look.sourceUri);setPreviewUri(look.previewUri);nav('preview',true)}}}"
new_open="onOpen={async look=>{const sh=shades.find(x=>x.id===look.shadeId);if(sh){const activeSource=await persistImage(look.sourceUri,'active-from-saved');const activePreview=await persistImage(look.previewUri,'active-preview-from-saved');setFamilyId(sh.family);setShadeId(sh.id);setPhotoUri(activeSource);setPreviewUri(activePreview);setAnalysis(look.analysis||null);setFormula(look.formula||null);await AsyncStorage.setItem(SESSION,JSON.stringify({familyId:sh.family,shadeId:sh.id,photoUri:activeSource,previewUri:activePreview}));nav('preview',true)}}}"
must_replace(old_open,new_open)

idx=s.rfind('});')
if idx<0:raise SystemExit('StyleSheet end not found')
extra=r'''  v18AdjustStage:{height:410,borderRadius:22,overflow:'hidden',backgroundColor:'#E9E0D7',position:'relative',alignItems:'center',justifyContent:'center'},v18AdjustImage:{width:'100%',height:'100%',resizeMode:'contain'},v18Frame:{position:'absolute',left:22,right:22,top:24,bottom:24,borderWidth:1,borderColor:'rgba(255,255,255,.72)',borderRadius:18},v18AdjustTag:{position:'absolute',left:12,bottom:12,backgroundColor:'rgba(255,253,249,.94)',paddingHorizontal:11,paddingVertical:7,borderRadius:99,flexDirection:'row',alignItems:'center',gap:7},v18Dot:{width:9,height:9,borderRadius:5},v18AdjustTagText:{fontSize:9.5,color:C.dark,fontWeight:'600'},v18EditorRow:{flexDirection:'row',alignItems:'center',justifyContent:'space-between',marginTop:14,gap:6},v18EditorButton:{flex:1,minHeight:56,borderRadius:16,backgroundColor:C.paper,borderWidth:1,borderColor:C.line,alignItems:'center',justifyContent:'center'},v18EditorIcon:{fontSize:19,color:C.dark},v18EditorLabel:{fontSize:8.5,color:C.muted,marginTop:3},v18ZoomReadout:{width:50,alignItems:'center'},v18ZoomText:{fontSize:10.5,color:C.ink,fontWeight:'700'},v18Reset:{alignSelf:'center',paddingVertical:13,paddingHorizontal:18},v18ResetText:{fontSize:10.5,color:C.muted,textDecorationLine:'underline'},
  v18InsightCard:{marginTop:16,padding:18,borderRadius:20,backgroundColor:C.paper,borderWidth:1,borderColor:C.line},v18InsightKicker:{fontSize:8.5,letterSpacing:1.8,color:C.rose,fontWeight:'700',marginBottom:12},v18MetricRow:{flexDirection:'row',gap:10,marginBottom:10},v18Metric:{flex:1,padding:12,borderRadius:14,backgroundColor:C.paper2},v18MetricValue:{fontFamily:'serif',fontSize:17,color:C.ink,textTransform:'capitalize'},v18MetricLabel:{fontSize:8.5,color:C.muted,marginTop:3},v18InsightText:{fontSize:11,lineHeight:17,color:C.muted,marginTop:3},v18Bullet:{fontSize:10.5,lineHeight:16,color:C.ink,marginTop:5},v18FormulaTitle:{fontFamily:'serif',fontSize:20,lineHeight:24,color:C.ink,marginBottom:7},v18FormulaMeta:{flexDirection:'row',flexWrap:'wrap',gap:7,marginVertical:10},v18Pill:{fontSize:9.5,color:C.dark,backgroundColor:'#EFE6DD',paddingHorizontal:10,paddingVertical:7,borderRadius:99},v18Step:{fontSize:10.5,lineHeight:17,color:C.ink,marginTop:6},v18Warning:{fontSize:10,lineHeight:16,color:C.rose,marginTop:8},
'''
s=s[:idx]+extra+s[idx:]
p.write_text(s)
print('Applied v1.8 persistence, real editor, AI analysis/formula UI patch to',p)
