#Script to syncronize files between two foldes
import os
import shutil
import logging
from tqdm import tqdm
import argparse
import time

#Check if source and replica exist
def check_files(src_dir, rep_dir):
    if not os.path.exists(src_dir):
        print(f"\nSource folder '{src_dir}' does not exist.")
        return False
    if not os.path.exists(rep_dir):
        os.makedirs(rep_dir)
        print(f"\Replica folder '{rep_dir}' created.")
    return True
    
def sync_folders(src_dir,rep_dir, delete=False):
    # 1 - Get a list of all files in the source folder
    files_to_sync = []
    for root, dirs, files in os.walk(src_dir):
        for directory in dirs:
            files_to_sync.append(os.path.join(root,directory))
        for file in files:
            files_to_sync.append(os.path.join(root,file))
    
    # 2 - Get copies to replica folder
    with tqdm(total=len(files_to_sync), desc='Syncing files', unit='file') as pbar:
        #Iterate over each file and copy each file in the source folder
        for source_path in files_to_sync:
            replica_path = os.path.join(rep_dir, os.path.relpath(source_path, src_dir))
            # Check path and create if it doesn't exist

            if os.path.isdir(source_path):
                if not os.path.exists(replica_path):
                    os.makedirs(replica_path)
                    logging.info(f"Directory created: {replica_path}")
            
            else:
                if not os.path.exists(replica_path):
                    pbar.set_description(f"Processing '{source_path}'")
                    print(f"\nCopying {source_path} to {replica_path}")
                    shutil.copy2(source_path, replica_path)
                    logging.info(f"File copied: {source_path} -> {replica_path}")

            pbar.update(1)
    if delete:
        for root, dirs, files in os.walk(rep_dir):
            for file in files:
                replica_file = os.path.join(root, file)
                source_file = os.path.join(src_dir, os.path.relpath(replica_file, rep_dir))

                if not os.path.exists(source_file):
                    os.remove(replica_file)
                    logging.info(f"File deleted: {replica_file}")

            for directory in dirs:
                replica_dir = os.path.join(root, directory)
                source_dir = os.path.join(src_dir, os.path.relpath(replica_dir, rep_dir))

                if not os.path.exists(source_dir):
                    shutil.rmtree(replica_dir)
                    logging.info(f"Directory deleted: {replica_dir}")

def create_log(log_file='sync_log.txt'):
    logging.basicConfig(
        filename=log_file,   # Log to a file
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log entries
        filemode='a'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)

    logging.info('Logging initialized')

def main():

    parser = argparse.ArgumentParser(description='Synchronize folders and log actions.')

    parser.add_argument('source', type=str, help='Source folder path')
    parser.add_argument('replica', type=str, help='Replica folder path')
    parser.add_argument('interval', type=int, help='Synchronization interval in milliseconds')
    parser.add_argument('log_file', type=str, help='Log file path')

    args = parser.parse_args()

    create_log(args.log_file)

    if check_files(args.source, args.replica):
        while True:
            sync_folders(args.source, args.replica, delete=True)
            time.sleep(args.interval)

if __name__ == '__main__':
    main()