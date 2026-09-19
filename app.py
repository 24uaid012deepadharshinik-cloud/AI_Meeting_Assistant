from flask import Flask, render_template, request, jsonify
from ollama_ai import generate_minutes
from speech_to_text import transcribe_audio

from moviepy import VideoFileClip

import os
import uuid


app = Flask(__name__)


# =========================================================
# UPLOAD SETTINGS
# =========================================================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum video size = 500 MB
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024


# Allowed video formats
ALLOWED_VIDEO_EXTENSIONS = {
    "mp4",
    "webm",
    "mov",
    "mkv",
    "avi"
}


def allowed_video(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_VIDEO_EXTENSIONS
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# VOICE RECORDING → SPEECH TO TEXT
# =========================================================

@app.route("/transcribe", methods=["POST"])
def transcribe():

    if "audio" not in request.files:

        return jsonify({
            "success": False,
            "error": "No audio file received."
        }), 400


    audio = request.files["audio"]


    if audio.filename == "":

        return jsonify({
            "success": False,
            "error": "No audio file selected."
        }), 400


    try:

        # Create unique filename
        filename = f"{uuid.uuid4()}.webm"


        audio_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )


        # Save recorded audio
        audio.save(audio_path)


        # Speech to text
        transcript = transcribe_audio(audio_path)


        return jsonify({

            "success": True,

            "transcript": transcript

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# VIDEO UPLOAD → AUDIO EXTRACTION → SPEECH TO TEXT
# =========================================================

@app.route("/upload_video", methods=["POST"])
def upload_video():

    # Check whether video was received
    if "video" not in request.files:

        return jsonify({

            "success": False,

            "error": "No video file received."

        }), 400


    video = request.files["video"]


    # Check filename
    if video.filename == "":

        return jsonify({

            "success": False,

            "error": "No video file selected."

        }), 400


    # Check video format
    if not allowed_video(video.filename):

        return jsonify({

            "success": False,

            "error":
                "Unsupported video format. "
                "Use MP4, WebM, MOV, MKV or AVI."

        }), 400


    video_path = None

    audio_path = None


    try:

        # Get extension
        extension = video.filename.rsplit(
            ".",
            1
        )[1].lower()


        # Create unique video filename
        video_filename = (
            f"{uuid.uuid4()}.{extension}"
        )


        video_path = os.path.join(
            UPLOAD_FOLDER,
            video_filename
        )


        # Save video
        video.save(video_path)


        # -------------------------------------------------
        # Extract audio from video
        # -------------------------------------------------

        audio_filename = (
            f"{uuid.uuid4()}.wav"
        )


        audio_path = os.path.join(
            UPLOAD_FOLDER,
            audio_filename
        )


        video_clip = VideoFileClip(video_path)


        # Extract audio
        video_clip.audio.write_audiofile(
            audio_path,
            logger=None
        )


        # Close video
        video_clip.close()


        # -------------------------------------------------
        # Convert speech to text
        # -------------------------------------------------

        transcript = transcribe_audio(
            audio_path
        )


        return jsonify({

            "success": True,

            "transcript": transcript

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# GENERATE MINUTES USING OLLAMA
# =========================================================

@app.route("/generate", methods=["POST"])
def generate():

    transcript = request.form.get(
        "transcript",
        ""
    ).strip()


    if not transcript:

        return jsonify({

            "success": False,

            "error":
                "No meeting transcript received."

        }), 400


    try:

        # Send transcript to Ollama
        result = generate_minutes(
            transcript
        )


        return jsonify({

            "success": True,

            "minutes": result

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# RUN FLASK APP
# =========================================================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
    