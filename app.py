import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from flask import Flask, jsonify
import re

app = Flask(__name__)

# process input news
def clean_input(text):
    #remove html
    html = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
    text = re.sub(html, "", text)

    #remove_non_ascii characters
    text = re.sub(r'[^\x00-\x7f]',r'', text)

    # remove_special_characters
    emoji_pattern = re.compile(
        '['
        u'\U0001F600-\U0001F64F'  # emoticons
        u'\U0001F300-\U0001F5FF'  # symbols & pictographs
        u'\U0001F680-\U0001F6FF'  # transport & map symbols
        u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
        u'\U00002702-\U000027B0'
        u'\U000024C2-\U0001F251'
        ']+',
        flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    # remove_punct
    text = re.sub(r'[]!"$%&\'()*+,./:;=#@?[\\^_`{|}~-]+', "", text)
    
    # lowercase text
    text = text.lower()

    return text

# prediction route
@app.route("/predict", methods=["POST"])
def predict(input_news):
    # clean the input_news
    text = clean_input(input_news)
    # tokenize the news
    text_sequences = tokenizer.texts_to_sequences(text)
    text_padded = pad_sequences(text_sequences, maxlen=1313, padding='post', truncating='post')
    # prediction
    tresh = 0.55
    proba = model.predict(text_padded)
    class_id = int((proba > tresh).astype(int)[0][0])
    prob_hoax = float(proba[0][0])
    prob_valid = 1 - prob_hoax

    return jsonify({'teks berita': text,
                    'prediksi kelas': class_id,
                    'probabilitas hoax': prob_hoax,
                    'probabilitas valid': prob_valid})


if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 12345 # If you don't provide any port the port will be set to 12345
    
    # load the model and tokenizer
    model = tf.keras.models.load_model('model.h5')
    print('Model loaded')
    tokenizer = pickle.load(open('tokenizer.pickle', 'rb'))
    print('Tokenizer loaded')

    app.run(debug=True, port=port)