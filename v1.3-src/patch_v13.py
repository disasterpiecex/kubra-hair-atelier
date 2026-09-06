from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

def block(start,end,replacement):
    global s
    a=s.index(start)
    b=s.index(end,a)
    s=s[:a]+replacement.rstrip()+'\n\n'+s[b:]

# Preserve full source image: no forced crop in either dimension.
s=s.replace("ImagePicker.launchImageLibraryAsync({quality:.92,allowsEditing:true,aspect:[3,4]})","ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:false})")
s=s.replace("ImagePicker.launchCameraAsync({quality:.92,allowsEditing:true,aspect:[3,4]})","ImagePicker.launchCameraAsync({quality:.95,allowsEditing:false})")

block('function PhotoScreen','function AdjustScreen',r'''function PhotoScreen({photoUri,pick,take,remove,next}:{photoUri:string;pick:()=>void;take:()=>void;remove:()=>void;next:()=>void}){
  return <View><TitleBlock eyebrow="TRY IT ON" title="Add your photo" copy="Choose the full frame. Kübra keeps the original width and height so your complete hair can stay visible."/>
    {photoUri?<View><View style={styles.photoStage}><Image key={photoUri} source={{uri:photoUri}} style={[styles.photo,styles.photoContain]}/><View style={styles.photoLabel}><Text style={styles.photoLabelText}>FULL FRAME</Text></View></View><Pressable onPress={remove} style={styles.removePhoto}><Text style={styles.removePhotoText}>Remove photo</Text></Pressable></View>
    :<View style={styles.photoEmpty}><View style={styles.faceIcon}><View style={styles.faceHead}/><View style={styles.faceShoulders}/></View><Text style={styles.photoEmptyTitle}>Your full photo becomes the canvas</Text><Text style={styles.photoEmptyCopy}>No forced 3:4 crop. Keep the complete width, height and full hair outline whenever possible.</Text></View>}
    <View style={styles.dual}><Pressable onPress={pick} style={styles.secondary}><Text style={styles.secondaryText}>Choose Photo</Text></Pressable><Pressable onPress={take} style={styles.secondary}><Text style={styles.secondaryText}>Take Photo</Text></Pressable></View>
    {photoUri?<View style={styles.cta}><Primary label="Continue →" onPress={next}/></View>:null}
  </View>
}''')

block('function AdjustScreen','function PreviewScreen',r'''function AdjustScreen({photoUri,shade,next}:{photoUri:string;shade?:Shade;next:()=>void}){
  return <View><TitleBlock eyebrow="ADJUST PHOTO" title="Frame your hair" copy="The source image is preserved. This screen only fits it inside the viewing area rather than cropping it."/>
    <View style={styles.adjustStage}><Image source={{uri:photoUri}} style={[styles.photo,styles.photoContain]}/><View style={styles.guideOval}/><View style={styles.guideTop}/><View style={styles.adjustTag}><View style={[styles.dot,{backgroundColor:shade?.hex||C.rose}]}/><Text style={styles.adjustTagText}>{shade?.name||'Selected shade'}</Text></View></View>
    <View style={styles.adjustHint}><Text style={styles.adjustHintTitle}>Full hair visible?</Text><Text style={styles.adjustHintText}>You can go back and choose another photo without affecting any results you already saved.</Text></View>
    <View style={styles.cta}><Primary label="Generate AI Preview →" onPress={next}/></View>
  </View>
}''')

block('function SavedScreen','function CompareScreen',r'''function SavedScreen({looks,selected,selecting,pendingDelete,onToggle,onCompare,onSelectMode,onOpen,onLongPress,onRemove}:{looks:SavedLook[];selected:string[];selecting:boolean;pendingDelete:string;onToggle:(id:string)=>void;onCompare:()=>void;onSelectMode:()=>void;onOpen:(look:SavedLook)=>void;onLongPress:(id:string)=>void;onRemove:(id:string)=>void}){
  return <View><TitleBlock eyebrow="YOUR PALETTE" title="Saved results" copy="Saved results stay here even if you remove or replace the current photo. Press and hold a result to remove it manually."/>
    {looks.length>=2?<View style={styles.savedActions}><Pressable onPress={onSelectMode} style={styles.outlineButton}><Text style={styles.outlineButtonText}>{selecting?'Done selecting':'Compare saved shades'}</Text></Pressable>{selecting?<Primary label={`Compare ${selected.length} →`} onPress={onCompare} disabled={selected.length<2}/>:null}</View>:null}
    {looks.length?<View style={styles.savedGrid}>{looks.map(look=>{const shade=shades.find(x=>x.id===look.shadeId);const on=selected.includes(look.id);const deleting=pendingDelete===look.id;return <Pressable key={look.id} onLongPress={()=>onLongPress(look.id)} delayLongPress={380} onPress={()=>selecting?onToggle(look.id):deleting?null:onOpen(look)} style={[styles.savedCard,on&&styles.savedCardOn]}><View style={styles.savedVisual}><Image source={{uri:look.previewUri}} style={styles.photo}/>{selecting?<View style={[styles.selectBadge,on&&styles.selectBadgeOn]}><Text style={[styles.selectBadgeText,on&&styles.selectBadgeTextOn]}>{on?'✓':'+'}</Text></View>:null}{deleting?<View style={styles.deleteShade}><Text style={styles.deleteHint}>Remove saved result?</Text><Pressable onPress={()=>onRemove(look.id)} style={styles.deleteButton}><Text style={styles.deleteButtonText}>Remove</Text></Pressable></View>:null}</View><Text style={styles.savedName}>{shade?.name||'Saved shade'}</Text><Text style={styles.savedMeta}>{shade?.family||''} · L{shade?.level||'—'}</Text></Pressable>})}</View>:<View style={styles.emptySaved}><Text style={styles.emptyHeart}>♡</Text><Text style={styles.emptyTitle}>Your palette is waiting</Text><Text style={styles.emptyCopy}>Save a generated result and it’ll remain here until you remove it yourself.</Text></View>}
  </View>
}''')

