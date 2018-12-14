print("prediction program is initializing...")
# Initialize pretrained Inception V3 model
import torchvision.models as models
from redis import StrictRedis
import json
import base64
from PIL import Image
import requests

model = models.inception_v3(pretrained=True)
model.transform_input = True

# Define the preprocessing function
from torch.autograd import Variable
import torchvision.transforms as transforms

normalize = transforms.Normalize(
   mean=[0.485, 0.456, 0.406],
   std=[0.229, 0.224, 0.225]
)
preprocess = transforms.Compose([
   transforms.Resize(256),
   transforms.CenterCrop(299),
   transforms.ToTensor(),
   normalize
])

content = requests.get("https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json").text
labels = json.loads(content)

data = {}
data["predictions"] = []


r = StrictRedis(host='localhost', port=6379)
print("prediction program is listening")
while True:
    image = json.loads(r.blpop('image')[1].decode("utf-8"))
    print("chat_id = "+str(image["chat_id"]))
    print("img in base64 = "+image["img"])
    image_base64_string = image["img"]
    image_data = base64.b64decode(image_base64_string)
    with open('image.jpg', 'wb') as outfile:
        outfile.write(image_data)
    im = Image.open('image.jpg')
    img_tensor = preprocess(im)
    img_tensor.unsqueeze_(0)
    img_variable = Variable(img_tensor)

    model.eval()
    preds = model(img_variable)

    # Convert the prediction into text labels
    # Get the top 3 predictions
    predictions = []
    for i, score in enumerate(preds[0].data.numpy()):
        predictions.append((score, labels[str(i)][1]))
       
    predictions.sort(reverse=True)
    for score, label in predictions[:5]:
        data["predictions"].append({"label":label, "score":float(score)})
    data["chat_id"] = image["chat_id"]
    message = json.dumps(data, indent=2)
    print(message)
    r.rpush('prediction', message.encode("utf-8"))


