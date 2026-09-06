export type PreviewResponse = { previewDataUrl: string; provider: string };

const API_URL = (process.env.EXPO_PUBLIC_API_URL || '').replace(/\/$/, '');

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

export async function generateHairPreview(photoUri:string, shade:{name:string;hex:string;level:string;tone:string}):Promise<PreviewResponse>{
  if(!API_URL) return {previewDataUrl:photoUri, provider:'mock-local'};
  const form = new FormData();
  form.append('photo', photoPart(photoUri));
  form.append('shade_name', shade.name);
  form.append('shade_hex', shade.hex);
  form.append('target_level', shade.level);
  form.append('target_tone', shade.tone);
  return asJson(await fetch(`${API_URL}/v1/hair/preview`, { method:'POST', body:form }));
}
