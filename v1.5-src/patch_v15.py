from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

def block(start,end,replacement):
    global s
    a=s.index(start)
    b=s.index(end,a)
    s=s[:a]+replacement.rstrip()+'\n\n'+s[b:]

PHOTO_BLONDE='https://images.unsplash.com/photo-1566407031110-dd0e2a148b2d?auto=format&fit=crop&fm=jpg&q=82&w=1200'
PHOTO_BROWN='https://images.unsplash.com/photo-1549412817-58f9893ebeb1?auto=format&fit=crop&fm=jpg&q=82&w=1200'
PHOTO_RED='https://images.unsplash.com/photo-1716010168978-00b1b013c1ac?auto=format&fit=crop&fm=jpg&q=82&w=1200'

# No forced crop in system picker. The full selected frame is preserved.
s=s.replace('ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:true})','ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:false})')
s=s.replace('ImagePicker.launchCameraAsync({quality:.95,allowsEditing:true})','ImagePicker.launchCameraAsync({quality:.95,allowsEditing:false})')

# Shared photographic helpers.
insert="""
const V15_PHOTOS={
  blonde:{uri:'%s'}, brown:{uri:'%s'}, red:{uri:'%s'}, copper:{uri:'%s'}, black:{uri:'%s'},
  blue:{uri:'%s'}, pink:{uri:'%s'}, violet:{uri:'%s'}, green:{uri:'%s'}, grey:{uri:'%s'}, pastel:{uri:'%s'}
};
function V15Photo({family='blonde',style}:{family?:string;style?:any}){return <Image source={(V15_PHOTOS as any)[family]||V15_PHOTOS.blonde} style={[styles.v15Photo,style]}/>}
"""%(PHOTO_BLONDE,PHOTO_BROWN,PHOTO_RED,PHOTO_RED,PHOTO_BROWN,PHOTO_BROWN,PHOTO_RED,PHOTO_RED,PHOTO_BROWN,PHOTO_BROWN,PHOTO_RED)
marker='function Wordmark'
s=s.replace(marker,insert+'\n'+marker,1)

block('function Home','function FamilyScreen',r'''function Home({go}:{go:(s:Screen)=>void}){
  return <View style={styles.v15Home}>
    <View style={styles.v15HomeHead}><Wordmark/><Text style={styles.v15Heart}>♡</Text></View>
    <Text style={styles.v15HomeTitle}>Your Hair.{`\n`}A New Story.</Text>
    <Text style={styles.v15HomeCopy}>Explore, try, and find the shade that feels like you.</Text>
    <Pressable onPress={()=>go('family')} style={styles.v15Primary}><Text style={styles.v15PrimaryText}>Get Started  →</Text></Pressable>
    <Pressable onPress={()=>go('family')} style={styles.v15HomePhoto}><V15Photo family="blonde"/><View style={styles.v15PhotoScrim}/><Text style={styles.v15HomePhotoText}>Explore Shades</Text></Pressable>
    <View style={styles.v15QuickRow}>
      <Pressable onPress={()=>go('photo')} style={styles.v15Quick}><Text style={styles.v15QuickKicker}>TRY IT</Text><Text style={styles.v15QuickTitle}>Use Your Photo</Text></Pressable>
      <Pressable onPress={()=>go('saved')} style={styles.v15Quick}><Text style={styles.v15QuickKicker}>YOUR PALETTE</Text><Text style={styles.v15QuickTitle}>Saved Shades</Text></Pressable>
    </View>
  </View>
}''')

