from run import (
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
import gradio as gr
import json
import os
import random
from datetime import datetime
import shutil
from PIL import Image
import io
import glob

# Constants
IMG_DIR = "img"
GEN_IMG_DIR = "gen_img"
THEMES_FILE = "dream_world_presets.json"

def setup_environment():
    """Set up the necessary directories and theme data"""
    # Create directories if they don't exist
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(GEN_IMG_DIR, exist_ok=True)
    
    # Generate theme presets file if it doesn't exist
    if not os.path.exists(THEMES_FILE):
        create_theme_presets()
    
    return "✅ Environment setup complete!"

def create_theme_presets():
    """Create the dream world theme presets JSON file"""
    theme_data = {
        "dream_world_themes": [
            {
                "name": "(No style)",
                "prompt": "{prompt}",
                "negative_prompt": "",
                "style_name": "Fantasy",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Cinematic",
                "prompt": "cinematic still {prompt} . emotional, harmonious, vignette, highly detailed, high budget, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy",
                "negative_prompt": "anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured",
                "style_name": "Anime",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Disney Character",
                "prompt": "A Pixar animation character of {prompt} . pixar-style, studio anime, Disney, high-quality",
                "negative_prompt": "lowres, bad anatomy, bad hands, text, bad eyes, bad arms, bad legs, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, blurry, grayscale, noisy, sloppy, messy, grainy, highly detailed, ultra textured, photo",
                "style_name": "Artistic",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Digital Art",
                "prompt": "concept art {prompt} . digital artwork, illustrative, painterly, matte painting, highly detailed",
                "negative_prompt": "photo, photorealistic, realism, ugly",
                "style_name": "Fantasy",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Photographic (Default)",
                "prompt": "cinematic photo {prompt} . 35mm photograph, film, bokeh, professional, 4k, highly detailed",
                "negative_prompt": "drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly",
                "style_name": "Fantasy",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Fantasy art",
                "prompt": "ethereal fantasy concept art of {prompt} . magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy",
                "negative_prompt": "photographic, realistic, realism, 35mm film, dslr, cropped, frame, text, deformed, glitch, noise, noisy, off-center, deformed, cross-eyed, closed eyes, bad anatomy, ugly, disfigured, sloppy, duplicate, mutated, black and white",
                "style_name": "Fantasy",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Neonpunk",
                "prompt": "neonpunk style {prompt} . cyberpunk, vaporwave, neon, vibes, vibrant, stunningly beautiful, crisp, detailed, sleek, ultramodern, magenta highlights, dark purple shadows, high contrast, cinematic, ultra detailed, intricate, professional",
                "negative_prompt": "painting, drawing, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured",
                "style_name": "Artistic",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Enhance",
                "prompt": "breathtaking {prompt} . award-winning, professional, highly detailed",
                "negative_prompt": "ugly, deformed, noisy, blurry, distorted, grainy",
                "style_name": "Artistic",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Comic book",
                "prompt": "comic {prompt} . graphic illustration, comic art, graphic novel art, vibrant, highly detailed",
                "negative_prompt": "photograph, deformed, glitch, noisy, realistic, stock photo",
                "style_name": "Artistic",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Seasons Calendar",
                "prompt": "a child img in a [season] themed scene, calendar style, vibrant colors, seasonal elements, whimsical",
                "negative_prompt": "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, scary, creepy, dark, sinister",
                "style_name": "Photographic (Default)",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0,
                "seasons": ["spring with flowers and butterflies", "summer with beach and sunshine", "autumn with falling leaves", "winter with snow and festivities"]
            },
            {
                "name": "Lowpoly",
                "prompt": "low-poly style {prompt} . low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition",
                "negative_prompt": "noisy, sloppy, messy, grainy, highly detailed, ultra textured, photo",
                "style_name": "Artistic",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            },
            {
                "name": "Line art",
                "prompt": "line art drawing {prompt} . professional, sleek, modern, minimalist, graphic, line art, vector graphics",
                "negative_prompt": "anime, photorealistic, 35mm film, deformed, glitch, blurry, noisy, off-center, deformed, cross-eyed, closed eyes, bad anatomy, ugly, disfigured, mutated, realism, realistic, impressionism, expressionism, oil, acrylic",
                "style_name": "Artistic",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0
            }
        ]
    }
    with open(THEMES_FILE, 'w') as f:
        json.dump(theme_data, f, indent=2)

def load_theme_data():
    """Load themes from the JSON file"""
    with open(THEMES_FILE, 'r') as f:
        return json.load(f)

def get_theme_names():
    """Get list of theme names for dropdown"""
    theme_data = load_theme_data()
    return [theme["name"] for theme in theme_data["dream_world_themes"]]

def get_theme_by_name(name):
    """Get theme data by name"""
    theme_data = load_theme_data()
    for theme in theme_data["dream_world_themes"]:
        if theme["name"] == name:
            return theme
    return None

def get_season_options(theme_name):
    """Get season options if available"""
    theme = get_theme_by_name(theme_name)
    if theme and "seasons" in theme:
        return theme["seasons"]
    return []

def update_season_dropdown(theme_name):
    """Update season dropdown based on selected theme"""
    seasons = get_season_options(theme_name)
    if seasons:
        return gr.Dropdown(choices=seasons, visible=True, label="Season")
    else:
        return gr.Dropdown(choices=[], visible=False, label="Season")

def update_theme_params(theme_name, season=None, custom_prompt=None):
    """Update the UI with parameters from selected theme and inject custom prompt"""
    theme = get_theme_by_name(theme_name)
    if not theme:
        return "", "", "", 50, 20, 5.0
    
    prompt_template = theme["prompt"]
    
    # Inject custom prompt if provided
    final_prompt = prompt_template
    if custom_prompt:
        final_prompt = prompt_template.replace("{prompt}", custom_prompt)
    
    # Handle season replacement if applicable
    if season and "[season]" in final_prompt:
        final_prompt = final_prompt.replace("[season]", season)
        
    return (
        final_prompt, 
        theme["negative_prompt"], 
        theme["style_name"],
        theme["num_steps"],
        theme["style_strength_ratio"],
        theme["guidance_scale"]
    )

def process_images(uploaded_files):
    """Process uploaded images and return their paths"""
    # Clear existing images in directory
    for file in os.listdir(IMG_DIR):
        file_path = os.path.join(IMG_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    # Save uploaded files
    image_paths = []
    for i, file in enumerate(uploaded_files):
        if file is not None:
            file_path = os.path.join(IMG_DIR, f"uploaded_img_{i}.png")
            if isinstance(file, str):  # If already a path
                shutil.copy(file, file_path)
            else:  # If a file object
                img = Image.open(file)
                img.save(file_path)
            image_paths.append(file_path)
    
    return image_paths

# Direct implementation of image generation (bypassing run.py to have exact same behavior as app.py)
def generate_photomaker_image(
    image_paths,
    prompt,
    negative_prompt,
    style_name,
    num_steps,
    style_strength_ratio,
    guidance_scale,
    seed
):
    # Check for trigger word
    image_token_id = pipe.tokenizer.convert_tokens_to_ids(pipe.trigger_word)
    input_ids = pipe.tokenizer.encode(prompt)
    if image_token_id not in input_ids:
        raise ValueError(f"Cannot find the trigger word '{pipe.trigger_word}' in text prompt! Please add 'img' to your prompt.")

    if input_ids.count(image_token_id) > 1:
        raise ValueError(f"Cannot use multiple trigger words '{pipe.trigger_word}' in text prompt!")

    # Determine output dimensions - using square format (1:1 aspect ratio) as in the original app
    output_w, output_h = 1024, 1024  # Default to square format like the original

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
        num_images_per_prompt=1,
        num_inference_steps=num_steps,
        start_merge_step=start_merge_step,
        generator=generator,
        guidance_scale=guidance_scale,
        id_embeds=id_embeds,
        image=None,  # No sketch image
        adapter_conditioning_scale=0.0,  # Disable adapter
        adapter_conditioning_factor=0.0,  # Disable adapter
    ).images
    
    return images

def generate_images(
    uploaded_files, 
    theme_name, 
    season, 
    custom_prompt,
    prompt, 
    negative_prompt, 
    style_name, 
    num_steps, 
    style_strength_ratio, 
    guidance_scale, 
    num_outputs, 
    seed
):
    """Generate images using the provided parameters"""
    if not uploaded_files:
        return "❌ Please upload at least one image of the child.", []
    
    # Process uploaded images
    image_paths = process_images(uploaded_files)
    
    # Generate a random seed if necessary
    if seed == 0:
        seed = random.randint(0, 2147483647)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clear previous generated images
    for file in os.listdir(GEN_IMG_DIR):
        file_path = os.path.join(GEN_IMG_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    # Import the actual generation function
    try:
        # Use our direct implementation for exact same behavior
        generated_images = generate_photomaker_image(
            image_paths=image_paths,
            prompt=prompt,
            negative_prompt=negative_prompt,
            style_name=style_name,
            num_steps=num_steps,
            style_strength_ratio=style_strength_ratio,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        # Save generated images
        saved_paths = []
        theme_name_safe = theme_name.replace(" ", "_").lower()
        
        for i, img in enumerate(generated_images[:num_outputs]):
            save_path = f"{GEN_IMG_DIR}/dream_{theme_name_safe}_{timestamp}_{i+1}.png"
            img.save(save_path)
            saved_paths.append(save_path)
        
        return f"✅ Generated {len(saved_paths)} images successfully!", saved_paths
        
    except Exception as e:
        return f"❌ Error generating images: {str(e)}\n\nTips: Make sure your images have clear faces and the prompt includes 'img' after the subject.", []

# Initialize environment
setup_environment()

# Create Gradio Interface
with gr.Blocks(title="Dream World Photo Generator") as demo:
    gr.Markdown("""
    # 🧙‍♂️ Dream World Photo Generator
    
    Upload photos of a child and transform them into magical dream world images!
    
    ## Instructions:
    1. Upload 1-5 photos of the child (face clearly visible)
    2. Choose a dream world theme
    3. Customize parameters if desired
    4. Generate images!
    """)
    
    # Upload Images Section
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 📷 Step 1: Upload Photos")
            upload = gr.File(
                file_count="multiple",
                label="Upload 1-5 photos of the child",
                file_types=["image"],
            )
        
        # Theme Selection Section
        with gr.Column(scale=1):
            gr.Markdown("## 🎨 Step 2: Choose a Theme")
            theme_dropdown = gr.Dropdown(
                choices=get_theme_names(),
                label="Select a Dream World Theme",
                info="Choose the magical theme for your images"
            )
            
            season_dropdown = gr.Dropdown(
                choices=[],
                label="Season",
                visible=False,
                info="Select a season for the theme"
            )
            
            # Add custom prompt input
            custom_prompt = gr.Textbox(
                label="Custom Prompt",
                placeholder="Enter a custom prompt (e.g., 'a child img in a forest')",
                info="Enter your custom prompt to replace {prompt} in the theme template",
            )
    
    # Advanced Parameters Section
    with gr.Accordion("🔧 Advanced Parameters", open=False):
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(
                    label="Final Prompt",
                    info="The final prompt after template processing",
                    lines=3
                )
                negative_prompt = gr.Textbox(
                    label="Negative Prompt",
                    info="What to avoid in the image",
                    lines=2,
                    value="nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
                )
                style_name = gr.Textbox(label="Style Name")
            
            with gr.Column():
                num_steps = gr.Slider(
                    minimum=20, 
                    maximum=100, 
                    value=50, 
                    step=1, 
                    label="Number of Steps",
                    info="Higher = better quality but slower"
                )
                style_strength = gr.Slider(
                    minimum=15, 
                    maximum=50, 
                    value=20, 
                    step=1, 
                    label="Style Strength",
                    info="Between 15-50 recommended"
                )
                guidance_scale = gr.Slider(
                    minimum=0.1, 
                    maximum=10.0, 
                    value=5.0, 
                    step=0.1, 
                    label="Guidance Scale"
                )
                
        with gr.Row():
            num_outputs = gr.Slider(
                minimum=1, 
                maximum=4, 
                value=2,  # Default from app.py
                step=1, 
                label="Number of Images to Generate"
            )
            seed = gr.Number(
                value=0, 
                label="Random Seed (0 for random)",
                precision=0
            )
    
    # Generate Button
    with gr.Row():
        generate_btn = gr.Button("🚀 Generate Dream World Images", variant="primary", size="lg")
    
    # Output Section
    with gr.Row():
        result_text = gr.Textbox(label="Status")
    
    with gr.Row():
        gallery = gr.Gallery(label="Generated Images", columns=2, height=500)
    
    # Set up theme change event to update parameters
    theme_dropdown.change(
        fn=update_season_dropdown,
        inputs=theme_dropdown,
        outputs=season_dropdown
    )
    
    # Update parameters when theme, season, or custom prompt changes
    def update_all_params(theme_name, season, custom_prompt):
        return update_theme_params(theme_name, season, custom_prompt)
        
    # Connect all three input changes to update parameters
    theme_dropdown.change(
        fn=update_all_params,
        inputs=[theme_dropdown, season_dropdown, custom_prompt],
        outputs=[prompt, negative_prompt, style_name, num_steps, style_strength, guidance_scale]
    )
    
    season_dropdown.change(
        fn=update_all_params,
        inputs=[theme_dropdown, season_dropdown, custom_prompt],
        outputs=[prompt, negative_prompt, style_name, num_steps, style_strength, guidance_scale]
    )
    
    custom_prompt.change(
        fn=update_all_params,
        inputs=[theme_dropdown, season_dropdown, custom_prompt],
        outputs=[prompt, negative_prompt, style_name, num_steps, style_strength, guidance_scale]
    )
    
    # Set up generate button click event
    generate_btn.click(
        fn=generate_images,
        inputs=[
            upload,
            theme_dropdown,
            season_dropdown,
            custom_prompt,
            prompt,
            negative_prompt,
            style_name,
            num_steps,
            style_strength,
            guidance_scale,
            num_outputs,
            seed
        ],
        outputs=[result_text, gallery]
    )

    # Add instructions
    with gr.Accordion("ℹ️ Tips & Information", open=False):
        gr.Markdown("""
        ## Tips for Best Results
        
        - Upload clear photos of the child's face
        - Different angles and expressions help create better images
        - Make sure the prompt includes 'img' after mentioning the subject
        - Higher step counts produce better quality but take longer
        - If you're not satisfied with the results, try a different seed value
        - Use the custom prompt field to personalize your images
        
        ## About Dream World Photo Generator
        
        This tool uses PhotoMaker V2 to create magical dream world images of children
        for comics, calendars, or stickers. The generated images can be used for:
        
        - Creating a comic book with different scenes
        - Making a personalized calendar
        - Designing custom stickers
        - Creating memorable digital art
        """)

# Launch the app in Colab
def launch_app():
    # First setup the environment
    setup_environment()
    # Launch the Gradio interface
    demo.launch(debug=True, share=True)

# This will be called to run the app
if __name__ == "__main__":
    launch_app()