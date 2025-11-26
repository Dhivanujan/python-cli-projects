import os
import shutil
import requests

def download_file(url, save_path):
    """Download a file from the internet."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded successfully: {save_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def rename_file(file_path, new_name):
    """Rename a file."""
    try:
        dir_name = os.path.dirname(file_path)
        new_path = os.path.join(dir_name, new_name)
        os.rename(file_path, new_path)
        print(f"File renamed successfully to: {new_path}")
    except Exception as e:
        print(f"Error renaming file: {e}")

def move_file(file_path, destination_folder):
    """Move a file to a different folder."""
    try:
        os.makedirs(destination_folder, exist_ok=True)
        shutil.move(file_path, destination_folder)
        print(f"File moved successfully to: {destination_folder}")
    except Exception as e:
        print(f"Error moving file: {e}")

def main():
    print("=== Python CLI Task Automation Tool ===")
    print("1. Download File")
    print("2. Rename File")
    print("3. Move File")
    choice = input("Choose a task (1/2/3): ")

    if choice == '1':
        url = input("Enter file URL: ")
        save_path = input("Enter save path (including filename): ")
        download_file(url, save_path)
    elif choice == '2':
        file_path = input("Enter current file path: ")
        new_name = input("Enter new file name: ")
        rename_file(file_path, new_name)
    elif choice == '3':
        file_path = input("Enter file path: ")
        destination_folder = input("Enter destination folder path: ")
        move_file(file_path, destination_folder)
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
