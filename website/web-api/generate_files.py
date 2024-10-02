import os
import json
import hashlib


# Function to generate hash of a file's content
def generate_hash(content):
    return hashlib.md5(json.dumps(content, sort_keys=True).encode('utf-8')).hexdigest()


# Load the merged_data.json file
with open('mapping.json', 'r') as file:
    merged_data = json.load(file)

# Directory to store the JSON files
api_directory = 'api/license'

# Create the directory if it doesn't exist
os.makedirs(api_directory, exist_ok=True)

# Iterate over the merged data
for key, value in merged_data.items():

    path = key.replace('/', '_')

    # Determine the file path for the current license
    file_path = os.path.join(api_directory, f'{path}.json')

    # Prepare the content to be written
    content = {"canonical": value}

    # Check if the file exists
    if os.path.exists(file_path):
        # Load existing content
        with open(file_path, 'r') as f:
            existing_content = json.load(f)

        # Check if the content is different
        if generate_hash(existing_content) == generate_hash(content):
            # Content is the same, skip writing
            print(f"No change for {file_path}, skipping...")
        else:
            # Content is different, update the file
            print(f"Updating {file_path}...")
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=4)
    else:
        # File does not exist, create it
        print(f"Creating {file_path}...")
        with open(file_path, 'w') as f:
            json.dump(content, f, indent=4)
