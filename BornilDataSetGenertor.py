import os
import cv2
import csv
import pandas as pd
from moviepy.editor import VideoFileClip


# Provide the path to the folder containing videos
input_folder = "path/to/content/drive/MyDrive/sign_language/platform/dataset/bn-BdSL/dataset_temp/recording/"

# Provide the path to the output folder for frames
output_frames_folder = "path/to/output/frames/folder"

# Provide the path to the input CSV file
csv_file_path = "./texts.csv"

# Provide the path to output the extracted data csv
output_csv_file = "./bornil.csv"


def csv_output_generator(input_csv_path, output_csv_path):
    # Open input CSV file
    try:
        with open(input_csv_path, 'r', encoding= 'utf-8') as input_file:
            reader = csv.DictReader(input_file)
            
            # Open output CSV file
            with open(output_csv_path, 'w', newline='', encoding='utf-8') as output_file:
                writer = csv.writer(output_file)
                # Write headers
                writer.writerow(['name|video|start|end|speaker|orth|translation'])


                # Iterate through rows in the input CSV file and write transformed data to the output CSV file
                for row in reader:
                    translation = row['content'] 
                    if len(translation.split()) <= 15:  # Check if translation has 15 or fewer word
                        name = row['recording'].replace('.webm', '')  # Remove ".webm" from recording name
                        video = f"{name}/1/*.png"
                        start = "-1"  # Set start value to -1
                        end = "-1"  # Set end value to -1
                        speaker = 'Signer'
                        orth = row['content']
                        combined_data = f"{name}|{video}|{start}|{end}|{speaker}|{orth}|{translation}"
                        writer.writerow([combined_data])
        print("CSV file generated successfully")

    except Exception as e:
        print(e)
        print("Provide the csv_file_path and output_csv_file")       

def load_csv_to_dataframe(csv_path):
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')

        # Filter rows where the contents column has less than 15 words
        filtered_df = df[df['content'].apply(lambda x: len(x.split()) <= 15)]
        
        after_filtering = filtered_df['recording'].apply(lambda x: x.replace(".webm", "")).tolist()
        
        # Output the recordings
        return after_filtering
    except Exception as e:
        print(e)
        print("Provide the csv_file_path")

def generate_csv(input_file_path, output_file_path):
    def filter_translation(text):
        return len(text.split()) <= 15

    def transform_row(row):
        name = row['recording'].replace('.webm', '')
        video = f"{name}/1/*.png"
        start = "-1"
        end = "-1"
        speaker = 'Signer'
        orth = row['content']
        translation = row['content']  # Assuming translation is the same as content
        return [name, video, start, end, speaker, orth, translation]

    with open(input_file_path, 'r') as input_file:
        reader = csv.DictReader(input_file)
        
        with open(output_file_path, 'w', newline='') as output_file:
            writer = csv.writer(output_file, delimiter='|')

            # Write headers
            writer.writerow(['name', 'video', 'start', 'end', 'speaker', 'orth', 'translation'])

            # Iterate through rows in the input CSV file, filter out rows with translation longer than 15 words,
            # and write transformed data to the output CSV file
            for row in reader:
                translation = row['content']
                if filter_translation(translation):
                    writer.writerow(transform_row(row))

def extract_frames(clip, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Initialize frame count
    frame_count = 0
    frames_extracted = 1
    # Read the video frame by frame
    for frame in clip.iter_frames():
        # Resize frame to 256x256 pixels
        frame = cv2.resize(frame, (256, 256))

        # Convert color space from RGB to BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Save frame as PNG file for every alternate frame
        if frame_count % 2 == 0:
            frame_path = os.path.join(output_folder, f"{frames_extracted:03d}.png")
            cv2.imwrite(frame_path, frame_bgr)
            frames_extracted += 1

        frame_count += 1

    print(f"Frames extracted: {frames_extracted} from {frame_count} frames")
       
def convert_videos_to_frames_using_moviepy(input_folder, output_frames_folder, csv_path):
    try:
        # Load csv to get list of recordings with long contents
        recordings_with_long_contents = load_csv_to_dataframe(csv_path)

        # Create output folder for frames if it doesn't exist
        os.makedirs(output_frames_folder, exist_ok=True)

        # Iterate through all files in the input folder
        for file in os.listdir(input_folder):
            # Check if file is a video file
            if file.endswith(".webm"):
                video_path = os.path.join(input_folder, file)
                video_name = os.path.splitext(file)[0]

                # Check if the video is in the recordings_with_long_contents list
                if video_name in recordings_with_long_contents:
                    output_folder = os.path.join(output_frames_folder, video_name, "1")

                    # Load the video clip
                    clip = VideoFileClip(video_path)

                    # Extract frames from the video
                    extract_frames(clip, output_folder)

                    # Close the video clip
                    clip.close()

                    print(f"Frames extracted for {video_name}")

                else:
                    print(f"Skipping {video_name} as it exceeds 15 words")
                    
        print("Frames extracted successfully")

    except Exception as e:
        print(e)
        print("Provide the input_folder, output_frames_folder, csv_file_path")
   
def convert_videos_to_frames__using_openCV(input_folder, output_frames_folder, csv_path):
    #For only selectinh the
    recordings_with_long_contents = load_csv_to_dataframe(csv_path)
    # Create output folder for frames if it doesn't exist
    os.makedirs(output_frames_folder, exist_ok=True)
    
    try:
    
        # Iterate through all files in the input folder
        for file in os.listdir(input_folder):
            
            # Check if file is a video file
            video_path = os.path.join(input_folder, file)
            video_name = os.path.splitext(file)[0]
            
            if file.endswith(".webm") and video_name in recordings_with_long_contents:
                
                # print(video_name)
                output_folder = os.path.join(output_frames_folder, video_name, "1")

                # Check video duration
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                # duration = frame_count / fps
                # cap.release()
                
                #  Create output folder if it doesn't exist
                os.makedirs(output_folder, exist_ok=True)

                # Open the video file
                # cap = cv2.VideoCapture(video_path)
                # print(f"Not Skipping {video_name}")
                # Initialize frame count
                frame_count = 0
                extrated_frames = 1

                # Read until video is completed
                while(cap.isOpened()):
                    # Capture frame-by-frame
                    ret, frame = cap.read()

                    if ret:
                        # Resize frame to 256x256 pixels
                        frame = cv2.resize(frame, (256, 256))

                        # Save frame as PNG file
                        if frame_count % 2 == 0:
                            frame_path = os.path.join(output_folder, f"{extrated_frames:05d}.png")
                            os.makedirs(os.path.dirname(frame_path), exist_ok=True)
                            cv2.imwrite(frame_path, frame)
                            extrated_frames += 1
                            
                        frame_count += 1
                        
                    else:
                        break

                # Release the video capture object
                cap.release()

                print(f"Frames extracted for {video_name}: {extrated_frames} at {fps} fps")
            else:
                print(f"Skipping {video_name} as it exceeds 15 words")
        print("Frames extracted successfully")
    except Exception as e:
        print(e)
        print("Provide the input_folder, output_frames_folder, csv_file_path")
        

  
#Dont run these together
convert_videos_to_frames__using_openCV(input_folder, output_frames_folder, csv_file_path)
# convert_videos_to_frames_using_moviepy(input_folder, output_frames_folder, csv_file_path)


csv_output_generator(csv_file_path, output_csv_file)

