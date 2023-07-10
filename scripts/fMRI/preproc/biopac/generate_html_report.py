#%%
import os
import glob

def generate_html_with_images(directory, output_file):
    # Find all .png files recursively in the directory
    png_files = glob.glob(os.path.join(directory, '**/*.png'), recursive=True)

    # Create the HTML file
    with open(output_file, 'w') as html_file:
        # Write the HTML header
        html_file.write('<html><body>\n')

        # Iterate over the PNG files
        for png_file in png_files:
            # Get the filename without the directory path
            filename = os.path.basename(png_file)

            # Write the header and image tag for each file
            html_file.write('<h2>{}</h2>\n'.format(filename))
            html_file.write('<img src="{}" />\n'.format(png_file))

        # Write the HTML footer
        html_file.write('</body></html>\n')

    print('HTML file generated successfully.')
#%%
# Example usage:
directory = r'\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\biopac\1080_wasabi\acq\physio02_sort'  # Specify the directory path here
output_file = r'\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\biopac\1080_wasabi\acq\physio02_sort_output.html'  # Specify the output HTML file path here

generate_html_with_images(directory, output_file)
# %%