block('function FamilyScreen','function ShadeScreen',r'''function FamilyScreen({selected,choose}:{selected:string;choose:(id:string)=>void}){
  const shown=families.filter(f=>['blonde','brown','red','black','pink'].includes(f.id));
  return <View>
    <Text style={styles.v15Title}>Color Families</Text><Text style={styles.v15Sub}>Explore timeless shades, from natural essentials to bold expressions.</Text>
    <View style={styles.v15FamilyList}>{shown.map(f=><Pressable key={f.id} onPress={()=>choose(f.id)} style={[styles.v15FamilyRow,f.id===selected&&styles.v15FamilyRowOn]}>
      <View style={styles.v15FamilyImg}><V15Photo family={f.id}/></View><View style={{flex:1}}><Text style={styles.v15FamilyName}>{f.name==='Pink'?'Fantasy':f.name}</Text><Text style={styles.v15FamilyCopy}>{f.id==='blonde'?'Bright, soft, effortless':f.id==='brown'?'Rich, natural, versatile':f.id==='red'?'Warm, bold, distinctive':f.id==='black'?'Deep, elegant, timeless':'Creative, unique, you'}</Text></View><Text style={styles.v15Chevron}>›</Text>
    </Pressable>)}</View>
  </View>
}''')

block('function ShadeScreen','function PhotoScreen',r'''function ShadeScreen({family,list,selected,choose}:{family?:Family;list:Shade[];selected:string;choose:(id:string)=>void}){
  return <View>
    <Text style={styles.v15Title}>{family?.name||'Shades'}</Text><Text style={styles.v15Sub}>Refined tones designed to be explored visually.</Text>
    <View style={styles.v15ShadeGrid}>{list.map((x,i)=>{const on=x.id===selected;return <Pressable key={x.id} onPress={()=>choose(x.id)} style={styles.v15ShadeItem}>
      <View style={[styles.v15ShadePhoto,on&&styles.v15ShadePhotoOn]}><V15Photo family={x.family}/><View style={[styles.v15Tint,{backgroundColor:x.hex}]}/>{on?<View style={styles.v15SelectedDot}><Text style={styles.v15SelectedDotText}>✓</Text></View>:null}</View>
      <Text style={styles.v15ShadeCode}>{x.level}.0</Text><Text numberOfLines={2} style={styles.v15ShadeLabel}>{x.name}</Text>
    </Pressable>})}</View>
  </View>
}''')

block('function PhotoScreen','function AdjustScreen',r'''function PhotoScreen({photoUri,pick,take,next}:{photoUri:string;pick:()=>void;take:()=>void;next:()=>void}){
  return <View>
    <View style={styles.v15CenterHead}><Text style={styles.v15Title}>Upload Your Photo</Text><Text style={styles.v15SubCenter}>A clear, natural photo gives the most realistic results.</Text></View>
    {photoUri?<View style={styles.v15ChosenPhoto}><Image source={{uri:photoUri}} style={styles.v15Contain}/></View>:<Pressable onPress={pick} style={styles.v15Upload}><Text style={styles.v15UploadIcon}>▧</Text><Text style={styles.v15UploadTitle}>Tap to choose a photo</Text><Text style={styles.v15UploadMeta}>JPG or PNG</Text></Pressable>}
    <View style={styles.v15PhotoActions}><Pressable onPress={pick} style={styles.v15Outline}><Text style={styles.v15OutlineText}>Choose Photo</Text></Pressable><Pressable onPress={take} style={styles.v15Outline}><Text style={styles.v15OutlineText}>Camera</Text></Pressable></View>
    <View style={styles.v15Tips}><Text style={styles.v15Tip}>✓  Good lighting</Text><Text style={styles.v15Tip}>✓  Entire hair visible</Text><Text style={styles.v15Tip}>×  Avoid filters</Text></View>
    {photoUri?<Pressable onPress={next} style={styles.v15Primary}><Text style={styles.v15PrimaryText}>Generate Preview  →</Text></Pressable>:null}
  </View>
}''')

