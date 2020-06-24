import argparse
import io
from xml.etree import ElementTree
from zipfile import ZipFile


def set_default_arrangements(path_to_playlist: str):
    files = {}

    with ZipFile(path_to_playlist, 'r') as zip_file:
        for filename in zip_file.filelist:
            file_data = zip_file.read(filename)
            if filename.filename == 'data.pro6pl':
                data = file_data
            else:
                files[filename.filename] = file_data
        data_xml = ElementTree.fromstring(data)
        documents = data_xml.findall('.//RVDocumentCue')

        for document in documents:
            song_path = document.get('filePath')
            try:
                song_buffer = zip_file.read(song_path)
                song_xml = ElementTree.fromstring(song_buffer)
                song_arrangement_id = song_xml.get('selectedArrangementID')
                document.set('selectedArrangementID', song_arrangement_id)
            except KeyError:
                print("Song %s is not included in file." % song_path)

    with ZipFile(path_to_playlist, 'w') as zip_file:
        file_buffer = io.BytesIO()
        ElementTree.ElementTree(data_xml).write(file_buffer, encoding='UTF-8', xml_declaration=True)
        zip_file.writestr('data.pro6pl', file_buffer.getvalue())
        for filename, file_data in files.items():
            zip_file.writestr(filename, file_data)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('path_to_playlist')
    args = arg_parser.parse_args()

    set_default_arrangements(args.path_to_playlist)