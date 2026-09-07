import base64
import json
import os
import tempfile
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

app = FastAPI(title="Kübra Hair Atelier API", version="1.8.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

VISION_MODEL = os.getenv("KHA_VISION_MODEL", "gpt-5.6-luna")
IMAGE_MODEL = os.getenv("KHA_IMAGE_MODEL", "gpt-image-2")


def client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="AI service is not configured on the server.")
    return OpenAI(api_key=key)


def parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


async def image_bytes(photo: UploadFile) -> tuple[bytes, str]:
    data = await photo.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty photo upload.")
    if len(data) > 18 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Photo is too large. Please use an image under 18 MB.")
    mime = photo.content_type if photo.content_type in {"image/jpeg", "image/png", "image/webp"} else "image/jpeg"
    return data, mime


@app.get("/health")
def health():
    return {
        "ok": True,
        "version": "1.8.0",
        "vision_model": VISION_MODEL,
        "image_model": IMAGE_MODEL,
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/v1/hair/preview")
async def preview(
    photo: UploadFile = File(...),
    shade_name: str = Form(...),
    shade_hex: str = Form(...),
    target_level: str = Form(...),
    target_tone: str = Form(...),
):
    data, mime = await image_bytes(photo)
    suffix = ".png" if mime == "image/png" else ".webp" if mime == "image/webp" else ".jpg"
    prompt = f"""
Edit this exact portrait photograph as a professional hair-color virtual try-on.
Change ONLY the visible hair color to {shade_name} ({shade_hex}), target salon level {target_level}, tone {target_tone}.
Preserve the person's identity, face, skin, expression, eyes, eyebrows, makeup, body, clothing, background, camera angle, framing, crop, hairstyle, hair length, curl pattern, strand geometry and flyaways.
Preserve realistic roots, highlights, lowlights, shadows, shine, translucency and scene lighting. Recolor individual hair strands naturally rather than painting a flat mask.
Do not alter facial hair unless it is clearly continuous with the hairstyle. Do not beautify, reshape, retouch or change anything except scalp hair color.
Return one photorealistic edited image with the same composition and as much of the original frame as possible.
""".strip()
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
            tmp.write(data)
            tmp.flush()
            with open(tmp.name, "rb") as image_file:
                result = client().images.edit(model=IMAGE_MODEL, image=image_file, prompt=prompt)
        b64 = result.data[0].b64_json
        if not b64:
            raise RuntimeError("Image model returned no image data.")
        return {"previewDataUrl": f"data:image/png;base64,{b64}", "provider": "openai"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hair preview failed: {exc}") from exc


@app.post("/v1/hair/analyze")
async def analyze(photo: UploadFile = File(...)):
    data, mime = await image_bytes(photo)
    encoded = base64.b64encode(data).decode("ascii")
    prompt = """
You are assisting a professional hair-color consultation. Analyze only visible cosmetic hair characteristics from the photo; do not identify the person.
Return ONLY a JSON object with exactly these fields:
currentLevel: integer 1-10 estimating the visible natural/colored depth,
undertone: short lowercase phrase,
porosity: one of "low", "medium", "high", "uncertain",
condition: one of "healthy", "slightly compromised", "compromised", "uncertain",
previousColor: short phrase describing visible evidence only, or "uncertain",
greyPercent: integer 0-100 estimated visible grey percentage,
confidence: number 0-1,
notes: array of 2-4 short practical observations.
Be conservative. A photo cannot reliably prove porosity, damage history, natural level, or prior chemical treatment; mark uncertainty where appropriate. Never invent a hidden history.
""".strip()
    try:
        response = client().responses.create(
            model=VISION_MODEL,
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": f"data:{mime};base64,{encoded}"},
                ],
            }],
        )
        result = parse_json(response.output_text)
        level = max(1, min(10, int(result.get("currentLevel", 5))))
        grey = max(0, min(100, int(result.get("greyPercent", 0))))
        confidence = max(0.0, min(1.0, float(result.get("confidence", 0.5))))
        return {
            "currentLevel": level,
            "undertone": str(result.get("undertone", "uncertain"))[:80],
            "porosity": str(result.get("porosity", "uncertain"))[:40],
            "condition": str(result.get("condition", "uncertain"))[:60],
            "previousColor": str(result.get("previousColor", "uncertain"))[:120],
            "greyPercent": grey,
            "confidence": confidence,
            "notes": [str(x)[:220] for x in result.get("notes", [])][:4],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hair analysis failed: {exc}") from exc


class HairAnalysis(BaseModel):
    currentLevel: int = Field(ge=1, le=10)
    undertone: str
    porosity: str
    condition: str
    previousColor: str
    greyPercent: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    notes: list[str] = []


class ShadeTarget(BaseModel):
    name: str
    hex: str
    level: str
    tone: str


class FormulaRequest(BaseModel):
    analysis: HairAnalysis
    shade: ShadeTarget


def generic_formula(a: HairAnalysis, shade: ShadeTarget) -> dict[str, Any]:
    current = int(a.currentLevel)
    try:
        target = max(1, min(10, int(float(shade.level))))
    except ValueError:
        target = current
    delta = target - current
    fantasy = any(word in shade.tone.lower() or word in shade.name.lower() for word in ["blue", "pink", "violet", "green", "pastel", "silver"])
    lift_required = delta >= 2 or (fantasy and target >= 7 and current < target)

    if fantasy:
        route = f"Create a clean level {target} base, then deposit {shade.name}." if lift_required else f"Deposit {shade.name} over the existing level {current} base."
        developer = "Use the direct-dye system as directed; no developer unless that product specifically requires one."
        mix = f"Use a professional {shade.name} / {shade.tone} direct or demi color. Do not invent a cross-brand ratio; follow that color line's specified mixing ratio."
    elif delta >= 3:
        route = f"Pre-lighten from about level {current} toward level {target}, then tone to {shade.tone}."
        developer = "Professional lightener + manufacturer-matched developer selected from a strand test; avoid choosing strength from the photo alone."
        mix = f"After lifting, tone with a level {target} neutral foundation plus the brand's {shade.tone} reflector, using that line's official color:developer ratio."
    elif delta >= 1:
        route = f"Controlled lift from about level {current} to {target}, then refine the {shade.tone} tone."
        developer = "Commonly a manufacturer-approved lift/deposit developer; confirm strength with a strand test and the chosen color line."
        mix = f"Use a level {target} formula anchored with neutral/base plus the matching {shade.tone} tone. Follow the chosen professional line's mixing ratio."
    else:
        route = f"Deposit/refine at level {target} toward {shade.name}."
        developer = "Low-volume deposit/demi developer if the selected professional line calls for one."
        mix = f"Use level {target} neutral/base plus the line's {shade.tone} tone as needed for control. Follow that brand's official mixing ratio."

    steps = [
        "Confirm the starting level and chemical history in person; perform a strand and allergy/patch test as required by the product.",
        "Section clean, dry hair and protect the skin/clothing according to the color line's instructions.",
    ]
    if lift_required:
        steps.append(f"Lift only as far as needed for an even level {target} canvas; monitor integrity and stop if the strand test shows unacceptable damage.")
    steps.extend([
        f"Apply the target {shade.name} tone using the selected professional color line's official timing and ratio.",
        "Rinse, condition and assess in neutral lighting; refine only after seeing the dry result.",
    ])
    warnings = [
        "Photo analysis is an estimate and cannot verify hidden banding, metallic salts, allergies, porosity or prior chemical history.",
        "Do not use a formula that conflicts with the chosen manufacturer's instructions or an in-person strand test.",
    ]
    if a.condition != "healthy" or a.porosity == "high":
        warnings.append("Visible condition/porosity may be compromised; prioritize strand integrity over reaching the target in one session.")
    maintenance = [
        "Use color-safe cleansing and limit unnecessary high heat.",
        f"Refresh the {shade.tone} tone with a compatible gloss/toner when fading becomes visible.",
    ]
    return {
        "targetLevel": target,
        "targetTone": shade.tone,
        "route": route,
        "liftRequired": lift_required,
        "developer": developer,
        "mix": mix,
        "steps": steps,
        "warnings": warnings,
        "maintenance": maintenance,
    }


@app.post("/v1/hair/formula")
def formula(req: FormulaRequest):
    return generic_formula(req.analysis, req.shade)
