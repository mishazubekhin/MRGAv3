import tensorflow as tf
from keras import layers
from keras.preprocessing.image import ImageDataGenerator

img_height = 224
img_width = 224
batch_size = 10

base_layers = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False)
base_layers.trainable = False

model = tf.keras.Sequential([base_layers,
    layers.Input((224, 224, 3)),
    layers.Conv2D(32, 3, activation='relu', padding='same'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, activation='relu', padding='same'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(20, activation=tf.nn.relu),  # input shape required
    layers.Dense(20, activation=tf.nn.relu),
    layers.Dense(20, activation=tf.nn.relu),
    layers.Dense(20, activation=tf.nn.relu),
    layers.Dense(1, activation='sigmoid')])

datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=10,
    zoom_range=(0.90, 0.99),
    brightness_range=(0.9, 1.0),
    horizontal_flip=True,
    vertical_flip=True,
    data_format='channels_last',
    validation_split=0.01
)

train_generator = datagen.flow_from_directory(
    'D:\PythonPROJECTS\MRGAv3\detector_photo\Flickr8k_text\\any_photo',
    target_size=(img_height, img_width),
    color_mode='rgb',
    class_mode='sparse',
    shuffle=True,
    subset='training',
    seed=123,
    keep_aspect_ratio=True
)


# ds_train = tf.keras.preprocessing.image_dataset_from_directory(
#     'detector_photo/Flickr8k_text/any_photo',
# class_names=['bad', 'good'],
# seed=123,
# subset='training')
#
# ds_validation = tf.keras.preprocessing.image_dataset_from_directory(
#     'detector_photo/Flickr8k_text/any_photo',
# class_names=['bad', 'good'],
# seed=123,
# subset='validation')

# def training(): pass
#
# for epoch in range(10):
#     num_batches = 0
#
#         for x, y in ds_train:
#             num_batches += 1
#
#             training()
#
#             if num_batches == 25:
#                 break

model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

model.fit(train_generator,
          epochs=7)
# [tf.keras.losses.SparseCategoricalCrossentropy()]

tf.keras.models.save_model(model, "D:\PythonPROJECTS\MRGAv3\detector_photo\Flickr8k_text\Models\\my_model.h5",
                           )