# Saved results are independent from active photo and gain explicit deletion state.
s=s.replace("  const [selectingSaved,setSelectingSaved]=useState(false);","  const [selectingSaved,setSelectingSaved]=useState(false);\n  const [pendingDeleteId,setPendingDeleteId]=useState('');")
s=s.replace("  const isSaved=!!(shade&&savedLooks.some(x=>x.shadeId===shade.id&&x.sourceUri===photoUri));","  function removeSavedLook(id:string){setSavedLooks(x=>x.filter(y=>y.id!==id));setSelectedSaved(x=>x.filter(y=>y!==id));setPendingDeleteId('')}\n  const isSaved=!!(shade&&savedLooks.some(x=>x.shadeId===shade.id&&x.sourceUri===photoUri));")
old=":screen==='saved'?<SavedScreen looks={savedLooks} selected={selectedSaved} selecting={selectingSaved} onToggle={id=>setSelectedSaved(x=>x.includes(id)?x.filter(y=>y!==id):[...x,id])} onCompare={()=>nav('compare',true)} onSelectMode={()=>{setSelectingSaved(x=>!x);setSelectedSaved([])}} onOpen={look=>{const sh=shades.find(x=>x.id===look.shadeId);if(sh){setFamilyId(sh.family);setShadeId(sh.id);setPhotoUri(look.sourceUri);setPreviewUri(look.previewUri);nav('preview',true)}}}/>"
new=":screen==='saved'?<SavedScreen looks={savedLooks} selected={selectedSaved} selecting={selectingSaved} pendingDelete={pendingDeleteId} onToggle={id=>setSelectedSaved(x=>x.includes(id)?x.filter(y=>y!==id):[...x,id])} onCompare={()=>nav('compare',true)} onSelectMode={()=>{setSelectingSaved(x=>!x);setSelectedSaved([]);setPendingDeleteId('')}} onLongPress={id=>setPendingDeleteId(id)} onRemove={removeSavedLook} onOpen={look=>{const sh=shades.find(x=>x.id===look.shadeId);if(sh){setFamilyId(sh.family);setShadeId(sh.id);setPhotoUri(look.sourceUri);setPreviewUri(look.previewUri);nav('preview',true)}}}/>"
if old not in s: raise SystemExit('SavedScreen call not found')
s=s.replace(old,new)

# Approved opening composition: real flowing-hair asset, centered wordmark, tagline, soft fade.
old_splash="if(showSplash)return <Animated.View style={[styles.splash,{opacity:splashOpacity}]}><StatusBar style=\"dark\"/><View style={styles.splashImage}><HairTexture base=\"#947463\" accent=\"#D7B8A9\"/><View style={styles.splashDark}/><View style={styles.splashLogo}><Wordmark large/></View></View><Text style={styles.splashTag}>BEAUTY LIVES IN YOUR SHADE</Text></Animated.View>;"
new_splash="if(showSplash)return <Animated.View style={[styles.splash,{opacity:splashOpacity}]}><StatusBar style=\"light\"/><View style={styles.splashImage}><Image source={require('./assets/opening-hair.jpg')} style={styles.splashHair}/><View style={styles.splashDark}/><View style={styles.splashLogo}><Wordmark large/></View></View><Text style={styles.splashTag}>BEAUTY LIVES IN YOUR SHADE</Text></Animated.View>;"
if old_splash not in s: raise SystemExit('splash block not found')
s=s.replace(old_splash,new_splash)

extra=r'''  photoContain:{resizeMode:'contain',backgroundColor:C.paper},splashHair:{position:'absolute',left:0,right:0,top:0,bottom:0,width:'100%',height:'100%',resizeMode:'cover'},
  deleteShade:{position:'absolute',left:8,right:8,bottom:8,backgroundColor:'rgba(49,35,30,.94)',borderRadius:14,padding:10,alignItems:'center'},deleteHint:{fontSize:9.5,color:'#FFF',marginBottom:7},deleteButton:{paddingHorizontal:18,paddingVertical:8,borderRadius:99,backgroundColor:C.paper},deleteButtonText:{fontSize:10,color:C.dark,fontWeight:'700'},
'''
idx=s.rfind('});')
s=s[:idx]+extra+s[idx:]
p.write_text(s)
print('Applied v1.3 patch to',p)
