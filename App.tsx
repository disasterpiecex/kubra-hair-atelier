import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Animated,
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

type Screen = 'home' | 'family' | 'shade' | 'photo' | 'adjust' | 'preview' | 'saved' | 'more';
type Family = { id: string; name: string; color: string; accent: string };
type Shade = { id: string; family: string; name: string; hex: string; level: string; tone: string; saturation: string };

const C = {
  bg: '#F5EFE7',
  paper: '#FFFDF9',
  paper2: '#FAF5EF',
  ink: '#31231E',
  muted: '#8B786D',
  line: '#E8DDD2',
  dark: '#493228',
  rose: '#AE7C70',
  champagne: '#D8C4B3',
  taupe: '#B89E8C',
  white: '#FFFFFF',
};

const families: Family[] = [
  { id: 'blonde', name: 'Blonde', color: '#D7BC86', accent: '#F4DEAA' },
  { id: 'brown', name: 'Brown', color: '#76543E', accent: '#B78867' },
  { id: 'red', name: 'Red', color: '#8F342F', accent: '#C9675D' },
  { id: 'copper', name: 'Copper', color: '#B76135', accent: '#E89B65' },
  { id: 'black', name: 'Black', color: '#272220', accent: '#61524B' },
  { id: 'blue', name: 'Blue', color: '#2B466B', accent: '#7390B7' },
  { id: 'pink', name: 'Pink', color: '#B66C79', accent: '#E6A6AE' },
  { id: 'violet', name: 'Violet', color: '#62486D', accent: '#A28AAF' },
  { id: 'green', name: 'Green', color: '#4F6853', accent: '#91A693' },
  { id: 'grey', name: 'Grey', color: '#7C7A76', accent: '#BAB4AD' },
  { id: 'pastel', name: 'Pastel', color: '#C9B9CB', accent: '#E7D7E0' },
];

const shades: Shade[] = [
  ['blonde','dark-ash-blonde','Dark Ash Blonde','#9B825F','6','ash','soft'],
  ['blonde','beige-blonde','Beige Blonde','#C5A777','8','beige','medium'],
  ['blonde','golden-blonde','Golden Blonde','#D2A759','8','golden','high'],
  ['blonde','champagne-blonde','Champagne Blonde','#D8C19A','9','neutral warm','soft'],
  ['blonde','pearl-blonde','Pearl Blonde','#DCCFB7','9','pearl','soft'],
  ['blonde','icy-blonde','Icy Blonde','#E6DFD4','10','cool','soft'],
  ['brown','espresso','Espresso','#49332A','4','neutral','deep'],
  ['brown','mocha','Mocha','#6C4E3D','5','neutral cool','medium'],
  ['brown','chocolate','Chocolate','#78523C','5','warm','medium'],
  ['brown','mushroom','Mushroom Brown','#75675B','6','cool neutral','soft'],
  ['brown','caramel','Caramel Brown','#9B6845','6','warm','medium'],
  ['brown','honey-brown','Honey Brown','#B17B4D','7','warm gold','medium'],
  ['red','burgundy','Burgundy','#642D37','4','wine','deep'],
  ['red','dark-cherry','Dark Cherry','#702830','4','cool red','deep'],
  ['red','cherry','Cherry Red','#A52E32','5','red','high'],
  ['red','ruby','Ruby','#A64046','5','cool red','high'],
  ['red','wine','Wine Red','#77333C','4','wine','deep'],
  ['red','auburn','Auburn','#834333','5','warm red','medium'],
  ['copper','dark-copper','Dark Copper','#7C462E','5','copper','deep'],
  ['copper','classic-copper','Classic Copper','#AA562F','7','copper','high'],
  ['copper','soft-ginger','Soft Ginger','#C87B50','8','warm copper','soft'],
  ['copper','apricot','Apricot Copper','#D98E65','8','peach copper','soft'],
  ['copper','copper-gold','Copper Gold','#C57A3C','8','gold copper','medium'],
  ['black','natural-black','Natural Black','#24201F','2','neutral','deep'],
  ['black','soft-black','Soft Black','#312A27','2','neutral warm','deep'],
  ['black','blue-black','Blue Black','#202633','2','blue cool','deep'],
  ['black','espresso-black','Espresso Black','#302724','2','warm neutral','deep'],
  ['blue','midnight-blue','Midnight Blue','#23304D','3','cool blue','deep'],
  ['blue','navy','Navy','#2B4169','4','cool blue','deep'],
  ['blue','deep-cobalt','Deep Cobalt','#355A91','5','cobalt','high'],
  ['blue','denim','Denim','#607797','6','muted blue','soft'],
  ['blue','sapphire','Sapphire','#2F5C9A','5','jewel blue','high'],
  ['blue','electric-blue','Electric Blue','#3F78BC','7','vivid blue','high'],
  ['pink','dusty-rose','Dusty Rose','#A96D77','7','rose','soft'],
  ['pink','rose-gold','Rose Gold','#C98E8C','8','warm rose','soft'],
  ['pink','bubblegum','Bubblegum','#DB849C','8','pink','high'],
  ['pink','hot-pink','Hot Pink','#D65382','7','vivid pink','high'],
  ['violet','deep-plum','Deep Plum','#4C354D','4','plum','deep'],
  ['violet','blackberry','Blackberry','#513C58','4','berry violet','deep'],
  ['violet','amethyst','Amethyst','#745887','6','violet','medium'],
  ['violet','orchid','Orchid','#9B70A8','7','orchid','medium'],
  ['violet','lavender','Lavender','#A791B3','8','lavender','soft'],
  ['green','forest','Forest Green','#3D5542','4','green','deep'],
  ['green','emerald','Emerald','#3F705B','5','jewel green','high'],
  ['green','teal','Teal','#447A75','6','teal','medium'],
  ['green','sage','Sage','#879783','7','muted green','soft'],
  ['green','mint','Mint','#A9C0A5','9','mint','soft'],
  ['grey','charcoal','Charcoal','#5E5C5B','4','cool grey','deep'],
  ['grey','smoky-grey','Smoky Grey','#85817D','6','smoke','soft'],
  ['grey','soft-silver','Soft Silver','#AAA8A4','8','silver','soft'],
  ['grey','pearl-silver','Pearl Silver','#C0BDB7','9','pearl silver','soft'],
  ['pastel','lavender-mist','Lavender Mist','#C7B5CA','9','pastel violet','soft'],
  ['pastel','peach-mist','Peach Mist','#E4B7A5','9','pastel peach','soft'],
  ['pastel','blush-pink','Blush Pink','#DDB5BF','9','pastel pink','soft'],
  ['pastel','powder-blue','Powder Blue','#B2C6D6','9','pastel blue','soft'],
  ['pastel','mint-cream','Mint Cream','#C7D8C5','9','pastel green','soft'],
].map(([family,id,name,hex,level,tone,saturation])=>({family,id,name,hex,level,tone,saturation})) as Shade[];

