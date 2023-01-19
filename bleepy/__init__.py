"""Bleepy Package"""
from .bleepy import (AudioFile, File, MediaFile, ProfanityBlocker,
                     ProfanityDetector, ProfanityExtractor, SpeechToText,
                     VideoFile)

VERSION = "0.0.1"

def get_version():
    """Return Version"""
    return VERSION