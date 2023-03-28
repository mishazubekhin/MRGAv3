import tensorflow as tf
from keras import layers
from keras.preprocessing.image import ImageDataGenerator

img_height = 224
img_width = 224

base_layers = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False)
base_layers.trainable = False

datagen = ImageDataGenerator(
    rescale=1./255,
    zoom_range=(0.9, 0.99),
    brightness_range=(0.8, 0.99),
    horizontal_flip=True,
    vertical_flip=True,
    data_format='channels_last',
    validation_split=0.01)

train_generator = datagen.flow_from_directory(
    'D:\\PythonPROJECTS\\Photo_for_datascience\\any_photo',
    target_size=(img_height, img_width),
    color_mode='rgb',
    class_mode='binary',
    subset='training',
    seed=123,
    keep_aspect_ratio=True
)

model = tf.keras.Sequential([
    layers.Input((224, 224, 3)),
    base_layers,
    # layers.Conv2D(224, 3, activation='relu', padding='same'),
    # layers.Conv2D(224, 3, activation='relu', padding='same'),
    # layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(112, activation=tf.nn.relu),
    layers.Dense(64, activation=tf.nn.relu),
    layers.Dense(32, activation=tf.nn.relu),
    layers.Dense(32, activation='relu'),
    layers.Dense(32, activation='relu'),
    layers.Dense(1, activation='sigmoid')])


model.compile(
    optimizer='adam',
    loss=tf.keras.losses.binary_crossentropy,
    metrics='accuracy')

model.fit(train_generator, epochs=3)

tf.keras.models.save_model(model, "D:\\PythonPROJECTS\\MRGAv3\\detector_photo\\Flickr8k_text\\Models\\my_model.h5")
