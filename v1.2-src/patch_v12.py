from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else 'App.tsx')
s = p.read_text()

def block(start, end, replacement):
    global s
    a = s.index(start)
    b = s.index(end, a)
    s = s[:a] + replacement.rstrip() + '\n\n' + s[b:]

s = s.replace("  Modal,\n  Platform,", "  Modal,\n  NativeModules,\n  Platform,")
s = s.replace("type Screen = 'home' | 'family' | 'shade' | 'photo' | 'adjust' | 'preview' | 'saved' | 'more';", "type Screen = 'home' | 'family' | 'shade' | 'photo' | 'adjust' | 'preview' | 'saved' | 'compare' | 'more';")
s = s.replace("type Shade = { id: string; family: string; name: string; hex: string; level: string; tone: string; saturation: string };", "type Shade = { id: string; family: string; name: string; hex: string; level: string; tone: string; saturation: string };\ntype SavedLook = { id:string; shadeId:string; previewUri:string; sourceUri:string; createdAt:number };")
s = s.replace("const SESSION = 'kha:v1.1.3:session';\nconst SAVED = 'kha:v1.1.3:saved';", "const SESSION = 'kha:v1.2:session';\nconst SAVED = 'kha:v1.2:savedLooks';")

block('function FamilyScreen', 'function ShadeScreen', r'''function FamilyScreen({selected,choose}:{selected:string;choose:(id:string)=>void}){
  return <View><TitleBlock eyebrow="COLOR INSPIRES YOU" title="Choose a color family" copy="Tap a family to continue to its shades."/>
    <View style={styles.familyGrid}>{families.map(f=>{const on=f.id===selected;return <Pressable key={f.id} onPress={()=>choose(f.id)} style={styles.familyItem}><View style={[styles.familyVisual,on&&styles.familyVisualOn]}><HairTexture base={f.color} accent={f.accent}/>{on?<View style={styles.check}><Text style={styles.checkText}>✓</Text></View>:null}</View><Text style={[styles.familyLabel,on&&styles.familyLabelOn]}>{f.name}</Text></Pressable>})}</View>
  </View>
}''')

block('function ShadeScreen', 'function PhotoScreen', r'''function ShadeScreen({family,list,selected,choose}:{family?:Family;list:Shade[];selected:string;choose:(id:string)=>void}){
  return <View><TitleBlock eyebrow="YOUR SHADE" title={`${family?.name||'Selected'} shades`} copy="Tap a shade to continue with your photo."/>
    <View style={styles.filterRow}><View style={styles.filterOn}><Text style={styles.filterOnText}>All</Text></View><View style={styles.filter}><Text style={styles.filterText}>Cool</Text></View><View style={styles.filter}><Text style={styles.filterText}>Warm</Text></View></View>
    <View style={styles.shadeGrid}>{list.map(x=>{const on=x.id===selected;return <Pressable key={x.id} onPress={()=>choose(x.id)} style={styles.shadeItem}><View style={[styles.shadeVisual,on&&styles.shadeVisualOn]}><HairTexture base={x.hex} accent="#F4E7DD"/>{on?<View style={styles.check}><Text style={styles.checkText}>✓</Text></View>:null}</View><Text numberOfLines={2} style={[styles.shadeName,on&&styles.shadeNameOn]}>{x.name}</Text><Text style={styles.shadeMeta}>L{x.level} · {x.tone}</Text></Pressable>})}</View>
  </View>
}''')