const SESSION = 'kha:v1.1.3:session';
const SAVED = 'kha:v1.1.3:saved';

const fill = { position:'absolute' as const, left:0, right:0, top:0, bottom:0 };

function HairTexture({base,accent='#FFFFFF',soft=false}:{base:string;accent?:string;soft?:boolean}){
  return <View style={[fill,{backgroundColor:base,overflow:'hidden'}]}>
    <View style={[styles.waveBlob,{backgroundColor:accent,opacity:soft?.16:.2}]} />
    {Array.from({length:11}).map((_,i)=><View key={i} style={[styles.strand,{left:-28+i*25,top:-30+i*4,opacity:.08+(i%4)*.025,transform:[{rotate:`${18+i*1.8}deg`}]}]} />)}
    <View style={styles.textureShadow}/>
  </View>
}

function Wordmark({large=false}:{large?:boolean}){
  return <View style={styles.wordmarkWrap}><Text style={[styles.wordmark,large&&styles.wordmarkLarge]}>KÜBRA</Text><Text style={[styles.wordmarkSub,large&&styles.wordmarkSubLarge]}>HAIR ATELIER</Text></View>
}

function Primary({label,onPress,disabled=false}:{label:string;onPress:()=>void;disabled?:boolean}){
  return <Pressable onPress={onPress} disabled={disabled} style={[styles.primary,disabled&&styles.primaryDisabled]}><Text style={styles.primaryText}>{label}</Text></Pressable>
}

function TopBar({onBack,onSaved}:{onBack:()=>void;onSaved:()=>void}){
  return <View style={styles.topBar}><Pressable onPress={onBack} style={styles.topButton}><Text style={styles.back}>‹</Text></Pressable><Wordmark/><Pressable onPress={onSaved} style={styles.topButton}><Text style={styles.heart}>♡</Text></Pressable></View>
}

function BottomNav({screen,onGo}:{screen:Screen;onGo:(s:Screen)=>void}){
  const exploreActive=['family','shade','photo','adjust','preview'].includes(screen);
  return <View style={styles.bottomNav}>
    {[
      ['home','⌂','Home',screen==='home'],
      ['family','◫','Explore',exploreActive],
      ['saved','♡','Saved',screen==='saved'],
      ['more','•••','More',screen==='more'],
    ].map(([id,icon,label,active])=><Pressable key={String(id)} onPress={()=>onGo(id as Screen)} style={styles.navItem}><Text style={[styles.navIcon,active&&styles.navOn]}>{icon}</Text><Text style={[styles.navLabel,active&&styles.navOn]}>{label}</Text></Pressable>)}
  </View>
}

function TitleBlock({eyebrow,title,copy}:{eyebrow:string;title:string;copy?:string}){
  return <View style={styles.titleBlock}><Text style={styles.eyebrow}>{eyebrow}</Text><Text style={styles.title}>{title}</Text>{copy?<Text style={styles.copy}>{copy}</Text>:null}</View>
}

