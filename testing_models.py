import glob


import tensorflow as tf
import os
# import matplotlib.pyplot as plt
#
# from skimage import measure
# from skimage.io import imread, imsave, imshow
# from skimage.transform import resize
# from skimage.filters import gaussian
# from skimage.morphology import dilation, disk
# from skimage.draw import polygon, polygon_perimeter

CLASSES = 15
SAMPLE_SIZE = (256, 256)

OUTPUT_SIZE = (1080, 1920) #Вывод текста

rgb_colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 165, 0),
    (255, 192, 203),
    (0, 255, 255),
    (255, 0, 255)
]

#//////////////
def load_images(image, text):
    image = tf.io.read_file(image)
    image = tf.io.decode_jpeg(image)
    image = tf.image.resize(image, OUTPUT_SIZE)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = image / 255.0

    text = tf.io.read_file(text)

    return image, text


def augmentate_images(image, text):
    random_crop = tf.random.uniform((), 0.3, 1)
    image = tf.image.central_crop(image, random_crop)

    random_flip = tf.random.uniform((), 0, 1)
    if random_flip >= 0.5:
        image = tf.image.flip_left_right(image)

    image = tf.image.resize(image, SAMPLE_SIZE)
    text = text

    return image, text
#///////////
images = sorted(glob.glob('detector_photo/Flickr8k_text/Images/*.jpg'))
text = glob.glob('detector_photo/Flickr8k_text/captions.txt')

images_dataset = tf.data.Dataset.from_tensor_slices(images)
text_dataset = tf.data.Dataset.from_tensor_slices(text)

dataset = tf.data.Dataset.zip((images_dataset, text_dataset))

dataset = dataset.map(load_images, num_parallel_calls=tf.data.AUTOTUNE)
dataset = dataset.map(augmentate_images, num_parallel_calls=tf.data.AUTOTUNE)

# //////////////////////////
images_and_text = list(dataset.take(5))
print(images_and_text)
# fig, ax = plt.subplots(nrows=2, ncols=5, figsize=(15, 5), dpi=125)
#
# for i, (image, text) in enumerate(images_and_text):
#     ax[0, i].set_title('Image')
#     ax[0, i].set_axis_off()
#     ax[0, i].imshow(image)
#
#     ax[1, i].set_title('Text')
#     ax[1, i].set_axis_off()
#     ax[0, i].imshow(text)
#
#     for channel in range(CLASSES):
#         contours = measure.find_contours(np.array(text[:, :, channel]))
#         for contour in contours:
#             ax[1, i].plot(contour[:, 1], contour[:, 0], linewidth=1)

# plt.show()
# plt.close()

#%% //////////////
def input_layer():
    return tf.keras.layers.Input(shape=SAMPLE_SIZE + (3,))


def downsample_block(filters, size, batch_norm=True):
    initializer = tf.keras.initializers.GlorotNormal()

    result = tf.keras.Sequential()

    result.add(
        tf.keras.layers.Conv2D(filters, size, strides=2, padding='same',
                               kernel_initializer=initializer, use_bias=False))

    if batch_norm:
        result.add(tf.keras.layers.BatchNormalization())

    result.add(tf.keras.layers.LeakyReLU())
    return result


def upsample_block(filters, size, dropout=False):
    initializer = tf.keras.initializers.GlorotNormal()

    result = tf.keras.Sequential()

    result.add(
        tf.keras.layers.Conv2DTranspose(filters, size, strides=2, padding='same',
                                        kernel_initializer=initializer, use_bias=False))

    result.add(tf.keras.layers.BatchNormalization())

    if dropout:
        result.add(tf.keras.layers.Dropout(0.25))

    result.add(tf.keras.layers.ReLU())
    return result


def output_layer(size):
    initializer = tf.keras.initializers.GlorotNormal()
    return tf.keras.layers.Conv2DTranspose(CLASSES, size, strides=2, padding='same',
                                           kernel_initializer=initializer, activation='sigmoid')
# ////////
inp_layer = input_layer()

downsample_stack = [
    downsample_block(64, 4, batch_norm=False),
    downsample_block(128, 4),
    downsample_block(256, 4),
    downsample_block(512, 4),
    downsample_block(512, 4),
    downsample_block(512, 4),
    downsample_block(512, 4),
]

upsample_stack = [
    upsample_block(512, 4, dropout=True),
    upsample_block(512, 4, dropout=True),
    upsample_block(512, 4, dropout=True),
    upsample_block(256, 4),
    upsample_block(128, 4),
    upsample_block(64, 4)
]

out_layer = output_layer(4)

# Реализуем skip connections
x = inp_layer

downsample_skips = []

for block in downsample_stack:
    x = block(x)
    downsample_skips.append(x)

downsample_skips = reversed(downsample_skips[:-1])

for up_block, down_block in zip(upsample_stack, downsample_skips):
    x = up_block(x)
    x = tf.keras.layers.Concatenate()([x, down_block])

out_layer = out_layer(x)

unet_like = tf.keras.Model(inputs=inp_layer, outputs=out_layer)

tf.keras.utils.plot_model(unet_like, show_shapes=True, dpi=72)



unet_like.load_weights('SemanticSegmentationLesson/networks/unet_like')
# frames = sorted(glob.glob('SemanticSegmentationLesson/videos/original_video/*.jpg'))
frames = glob.glob('detector_photo/Flickr8k_text/Images/667626_18933d713e.jpg')

for filename in frames:
    frame = imread(filename)
    sample = resize(frame, SAMPLE_SIZE)

    predict = unet_like.predict(sample.reshape((1,) + SAMPLE_SIZE + (3,)))
    predict = predict.reshape(SAMPLE_SIZE + (CLASSES,))

    scale = frame.shape[0] / SAMPLE_SIZE[0], frame.shape[1] / SAMPLE_SIZE[1]

    frame = (frame / 1.5).astype(np.uint8)

    for channel in range(1, CLASSES):
        contour_overlay = np.zeros((frame.shape[0], frame.shape[1]))
        contours = measure.find_contours(np.array(predict[:, :, channel]))

        try:
            for contour in contours:
                rr, cc = polygon_perimeter(contour[:, 0] * scale[0],
                                           contour[:, 1] * scale[1],
                                           shape=contour_overlay.shape)

                contour_overlay[rr, cc] = 1

            contour_overlay = dilation(contour_overlay, disk(1))
            frame[contour_overlay == 1] = rgb_colors[channel]
        except:
            pass

    imsave(f'SemanticSegmentationLesson/videos/processed/{os.path.basename(filename)}', frame)