block('function PhotoScreen', 'function AdjustScreen', r'''function PhotoScreen({photoUri,pick,take,remove,next}:{photoUri:string;pick:()=>void;take:()=>void;remove:()=>void;next:()=>void}){
  return <View><TitleBlock eyebrow="TRY IT ON" title="Add your photo" copy="Use a clear, well-lit image with your hair fully visible."/>
    {photoUri?<View><View style={styles.photoStage}><Image key={photoUri} source={{uri:photoUri}} style={styles.photo}/><View style={styles.photoLabel}><Text style={styles.photoLabelText}>YOUR PHOTO</Text></View></View><Pressable onPress={remove} style={styles.removePhoto}><Text style={styles.removePhotoText}>Remove photo</Text></Pressable></View>
    :<View style={styles.photoEmpty}><View style={styles.faceIcon}><View style={styles.faceHead}/><View style={styles.faceShoulders}/></View><Text style={styles.photoEmptyTitle}>Your photo becomes the canvas</Text><Text style={styles.photoEmptyCopy}>A front-facing portrait gives the most natural preview.</Text></View>}
    <View style={styles.dual}><Pressable onPress={pick} style={styles.secondary}><Text style={styles.secondaryText}>Choose Photo</Text></Pressable><Pressable onPress={take} style={styles.secondary}><Text style={styles.secondaryText}>Take Photo</Text></Pressable></View>
    {photoUri?<View style={styles.cta}><Primary label="Continue →" onPress={next}/></View>:null}
  </View>
}''')

block('function PreviewScreen', 'function SavedScreen', r'''function PreviewScreen({source,preview,shade,notice,busy,retry,save,saved}:{source:string;preview:string;shade?:Shade;notice:string;busy:boolean;retry:()=>void;save:()=>void;saved:boolean}){
  return <View><TitleBlock eyebrow="YOUR RESULT" title="A glimpse of your next shade" copy="Compare your original with the generated result."/>
    <View style={styles.resultCard}><Image source={{uri:preview}} style={styles.resultImage}/><View style={styles.resultScrim}/><View style={styles.resultCopy}><Text style={styles.resultName}>{shade?.name||'Your shade'}</Text><Text style={styles.resultMeta}>LEVEL {shade?.level||'—'} · {(shade?.tone||'').toUpperCase()}</Text></View></View>
    <View style={styles.beforeAfter}><View style={styles.mini}><Image source={{uri:source}} style={styles.photo}/><Text style={styles.miniLabel}>BEFORE</Text></View><View style={styles.mini}><Image source={{uri:preview}} style={styles.photo}/><Text style={styles.miniLabel}>AFTER</Text></View></View>
    {notice?<View style={styles.notice}><Text style={styles.noticeTitle}>AI preview status</Text><Text style={styles.noticeText}>{notice}</Text><Pressable onPress={retry}><Text style={styles.noticeLink}>{busy?'Generating…':'Try again'}</Text></Pressable></View>:null}
    <View style={styles.cta}><Primary label={saved?'♥ Saved result':'♡ Save generated result'} onPress={save}/></View>
  </View>
}''')