function Home({go}:{go:(s:Screen)=>void}){
  return <View>
    <View style={styles.homeWordmark}><Wordmark/></View>
    <View style={styles.homeIntro}><Text style={styles.homeEyebrow}>KÜBRA HAIR ATELIER</Text><Text style={styles.homeTitle}>A more you</Text><Text style={styles.homeCopy}>Explore color through texture, tone and light. Find the shade that feels unmistakably yours.</Text></View>
    <View style={styles.homeCards}>
      <Pressable onPress={()=>go('family')} style={styles.heroCard}><HairTexture base="#76594A" accent="#D4B6A5"/><View style={styles.cardShade}/><View style={styles.cardCopy}><Text style={styles.cardKicker}>DISCOVER</Text><Text style={styles.cardTitle}>Explore Shades</Text><Text style={styles.cardArrow}>→</Text></View></Pressable>
      <Pressable onPress={()=>go('photo')} style={styles.smallHero}><HairTexture base="#A77E6D" accent="#E7CBBF" soft/><View style={styles.cardShade}/><View style={styles.cardCopy}><Text style={styles.cardKicker}>PERSONALIZE</Text><Text style={styles.cardTitleSmall}>Try with Your Photo</Text><Text style={styles.cardArrow}>→</Text></View></Pressable>
      <Pressable onPress={()=>go('family')} style={styles.smallHero}><HairTexture base="#C5A489" accent="#F0D7C3" soft/><View style={styles.cardShade}/><View style={styles.cardCopy}><Text style={styles.cardKicker}>ATELIER</Text><Text style={styles.cardTitleSmall}>Create Custom Shade</Text><Text style={styles.cardArrow}>→</Text></View></Pressable>
    </View>
  </View>
}

function FamilyScreen({selected,choose,next}:{selected:string;choose:(id:string)=>void;next:()=>void}){
  return <View><TitleBlock eyebrow="COLOR INSPIRES YOU" title="Choose a color family" copy="Begin with the mood. You can refine the exact shade next."/>
    <View style={styles.familyGrid}>{families.map(f=>{const on=f.id===selected;return <Pressable key={f.id} onPress={()=>choose(f.id)} style={styles.familyItem}><View style={[styles.familyVisual,on&&styles.familyVisualOn]}><HairTexture base={f.color} accent={f.accent}/>{on?<View style={styles.check}><Text style={styles.checkText}>✓</Text></View>:null}</View><Text style={[styles.familyLabel,on&&styles.familyLabelOn]}>{f.name}</Text></Pressable>})}</View>
    <View style={styles.cta}><Primary label="Next →" onPress={next} disabled={!selected}/></View>
  </View>
}

function ShadeScreen({family,list,selected,saved,choose,toggle,next}:{family?:Family;list:Shade[];selected:string;saved:string[];choose:(id:string)=>void;toggle:(id:string)=>void;next:()=>void}){
  return <View><TitleBlock eyebrow="YOUR SHADE" title={`${family?.name||'Selected'} shades`} copy="Tap a color to select it. Save the ones you want to revisit."/>
    <View style={styles.filterRow}><View style={styles.filterOn}><Text style={styles.filterOnText}>All</Text></View><View style={styles.filter}><Text style={styles.filterText}>Cool</Text></View><View style={styles.filter}><Text style={styles.filterText}>Warm</Text></View></View>
    <View style={styles.shadeGrid}>{list.map(x=>{const on=x.id===selected;const fav=saved.includes(x.id);return <Pressable key={x.id} onPress={()=>choose(x.id)} style={styles.shadeItem}><View style={[styles.shadeVisual,on&&styles.shadeVisualOn]}><HairTexture base={x.hex} accent="#F4E7DD"/>
      <Pressable onPress={()=>toggle(x.id)} style={styles.fav}><Text style={styles.favText}>{fav?'♥':'♡'}</Text></Pressable>{on?<View style={styles.check}><Text style={styles.checkText}>✓</Text></View>:null}</View>
      <Text numberOfLines={2} style={[styles.shadeName,on&&styles.shadeNameOn]}>{x.name}</Text><Text style={styles.shadeMeta}>L{x.level} · {x.tone}</Text></Pressable>})}</View>
    <View style={styles.cta}><Primary label="Continue →" onPress={next} disabled={!selected}/></View>
  </View>
}