block('function PreviewScreen','function SavedScreen',r'''function PreviewScreen({source,preview,shade,notice,busy,retry,save,saved}:{source:string;preview:string;shade?:Shade;notice:string;busy:boolean;retry:()=>void;save:()=>void;saved:boolean}){
  return <View>
    <View style={styles.v15CenterHead}><Text style={styles.v15Title}>Your Preview</Text><Text style={styles.v15SubCenter}>Full framing preserved — no forced zoom or crop.</Text></View>
    <View style={styles.v15CompareRow}>
      <View style={styles.v15CompareCard}><Image source={{uri:source}} style={styles.v15Contain}/><View style={styles.v15ImageTag}><Text style={styles.v15ImageTagText}>Before</Text></View></View>
      <View style={styles.v15CompareCard}><Image source={{uri:preview}} style={styles.v15Contain}/><View style={styles.v15ImageTag}><Text style={styles.v15ImageTagText}>After</Text></View></View>
    </View>
    <View style={styles.v15ShadeSummary}><View style={[styles.v15Swatch,{backgroundColor:shade?.hex||C.taupe}]}/><View style={{flex:1}}><Text style={styles.v15SummaryTitle}>{shade?.level||'—'}.0 {shade?.name||'Your shade'}</Text><Text style={styles.v15SummarySub}>{shade?.tone||'Selected tone'} · {shade?.saturation||''}</Text></View><Text style={styles.v15SummaryHeart}>{saved?'♥':'♡'}</Text></View>
    {notice?<View style={styles.notice}><Text style={styles.noticeText}>{notice}</Text><Pressable onPress={retry}><Text style={styles.noticeLink}>{busy?'Generating…':'Try again'}</Text></Pressable></View>:null}
    <Pressable onPress={save} style={styles.v15Primary}><Text style={styles.v15PrimaryText}>{saved?'♥ Saved':'Save Shade'}</Text></Pressable>
  </View>
}''')

# Skip the non-functional Adjust Photo screen entirely.
s=s.replace("function goBack(){const p:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',adjust:'photo',preview:'adjust',saved:'home',more:'home'};setScreen(p[screen])}","function goBack(){const p:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',adjust:'photo',preview:'photo',saved:'home',more:'home'};setScreen(p[screen])}")
s=s.replace("<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={()=>setScreen('adjust')}/>","<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={preview}/>")
s=s.replace("<PhotoScreen photoUri={photoUri} pick={pick} take={take} next={()=>setScreen('adjust')}/>","<PhotoScreen photoUri={photoUri} pick={pick} take={take} next={preview}/>")

# Replace the opening completely with the newly approved photographic treatment.
start=s.index('if(showSplash)return ')
end=s.index('\n\n  const body',start)
s=s[:start]+"if(showSplash)return <Animated.View style={[styles.v15Splash,{opacity:splashOpacity}]}><StatusBar style=\"light\"/><Image source={require('./assets/v15-opening.jpg')} style={styles.v15SplashImage}/></Animated.View>;"+s[end:]

