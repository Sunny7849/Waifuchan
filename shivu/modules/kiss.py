import requests
from PIL import Image, ImageTk
import tkinter as tk
import random
from io import BytesIO

# GIF URLs list (All Added)
gif_urls = [
    "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
    "https://media.giphy.com/media/flmwfIpFVrSKI/giphy.gif",
    "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
    "https://media.giphy.com/media/zkppEMFvRX5FC/giphy.gif",
    "https://media.giphy.com/media/gTLfgIRwAiWOc/giphy.gif",
    "https://media.giphy.com/media/wOtkVwroA6yzK/giphy.gif"
]

# Function to download and show a random GIF
def show_gif():
    gif_url = random.choice(gif_urls)  # Select a random GIF
    response = requests.get(gif_url)  # Download GIF
    img_data = BytesIO(response.content)  # Convert to bytes
    img = Image.open(img_data)  # Open image
    img = img.resize((300, 300))  # Resize if needed

    gif_image = ImageTk.PhotoImage(img)  # Convert for Tkinter
    img_label.config(image=gif_image)
    img_label.image = gif_image

# Create Tkinter Window
root = tk.Tk()
root.title("Random Kiss GIF")
root.geometry("400x400")

# Button to load GIF
button = tk.Button(root, text="Kiss GIF Dekho", command=show_gif)
button.pack(pady=20)

# Label to show GIF
img_label = tk.Label(root)
img_label.pack()

# Run Tkinter loop
root.mainloop()
