import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
import numpy as np

def parse_text_file(file_path):
    """Parse the text file with timestamps and messages."""
    entries = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    time, message = parts
                    minutes, seconds = map(int, time.split(':'))
                    timestamp = minutes * 60 + seconds
                    entries.append((timestamp, message))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse text file: {e}")
    return entries

def create_message_frame(message, frame_size, duration, fps, bg_color):
    """Create a frame with the message displayed."""
    width, height = frame_size
    font_scale = 2
    font_thickness = 3
    color = (255, 255, 255)

    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = bg_color

    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(message, font, font_scale, font_thickness)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2
    cv2.putText(frame, message, (text_x, text_y), font, font_scale, color, font_thickness, lineType=cv2.LINE_AA)

    return [frame for _ in range(int(duration * fps))]

def process_video(video_path, text_entries, output_path, bg_color):
    """Process the video to interleave frames with messages."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Cannot open video file")

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (width, height)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

        text_entries.sort()
        current_entry_index = 0
        current_message_frames = []

        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            current_time = frame_count / fps

            if (current_entry_index < len(text_entries) and
                current_time >= text_entries[current_entry_index][0]):

                message = text_entries[current_entry_index][1]
                current_message_frames = create_message_frame(message, frame_size, 5, fps, bg_color)
                for mf in current_message_frames:
                    out.write(mf)
                current_entry_index += 1

            out.write(frame)
            frame_count += 1

        cap.release()
        out.release()
        messagebox.showinfo("Success", f"Video saved to {output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to process video: {e}")

def select_video():
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
    if video_path:
        video_var.set(video_path)

def select_text_file():
    text_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if text_path:
        text_var.set(text_path)

def select_output_file():
    output_path = filedialog.asksaveasfilename(filetypes=[("Video Files", "*.mp4")], defaultextension=".mp4")
    if output_path:
        output_var.set(output_path)

def process():
    video_path = video_var.get()
    text_path = text_var.get()
    output_path = output_var.get()
    bg_color_hex = bg_color_var.get()

    if not video_path or not text_path or not output_path:
        messagebox.showerror("Error", "Please select all required files and specify output path.")
        return

    try:
        # Convert hex color to BGR for OpenCV
        bg_color = tuple(int(bg_color_hex.lstrip('#')[i:i+2], 16) for i in (4, 2, 0))
    except:
        messagebox.showerror("Error", "Invalid background color.")
        return

    text_entries = parse_text_file(text_path)
    if not text_entries:
        messagebox.showerror("Error", "No valid entries in the text file.")
        return

    process_video(video_path, text_entries, output_path, bg_color)

# Create the GUI
root = tk.Tk()
root.title("Video Text Overlay Tool")

video_var = tk.StringVar()
text_var = tk.StringVar()
output_var = tk.StringVar()
bg_color_var = tk.StringVar()

# Video file selection
tk.Label(root, text="Video File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
video_button = tk.Button(root, text="Browse", command=select_video)
video_button.grid(row=0, column=1, padx=10, pady=5, sticky="w")
video_label = tk.Label(root, textvariable=video_var, anchor="w", width=50, relief="sunken")
video_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

# Text file selection
tk.Label(root, text="Text File:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
text_button = tk.Button(root, text="Browse", command=select_text_file)
text_button.grid(row=1, column=1, padx=10, pady=5, sticky="w")
text_label = tk.Label(root, textvariable=text_var, anchor="w", width=50, relief="sunken")
text_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")

# Output file selection
tk.Label(root, text="Output File:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
output_button = tk.Button(root, text="Browse", command=select_output_file)
output_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")
output_label = tk.Label(root, textvariable=output_var, anchor="w", width=50, relief="sunken")
output_label.grid(row=2, column=2, padx=10, pady=5, sticky="w")

# Background color
tk.Label(root, text="Background Color (Hex):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
bg_color_entry = tk.Entry(root, textvariable=bg_color_var, width=10)
bg_color_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

# Process button
process_button = tk.Button(root, text="Process Video", command=process)
process_button.grid(row=4, column=0, columnspan=3, pady=10)

root.mainloop()