# Fresh visual system. Old styles remain harmlessly for legacy components.
idx=s.rfind('});')
extra=r'''
  v15Splash:{flex:1,backgroundColor:'#80695A'},v15SplashImage:{width:'100%',height:'100%',resizeMode:'cover'},
  v15Photo:{width:'100%',height:'100%',resizeMode:'cover'},v15Home:{paddingTop:8},v15HomeHead:{flexDirection:'row',alignItems:'center',justifyContent:'space-between',marginBottom:38},v15Heart:{fontSize:28,color:C.dark},v15HomeTitle:{fontFamily:'serif',fontSize:43,lineHeight:47,color:C.ink},v15HomeCopy:{fontSize:13,lineHeight:20,color:C.muted,marginTop:13,maxWidth:300},v15Primary:{height:54,borderRadius:28,backgroundColor:'#34271F',alignItems:'center',justifyContent:'center',marginTop:22},v15PrimaryText:{fontFamily:'serif',fontSize:15,color:'#FFF'},v15HomePhoto:{height:270,borderRadius:26,overflow:'hidden',marginTop:22,justifyContent:'flex-end'},v15PhotoScrim:{...fill,backgroundColor:'rgba(38,27,20,.18)'},v15HomePhotoText:{fontFamily:'serif',fontSize:27,color:'#FFF',padding:20},v15QuickRow:{flexDirection:'row',gap:10,marginTop:10},v15Quick:{flex:1,borderRadius:20,backgroundColor:'#EEE5DC',padding:18,minHeight:94},v15QuickKicker:{fontSize:8,letterSpacing:1.8,color:C.muted},v15QuickTitle:{fontFamily:'serif',fontSize:17,color:C.ink,marginTop:8},
  v15Title:{fontFamily:'serif',fontSize:34,lineHeight:39,color:C.ink},v15Sub:{fontSize:12.5,lineHeight:19,color:C.muted,marginTop:7,marginBottom:20},v15SubCenter:{fontSize:12.5,lineHeight:19,color:C.muted,marginTop:7,textAlign:'center',maxWidth:310},v15CenterHead:{alignItems:'center',marginBottom:22},v15FamilyList:{gap:9},v15FamilyRow:{height:91,borderRadius:18,backgroundColor:'#EFE7DE',flexDirection:'row',alignItems:'center',padding:8,gap:13},v15FamilyRowOn:{borderWidth:1.5,borderColor:C.dark},v15FamilyImg:{width:78,height:75,borderRadius:15,overflow:'hidden'},v15FamilyName:{fontFamily:'serif',fontSize:20,color:C.ink},v15FamilyCopy:{fontSize:10.5,color:C.muted,marginTop:4},v15Chevron:{fontSize:26,color:C.dark,paddingHorizontal:8},
  v15ShadeGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:20},v15ShadeItem:{width:'31%'},v15ShadePhoto:{height:126,borderRadius:13,overflow:'hidden',position:'relative',backgroundColor:'#D8C8BC'},v15ShadePhotoOn:{borderWidth:2,borderColor:C.dark},v15Tint:{...fill,opacity:.38},v15SelectedDot:{position:'absolute',right:7,top:7,width:24,height:24,borderRadius:12,backgroundColor:'rgba(255,255,255,.94)',alignItems:'center',justifyContent:'center'},v15SelectedDotText:{fontSize:11,color:C.dark,fontWeight:'700'},v15ShadeCode:{fontSize:10,fontWeight:'700',color:C.ink,marginTop:7},v15ShadeLabel:{fontSize:9.5,lineHeight:12,color:C.muted},
  v15Upload:{height:250,borderWidth:1,borderStyle:'dashed',borderColor:'#CFC1B5',borderRadius:20,alignItems:'center',justifyContent:'center',backgroundColor:'#FAF6F0'},v15UploadIcon:{fontSize:34,color:C.dark},v15UploadTitle:{fontFamily:'serif',fontSize:16,color:C.ink,marginTop:14},v15UploadMeta:{fontSize:10,color:C.muted,marginTop:7},v15ChosenPhoto:{height:390,borderRadius:22,overflow:'hidden',backgroundColor:'#E9E0D7'},v15Contain:{width:'100%',height:'100%',resizeMode:'contain',backgroundColor:'#E9E0D7'},v15PhotoActions:{flexDirection:'row',gap:10,marginTop:12},v15Outline:{flex:1,height:44,borderRadius:22,borderWidth:1,borderColor:C.line,alignItems:'center',justifyContent:'center',backgroundColor:C.paper},v15OutlineText:{fontSize:12,color:C.ink},v15Tips:{flexDirection:'row',justifyContent:'space-between',marginTop:22},v15Tip:{fontSize:9.5,color:C.muted},
  v15CompareRow:{flexDirection:'row',gap:10},v15CompareCard:{flex:1,height:350,borderRadius:20,overflow:'hidden',position:'relative',backgroundColor:'#E9E0D7'},v15ImageTag:{position:'absolute',left:10,bottom:10,borderRadius:9,backgroundColor:'rgba(44,32,25,.72)',paddingHorizontal:10,paddingVertical:6},v15ImageTagText:{fontSize:10,color:'#FFF'},v15ShadeSummary:{flexDirection:'row',alignItems:'center',gap:13,marginTop:16,marginBottom:4},v15Swatch:{width:66,height:66,borderRadius:16},v15SummaryTitle:{fontFamily:'serif',fontSize:19,color:C.ink},v15SummarySub:{fontSize:10.5,color:C.muted,marginTop:4,textTransform:'capitalize'},v15SummaryHeart:{fontSize:28,color:C.dark},
'''
s=s[:idx]+extra+s[idx:]
p.write_text(s)
print('Applied v1.5 approved visual redesign to',p)
