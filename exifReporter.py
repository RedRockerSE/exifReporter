import sys
import os
from tqdm import tqdm
from scripts.exif import ExifTool
import json
import argparse
from PIL import Image
import datetime
import shutil
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

def get_config(key=None):
    with open('config.json') as f:
        config = json.load(f)
    if key:
        return config[key]

def get_datestamp(format):
    now = datetime.datetime.now()
    return now.strftime(format)

def enumerate_files(folder):
    file_list = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_report(file_list_data, report_folder):
    env = Environment(loader=FileSystemLoader('layout'))
    template = env.get_template(get_config("report_template"))
    data = {
        'title': 'exifReporter',
        'report_name': get_config("report_name"),
        'report_description': get_config("report_description"),
        'file_list_data': file_list_data
    }
    html = template.render(data)
    with open(f'output\\{report_folder}\\index.html', 'w') as f:
        f.write(html)

def create_thumbnail(file, report_folder):
    size = 240, 240
    filename = os.path.splitext(os.path.basename(file))[0]
    try:
        im = Image.open(file)
        im.thumbnail(size)
        match im.format:
            case 'JPEG':
                thumbnail = f'output\\{report_folder}\\thumbnails\\{filename}_exifReporter_thumb.jpg'
                im.save(thumbnail, 'JPEG')
                return thumbnail
            case 'PNG':
                thumbnail = f'output\\{report_folder}\\thumbnails\\{filename}_exifReporter_thumb.png'
                im.save(thumbnail, 'PNG')
                return thumbnail
            case 'GIF':
                thumbnail = f'output\\{report_folder}\\thumbnails\\{filename}_exifReporter_thumb.gif'
                im.save(thumbnail, 'GIF')
                return thumbnail
    except IOError as e:
        print("Error creating thumbnail:", e)
        print("Cannot create thumbnail for", file)
        
def copy_file_preserve_metadata(src, dest):
    shutil.copy2(src, dest)


def main(folder):
    format = "%Y-%m-%d_%H%M%S"
    datestmp = get_datestamp(format)
    create_folder(f'output\\{datestmp}\\thumbnails')
    create_folder(f'output\\{datestmp}\\fullsize')
    
    file_list = enumerate_files(folder)
    print(f"[i] hittade {len(file_list)} filer att analysera")
    with ExifTool(get_config("exiftool_executable")) as e:
        file_list_data = defaultdict(list)
        for file in tqdm(file_list):
            metadata = e.get_metadata(file)
            copy_file_preserve_metadata(file, f'output\\{datestmp}\\fullsize\\{os.path.basename(file)}')
            thumbnail = create_thumbnail(file, datestmp)
            thumb_filename = os.path.basename(thumbnail)
            file_list_data[thumb_filename].append(metadata[0])
    print(f"[i] skapar rapport")
    create_report(file_list_data, datestmp)


if __name__ == '__main__':
    os.system('cls')
    parser = argparse.ArgumentParser(description='Exif Reporter')
    parser.add_argument('-f', '--folder', type=str, help='Folder path to scan for files')
    args = parser.parse_args()
    
    if args.folder:
        folder = args.folder
    else:
        folder = 'c:\\temp\\exif'
    
    main(folder)
    