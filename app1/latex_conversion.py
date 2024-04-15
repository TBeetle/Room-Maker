import pandas as pd
import subprocess
import os
import shutil
from pdf2image import convert_from_path
from django.conf import settings

def conversion(file, layout_style):
    
    # Read Excel data into a dataframe
    excel_data = pd.read_excel(os.path.join(settings.MEDIA_ROOT, 'imported_files', file))
  
    # Convert first row and first column to lowercase
    excel_data.columns = excel_data.columns.str.lower()
    excel_data['type'] = excel_data['type'].str.lower()

    print("CALLING CONVERSION CODE:")
    print(file)
    
    # Define LaTeX template
    latex_walls_template = "\\draw[wall, line width={width}pt,color ={color}] ({x1},{y1}) -- ({x2},{y2}) coordinate (c);\n".format(width=layout_style.wall_width,color=layout_style.wall_color, x1='{:.2f}',y1='{:.2f}',x2='{:.2f}',y2='{:.2f}' )
   
    # Define LaTeX template for furniture
    latex_rectangle_furniture_template = "\\furnitureR[height={h1}, width={w1}, rotate={r1}]({a1}, {a2});\n".format(h1='{}',w1='{}', r1='{}',a1='{}',a2='{}')
    latex_circle_furniture_template = "\\furnitureC[radius={a1}]({a2}, {a3});\n".format(a1='{}', a2='{}', a3='{}')
    latex_furniture_label_template = "\\node[furniture-label, text={color} ] at ({a1},{a2}) {a3};\n".format(color=layout_style.furniture_color, a1='{}', a2='{}', a3='{{{}}}')

    # Define LaTeX template for windows
    latex_windows_template = "\\draw[window,line width={width}pt, color={color}] ({x1},{y1}) -- ({x2},{y2}) coordinate (c);\n".format(width=layout_style.window_width, color=layout_style.window_color, x1='{:.2f}',y1='{:.2f}',x2='{:.2f}',y2='{:.2f}' )

    # Define LaTeX template for sensors
    latex_sensor_template = "\\node[sensor, color={color}](sensor) at ({s1},{s2}) {{{s3}}};\n".format(color=layout_style.sensor_label_color,s1='{}',s2='{}',s3='{}')
    latex_sensor_label_template = "\\node[sensor-label,text={color}] at ({x1},{y1}) {a1};\n".format(color=layout_style.sensor_label_color,x1='{s1:.2f}',y1='{s2:.2f}',a1='{{{s3} \\\\ ({s1:.2f}, {s2:.2f})}}')

    # Define LaTeX template for cameras
    latex_camera_template = "\\camera[color={color},rotate={c1}]({c2},{c3});\n".format(color=layout_style.camera_label_color, c1='{}',c2='{}',c3='{}')
    latex_camera_label_template = "\\node[camera-label, text={color}] at ({c1},{c2}) {c3};\n".format(color=layout_style.camera_label_color,c1='{}',c2='{}',c3='{{{}}}')

    # Define LaTeX template for calibration locations
    latex_calibration_template = "\\node[location, color={color}]({l1}) at ({l2},{l3}) {{{l4}}};\n".format(color=layout_style.calibration_color,l1='{}',l2='{}',l3='{}',l4='{}')
    latex_calibration_label_template = "\\node[location-label, text={color}] at ({l1}) {l2};\n".format(color=layout_style.calibration_color,l1='{}',l2='{{{}}}')
    
    # Define LaTeX template for doors
    latex_door_template = "\\draw[door, rotate around={a}, line width={width}pt, color={color}] ({x1},{y1}) -- ++({x2},{y2});\n".format(a='{{{d1:.2f}:({d2:.2f},{d3:.2f})}}', width=layout_style.door_width,color=layout_style.door_color, x1='{d2:.2f}',y1='{d3:.2f}', x2='{d4:.2f}',y2='{d5:.2f}')
    # Define LaTeX template for room navigation
    latex_room_nav_template = "\\draw[nav-arrow,color={color}] ({r1},{r2}) -- ++({r3},{r4}) node[{r5}, fill=white] {r6};\n".format(color=layout_style.navigation_arrow_color,r1='{}',r2='{}',r3='{}',r4='{}',r5='{}',r6='{{{}}}')

    # Define LaTeX template for furniture styling
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

    # Define LaTeX template for gridlines

    # TODO: Add checks that user has entered correct column labels in header

    # check that data entered is valid
    x_axis_data = excel_data[excel_data['type'] == 'x axis'].iloc[0]
    y_axis_data = excel_data[excel_data['type'] == 'y axis'].iloc[0]
    x_min = x_axis_data['min']
    x_max = x_axis_data['max']
    if not is_numeric(x_min) or not is_numeric(x_max):
        message = f"Invalid input types for X Axis min/max values. Please enter real numbers."
        return {'success': False, 'message': message}
    y_min = y_axis_data['min']
    y_max = y_axis_data['max']
    if not is_numeric(y_min) or not is_numeric(y_max):
        message = f"Invalid input types for Y Axis min/max values. Please enter real numbers."
        return {'success': False, 'message': message}
    if (not x_min < x_max):
        message = f"Invalid input for X Axis min/max values. Please ensure that x_min is less than x_max."
    if (not y_min < y_max):
        message = f"Invalid input for Y Axis min/max values. Please ensure that y_min is less than y_max."
    x_step = x_axis_data['step']
    y_step = y_axis_data['step']
    if not is_numeric(x_step):
        message = f"Invalid input type for X Axis step value. Please enter a real number."
        return {'success': False, 'message': message}
    if x_step > abs(x_max-x_min):
        message = f"Invalid step value for X Axis. Please enter a number between {x_min} and {x_max}."
        return {'success': False, 'message': message}
    if not is_numeric(y_step):
        message = f"Invalid input types for Y Axis step value. Please enter a real number."
        return {'success': False, 'message': message}
    if y_step > abs(y_max-y_min):
        message = f"Invalid step value for Y Axis. Please enter a number between {y_min} and {y_max}."
        return {'success': False, 'message': message}

    latex_gridline_template = """
        %% GRID - X
        \\foreach \\i in {{{a1},{a2},...,{a3}}}{{
            \\draw[grid-line] (\\i,{a4}) -- (\\i,{a5});
            \\tikzmath{{int \\value; \\value = \\i;}}; 
            \\node[gray, below] at (\i,{a4}) {{\\SI{{\\value}}{{\\inch}}}};
        }}

        %% GRID - Y
        \\foreach \\i in {{{a6},{a7},...,{a8}}}{{
            \\draw[grid-line] ({a9},\\i) -- ({a10},\\i);
            \\tikzmath{{int \\value; \\value = \\i;}};
            \\node[gray, left] at ({a9},\\i) {{\\SI{{\\value}}{{\\inch}}}};
        }}
    """.format(a1=x_min,a2=x_min+x_step,a3=x_max, a4=y_min-5,a5=y_max+5,a6=y_min,a7=y_min+y_step,a8=y_max,a9=x_min-5,a10=x_max+5)

    
    # TODO: Do whatever you want with the labels here; this will only be called when a user changes the labels from Edit Style page
    # also move this section of code wherever


    # Iterate through rows and generate LaTeX code for walls and furniture
    latex_code = ""

    # Declaring variables to hold metadata
    latex_date = ""
    latex_room_name = ""
    latex_neighborhood = ""
    latex_building = ""
    latex_orientation = "portrait"

    # Defining allowed values for data validation
    WALL = 'wall'
    WINDOW = 'window'
    DOOR = 'door'
    FURNITURE = 'furniture'

    # Parse through uploaded Excel file
    for index, row in excel_data.iterrows():
        descriptor = row['descriptor']
        row_type = row['type']

        # Prevent parsing lines that don't contain data
        if row_type in ['x axis', 'y axis']:
            continue

        if descriptor.lower() == WALL and index < len(excel_data) - 1: 
            x1 = row['x']
            y1 = row['y']
             # check that x and y are valid number values
            if not is_numeric(x1):
                message = f"Invalid input type for x in row {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            if not is_numeric(y1):
                message = f"Invalid input type for y in row {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            # check that x and y are within range of gridlines
            if x1 < x_min or x1 > x_max:
                message = f"Invalid input for wall x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y1 < y_min or y1 > y_max:
                message = f"Invalid input for wall y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            # --- Data validation passed ---
            if excel_data.iloc[index + 1]['descriptor'].lower() != WALL:
                # If the next row is not a wall
                x2 = x1  # Set x2 to the same as x1
                y2 = y1  # Set y2 to the same as y1
            else:
                # If the next row is another wall
                x2 = excel_data.at[index + 1, 'x']
                y2 = excel_data.at[index + 1, 'y']
            latex_code += latex_walls_template.format(x1, y1, x2, y2)
        elif descriptor.lower() == WALL and index == len(excel_data) - 1:
            x1 = row['x']
            y1 = row['y']
            # check that x and y are valid number values
            if not is_numeric(x1):
                message = f"Invalid input type for x in row {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            if not is_numeric(y1):
                message = f"Invalid input type for y in row {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            # check that x and y are within range of gridlines
            if x1 < x_min or x1 > x_max:
                message = f"Invalid input for wall x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y1 < y_min or y1 > y_max:
                message = f"Invalid input for wall y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            # --- Data validation passed ---
            # If the current row is the last row and it's a wall
            x2 = x1  # Set x2 to the same as x1
            y2 = y1  # Set y2 to the same as y1
            latex_code += latex_walls_template.format(x1, y1, x2, y2)
        elif descriptor.lower() == WINDOW and index < len(excel_data) - 1:
            x1 = row['x']
            y1 = row['y']
            # check that x and y are valid number values
            if not is_numeric(x1):
                message = f"Invalid input type for x in row {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            if not is_numeric(y1):
                message = f"Invalid input type for y in row {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            if x1 < x_min or x1 > x_max:
                message = f"Invalid input for window x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y1 < y_min or y1 > y_max:
                message = f"Invalid input for window y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            if index == len(excel_data) - 2 and excel_data.iloc[index + 1]['type'] != 'exterior':
                # Use the current row's coordinates for the last window before the furniture
                x2 = row['x']
                y2 = row['y']
            else:
                x2 = excel_data.at[index + 1, 'x']
                y2 = excel_data.at[index + 1, 'y']
            latex_code += latex_windows_template.format(x1, y1, x2, y2)
        elif descriptor.lower() == DOOR and index < len(excel_data) - 1:
            x = row['x']
            y = row['y']
            door_angle = row['door_angle']
            # check that x, y, and angle are valid number values
            if not is_numeric(x):
                message = f"Invalid input type for x in row {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            if not is_numeric(y):
                message = f"Invalid input type for y in row + {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            if (not is_numeric(y)) or door_angle < 0 or door_angle > 360:
                message = f"Invalid input type for door_angle in row {index+2}. Please enter a number between 0 - 360."
                return {'success': False, 'message': message}
            if x < x_min or x > x_max:
                message = f"Invalid input for door x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y < y_min or y > y_max:
                message = f"Invalid input for door y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            door_xy = row['door_xory']
            # check that door_xy is either x or y
            if type(door_xy) in [str]:
                door_xy = door_xy.lower()
                if not is_numeric(row['door_length']):
                    message = f"Invalid input type for door_length in row {index+2}. Please enter a real number."
                    return {'success': False, 'message': message}
                if(door_xy == 'x'):
                    door_x = row['door_length']
                    door_y = 0
                elif(door_xy == 'y'):
                    door_x = 0
                    door_y = row['door_length']
                else:
                    message = f"Invalid input type for door_xory in row {index+2}. Please enter either 'X' or 'Y'."
                    print(message)  
                    return {'success': False, 'message': message}
            else:
                message = f"Invalid input type for door_xory in row {index+2}. Please enter either 'X' or 'Y'."
                return {'success': False, 'message': message}
            
            latex_code += latex_door_template.format(d1=door_angle, d2=x, d3=y, d4=door_x, d5=door_y)
        elif row_type == FURNITURE and row['furniture_type'].lower() == 'rectangle':
            width = row['width']
            height = row['height']
            rotation = row['rotation']
            table_name = descriptor.lower()
            x = row['x']
            y = row['y']
            # check that width, height, rotation, x, and y are all valid numbers.
            if (not is_numeric(width)) or (not is_numeric(height)) or (not is_numeric(rotation)) or (not is_numeric(x)) or (not is_numeric(y)):
                message = f"Invalid input type for furniture in line {index+2}. Please ensure you entered valid numbers for width, height, rotation, x, and y."
                return {'success': False, 'message': message}
            if x < x_min or x > x_max:
                message = f"Invalid input for furniture x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y < y_min or y > y_max:
                message = f"Invalid input for furniture y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            if width < 0 or width > abs(x_max-x_min):
                message = f"Invalid input for furniture width in row {index+2}. Please enter a width greater than 0 and within range of layout grid."
                return {'success': False, 'message': message}
            if height < 0 or height > abs(y_max-y_min):
                message = f"Invalid input for furniture height in row {index+2}. Please enter a height greater than 0 and within range of layout grid."
                return {'success': False, 'message': message}
            latex_code += latex_rectangle_furniture_template.format(height, width, rotation, x, y)
            latex_code += latex_furniture_label_template.format(x, y, descriptor)
        elif row_type == FURNITURE and row['furniture_type'].lower() == 'circle':
            radius = row['radius']
            x = row['x']
            y = row['y']
            if (not is_numeric(radius)) or (not is_numeric(x)) or (not is_numeric(y)):
                message = f"Invalid input type for furniture in line {index+2}. Please ensure you entered valid numbers for radius, x, and y."
                return {'success': False, 'message': message}
            if x < x_min or x > x_max:
                message = f"Invalid input for furniture x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y < y_min or y > y_max:
                message = f"Invalid input for furniture y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            if radius < 0 or radius > abs(x_max-x_min) or radius > abs(y_max-y_min):
                message = f"Invalid input for furniture radius in row {index+2}. Please enter a value greater than 0 and within range of layout grid."
                return {'success': False, 'message': message}
            latex_code += latex_circle_furniture_template.format(radius, x, y)
            latex_code += latex_furniture_label_template.format(x, y, descriptor)
        elif row_type == FURNITURE and row['furniture_type'].lower() not in ['rectangle', 'circle']:
            message = f"Invalid value for furniture_type in row {index+2}. Please enter either 'rectangle' or 'circle'."
            print(message)
            return {'success': False, 'message': message}
        elif row_type == 'sensor':
            x = row['x']
            y = row['y']
            if (not is_numeric(x)) or (not is_numeric(y)):
                message = f"Invalid input type for sensor x/y coordinates in line {index+2}. Please enter real numbers."
                return {'success': False, 'message': message}
            if x < x_min or x > x_max:
                message = f"Invalid input for sensor x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y < y_min or y > y_max:
                message = f"Invalid input for sensor y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            latex_code += latex_sensor_template.format(x, y)
            latex_code += latex_sensor_label_template.format(s1=x, s2=y, s3=descriptor)
        elif row_type == 'camera':
            x = row['x']
            y = row['y']
            rotation = row['rotation']
            if (not is_numeric(x)) or (not is_numeric(y)):
                message = f"Invalid input type for camera x/y coordinates in line {index+2}. Please enter real numbers."
                return {'success': False, 'message': message}
            if (is_numeric(rotation) and (rotation < 0 or rotation > 360)) or not is_numeric(rotation):
                message = f"Invalid input type for camera rotation in line {index+2}. Please enter a real number between 0-360."
            if x < x_min or x > x_max:
                message = f"Invalid input for camera x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y < y_min or y > y_max:
                message = f"Invalid input for camera y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            latex_code += latex_camera_template.format(rotation, x, y)
            latex_code += latex_camera_label_template.format(x, y, descriptor)
        elif row_type == 'calibration':
            x = row['x']
            y = row['y']
            if (not is_numeric(x)) or (not is_numeric(y)):
                message = f"Invalid input type for calibration x/y coordinates in line {index+2}. Please enter real numbers."
                return {'success': False, 'message': message}
            if x < x_min or x > x_max:
                message = f"Invalid input for calibration x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y < y_min or y > y_max:
                message = f"Invalid input for calibration y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            latex_code += latex_calibration_template.format(descriptor, x, y)
            latex_code += latex_calibration_label_template.format(descriptor,descriptor)
        elif row_type == 'room navigation':
            x = row['x']
            y = row['y']
            if (not is_numeric(x)) or (not is_numeric(y)):
                message = f"Invalid input type for room navigation x/y coordinates in line {index+2}. Please enter a real number."
                return {'success': False, 'message': message}
            if x < x_min or x > x_max:
                message = f"Invalid input for room navigation x-coordinate in row {index+2}. Please enter a coordinate between {x_min} and {x_max}."
                return {'success': False, 'message': message}
            if y < y_min or y > y_max:
                message = f"Invalid input for room navigation y-coordinate in row {index+2}. Please enter a coordinate between {y_min} and {y_max}."
                return {'success': False, 'message': message}
            room_nav_direction = row['room_nav_direction'].lower()
            if room_nav_direction not in ['left', 'right', 'up', 'down']:
                message = f"Invalid input type for room_nav_direction in line {index+2}. Please enter either left, right, down, or up."
                return {'success': False, 'message': message}
            
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
            
            latex_code += latex_room_nav_template.format(x, y, arrow_x, arrow_y, node_location, descriptor)
        elif row_type == 'date':
            latex_date = descriptor
        elif row_type == 'room name':
            latex_room_name = descriptor
        elif row_type == 'neighborhood':
            latex_neighborhood = descriptor
            print(f"neighborhood: {latex_neighborhood}")
        elif row_type == 'building':
            latex_building = descriptor
        elif row_type == 'orientation':
            orientation = descriptor.lower()
            if orientation not in ['portrait', 'landscape']:
                message = f"Invalid input type for orientation in line {index+2}. Please enter either 'portrait' or 'orientation'."
                return {'success': False, 'message': message}
            latex_orientation = descriptor

    # Scaling Layout
    y_scale_max = y_max+5
    y_scale_min = y_min-5
    y_scale_number = y_scale_max-y_scale_min
    if(y_scale_number >= 0 and y_scale_number<=274 and latex_orientation == "portrait"):
        latex_scale=1/10
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=275 and y_scale_number<=300 and latex_orientation == "portrait"):
        latex_scale=1/11
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=301 and y_scale_number<=329 and latex_orientation == "portrait"):
        latex_scale=1/12
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=330 and y_scale_number<=355 and latex_orientation == "portrait"):
        latex_scale=1/13
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=356 and y_scale_number<=383 and latex_orientation == "portrait"):
        latex_scale=1/14
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=384 and y_scale_number<=411 and latex_orientation == "portrait"):
        latex_scale=1/15
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=412 and y_scale_number<=439 and latex_orientation == "portrait"):
        latex_scale=1/16
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=440 and y_scale_number<=466 and latex_orientation == "portrait"):
        latex_scale=1/17
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=467 and y_scale_number<=494 and latex_orientation == "portrait"):
        latex_scale=1/18
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=495 and y_scale_number<=521 and latex_orientation == "portrait"):
        latex_scale=1/19
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=522 and y_scale_number<=549 and latex_orientation == "portrait"):
        latex_scale=1/20
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=550 and y_scale_number<=576 and latex_orientation == "portrait"):
        latex_scale=1/21
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=577 and y_scale_number<=604 and latex_orientation == "portrait"):
        latex_scale=1/22
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=605 and y_scale_number<=632 and latex_orientation == "portrait"):
        latex_scale=1/23
        latex_paper_size = "legalpaper"
    # Big Paper
    elif(y_scale_number >=633 and y_scale_number<=666 and latex_orientation == "portrait"):
        latex_scale=1/8
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=667 and y_scale_number<=750 and latex_orientation == "portrait"):
        latex_scale=1/9
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=751 and y_scale_number<=833 and latex_orientation == "portrait"):
        latex_scale=1/10
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=834 and y_scale_number<=916 and latex_orientation == "portrait"):
        latex_scale=1/11
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=917 and y_scale_number<=1000 and latex_orientation == "portrait"):
        latex_scale=1/12
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=1001 and y_scale_number<=1083 and latex_orientation == "portrait"):
        latex_scale=1/13
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=1084 and y_scale_number<=1150 and latex_orientation == "portrait"):
        latex_scale=1/14
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=1100 and y_scale_number<=1150 and latex_orientation == "landscape"):
        latex_scale=1/23.1
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=1050 and y_scale_number<=1099 and latex_orientation == "landscape"):
        latex_scale=1/22
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=1000 and y_scale_number<=1049 and latex_orientation == "landscape"):
        latex_scale=1/21
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=950 and y_scale_number<=999 and latex_orientation == "landscape"):
        latex_scale=1/20
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=900 and y_scale_number<=949 and latex_orientation == "landscape"):
        latex_scale=1/19
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=850 and y_scale_number<=899 and latex_orientation == "landscape"):
        latex_scale=1/18
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=800 and y_scale_number<=849 and latex_orientation == "landscape"):
        latex_scale=1/17
        latex_paper_size = "legalpaper"
    elif(y_scale_number >=750 and y_scale_number<=799 and latex_orientation == "landscape"):
        latex_scale=1/16
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=700 and y_scale_number<=749 and latex_orientation == "landscape"):
        latex_scale=1/15
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=650 and y_scale_number<=699 and latex_orientation == "landscape"):
        latex_scale=1/14
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=600 and y_scale_number<=649 and latex_orientation == "landscape"):
        latex_scale=1/13
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=545 and y_scale_number<=599 and latex_orientation == "landscape"):
        latex_scale=1/12
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=495 and y_scale_number<=544 and latex_orientation == "landscape"):
        latex_scale=1/11
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=445 and y_scale_number<=494 and latex_orientation == "landscape"):
        latex_scale=1/10
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=395 and y_scale_number<=444 and latex_orientation == "landscape"):
        latex_scale=1/9
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=344 and y_scale_number<=394 and latex_orientation == "landscape"):
        latex_scale=1/8
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=294 and y_scale_number<=343 and latex_orientation == "landscape"):
        latex_scale=1/7
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=244 and y_scale_number<=293 and latex_orientation == "landscape"):
        latex_scale=1/6
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=193 and y_scale_number<=243 and latex_orientation == "landscape"):
        latex_scale=1/5
        latex_paper_size = "papersize={{24in, 36in}}"
    elif(y_scale_number >=0 and y_scale_number<=192 and latex_orientation == "landscape"):
        latex_scale=1/19
        latex_paper_size = "legalpaper"



    # Complete LaTeX code with autopopulated walls
    complete_latex_code = f"""
    %!TeX program = lualatex
    \\documentclass[12pt]{{article}}

    \\usepackage[hmargin=0.5in, tmargin=0.75in, bmargin=0.9in]{{geometry}}
    \\geometry{{{latex_paper_size}, {latex_orientation}}}
   
    \\usepackage{{graphicx}}  % graphic controls
    \\usepackage{{float}}  % positioning controls
    \\usepackage{{lastpage}}  % last page number finder
    \\usepackage{{makecell}}  % helpers for multilined table cells

    % header/footer
    \\usepackage{{fancyhdr}}
    \\pagestyle{{fancy}}

    \\lhead{{{latex_date}}}
    \\chead{{}}
    \\rhead{{\\footnotesize \\thepage \\ {{\\color{{gray}} of \\pageref{{LastPage}}}}}}

    \\cfoot{{}}
    \\rfoot{{\\textbf{{\\LARGE {latex_room_name}}}\\\\\\vspace{{3pt}}{{\\large\\color{{gray}}NIH STTR Phase II}}}}

    \\renewcommand{{\\headrulewidth}}{{0.25pt}}
    \\renewcommand{{\\footrulewidth}}{{0.25pt}}

    % drawing things
    \\usepackage{{tikz}}
    \\usetikzlibrary{{math, calc, shapes, arrows.meta}}

    \\tikzstyle{{grid-line}} = [gray, very thin]
    \\tikzstyle{{wall}} = [line width=2pt, line cap=round]
    \\tikzstyle{{window}} = [line width=1pt, line cap=round]
    \\tikzstyle{{door}} = [line width=1pt]
    \\tikzstyle{{furniture}} = [draw, line width=0.5pt, transform shape]
    \\tikzstyle{{furniture-label}} = [fill=white, align=center]
    \\tikzstyle{{sensor}} = [circle, draw, color=teal, fill=teal, inner sep=0.5mm]
    \\tikzstyle{{sensor-label}} = [above, yshift=2pt, fill=white, align=center, text=teal]
    \\tikzstyle{{location}} = [diamond, draw, color=violet, fill=violet, inner sep=0.5mm]
    \\tikzstyle{{location-label}} = [above, yshift=3pt, fill=white, text=violet]
    \\tikzstyle{{walking-path}} = [densely dashed, line width=0.25mm, -{{Stealth[length=4mm, width=2mm]}}]
    \\tikzstyle{{nav-arrow}} = [line width=0.25mm, {{Stealth[length=4mm, width=2mm]}}-, green!60!black]
    
    {latex_furniture_styling}

    \\def\camera[#1](#2,#3){{
	    \\node[circle, draw, color=blue!75!black, fill=blue!75!black, inner sep=0in, minimum size=0.1in, anchor=center, #1] at (#2,#3) {{}};
	    \\node[isosceles triangle, draw, color=blue!75!black, fill=blue!75!black, inner sep=0in, minimum size=0.1in, isosceles triangle apex angle=75, anchor=east, #1] at (#2,#3) {{}}
     }}

    \\tikzstyle{{camera-label}} = [fill=white, align=center, text=blue!75!black, above, yshift=8pt]

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
    \\begin{{figure}}[H]
        \\centering

        \\begin{{tikzpicture}}[scale={latex_scale},  % use this to reduce or enlargen the image on paper
                            rotate=0]  % use this to rotate orientation by degrees on paper

    {latex_gridline_template}

    {latex_code}

    
    \\end{{tikzpicture}}
    \\end{{figure}}
    
    \\vspace*{{\\fill}}  % fills the area between the table and layout with whitespace, forcing the table to the bottom of the page.
    \\begin{{table}}[H]
	\\begin{{tabular}}{{l l}}
		\\makecell[lt]{{
			\\textbf{{Location:}}\\\\
     		{latex_neighborhood} Neighborhood \\\\
 		    {latex_building} Bldg, Still Hopes\\\\
           	1 Still Hopes Drive\\\\
           	West Columbia, SC 29033\\\\\\\\
        }}   	
        &	
		\\makecell[tp{{5in}}]{{
		\\textbf{{Notes:}}\\\\
		\\vspace{{-8mm}}  % reduce whitespace created by itemize above list
		\\begin{{itemize}}
			\\setlength\\itemsep{{-3mm}}  % reduce whitespace created by itemize between lines
			\\item Measurements are to the nearest \SI{{0.25}}{{\inch}}
			\\item The furniture locations are approximate.
			\\item Laptop and data acquisition system is located beside the table.
			\\item Cameras are located on the ceiling.
		\\end{{itemize}}
		}}	
			
	\\end{{tabular}}
	\\vspace{{-8mm}} % reduce whitespace after table
\\end{{table}}

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
        return {'success': True, 'message': ''};

    else:
        print("Error during PDF generation. Check the LaTeX log for details.")
        return {'success': False, 'message': 'Error occurred during PDF generation.'};



def is_numeric(value):
    try:
        pd.to_numeric(value)
        return True
    except ValueError:
        return False