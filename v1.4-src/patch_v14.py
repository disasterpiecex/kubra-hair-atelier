from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

def block(start,end,replacement):
    global s
    a=s.index(start)
    b=s.index(end,a)
    s=s[:a]+replacement.rstrip()+'\n\n'+s[b:]

# Restore optional crop/editing without forcing an aspect ratio.
s=s.replace("ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:false})","ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:true})")
s=s.replace("ImagePicker.launchCameraAsync({quality:.95,allowsEditing:false})","ImagePicker.launchCameraAsync({quality:.95,allowsEditing:true})")

block('function Home','function FamilyScreen',r'''function Home({go}:{go:(s:Screen)=>void}){
  const Hero=({title,subtitle,base,accent,onPress}:{title:string;subtitle:string;base:string;accent:string;onPress:()=>void})=><Pressable onPress={onPress} style={styles.v14HomeCard}><HairTexture base={base} accent={accent}/><View style={styles.v14CardFade}/><View style={styles.v14CardText}><Text style={styles.v14CardTitle}>{title}</Text><Text style={styles.v14CardSub}>{subtitle}</Text></View><Text style={styles.v14CardArrow}>›</Text></Pressable>;
  return <View>
    <View style={styles.v14HomeTop}><Wordmark/><View style={styles.v14Profile}><Text style={styles.v14ProfileText}>○</Text></View></View>
    <Text style={styles.v14HomeTitle}>A more you</Text><Text style={styles.v14HomeCopy}>Discover, try and find{`\n`}your perfect shade.</Text>
    <View style={styles.v14HomeCards}>
      <Hero title="Explore Shades" subtitle="Find your tone" base="#CDB79A" accent="#EEE0CD" onPress={()=>go('family')}/>
      <Hero title="Try with Your Photo" subtitle="See it on you" base="#8A6756" accent="#C9A595" onPress={()=>go('photo')}/>
      <Hero title="Create Custom Shade" subtitle="Build your look" base="#B79A81" accent="#E8D3C0" onPress={()=>go('family')}/>
    </View>
  </View>
}''')

block('function FamilyScreen','function ShadeScreen',r'''function FamilyScreen({selected,choose}:{selected:string;choose:(id:string)=>void}){
  return <View><View style={styles.v14CenterHead}><Text style={styles.v14ScreenTitle}>Color Families</Text><Text style={styles.v14ScreenSub}>Find your tone.</Text></View>
    <View style={styles.v14FamilyGrid}>{families.map(f=>{const on=f.id===selected;return <Pressable key={f.id} onPress={()=>choose(f.id)} style={[styles.v14FamilyCard,on&&styles.v14SelectedCard]}><HairTexture base={f.color} accent={f.accent}/><View style={styles.v14TileFade}/><Text style={styles.v14FamilyName}>{f.name}</Text>{on?<View style={styles.v14Check}><Text style={styles.v14CheckText}>✓</Text></View>:null}</Pressable>})}</View>
  </View>
}''')

block('function ShadeScreen','function PhotoScreen',r'''function ShadeScreen({family,list,selected,choose}:{family?:Family;list:Shade[];selected:string;choose:(id:string)=>void}){
  const hero=list[0];
  return <View>
    <View style={styles.v14ShadeHero}>{hero?<HairTexture base={hero.hex} accent="#F3E1D3"/>:null}<View style={styles.v14TileFade}/><View style={styles.v14ShadeHeroText}><Text style={styles.v14ShadeFamily}>{family?.name||'Shades'}</Text><Text style={styles.v14ShadeFamilySub}>Bright, natural, effortless.</Text></View></View>
    <View style={styles.v14Filters}><View style={styles.v14FilterOn}><Text style={styles.v14FilterOnText}>All</Text></View><View style={styles.v14Filter}><Text style={styles.v14FilterText}>Cool</Text></View><View style={styles.v14Filter}><Text style={styles.v14FilterText}>Neutral</Text></View><View style={styles.v14Filter}><Text style={styles.v14FilterText}>Warm</Text></View></View>
    <View style={styles.v14ShadeGrid}>{list.map(x=>{const on=x.id===selected;return <Pressable key={x.id} onPress={()=>choose(x.id)} style={styles.v14ShadeItem}><View style={[styles.v14ShadeTile,on&&styles.v14SelectedCard]}><HairTexture base={x.hex} accent="#F4E7DD"/>{on?<View style={styles.v14HeartBadge}><Text style={styles.v14HeartText}>♥</Text></View>:null}</View><Text style={styles.v14ShadeLevel}>{x.level}.0</Text><Text numberOfLines={2} style={styles.v14ShadeName}>{x.name}</Text></Pressable>})}</View>
  </View>
}''')

