import os, sys, subprocess
import argparse
import src

def main() -> int:
    print("Starting main function")
    parser = argparse.ArgumentParser(
        description="Produces a transcript of a .wav file",
    )
    parser.add_argument("audio_file")
    parser.add_argument(
        "-c",
        "--cleanup",
        action="store_true",
        help="if set, will delete the source audio after transcribing",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="if set, will overwrite any existing files on disk related to previous extraction attempts on the input video",
    )

    args = parser.parse_args()

    src.transcribe(args.audio_file, overwrite=args.overwrite, cleanup=args.cleanup)

    return 0


if __name__ == "__main__":
    sys.exit(main())