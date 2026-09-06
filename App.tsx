import React, { useEffect, useMemo, useState } from 'react';
import {
  BackHandler,
  Image,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StatusBar as NativeStatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { generateHairPreview } from './api';

type Screen = 'home' | 'family' | 'shade' | 'photo' | 'preview' | 'saved' | 'more';
type Family = { id: string; name: string; color: string; accent: string };
type Shade = { id: string; family: string; name: string; hex: string; level: string; tone: string; saturation: string };

const C = {
  bg: '#F3EEE8',
  paper: '#FBF8F3',
  paper2: '#F8F3EC',
  ink: '#33251F',
  muted: '#8D7B70',
  line: '#E7DDD3',
  dark: '#463028',
  rose: '#B88C7B',
  champagne: '#D7C2B1',
  pale: '#EEE4DA',
  white: '#FFFDF9',
};

const families: Family[] = [
  { id: 'blonde', name: 'Blonde', color: '#D8B983', accent: '#F2DDAF' },
  { id: 'brown', name: 'Brown', color: '#76523B', accent: '#B68763' },
  { id: 'red', name: 'Red', color: '#8C2F2A', accent: '#C95B4F' },
  { id: 'copper', name: 'Copper', color: '#B75E32', accent: '#E7965F' },
  { id: 'black', name: 'Black', color: '#272220', accent: '#5A4C46' },
  { id: 'blue', name: 'Blue', color: '#263E65', accent: '#667FA5' },
  { id: 'pink', name: 'Pink', color: '#B96A78', accent: '#E8A9B0' },
  { id: 'violet', name: 'Violet', color: '#5E456A', accent: '#9D83AD' },
  { id: 'green', name: 'Green', color: '#4E6651', accent: '#8EA38E' },
  { id: 'grey', name: 'Grey', color: '#7D7B77', accent: '#B6B0A8' },
  { id: 'pastel', name: 'Pastel', color: '#C7B7C9', accent: '#E6D5DF' },
];

const shades: Shade[] = [
  ['blonde','dark-ash-blonde','Dark Ash Blonde','#9D835F','6','ash','soft'],
  ['blonde','beige-blonde','Beige Blonde','#C6A77A','8','beige','medium'],
  ['blonde','golden-blonde','Golden Blonde','#D5A858','8','golden','high'],
  ['blonde','champagne-blonde','Champagne Blonde','#D9C19A','9','neutral-warm','soft'],
  ['blonde','pearl-blonde','Pearl Blonde','#DDD0B6','9','pearl','soft'],
  ['blonde','icy-blonde','Icy Blonde','#E7E0D5','10','cool','soft'],
  ['brown','espresso','Espresso','#4A3328','4','neutral','deep'],
  ['brown','mocha','Mocha','#6B4D3C','5','neutral-cool','medium'],
  ['brown','chocolate','Chocolate','#79513A','5','warm','medium'],
  ['brown','mushroom','Mushroom Brown','#75665A','6','cool-neutral','soft'],
  ['brown','caramel','Caramel Brown','#9A6744','6','warm','medium'],
  ['brown','honey-brown','Honey Brown','#AF7A4E','7','warm-gold','medium'],
  ['red','burgundy','Burgundy','#642D37','4','wine','deep'],
  ['red','dark-cherry','Dark Cherry','#6F2730','4','cool-red','deep'],
  ['red','cherry','Cherry Red','#A3292E','5','red','high'],
  ['red','ruby','Ruby','#A53C43','5','cool-red','high'],
  ['red','auburn','Auburn','#824232','5','warm-red','medium'],
  ['copper','dark-copper','Dark Copper','#7C452E','5','copper','deep'],
  ['copper','classic-copper','Classic Copper','#A9532D','7','copper','high'],
  ['copper','ginger','Soft Ginger','#C87A4F','8','warm-copper','soft'],
  ['copper','apricot','Apricot Copper','#D88C63','8','peach-copper','soft'],
  ['black','natural-black','Natural Black','#24201F','2','neutral','deep'],
  ['black','soft-black','Soft Black','#302A27','2','neutral-warm','deep'],
  ['black','blue-black','Blue Black','#202633','2','blue-cool','deep'],
  ['black','espresso-black','Espresso Black','#2F2723','2','warm-neutral','deep'],
  ['blue','midnight-blue','Midnight Blue','#23304D','3','cool-blue','deep'],
  ['blue','navy','Navy','#2B4169','4','cool-blue','deep'],
  ['blue','deep-cobalt','Deep Cobalt','#355A91','5','cobalt','high'],
  ['blue','denim','Denim','#607797','6','muted-blue','soft'],
  ['blue','sapphire','Sapphire','#2F5C9A','5','jewel-blue','high'],
  ['pink','dusty-rose','Dusty Rose','#A96D77','7','rose','soft'],
  ['pink','rose-gold','Rose Gold','#C98E8C','8','warm-rose','soft'],
  ['pink','bubblegum','Bubblegum','#DB849C','8','pink','high'],
  ['violet','deep-plum','Deep Plum','#4C354D','4','plum','deep'],
  ['violet','amethyst','Amethyst','#745887','6','violet','medium'],
  ['violet','lavender','Lavender','#A791B3','8','lavender','soft'],
  ['green','forest','Forest Green','#3D5542','4','green','deep'],
  ['green','emerald','Emerald','#3F705B','5','jewel-green','high'],
  ['green','sage','Sage','#879783','7','muted-green','soft'],
  ['grey','charcoal','Charcoal','#5E5C5B','4','cool-grey','deep'],
  ['grey','smoky-grey','Smoky Grey','#85817D','6','smoke','soft'],
  ['grey','soft-silver','Soft Silver','#AAA8A4','8','silver','soft'],
  ['pastel','lavender-mist','Lavender Mist','#C7B5CA','9','pastel-violet','soft'],
  ['pastel','peach-mist','Peach Mist','#E4B7A5','9','pastel-peach','soft'],
  ['pastel','powder-blue','Powder Blue','#B2C6D6','9','pastel-blue','soft'],
].map(([family,id,name,hex,level,tone,saturation])=>({family,id,name,hex,level,tone,saturation})) as Shade[];

const SESSION = 'kha:v1.1.2:session';
const SAVED = 'kha:v1.1.2:saved';

function HairTexture({ base, accent, large=false }: { base: string; accent?: string; large?: boolean }) {
  const lines = Array.from({ length: large ? 11 : 8 });
  return <View style={[StyleSheet.absoluteFillObject, { backgroundColor: base, overflow: 'hidden' }]}>
    <View style={[styles.hairGlow,{backgroundColor:accent || 'rgba(255,255,255,.28)'}]} />
    {lines.map((_,i)=><View key={i} style={[styles.hairLine,{left:-30+i*22,top:-22+i*5,transform:[{rotate:`${16+i*1.2}deg`}],opacity:.11+(i%3)*.03}]} />)}
    <View style={styles.hairShade} />
  </View>
}

function Wordmark({compact=false}:{compact?:boolean}){
  return <View style={{alignItems:'center'}}><Text style={[styles.wordmark,compact&&{fontSize:18,letterSpacing:3.2}]}>KÜBRA</Text><Text style={[styles.wordmarkSub,compact&&{fontSize:7,letterSpacing:2.6}]}>HAIR ATELIER</Text></View>
}

function BottomNav({screen,onGo}:{screen:Screen,onGo:(s:Screen)=>void}){
  const items:[Screen,string,string][]=[['home','⌂','Home'],['family','◫','Explore'],['saved','♡','Saved'],['more','•••','More']];
  return <View style={styles.bottomNav}>{items.map(([id,icon,label])=><Pressable key={id} onPress={()=>onGo(id)} style={styles.navItem}><Text style={[styles.navIcon,(screen===id||(id==='family'&&['shade','photo','preview'].includes(screen)))&&styles.navOn]}>{icon}</Text><Text style={[styles.navLabel,(screen===id||(id==='family'&&['shade','photo','preview'].includes(screen)))&&styles.navOn]}>{label}</Text></Pressable>)}</View>
}

function TopBar({screen,onBack,onSaved}:{screen:Screen,onBack:()=>void,onSaved:()=>void}){
  return <View style={styles.topBar}><Pressable onPress={onBack} style={styles.iconButton}><Text style={styles.backIcon}>‹</Text></Pressable><Wordmark compact/><Pressable onPress={onSaved} style={styles.iconButton}><Text style={styles.heart}>♡</Text></Pressable></View>
}

function TitleBlock({eyebrow,title,copy}:{eyebrow:string,title:string,copy?:string}){
  return <View style={styles.titleBlock}><Text style={styles.eyebrow}>{eyebrow}</Text><Text style={styles.bigTitle}>{title}</Text>{copy?<Text style={styles.copy}>{copy}</Text>:null}</View>
}

function PrimaryButton({label,onPress,disabled=false}:{label:string,onPress:()=>void,disabled?:boolean}){
 return <Pressable disabled={disabled} onPress={onPress} style={[styles.primary,disabled&&styles.primaryDisabled]}><Text style={styles.primaryText}>{label}</Text></Pressable>
}

function App(){
 const [screen,setScreen]=useState<Screen>('home');
 const [familyId,setFamilyId]=useState('');
 const [shadeId,setShadeId]=useState('');
 const [photoUri,setPhotoUri]=useState('');
 const [previewUri,setPreviewUri]=useState('');
 const [savedIds,setSavedIds]=useState<string[]>([]);
 const [showSplash,setShowSplash]=useState(true);
 const [showExit,setShowExit]=useState(false);
 const [previewBusy,setPreviewBusy]=useState(false);
 const [previewNotice,setPreviewNotice]=useState('');
 const family=useMemo(()=>families.find(x=>x.id===familyId),[familyId]);
 const shade=useMemo(()=>shades.find(x=>x.id===shadeId),[shadeId]);
 const familyShades=useMemo(()=>shades.filter(x=>x.family===familyId),[familyId]);

 useEffect(()=>{(async()=>{try{const s=JSON.parse(await AsyncStorage.getItem(SESSION)||'{}');setFamilyId(s.familyId||'');setShadeId(s.shadeId||'');setPhotoUri(s.photoUri||'');setSavedIds(JSON.parse(await AsyncStorage.getItem(SAVED)||'[]'))}catch{}})()},[]);
 useEffect(()=>{AsyncStorage.setItem(SESSION,JSON.stringify({familyId,shadeId,photoUri})).catch(()=>{})},[familyId,shadeId,photoUri]);
 useEffect(()=>{AsyncStorage.setItem(SAVED,JSON.stringify(savedIds)).catch(()=>{})},[savedIds]);
 useEffect(()=>{const t=setTimeout(()=>setShowSplash(false),1300);return()=>clearTimeout(t)},[]);
 useEffect(()=>{if(Platform.OS!=='android')return;const sub=BackHandler.addEventListener('hardwareBackPress',()=>{if(showExit){setShowExit(false);return true}if(screen==='home'){setShowExit(true);return true}goBack();return true});return()=>sub.remove()},[screen,showExit]);

 function goBack(){
   const map:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',preview:'photo',saved:'home',more:'home'};
   setScreen(map[screen]);
 }
 async function pickPhoto(){
   const result=await ImagePicker.launchImageLibraryAsync({quality:.9,allowsEditing:false});
   if(!result.canceled&&result.assets?.[0]?.uri){setPhotoUri(result.assets[0].uri);setPreviewUri('');setPreviewNotice('');}
 }
 async function takePhoto(){
   const perm=await ImagePicker.requestCameraPermissionsAsync();if(!perm.granted)return;
   const result=await ImagePicker.launchCameraAsync({quality:.9});
   if(!result.canceled&&result.assets?.[0]?.uri){setPhotoUri(result.assets[0].uri);setPreviewUri('');setPreviewNotice('');}
 }
 async function makePreview(){
   if(!photoUri||!shade)return;setPreviewBusy(true);setPreviewNotice('');
   try{const r=await generateHairPreview(photoUri,shade);setPreviewUri(r.previewDataUrl||photoUri);if(r.provider==='mock-local')setPreviewNotice('Live AI preview is not connected in this build. Your original photo is shown instead.');setScreen('preview');}catch(e:any){setPreviewNotice(e?.message||'AI preview is currently unavailable.');setScreen('preview')}finally{setPreviewBusy(false)}
 }
 function chooseFamily(id:string){setFamilyId(id);setShadeId('');setPreviewUri('');}
 function chooseShade(id:string){setShadeId(id);setPreviewUri('');}
 function toggleSave(id:string){setSavedIds(x=>x.includes(id)?x.filter(y=>y!==id):[...x,id])}

 if(showSplash)return <View style={styles.splash}><StatusBar style="dark"/><View style={styles.splashHero}><HairTexture base="#9A796A" accent="#D5B4A4" large/><View style={styles.splashVeil}/><View style={styles.splashBrand}><Wordmark/></View></View><Text style={styles.splashTag}>BEAUTY LIVES IN YOUR SHADE</Text></View>;

 const content = screen==='home' ? <Home onExplore={()=>setScreen('family')} onPhoto={()=>setScreen(photoUri?'shade':'family')} onSaved={()=>setScreen('saved')}/>
 : screen==='family' ? <FamilyScreen selected={familyId} choose={chooseFamily} next={()=>setScreen('shade')}/>
 : screen==='shade' ? <ShadeScreen family={family} list={familyShades} selected={shadeId} savedIds={savedIds} choose={chooseShade} save={toggleSave} next={()=>setScreen('photo')}/>
 : screen==='photo' ? <PhotoScreen photoUri={photoUri} shade={shade} pick={pickPhoto} take={takePhoto} preview={makePreview} busy={previewBusy}/>
 : screen==='preview' ? <PreviewScreen source={photoUri} preview={previewUri||photoUri} shade={shade} notice={previewNotice} retry={makePreview} saved={shade? savedIds.includes(shade.id):false} save={()=>shade&&toggleSave(shade.id)}/>
 : screen==='saved' ? <SavedScreen saved={shades.filter(x=>savedIds.includes(x.id))} open={(x)=>{setFamilyId(x.family);setShadeId(x.id);setScreen('shade')}}/>
 : <MoreScreen/>;

 return <View style={styles.app}><StatusBar style="dark"/><View style={styles.statusSpace}/>{screen!=='home'&&<TopBar screen={screen} onBack={goBack} onSaved={()=>setScreen('saved')}/>}<ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={[styles.scroll,screen==='home'&&{paddingTop:0}]}>{content}</ScrollView><BottomNav screen={screen} onGo={setScreen}/><Modal visible={showExit} transparent animationType="fade" onRequestClose={()=>setShowExit(false)}><View style={styles.modalBack}><View style={styles.exitCard}><View style={styles.exitGlyph}><Text style={styles.exitGlyphText}>〰</Text></View><Text style={styles.exitTitle}>Leave Kübra Hair Atelier?</Text><Text style={styles.exitCopy}>Your progress will be saved, so you can always come back.</Text><View style={styles.exitButtons}><Pressable onPress={()=>setShowExit(false)} style={styles.stay}><Text style={styles.stayText}>Stay</Text></Pressable><Pressable onPress={()=>BackHandler.exitApp()} style={styles.exit}><Text style={styles.exitText}>Exit</Text></Pressable></View><Text style={styles.exitTag}>BEAUTY LIVES IN YOUR SHADE</Text></View></View></Modal></View>
}

function Home({onExplore,onPhoto,onSaved}:{onExplore:()=>void,onPhoto:()=>void,onSaved:()=>void}){
 return <View><View style={styles.homeHead}><Wordmark/><View style={styles.heroCopy}><Text style={styles.homeEyebrow}>COLOR, CURATED FOR YOU</Text><Text style={styles.homeTitle}>A more you.</Text><Text style={styles.homeCopy}>Discover your next shade with a softer, more personal way to explore color.</Text></View></View><View style={styles.editorialStack}>
   <Pressable onPress={onExplore} style={styles.featureCard}><View style={styles.featureImage}><HairTexture base="#6A4B3B" accent="#A9765F" large/><View style={styles.featureShade}/><View style={styles.featureLabel}><Text style={styles.featureKicker}>01 · DISCOVER</Text><Text style={styles.featureTitle}>Explore Shades</Text><Text style={styles.featureArrow}>→</Text></View></View></Pressable>
   <Pressable onPress={onPhoto} style={styles.featureCardSmall}><View style={styles.featureImage}><HairTexture base="#B99A83" accent="#E6CCB8" large/><View style={styles.featureShade}/><View style={styles.featureLabel}><Text style={styles.featureKicker}>02 · PREVIEW</Text><Text style={styles.featureTitle}>Try with Your Photo</Text><Text style={styles.featureArrow}>→</Text></View></View></Pressable>
   <Pressable onPress={onSaved} style={styles.featureCardSmall}><View style={styles.featureImage}><HairTexture base="#A7796C" accent="#D8B3A3" large/><View style={styles.featureShade}/><View style={styles.featureLabel}><Text style={styles.featureKicker}>03 · YOUR PALETTE</Text><Text style={styles.featureTitle}>Saved Shades</Text><Text style={styles.featureArrow}>→</Text></View></View></Pressable>
 </View></View>
}

function FamilyScreen({selected,choose,next}:{selected:string,choose:(x:string)=>void,next:()=>void}){
 return <View><TitleBlock eyebrow="COLOR INSPIRES YOU" title="Choose a color family" copy="Begin with the family that feels closest to the look you want."/><View style={styles.familyGrid}>{families.map(f=>{const on=selected===f.id;return <Pressable key={f.id} onPress={()=>choose(f.id)} style={styles.familyItem}><View style={[styles.familyVisual,on&&styles.familyVisualOn]}><HairTexture base={f.color} accent={f.accent}/>{on&&<View style={styles.check}><Text style={styles.checkText}>✓</Text></View>}</View><Text style={[styles.familyName,on&&styles.familyNameOn]}>{f.name}</Text></Pressable>})}</View><View style={styles.ctaGap}><PrimaryButton label="Next  →" disabled={!selected} onPress={next}/></View></View>
}

function ShadeScreen({family,list,selected,savedIds,choose,save,next}:{family?:Family,list:Shade[],selected:string,savedIds:string[],choose:(x:string)=>void,save:(x:string)=>void,next:()=>void}){
 return <View><TitleBlock eyebrow={`${family?.name?.toUpperCase()||'YOUR'} COLLECTION`} title="Choose your shade" copy="Tap a shade to see it selected. Save the ones you want to come back to."/><View style={styles.pills}><View style={styles.pillOn}><Text style={styles.pillOnText}>All shades</Text></View><View style={styles.pill}><Text style={styles.pillText}>Cool</Text></View><View style={styles.pill}><Text style={styles.pillText}>Warm</Text></View></View><View style={styles.shadeGrid}>{list.map(x=>{const on=x.id===selected;const fav=savedIds.includes(x.id);return <Pressable key={x.id} onPress={()=>choose(x.id)} style={[styles.shadeCard,on&&styles.shadeCardOn]}><View style={styles.shadeVisual}><HairTexture base={x.hex} accent="#EED9CA"/>{on&&<View style={styles.check}><Text style={styles.checkText}>✓</Text></View>}<Pressable onPress={()=>save(x.id)} style={styles.favBubble}><Text style={styles.favText}>{fav?'♥':'♡'}</Text></Pressable></View><Text style={styles.shadeName}>{x.name}</Text><Text style={styles.shadeMeta}>Level {x.level} · {x.tone}</Text></Pressable>})}</View><View style={styles.ctaGap}><PrimaryButton label="Continue  →" disabled={!selected} onPress={next}/></View></View>
}

function PhotoScreen({photoUri,shade,pick,take,preview,busy}:{photoUri:string,shade?:Shade,pick:()=>void,take:()=>void,preview:()=>void,busy:boolean}){
 return <View><TitleBlock eyebrow="TRY YOUR SHADE" title="Add your photo" copy={`We’ll use one clear photo to preview ${shade?.name||'your selected color'} while keeping your face and features untouched.`}/>{photoUri?<View style={styles.photoStage}><Image source={{uri:photoUri}} style={styles.photo}/><View style={styles.photoTag}><Text style={styles.photoTagText}>PHOTO READY</Text></View></View>:<View style={styles.photoPlaceholder}><View style={styles.faceGuide}><View style={styles.head}/><View style={styles.shoulders}/></View><Text style={styles.placeholderTitle}>Use a clear, front-facing photo</Text><Text style={styles.placeholderCopy}>Natural light works best. Keep hair visible from roots to ends.</Text></View>}<View style={styles.dual}><Pressable style={styles.secondary} onPress={pick}><Text style={styles.secondaryText}>Choose Photo</Text></Pressable><Pressable style={styles.secondary} onPress={take}><Text style={styles.secondaryText}>Camera</Text></Pressable></View><View style={styles.ctaGap}><PrimaryButton label={busy?'Creating preview…':'Generate AI Preview  →'} disabled={!photoUri||busy} onPress={preview}/></View></View>
}

function PreviewScreen({source,preview,shade,notice,retry,saved,save}:{source:string,preview:string,shade?:Shade,notice:string,retry:()=>void,saved:boolean,save:()=>void}){
 return <View><TitleBlock eyebrow="YOUR PREVIEW" title="Meet your shade" copy={shade?`${shade.name} · Level ${shade.level} · ${shade.tone}`:undefined}/><View style={styles.resultCard}><Image source={{uri:preview}} style={styles.resultImage}/><View style={styles.resultOverlay}><Text style={styles.resultShade}>{shade?.name}</Text><Text style={styles.resultMeta}>AI HAIR COLOR PREVIEW</Text></View></View>{source?<View style={styles.beforeAfter}><View style={styles.miniResult}><Image source={{uri:source}} style={styles.miniImage}/><Text style={styles.miniLabel}>BEFORE</Text></View><View style={styles.miniResult}><Image source={{uri:preview}} style={styles.miniImage}/><Text style={styles.miniLabel}>AFTER</Text></View></View>:null}{notice?<View style={styles.notice}><Text style={styles.noticeTitle}>Preview service</Text><Text style={styles.noticeText}>{notice}</Text><Pressable onPress={retry}><Text style={styles.noticeLink}>Try again</Text></Pressable></View>:null}<View style={styles.dual}><Pressable style={styles.secondary} onPress={save}><Text style={styles.secondaryText}>{saved?'♥ Saved':'♡ Save Shade'}</Text></Pressable><Pressable style={styles.secondary}><Text style={styles.secondaryText}>Compare</Text></Pressable></View></View>
}

function SavedScreen({saved,open}:{saved:Shade[],open:(x:Shade)=>void}){
 return <View><TitleBlock eyebrow="YOUR PALETTE" title="Saved shades" copy="A private collection of colors worth revisiting."/>{saved.length?<View style={styles.shadeGrid}>{saved.map(x=><Pressable key={x.id} onPress={()=>open(x)} style={styles.shadeCard}><View style={styles.shadeVisual}><HairTexture base={x.hex} accent="#EED9CA"/></View><Text style={styles.shadeName}>{x.name}</Text><Text style={styles.shadeMeta}>{x.family} · Level {x.level}</Text></Pressable>)}</View>:<View style={styles.emptySaved}><Text style={styles.emptyGlyph}>♡</Text><Text style={styles.emptyTitle}>Your palette is waiting</Text><Text style={styles.emptyCopy}>Save shades while you explore and they’ll appear here.</Text></View>}</View>
}

function MoreScreen(){return <View><TitleBlock eyebrow="KÜBRA HAIR ATELIER" title="More" copy="A quiet space for preferences, help, and future atelier tools."/><View style={styles.moreList}>{['Color journey','Photo & privacy','AI preview status','About Kübra Hair Atelier'].map(x=><View key={x} style={styles.moreRow}><Text style={styles.moreText}>{x}</Text><Text style={styles.moreArrow}>›</Text></View>)}</View></View>}

const styles=StyleSheet.create({
 app:{flex:1,backgroundColor:C.bg},statusSpace:{height:Platform.OS==='android'?(NativeStatusBar.currentHeight??24):10},scroll:{paddingHorizontal:20,paddingTop:8,paddingBottom:120},
 splash:{flex:1,backgroundColor:C.bg,alignItems:'center'},splashHero:{width:'100%',height:'74%',overflow:'hidden',alignItems:'center',justifyContent:'center'},splashVeil:{...StyleSheet.absoluteFillObject,backgroundColor:'rgba(44,29,24,.20)'},splashBrand:{position:'absolute',alignItems:'center',justifyContent:'center',backgroundColor:'rgba(248,243,236,.86)',paddingVertical:24,paddingHorizontal:38,borderRadius:2},splashTag:{marginTop:42,fontSize:9,letterSpacing:3.1,color:C.muted},
 hairGlow:{position:'absolute',width:'45%',height:'145%',top:'-20%',left:'30%',borderRadius:160,opacity:.35,transform:[{rotate:'16deg'}]},hairLine:{position:'absolute',width:18,height:'160%',borderRadius:50,backgroundColor:'#FFF'},hairShade:{position:'absolute',right:-60,bottom:-50,width:'62%',height:'90%',borderRadius:180,backgroundColor:'rgba(31,19,16,.18)',transform:[{rotate:'12deg'}]},
 wordmark:{fontFamily:'serif',fontSize:28,fontWeight:'700',letterSpacing:5.5,color:C.ink},wordmarkSub:{fontSize:8,letterSpacing:4.4,color:C.muted,marginTop:3},topBar:{height:66,flexDirection:'row',alignItems:'center',justifyContent:'space-between',paddingHorizontal:18},iconButton:{width:42,height:42,alignItems:'center',justifyContent:'center'},backIcon:{fontSize:31,color:C.ink,fontWeight:'300'},heart:{fontSize:24,color:C.ink},
 bottomNav:{position:'absolute',left:0,right:0,bottom:0,height:82,backgroundColor:'rgba(251,248,243,.97)',borderTopWidth:1,borderTopColor:C.line,flexDirection:'row',paddingBottom:8},navItem:{flex:1,alignItems:'center',justifyContent:'center'},navIcon:{fontSize:20,color:'#A99A90'},navLabel:{fontSize:9,marginTop:5,color:'#A99A90'},navOn:{color:C.dark,fontWeight:'700'},
 homeHead:{alignItems:'center',paddingTop:12},heroCopy:{width:'100%',paddingTop:44,paddingBottom:26},homeEyebrow:{fontSize:9,letterSpacing:2.7,color:C.rose,fontWeight:'700'},homeTitle:{fontFamily:'serif',fontSize:48,lineHeight:52,color:C.ink,marginTop:10},homeCopy:{fontSize:13,lineHeight:21,color:C.muted,marginTop:10,maxWidth:310},editorialStack:{gap:14},featureCard:{height:300,borderRadius:28,overflow:'hidden'},featureCardSmall:{height:198,borderRadius:28,overflow:'hidden'},featureImage:{flex:1,justifyContent:'flex-end'},featureShade:{...StyleSheet.absoluteFillObject,backgroundColor:'rgba(38,24,19,.16)'},featureLabel:{padding:24},featureKicker:{fontSize:9,letterSpacing:2.2,color:'#F5ECE4',fontWeight:'700'},featureTitle:{fontFamily:'serif',fontSize:30,color:'#FFF',marginTop:6},featureArrow:{position:'absolute',right:24,bottom:24,fontSize:25,color:'#FFF'},
 titleBlock:{paddingTop:22,paddingBottom:24},eyebrow:{fontSize:9,letterSpacing:2.7,color:C.rose,fontWeight:'700'},bigTitle:{fontFamily:'serif',fontSize:39,lineHeight:43,color:C.ink,marginTop:10},copy:{fontSize:13,lineHeight:20,color:C.muted,marginTop:10,maxWidth:330},
 familyGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:18},familyItem:{width:'31%',alignItems:'center'},familyVisual:{width:'100%',aspectRatio:1,borderRadius:22,overflow:'hidden',borderWidth:1,borderColor:'rgba(60,40,32,.05)'},familyVisualOn:{borderColor:C.dark,borderWidth:2},familyName:{fontSize:11,color:C.ink,marginTop:8},familyNameOn:{fontWeight:'700'},check:{position:'absolute',right:7,top:7,width:26,height:26,borderRadius:13,backgroundColor:C.white,alignItems:'center',justifyContent:'center',shadowColor:'#000',shadowOpacity:.12,shadowRadius:5,elevation:3},checkText:{fontSize:13,color:C.dark,fontWeight:'700'},
 pills:{flexDirection:'row',gap:8,marginBottom:18},pill:{paddingHorizontal:15,paddingVertical:9,borderRadius:99,borderWidth:1,borderColor:C.line,backgroundColor:C.paper2},pillOn:{paddingHorizontal:15,paddingVertical:9,borderRadius:99,backgroundColor:C.dark},pillText:{fontSize:10,color:C.muted},pillOnText:{fontSize:10,color:'#FFF'},shadeGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:16},shadeCard:{width:'48.3%',backgroundColor:C.paper,borderRadius:23,padding:9,borderWidth:1,borderColor:C.line},shadeCardOn:{borderColor:C.dark,borderWidth:2},shadeVisual:{width:'100%',aspectRatio:.92,borderRadius:17,overflow:'hidden'},favBubble:{position:'absolute',left:7,top:7,width:30,height:30,borderRadius:15,backgroundColor:'rgba(255,253,249,.88)',alignItems:'center',justifyContent:'center'},favText:{color:C.dark,fontSize:16},shadeName:{fontFamily:'serif',fontSize:17,lineHeight:20,color:C.ink,marginTop:10},shadeMeta:{fontSize:9.5,color:C.muted,marginTop:4,marginBottom:3,textTransform:'capitalize'},ctaGap:{marginTop:24},primary:{height:58,borderRadius:22,backgroundColor:C.dark,alignItems:'center',justifyContent:'center'},primaryDisabled:{opacity:.32},primaryText:{fontSize:13,color:'#FFF',fontWeight:'700',letterSpacing:.2},
 photoPlaceholder:{height:360,borderRadius:30,backgroundColor:C.paper,borderWidth:1,borderColor:C.line,alignItems:'center',justifyContent:'center',padding:28},faceGuide:{width:150,height:180,alignItems:'center',justifyContent:'center',opacity:.42},head:{width:76,height:94,borderRadius:45,borderWidth:1.5,borderColor:C.muted},shoulders:{position:'absolute',bottom:4,width:145,height:70,borderTopLeftRadius:75,borderTopRightRadius:75,borderWidth:1.5,borderBottomWidth:0,borderColor:C.muted},placeholderTitle:{fontFamily:'serif',fontSize:22,color:C.ink,textAlign:'center'},placeholderCopy:{fontSize:12,lineHeight:18,color:C.muted,textAlign:'center',marginTop:8},photoStage:{height:410,borderRadius:30,overflow:'hidden',backgroundColor:C.paper},photo:{width:'100%',height:'100%',resizeMode:'cover'},photoTag:{position:'absolute',left:18,bottom:18,backgroundColor:'rgba(251,248,243,.92)',paddingHorizontal:13,paddingVertical:8,borderRadius:99},photoTagText:{fontSize:8,letterSpacing:1.8,color:C.dark,fontWeight:'700'},dual:{flexDirection:'row',gap:10,marginTop:14},secondary:{flex:1,height:52,borderRadius:18,borderWidth:1,borderColor:C.champagne,backgroundColor:C.paper,alignItems:'center',justifyContent:'center'},secondaryText:{fontSize:11.5,color:C.dark,fontWeight:'600'},
 resultCard:{height:470,borderRadius:30,overflow:'hidden',backgroundColor:C.paper},resultImage:{width:'100%',height:'100%',resizeMode:'cover'},resultOverlay:{position:'absolute',left:0,right:0,bottom:0,padding:22,backgroundColor:'rgba(38,24,19,.25)'},resultShade:{fontFamily:'serif',fontSize:28,color:'#FFF'},resultMeta:{fontSize:8,letterSpacing:2.1,color:'#F4E9E0',marginTop:4},beforeAfter:{flexDirection:'row',gap:10,marginTop:12},miniResult:{flex:1,height:180,borderRadius:20,overflow:'hidden',backgroundColor:C.paper},miniImage:{width:'100%',height:'100%',resizeMode:'cover'},miniLabel:{position:'absolute',left:10,bottom:10,fontSize:8,letterSpacing:1.8,color:'#FFF',fontWeight:'700'},notice:{marginTop:14,padding:18,borderRadius:20,backgroundColor:C.paper,borderWidth:1,borderColor:C.line},noticeTitle:{fontFamily:'serif',fontSize:18,color:C.ink},noticeText:{fontSize:11.5,lineHeight:18,color:C.muted,marginTop:5},noticeLink:{fontSize:11,color:C.dark,fontWeight:'700',marginTop:9},
 emptySaved:{paddingVertical:90,alignItems:'center'},emptyGlyph:{fontSize:44,color:C.champagne},emptyTitle:{fontFamily:'serif',fontSize:25,color:C.ink,marginTop:10},emptyCopy:{fontSize:12.5,lineHeight:19,color:C.muted,textAlign:'center',maxWidth:280,marginTop:8},moreList:{backgroundColor:C.paper,borderRadius:24,overflow:'hidden',borderWidth:1,borderColor:C.line},moreRow:{minHeight:58,paddingHorizontal:18,flexDirection:'row',alignItems:'center',justifyContent:'space-between',borderBottomWidth:1,borderBottomColor:C.line},moreText:{fontSize:13,color:C.ink},moreArrow:{fontSize:22,color:C.muted},
 modalBack:{flex:1,backgroundColor:'rgba(43,28,23,.42)',alignItems:'center',justifyContent:'center',padding:28},exitCard:{width:'100%',maxWidth:355,backgroundColor:C.paper,borderRadius:30,padding:25,alignItems:'center'},exitGlyph:{width:50,height:50,borderRadius:25,borderWidth:1,borderColor:C.champagne,alignItems:'center',justifyContent:'center'},exitGlyphText:{fontSize:28,color:C.rose},exitTitle:{fontFamily:'serif',fontSize:28,lineHeight:32,color:C.ink,textAlign:'center',marginTop:17},exitCopy:{fontSize:12.5,lineHeight:19,color:C.muted,textAlign:'center',marginTop:9,maxWidth:280},exitButtons:{flexDirection:'row',gap:10,width:'100%',marginTop:20},stay:{flex:1,height:52,borderRadius:18,borderWidth:1,borderColor:C.champagne,alignItems:'center',justifyContent:'center'},exit:{flex:1,height:52,borderRadius:18,backgroundColor:C.dark,alignItems:'center',justifyContent:'center'},stayText:{fontSize:12,color:C.dark,fontWeight:'700'},exitText:{fontSize:12,color:'#FFF',fontWeight:'700'},exitTag:{fontSize:8,letterSpacing:2.3,color:C.muted,marginTop:18},
});

export default App;
