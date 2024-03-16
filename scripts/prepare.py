
import os
import csv
import shutil
import glob

DATA_PATH = "/root/dsti/deep learning/try/20bn-jester-v1"
DESTINATION_PATH = "/root/dsti/deep learning/dir_to_upload"
CLASS_NAMES = ["Doing other things", "Thumb Down", "Thumb Up", "Stop Sign", "Swiping Left"]
LABEL_FILE_DIR = "/root/dsti/deep learning/try/20bn-jester-download-package-labels/labels"

LABEL_TYPE_NAMES = ["train", "validation", "test-answers"]

for label in LABEL_TYPE_NAMES:
    csv_file_name = os.path.join(LABEL_FILE_DIR, label + ".csv")
    with open(csv_file_name, newline='') as csvfile:
        label_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in label_reader:
            index_dataset = row[0]
            class_name = row[1]
            # print(index_dataset, class_name)
            if CLASS_NAMES.count(class_name) > 0:
                dest_path = os.path.join(DESTINATION_PATH, label, class_name, index_dataset)
                source_path = os.path.join(DATA_PATH, index_dataset)
                os.makedirs(dest_path, exist_ok=True)
                print("Copying {} to {}" .format(source_path, dest_path))
                files_list = glob.glob(os.path.join(source_path, "*"))
                for f in files_list:
                    shutil.copy(f, dest_path)