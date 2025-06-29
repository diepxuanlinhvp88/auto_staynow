import argparse
from tiktok_uploader import tiktok, Video
from tiktok_uploader.basics import eprint
from tiktok_uploader.Config import Config
from tiktok_uploader.VideoEditor import VideoEditor
import sys, os

if __name__ == "__main__":
    _ = Config.load("./config.txt")
    parser = argparse.ArgumentParser(description="TikTokAutoUpload CLI, scheduled and immediate uploads")
    subparsers = parser.add_subparsers(dest="subcommand")

    # Login subcommand.
    login_parser = subparsers.add_parser("login", help="Login into TikTok to extract the session id (stored locally)")
    login_parser.add_argument("-n", "--name", help="Name to save cookie as", required=True)

    # Upload subcommand.
    upload_parser = subparsers.add_parser("upload", help="Upload video on TikTok")
    upload_parser.add_argument("-u", "--users", help="Enter cookie name from login", required=True)
    upload_parser.add_argument("-v", "--video", help="Path to video file")
    upload_parser.add_argument("-yt", "--youtube", help="Enter Youtube URL")
    upload_parser.add_argument("-t", "--title", help="Title of the video", required=True)
    upload_parser.add_argument("-sc", "--schedule", type=int, default=0, help="Schedule time in seconds")
    upload_parser.add_argument("-ct", "--comment", type=int, default=1, choices=[0, 1])
    upload_parser.add_argument("-d", "--duet", type=int, default=0, choices=[0, 1])
    upload_parser.add_argument("-st", "--stitch", type=int, default=0, choices=[0, 1])
    upload_parser.add_argument("-vi", "--visibility", type=int, default=0, help="Visibility type: 0 for public, 1 for private")
    upload_parser.add_argument("-bo", "--brandorganic", type=int, default=0)
    upload_parser.add_argument("-bc", "--brandcontent", type=int, default=0)
    upload_parser.add_argument("-ai", "--ailabel", type=int, default=0)
    upload_parser.add_argument("-p", "--proxy", default="")

    # Video editing options
    upload_parser.add_argument("--audio", help="Path to audio file to add")
    upload_parser.add_argument("--audio-start", type=float, default=0, help="Start time for added audio (seconds)")
    upload_parser.add_argument("--audio-volume", type=float, default=1.0, help="Volume for added audio (0.0-1.0)")
    
    upload_parser.add_argument("--speed", type=float, help="Speed up/slow down video (e.g. 1.5 for faster, 0.5 for slower)")
    
    upload_parser.add_argument("--effects", nargs="+", help="Add effects: brightness-1.5 contrast-1.2 blur-3 mirror_x mirror_y")
    
    upload_parser.add_argument("--overlay", help="Path to overlay image/video")
    upload_parser.add_argument("--overlay-position", nargs=2, type=int, help="Overlay position (x y)")
    upload_parser.add_argument("--overlay-start", type=float, default=0, help="Start time for overlay (seconds)")
    upload_parser.add_argument("--overlay-duration", type=float, help="Duration for overlay (seconds)")
    upload_parser.add_argument("--overlay-opacity", type=float, default=1.0, help="Opacity for overlay (0.0-1.0)")
    
    upload_parser.add_argument("--text", help="Text to add to video")
    upload_parser.add_argument("--text-position", nargs=2, type=int, help="Text position (x y)")
    upload_parser.add_argument("--text-color", default="white", help="Text color")
    upload_parser.add_argument("--text-size", type=int, default=70, help="Text font size")
    upload_parser.add_argument("--text-bg", help="Text background color")

    # Edit subcommand
    edit_parser = subparsers.add_parser("edit", help="Edit video without uploading")
    edit_parser.add_argument("-i", "--input", help="Name of video file from input directory", required=True)
    edit_parser.add_argument("-o", "--output", help="Name for output video file (will be saved in videos directory)", required=True)
    edit_parser.add_argument("-a", "--audio", help="Name of audio file from music directory")
    edit_parser.add_argument("-av", "--audio-volume", type=float, default=1.0, help="Volume for added audio (0.0-1.0)")
    edit_parser.add_argument("-s", "--speed", type=float, help="Speed up/slow down video (e.g. 1.5 for faster)")
    edit_parser.add_argument("-e", "--effects", nargs="+", help="Add effects: brightness-1.5 contrast-1.2 blur-3 mirror_x mirror_y")
    edit_parser.add_argument("-t", "--text", help="Text to add to video")
    edit_parser.add_argument("-tc", "--text-color", default="white", help="Text color")
    edit_parser.add_argument("-ts", "--text-size", type=int, default=70, help="Text font size")

    # Show subcommand
    show_parser = subparsers.add_parser("show", help="Show users and videos available for system.")
    show_parser.add_argument("-u", "--users", action='store_true', help="Shows all available cookie names")
    show_parser.add_argument("-v", "--videos", action='store_true', help="Shows all available processed videos")
    show_parser.add_argument("-i", "--input", action='store_true', help="Shows all available input videos")
    show_parser.add_argument("-m", "--music", action='store_true', help="Shows all available music files")

    # Parse the command-line arguments
    args = parser.parse_args()

    if args.subcommand == "login":
        if not hasattr(args, 'name') or args.name is None:
            parser.error("The 'name' argument is required for the 'login' subcommand.")
        login_name = args.name
        tiktok.login(login_name)

    elif args.subcommand == "upload":
        if not hasattr(args, 'users') or args.users is None:
            parser.error("The 'cookie' argument is required for the 'upload' subcommand.")
        
        if args.video is None and args.youtube is None:
            eprint("No source provided. Use -v or -yt to provide video source.")
            sys.exit(1)
        if args.video and args.youtube:
            eprint("Both -v and -yt flags cannot be used together.")
            sys.exit(1)

        if args.youtube:
            video_obj = Video(args.youtube, args.title)
            video_obj.is_valid_file_format()
            video = video_obj.source_ref
            args.video = video
        else:
            if not os.path.exists(os.path.join(os.getcwd(), Config.get().videos_dir, args.video)) and args.video:
                print("[-] Video does not exist")
                print("Video Names Available: ")
                video_dir = os.path.join(os.getcwd(), Config.get().videos_dir)
                for name in os.listdir(video_dir):
                    print(f'[-] {name}')
                sys.exit(1)

        tiktok.upload_video(args.users, args.video, args.title, args.schedule, args.comment, args.duet, args.stitch, args.visibility, args.brandorganic, args.brandcontent, args.ailabel, args.proxy)

    elif args.subcommand == "edit":
        # Check if input file exists in input directory
        input_path = os.path.join(os.getcwd(), Config.get().video_input_dir, args.input)
        if not os.path.exists(input_path):
            print("[-] Input video does not exist")
            print("Available Input Videos: ")
            input_dir = os.path.join(os.getcwd(), Config.get().video_input_dir)
            for name in os.listdir(input_dir):
                if name.endswith(('.mp4', '.webm')):
                    print(f'[-] {name}')
            sys.exit(1)

        try:
            # Initialize video editor
            editor = VideoEditor(input_path)
            
            # Change speed first if specified
            if args.speed:
                if not editor.change_speed(args.speed):
                    print("[-] Error changing video speed")
                    sys.exit(1)
            
            # Then add audio if specified
            if args.audio:
                audio_path = os.path.join(os.getcwd(), Config.get().music_dir, args.audio)
                if not os.path.exists(audio_path):
                    print("[-] Audio file does not exist")
                    print("Music Files Available: ")
                    music_dir = os.path.join(os.getcwd(), Config.get().music_dir)
                    for name in os.listdir(music_dir):
                        if name.endswith(('.mp3', '.wav', '.m4a')):
                            print(f'[-] {name}')
                    sys.exit(1)
                if not editor.add_audio(audio_path, volume=args.audio_volume):
                    print("[-] Error adding audio")
                    sys.exit(1)
            
            # Add effects if specified
            if args.effects:
                effects_list = []
                for effect in args.effects:
                    if '-' in effect:
                        name, value = effect.split('-')
                        effects_list.append((name, float(value)))
                    else:
                        effects_list.append((effect, None))
                if not editor.add_effects(effects_list):
                    print("[-] Error adding effects")
                    sys.exit(1)
            
            # Finally add text if specified
            if args.text:
                if not editor.add_text(args.text, color=args.text_color, fontsize=args.text_size):
                    print("[-] Error adding text")
                    sys.exit(1)
            
            # Save edited video to videos directory
            output_path = os.path.join(os.getcwd(), Config.get().videos_dir, args.output)
            print(f"[-] Saving edited video to: {output_path}")
            if not editor.save(output_path):
                print("[-] Error saving edited video")
                sys.exit(1)
            print("[-] Video editing completed successfully!")

        except Exception as e:
            print(f"[-] Error editing video: {str(e)}")
            sys.exit(1)

    elif args.subcommand == "show":
        if args.users:
            print("User Names logged in: ")
            cookie_dir = os.path.join(os.getcwd(), Config.get().cookies_dir)
            for name in os.listdir(cookie_dir):
                if name.startswith("tiktok_session-"):
                    print(f'[-] {name.split("tiktok_session-")[1]}')

        if args.videos:
            print("Processed Videos: ")
            video_dir = os.path.join(os.getcwd(), Config.get().videos_dir)
            for name in os.listdir(video_dir):
                if name.endswith(('.mp4', '.webm')):
                    print(f'[-] {name}')

        if args.input:
            print("Input Videos: ")
            input_dir = os.path.join(os.getcwd(), Config.get().video_input_dir)
            for name in os.listdir(input_dir):
                if name.endswith(('.mp4', '.webm')):
                    print(f'[-] {name}')

        if args.music:
            print("Music Files: ")
            music_dir = os.path.join(os.getcwd(), Config.get().music_dir)
            for name in os.listdir(music_dir):
                if name.endswith(('.mp3', '.wav', '.m4a')):
                    print(f'[-] {name}')

        if not args.users and not args.videos and not args.input and not args.music:
            print("No flag provided. Use -u (show users), -v (show processed videos), -i (show input videos), or -m (show music).")

    else:
        eprint("Invalid subcommand. Use 'login', 'upload', 'edit' or 'show'.")