block('function PhotoScreen','function AdjustScreen',r'''function PhotoScreen({photoUri,pick,take,remove,next}:{photoUri:string;pick:()=>void;take:()=>void;remove:()=>void;next:()=>void}){
  return <View><View style={styles.v14CenterHead}><Text style={styles.v14ScreenTitle}>Try with Your Photo</Text><Text style={styles.v14ScreenSub}>See how a shade looks on you{`\n`}before you decide.</Text></View>
    {photoUri?<View><View style={styles.v14UploadPreview}><Image key={photoUri} source={{uri:photoUri}} style={styles.v14Contain}/><Pressable onPress={remove} style={styles.v14RemoveX}><Text style={styles.v14RemoveXText}>×</Text></Pressable></View></View>:<View style={styles.v14UploadBox}><View style={styles.v14CameraCircle}><Text style={styles.v14Camera}>▣</Text></View><Text style={styles.v14UploadTitle}>Upload a Photo</Text><Text style={styles.v14UploadSub}>Or take a new one</Text></View>}
    <View style={styles.dual}><Pressable onPress={pick} style={styles.secondary}><Text style={styles.secondaryText}>Choose Photo</Text></Pressable><Pressable onPress={take} style={styles.secondary}><Text style={styles.secondaryText}>Take Photo</Text></Pressable></View>
    <Text style={styles.v14PhotoHint}>Use a clear photo with good lighting for the best result.</Text>
    {photoUri?<View style={styles.cta}><Primary label="Adjust Photo →" onPress={next}/></View>:null}
  </View>
}''')

block('function AdjustScreen','function PreviewScreen',r'''function AdjustScreen({photoUri,shade,next}:{photoUri:string;shade?:Shade;next:()=>void}){
  return <View><View style={styles.v14CenterHead}><Text style={styles.v14ScreenTitle}>Adjust Your Photo</Text><Text style={styles.v14ScreenSub}>Make sure your hair is clearly visible.</Text></View>
    <View style={styles.v14AdjustStage}><Image source={{uri:photoUri}} style={styles.v14Contain}/><View style={styles.v14CropFrame}><View style={[styles.v14Corner,styles.v14CornerTL]}/><View style={[styles.v14Corner,styles.v14CornerTR]}/><View style={[styles.v14Corner,styles.v14CornerBL]}/><View style={[styles.v14Corner,styles.v14CornerBR]}/></View></View>
    <View style={styles.v14AdjustTools}><View><Text style={styles.v14ToolIcon}>↻</Text><Text style={styles.v14ToolText}>Rotate</Text></View><View><Text style={styles.v14ToolIcon}>⊙</Text><Text style={styles.v14ToolText}>Zoom</Text></View><View><Text style={styles.v14ToolIcon}>□</Text><Text style={styles.v14ToolText}>Fit</Text></View></View>
    <Text style={styles.v14AdjustNote}>The crop you chose in the photo editor is preserved. Use this screen to check the framing before continuing.</Text>
    <View style={styles.cta}><Primary label="Continue" onPress={next}/></View>
  </View>
}''')

block('function PreviewScreen','function SavedScreen',r'''function PreviewScreen({source,preview,shade,notice,busy,retry,save,saved}:{source:string;preview:string;shade?:Shade;notice:string;busy:boolean;retry:()=>void;save:()=>void;saved:boolean}){
  return <View><View style={styles.v14CenterHead}><Text style={styles.v14ScreenTitle}>Your Preview</Text></View>
    <View style={styles.v14PreviewStage}><View style={styles.v14Half}><Image source={{uri:source}} style={styles.v14Cover}/></View><View style={styles.v14Half}><Image source={{uri:preview}} style={styles.v14Cover}/></View><View style={styles.v14Divider}/><View style={styles.v14DividerKnob}><Text style={styles.v14KnobText}>↔</Text></View><View style={styles.v14BeforeTag}><Text style={styles.v14TagText}>Before</Text></View><View style={styles.v14AfterTag}><Text style={styles.v14TagText}>After</Text></View></View>
    <View style={styles.v14ShadeSummary}><View style={[styles.v14Swatch,{backgroundColor:shade?.hex||C.taupe}]}/><View style={{flex:1}}><Text style={styles.v14SummaryTitle}>{shade?.level||'—'}.3 {shade?.name||'Your shade'}</Text><Text style={styles.v14SummarySub}>Warm, elegant, natural.</Text></View><Text style={styles.v14SummaryHeart}>{saved?'♥':'♡'}</Text></View>
    {notice?<View style={styles.notice}><Text style={styles.noticeText}>{notice}</Text><Pressable onPress={retry}><Text style={styles.noticeLink}>{busy?'Generating…':'Try again'}</Text></Pressable></View>:null}
    <View style={styles.cta}><Primary label={saved?'♥ Saved':'Save Shade'} onPress={save}/></View>
  </View>
}''')

