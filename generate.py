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

def text_to_image(text):
    # Choose a font and size
    font = ImageFont.truetype("FreeMono.ttf", size=12)

    # Split the text into lines and measure each line
    lines = text.split('\n')
    line_widths = [font.getsize(line)[0] for line in lines]
    line_heights = [font.getsize(line)[1] for line in lines]

    # Calculate the total width and height for the image
    img_width = max(line_widths) + 20  # Adding some padding
    img_height = sum(line_heights) + (len(lines) * 5) + 15  # Adding space between lines and some padding

    # Create a blank white image
    img = Image.new('RGB', (img_width, img_height), color='white')
    d = ImageDraw.Draw(img)

    # Insert each line onto the image
    y_text = 5
    for line in lines:
        d.text((10, y_text), line, fill='black', font=font)
        y_text += font.getsize(line)[1] + 5  # Move to the next line position

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

