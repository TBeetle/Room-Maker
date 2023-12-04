import pandas as pd


# Read Excel data
#excel_data = pd.read_excel('C:\\Users\\Grant Ward\\Desktop\\UofSC School\\Senior Design\\example.xlsx')

# Construct the raw GitHub URL
excel_data = pd.read_excel('https://raw.githubusercontent.com/TBeetle/TheBackyardigans/ward_layoutconversion/layoutGenerator/uploads/imported_files/test-file.xlsx')

# Define LaTeX template for walls
latex_walls_template = "\\draw[wall, line cap=round] ({:.2f},{:.2f}) -- ({:.2f},{:.2f}) coordinate (c);\n"

# Define LaTeX template for furniture
latex_furniture_template = "\\node[furniture, rectangle, minimum width={:.2f}cm, minimum height={:.2f}cm]({}) at ({},{}) {{}};\n"
latex_furniture_label_template = "\\node[furniture-label] at ({}) {{{}}};\n"

#Define LAteX for template for windows
latex_windows_template = "\\draw[window] ({:.2f},{:.2f}) -- ({:.2f},{:.2f}) coordinate (c);\n"

# Iterate through rows and generate LaTeX code
# Iterate through rows and generate LaTeX code for walls and furniture
latex_code = ""
for index, row in excel_data.iterrows():
    if row['Type'] == 'Exterior' and index < len(excel_data) - 1 and row['Description' == 'WALL']:
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
    elif row['Type'] == 'Exterior' and index < len(excel_data) - 1 and row['Description' == 'WINDOW']:
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

# You can save it to a .tex file if needed
with open('output.tex', 'w') as f:
    f.write(complete_latex_code)