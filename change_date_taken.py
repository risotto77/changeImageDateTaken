import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import argparse
import re

def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()

def get_labeled_exif(exif):
    if exif is not None:
        labeled = {}
        for (key, val) in exif.items():
            if key in TAGS:
                labeled[TAGS[key]] = val
        return labeled
    else:
        return {}

def get_datetime_from_filename(filename):
    try:
        # Try to parse the date from the file name in the format YYYYMMDD or YYYY-MM-DD
        date_time_str = re.search(r'\d{8}|\d{4}-\d{2}-\d{2}', os.path.splitext(os.path.basename(filename))[0])
        if date_time_str:
            date_time_str = date_time_str.group()
            date_time_str = date_time_str.replace('-', '')
            return datetime.strptime(date_time_str, '%Y%m%d')
    except:
        return None

def set_exif_date_time(filename, date_time, dry_run=False):
    try:
        image = Image.open(filename)
        image_exif = image.getexif()
        if image_exif is not None:
            original_date_time = image_exif.get(36867, None)
            if original_date_time and original_date_time.decode() != date_time.strftime('%Y:%m:%d %H:%M:%S'):
                if not dry_run:
                    image_exif[36867] = date_time.strftime('%Y:%m:%d %H:%M:%S').encode()
                    image.save(filename, exif=image_exif)
                print(f"Updated date time for {filename} from {original_date_time.decode()} to {date_time.strftime('%Y:%m:%d %H:%M:%S')}")
            elif original_date_time is None:
                if not dry_run:
                    image_exif[36867] = date_time.strftime('%Y:%m:%d %H:%M:%S').encode()
                    image.save(filename, exif=image_exif)
                print(f"Set date time for {filename} to {date_time.strftime('%Y:%m:%d %H:%M:%S')}")
    except:
        print(f"Error setting date time for {filename}")

def update_exif_date_time(file_path, dry_run=False):
    date_time_from_filename = get_datetime_from_filename(file_path)
    if date_time_from_filename:
        set_exif_date_time(file_path, date_time_from_filename, dry_run)
    else:
        # If the date can't be extracted from the file name, use the current date
        set_exif_date_time(file_path, datetime.now(), dry_run)

def main():
    parser = argparse.ArgumentParser(description='Update EXIF date time for image files')
    parser.add_argument('--directory', default='.', help='Path to the directory containing the image files (default is current directory)')
    parser.add_argument('--recursive', action='store_true', help='Apply the update recursively')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Dry run, don\'t actually update the files (default is true)')
    args = parser.parse_args()

    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png"):
                file_path = os.path.join(root, file)
                update_exif_date_time(file_path, args.dry_run)
        if not args.recursive:
            break

if __name__ == "__main__":
    main()