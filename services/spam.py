"""
Spam detection service using ML model.

Features:
- Lazy loading of ML models (faster startup)
- Quick substring check before expensive ML inference
- Auto-unload after TTL to save RAM
"""
from typing import Optional
import logging
import threading
import time
import gc

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

MODEL_PATH = "ruspam_model/torch/"

# lazy-loaded model and tokenizer
_tokenizer: Optional[AutoTokenizer] = None
_model: Optional[AutoModelForSequenceClassification] = None
_last_used: float = 0.0  # timestamp of last usage

# Guards all access to the globals above
_lock = threading.RLock()

# known spam substrings to check first (faster than ML)
SPAM_SUBSTRINGS = [
    "official_vpnbot",
    "rkt_vpn_bot",
    "vpnbot",
    "vpn_bot",
    "oflvpn"
]

# precompute lowercase versions for faster matching
_SPAM_SUBSTRINGS_LOWER = [s.lower() for s in SPAM_SUBSTRINGS]


def _get_tokenizer() -> AutoTokenizer:
    """Lazy load tokenizer on first use. Hold _lock before calling."""
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
    return _tokenizer


def _get_model() -> AutoModelForSequenceClassification:
    """Lazy load model on first use. Hold _lock before calling."""
    global _model
    if _model is None:
        _model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_PATH, local_files_only=True,
            low_cpu_mem_usage=False, device_map=None,
            dtype=torch.float32,
        )
        # guard: only move if real weights exist
        if not any(p.is_meta for p in _model.parameters()):
            _model.to("cpu")
        _model.eval()  # Set to evaluation mode
    return _model


def _touch() -> None:
    """Update last used timestamp."""
    global _last_used
    _last_used = time.time()


def predict(text: str) -> bool:
    """
    Predict if text is spam.

    Args:
        text: Text to check for spam

    Returns:
        True if spam, False otherwise
    """
    # quick check for known spam patterns (O(n) string search)
    text_lower = text.lower()
    if any(sub in text_lower for sub in _SPAM_SUBSTRINGS_LOWER):
        return True

    # ML prediction (lazy load models)
    result = _run_inference(text)
    if result is not None:
        return result

    # torch state corrupted (meta device) - force reload and retry once
    logger.warning("Spam inference failed, attempting recovery...")
    try:
        _force_reload()
    except Exception as e:
        logger.error(f"Spam model reload failed: {e}, returning safe fallback")
        return False

    result = _run_inference(text)
    if result is not None:
        return result

    logger.error("Spam inference failed after recovery, returning safe fallback")
    return False


def _run_inference(text: str) -> Optional[bool]:
    """Run model inference, returns None on torch device errors."""
    try:
        # Load + capture local refs under the lock so a concurrent unload
        # (sets globals to None) can't free the objects mid-inference
        with _lock:
            tokenizer = _get_tokenizer()
            model = _get_model()
            _touch()  # update last used time

        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=1).item()

        return predicted_class == 1
    except RuntimeError as e:
        if "meta" in str(e) or "expected device" in str(e).lower():
            return None
        raise


def _force_reload() -> None:
    """Force full model reload, clearing corrupted torch state."""
    global _model, _tokenizer

    logger.warning("Forcing full spam model reload (torch state recovery)")

    with _lock:
        _model = None
        _tokenizer = None

        gc.collect()

        _get_tokenizer()
        _get_model()


def preload_model() -> None:
    """
    Preload the ML model (call during startup if you want eager loading).
    Useful if you want to avoid latency on first spam check.
    """
    with _lock:
        _get_tokenizer()
        _get_model()
        _touch()


def unload_model() -> bool:
    """Free memory by unloading model."""
    global _model, _tokenizer, _last_used

    with _lock:
        if _model is None and _tokenizer is None:
            return False

        _model = None
        _tokenizer = None
        _last_used = 0.0

        gc.collect()
    return True


def is_loaded() -> bool:
    """Check if model is currently loaded."""
    return _model is not None


def get_last_used() -> float:
    """Get timestamp of last model usage."""
    return _last_used
