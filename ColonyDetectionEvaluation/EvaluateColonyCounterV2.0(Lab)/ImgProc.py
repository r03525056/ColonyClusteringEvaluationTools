import cv2
import numpy as np
import sys, os
import math
import time
#
# img must be a binary image
# return white region as a list of components
#

OFFSET_x = 0
OFFSET_y = 1
OFFSET_B = 2
OFFSET_G = 3
OFFSET_R = 4
OFFSET_Y = 5
OFFSET_Cr = 6
OFFSET_Cb = 7
BLACK = [0,0,0]

OFFSET_MIN_X = 0
OFFSET_MAX_X = 1
OFFSET_MIN_Y = 2
OFFSET_MAX_Y = 3
OFFSET_PIXELS= 4
OFFSET_SHAPE_FACTOR = 5
OFFSET_COLOR_MODE   = 6
OFFSET_GRADIENT_MODE= 7
OFFSET_AREA  = 8
OFFSET_PERIMETER = 9
OFFSET_MEAN = 10
OFFSET_STD  = 11
OFFSET_SOLIDITY  = 12
OFFSET_ASPECT_RATIO = 13
OFFSET_COLONY_TYPE = 14


def connectedComponent(img, type='gray'):
    if type == 'gray':
        # get rows, cols of img
        rows, cols = img.shape
        # initialize connected component labels
        conn = []
        for i in range(rows):
            conn.append([0] * cols)    
        
        # initialize label
        label = 0        
    
        # first label of conn
        for y in range(rows):
            for x in range(cols):
                # get non-zero intensity pixel and assign label
                if img[y][x] != 0:
                    label += 1
                    conn[y][x] = label
            
    
        # do_first is used to make loop like a do-while loop
        do_first = True
        change = False
        while(do_first or change):
            change = False
            # top-down scan using 4-connected
            for y in range(rows):
                for x in range(cols):
                    if conn[y][x] != 0:
                        # check north
                        if y-1 >= 0 and conn[y-1][x] != 0 and conn[y-1][x] < conn[y][x]:
                            conn[y][x] = conn[y-1][x]
                            change = True
                        # check east
                        if x+1 < cols and conn[y][x+1] != 0 and conn[y][x+1] < conn[y][x]:
                            conn[y][x] = conn[y][x+1]
                            change = True
                        # check south
                        if y+1 < rows and conn[y+1][x] != 0 and conn[y+1][x] < conn[y][x]:
                            conn[y][x] = conn[y+1][x]
                            change = True
                        # check west
                        if x-1 >= 0 and conn[y][x-1] != 0 and conn[y][x-1] < conn[y][x]:
                            conn[y][x] = conn[y][x-1]
                            change = True
            # bottom-up scan using 4-connected
            for y in range(rows):
                for x in range(cols):
                    if conn[rows-1-y][cols-1-x] != 0:
                        # check north
                        if rows-1-y-1 >= 0 and conn[rows-1-y-1][cols-1-x] != 0 and conn[rows-1-y-1][cols-1-x] < conn[rows-1-y][cols-1-x]:
                            conn[rows-1-y][cols-1-x] = conn[rows-1-y-1][cols-1-x]
                            change = True
                        # check east
                        if cols-1-x+1 < cols and conn[rows-1-y][cols-1-x+1] != 0 and conn[rows-1-y][cols-1-x+1] < conn[rows-1-y][cols-1-x]:
                            conn[rows-1-y][cols-1-x] = conn[rows-1-y][cols-1-x+1]
                            change = True
                        # check south
                        if rows-1-y+1 < rows and conn[rows-1-y+1][cols-1-x] != 0 and conn[rows-1-y+1][cols-1-x] < conn[rows-1-y][cols-1-x]:
                            conn[rows-1-y][cols-1-x] = conn[rows-1-y+1][cols-1-x]
                            change = True
                        # check west
                        if cols-1-x-1 >= 0 and conn[rows-1-y][cols-1-x-1] != 0 and conn[rows-1-y][cols-1-x-1] < conn[rows-1-y][cols-1-x]:
                            conn[rows-1-y][cols-1-x] = conn[rows-1-y][cols-1-x-1]
                            change = True
        
            # after do first, set it to False
            if do_first:
                do_first = False    
    
    
        components = {}
        # find connected components and compute component features
    
        for y in range(rows):
            for x in range(cols):    
                # find pixels whose label > 0
                if conn[y][x] != 0:
                    i = conn[y][x]
            
                    #peri_count = 0
                    ## check for top
                    #if y-1<0 or conn[y-1][x] == 0:
                        #peri_count += 1
                    ## check for east
                    #if x+1>=cols or conn[y][x+1] == 0:
                        #peri_count += 1
                    ## check for south
                    #if y+1>=rows or conn[y+1][x] == 0:
                        #peri_count += 1
                    ## check for west
                    #if x-1<0 or conn[y][x-1] == 0:
                        #peri_count += 1
            
                    if i not in components:
                        components[i] = {}
                        components[i]['area'] = 1
                        components[i]['min_x'] = x
                        components[i]['min_y'] = y
                        components[i]['max_x'] = x
                        components[i]['max_y'] = y
                        components[i]['total_x'] = x
                        components[i]['total_y'] = y
                        components[i]['pixels'] = []
                        components[i]['pixels'].append({'x':x, 'y':y})
                        #components[i]['perimeter'] = peri_count
                    else:
                        components[i]['area'] += 1
                        if x < components[i]['min_x']:
                            components[i]['min_x'] = x
                        if y < components[i]['min_y']:
                            components[i]['min_y'] = y
                        if x > components[i]['max_x']:
                            components[i]['max_x'] = x
                        if y > components[i]['max_y']:
                            components[i]['max_y'] = y
                        components[i]['total_x'] += x
                        components[i]['total_y'] += y
                        components[i]['pixels'].append({'x':x, 'y':y})
                        #components[i]['perimeter'] += peri_count
    elif type == 'color':
        # get rows, cols of img
        rows, cols, channels = img.shape
        img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
        #label = [[False for i in range(cols)] for j in range(rows)]
        label = np.zeros((cols, rows))
        components = []
        #print rows,cols
        key = ''
        for y in range(rows):
            for x in range(cols):
                if not label[y, x] and not (img[y, x] == BLACK).all():
                    label[y, x] = True
                    region = []
                    component = [None] * 15
                    component_pixels = []
                    neighbor_pixel = get_pixel(y, x, img[y, x], img_ycrcb[y, x])
                    region.append(neighbor_pixel)
                    min_x = x
                    max_x = x
                    min_y = y
                    max_y = y

                    isUpdate = False
                    while len(region) != 0:
                        pixel = region.pop(0)
                        component_pixels.append(pixel)
                        neighbor_x = pixel[OFFSET_x]
                        neighbor_y = pixel[OFFSET_y]
                        
                        # check left pixel
                        X = neighbor_x-1
                        Y = neighbor_y
                        if X >= 0 and not label[Y, X] and not (img[Y, X] == BLACK).all():
                            neighbor_pixel = get_pixel(Y, X, img[Y, X], img_ycrcb[Y, X])
                            region.append(neighbor_pixel)
                            label[Y, X] = True
                            min_x = min(X, min_x)
 
                        # check top pixel
                        X = neighbor_x
                        Y = neighbor_y-1         
                        if Y >= 0 and not label[Y, X] and not (img[Y, X] == BLACK).all():
                            neighbor_pixel = get_pixel(Y, X, img[Y, X], img_ycrcb[Y, X])
                            region.append(neighbor_pixel)
                            label[Y, X] = True
                            min_y = min(Y, min_y)

                        # check right pixel
                        X = neighbor_x+1
                        Y = neighbor_y       
                        if X < cols and not label[Y, X] and not (img[Y, X] == BLACK).all():
                            neighbor_pixel = get_pixel(Y, X, img[Y, X], img_ycrcb[Y, X])
                            region.append(neighbor_pixel)
                            label[Y, X] = True
                            max_x = max(X, max_x)
                            
                        # check bot pixel
                        X = neighbor_x
                        Y = neighbor_y+1        
                        if Y < rows and not label[Y, X] and not (img[Y, X] == BLACK).all():
                            neighbor_pixel = get_pixel(Y, X, img[Y, X], img_ycrcb[Y, X])
                            region.append(neighbor_pixel)
                            label[Y, X] = True
                            max_y = max(Y, max_y)
                                             
                    component[OFFSET_MIN_X] = min_x
                    component[OFFSET_MAX_X] = max_x
                    component[OFFSET_MIN_Y] = min_y
                    component[OFFSET_MAX_Y] = max_y
                    component[OFFSET_PIXELS]= component_pixels
                    components.append(component)
    elif type == 'ycrcb':
        # get rows, cols of img
        rows, cols, channels = img.shape
        img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
        label = [[False for i in range(cols)] for j in range(rows)]
        components = []
        for y in range(rows):
            for x in range(cols):
                if not np.array_equal(img[y][x], [0,0,0]) and not label[y][x]:
                    label[y][x] = True
                    region = []
                    component = {}
                    component_pixels = []
                    component_pixels.append(get_pixel(y, x, img[y][x], img_ycrcb[y][x]))
                    min_x = x
                    max_x = x
                    min_y = y
                    max_y = y
            
                    # check left pixel
                    if x-1 >= 0 and not np.array_equal(img[y][x-1], [0,0,0]) and not label[y][x-1]:
                        neighbor_pixel = get_pixel(y, x-1, img[y][x-1], img_ycrcb[y][x-1])
                        region.append(neighbor_pixel)
                        component_pixels.append(neighbor_pixel)
                        label[y][x-1] = True
                        if x-1 < min_x:
                            min_x = x-1
                    # check top pixel
                    if y-1 >= 0 and not np.array_equal(img[y-1][x], [0,0,0]) and not label[y-1][x]:
                        neighbor_pixel = get_pixel(y-1, x, img[y-1][x], img_ycrcb[y-1][x])
                        region.append(neighbor_pixel)
                        component_pixels.append(neighbor_pixel)
                        label[y-1][x] = True
                        if y-1 < min_y:
                            min_y = y-1
            # check right pixel
                    if x+1 < cols and not np.array_equal(img[y][x+1], [0,0,0]) and not label[y][x+1]:
                        neighbor_pixel = get_pixel(y, x+1, img[y][x+1], img_ycrcb[y][x+1])
                        region.append(neighbor_pixel)
                        component_pixels.append(neighbor_pixel)
                        label[y][x+1] = True
                        if x+1 > max_x:
                            max_x = x+1
                    # check bot pixel
                    if y+1 < rows and not np.array_equal(img[y+1][x], [0,0,0]) and not label[y+1][x]:
                        neighbor_pixel = get_pixel(y+1, x, img[y+1][x], img_ycrcb[y+1][x])
                        region.append(neighbor_pixel)
                        component_pixels.append(neighbor_pixel)
                        label[y+1][x] = True
                        if y+1 > max_y:
                            max_y = y+1

                    while len(region) != 0:
                        pixel = region.pop(0)
                        neighbor_x = pixel['x']
                        neighbor_y = pixel['y']
                        # check left pixel
                        if neighbor_x-1 >= 0 and not np.array_equal(img[neighbor_y][neighbor_x-1], [0,0,0]) and not label[neighbor_y][neighbor_x-1]:
                            neighbor_pixel = get_pixel(neighbor_y, neighbor_x-1, img[neighbor_y][neighbor_x-1], img_ycrcb[neighbor_y][neighbor_x-1])
                            region.append(neighbor_pixel)
                            component_pixels.append(neighbor_pixel)
                            label[neighbor_y][neighbor_x-1] = True
                            if neighbor_x-1 < min_x:
                                min_x = neighbor_x-1                
                        # check top pixel
                        if neighbor_y-1 >= 0 and not np.array_equal(img[neighbor_y-1][neighbor_x], [0,0,0]) and not label[neighbor_y-1][neighbor_x]:
                            neighbor_pixel = get_pixel(neighbor_y-1, neighbor_x, img[neighbor_y-1][neighbor_x], img_ycrcb[neighbor_y-1][neighbor_x])
                            region.append(neighbor_pixel)
                            component_pixels.append(neighbor_pixel)
                            label[neighbor_y-1][neighbor_x] = True
                            if neighbor_y-1 < min_y:
                                min_y = neighbor_y-1                
                        # check right pixel
                        if neighbor_x+1 < cols and not np.array_equal(img[neighbor_y][neighbor_x+1], [0,0,0]) and not label[neighbor_y][neighbor_x+1]:
                            neighbor_pixel = get_pixel(neighbor_y, neighbor_x+1, img[neighbor_y][neighbor_x+1], img_ycrcb[neighbor_y][neighbor_x+1])
                            region.append(neighbor_pixel)
                            component_pixels.append(neighbor_pixel)
                            label[neighbor_y][neighbor_x+1] = True
                            if neighbor_x+1 > max_x:
                                max_x = neighbor_x+1                
                        # check bot pixel
                        if neighbor_y+1 < rows and not np.array_equal(img[neighbor_y+1][neighbor_x], [0,0,0]) and not label[neighbor_y+1][neighbor_x]:
                            neighbor_pixel = get_pixel(neighbor_y+1, neighbor_x, img[neighbor_y+1][neighbor_x], img_ycrcb[neighbor_y+1][neighbor_x])
                            region.append(neighbor_pixel)
                            component_pixels.append(neighbor_pixel)
                            label[neighbor_y+1][neighbor_x] = True
                            if neighbor_y+1 > max_y:
                                max_y = neighbor_y+1                

                    component['pixels'] = component_pixels
                    component['min_x'] = min_x
                    component['max_x'] = max_x
                    component['min_y'] = min_y
                    component['max_y'] = max_y
                    components.append(component)    
    
    return components


