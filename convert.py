import os
import re

regular_folder = "/Users/jonathanyu/Desktop/coding/hopekcc_chordpro/temp/worship"
converted_folder = "/Users/jonathanyu/Desktop/coding/hopekcc_chordpro/converted"

def read_edit(file_name):
    print(f"Converting {file_name}...")
    
    try:
        with open(os.path.join(regular_folder, file_name), "r", encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File {file_name} not found in {regular_folder}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Create output filename
    base_name = os.path.splitext(file_name)[0]
    output_path = os.path.join(converted_folder, f"{base_name}.cho")
    
    # Ensure output directory exists
    os.makedirs(converted_folder, exist_ok=True)
    
    try:
        with open(output_path, "w", encoding='utf-8') as output_file:
            # Track current section state
            current_section = None
            
            # Write header (removed comment line)
            # output_file.write("# ChordPro file converted from OnSong format\n")
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Check if line contains metadata (has colon and no chord brackets before colon)
                if ":" in line and not re.search(r'\[[^\]]*\].*:', line):
                    lower = line.lower()
                    
                    if "title" in lower and lower.startswith("title"):
                        title = line.split(":", 1)[1].strip()
                        output_file.write(f"{{title: {title}}}\n")
                    
                    elif lower.startswith("key"):
                        # Extract key from [G] format or plain text
                        key_part = line.split(":", 1)[1].strip()
                        if "[" in key_part and "]" in key_part:
                            key = key_part.split("[")[1].split("]")[0].strip()
                        else:
                            key = key_part
                        output_file.write(f"{{key: {key}}}\n")
                    
                    elif "artist" in lower and lower.startswith("artist"):
                        artist = line.split(":", 1)[1].strip()
                        output_file.write(f"{{artist: {artist}}}\n")
                    
                    elif "tempo" in lower and lower.startswith("tempo"):
                        tempo = line.split(":", 1)[1].strip()
                        output_file.write(f"{{tempo: {tempo}}}\n")
                    
                    elif "scripture reference" in lower:
                        continue  # Skip scripture references
                    
                    elif "notes" in lower and lower.startswith("notes"):
                        continue  # Skip notes
                    
                    elif "book" in lower and lower.startswith("book"):
                        continue  # Skip book info
                    
                    # Section headers
                    elif "chorus" in lower and lower.startswith("chorus"):
                        if current_section:
                            output_file.write(f"{{end_of_{current_section}}}\n")
                        output_file.write("\n{start_of_chorus}\n")
                        current_section = "chorus"
                    
                    elif "verse" in lower and lower.startswith("verse"):
                        if current_section:
                            output_file.write(f"{{end_of_{current_section}}}\n")
                        # Extract verse number if present
                        verse_label = line.split(":")[0].strip()
                        if any(char.isdigit() for char in verse_label):
                            verse_num = re.search(r'\d+', verse_label)
                            if verse_num:
                                output_file.write(f"\n{{start_of_verse: Verse {verse_num.group()}}}\n")
                            else:
                                output_file.write(f"\n{{start_of_verse}}\n")
                        else:
                            output_file.write(f"\n{{start_of_verse}}\n")
                        current_section = "verse"
                    
                    elif any(keyword in lower for keyword in ["bridge", "tag", "pre-chorus", "pre chorus"]):
                        if current_section:
                            output_file.write(f"{{end_of_{current_section}}}\n")
                        section_name = line.split(":")[0].strip().lower()
                        if "tag" in section_name:
                            output_file.write(f"\n{{start_of_bridge: Tag}}\n")
                        elif "pre" in section_name:
                            output_file.write(f"\n{{start_of_bridge: Pre-Chorus}}\n")
                        else:
                            output_file.write(f"\n{{start_of_bridge}}\n")
                        current_section = "bridge"
                    
                    else:
                        # Skip unknown metadata
                        continue
                
                else:
                    # This is a lyric/chord line
                    if current_section is None:
                        # If we encounter lyrics without a section header, assume it's a verse
                        output_file.write("\n{start_of_verse}\n")
                        current_section = "verse"
                    
                    # Process the line to ensure proper ChordPro formatting
                    processed_line = process_chord_line(line)
                    output_file.write(f"{processed_line}\n")
            
            # Close final section if needed
            if current_section:
                output_file.write(f"{{end_of_{current_section}}}\n")
                
    except Exception as e:
        print(f"Error writing output file: {e}")
        return
    
    print(f"Successfully converted to {output_path}")

def process_chord_line(line):
    chord_pattern = r'\[([^\]]+)\]'
    processed = re.sub(r'\s+', ' ', line.strip())
    
    return processed

def convert_all_files():
    if not os.path.exists(regular_folder):
        print(f"Error: Source folder {regular_folder} does not exist")
        return
    
    onsong_files = [f for f in os.listdir(regular_folder) if f.lower().endswith('.onsong')]
    
    if not onsong_files:
        print("No .onsong files found in the source folder")
        return
    
    print(f"Found {len(onsong_files)} OnSong files to convert:")
    for file in onsong_files:
        read_edit(file)
    
    print("Conversion complete!")

def main():
    # Convert all .onsong files in the folder
    convert_all_files()

if __name__ == "__main__":
    main()