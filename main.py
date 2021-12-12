# This is a sample Python script.
import shutil
import sys
import HManga as hm
import zipfile
import os

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
base = "F:\\Fakku\\Extra"
foldername = 'FScraper'


def prepare_zip(dir_path):
    new_file = dir_path + '.zip'
    zip = zipfile.ZipFile(new_file, 'w', zipfile.ZIP_DEFLATED)

    for dir_path, dir_names, files in os.walk(dir_path):
        f_path = dir_path.replace(dir_path, '')
        f_path = f_path and f_path + os.sep

        for file in files:
            zip.write(os.path.join(dir_path, file), f_path + file)

        zip.close()
        print('file successfully created...')
        return new_file


def extract_zip(dir_path):
    with zipfile.ZipFile(dir_path, 'r') as zip_inst:
        zip_inst.extractall()


def stream_contents(src_zip, dst_zip, file_list=[], xml_file=''):
    with zipfile.ZipFile(src_zip, 'r', compression=zipfile.ZIP_DEFLATED) as src_zip_archive:
        with zipfile.ZipFile(dst_zip, 'w', compression=zipfile.ZIP_DEFLATED) as dst_zip_archive:
            for zitem in src_zip_archive.namelist():
                if zitem in file_list or len(file_list) == 0:
                    if sys.version_info >= (3, 6):
                        with src_zip_archive.open(zitem) as from_item:
                            with dst_zip_archive.open(zitem, 'w') as to_item:
                                shutil.copyfileobj(from_item, to_item)
                    else:
                        dst_zip_archive.writestr(zitem, src_zip_archive.read(zitem))

            if 'comicinfo.xml' not in dst_zip_archive.namelist():
                with dst_zip_archive.open('ComicInfo.xml', 'w') as f:
                    xml_file.write(f, encoding='UTF-8', xml_declaration=True)


def walk_recursively(path):
    '''
    recurse, which folder to recursively check
    save_to which folder to save all of the files to

    :param recurse:
    :param save_to:
    :return:
    '''
    files = []
    file_paths = []
    directories = []

    try:
        shutil.rmtree(base + "\\" + foldername)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    #    return

    for directory, folders, filenames in os.walk(base):
        count = 1
        if os.path.basename(base) in directory:
            if not os.path.exists(directory.replace(base, base + "\\" + foldername)):
                os.makedirs(directory.replace(base, base + "\\" + foldername))
            for file in filenames:
                if '.zip' in file:
                    if file not in files:
                        manga = hm.HManga(file)

                        files.append(file)
                        new_location = directory.replace(base, base + "\\" + foldername) + "\\" + file
                        old_location = directory + "\\" + file
                        stream_contents(old_location, new_location, xml_file=manga.get_xml())
                        print(count.__str__() + "/" + len(
                            filenames).__str__() + " Creating " + file + " from " + directory + "...")
                        count += 1
                    if directory not in directories:
                        directories.append(directory)
                    file_paths.append(os.path.join(directory, file))


def walk():
    for dirpath, dirs, files in os.walk("./TREE/"):
        for filename in files:
            fname = os.path.join(dirpath, filename)
            with open(fname) as myfile:
                print(myfile.read())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    walk_recursively(base)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