function PhotoScreen({photoUri,pick,take,next}:{photoUri:string;pick:()=>void;take:()=>void;next:()=>void}){
  return <View><TitleBlock eyebrow="TRY IT ON" title="Add your photo" copy="Use a clear, well-lit image with your hair fully visible."/>
    {photoUri?<View style={styles.photoStage}><Image source={{uri:photoUri}} style={styles.photo}/><View style={styles.photoLabel}><Text style={styles.photoLabelText}>YOUR PHOTO</Text></View></View>
    :<View style={styles.photoEmpty}><View style={styles.faceIcon}><View style={styles.faceHead}/><View style={styles.faceShoulders}/></View><Text style={styles.photoEmptyTitle}>Your photo becomes the canvas</Text><Text style={styles.photoEmptyCopy}>A front-facing portrait gives the most natural preview.</Text></View>}
    <View style={styles.dual}><Pressable onPress={pick} style={styles.secondary}><Text style={styles.secondaryText}>Choose Photo</Text></Pressable><Pressable onPress={take} style={styles.secondary}><Text style={styles.secondaryText}>Take Photo</Text></Pressable></View>
    <View style={styles.cta}><Primary label="Continue →" onPress={next} disabled={!photoUri}/></View>
  </View>
}

function AdjustScreen({photoUri,shade,next}:{photoUri:string;shade?:Shade;next:()=>void}){
  return <View><TitleBlock eyebrow="ADJUST PHOTO" title="Frame your hair" copy="Keep your face centered and make sure the full outline of your hair is visible."/>
    <View style={styles.adjustStage}><Image source={{uri:photoUri}} style={styles.photo}/><View style={styles.guideOval}/><View style={styles.guideTop}/><View style={styles.adjustTag}><View style={[styles.dot,{backgroundColor:shade?.hex||C.rose}]}/><Text style={styles.adjustTagText}>{shade?.name||'Selected shade'}</Text></View></View>
    <View style={styles.adjustHint}><Text style={styles.adjustHintTitle}>Looks good?</Text><Text style={styles.adjustHintText}>You can change the shade later without uploading your photo again.</Text></View>
    <View style={styles.cta}><Primary label="Generate AI Preview →" onPress={next}/></View>
  </View>
}

function PreviewScreen({source,preview,shade,notice,busy,retry,save,saved}:{source:string;preview:string;shade?:Shade;notice:string;busy:boolean;retry:()=>void;save:()=>void;saved:boolean}){
  return <View><TitleBlock eyebrow="YOUR RESULT" title="A glimpse of your next shade" copy="Compare your original with the generated result."/>
    <View style={styles.resultCard}><Image source={{uri:preview}} style={styles.resultImage}/><View style={styles.resultScrim}/><View style={styles.resultCopy}><Text style={styles.resultName}>{shade?.name||'Your shade'}</Text><Text style={styles.resultMeta}>LEVEL {shade?.level||'—'} · {(shade?.tone||'').toUpperCase()}</Text></View></View>
    <View style={styles.beforeAfter}><View style={styles.mini}><Image source={{uri:source}} style={styles.photo}/><Text style={styles.miniLabel}>BEFORE</Text></View><View style={styles.mini}><Image source={{uri:preview}} style={styles.photo}/><Text style={styles.miniLabel}>AFTER</Text></View></View>
    {notice?<View style={styles.notice}><Text style={styles.noticeTitle}>AI preview status</Text><Text style={styles.noticeText}>{notice}</Text><Pressable onPress={retry}><Text style={styles.noticeLink}>{busy?'Generating…':'Try again'}</Text></Pressable></View>:null}
    <View style={styles.dual}><Pressable onPress={save} style={styles.secondary}><Text style={styles.secondaryText}>{saved?'♥ Saved':'♡ Save Shade'}</Text></Pressable><Pressable style={styles.secondary}><Text style={styles.secondaryText}>Compare</Text></Pressable></View>
  </View>
}

function SavedScreen({items,open}:{items:Shade[];open:(x:Shade)=>void}){
  return <View><TitleBlock eyebrow="YOUR PALETTE" title="Saved shades" copy="A private collection of colors worth revisiting."/>{items.length?<View style={styles.savedGrid}>{items.map(x=><Pressable key={x.id} onPress={()=>open(x)} style={styles.savedCard}><View style={styles.savedVisual}><HairTexture base={x.hex} accent="#F1DED2"/></View><Text style={styles.savedName}>{x.name}</Text><Text style={styles.savedMeta}>{x.family} · L{x.level}</Text></Pressable>)}</View>:<View style={styles.emptySaved}><Text style={styles.emptyHeart}>♡</Text><Text style={styles.emptyTitle}>Your palette is waiting</Text><Text style={styles.emptyCopy}>Save shades while you explore and they’ll appear here.</Text></View>}</View>
}

function MoreScreen(){return <View><TitleBlock eyebrow="KÜBRA HAIR ATELIER" title="More" copy="Preferences, help and future atelier tools."/><View style={styles.moreCard}>{['Color journey','Photo & privacy','AI preview status','About Kübra Hair Atelier'].map((x,i)=><View key={x} style={[styles.moreRow,i===3&&{borderBottomWidth:0}]}><Text style={styles.moreText}>{x}</Text><Text style={styles.moreArrow}>›</Text></View>)}</View></View>}

