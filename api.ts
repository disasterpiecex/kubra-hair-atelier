export type PreviewResponse = { previewDataUrl: string; provider: string };
export type HairAnalysis = {
  currentLevel:number;
  undertone:string;
  porosity:string;
  condition:string;
  previousColor:string;
  greyPercent:number;
  confidence:number;
  notes:string[];
};
export type FormulaResult = {
  targetLevel:number;
  targetTone:string;
  route:string;
  liftRequired:boolean;
  developer:string;
  mix:string;
  steps:string[];
  warnings:string[];
  maintenance:string[];
};

type ShadeTarget={name:string;hex:string;level:string;tone:string};
const API_URL = (process.env.EXPO_PUBLIC_API_URL || '').replace(/\/$/, '');

function requireApi(){
  if(!API_URL) throw new Error('Live AI service is not configured in this build yet.');
  return API_URL;
}
function photoPart(uri:string): any {
  const ext = (uri.split('.').pop() || 'jpg').split('?')[0].toLowerCase();
  const type = ext === 'png' ? 'image/png' : 'image/jpeg';
  return { uri, name:`hair.${ext === 'png' ? 'png' : 'jpg'}`, type };
}
async function asJson(res:Response){
  const body = await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(body?.detail || body?.message || `Request failed (${res.status})`);
  return body;
}
export async function generateHairPreview(photoUri:string, shade:ShadeTarget):Promise<PreviewResponse>{
  const base=requireApi();
  const form = new FormData();
  form.append('photo', photoPart(photoUri));
  form.append('shade_name', shade.name);
  form.append('shade_hex', shade.hex);
  form.append('target_level', shade.level);
  form.append('target_tone', shade.tone);
  return asJson(await fetch(`${base}/v1/hair/preview`, { method:'POST', body:form }));
}
export async function analyzeHair(photoUri:string):Promise<HairAnalysis>{
  const base=requireApi();
  const form=new FormData();
  form.append('photo',photoPart(photoUri));
  return asJson(await fetch(`${base}/v1/hair/analyze`,{method:'POST',body:form}));
}
export async function generateFormula(analysis:HairAnalysis,shade:ShadeTarget):Promise<FormulaResult>{
  const base=requireApi();
  return asJson(await fetch(`${base}/v1/hair/formula`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({analysis,shade})}));
}
