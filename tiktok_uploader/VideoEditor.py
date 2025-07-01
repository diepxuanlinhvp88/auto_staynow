from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip
import moviepy.video.fx as vfx
import os
import cv2
import numpy as np

class VideoEditor:
    def __init__(self, video_path):
        """Initialize video editor with input video path"""
        print(f"Loading video from: {video_path}")
        self.video = VideoFileClip(video_path)
        print(f"Video loaded. Duration: {self.video.duration}s, Size: {self.video.size}")
        self.audio = None
        self.text_clip = None
        
    def change_speed(self, speed_factor):
        """Change video speed - should be called first"""
        try:
            if speed_factor <= 0:
                raise ValueError("Speed factor must be positive")
            print(f"Changing video speed by factor: {speed_factor}")
            
            # Apply speed effect using new API
            self.video = self.video.with_effects([
                vfx.MultiplySpeed(factor=speed_factor)
            ])
            
            print(f"New video duration after speed change: {self.video.duration}s")
            return True
        except Exception as e:
            print(f"Error changing speed: {str(e)}")
            return False

    def add_audio(self, audio_path, volume=1.0):
        """Add audio to video and trim it to match video length"""
        print(f"Adding audio from: {audio_path} with volume {volume}")
        try:
            # Load audio
            audio = AudioFileClip(audio_path)
            print(f"Audio duration: {audio.duration}s, Video duration: {self.video.duration}s")
            
            # Create a new audio clip with the correct duration
            if audio.duration > self.video.duration:
                print(f"Trimming audio from {audio.duration}s to {self.video.duration}s")
                # Set duration directly
                audio.duration = self.video.duration
            elif audio.duration < self.video.duration:
                print(f"Looping audio to match video duration of {self.video.duration}s")
                # Calculate how many times we need to loop
                repeats = int(self.video.duration / audio.duration) + 1
                # Create a list of audio clips
                audio_clips = []
                current_time = 0
                while current_time < self.video.duration:
                    audio_clips.append(audio.copy())
                    current_time += audio.duration
                # Combine them into one clip
                audio = audio_clips[0]
                for clip in audio_clips[1:]:
                    audio = audio.concatenate_audioclips([audio, clip])
                # Set final duration
                audio.duration = self.video.duration
            
            # Store the audio
            self.audio = audio
            return True
        except Exception as e:
            print(f"Error adding audio: {str(e)}")
            return False

    def add_effects(self, effects_list):
        """Add visual effects to video"""
        try:
            effects = []
            for effect, value in effects_list:
                print(f"Adding effect: {effect} with value {value}")
                if effect == "mirror_x":
                    effects.append(vfx.MirrorX())
                elif effect == "mirror_y":
                    effects.append(vfx.MirrorY())
                # Add more effects as needed
            
            if effects:
                self.video = self.video.with_effects(effects)
            return True
        except Exception as e:
            print(f"Error adding effects: {str(e)}")
            return False

    def add_text(self, text, color="white", fontsize=35):
        """Add text to video at specified position (centered horizontally, 3/4 from top)"""
        try:
            print(f"Adding text: '{text}' with color {color} and size {fontsize}")
            
            # Get video dimensions
            w, h = self.video.size
            print(f"Video dimensions: {w}x{h}")
            
            # Create text clip with new API
            self.text_clip = (
                TextClip(
                    text=text,
                    font_size=fontsize,
                    color=color,
                    stroke_color="black",
                    stroke_width=2,
                    method='caption',
                    size=(w, None),
                    font="font/Be_Vietnam_Pro/BeVietnamPro-Bold.ttf"  # Width of video, auto-height
                )
                .with_duration(self.video.duration)
                .with_position(("center", h * 0.2))  # Center horizontally, 1/4 from top
            )
            
            print("Text overlay created successfully")
            return True
        except Exception as e:
            print(f"Error adding text: {str(e)}")
            return False

    def save(self, output_path):
        """Save edited video"""
        try:
            print("\nStarting video export process...")
            
            # Start with base video
            clips = [self.video]
            
            # Add text if exists
            if self.text_clip:
                print("Adding text overlay...")
                clips.append(self.text_clip)
            
            # Create final composition
            final = CompositeVideoClip(clips)
            
            # Add audio if exists
            if self.audio:
                print("Adding audio track...")
                final = final.with_audio(self.audio)
            
            print(f"Writing final video to: {output_path}")
            print(f"Final video properties: Duration={final.duration}s, Size={final.size}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write output file
            final.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=self.video.fps
            )
            
            # Clean up
            print("Cleaning up resources...")
            if self.text_clip:
                self.text_clip.close()
            if self.audio:
                self.audio.close()
            final.close()
            self.video.close()
            
            print("Video saved successfully!")
            return True
            
        except Exception as e:
            print(f"Error saving video: {str(e)}")
            return False

    def add_overlay(self, overlay_path, position="center", start_time=0, duration=None, opacity=1.0):
        """
        Thêm overlay (ảnh hoặc video) lên video chính
        - position: ("center", "center") hoặc (x, y)
        - opacity: độ trong suốt (0.0 -> 1.0)
        """
        try:
            if overlay_path.endswith(('.png', '.jpg', '.jpeg')):
                overlay = ImageClip(overlay_path)
            else:
                overlay = VideoFileClip(overlay_path)
            
            if duration:
                overlay = overlay.set_duration(duration)
            
            overlay = (overlay
                      .set_position(position)
                      .set_start(start_time)
                      .set_opacity(opacity))
            
            self.video = CompositeVideoClip([self.video, overlay])
            return self.video
        except Exception as e:
            print(f"Error adding overlay: {str(e)}")
            return self.video 


