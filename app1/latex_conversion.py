import pandas as pd
import subprocess
import os
import shutil
from pdf2image import convert_from_path
from django.conf import settings

def conversion(file, style_settings):

    # Read Excel data
    excel_data = pd.read_excel(os.path.join(settings.MEDIA_ROOT, 'imported_files', file))
    print("CALLING CONVERSION CODE:")
    print(file)

    # Define LaTeX template
    latex_walls_template = "\\draw[wall, line cap=round] ({:.2f},{:.2f}) -- ({:.2f},{:.2f}) coordinate (c);\n"
   
    # Check the number of placeholders in the string
    num_placeholders = latex_walls_template.count('{}')
    print("Number of placeholders:", num_placeholders)
    # Check the number of values being passed
    num_values = 4  # Adjust this based on the actual number of values you're passing
    print("Number of values:", num_values)

    # Define LaTeX template for furniture
    latex_furniture_template = "\\node[furniture, rectangle, minimum width={:.2f}cm, minimum height={:.2f}cm]({}) at ({},{}) {{}};\n"
    latex_furniture_label_template = "\\node[furniture-label] at ({}) {{{}}};\n"
    print("check")

    # Define LaTeX template for windows
    latex_windows_template = "\\draw[window, line cap=round] ({:.2f},{:.2f}) -- ({:.2f},{:.2f}) coordinate (c);\n"

    # Iterate through rows and generate LaTeX code for walls and furniture
    latex_code = ""
    for index, row in excel_data.iterrows():
        if row['Descriptor'] == 'WALL' and index < len(excel_data) - 1:
            x1 = row['X']
            y1 = row['Y']
            if index == len(excel_data) - 2 and excel_data.iloc[index + 1]['Type'] == 'Furniture':
                # Use the current row's coordinates for the last wall before the furniture
                x2 = row['X']
                y2 = row['Y']
            else:
                x2 = excel_data.at[index + 1, 'X']
                y2 = excel_data.at[index + 1, 'Y']
            latex_code += latex_walls_template.format(x1, y1, x2, y2)
        elif row['Descriptor'] == 'WINDOW' and index < len(excel_data) - 1:
            window_width = style_settings.window_width
            x1 = row['X']
            y1 = row['Y']
            if index == len(excel_data) - 2 and excel_data.iloc[index + 1]['Type'] == 'Furniture':
                # Use the current row's coordinates for the last window before the furniture
                x2 = row['X']
                y2 = row['Y']
            else:
                x2 = excel_data.at[index + 1, 'X']
                y2 = excel_data.at[index + 1, 'Y']
            latex_code += latex_windows_template.format(x1, y1, x2, y2)
        elif row['Type'] == 'Furniture':
            width = row['width']
            height = row['height']
            table_name = row['Descriptor'].lower()
            x = row['X']
            y = row['Y']
            latex_code += latex_furniture_template.format(width, height, table_name, x, y)
            latex_code += latex_furniture_label_template.format(f"{table_name}.center", row['Descriptor'])
    

    # Complete LaTeX code with autopopulated walls
    complete_latex_code = f"""
    %!TeX program = lualatex
    \\documentclass[12pt]{{article}}

    \\usepackage[hmargin=0.5in, tmargin=0.75in, bmargin=0.9in]{{geometry}}
    \\geometry{{legalpaper, portrait}}

    \\usepackage{{graphicx}}  % graphic controls
    \\usepackage{{float}}  % positioning controls
    \\usepackage{{lastpage}}  % last page number finder
    \\usepackage{{makecell}}  % helpers for multilined table cells

    % header/footer
    \\usepackage{{fancyhdr}}
    \\pagestyle{{fancy}}

    \\lhead{{2023 June 5}}
    \\chead{{}}
    \\rhead{{\\footnotesize \\thepage \\ {{\\color{{gray}} of \\pageref{{LastPage}}}}}}

    \\cfoot{{}}
    \\rfoot{{\\textbf{{\\LARGE Congaree Activity Room Layout}}\\\\\\vspace{{3pt}}{{\\large\\color{{gray}}NIH STTR Phase II}}}}

    \\renewcommand{{\\headrulewidth}}{{0.25pt}}
    \\renewcommand{{\\footrulewidth}}{{0.25pt}}

    % drawing things
    \\usepackage{{tikz}}
    \\usetikzlibrary{{math, calc, shapes, arrows.meta}}

    \\tikzstyle{{grid-line}} = [gray, very thin]
    \\tikzstyle{{wall}} = [line width=2pt]
    \\tikzstyle{{window}} = [line width=1pt]
    \\tikzstyle{{door}} = [line width=1pt]
    \\tikzstyle{{furniture}} = [draw, line width=0.5pt, transform shape]
    \\tikzstyle{{furniture-label}} = [fill=white]
    \\tikzstyle{{sensor}} = [circle, draw, color=teal, fill=teal, inner sep=0.5mm]
    \\tikzstyle{{sensor-label}} = [above, yshift=2pt, fill=white, align=center, text=teal]
    \\tikzstyle{{location}} = [diamond, draw, color=violet, fill=violet, inner sep=0.5mm]
    \\tikzstyle{{location-label}} = [below, yshift=-3pt, fill=white, text=violet]
    \\tikzstyle{{walking-path}} = [densely dashed, line width=0.25mm, -{{Stealth[length=4mm, width=2mm]}}]
    \\tikzstyle{{nav-arrow}} = [line width=0.25mm, {{Stealth[length=4mm, width=2mm]}}-, green!60!black]
    \\tikzstyle{{nav-arrow2}} = [line width=0.25mm, {{Stealth[length=4mm, width=2mm]}}-, violet]

    \\tikzstyle{{camera-label}} = [fill=white, text=blue!75!black]

    % units
    \\usepackage{{siunitx}}
    \\sisetup{{per-mode = symbol}}

    \\let\\DeclareUSUnit\\DeclareSIUnit
    \\let\\US\\SI
    \\let\\us\\si
    \\DeclareUSUnit\\inch{{in}}
    \\DeclareUSUnit\\feet{{ft}}
    \\DeclareUSUnit\\foot{{ft}}
    \\DeclareUSUnit\\pound{{lb}}
    \\DeclareUSUnit\\slug{{slug}}

    % paragraph settings
    \\setlength{{\\parindent}}{{0em}}
    \\raggedright

    \\begin{{document}}
    \\vspace*{{.8in}}
    \\begin{{figure}}[H]
        \\centering

        \\begin{{tikzpicture}}[scale=1/12,  % use this to reduce or enlargen the image on paper
                            rotate=0]  % use this to rotate orientation by degrees on paper

        %% GRID - X
        \\foreach \\i in {{0,24,...,192}}{{
            \\draw[grid-line] (\\i,-12) -- (\\i,204);
            \\tikzmath{{int \\value; \\value = \\i;}}; 
            \\node[gray, below] at (\i,-12) {{\\SI{{\\value}}{{\\inch}}}};
        }}

        %% GRID - Y
        \\foreach \\i in {{0,24,...,192}}{{
            \\draw[grid-line] (-12,\\i) -- (204,\\i);
            \\tikzmath{{int \\value; \\value = \\i;}};
            \\node[gray, left] at (-12,\\i) {{\\SI{{\\value}}{{\\inch}}}};
        }}

        {latex_code}

        \\end{{tikzpicture}}
    \\end{{figure}}
    \\end{{document}}
    """
    # Print or save LaTeX code
    # print(complete_latex_code)

    # Save LaTeX code to a .tex file
    tex_file_path = 'output.tex'
    with open(tex_file_path, 'w') as f:
        f.write(complete_latex_code)

    # TODO: create a new ConvertedFile for the user and upload the 'output.tex' 

    # Run the LaTeX compiler (lualatex) to generate the PDF
    process = subprocess.run(['lualatex', tex_file_path])

    # Check if the compilation was successful
    if process.returncode == 0:
        print("PDF generated successfully.")

        # Specify the destination folder
        pdf_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.pdf')
        tex_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.tex')
        aux_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.aux')
        log_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.log')

        # Move the generated PDF to the destination folder
        shutil.move('output.pdf', pdf_destination_folder)
        shutil.move('output.tex', tex_destination_folder)
        shutil.move('output.aux', aux_destination_folder)
        shutil.move('output.log', log_destination_folder)

        # Delete current output.png and replace with updated one
        output_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.png')
        png = convert_from_path(pdf_destination_folder)
        for i, image in enumerate(png):
            image.save(f'{output_path}', 'PNG')

    else:
        print("Error during PDF generation. Check the LaTeX log for details.")