block('function SavedScreen', 'function MoreScreen', r'''function SavedScreen({looks,selected,selecting,onToggle,onCompare,onSelectMode,onOpen}:{looks:SavedLook[];selected:string[];selecting:boolean;onToggle:(id:string)=>void;onCompare:()=>void;onSelectMode:()=>void;onOpen:(look:SavedLook)=>void}){
  return <View><TitleBlock eyebrow="YOUR PALETTE" title="Saved results" copy="Your generated hair previews, kept together for easy comparison."/>
    {looks.length>=2?<View style={styles.savedActions}><Pressable onPress={onSelectMode} style={styles.outlineButton}><Text style={styles.outlineButtonText}>{selecting?'Done selecting':'Compare saved shades'}</Text></Pressable>{selecting?<Primary label={`Compare ${selected.length} →`} onPress={onCompare} disabled={selected.length<2}/>:null}</View>:null}
    {looks.length?<View style={styles.savedGrid}>{looks.map(look=>{const shade=shades.find(x=>x.id===look.shadeId);const on=selected.includes(look.id);return <Pressable key={look.id} onPress={()=>selecting?onToggle(look.id):onOpen(look)} style={[styles.savedCard,on&&styles.savedCardOn]}><View style={styles.savedVisual}><Image source={{uri:look.previewUri}} style={styles.photo}/>{selecting?<View style={[styles.selectBadge,on&&styles.selectBadgeOn]}><Text style={[styles.selectBadgeText,on&&styles.selectBadgeTextOn]}>{on?'✓':'+'}</Text></View>:null}</View><Text style={styles.savedName}>{shade?.name||'Saved shade'}</Text><Text style={styles.savedMeta}>{shade?.family||''} · L{shade?.level||'—'}</Text></Pressable>})}</View>:<View style={styles.emptySaved}><Text style={styles.emptyHeart}>♡</Text><Text style={styles.emptyTitle}>Your palette is waiting</Text><Text style={styles.emptyCopy}>Save a generated result and it’ll appear here as a photo.</Text></View>}
  </View>
}

function CompareScreen({looks,onBack}:{looks:SavedLook[];onBack:()=>void}){
  return <View><TitleBlock eyebrow="SIDE BY SIDE" title="Compare saved shades" copy="See your generated results together on the same source photo."/><View style={styles.compareGrid}>{looks.map(look=>{const shade=shades.find(x=>x.id===look.shadeId);return <View key={look.id} style={styles.compareCard}><Image source={{uri:look.previewUri}} style={styles.compareImage}/><Text style={styles.compareName}>{shade?.name||'Saved shade'}</Text><Text style={styles.savedMeta}>L{shade?.level||'—'} · {shade?.tone||''}</Text></View>})}</View><View style={styles.cta}><Primary label="Back to saved" onPress={onBack}/></View></View>
}''')

