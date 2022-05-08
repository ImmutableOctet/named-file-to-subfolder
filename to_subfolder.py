import sys
import os
import os.path
import errno
import shutil

import argparse
import re

def ensure_path(path):
	if not os.path.exists(os.path.dirname(path)):
		try:
			os.makedirs(os.path.dirname(path))
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise

def process_files(cfg, regexp, input_path, file_names, output_path):
    for f in file_names:
        process_file(cfg, regexp, input_path, f, output_path)

def process_file(cfg, regexp, input_path, file_name, output_path):
    details = regexp.match(file_name)

    if (not details):
        return False

    dest_subfolder = details.group(cfg.rcap_folder)

    if (cfg.keep_original_filename):
        dest_file_name = file_name
    else:
        dest_file_name = details.group(cfg.rcap_file)

    if (cfg.separate_extensions):
        dest_file_ext = details.group(cfg.rcap_ext)
    else:
        dest_file_ext = None

    full_file_path_out = os.path.join(output_path, dest_subfolder)

    if (dest_file_ext):
        full_file_path_out = os.path.join(full_file_path_out, dest_file_ext)

        dest_file_name = f'{dest_file_name}.{dest_file_ext}'

    full_file_path_out = os.path.join(full_file_path_out, dest_file_name)
    
    full_file_path_in = os.path.join(input_path, file_name)

    print(f'Moving file from\n"{full_file_path_in}"\nto:\n"{full_file_path_out}"')

    if (cfg.ensure_output_path):
        ensure_path(full_file_path_out)
    
    if (cfg.mode == 'copy'):
        shutil.copyfile(full_file_path_in, full_file_path_out)
    elif (cfg.mode == 'move'):
        shutil.move(full_file_path_in, full_file_path_out)
    else:
        assert(False, f"Invalid transfer mode detected: {cfg.mode}")

    print('File moved.\n')

    return True

def to_subfolder(cfg):
    print(f'Moving files from "{cfg.input_path}" to "{cfg.output_path}" with: \'{cfg.regular_expression}\'')

    regexp = re.compile(cfg.regular_expression)

    for (path, dir_names, file_names) in os.walk(cfg.input_path):
        process_files(cfg, regexp, path, file_names, cfg.output_path)

def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='Migrate \'named\' files from one location to a subdirectory of another path.\n\n'
                                                                                    'e.g. a file named "A - B.txt" could be moved from folder "C" to folder "D/A" as "B.txt" --\n'
                                                                                    'so your final path would be something like: "D/A/B.txt"\n')

    parser.add_argument('-r', "--regex", dest='regular_expression', default=r'(.*?)\s-\s(.+)\.(.+)',
                            help='The regular expression used to identify a subfolder name\n'
                                'By default, this is configured to look for files similar to "Subfolder Name - File Name.FILEEXTENSION".\n'
                                'To change which capture maps to what element, use:\n'
                                '--folder-capture\tNUMBER\n'
                                '--file-capture\tNUMBER\n'
                                '--ext-capture\tNUMBER\n')

    parser.add_argument('-i', "--input", dest='input_path', required=True)
    parser.add_argument('-o', "--output", dest='output_path', required=True)

    parser.add_argument('-folderc', "--folder-capture", dest='rcap_folder', default=1, type=int)
    parser.add_argument('-filec', "--file-capture", dest='rcap_file', default=2, type=int)
    parser.add_argument('-extc', "--ext-capture", dest='rcap_ext', default=3, type=int)

    parser.add_argument('-se', "--separate-ext", dest='separate_extensions', default=False, action='store_true')
    parser.add_argument('-sf', "--shorten-filename", dest='keep_original_filename', default=True, action='store_false')
    parser.add_argument('-aso', "--assume-safe-output-path", dest='ensure_output_path', default=True, action='store_false')

    parser.add_argument('-m', "--mode", dest='mode', default='move', help="Transfer mode:\nThis can be either 'copy' or 'move'.\nBy default, this is set to 'move'\n")

    cfg = parser.parse_args(argv)

    to_subfolder(cfg)

if __name__ == "__main__":
    #main(['-i', 'E:\\Downloads\\New folder', '-o', 'E:\\Downloads\\New folder (2)'])
    
    main(sys.argv[1:])
