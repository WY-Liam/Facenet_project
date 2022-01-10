from flask import Flask, render_template, request;
from datetime import timedelta
from PIL import Image
import h5py
import torch
import numpy.linalg as LA
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1

mtcnn = MTCNN(image_size=224)
model = InceptionResnetV1(pretrained='vggface2').eval()

app = Flask(__name__)

app.send_file_max_age_default = timedelta(seconds=1)

file_name = "./static/data/features_data.h5"
h5f = h5py.File(file_name, "r")
feats = h5f["features"][:]

file_label = "./static/data/label.txt"
temp = open(file_label, 'r').read().splitlines()

@app.route("/")
def home():
    return render_template('demo.html')    

@app.route('/upload', methods=['POST', 'GET']) 
def upload():
    if request.method == 'POST':
        img = request.files['file']
        file_path = "./static/"
        img.save(file_path + img.filename)
        data = Image.open(file_path + img.filename)
        img_cropped = mtcnn(data, save_path = file_path + "result.jpg")
        embed4 = model(img_cropped.unsqueeze(0))
        data1 = torch.flatten(embed4).detach().numpy()
        rs = data1/(LA.norm(data1))
        output = np.dot(rs.T, feats)
        labels = temp[np.argmax(output)][:-5]
        return render_template('index.html', file_name = img.filename, idx = labels, file_name_1 = "result.jpg")
    return render_template('upload.html')
 
if __name__ == '__main__':
    app.run()