from flask import Flask, render_template, Response, send_file, request, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import io
import random
import string
#... [Your functions here] ...

def load_words_from_file(filename):
    """Load words from a file and return them as a list."""
    with open(filename, 'r') as f:
        return [word.strip() for word in f.read().split(',')]

def create_string_of_words(words, target_length=35):
    filtered_words = [word for word in words if not (any(char.isdigit() for char in word) or '.' in word)]
    random.shuffle(filtered_words)
    
    line = ""
    for word in filtered_words:
        if len(line) + len(word) + 1 <= target_length:
            line += (word.upper() + " ")
            if len(line) >= target_length:
                break
    return line.strip()

def text_to_image(text, width=1050, height=600):
    # Choose a font and size
    font_size = 18
    font_path = "FreeMono.ttf"  # Update the path to your font file
    font = ImageFont.truetype(font_path, size=font_size)

    # Create a blank white image with the specified width and height
    img = Image.new('RGB', (width, height), color='white')
    d = ImageDraw.Draw(img)

    # Split the text into lines and measure each line
    lines = text.split('\n')
    line_height = font.getsize('H')[1]  # Get the height of a typical character ('H')

    # Calculate the vertical position for centering the text
    total_text_height = len(lines) * line_height
    y_text = (height - total_text_height) // 2

    # Insert each line onto the image
    for line in lines:
        text_width, text_height = d.textsize(line, font=font)
        x_text = (width - text_width) // 2  # Calculate the horizontal position for centering
        d.text((x_text, y_text), line, fill='black', font=font)
        y_text += line_height  # Move to the next line position

    # Save the image to a bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        seed_value = request.form.get('seed')
        
        # Check if the seed is provided and is a valid number. 
        # If not, generate a random seed.
        try:
            seed_value = int(seed_value)
        except (ValueError, TypeError):
            seed_value = random.randint(0, 1e6)
        
        # After processing and generating text block, 
        # redirect back to the GET route with seed_value as a parameter.
        return redirect(url_for('generate', seed=seed_value))
    
    else:  # Handle GET requests
        seed_value = request.args.get('seed', default=random.randint(0, 1e6), type=int)
        random.seed(seed_value)

        words = load_words_from_file('output.txt')
        lines = []

        for i in range(10):
            line = create_string_of_words(words)
            while not (34 <= len(line) <= 35):
                line = create_string_of_words(words)
            lines.append(f"{i} {line}")

        seed_line = f"{seed_value}"
        lines.append(seed_line)

        text_block = '\n'.join(lines)
        return render_template('index.html', text_block=text_block, seed=seed_value)

@app.route('/download')
def download():
    seed_value = request.args.get('seed', default=random.randint(0, 1e6), type=int)
    random.seed(seed_value)

    words = load_words_from_file('output.txt')
    lines = []

    for i in range(10):
        line = create_string_of_words(words)
        while not (34 <= len(line) <= 35):
            line = create_string_of_words(words)
        lines.append(f"{i} {line}")

    seed_line = f"{seed_value}"
    lines.append(seed_line)
    
    # Convert the text to an image
    text_content = '\n'.join(lines)
    img_buffer = text_to_image(text_content)
    
    # Return the image as a download
    return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name='text_block.png')

if __name__ == '__main__':
    app.run(debug=True)

