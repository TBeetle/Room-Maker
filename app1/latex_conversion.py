import pandas as pd
import subprocess
import os
import shutil
from pdf2image import convert_from_path
from django.conf import settings

def conversion(file, layout_style):
    
    # Read Excel data 
    excel_data = pd.read_excel(os.path.join(settings.MEDIA_ROOT, 'imported_files', file))
    print("CALLING CONVERSION CODE:")
    print(file)

    # Define LaTeX template
    latex_walls_template = "\\draw[wall, line width={width}pt, line cap=round, color ={color}] ({x1},{y1}) -- ({x2},{y2}) coordinate (c);\n".format(width=layout_style.wall_width,color=layout_style.wall_color, x1='{:.2f}',y1='{:.2f}',x2='{:.2f}',y2='{:.2f}' )

    # Define LaTeX template for furniture
    latex_rectangle_furniture_template = "\\furnitureR[height={h1}, width={w1}, rotate={r1}]({a1}, {a2});\n".format(h1='{}',w1='{}', r1='{}',a1='{}',a2='{}')
    latex_circle_furniture_template = "\\furnitureC[radius={a1}]({a2}, {a3});\n".format(a1='{}', a2='{}', a3='{}')
    latex_furniture_label_template = "\\node[furniture-label, text={color} ] at ({a1},{a2}) {a3};\n".format(color=layout_style.furniture_color, a1='{}', a2='{}', a3='{{{}}}')

    # Define LaTeX template for windows
    latex_windows_template = "\\draw[window,line width={width}pt, line cap=round, color={color}] ({x1},{y1}) -- ({x2},{y2}) coordinate (c);\n".format(width=layout_style.window_width, color=layout_style.window_color, x1='{:.2f}',y1='{:.2f}',x2='{:.2f}',y2='{:.2f}' )

    # Define LaTeX template for sensors
    latex_sensor_template = "\\node[sensor, color={color}](sensor) at ({s1},{s2}) {{{s3}}};\n".format(color=layout_style.sensor_label_color,s1='{}',s2='{}',s3='{}')
    latex_sensor_label_template = "\\node[sensor-label,text={color}] at ({x1},{y1}) {a1};\n".format(color=layout_style.sensor_label_color,x1='{s1:.2f}',y1='{s2:.2f}',a1='{{{s3} \\\\ ({s1:.2f}, {s2:.2f})}}')

    # Define LaTeX template for cameras
    latex_camera_template = "\\camera[color={color},rotate={c1}]({c2},{c3});\n".format(color=layout_style.camera_label_color, c1='{}',c2='{}',c3='{}')
    latex_camera_label_template = "\\node[camera-label, text={color}] at ({c1},{c2}) {c3};\n".format(color=layout_style.camera_label_color,c1='{}',c2='{}',c3='{{{}}}')

    # Define LaTeX template for calibration locations
    latex_calibration_template = "\\node[location]({l1}) at ({l2},{l3}) {{{l4}}};\n".format(l1='{}',l2='{}',l3='{}',l4='{}')
    latex_calibration_label_template = "\\node[location-label] at ({l1}) {l2};\n".format(l1='{}',l2='{{{}}}')
    
    # Define LaTeX template for doors
    latex_door_template = "\\draw[door, rotate around={a}, line width={width}pt, color={color}] ({x1},{y1}) -- ++({x2},{y2});\n".format(a='{{{d1:.2f}:({d2:.2f},{d3:.2f})}}', width=layout_style.door_width,color=layout_style.door_color, x1='{d2:.2f}',y1='{d3:.2f}', x2='{d4:.2f}',y2='{d5:.2f}')
    # Define LaTeX template for room navigation
    latex_room_nav_template = "\\draw[nav-arrow,text={color}] ({r1},{r2}) -- ++({r3},{r4}) node[{r5}, fill=white] {r6};\n".format(color=layout_style.navigation_arrow_color,r1='{}',r2='{}',r3='{}',r4='{}',r5='{}',r6='{{{}}}')
    
     #Define LaTeX template for font
    latex_font_template = "\\setmainfont{{{font}}}\n".format(font=layout_style.font_type)

    latex_furniture_styling = """
    \\def\\furnitureR[height=#1, width=#2, rotate=#3](#4, #5){{%
	% Draws a rectangular furniture piece centered on provided coordinates in a Tikz picture
	% \\furnitureR[height=<value>, width=<value>, rotate=<degrees>](<x>, <y>)
	\\draw[line width={width}pt, color={color}, rotate around={{#3:(#4,#5)}}] (#4-#2/2, #5-#1/2) rectangle (#4+#2/2, #5+#1/2)  
    }}

    \\def\\furnitureC[radius=#1](#2, #3){{%
	    % Draws a circular furniture piece centered on provided coordinates in a Tikz picture
	    % \\furnitureC[radius=<value>](<x>, <y>)
	    \\draw[line width={width}pt, color={color}] (#2, #3) circle (#1)
    }}

    """.format(width=layout_style.furniture_width, color=layout_style.furniture_color)
    # Iterate through rows and generate LaTeX code for walls and furniture
    latex_code = ""
    for index, row in excel_data.iterrows():
        if row['Descriptor'] == 'WALL' and index < len(excel_data) - 1:
            x1 = row['X']
            y1 = row['Y']
            if index == len(excel_data) - 2 and excel_data.iloc[index + 1]['Type'] != 'Exterior':
                # Use the current row's coordinates for the last wall before the furniture
                x2 = row['X']
                y2 = row['Y']
            else:
                x2 = excel_data.at[index + 1, 'X']
                y2 = excel_data.at[index + 1, 'Y']
            latex_code += latex_walls_template.format(x1, y1, x2, y2)
        elif row['Descriptor'] == 'WINDOW' and index < len(excel_data) - 1:
            window_width = layout_style.window_width
            x1 = row['X']
            y1 = row['Y']
            if index == len(excel_data) - 2 and excel_data.iloc[index + 1]['Type'] != 'Exterior':
                # Use the current row's coordinates for the last window before the furniture
                x2 = row['X']
                y2 = row['Y']
            else:
                x2 = excel_data.at[index + 1, 'X']
                y2 = excel_data.at[index + 1, 'Y']
            latex_code += latex_windows_template.format(x1, y1, x2, y2)
        elif row['Descriptor'] == 'DOOR' and index < len(excel_data) - 1:
            x = row['X']
            y = row['Y']
            door_angle = row['door_angle']
            if(row['door_xory'] == 'x'):
                door_x = row['door_length']
                door_y = 0
            elif(row['door_xory'] == 'y'):
                door_x = 0
                door_y = row['door_length']
            
            latex_code += latex_door_template.format(d1=door_angle, d2=x, d3=y, d4=door_x, d5=door_y)
        elif row['Type'] == 'Furniture' and row['furniture_type'] == 'rectangle':
            width = row['width']
            height = row['height']
            rotation = row['rotation']
            table_name = row['Descriptor'].lower()
            x = row['X']
            y = row['Y']
            latex_code += latex_rectangle_furniture_template.format(height, width, rotation, x, y)
            latex_code += latex_furniture_label_template.format(x, y, row['Descriptor'])
        elif row['Type'] == 'Furniture' and row['furniture_type'] == 'circle':
            radius = row['radius']
            table_name = row['Descriptor'].lower()
            x = row['X']
            y = row['Y']
            latex_code += latex_circle_furniture_template.format(radius, x, y)
            latex_code += latex_furniture_label_template.format(x, y, row['Descriptor'])
        elif row['Type'] == 'Sensor':
            x = row['X']
            y = row['Y']
            latex_code += latex_sensor_template.format(x, y)
            latex_code += latex_sensor_label_template.format(s1=x, s2=y, s3=row['Descriptor'])
        elif row['Type'] == 'Camera':
            x = row['X']
            y = row['Y']
            rotation = row['rotation']
            latex_code += latex_camera_template.format(rotation, x, y)
            latex_code += latex_camera_label_template.format(x, y, row['Descriptor'])
        elif row['Type'] == 'Calibration':
            x = row['X']
            y = row['Y']
            latex_code += latex_calibration_template.format(row['Descriptor'], x, y)
            latex_code += latex_calibration_label_template.format(row['Descriptor'],row['Descriptor'])
        elif row['Type'] == 'Room Navigation':
            x = row['X']
            y = row['Y']
            if row['room_nav_direction'] == 'left':
                arrow_x = 12
                arrow_y = 0
                node_location = 'right'
            elif row['room_nav_direction'] == 'right':
                arrow_x = -12
                arrow_y = 0
                node_location = 'left'
            elif row['room_nav_direction'] == 'down':
                arrow_x = 0
                arrow_y = 12
                node_location = 'above'
            elif row['room_nav_direction'] == 'up':
                arrow_x = 0
                arrow_y = -12
                node_location = 'below'
            latex_code += latex_room_nav_template.format(x, y, arrow_x, arrow_y, node_location, row['Descriptor'])

    # Complete LaTeX code with autopopulated walls
    complete_latex_code = f"""
    %!TeX program = lualatex
    \\documentclass[12pt]{{article}}

    \\usepackage[hmargin=0.5in, tmargin=0.75in, bmargin=0.9in]{{geometry}}
    \\geometry{{legalpaper, portrait}}
    \\usepackage{{fontspec}}
   
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
    \\tikzstyle{{furniture-label}} = [fill=white, align=center]
    \\tikzstyle{{sensor}} = [circle, draw, color=teal, fill=teal, inner sep=0.5mm]
    \\tikzstyle{{sensor-label}} = [above, yshift=2pt, fill=white, align=center, text=teal]
    \\tikzstyle{{location}} = [diamond, draw, color=violet, fill=violet, inner sep=0.5mm]
    \\tikzstyle{{location-label}} = [above, yshift=3pt, fill=white, text=violet]
    \\tikzstyle{{walking-path}} = [densely dashed, line width=0.25mm, -{{Stealth[length=4mm, width=2mm]}}]
    \\tikzstyle{{nav-arrow}} = [line width=0.25mm, {{Stealth[length=4mm, width=2mm]}}-, green!60!black]
    \\tikzstyle{{nav-arrow2}} = [line width=0.25mm, {{Stealth[length=4mm, width=2mm]}}-, violet]
    
    {latex_furniture_styling}

    \\def\camera[#1](#2,#3){{
	    \\node[circle, draw, color=blue!75!black, fill=blue!75!black, inner sep=0in, minimum size=0.1in, anchor=center, #1] at (#2,#3) {{}};
	    \\node[isosceles triangle, draw, color=blue!75!black, fill=blue!75!black, inner sep=0in, minimum size=0.1in, isosceles triangle apex angle=75, anchor=east, #1] at (#2,#3) {{}}
     }}

    \\tikzstyle{{camera-label}} = [fill=white, align=center, text=blue!75!black, above, yshift=5pt]

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
        print("PDF generated successfully.") # Specify the destination folder
        print(layout_style.camera_label_color)

        pdf_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.pdf')
        tex_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.tex')
        aux_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.aux')
        log_destination_folder = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.log')
        
        # Move the generated PDF to the destination folder
        try:
            shutil.move('output.pdf', pdf_destination_folder)
            shutil.move('output.tex', tex_destination_folder)
            shutil.move('output.aux', aux_destination_folder)
            shutil.move('output.log', log_destination_folder)
        except Exception as e:
            print(f"Error moving files: {e}")
        
        # Delete current output.png and replace with updated one
        output_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.png')
        png = convert_from_path(pdf_destination_folder)
        for i, image in enumerate(png):
            image.save(f'{output_path}', 'PNG')
        return True;

    else:
        print("Error during PDF generation. Check the LaTeX log for details.")
        return False;
