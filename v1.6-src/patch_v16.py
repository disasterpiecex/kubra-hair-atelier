from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'App.tsx')
s=p.read_text()

def block(start,end,replacement):
    global s
    a=s.index(start)
    b=s.index(end,a)
    s=s[:a]+replacement.rstrip()+'\n\n'+s[b:]

# Bring back the system crop/editor, but do not force a fixed aspect ratio.
s=s.replace('ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:false})','ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:true})')
s=s.replace('ImagePicker.launchCameraAsync({quality:.95,allowsEditing:false})','ImagePicker.launchCameraAsync({quality:.95,allowsEditing:true})')
s=s.replace('ImagePicker.launchImageLibraryAsync({quality:.9,allowsEditing:false})','ImagePicker.launchImageLibraryAsync({quality:.95,allowsEditing:true})')
s=s.replace('ImagePicker.launchCameraAsync({quality:.9,allowsEditing:false})','ImagePicker.launchCameraAsync({quality:.95,allowsEditing:true})')

# Restore the more useful color-first family selection while keeping the v1.5 overall visual language.
block('function FamilyScreen','function ShadeScreen',r'''function FamilyScreen({selected,choose}:{selected:string;choose:(id:string)=>void}){
  return <View>
    <View style={styles.v15CenterHead}><Text style={styles.v15Title}>Color Families</Text><Text style={styles.v15SubCenter}>Choose by color first, then refine the exact shade.</Text></View>
    <View style={styles.v14FamilyGrid}>{families.map(f=>{const on=f.id===selected;return <Pressable key={f.id} onPress={()=>choose(f.id)} style={[styles.v14FamilyCard,on&&styles.v14SelectedCard]}><HairTexture base={f.color} accent={f.accent}/><View style={styles.v14TileFade}/><Text style={styles.v14FamilyName}>{f.name}</Text>{on?<View style={styles.v14Check}><Text style={styles.v14CheckText}>✓</Text></View>:null}</Pressable>})}</View>
  </View>
}''')

# Restore direct shade-color swatches rather than photographic tiles.
block('function ShadeScreen','function PhotoScreen',r'''function ShadeScreen({family,list,selected,choose}:{family?:Family;list:Shade[];selected:string;choose:(id:string)=>void}){
  const hero=list[0];
  return <View>
    <View style={styles.v14ShadeHero}>{hero?<HairTexture base={hero.hex} accent="#F3E1D3"/>:null}<View style={styles.v14TileFade}/><View style={styles.v14ShadeHeroText}><Text style={styles.v14ShadeFamily}>{family?.name||'Shades'}</Text><Text style={styles.v14ShadeFamilySub}>See the color itself before choosing.</Text></View></View>
    <View style={styles.v14Filters}><View style={styles.v14FilterOn}><Text style={styles.v14FilterOnText}>All</Text></View><View style={styles.v14Filter}><Text style={styles.v14FilterText}>Cool</Text></View><View style={styles.v14Filter}><Text style={styles.v14FilterText}>Neutral</Text></View><View style={styles.v14Filter}><Text style={styles.v14FilterText}>Warm</Text></View></View>
    <View style={styles.v14ShadeGrid}>{list.map(x=>{const on=x.id===selected;return <Pressable key={x.id} onPress={()=>choose(x.id)} style={styles.v14ShadeItem}><View style={[styles.v14ShadeTile,on&&styles.v14SelectedCard]}><HairTexture base={x.hex} accent="#F4E7DD"/>{on?<View style={styles.v14HeartBadge}><Text style={styles.v14HeartText}>♥</Text></View>:null}</View><Text style={styles.v14ShadeLevel}>{x.level}.0</Text><Text numberOfLines={2} style={styles.v14ShadeName}>{x.name}</Text></Pressable>})}</View>
  </View>
}''')

# Restore active-photo removal. Saved/favorite results are stored separately and are not touched here.
block('function PhotoScreen','function AdjustScreen',r'''function PhotoScreen({photoUri,pick,take,remove,next}:{photoUri:string;pick:()=>void;take:()=>void;remove:()=>void;next:()=>void}){
  return <View>
    <View style={styles.v15CenterHead}><Text style={styles.v15Title}>Upload Your Photo</Text><Text style={styles.v15SubCenter}>Crop only if you want to. Keep the full frame when that shows your hair better.</Text></View>
    {photoUri?<View><View style={styles.v15ChosenPhoto}><Image source={{uri:photoUri}} style={styles.v15Contain}/><Pressable onPress={remove} style={styles.v14RemoveX}><Text style={styles.v14RemoveXText}>×</Text></Pressable></View><Pressable onPress={remove} style={styles.v16RemovePhoto}><Text style={styles.v16RemovePhotoText}>Remove photo</Text></Pressable></View>:<Pressable onPress={pick} style={styles.v15Upload}><Text style={styles.v15UploadIcon}>▧</Text><Text style={styles.v15UploadTitle}>Tap to choose a photo</Text><Text style={styles.v15UploadMeta}>JPG or PNG</Text></Pressable>}
    <View style={styles.v15PhotoActions}><Pressable onPress={pick} style={styles.v15Outline}><Text style={styles.v15OutlineText}>Choose Photo</Text></Pressable><Pressable onPress={take} style={styles.v15Outline}><Text style={styles.v15OutlineText}>Camera</Text></Pressable></View>
    <View style={styles.v15Tips}><Text style={styles.v15Tip}>✓  Good lighting</Text><Text style={styles.v15Tip}>✓  Entire hair visible</Text><Text style={styles.v15Tip}>×  Avoid filters</Text></View>
    {photoUri?<Pressable onPress={next} style={styles.v15Primary}><Text style={styles.v15PrimaryText}>Generate Preview  →</Text></Pressable>:null}
  </View>
}''')

# Remove Adjust Photo from the actual route completely. Photo goes directly to preview generation.
s=s.replace("function goBack(){const p:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',adjust:'photo',preview:'adjust',saved:'home',more:'home'};setScreen(p[screen])}","function goBack(){const p:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',adjust:'photo',preview:'photo',saved:'home',more:'home'};setScreen(p[screen])}")
s=s.replace("function goBack(){const p:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',adjust:'photo',preview:'photo',saved:'home',more:'home'};setScreen(p[screen])}","function goBack(){const p:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',adjust:'photo',preview:'photo',saved:'home',more:'home'};setScreen(p[screen])}")

# Handle both navigation shapes produced by earlier patches.
s=s.replace("<PhotoScreen photoUri={photoUri} pick={pick} take={take} next={preview}/>","<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={preview}/>")
s=s.replace("<PhotoScreen photoUri={photoUri} pick={pick} take={take} next={()=>setScreen('adjust')}/>","<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={preview}/>")
s=s.replace(":screen==='adjust'?<AdjustScreen photoUri={photoUri} shade={shade} next={preview}/>",":screen==='adjust'?<PhotoScreen photoUri={photoUri} pick={pick} take={take} remove={removePhoto} next={preview}/>")

# Small styling for explicit photo removal.
idx=s.rfind('});')
extra=r'''  v16RemovePhoto:{alignSelf:'center',paddingHorizontal:18,paddingVertical:10,marginTop:8},v16RemovePhotoText:{fontSize:11,color:C.muted,textDecorationLine:'underline'},
'''
s=s[:idx]+extra+s[idx:]

p.write_text(s)
print('Applied v1.6 targeted UX fixes to',p)
