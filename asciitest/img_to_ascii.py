import colorama
import os
import ascii_magic

save_path = r'C:\Users\emilm\OneDrive\Tiedostot\asciigame\asciigame\asciitest'
output_file = "ascii_image"
input_file = "faerun2"
completeInputName = os.path.join(save_path, input_file+".jpeg")
masterHtml = os.path.join(save_path, 'ascii_art'+".html")

masterInput = ascii_magic.obj_from_image_file(completeInputName)
masterInput.to_html_file(
    masterHtml,
    columns=300,
    char="@"
)