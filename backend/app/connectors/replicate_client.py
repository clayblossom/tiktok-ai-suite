"""Replicate API Client — Image generation (FLUX), video generation."""
from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

import httpx

from ..config import REPLICATE_API_TOKEN
from ..utils.logging import get_logger
from ..utils import cost_tracker

logger = get_logger(__name__)

BASE_URL = "https://api.replicate.com/v1"
MAX_RETRIES = 3

# Model versions
FLUX_MODEL = "black-forest-labs/flux-schnell"
FLUX_DEV_MODEL = "black-forest-labs/flux-dev"
VIDEO_GEN_MODEL = "minimax/video-01-live"
IMAGE_UPSCALE_MODEL = "nightmareai/real-esrgan"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }


async def _create_prediction(model: str, input_data: dict, timeout: float = 120) -> dict:
    """Create a prediction and wait for completion."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Start prediction
        resp = await client.post(
            f"{BASE_URL}/predictions",
            headers=_headers(),
            json={"version": model, "input": input_data},
        )
        resp.raise_for_status()
        prediction = resp.json()

        # Poll for completion
        poll_url = prediction.get("urls", {}).get("get", "")
        max_polls = int(timeout / 2)
        for _ in range(max_polls):
            await asyncio.sleep(2)
            poll_resp = await client.get(poll_url, headers=_headers())
            prediction = poll_resp.json()
            status = prediction.get("status", "")
            if status == "succeeded":
                return prediction
            elif status == "failed":
                raise Exception(f"Replicate prediction failed: {prediction.get('error', 'Unknown error')}")

        raise Exception(f"Replicate prediction timed out after {timeout}s")


async def generate_image_flux(
    prompt: str,
    width: int = 1080,
    height: int = 1920,
    num_outputs: int = 1,
    guidance_scale: float = 7.5,
    model: str = FLUX_MODEL,
) -> list[str]:
    """Generate images using FLUX model.

    Returns list of image URLs.
    """
    if not REPLICATE_API_TOKEN:
        raise Exception("REPLICATE_API_TOKEN not configured")

    input_data = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_outputs": num_outputs,
    }
    if model == FLUX_DEV_MODEL:
        input_data["guidance_scale"] = guidance_scale

    prediction = await _create_prediction(model, input_data, timeout=180)
    output = prediction.get("output", [])
    if isinstance(output, str):
        output = [output]

    cost = cost_tracker.calculate_replicate_cost("flux", num_outputs)
    cost_tracker.track("replicate", "flux/generate", 0, cost,
                       {"prompt": prompt[:100], "model": model, "num_outputs": num_outputs})

    logger.info("image_generated", model=model, num_outputs=len(output))
    return output


async def generate_video(
    prompt: str,
    duration: float = 5.0,
    fps: int = 24,
) -> str:
    """Generate video using Replicate video models.

    Returns video URL.
    """
    if not REPLICATE_API_TOKEN:
        raise Exception("REPLICATE_API_TOKEN not configured")

    prediction = await _create_prediction(
        VIDEO_GEN_MODEL,
        {"prompt": prompt, "duration": duration, "fps": fps},
        timeout=300,
    )
    output = prediction.get("output", "")
    if isinstance(output, list):
        output = output[0] if output else ""

    cost = cost_tracker.calculate_replicate_cost("video_gen", int(duration))
    cost_tracker.track("replicate", "video/generate", 0, cost,
                       {"prompt": prompt[:100], "duration": duration})

    logger.info("video_generated", model=VIDEO_GEN_MODEL, duration=duration)
    return output


async def upscale_image(image_url: str, scale: int = 4) -> str:
    """Upscale an image using Real-ESRGAN.

    Returns upscaled image URL.
    """
    prediction = await _create_prediction(
        IMAGE_UPSCALE_MODEL,
        {"image": image_url, "scale": scale},
        timeout=120,
    )
    output = prediction.get("output", "")
    cost_tracker.track("replicate", "upscale", 0, 0.005)
    return output


async def download_file(url: str, output_path: str) -> str:
    """Download a file from Replicate output URL."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
    return output_path


async def check_status() -> dict:
    """Check Replicate API status and account info."""
    if not REPLICATE_API_TOKEN:
        return {"configured": False}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{BASE_URL}/account", headers=_headers())
            resp.raise_for_status()
            return {"configured": True, "account": resp.json()}
    except Exception as e:
        return {"configured": True, "error": str(e)}