app = r'''export default function App(){
  const [screen,setScreen]=useState<Screen>('home');
  const [familyId,setFamilyId]=useState('');
  const [shadeId,setShadeId]=useState('');
  const [photoUri,setPhotoUri]=useState('');
  const [previewUri,setPreviewUri]=useState('');
  const [savedLooks,setSavedLooks]=useState<SavedLook[]>([]);
  const [selectedSaved,setSelectedSaved]=useState<string[]>([]);
  const [selectingSaved,setSelectingSaved]=useState(false);
  const [showExit,setShowExit]=useState(false);
  const [showSplash,setShowSplash]=useState(true);
  const [notice,setNotice]=useState('');
  const [busy,setBusy]=useState(false);
  const splashOpacity=useRef(new Animated.Value(1)).current;
  const sceneOpacity=useRef(new Animated.Value(1)).current;
  const sceneX=useRef(new Animated.Value(0)).current;
  const direction=useRef(1);

  const family=useMemo(()=>families.find(x=>x.id===familyId),[familyId]);
  const shade=useMemo(()=>shades.find(x=>x.id===shadeId),[shadeId]);
  const familyShades=useMemo(()=>shades.filter(x=>x.family===familyId),[familyId]);
  const comparedLooks=useMemo(()=>savedLooks.filter(x=>selectedSaved.includes(x.id)),[savedLooks,selectedSaved]);

  useEffect(()=>{(async()=>{try{const x=JSON.parse(await AsyncStorage.getItem(SESSION)||'{}');setFamilyId(x.familyId||'');setShadeId(x.shadeId||'');setPhotoUri(x.photoUri||'');setPreviewUri(x.previewUri||'');setSavedLooks(JSON.parse(await AsyncStorage.getItem(SAVED)||'[]'))}catch{}})()},[]);
  useEffect(()=>{AsyncStorage.setItem(SESSION,JSON.stringify({familyId,shadeId,photoUri,previewUri})).catch(()=>{})},[familyId,shadeId,photoUri,previewUri]);
  useEffect(()=>{AsyncStorage.setItem(SAVED,JSON.stringify(savedLooks)).catch(()=>{})},[savedLooks]);
  useEffect(()=>{const t=setTimeout(()=>Animated.timing(splashOpacity,{toValue:0,duration:420,useNativeDriver:true}).start(()=>setShowSplash(false)),1100);return()=>clearTimeout(t)},[splashOpacity]);
  useEffect(()=>{sceneOpacity.setValue(.45);sceneX.setValue(direction.current*16);Animated.parallel([Animated.timing(sceneOpacity,{toValue:1,duration:190,useNativeDriver:true}),Animated.timing(sceneX,{toValue:0,duration:190,useNativeDriver:true})]).start()},[screen]);
  useEffect(()=>{if(Platform.OS!=='android')return;const sub=BackHandler.addEventListener('hardwareBackPress',()=>{if(showExit){setShowExit(false);return true}if(screen==='home'){setShowExit(true);return true}goBack();return true});return()=>sub.remove()},[screen,showExit]);

  function nav(x:Screen,forward=true){direction.current=forward?1:-1;setScreen(x)}
  function goBack(){const p:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',adjust:'photo',preview:'adjust',saved:'home',compare:'saved',more:'home'};nav(p[screen],false)}
  function chooseFamily(id:string){setFamilyId(id);setShadeId('');setPreviewUri('');setNotice('');setTimeout(()=>nav('shade',true),90)}
  function chooseShade(id:string){setShadeId(id);setPreviewUri('');setNotice('');setTimeout(()=>nav('photo',true),90)}
  function removePhoto(){setPhotoUri('');setPreviewUri('');setNotice('')}
  async function pick(){const r=await ImagePicker.launchImageLibraryAsync({quality:.92,allowsEditing:true,aspect:[3,4]});if(!r.canceled&&r.assets?.[0]?.uri){setPhotoUri(r.assets[0].uri);setPreviewUri('');setNotice('')}}
  async function take(){const p=await ImagePicker.requestCameraPermissionsAsync();if(!p.granted)return;const r=await ImagePicker.launchCameraAsync({quality:.92,allowsEditing:true,aspect:[3,4]});if(!r.canceled&&r.assets?.[0]?.uri){setPhotoUri(r.assets[0].uri);setPreviewUri('');setNotice('')}}
  async function preview(){if(!photoUri||!shade)return;setBusy(true);setNotice('');try{const r=await generateHairPreview(photoUri,shade);setPreviewUri(r.previewDataUrl||photoUri);if(r.provider==='mock-local')setNotice('Live AI is not connected in this build yet. Your original photo is shown instead.');nav('preview',true)}catch(e:any){setPreviewUri(photoUri);setNotice(e?.message||'AI preview is currently unavailable.');nav('preview',true)}finally{setBusy(false)}}
  function saveCurrent(){if(!shade||!previewUri)return;setSavedLooks(prev=>{const old=prev.find(x=>x.shadeId===shade.id&&x.sourceUri===photoUri);if(old)return prev.filter(x=>x.id!==old.id);return [{id:`${shade.id}-${Date.now()}`,shadeId:shade.id,previewUri,sourceUri:photoUri,createdAt:Date.now()},...prev]})}
  const isSaved=!!(shade&&savedLooks.some(x=>x.shadeId===shade.id&&x.sourceUri===photoUri));
  function fullyExit(){setShowExit(false);if(Platform.OS==='android'){const native=NativeModules.KubraExit;if(native?.exitApp){native.exitApp();return}BackHandler.exitApp()}}

  if(showSplash)return <Animated.View style={[styles.splash,{opacity:splashOpacity}]}><StatusBar style="dark"/><View style={styles.splashImage}><HairTexture base="#947463" accent="#D7B8A9"/><View style={styles.splashDark}/><View style={styles.splashLogo}><Wordmark large/></View></View><Text style={styles.splashTag}>BEAUTY LIVES IN YOUR SHADE</Text></Animated.View>;

  const body=screen==='home'?<Home go={x=>nav(x,true)}/>
    :screen==='family'?<FamilyScreen selected={familyId} choose={chooseFamily}/>
    :screen==='shade'?<ShadeScreen family={family} list={familyShades} selected={shadeId} choose={chooseShade}/>
    :screen==='photo'?<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={()=>nav('adjust',true)}/>
    :screen==='adjust'?<AdjustScreen photoUri={photoUri} shade={shade} next={preview}/>
    :screen==='preview'?<PreviewScreen source={photoUri} preview={previewUri||photoUri} shade={shade} notice={notice} busy={busy} retry={preview} save={saveCurrent} saved={isSaved}/>
    :screen==='saved'?<SavedScreen looks={savedLooks} selected={selectedSaved} selecting={selectingSaved} onToggle={id=>setSelectedSaved(x=>x.includes(id)?x.filter(y=>y!==id):[...x,id])} onCompare={()=>nav('compare',true)} onSelectMode={()=>{setSelectingSaved(x=>!x);setSelectedSaved([])}} onOpen={look=>{const sh=shades.find(x=>x.id===look.shadeId);if(sh){setFamilyId(sh.family);setShadeId(sh.id);setPhotoUri(look.sourceUri);setPreviewUri(look.previewUri);nav('preview',true)}}}/>
    :screen==='compare'?<CompareScreen looks={comparedLooks} onBack={()=>nav('saved',false)}/>
    :<MoreScreen/>;

  return <View style={styles.app}><StatusBar style="dark"/><View style={styles.statusSpace}/>{screen!=='home'?<TopBar onBack={goBack} onSaved={()=>nav('saved',true)}/>:null}<ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={[styles.scroll,screen==='home'&&styles.scrollHome]}><Animated.View style={{opacity:sceneOpacity,transform:[{translateX:sceneX}]}}>{body}</Animated.View></ScrollView><BottomNav screen={screen} onGo={x=>nav(x,true)}/>
    <Modal transparent visible={showExit} animationType="fade" onRequestClose={()=>setShowExit(false)}><View style={styles.modalBack}><View style={styles.exitCard}><View style={styles.exitGlyph}><Text style={styles.exitGlyphText}>〰</Text></View><Text style={styles.exitTitle}>Leave Kübra Hair Atelier?</Text><Text style={styles.exitCopy}>Your progress will be saved, so you can always come back.</Text><View style={styles.exitButtons}><Pressable onPress={()=>setShowExit(false)} style={styles.stay}><Text style={styles.stayText}>Stay</Text></Pressable><Pressable onPress={fullyExit} style={styles.exit}><Text style={styles.exitText}>Exit</Text></Pressable></View><Text style={styles.exitTag}>BEAUTY LIVES IN YOUR SHADE</Text></View></View></Modal>
  </View>
}'''
block('export default function App(){', 'const styles=StyleSheet.create({', app)

