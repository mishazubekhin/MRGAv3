import tensorflow as tf
import numpy as np


model = tf.keras.models.load_model('D:\PythonPROJECTS\MRGAv3\detector_photo\Flickr8k_text\Models\my_model.h5')


input_image = tf.keras.utils.load_img(
    "D:\\PythonPROJECTS\\MRGAv3\\detector_photo\\Flickr8k_text\\any_photo\good\\13S1t.jpg")

def resize_images(img, label):
    img = tf.cast(img, tf.float32)
    img = tf.image.resize(img, (224,224))
    img = img / 255.0
    return img, label


class_names =['bad', 'good']


img_resized = tf.image.resize(input_image, [224, 224])
img_expended = np.expand_dims(img_resized, axis=0)
prediction = model.predict(img_expended)
print(prediction)
print(f'Вероятность отнесения изображения к хорошему: {prediction[0][0]*10000}')
if 0.5 <= prediction[0][0]*100 <= 1:
    print("good")
else:
    print('bad')

# for i, logits in enumerate(prediction):
#   class_idx = tf.argmax(logits).numpy()
#   p = tf.nn.softmax(logits)[class_idx]
#   name = class_names[class_idx]
#   print("Example {} prediction: {} ({:2.1f}%)".format(i, name, 100*p))
