import comfy.sd
import comfy.utils
from nodes import LoadImage, VAEDecode, KSampler, EmptyLatentImage, ControlNetLoader
from custom_nodes.ComfyUI_InstantID.InstantID import InstantIDModelLoader, ApplyInstantID, InstantIDFaceAnalysis
from PIL import Image, ImageOps
import numpy as np
import torch
import random

# input
# prompt = "hiking in a mountain"
with open("./input/prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read().strip()
input_image_path = "input.png"

width = 1024
seed = random.randint(1, 1000000000000)
# seed = 684846067469548

# process settings
height = int(width / 4 * 3)
prompt = "a close distance portrait of a person " + prompt
negative_prompt = "(cover), (tights, underwear), (deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime, mutated hands and fingers:1.4), (deformed, distorted, disfigured:1.3), poorly drawn, (bad anatomy, wrong anatomy, extra person, extra limb, missing limb, floating limbs, disconnected limbs, mutation, mutated:1.5), ugly, disgusting, amputation, (watermark:1.5)"

# model configures and loading
model_path = "models/checkpoints/SDXLLightning/juggernautXL_v9Rdphoto2Lightning.safetensors"
controlnet_path = "SDXL1.0/InstantID_diffusion_pytorch_model.safetensors"
instantid_path = "ip-adapter.bin"

model = comfy.sd.load_checkpoint_guess_config(model_path)
clip = model[1]
vae = model[2]

controlnet = ControlNetLoader().load_controlnet(controlnet_path)
instantid = InstantIDModelLoader().load_model(instantid_path)
face_analysis = InstantIDFaceAnalysis().load_insight_face("CPU")

# process prompt
positive_cond = clip.encode_from_tokens_scheduled(clip.tokenize(prompt))
negative_cond = clip.encode_from_tokens_scheduled(clip.tokenize(negative_prompt))

# image util functions
def tensor_to_pil(img_tensor):
    """
    将 torch.Tensor (1, H, W, 3) 归一化图像转换为 PIL.Image
    """
    img = img_tensor[0].clamp(0, 1).mul(255).byte().numpy()
    return Image.fromarray(img, mode='RGB')

def pil_to_tensor(image_pil):
    img_np = np.array(image_pil).astype(np.float32) / 255.0
    return torch.from_numpy(img_np).unsqueeze(0)

# image loading
image_tensor, _ = LoadImage().load_image(input_image_path)
image_pil = tensor_to_pil(image_tensor)

# initiate empty latent images
latent = EmptyLatentImage().generate(width, height)

# generate pose reference
sketch = KSampler().sample(
    model=model[0],
    positive=positive_cond,
    negative=negative_cond,
    latent_image=latent[0],
    seed=seed,
    steps=3,
    cfg=2,
    sampler_name="dpmpp_sde",
    scheduler="karras",
    denoise=1.0
)

# prepare for reference
decoded_sketch = VAEDecode().decode(vae, sketch[0])
extended_sketch = ImageOps.expand(tensor_to_pil(decoded_sketch[0]), border=(int(width / 2), int(width / 8), int(width / 2), int(width / 8 * 5)), fill="#000000")
image_kps = pil_to_tensor(extended_sketch)

# apply InstantID to get new model
applied = ApplyInstantID().apply_instantid(
    instantid=instantid[0],
    insightface=face_analysis[0],
    control_net=controlnet[0],
    image=image_tensor,
    image_kps=image_kps,
    model=model[0],
    positive=positive_cond,
    negative=negative_cond,
    start_at=0,
    end_at=1,
    mask=None
)

# release VRAM
del model, instantid, face_analysis, controlnet, image_tensor, decoded_sketch, image_kps
torch.cuda.empty_cache()

# generate it
sampled = KSampler().sample(
    model=applied[0],
    positive=applied[1],
    negative=applied[2],
    latent_image=latent[0],
    seed=seed,
    steps=5,
    cfg=2,
    sampler_name="dpmpp_sde",
    scheduler="karras",
    denoise=1.0
)

# release VRAM
del applied
torch.cuda.empty_cache()

# decode and save
decoded_image = VAEDecode().decode(vae, sampled[0])
tensor_to_pil(decoded_image[0]).save("output.png")