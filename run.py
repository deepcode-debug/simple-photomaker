from app import (
    pipe, 
    device, 
    face_detector, 
    apply_style, 
    styles, 
    aspect_ratios,
    analyze_faces, 
    torch, 
    np, 
    load_image,
    TF
)

def generate_image_no_gradio(
    image_paths, 
    prompt, 
    negative_prompt="nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
    aspect_ratio_name="", 
    style_name="Photographic (Default)", 
    num_steps=50, 
    style_strength_ratio=20, 
    guidance_scale=5.0, 
    seed=0,
    use_doodle=False,
    sketch_path=None,
    adapter_conditioning_scale=0.7,
    adapter_conditioning_factor=0.8
):
    # Process sketch if doodle is enabled
    if use_doodle and sketch_path:
        sketch_image = load_image(sketch_path)
        r, g, b, a = sketch_image.split()
        sketch_image = a.convert("RGB")
        sketch_image = TF.to_tensor(sketch_image) > 0.5  # Inversion 
        sketch_image = TF.to_pil_image(sketch_image.to(torch.float32))
    else:
        adapter_conditioning_scale = 0.
        adapter_conditioning_factor = 0.
        sketch_image = None

    # Check for trigger word
    image_token_id = pipe.tokenizer.convert_tokens_to_ids(pipe.trigger_word)
    input_ids = pipe.tokenizer.encode(prompt)
    if image_token_id not in input_ids:
        raise ValueError(f"Cannot find the trigger word '{pipe.trigger_word}' in text prompt! Please add 'img' to your prompt.")

    if input_ids.count(image_token_id) > 1:
        raise ValueError(f"Cannot use multiple trigger words '{pipe.trigger_word}' in text prompt!")

    # Determine output dimensions by the aspect ratio
    output_w, output_h = aspect_ratios["Instagram (1:1)"]
    print(f"[Debug] Generate image using aspect ratio [{aspect_ratio_name}] => {output_w} x {output_h}")

    # Apply the style template
    prompt, negative_prompt = apply_style(style_name, prompt, negative_prompt)

    input_id_images = []
    for img_path in image_paths:
        input_id_images.append(load_image(img_path))
    
    id_embed_list = []

    for img in input_id_images:
        img = np.array(img)
        img = img[:, :, ::-1]  # RGB to BGR
        faces = analyze_faces(face_detector, img)
        if len(faces) > 0:
            id_embed_list.append(torch.from_numpy((faces[0]['embedding'])))

    if len(id_embed_list) == 0:
        raise ValueError("No face detected, please update the input face image(s)")
    
    id_embeds = torch.stack(id_embed_list)

    generator = torch.Generator(device=device).manual_seed(seed)

    print("Start inference...")
    print(f"[Debug] Seed: {seed}")
    print(f"[Debug] Prompt: {prompt}")
    print(f"[Debug] Neg Prompt: {negative_prompt}")
    
    start_merge_step = int(float(style_strength_ratio) / 100 * num_steps)
    if start_merge_step > 30:
        start_merge_step = 30
    print(f"[Debug] Start merge step: {start_merge_step}")
    
    images = pipe(
        prompt=prompt,
        width=output_w,
        height=output_h,
        input_id_images=input_id_images,
        negative_prompt=negative_prompt,
        num_images_per_prompt=1,  # You can adjust this as needed
        num_inference_steps=num_steps,
        start_merge_step=start_merge_step,
        generator=generator,
        guidance_scale=guidance_scale,
        id_embeds=id_embeds,
        image=sketch_image,
        adapter_conditioning_scale=adapter_conditioning_scale,
        adapter_conditioning_factor=adapter_conditioning_factor,
    ).images
    
    return images