extra = r'''  removePhoto:{alignSelf:'flex-end',paddingVertical:10,paddingHorizontal:3},removePhotoText:{fontSize:11,color:C.rose,fontWeight:'700'},
  savedActions:{gap:10,marginBottom:18},outlineButton:{height:50,borderRadius:18,borderWidth:1,borderColor:C.champagne,backgroundColor:C.paper,alignItems:'center',justifyContent:'center'},outlineButtonText:{fontSize:11.5,color:C.dark,fontWeight:'700'},savedCardOn:{borderColor:C.dark,borderWidth:2},selectBadge:{position:'absolute',right:8,top:8,width:28,height:28,borderRadius:14,backgroundColor:'rgba(255,253,249,.92)',alignItems:'center',justifyContent:'center'},selectBadgeOn:{backgroundColor:C.dark},selectBadgeText:{color:C.dark,fontWeight:'700'},selectBadgeTextOn:{color:'#FFF'},
  compareGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:14},compareCard:{width:'48.4%',backgroundColor:C.paper,borderRadius:22,padding:8,borderWidth:1,borderColor:C.line},compareImage:{width:'100%',aspectRatio:.82,borderRadius:16,resizeMode:'cover'},compareName:{fontFamily:'serif',fontSize:16,color:C.ink,marginTop:10},
'''
idx = s.rfind('});')
s = s[:idx] + extra + s[idx:]
p.write_text(s)
print('Applied v1.2 patch to', p)
