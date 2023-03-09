import os
from PIL import Image
from pillow_heif import register_heif_opener


# Укажите путь к папке, содержащей файлы HEIC
heic_folder = "D:\ФОТО\Питер2020камера"

# Укажите путь к папке, в которую сохранять файлы JPEG
jpeg_folder = 'D:\PythonPROJECTS\MRGAv3\detector_photo\Flickr8k_text\\any_photo\good'



def heic_to_jpg():
     register_heif_opener()
     for root, dirs, files in os.walk(heic_folder):
         for file in files:
             if file.endswith('.HEIC'):
                print(root)
                print(file)
                image = Image.open(os.path.join(root, file))
                image.save(os.path.join(root, file.replace('.HEIC', '.JPG')))

                os.remove(os.path.join(root, file)) # Удаляет файл .HEIC


# def del_files():
#     for root, dirs, files in os.walk(source_dir):
#         for file in files:
#  if file.endswith('.AAE'):
#                 print(file)
#  os.remove(os.path.join(root, file))


if __name__ == '__main__':
    heic_to_jpg()
    # del_files()'JPEG')