export default function App(){
  const [screen,setScreen]=useState<Screen>('home');
  const [familyId,setFamilyId]=useState('');
  const [shadeId,setShadeId]=useState('');
  const [photoUri,setPhotoUri]=useState('');
  const [previewUri,setPreviewUri]=useState('');
  const [savedIds,setSavedIds]=useState<string[]>([]);
  const [showExit,setShowExit]=useState(false);
  const [showSplash,setShowSplash]=useState(true);
  const [notice,setNotice]=useState('');
  const [busy,setBusy]=useState(false);
  const splashOpacity=useRef(new Animated.Value(1)).current;

  const family=useMemo(()=>families.find(x=>x.id===familyId),[familyId]);
  const shade=useMemo(()=>shades.find(x=>x.id===shadeId),[shadeId]);
  const familyShades=useMemo(()=>shades.filter(x=>x.family===familyId),[familyId]);

  useEffect(()=>{(async()=>{try{const s=JSON.parse(await AsyncStorage.getItem(SESSION)||'{}');setFamilyId(s.familyId||'');setShadeId(s.shadeId||'');setPhotoUri(s.photoUri||'');setSavedIds(JSON.parse(await AsyncStorage.getItem(SAVED)||'[]'))}catch{}})()},[]);
  useEffect(()=>{AsyncStorage.setItem(SESSION,JSON.stringify({familyId,shadeId,photoUri})).catch(()=>{})},[familyId,shadeId,photoUri]);
  useEffect(()=>{AsyncStorage.setItem(SAVED,JSON.stringify(savedIds)).catch(()=>{})},[savedIds]);
  useEffect(()=>{const t=setTimeout(()=>Animated.timing(splashOpacity,{toValue:0,duration:300,useNativeDriver:true}).start(()=>setShowSplash(false)),1200);return()=>clearTimeout(t)},[splashOpacity]);
  useEffect(()=>{if(Platform.OS!=='android')return;const sub=BackHandler.addEventListener('hardwareBackPress',()=>{if(showExit){setShowExit(false);return true}if(screen==='home'){setShowExit(true);return true}goBack();return true});return()=>sub.remove()},[screen,showExit]);

  function goBack(){const p:Record<Screen,Screen>={home:'home',family:'home',shade:'family',photo:'shade',adjust:'photo',preview:'adjust',saved:'home',more:'home'};setScreen(p[screen])}
  function go(s:Screen){setScreen(s)}
  function chooseFamily(id:string){setFamilyId(id);setShadeId('');setPreviewUri('');setNotice('')}
  function chooseShade(id:string){setShadeId(id);setPreviewUri('');setNotice('')}
  function toggleSaved(id:string){setSavedIds(x=>x.includes(id)?x.filter(y=>y!==id):[...x,id])}

  async function pick(){const r=await ImagePicker.launchImageLibraryAsync({quality:.9,allowsEditing:false});if(!r.canceled&&r.assets?.[0]?.uri){setPhotoUri(r.assets[0].uri);setPreviewUri('');setNotice('')}}
  async function take(){const p=await ImagePicker.requestCameraPermissionsAsync();if(!p.granted)return;const r=await ImagePicker.launchCameraAsync({quality:.9});if(!r.canceled&&r.assets?.[0]?.uri){setPhotoUri(r.assets[0].uri);setPreviewUri('');setNotice('')}}
  async function preview(){if(!photoUri||!shade)return;setBusy(true);setNotice('');try{const r=await generateHairPreview(photoUri,shade);setPreviewUri(r.previewDataUrl||photoUri);if(r.provider==='mock-local')setNotice('Live AI is not connected in this build yet. Your original photo is shown instead.');setScreen('preview')}catch(e:any){setPreviewUri(photoUri);setNotice(e?.message||'AI preview is currently unavailable.');setScreen('preview')}finally{setBusy(false)}}

  if(showSplash)return <Animated.View style={[styles.splash,{opacity:splashOpacity}]}><StatusBar style="dark"/><View style={styles.splashImage}><HairTexture base="#947463" accent="#D7B8A9"/><View style={styles.splashDark}/><View style={styles.splashLogo}><Wordmark large/></View></View><Text style={styles.splashTag}>BEAUTY LIVES IN YOUR SHADE</Text></Animated.View>;

  const body = screen==='home'?<Home go={go}/>
    :screen==='family'?<FamilyScreen selected={familyId} choose={chooseFamily} next={()=>setScreen('shade')}/>
    :screen==='shade'?<ShadeScreen family={family} list={familyShades} selected={shadeId} saved={savedIds} choose={chooseShade} toggle={toggleSaved} next={()=>setScreen('photo')}/>
    :screen==='photo'?<PhotoScreen photoUri={photoUri} pick={pick} take={take} next={()=>setScreen('adjust')}/>
    :screen==='adjust'?<AdjustScreen photoUri={photoUri} shade={shade} next={preview}/>
    :screen==='preview'?<PreviewScreen source={photoUri} preview={previewUri||photoUri} shade={shade} notice={notice} busy={busy} retry={preview} save={()=>shade&&toggleSaved(shade.id)} saved={shade? savedIds.includes(shade.id):false}/>
    :screen==='saved'?<SavedScreen items={shades.filter(x=>savedIds.includes(x.id))} open={x=>{setFamilyId(x.family);setShadeId(x.id);setScreen('shade')}}/>
    :<MoreScreen/>;

  return <View style={styles.app}><StatusBar style="dark"/><View style={styles.statusSpace}/>{screen!=='home'?<TopBar onBack={goBack} onSaved={()=>setScreen('saved')}/>:null}<ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={[styles.scroll,screen==='home'&&styles.scrollHome]}>{body}</ScrollView><BottomNav screen={screen} onGo={go}/>
    <Modal transparent visible={showExit} animationType="fade" onRequestClose={()=>setShowExit(false)}><View style={styles.modalBack}><View style={styles.exitCard}><View style={styles.exitGlyph}><Text style={styles.exitGlyphText}>〰</Text></View><Text style={styles.exitTitle}>Leave Kübra Hair Atelier?</Text><Text style={styles.exitCopy}>Your progress will be saved, so you can always come back.</Text><View style={styles.exitButtons}><Pressable onPress={()=>setShowExit(false)} style={styles.stay}><Text style={styles.stayText}>Stay</Text></Pressable><Pressable onPress={()=>BackHandler.exitApp()} style={styles.exit}><Text style={styles.exitText}>Exit</Text></Pressable></View><Text style={styles.exitTag}>BEAUTY LIVES IN YOUR SHADE</Text></View></View></Modal>
  </View>
}

