import runpod
import requests
import json
import time
import os
import base64
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
COMFY_HOST = os.getenv("COMFY_HOST", "127.0.0.1:3001")  # Updated to match install script
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE_MB", "20")) * 1024 * 1024  # 20MB default
COMFY_DIR = "/workspace/ComfyUI"

def check_comfyui_health():
    """Check if ComfyUI is running and accessible"""
    try:
        response = requests.get(f"http://{COMFY_HOST}/", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def wait_for_comfyui(timeout=60):
    """Wait for ComfyUI to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_comfyui_health():
            logger.info("ComfyUI is ready")
            return True
        logger.info("Waiting for ComfyUI to start...")
        time.sleep(2)
    return False

def handler(job):
    try:
        logger.info(f"Starting job processing: {job.get('id', 'unknown')}")
        
        # === FILESYSTEM DEBUG START ===
        logger.info(f"Contents of /runpod-volume: {os.listdir('/runpod-volume') if os.path.exists('/runpod-volume') else 'Directory not found'}")
        if os.path.exists('/runpod-volume/ComfyUI/models'):
            logger.info(f"Contents of /runpod-volume/ComfyUI/models: {os.listdir('/runpod-volume/ComfyUI/models')}")
            # Check each model subdirectory
            model_subdirs = ['checkpoints', 'vae', 'controlnet', 'clip', 'upscale_models', 'text_encoders']
            for subdir in model_subdirs:
                subdir_path = f'/runpod-volume/ComfyUI/models/{subdir}'
                if os.path.exists(subdir_path):
                    files = os.listdir(subdir_path)
                    logger.info(f"Contents of {subdir_path}: {files}")
                else:
                    logger.info(f"{subdir_path}: Directory not found")
        else:
            logger.info("/runpod-volume/ComfyUI/models: Directory not found")
        logger.info("=== FILESYSTEM DEBUG END ===")
        # Check if ComfyUI is ready
        if not check_comfyui_health():
            logger.error("ComfyUI is not accessible")
            if not wait_for_comfyui():
                return {"error": "ComfyUI service is not available"}
        
        job_input = job["input"]

        # --- 1. Get Your API Inputs ---
        # We expect a 'prompt' and a base64 'image' from the API call
        prompt_text = job_input.get("prompt")
        image_base64 = job_input.get("image")
        
        # Validate required inputs
        if not prompt_text or not isinstance(prompt_text, str):
            return {"error": "Missing or invalid 'prompt' parameter - must be a non-empty string"}
        
        if not image_base64 or not isinstance(image_base64, str):
            return {"error": "Missing or invalid 'image' parameter - must be a base64 encoded string"}
            
        # Validate prompt length
        if len(prompt_text.strip()) == 0:
            return {"error": "Prompt cannot be empty"}
            
        if len(prompt_text) > 2000:
            return {"error": "Prompt too long (max 2000 characters)"}
            
        logger.info(f"Processing prompt: {prompt_text[:100]}...")
        
    except Exception as e:
        logger.error(f"Error in input validation: {str(e)}")
        return {"error": f"Input validation failed: {str(e)}"}

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
      "model_name": "4x-UltraSharp.pth"
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
    try:
        # Strip Data URI prefix if present (e.g., "data:image/png;base64,")
        if "," in image_base64:
            # Find the comma and take everything after it
            base64_data = image_base64.split(",", 1)[1]
        else:
            # Assume it's already pure base64
            base64_data = image_base64
            
        # Validate base64 format
        try:
            image_data = base64.b64decode(base64_data, validate=True)
        except Exception as e:
            logger.error(f"Invalid base64 image data: {str(e)}")
            return {"error": "Invalid base64 image data"}
            
        # Check image size (optional but recommended)
        if len(image_data) > MAX_IMAGE_SIZE:
            return {"error": f"Image too large (max {MAX_IMAGE_SIZE // (1024*1024)}MB)"}
            
        if len(image_data) < 100:  # Minimum reasonable image size
            return {"error": "Image data too small - likely corrupted"}
            
        # Ensure input directory exists
        input_dir = os.path.join(COMFY_DIR, "input")
        os.makedirs(input_dir, exist_ok=True)
        
        input_path = os.path.join(input_dir, "input.png")
        with open(input_path, "wb") as f:
            f.write(image_data)
            
        logger.info(f"Successfully saved input image ({len(image_data)} bytes)")
        
    except Exception as e:
        logger.error(f"Failed to process input image: {str(e)}")
        return {"error": f"Failed to process input image: {str(e)}"}

    # --- Debug: Check available nodes ---
    try:
        logger.info("Checking available ComfyUI nodes...")
        nodes_req = requests.get(f"http://{COMFY_HOST}/object_info", timeout=10)
        if nodes_req.status_code == 200:
            available_nodes = nodes_req.json()
            required_nodes = ["AIO_Preprocessor", "GetImageSize+", "ColorMatch", "NunchakuFluxDiTLoader", "ImageResizeKJv2", "SaveImagePlus"]
            missing_nodes = []
            for node in required_nodes:
                if node not in available_nodes:
                    missing_nodes.append(node)
                    logger.warning(f"Missing required node: {node}")
                else:
                    logger.info(f"Found required node: {node}")
            
            if missing_nodes:
                logger.error(f"Missing custom nodes: {missing_nodes}")
                return {"error": f"Missing required custom nodes: {missing_nodes}. Please ensure all custom nodes are properly installed and loaded."}
        else:
            logger.warning(f"Could not check available nodes (status: {nodes_req.status_code})")
    except requests.RequestException as e:
        logger.warning(f"Could not check available nodes: {str(e)}")

    # --- 5. Queue the Prompt & Get the Output ---
    try:
        logger.info("Queuing workflow to ComfyUI...")
        req = requests.post(f"http://{COMFY_HOST}/prompt", json={"prompt": workflow}, timeout=30)
        req.raise_for_status()
        response_data = req.json()
        prompt_id = response_data.get('prompt_id')
        if not prompt_id:
            logger.error(f"No prompt_id in ComfyUI response: {response_data}")
            return {"error": f"No prompt_id in response: {response_data}"}
        logger.info(f"Workflow queued successfully with prompt_id: {prompt_id}")
    except requests.RequestException as e:
        logger.error(f"Failed to queue workflow: {str(e)}")
        return {"error": f"Failed to queue workflow: {str(e)}"}

    output_image = None
    # Just keep checking until RunPod kills us or we get results
    # Keep these variables for progress tracking (not timeout!)
    check_count = 0
    start_time = time.time()  # Just for progress logging, not timeout

    while output_image is None:
        check_count += 1
        
        # Log progress every 10 seconds (but don't timeout!)
        if check_count % 10 == 0:
            elapsed_time = time.time() - start_time  # Calculate how long we've been waiting
            logger.info(f"Still waiting for completion... ({elapsed_time:.1f}s elapsed)")
                
        try:
            history_req = requests.get(f"http://{COMFY_HOST}/history/{prompt_id}", timeout=60)
            history_req.raise_for_status()
            history = history_req.json().get(prompt_id, {})
        except requests.RequestException as e:
            logger.error(f"Failed to check workflow status: {str(e)}")
            return {"error": f"Failed to check workflow status: {str(e)}"}
            
        # Check for errors in the workflow execution
        if 'status' in history and history['status'].get('status_str') == 'error':
            error_details = history['status'].get('messages', [])
            logger.error(f"Workflow execution failed: {error_details}")
            return {"error": f"Workflow execution failed: {error_details}"}
            
        # Check if the job is done and has outputs
        if history.get('outputs'):
            outputs = history['outputs']
            logger.info("Workflow completed, processing outputs...")
            # Find your "SaveImagePlus" node's output (node "95")
            save_image_node_id = "95" 
            if save_image_node_id in outputs:
                node_output = outputs[save_image_node_id]
                if 'images' in node_output and len(node_output['images']) > 0:
                    image_data = node_output['images'][0]
                    image_url = f"http://{COMFY_HOST}/view?filename={image_data['filename']}&subfolder={image_data.get('subfolder', '')}&type={image_data.get('type', 'output')}"
                    try:
                        logger.info(f"Downloading output image: {image_data['filename']}")
                        response = requests.get(image_url, timeout=30)
                        response.raise_for_status()
                        output_image = response.content
                        logger.info(f"Successfully downloaded output image ({len(output_image)} bytes)")
                    except requests.RequestException as e:
                        logger.error(f"Failed to download output image: {str(e)}")
                        return {"error": f"Failed to download output image: {str(e)}"}
                else:
                    logger.error("No images found in SaveImagePlus node output")
                    return {"error": "No images generated by the workflow"}
            else:
                logger.error(f"SaveImagePlus node (ID: {save_image_node_id}) not found in outputs")
                return {"error": "Expected output node not found"}
            # If we have outputs but not the one we want, something is wrong, stop waiting.
            break 
                
        time.sleep(1.0)  # Wait 1 second between checks

    # --- 6. Return the Final Image ---
    if output_image:
        image_base64_out = base64.b64encode(output_image).decode('utf-8')
        return {
            "images": [
                {
                    "filename": f"FormDez_{prompt_id}.webp",
                    "type": "base64",
                    "data": image_base64_out
                }
            ]
        }
    else:
        return {"error": "Failed to generate image."}


def health_check():
    """Health check endpoint for RunPod"""
    try:
        comfy_healthy = check_comfyui_health()
        return {
            "status": "healthy" if comfy_healthy else "unhealthy",
            "comfyui": "running" if comfy_healthy else "not_running",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }


def initialize_comfyui():
    """Initialize ComfyUI server on startup"""
    import subprocess
    import threading
    
    def start_comfyui():
        """Start ComfyUI server in background"""
        try:
            # Start ComfyUI server using the virtual environment
            # This matches your install script setup
            command = [
                "/bin/bash", "-c",
                f"cd {COMFY_DIR} && source venv/bin/activate && python main.py --listen --port 3001"
            ]
            subprocess.run(command, check=False)
        except Exception as e:
            logger.error(f"Failed to start ComfyUI: {str(e)}")
    
    logger.info("Starting ComfyUI server...")
    # Start ComfyUI in a separate thread
    comfyui_thread = threading.Thread(target=start_comfyui, daemon=True)
    comfyui_thread.start()
    
    # Wait for ComfyUI to be ready
    if wait_for_comfyui(timeout=120):  # Wait up to 2 minutes for startup
        logger.info("ComfyUI initialization complete")
        return True
    else:
        logger.error("ComfyUI failed to start within timeout period")
        return False

if __name__ == "__main__":
    # Initialize ComfyUI on startup
    if not initialize_comfyui():
        logger.error("Failed to initialize ComfyUI - exiting")
        exit(1)
    
    logger.info("Starting RunPod serverless handler...")
    runpod.serverless.start({
        "handler": handler,
        "rp_healthcheck": health_check
    })