#
#
# region growing
#
# img: must be a binary image
# dis: intensity difference

def regionGrowing(img, dis, buffer_size, color=True, seed_list=None, pca=None):
    #rows = img.shape[0]
    #cols = img.shape[1]

    rows, cols, ch = img.shape
    #label = [[False for i in range(cols)] for j in range(rows)]
    label = np.zeros((cols, rows))
    components = []
    train_means = []
    img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)

    # img type is gray
    if color == 'gray':
        for y in range(rows):
            for x in range(cols):
                if not label[y][x]:
                    now_intensity = int(img[y][x])
                    now_pixel = {'x':x, 'y':y}
                    label[y][x] = True
                    region = []
                    component = []
                    component.append(now_pixel)
                    region.append(now_pixel)

                    while len(region) != 0:
                        pixel = region.pop()
                        neighbor_x = pixel['x']
                        neighbor_y = pixel['y']
                        # check left pixel
                        if neighbor_x-1 >= 0 and not label[neighbor_y][neighbor_x-1] and abs(now_intensity-int(img[neighbor_y][neighbor_x-1])) <= dis:
                            neighbor_pixel = {'x':neighbor_x-1, 'y':neighbor_y}
                            region.append(neighbor_pixel)
                            component.append(neighbor_pixel)
                            label[neighbor_y][neighbor_x-1] = True
                        # check top pixel
                        if neighbor_y-1 >= 0 and not label[neighbor_y-1][neighbor_x] and abs(now_intensity-int(img[neighbor_y-1][neighbor_x])) <= dis:
                            neighbor_pixel = {'x':neighbor_x, 'y':neighbor_y-1}
                            region.append(neighbor_pixel)
                            component.append(neighbor_pixel)
                            label[neighbor_y-1][neighbor_x] = True
                        # check right pixel
                        if neighbor_x+1 < cols and not label[neighbor_y][neighbor_x+1] and abs(now_intensity-int(img[neighbor_y][neighbor_x+1])) <= dis:
                            neighbor_pixel = {'x':neighbor_x+1, 'y':neighbor_y}
                            region.append(neighbor_pixel)
                            component.append(neighbor_pixel)
                            label[neighbor_y][neighbor_x+1] = True  
                        # check bot pixel
                        if neighbor_y+1 < rows and not label[neighbor_y+1][neighbor_x] and abs(now_intensity-int(img[neighbor_y+1][neighbor_x])) <= dis:
                            neighbor_pixel = {'x':neighbor_x, 'y':neighbor_y+1}
                            region.append(neighbor_pixel)
                            component.append(neighbor_pixel)
                            label[neighbor_y+1][neighbor_x] = True

                    components.append(component)
    # img type is color
    elif seed_list is not None and color == 'rgb':
        pca_min = 9999
        pca_max = -9999

        while len(seed_list) != 0:
            #print len(seed_list)
            # BFS for seed
            now_pixel = seed_list.pop(0)
            y = now_pixel[OFFSET_y]
            x = now_pixel[OFFSET_x]
            #now_color = now_pixel[OFFSET_B:OFFSET_B+3]

            if not label[y][x]:
                # to count mean dynamically

                #buffer_count = 0
                #buffer_count = 1
                train_mean = now_pixel[OFFSET_B:OFFSET_B+3]
                #sum_b = 0
                #sum_g = 0
                #sum_r = 0
                sum_b = now_pixel[OFFSET_B]
                sum_g = now_pixel[OFFSET_G]
                sum_r = now_pixel[OFFSET_R]
                meanArray = np.array(train_mean)
                label[y][x] = True
                region = []
                component = []
                region.append(now_pixel)
                '''
                # check left pixel
                if x-1 >= 0 and not label[y][x-1]:
                    neighbor_pixel = get_pixel(y, x-1, img[y][x-1], img_ycrcb[y][x-1])
                    if distance(train_mean, neighbor_pixel['color']) <= dis:
                        region.append(neighbor_pixel)
                        component.append(neighbor_pixel)
                        label[y][x-1] = True
                        buffer_count += 1
                        sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['color'], buffer_count, buffer_size, train_mean)
                        if not (pca is None):
                            pca_value = pca.transform(neighbor_pixel['color'])
                            if pca_value < pca_min:
                                pca_min = pca_value
                            if pca_value > pca_max:
                                pca_max = pca_value
                # check top pixel
                if y-1 >= 0 and not label[y-1][x]:
                    neighbor_pixel = get_pixel(y-1, x, img[y-1][x], img_ycrcb[y-1][x])
                    if distance(train_mean, neighbor_pixel['color']) <= dis:
                        region.append(neighbor_pixel)
                        component.append(neighbor_pixel)
                        label[y-1][x] = True       
                        buffer_count += 1
                        sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['color'], buffer_count, buffer_size, train_mean)        
                        if not (pca is None):
                            pca_value = pca.transform(neighbor_pixel['color'])
                            if pca_value < pca_min:
                                pca_min = pca_value
                            if pca_value > pca_max:
                                pca_max = pca_value                
                # check right pixel
                if x+1 < cols and not label[y][x+1]:
                    neighbor_pixel = get_pixel(y, x+1, img[y][x+1], img_ycrcb[y][x+1])
                    if distance(train_mean, neighbor_pixel['color']) <= dis:
                        region.append(neighbor_pixel)
                        component.append(neighbor_pixel)
                        label[y][x+1] = True
                        buffer_count += 1
                        sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['color'], buffer_count, buffer_size, train_mean)
                        if not (pca is None):
                            pca_value = pca.transform(neighbor_pixel['color'])
                            if pca_value < pca_min:
                                pca_min = pca_value
                               #print("(%d)--- %s seconds ---" % (buffer_count, time.time() - startTime))             if pca_value > pca_max:
                                pca_max = pca_value                
                # check bot pixel
                if y+1 < rows and not label[y+1][x]:
                    neighbor_pixel = get_pixel(y+1, x, img[y+1][x], img_ycrcb[y+1][x])
                    if distance(train_mean, neighbor_pixel['color']) <= dis:
                        region.append(neighbor_pixel)
                        component.append(neighbor_pixel)
                        label[y+1][x] = True
                        buffer_count += 1
                        sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['color'], buffer_count, buffer_size, train_mean)
                        if not (pca is None):
                              #print("(%d)--- %s seconds ---" % (buffer_count, time.time() - startTime))              pca_value = pca.transform(neighbor_pixel['color'])
                            if pca_value < pca_min:
                                pca_min = pca_value
                            if pca_value > pca_max:
                                pca_max = pca_value                
                '''
                while len(region) != 0:
                    pixel = region.pop(0)
                    component.append(pixel)
                    neighbor_x = pixel[OFFSET_x]
                    neighbor_y = pixel[OFFSET_y]
                    
                    # check left pixel
                    if neighbor_x-1 >= 0 and not label[neighbor_y][neighbor_x-1]:
                        neighbor_pixel = get_pixel(neighbor_y, neighbor_x-1, img[neighbor_y][neighbor_x-1], img_ycrcb[neighbor_y][neighbor_x-1])
                        if distance(train_mean, neighbor_pixel[OFFSET_B:OFFSET_B+3]) <= dis:
                            region.append(neighbor_pixel)
                            #component.append(neighbor_pixel)
                            label[neighbor_y][neighbor_x-1] = True
                            np.concatenate((meanArray, neighbor_pixel[OFFSET_B:OFFSET_B+3]), axis=0)
                            #buffer_count += 1
                            #sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel[OFFSET_B:OFFSET_B+3], buffer_count, buffer_size, train_mean)
                            if not (pca is None):
                                pca_value = pca.transform(neighbor_pixel[OFFSET_B:OFFSET_B+3])
                                pca_min = min(pca_value, pca_min)
                                pca_max = max(pca_value, pca_max)
                    # check top pixel
                    if neighbor_y-1 >= 0 and not label[neighbor_y-1][neighbor_x]:
                        neighbor_pixel = get_pixel(neighbor_y-1, neighbor_x, img[neighbor_y-1][neighbor_x], img_ycrcb[neighbor_y-1][neighbor_x])
                        if distance(train_mean, neighbor_pixel[OFFSET_B:OFFSET_B+3]) <= dis:
                            region.append(neighbor_pixel)
                            #component.append(neighbor_pixel)
                            label[neighbor_y-1][neighbor_x] = True
                            np.concatenate((meanArray, neighbor_pixel[OFFSET_B:OFFSET_B+3]), axis=0)
                            #buffer_count += 1
                            #sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel[OFFSET_B:OFFSET_B+3], buffer_count, buffer_size, train_mean)
                            if not (pca is None):
                                pca_value = pca.transform(neighbor_pixel[OFFSET_B:OFFSET_B+3])
                                pca_min = min(pca_value, pca_min)
                                pca_max = max(pca_value, pca_max)
                    # check right pixel
                    if neighbor_x+1 < cols and not label[neighbor_y][neighbor_x+1]:
                        neighbor_pixel = get_pixel(neighbor_y, neighbor_x+1, img[neighbor_y][neighbor_x+1], img_ycrcb[neighbor_y][neighbor_x+1])
                        if distance(train_mean, neighbor_pixel[OFFSET_B:OFFSET_B+3]) <= dis:
                            region.append(neighbor_pixel)
                            #component.append(neighbor_pixel)
                            label[neighbor_y][neighbor_x+1] = True
                            np.concatenate((meanArray, neighbor_pixel[OFFSET_B:OFFSET_B+3]), axis=0)
                            #buffer_count += 1
                            #sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel[OFFSET_B:OFFSET_B+3], buffer_count, buffer_size, train_mean)
                            if not (pca is None):
                                pca_value = pca.transform(neighbor_pixel[OFFSET_B:OFFSET_B+3])
                                pca_min = min(pca_value, pca_min)
                                pca_max = max(pca_value, pca_max)
                    # check bot pixel
                    if neighbor_y+1 < rows and not label[neighbor_y+1][neighbor_x]:
                        neighbor_pixel = get_pixel(neighbor_y+1, neighbor_x, img[neighbor_y+1][neighbor_x], img_ycrcb[neighbor_y+1][neighbor_x])
                        if distance(train_mean, neighbor_pixel[OFFSET_B:OFFSET_B+3]) <= dis:
                            region.append(neighbor_pixel)
                            #component.append(neighbor_pixel)
                            label[neighbor_y+1][neighbor_x] = True
                            np.concatenate((meanArray, neighbor_pixel[OFFSET_B:OFFSET_B+3]), axis=0)
                            #buffer_count += 1
                            #sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel[OFFSET_B:OFFSET_B+3], buffer_count, buffer_size, train_mean)
                            if not (pca is None):
                                pca_value = pca.transform(neighbor_pixel[OFFSET_B:OFFSET_B+3])
                                pca_min = min(pca_value, pca_min)
                                pca_max = max(pca_value, pca_max)
                #if buffer_count != 0:
                #    train_mean = [float(sum_b)/buffer_count, float(sum_g)/buffer_count, float(sum_r)/buffer_count]

                train_means.append(np.mean(meanArray))
                #train_means.append(train_mean)
                components.append(component)
    elif color == 'ycrcb':
        if not (seed_list is None):        
            while len(seed_list) != 0:
                #print len(seed_list)
                # BFS for seed
                now_pixel = seed_list.pop(0)
                y = now_pixel['y']
                x = now_pixel['x']
                now_color = now_pixel['ycrcb']

                if not label[y][x]:
                    # to count mean dynamically
                    buffer_count = 0
                    train_mean = now_color
                    sum_b = 0
                    sum_g = 0
                    sum_r = 0

                    label[y][x] = True
                    region = []
                    component = []
                    component.append(now_pixel)

                    # check left pixel
                    if x-1 >= 0 and not label[y][x-1]:
                        neighbor_pixel = get_pixel(y, x-1, img[y][x-1], img_ycrcb[y][x-1])
                        if distance(train_mean, neighbor_pixel['ycrcb']) <= dis:
                            region.append(neighbor_pixel)
                            component.append(neighbor_pixel)
                            label[y][x-1] = True
                            buffer_count += 1
                            sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['ycrcb'], buffer_count, buffer_size, train_mean)
                    # check top pixel
                    if y-1 >= 0 and not label[y-1][x]:
                        neighbor_pixel = get_pixel(y-1, x, img[y-1][x], img_ycrcb[y-1][x])
                        if distance(train_mean, neighbor_pixel['ycrcb']) <= dis:
                            region.append(neighbor_pixel)
                            component.append(neighbor_pixel)
                            label[y-1][x] = True       
                            buffer_count += 1
                            sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['ycrcb'], buffer_count, buffer_size, train_mean)
                    # check right pixel
                    if x+1 < cols and not label[y][x+1]:
                        neighbor_pixel = get_pixel(y, x+1, img[y][x+1], img_ycrcb[y][x+1])
                        if distance(train_mean, neighbor_pixel['ycrcb']) <= dis:
                            region.append(neighbor_pixel)
                            component.append(neighbor_pixel)
                            label[y][x+1] = True
                            buffer_count += 1
                            sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['ycrcb'], buffer_count, buffer_size, train_mean)        
                    # check bot pixel
                    if y+1 < rows and not label[y+1][x]:
                        neighbor_pixel = get_pixel(y+1, x, img[y+1][x], img_ycrcb[y+1][x])
                        if distance(train_mean, neighbor_pixel['ycrcb']) <= dis:
                            region.append(neighbor_pixel)
                            component.append(neighbor_pixel)
                            label[y+1][x] = True
                            buffer_count += 1
                            sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['ycrcb'], buffer_count, buffer_size, train_mean)

                    while len(region) != 0:
                        pixel = region.pop(0)
                        neighbor_x = pixel['x']
                        neighbor_y = pixel['y']
                        # check left pixel
                        if neighbor_x-1 >= 0 and not label[neighbor_y][neighbor_x-1]:
                            neighbor_pixel = get_pixel(neighbor_y, neighbor_x-1, img[neighbor_y][neighbor_x-1], img_ycrcb[neighbor_y][neighbor_x-1])
                            if distance(train_mean, neighbor_pixel['ycrcb']) <= dis:
                                region.append(neighbor_pixel)
                                component.append(neighbor_pixel)
                                label[neighbor_y][neighbor_x-1] = True
                                buffer_count += 1
                                sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['ycrcb'], buffer_count, buffer_size, train_mean)    
                        # check top pixel
                        if neighbor_y-1 >= 0 and not label[neighbor_y-1][neighbor_x]:
                            neighbor_pixel = get_pixel(neighbor_y-1, neighbor_x, img[neighbor_y-1][neighbor_x], img_ycrcb[neighbor_y-1][neighbor_x])
                            if distance(train_mean, neighbor_pixel['ycrcb']) <= dis:
                                region.append(neighbor_pixel)
                                component.append(neighbor_pixel)
                                label[neighbor_y-1][neighbor_x] = True     
                                buffer_count += 1
                                sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['ycrcb'], buffer_count, buffer_size, train_mean)    
                        # check right pixel
                        if neighbor_x+1 < cols and not label[neighbor_y][neighbor_x+1]:
                            neighbor_pixel = get_pixel(neighbor_y, neighbor_x+1, img[neighbor_y][neighbor_x+1], img_ycrcb[neighbor_y][neighbor_x+1])
                            if distance(train_mean, neighbor_pixel['ycrcb']) <= dis:
                                region.append(neighbor_pixel)
                                component.append(neighbor_pixel)
                                label[neighbor_y][neighbor_x+1] = True 
                                buffer_count += 1
                                sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['ycrcb'], buffer_count, buffer_size, train_mean)
                        # check bot pixel
                        if neighbor_y+1 < rows and not label[neighbor_y+1][neighbor_x]:
                            neighbor_pixel = get_pixel(neighbor_y+1, neighbor_x, img[neighbor_y+1][neighbor_x], img_ycrcb[neighbor_y+1][neighbor_x])
                            if distance(train_mean, neighbor_pixel['ycrcb']) <= dis:
                                region.append(neighbor_pixel)
                                component.append(neighbor_pixel)
                                label[neighbor_y+1][neighbor_x] = True
                                buffer_count += 1
                                sum_b, sum_g, sum_r, train_mean = count_mean(sum_b, sum_g, sum_r, neighbor_pixel['ycrcb'], buffer_count, buffer_size, train_mean)

                    if buffer_count != 0:
                        train_mean = [float(sum_b)/buffer_count, float(sum_g)/buffer_count, float(sum_r)/buffer_count]
                    train_means.append(train_mean)
                    components.append(component)    
    
    #print pca_min, pca_max
    return train_means, components, pca_min, pca_max


def count_mean(sum_b, sum_g, sum_r, pixel_color, buffer_count, buffer_size, train_mean):
    sum_b += int(pixel_color[0])
    sum_g += int(pixel_color[1])
    sum_r += int(pixel_color[2])
    if buffer_count % buffer_size == 0:
        train_mean = [float(sum_b)/buffer_count, float(sum_g)/buffer_count, float(sum_r)/buffer_count]

    return sum_b, sum_g, sum_r, train_mean

def get_pixel(y, x, color, color_ycrcb):
    # [x, y, B, G, R, Y, Cr, Cb]
    return [x, y, color[0], color[1], color[2], color_ycrcb[0], color_ycrcb[1], color_ycrcb[2]]


def distance(p1, p2):
    return math.sqrt(math.pow(int(p1[0])-int(p2[0]), 2) + math.pow(int(p1[1])-int(p2[1]), 2) + math.pow(int(p1[2])-int(p2[2]), 2))