const styles=StyleSheet.create({
  app:{flex:1,backgroundColor:C.bg},statusSpace:{height:Platform.OS==='android'?(NativeStatusBar.currentHeight??24):10},scroll:{paddingHorizontal:20,paddingTop:8,paddingBottom:118},scrollHome:{paddingTop:0},
  waveBlob:{position:'absolute',width:'47%',height:'150%',top:'-25%',left:'29%',borderRadius:180,transform:[{rotate:'14deg'}]},strand:{position:'absolute',width:18,height:'175%',borderRadius:50,backgroundColor:'#FFF'},textureShadow:{position:'absolute',right:-65,bottom:-55,width:'68%',height:'105%',borderRadius:190,backgroundColor:'rgba(28,17,14,.17)',transform:[{rotate:'12deg'}]},
  wordmarkWrap:{alignItems:'center'},wordmark:{fontFamily:'serif',fontWeight:'700',fontSize:20,letterSpacing:4.6,color:C.ink},wordmarkLarge:{fontSize:34,letterSpacing:7},wordmarkSub:{fontSize:7.5,letterSpacing:3.5,color:C.muted,marginTop:2},wordmarkSubLarge:{fontSize:9,letterSpacing:5},
  splash:{flex:1,backgroundColor:C.bg,alignItems:'center'},splashImage:{width:'100%',height:'77%',overflow:'hidden',alignItems:'center',justifyContent:'center'},splashDark:{...fill,backgroundColor:'rgba(44,28,23,.16)'},splashLogo:{backgroundColor:'rgba(250,245,239,.88)',paddingHorizontal:36,paddingVertical:24},splashTag:{marginTop:44,fontSize:9,letterSpacing:3.2,color:C.muted},
  topBar:{height:68,paddingHorizontal:18,flexDirection:'row',alignItems:'center',justifyContent:'space-between'},topButton:{width:42,height:42,alignItems:'center',justifyContent:'center'},back:{fontSize:31,color:C.dark,fontWeight:'300'},heart:{fontSize:24,color:C.dark},
  bottomNav:{position:'absolute',left:0,right:0,bottom:0,height:82,backgroundColor:'rgba(255,253,249,.97)',borderTopWidth:1,borderTopColor:C.line,flexDirection:'row',paddingBottom:8},navItem:{flex:1,alignItems:'center',justifyContent:'center'},navIcon:{fontSize:20,color:'#AD9D93'},navLabel:{fontSize:9,color:'#AD9D93',marginTop:5},navOn:{color:C.dark,fontWeight:'700'},
  homeWordmark:{alignItems:'center',paddingTop:8},homeIntro:{paddingTop:44,paddingBottom:28},homeEyebrow:{fontSize:9,letterSpacing:2.7,color:C.rose,fontWeight:'700'},homeTitle:{fontFamily:'serif',fontSize:49,lineHeight:52,color:C.ink,marginTop:10},homeCopy:{fontSize:13,lineHeight:21,color:C.muted,maxWidth:320,marginTop:10},homeCards:{gap:14},heroCard:{height:300,borderRadius:30,overflow:'hidden'},smallHero:{height:196,borderRadius:28,overflow:'hidden'},cardShade:{...fill,backgroundColor:'rgba(41,26,21,.16)'},cardCopy:{position:'absolute',left:24,right:24,bottom:23},cardKicker:{fontSize:9,letterSpacing:2.2,color:'#F9EFE7',fontWeight:'700'},cardTitle:{fontFamily:'serif',fontSize:31,color:'#FFF',marginTop:6},cardTitleSmall:{fontFamily:'serif',fontSize:27,color:'#FFF',marginTop:6},cardArrow:{position:'absolute',right:0,bottom:0,fontSize:24,color:'#FFF'},
  titleBlock:{paddingTop:24,paddingBottom:26},eyebrow:{fontSize:9,letterSpacing:2.7,color:C.rose,fontWeight:'700'},title:{fontFamily:'serif',fontSize:40,lineHeight:43,color:C.ink,marginTop:10},copy:{fontSize:13,lineHeight:20,color:C.muted,marginTop:10,maxWidth:340},
  familyGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:18},familyItem:{width:'31%',alignItems:'center'},familyVisual:{width:'100%',aspectRatio:1,borderRadius:22,overflow:'hidden',borderWidth:1,borderColor:'rgba(60,40,32,.05)'},familyVisualOn:{borderColor:C.dark,borderWidth:2},familyLabel:{fontSize:11,color:C.ink,marginTop:8},familyLabelOn:{fontWeight:'700'},check:{position:'absolute',right:7,top:7,width:26,height:26,borderRadius:13,backgroundColor:C.paper,alignItems:'center',justifyContent:'center',shadowColor:'#000',shadowOpacity:.12,shadowRadius:5,elevation:3},checkText:{fontSize:13,color:C.dark,fontWeight:'700'},
  filterRow:{flexDirection:'row',gap:8,marginBottom:18},filter:{paddingHorizontal:14,paddingVertical:9,borderRadius:99,borderWidth:1,borderColor:C.line,backgroundColor:C.paper2},filterOn:{paddingHorizontal:14,paddingVertical:9,borderRadius:99,backgroundColor:C.dark},filterText:{fontSize:10,color:C.muted},filterOnText:{fontSize:10,color:'#FFF'},
  shadeGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:18},shadeItem:{width:'31%',alignItems:'stretch'},shadeVisual:{width:'100%',aspectRatio:1,borderRadius:19,overflow:'hidden',borderWidth:1,borderColor:'rgba(60,40,32,.06)'},shadeVisualOn:{borderWidth:2,borderColor:C.dark},fav:{position:'absolute',left:6,top:6,width:27,height:27,borderRadius:14,backgroundColor:'rgba(255,253,249,.9)',alignItems:'center',justifyContent:'center'},favText:{fontSize:14,color:C.dark},shadeName:{fontFamily:'serif',fontSize:13.5,lineHeight:16,color:C.ink,marginTop:8,minHeight:33},shadeNameOn:{fontWeight:'700'},shadeMeta:{fontSize:8.5,color:C.muted,marginTop:2,textTransform:'capitalize'},
  cta:{marginTop:26},primary:{height:58,borderRadius:22,backgroundColor:C.dark,alignItems:'center',justifyContent:'center'},primaryDisabled:{opacity:.32},primaryText:{fontSize:13,color:'#FFF',fontWeight:'700'},
  photoEmpty:{height:350,borderRadius:30,backgroundColor:C.paper,borderWidth:1,borderColor:C.line,alignItems:'center',justifyContent:'center',padding:30},faceIcon:{width:160,height:180,alignItems:'center',justifyContent:'center',opacity:.45},faceHead:{width:76,height:96,borderRadius:45,borderWidth:1.5,borderColor:C.muted},faceShoulders:{position:'absolute',bottom:8,width:145,height:68,borderTopLeftRadius:75,borderTopRightRadius:75,borderWidth:1.5,borderBottomWidth:0,borderColor:C.muted},photoEmptyTitle:{fontFamily:'serif',fontSize:22,color:C.ink,textAlign:'center'},photoEmptyCopy:{fontSize:12,lineHeight:18,color:C.muted,textAlign:'center',marginTop:8},photoStage:{height:410,borderRadius:30,overflow:'hidden',backgroundColor:C.paper},photo:{width:'100%',height:'100%',resizeMode:'cover'},photoLabel:{position:'absolute',left:18,bottom:18,backgroundColor:'rgba(255,253,249,.92)',paddingHorizontal:13,paddingVertical:8,borderRadius:99},photoLabelText:{fontSize:8,letterSpacing:1.8,color:C.dark,fontWeight:'700'},dual:{flexDirection:'row',gap:10,marginTop:14},secondary:{flex:1,height:52,borderRadius:18,borderWidth:1,borderColor:C.champagne,backgroundColor:C.paper,alignItems:'center',justifyContent:'center'},secondaryText:{fontSize:11.5,color:C.dark,fontWeight:'700'},
  adjustStage:{height:430,borderRadius:30,overflow:'hidden',backgroundColor:C.paper},guideOval:{position:'absolute',left:'18%',right:'18%',top:'9%',bottom:'18%',borderRadius:190,borderWidth:1.5,borderColor:'rgba(255,255,255,.78)'},guideTop:{position:'absolute',left:'30%',right:'30%',top:'7%',height:2,backgroundColor:'rgba(255,255,255,.8)'},adjustTag:{position:'absolute',left:16,bottom:16,backgroundColor:'rgba(255,253,249,.92)',paddingHorizontal:12,paddingVertical:8,borderRadius:99,flexDirection:'row',alignItems:'center',gap:7},dot:{width:10,height:10,borderRadius:5},adjustTagText:{fontSize:9,color:C.dark,fontWeight:'700'},adjustHint:{marginTop:14,padding:18,borderRadius:20,backgroundColor:C.paper,borderWidth:1,borderColor:C.line},adjustHintTitle:{fontFamily:'serif',fontSize:18,color:C.ink},adjustHintText:{fontSize:11.5,lineHeight:18,color:C.muted,marginTop:5},
  resultCard:{height:470,borderRadius:30,overflow:'hidden',backgroundColor:C.paper},resultImage:{width:'100%',height:'100%',resizeMode:'cover'},resultScrim:{...fill,backgroundColor:'rgba(37,22,18,.12)'},resultCopy:{position:'absolute',left:22,right:22,bottom:22},resultName:{fontFamily:'serif',fontSize:29,color:'#FFF'},resultMeta:{fontSize:8,letterSpacing:2.1,color:'#F7ECE5',marginTop:4},beforeAfter:{flexDirection:'row',gap:10,marginTop:12},mini:{flex:1,height:178,borderRadius:20,overflow:'hidden',backgroundColor:C.paper},miniLabel:{position:'absolute',left:10,bottom:10,fontSize:8,letterSpacing:1.8,color:'#FFF',fontWeight:'700'},notice:{marginTop:14,padding:18,borderRadius:20,backgroundColor:C.paper,borderWidth:1,borderColor:C.line},noticeTitle:{fontFamily:'serif',fontSize:18,color:C.ink},noticeText:{fontSize:11.5,lineHeight:18,color:C.muted,marginTop:5},noticeLink:{fontSize:11,color:C.dark,fontWeight:'700',marginTop:9},
  savedGrid:{flexDirection:'row',flexWrap:'wrap',justifyContent:'space-between',rowGap:16},savedCard:{width:'48.3%',backgroundColor:C.paper,borderRadius:23,padding:9,borderWidth:1,borderColor:C.line},savedVisual:{width:'100%',aspectRatio:.92,borderRadius:17,overflow:'hidden'},savedName:{fontFamily:'serif',fontSize:17,color:C.ink,marginTop:10},savedMeta:{fontSize:9.5,color:C.muted,marginTop:4,marginBottom:3,textTransform:'capitalize'},emptySaved:{paddingVertical:90,alignItems:'center'},emptyHeart:{fontSize:44,color:C.champagne},emptyTitle:{fontFamily:'serif',fontSize:25,color:C.ink,marginTop:10},emptyCopy:{fontSize:12.5,lineHeight:19,color:C.muted,textAlign:'center',maxWidth:280,marginTop:8},
  moreCard:{backgroundColor:C.paper,borderRadius:24,overflow:'hidden',borderWidth:1,borderColor:C.line},moreRow:{minHeight:58,paddingHorizontal:18,flexDirection:'row',alignItems:'center',justifyContent:'space-between',borderBottomWidth:1,borderBottomColor:C.line},moreText:{fontSize:13,color:C.ink},moreArrow:{fontSize:22,color:C.muted},
  modalBack:{flex:1,backgroundColor:'rgba(43,28,23,.42)',alignItems:'center',justifyContent:'center',padding:28},exitCard:{width:'100%',maxWidth:355,backgroundColor:C.paper,borderRadius:30,padding:25,alignItems:'center'},exitGlyph:{width:50,height:50,borderRadius:25,borderWidth:1,borderColor:C.champagne,alignItems:'center',justifyContent:'center'},exitGlyphText:{fontFamily:'serif',fontSize:31,color:C.rose},exitTitle:{fontFamily:'serif',fontSize:28,lineHeight:32,color:C.ink,textAlign:'center',marginTop:17},exitCopy:{fontSize:12.5,lineHeight:19,color:C.muted,textAlign:'center',marginTop:9,maxWidth:280},exitButtons:{flexDirection:'row',gap:10,width:'100%',marginTop:20},stay:{flex:1,height:52,borderRadius:18,borderWidth:1,borderColor:C.champagne,alignItems:'center',justifyContent:'center'},exit:{flex:1,height:52,borderRadius:18,backgroundColor:C.dark,alignItems:'center',justifyContent:'center'},stayText:{fontSize:12,color:C.dark,fontWeight:'700'},exitText:{fontSize:12,color:'#FFF',fontWeight:'700'},exitTag:{fontSize:8,letterSpacing:2.3,color:C.muted,marginTop:18},
});
