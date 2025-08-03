import runpod
import requests
import json
import time
import os
import base64
import random

COMFY_HOST = "127.0.0.1:8188"

def handler(job):
    job_input = job["input"]

    # --- 1. Get Your API Inputs ---
    # We expect a 'prompt' and a base64 'image' from the API call
    prompt_text = job_input.get("prompt")
    image_base64 = job_input.get("image")
    
    # Validate required inputs
    if not prompt_text:
        return {"error": "Missing required 'prompt' parameter"}
    
    if not image_base64:
        return {"error": "Missing required 'image' parameter"}

    # --- 2. Load Your Workflow ---
    # This is the static workflow from your file.
    workflow_api_json = """
    {
  "1": {
    "inputs": {
      "image": "maxresdefault (99).jpg"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "2": {
    "inputs": {
      "preprocessor": "TilePreprocessor",
      "resolution": 512,
      "image": [
        "68",
        0
      ]
    },
    "class_type": "AIO_Preprocessor",
    "_meta": {
      "title": "AIO Aux Preprocessor"
    }
  },
  "3": {
    "inputs": {
      "strength": 0.4000000000000001,
      "start_percent": 0.010000000000000002,
      "end_percent": 0.5000000000000001,
      "positive": [
        "14",
        0
      ],
      "negative": [
        "9",
        0
      ],
      "control_net": [
        "4",
        0
      ],
      "image": [
        "2",
        0
      ],
      "vae": [
        "23",
        0
      ]
    },
    "class_type": "ControlNetApplyAdvanced",
    "_meta": {
      "title": "Apply ControlNet"
    }
  },
  "4": {
    "inputs": {
      "control_net_name": "FLUX.1-dev-ControlNet-Union-Pro-Shakker-Labs.safetensors"
    },
    "class_type": "ControlNetLoader",
    "_meta": {
      "title": "Load ControlNet Model"
    }
  },
  "9": {
    "inputs": {
      "clip_l": "",
      "t5xxl": "",
      "guidance": 3.5,
      "clip": [
        "76",
        0
      ]
    },
    "class_type": "CLIPTextEncodeFlux",
    "_meta": {
      "title": "CLIPTextEncodeFlux"
    }
  },
  "13": {
    "inputs": {
      "width": [
        "31",
        0
      ],
      "height": [
        "31",
        1
      ],
      "batch_size": 1
    },
    "class_type": "EmptySD3LatentImage",
    "_meta": {
      "title": "EmptySD3LatentImage"
    }
  },
  "14": {
    "inputs": {
      "guidance": 3.5,
      "conditioning": [
        "30",
        0
      ]
    },
    "class_type": "FluxGuidance",
    "_meta": {
      "title": "FluxGuidance"
    }
  },
  "23": {
    "inputs": {
      "vae_name": "flux_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  },
  "30": {
    "inputs": {
      "text": [
        "56",
        0
      ],
      "clip": [
        "76",
        0
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "31": {
    "inputs": {
      "image": [
        "68",
        0
      ]
    },
    "class_type": "GetImageSize+",
    "_meta": {
      "title": "🔧 Get Image Size"
    }
  },
  "35": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "37": {
    "inputs": {
      "samples": [
        "43",
        0
      ],
      "vae": [
        "23",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "38": {
    "inputs": {
      "threshold": 1,
      "cfg": 1,
      "uncond_zero_scale": 0,
      "cfg_start_pct": 0,
      "model": [
        "63",
        0
      ],
      "positive": [
        "3",
        0
      ],
      "negative": [
        "3",
        1
      ]
    },
    "class_type": "AdaptiveGuidance",
    "_meta": {
      "title": "AdaptiveGuider"
    }
  },
  "39": {
    "inputs": {
      "noise_seed": 52
    },
    "class_type": "RandomNoise",
    "_meta": {
      "title": "RandomNoise"
    }
  },
  "42": {
    "inputs": {
      "scheduler": "normal",
      "steps": 40,
      "denoise": 1,
      "model": [
        "63",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "43": {
    "inputs": {
      "noise": [
        "39",
        0
      ],
      "guider": [
        "38",
        0
      ],
      "sampler": [
        "35",
        0
      ],
      "sigmas": [
        "42",
        0
      ],
      "latent_image": [
        "13",
        0
      ]
    },
    "class_type": "SamplerCustomAdvanced",
    "_meta": {
      "title": "SamplerCustomAdvanced"
    }
  },
  "51": {
    "inputs": {
      "method": "mkl",
      "strength": 0.8000000000000002,
      "image_ref": [
        "68",
        0
      ],
      "image_target": [
        "37",
        0
      ]
    },
    "class_type": "ColorMatch",
    "_meta": {
      "title": "Color Match"
    }
  },
  "56": {
    "inputs": {
      "text": "A man with a thick beard, wearing a backward cap, open flannel shirt, and white tank top, stands next to a flip chart. The chart has bold black text reading “IT’S NOT,” followed by “REAL ESTATE” in white letters on a red background. Below the text is a hand-drawn house, crossed out with a large red X, and a dashed arrow pointing away from it. His expression is mid-explanation, suggesting he's debunking the idea that real estate is the best investment. The background is a clean blue gradient, giving it a sharp, attention-grabbing look typical of YouTube thumbnails."
    },
    "class_type": "Textbox",
    "_meta": {
      "title": "Textbox"
    }
  },
  "63": {
    "inputs": {
      "model_path": "svdq-int4-flux.1-dev.safetensors",
      "cache_threshold": 0,
      "attention": "nunchaku-fp16",
      "cpu_offload": "auto",
      "device_id": 0,
      "data_type": "bfloat16",
      "i2f_mode": "enabled"
    },
    "class_type": "NunchakuFluxDiTLoader",
    "_meta": {
      "title": "Nunchaku FLUX DiT Loader"
    }
  },
  "68": {
    "inputs": {
      "width": 1280,
      "height": 720,
      "upscale_method": "nearest-exact",
      "keep_proportion": "stretch",
      "pad_color": "0, 0, 0",
      "crop_position": "top",
      "divisible_by": 2,
      "device": "cpu",
      "image": [
        "1",
        0
      ]
    },
    "class_type": "ImageResizeKJv2",
    "_meta": {
      "title": "Resize Image v2"
    }
  },
  "76": {
    "inputs": {
      "model_type": "flux.1",
      "text_encoder1": "clip_l.safetensors",
      "text_encoder2": "t5xxl_fp8_e4m3fn.safetensors",
      "t5_min_length": 512
    },
    "class_type": "NunchakuTextEncoderLoaderV2",
    "_meta": {
      "title": "Nunchaku Text Encoder Loader V2"
    }
  },
  "81": {
    "inputs": {
      "model_name": "RealESRGAN_x8.pth"
    },
    "class_type": "UpscaleModelLoader",
    "_meta": {
      "title": "Load Upscale Model"
    }
  },
  "84": {
    "inputs": {
      "upscale_by": 1.0000000000000002,
      "rescale_method": "lanczos",
      "upscale_model": [
        "81",
        0
      ],
      "image": [
        "51",
        0
      ]
    },
    "class_type": "UpscaleImageByUsingModel",
    "_meta": {
      "title": "Upscale Image By (Using Model)"
    }
  },
  "95": {
    "inputs": {
      "filename_prefix": "FormDez",
      "file_type": "WEBP (lossless)",
      "remove_metadata": true,
      "images": [
        "84",
        0
      ]
    },
    "class_type": "SaveImagePlus",
    "_meta": {
      "title": "Save Image Plus"
    }
  }
}
    """
    workflow = json.loads(workflow_api_json)

    # --- 3. Modify the Workflow with Your Inputs ---
    # Update the correct node IDs based on your actual workflow

    # Set the prompt text in the Textbox node (node "56")
    if prompt_text:
        workflow["56"]["inputs"]["text"] = prompt_text

    # Set the image filename in the LoadImage node (node "1")
    # We'll save the uploaded image as 'input.png'
    workflow["1"]["inputs"]["image"] = "input.png"

    # Randomize the seed in RandomNoise node (node "39")
    workflow["39"]["inputs"]["noise_seed"] = random.randint(0, 2147483647)

    # --- 4. Handle the Uploaded Image ---
    # Decode the base64 image and save it to ComfyUI's input folder
    if image_base64:
        # Strip Data URI prefix if present (e.g., "data:image/png;base64,")
        if "," in image_base64:
            # Find the comma and take everything after it
            base64_data = image_base64.split(",", 1)[1]
        else:
            # Assume it's already pure base64
            base64_data = image_base64
            
        try:
            image_data = base64.b64decode(base64_data)
            with open("/workspace/ComfyUI/input/input.png", "wb") as f:
                f.write(image_data)
        except Exception as e:
            return {"error": f"Failed to decode or save input image: {str(e)}"}

    # --- 5. Queue the Prompt & Get the Output ---
    try:
        req = requests.post(f"http://{COMFY_HOST}/prompt", json={"prompt": workflow}, timeout=30)
        req.raise_for_status()
        response_data = req.json()
        prompt_id = response_data.get('prompt_id')
        if not prompt_id:
            return {"error": f"No prompt_id in response: {response_data}"}
    except requests.RequestException as e:
        return {"error": f"Failed to queue workflow: {str(e)}"}

    output_image = None
    max_wait_time = 300  # Maximum wait time in seconds (5 minutes)
    start_time = time.time()
    
    while output_image is None:
        if time.time() - start_time > max_wait_time:
            return {"error": "Timeout waiting for workflow completion"}
            
        try:
            history_req = requests.get(f"http://{COMFY_HOST}/history/{prompt_id}", timeout=10)
            history_req.raise_for_status()
            history = history_req.json().get(prompt_id, {})
        except requests.RequestException as e:
            return {"error": f"Failed to check workflow status: {str(e)}"}
        
        # Check if the job is done and has outputs
        if history.get('outputs'):
            outputs = history['outputs']
            # Find your "SaveImagePlus" node's output (node "95")
            save_image_node_id = "95" 
            if save_image_node_id in outputs:
                node_output = outputs[save_image_node_id]
                if 'images' in node_output:
                    image_data = node_output['images'][0]
                    image_url = f"http://{COMFY_HOST}/view?filename={image_data['filename']}&subfolder={image_data.get('subfolder', '')}&type={image_data.get('type', 'output')}"
                    try:
                        response = requests.get(image_url, timeout=30)
                        response.raise_for_status()
                        output_image = response.content
                    except requests.RequestException as e:
                        return {"error": f"Failed to download output image: {str(e)}"}
            # If we have outputs but not the one we want, something is wrong, stop waiting.
            break 
            
        time.sleep(1.0)  # Wait 1 second between checks

    # --- 6. Return the Final Image ---
    if output_image:
        image_base64_out = base64.b64encode(output_image).decode('utf-8')
        return {"image_base64": image_base64_out}
    else:
        return {"error": "Failed to generate image."}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})