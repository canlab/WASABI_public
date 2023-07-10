#%%
# Written by Michael Sun, Ph.D.

import os
import glob

# This script helps generate a report of all distortion correction images from fmriprep output

def generate_html_with_images(directory):
    # Find all .svg files recursively in the directory
    svg_files = glob.glob(os.path.join(directory, 'sub-*/figures/*sdc_bold.svg'), recursive=True)

    # Create a dictionary to store SVG files by sub- and ses-
    svg_files_by_sub_ses = {}

    # Sort and group SVG files by sub- and ses-
    for svg_file in svg_files:
        # Get the filename without the directory path
        filename = os.path.basename(svg_file)
        # Extract the sub- and ses- keys from the filename
        sub_key, ses_key = filename.split('_')[:2]
        # Add the SVG file to the corresponding sub- and ses- key in the dictionary
        if sub_key not in svg_files_by_sub_ses:
            svg_files_by_sub_ses[sub_key] = {}
        if ses_key not in svg_files_by_sub_ses[sub_key]:
            svg_files_by_sub_ses[sub_key][ses_key] = []
        svg_files_by_sub_ses[sub_key][ses_key].append(svg_file)

    # Iterate over the sub- keys and generate HTML pages
    for sub_key, sub_svg_files in svg_files_by_sub_ses.items():
        # Sort the ses- keys within the sub- key
        sorted_ses_keys = sorted(sub_svg_files.keys())

        # Iterate over the sorted ses- keys and generate HTML pages
        for ses_key in sorted_ses_keys:
            # Create the HTML file for the sub- and ses-
            output_file = f"sub_{sub_key}_ses_{ses_key}.html"
            with open(output_file, 'w') as html_file:
                # Write the HTML header
                html_file.write('<html><body>\n')

                # Iterate over the SVG files for the sub- and ses-
                for svg_file in sub_svg_files[ses_key]:
                    # Get the filename without the directory path
                    filename = os.path.basename(svg_file)

                    svg_html = ''
                    with open(svg_file, 'r') as f:
                        svg_content = f.read()
                        svg_html += f'<div>{svg_content}</div>\n'

                    # Write the header and image tag for each file
                    html_file.write('<h2>{}</h2>\n'.format(filename))
                    html_file.write('{}'.format(svg_html))

                # Write the link to navigate to the next page
                next_ses_index = sorted_ses_keys.index(ses_key) + 1
                if next_ses_index < len(sorted_ses_keys):
                    next_ses_key = sorted_ses_keys[next_ses_index]
                    next_page = f"sub_{sub_key}_ses_{next_ses_key}.html"
                    html_file.write('<a href="{}">Next Page</a>\n'.format(next_page))

                # Write the HTML footer
                html_file.write('</body></html>\n')

            print('HTML file for sub-{}_ses_{} generated successfully.'.format(sub_key, ses_key))
#%%
# Example usage:

# Windows:
fmriprep_directory = r'\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\derivatives\fmriprep'  # Specify the directory path here
output_file = r'\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\scripts\fmriprepDSC_output.html'  # Specify the output HTML file path here

# Unix:
# directory = '//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep'  # Specify the directory path here
# output_file = '//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/scripts/fmriprepDSC_output.html'  # Specify the output HTML file path here

generate_html_with_images(fmriprep_directory, output_file)

# %%
# Look at a specific SVG file.
from IPython.display import SVG

# Load the SVG image file
svg_file = 'path/to/your/image.svg'

# Display the SVG image
SVG(filename=svg_file)