# Approved opening artwork, directly sourced from the approved mockup.
s=s.replace("require('./assets/opening-hair.jpg')","require('./assets/opening-approved.jpg')")
s=s.replace("require('./assets/opening-hair.png')","require('./assets/opening-approved.jpg')")

extra=r'''  v14HomeTop:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginBottom:24},v14Profile:{width:34,height:34,borderRadius:17,borderWidth:1,borderColor:C.line,alignItems:'center',justifyContent:'center'},v14ProfileText:{fontSize:20,color:C.ink},v14HomeTitle:{fontFamily:'serif',fontSize:34,color:C.ink,marginBottom:8},v14HomeCopy:{fontSize:13,color:C.muted,lineHeight:19,marginBottom:24},v14HomeCards:{gap:10},v14HomeCard:{height:132,borderRadius:22,overflow:'hidden',position:'relative',justifyContent:'center'},v14CardFade:{...fill,backgroundColor:'rgba(40,24,18,.15)'},v14CardText:{paddingHorizontal:20},v14CardTitle:{fontFamily:'serif',fontSize:22,color:'#FFF'},v14CardSub:{fontSize:11,color:'rgba(255,255,255,.82)',marginTop:4},v14CardArrow:{position:'absolute',right:18,fontSize:32,color:'#FFF',fontWeight:'200'},
  v14CenterHead:{alignItems:'center',marginBottom:22},v14ScreenTitle:{fontFamily:'serif',fontSize:27,color:C.ink,textAlign:'center'},v14ScreenSub:{fontSize:11.5,color:C.muted,textAlign:'center',lineHeight:17,marginTop:6},v14FamilyGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:10},v14FamilyCard:{width:'48.5%',aspectRatio:1.18,borderRadius:20,overflow:'hidden',position:'relative',justifyContent:'flex-end'},v14SelectedCard:{borderWidth:2,borderColor:C.dark},v14TileFade:{...fill,backgroundColor:'rgba(40,25,18,.16)'},v14FamilyName:{fontFamily:'serif',fontSize:19,color:'#FFF',padding:14},v14Check:{position:'absolute',right:9,top:9,width:26,height:26,borderRadius:13,backgroundColor:C.paper,alignItems:'center',justifyContent:'center'},v14CheckText:{color:C.dark,fontWeight:'700'},
  v14ShadeHero:{height:118,borderRadius:22,overflow:'hidden',position:'relative',justifyContent:'flex-end',marginBottom:14},v14ShadeHeroText:{padding:16},v14ShadeFamily:{fontFamily:'serif',fontSize:25,color:'#FFF'},v14ShadeFamilySub:{fontSize:10,color:'rgba(255,255,255,.85)',marginTop:3},v14Filters:{flexDirection:'row',gap:8,marginBottom:16},v14Filter:{flex:1,height:32,borderRadius:16,backgroundColor:'#EFE8E1',alignItems:'center',justifyContent:'center'},v14FilterOn:{flex:1,height:32,borderRadius:16,backgroundColor:C.dark,alignItems:'center',justifyContent:'center'},v14FilterText:{fontSize:10,color:C.muted},v14FilterOnText:{fontSize:10,color:'#FFF'},v14ShadeGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:18},v14ShadeItem:{width:'31%'},v14ShadeTile:{width:'100%',aspectRatio:1,borderRadius:15,overflow:'hidden',position:'relative'},v14HeartBadge:{position:'absolute',right:7,top:7,width:24,height:24,borderRadius:12,backgroundColor:'rgba(255,255,255,.9)',alignItems:'center',justifyContent:'center'},v14HeartText:{fontSize:12,color:C.dark},v14ShadeLevel:{fontSize:10,color:C.ink,marginTop:7,fontWeight:'600'},v14ShadeName:{fontSize:10,color:C.muted,lineHeight:13},
  v14UploadBox:{height:236,borderRadius:24,backgroundColor:'#F1E9E3',alignItems:'center',justifyContent:'center',marginBottom:14},v14CameraCircle:{width:60,height:60,borderRadius:30,backgroundColor:'#E3BBC0',alignItems:'center',justifyContent:'center',marginBottom:16},v14Camera:{fontSize:26,color:C.dark},v14UploadTitle:{fontFamily:'serif',fontSize:18,color:C.ink},v14UploadSub:{fontSize:11,color:C.muted,marginTop:6},v14UploadPreview:{height:360,borderRadius:24,overflow:'hidden',backgroundColor:'#EEE6E0',position:'relative',marginBottom:12},v14Contain:{width:'100%',height:'100%',resizeMode:'contain',backgroundColor:'#EEE6E0'},v14Cover:{width:'100%',height:'100%',resizeMode:'cover'},v14RemoveX:{position:'absolute',right:12,top:12,width:32,height:32,borderRadius:16,backgroundColor:'rgba(255,255,255,.9)',alignItems:'center',justifyContent:'center'},v14RemoveXText:{fontSize:22,color:C.ink},v14PhotoHint:{fontSize:10.5,color:C.muted,textAlign:'center',marginTop:14,lineHeight:15},
  v14AdjustStage:{height:410,borderRadius:22,overflow:'hidden',backgroundColor:'#2F2925',position:'relative'},v14CropFrame:{position:'absolute',left:26,right:26,top:30,bottom:30},v14Corner:{position:'absolute',width:28,height:28,borderColor:'#FFF'},v14CornerTL:{left:0,top:0,borderLeftWidth:3,borderTopWidth:3},v14CornerTR:{right:0,top:0,borderRightWidth:3,borderTopWidth:3},v14CornerBL:{left:0,bottom:0,borderLeftWidth:3,borderBottomWidth:3},v14CornerBR:{right:0,bottom:0,borderRightWidth:3,borderBottomWidth:3},v14AdjustTools:{flexDirection:'row',justifyContent:'space-around',paddingVertical:16},v14ToolIcon:{fontSize:24,color:C.ink,textAlign:'center'},v14ToolText:{fontSize:10,color:C.muted,textAlign:'center',marginTop:3},v14AdjustNote:{fontSize:10.5,color:C.muted,textAlign:'center',lineHeight:15,paddingHorizontal:18},
  v14PreviewStage:{height:430,borderRadius:22,overflow:'hidden',position:'relative',flexDirection:'row',backgroundColor:'#D8C9BE'},v14Half:{width:'50%',height:'100%',overflow:'hidden'},v14Divider:{position:'absolute',left:'50%',top:0,bottom:0,width:1,backgroundColor:'#FFF'},v14DividerKnob:{position:'absolute',left:'50%',top:'52%',marginLeft:-18,width:36,height:36,borderRadius:18,backgroundColor:'#FFF',alignItems:'center',justifyContent:'center'},v14KnobText:{fontSize:15,color:C.dark},v14BeforeTag:{position:'absolute',left:12,bottom:12,backgroundColor:'rgba(43,29,23,.72)',borderRadius:9,paddingHorizontal:10,paddingVertical:6},v14AfterTag:{position:'absolute',right:12,bottom:12,backgroundColor:'rgba(43,29,23,.72)',borderRadius:9,paddingHorizontal:10,paddingVertical:6},v14TagText:{fontSize:10,color:'#FFF'},v14ShadeSummary:{flexDirection:'row',alignItems:'center',gap:12,paddingVertical:16},v14Swatch:{width:56,height:56,borderRadius:12},v14SummaryTitle:{fontFamily:'serif',fontSize:16,color:C.ink},v14SummarySub:{fontSize:10.5,color:C.muted,marginTop:3},v14SummaryHeart:{fontSize:24,color:C.dark},
'''
idx=s.rfind('});')
s=s[:idx]+extra+s[idx:]
p.write_text(s)
print('Applied v1.4 redesign to',p)
