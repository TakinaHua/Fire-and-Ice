from PIL import Image
import os

# === Load your image ===
image_path = "/Users/huashan/Desktop/ALL/15112/Team project/Browser Games - Fireboy and Watergirl The Forest Temple - Watergirl Partially Assembled copy.png"
image = Image.open(image_path)

# === Output folder for cropped faces ===
output_dir = "cropped_faces"
os.makedirs(output_dir, exist_ok=True)

# === Setup ===
num_faces = 11  # Number of faces in the image
full_height = image.size
face_width = 205
face_height = 473  

# === Crop and save each face ===
for i in range(num_faces):
    # Crop just inside the green lines: adjust as needed
    left = i * face_width + (i+1)*3   
    right =  (i + 1) * face_width + (i+1)*3  
    top = 162
    bottom = 641

    cropped_face = image.crop((left, top, right, bottom))
    cropped_face.save(os.path.join(output_dir, f"watergirl_face_{i+1}.png"))

print("✅ Cropping complete! Check the 'cropped_faces' folder.")
