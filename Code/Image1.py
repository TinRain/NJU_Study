# coding=utf-8

import json
import os

import cv2
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
import time
from aip import AipOcr

# 图片处理类
class Image(object):
    API_URL = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/ocr'
    timeCostForOCR = 0
    isRerun = False

    def __init__(self, image_path):
        self.img = cv2.imread(image_path)
        self.image_path = image_path
        self.image_name = image_path.replace('/','#')
        self.original_image = cv2.imread(image_path)
        self.original_image_width = self.original_image.shape[1]
        self.original_image_height = self.original_image.shape[2]

    # 获取图中轮廓信息
    def get_contour_information(self):
        contour_list = []
        gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        canny = cv2.Canny(thresh, 5, 500)
        kernel = np.ones((3, 3), np.uint8)
        dilate = cv2.dilate(canny, kernel, iterations=2)  # 扩大轮廓范围
        method_contour = cv2.RETR_LIST
        _, contours, hierarchy = cv2.findContours(dilate, method_contour, cv2.CHAIN_APPROX_SIMPLE)
        for index in range(len(contours)):
            box = {}
            x, y, w, h = cv2.boundingRect(contours[index])
            box['x'] = x
            box['y'] = y
            box['w'] = w
            box['h'] = h
            box['type'] = 'non-text'
            contour_list.append(box)
        return contour_list

    # 过滤图中轮廓信息
    def get_filtered_contour(self):
        _contour_list = self.get_contour_information()
        temp = [box for box in _contour_list if not (box['h'] < 15 or (box['y']> 150 and box['w'] < 15)
                                                     or box['y']<50
                                                     )]

        return self.filter_contour(temp, rate=0.6)

    # 去除被text block覆盖的元素轮廓
    # 去除位于两个text block间的轮廓
    def get_filtered_contour_by_text(self):
        _contour_list = self.get_filtered_contour()
        _text_block = self.get_text_block()
        contour_list = []
        for contour in _contour_list:
            label = False  # 用于标记该contour是否冲突
            for word1 in _text_block:
                if self.contour_is_covered(contour, word1, rate=0.6) and contour['h']<150:
                    label = True
            if not label:
                contour_list.append(contour)
        return contour_list

    # 使用api获取ocr识别结果
    '''
    def get_text_information(self):
        if os.path.exists('./json/' + self.image_name + '_json.txt') and "temp.png" not in self.image_name and not ('_#' in self.image_name and Image.isRerun):
            if os.path.exists(
                                    './Timejson/' + self.image_name + '_Timejson.txt') and "temp.png" not in self.image_name and not (
                    '_#' in self.image_name and Image.isRerun) and "_" in self.image_name:
                with open('./Timejson/' + self.image_name + '_Timejson.txt', 'r') as f:
                    cachedTime = float(f.readlines()[0].strip())
                    time.sleep(cachedTime)


            with open('./json/' + self.image_name + '_json.txt', 'r') as f:
                the_json = json.load(f)
                return the_json
        else:
            timeBefore = datetime.now()
            with open(self.image_path, 'rb') as f:
                img_data = f.read()

                header = {
                    'Ocp-Apim-Subscription-Key': '709f1f0aed294878a798f3a42068407f',
                    'Content-Type': 'application/octet-stream'
                }

                params = {
                    'language': 'unk',
                    'detectOrientation ': 'true'
                }

                try:
                    r = requests.post(self.API_URL,
                                      params=params,
                                      headers=header,
                                      data=img_data)

                    r.raise_for_status()

                    data = r.json()
                    with open('./json/' + self.image_name + '_json.txt', 'w') as fw:
                        json.dump(data, fw)

                    if "_" not in self.image_name:
                        return data

                    with open('./Timejson/' + self.image_name + '_Timejson.txt', 'w') as fwTime:
                        timeAfter = datetime.now()
                        deltaTime = (timeAfter - timeBefore).seconds + (timeAfter - timeBefore).microseconds / 1000000.0
                        fwTime.write(str(deltaTime))
                    return data

                except requests.HTTPError as e:
                    print('HTTP error occurred: {}'.format(e))

                except Exception as e:
                    print('Error occurred: {}'.format(e))

    '''
    def get_text_information(self):
        #json_path = Config.IMAGE_PARSE_JSON_PATH + Config.APP_NAME + '/' + self.img_name + '_json.txt'

        if os.path.exists('./json/' + self.image_name + '_json.txt') and "temp.png" not in self.image_name and not (
                '_#' in self.image_name and Image.isRerun):
            if os.path.exists(
                                    './Timejson/' + self.image_name + '_Timejson.txt') and "temp.png" not in self.image_name and not (
                            '_#' in self.image_name and Image.isRerun) and "_" in self.image_name:
                with open('./Timejson/' + self.image_name + '_Timejson.txt', 'r') as f:
                    cachedTime = float(f.readlines()[0].strip())
                    time.sleep(cachedTime)

            with open('./json/' + self.image_name + '_json.txt', 'r') as f:
                the_json = json.load(f)
                return the_json

        else:
            timeBefore = datetime.now()
            with open(self.image_path, 'rb') as img_f:
                img_data = img_f.read()
                options = {}
                options["recognize_granularity"] = "big"
                options["language_type"] = "CHN_ENG"
                options["detect_direction"] = "true"
                options["detect_language"] = "true"
                options["vertexes_location"] = "false"
                options["probability"] = "true"

                config = {
                    'appId': '10930258',
                    'apiKey': '	k8s4mTA5DnAIQW52xGQ4rs9F',
                    'secretKey': '5b8S7v4SvTifhQw776LMvnYHWtelRfu1'
                }
                client = AipOcr(**config)

                try:
                    data = client.general(img_data, options)
                    with open('./json/' + self.image_name + '_json.txt', 'w') as fw:
                        json.dump(data, fw)

                    if "_" not in self.image_name:
                        return data

                    with open('./Timejson/' + self.image_name + '_Timejson.txt', 'w') as fwTime:
                        timeAfter = datetime.now()
                        deltaTime = (timeAfter - timeBefore).seconds + (timeAfter - timeBefore).microseconds / 1000000.0
                        fwTime.write(str(deltaTime))
                    return data


                except Exception as e:
                    print('Error occurred: {}'.format(e))


    def divideLineWord(self,lineList,divideParameter=32):
        returnList = []
        indexList = []
        for index, word in enumerate(lineList['words']):
            if index == 0:
                continue
            word_countour_size1 = lineList['words'][index-1]['boundingBox'].split(',')
            word_countour_size2 = word['boundingBox'].split(',')

            if int(word_countour_size2[0])-int(word_countour_size1[0])-int(word_countour_size1[2])>divideParameter:
                indexList.append(index)
        for index, indexValue in enumerate(indexList):
            if len(returnList)==0:
                returnList.append(lineList['words'][0:indexValue])
            else:
                returnList.append(lineList['words'][indexList[index-1]:indexValue])
            if index == len(indexList)-1:
                returnList.append(lineList['words'][indexValue:])
        if len(indexList)==0:
            returnList.append(lineList['words'][0:])
        return returnList






    # 获取位于同一行的文字
    # 返回结果为一行中水平距离足够接近的文本信息
    '''
    def get_text_block(self):
        timeBefore = datetime.now()


        _json = self.get_text_information()


        all_text_block = []
        if _json is None:
            return all_text_block
        for region in _json['regions']:
            for line in region['lines']:


                # 当只有一个单词且单词长度为1时，认为其假正
                if not (len(line['words']) == 1 and len(line['words'][0]['text']) == 1):

                    dividedLineList = self.divideLineWord(line)

                    for dividedLine in dividedLineList:
                        big_box = {
                            'type': 'text'
                        }
                        text = ''
                        big_box_x, big_box_y, big_box_max_width, big_box_max_height = 100000, 100000, 0, 0
                        for word in dividedLine:
                            word_countour_size = word['boundingBox'].split(',')
                            big_box_x = min(big_box_x, int(word_countour_size[0]))
                            big_box_y = min(big_box_y, int(word_countour_size[1]))
                            big_box_max_width = max(big_box_max_width, int(word_countour_size[0]) + int(word_countour_size[2]))
                            big_box_max_height = max(big_box_max_height,
                                                int(word_countour_size[1]) + int(word_countour_size[3]))
                            text += word['text']
                            text += ' '
                        text = text[:-1]
                        if len(text) >= 1:
                            big_box['text'] = text
                            big_box['x'] = big_box_x
                            big_box['y'] = big_box_y
                            big_box['w'] = big_box_max_width - big_box_x
                            big_box['h'] = big_box_max_height - big_box_y
                            all_text_block.append(big_box)

        timeAfter = datetime.now()
        deltaTime = (timeAfter-timeBefore).seconds+(timeAfter-timeBefore).microseconds/1000000.0
        Image.timeCostForOCR = Image.timeCostForOCR + deltaTime

        return all_text_block

    '''
    def get_text_block(self):
        timeBefore = datetime.now()
        _json = self.get_text_information()
        if _json is None:
            print('ocr error')
            return []
        text_blocks = []
        for word_result in _json['words_result']:
            if word_result['probability']['average'] < 0.5 or len(word_result['words']) <= 1:
                # 去除置信度较低的提取结果
                continue
            text_block = {
                'x': word_result['location']['left'],
                'y': word_result['location']['top'],
                'w': word_result['location']['width'],
                'h': word_result['location']['height'],
                'text': word_result['words'],
                'type': 'text'
            }
            text_blocks.append(text_block)
        #self.draw_picture(text_blocks, self.img)

        timeAfter = datetime.now()
        deltaTime = (timeAfter - timeBefore).seconds + (timeAfter - timeBefore).microseconds / 1000000.0
        Image.timeCostForOCR = Image.timeCostForOCR + deltaTime
        return text_blocks

    # return time cost with the level of minutes
    def getOCRTimeCost(self):
        return Image.timeCostForOCR/60.0

    # 消除存在于两个text block中的轮廓
    # 对于位于两个text block中的轮廓将其合并进text block并扩大text block的范围
    def delete_contour_between_text_block(self):
        _contour_list = self.get_filtered_contour_by_text()
        _text_block = self.get_text_block()
        _text_block = sorted(_text_block, key=lambda _text_block:_text_block['y'])
        new_contour_list, new_text_block = [], []
        for contour in _contour_list:
            label = True
            for index1, text_block1 in enumerate(_text_block):
                if index1 == len(_text_block) - 1:
                    if text_block1 not in new_text_block:
                        new_text_block.append(text_block1)
                    continue
                text_block2 = _text_block[index1 + 1]
                if text_block1['x'] <= contour['x'] <= text_block1['x'] + text_block1['w'] \
                        and text_block2['x'] <= contour['x'] <= text_block2['x'] + text_block2['w'] \
                        and text_block1['y'] <= contour['y'] <= text_block2['y']:
                    label = False
                    text_block1['h'] = contour['y'] + contour['h'] - text_block1['y'] + 10
                if text_block1 not in new_text_block:
                    new_text_block.append(text_block1)
            if label:
                new_contour_list.append(contour)
        return new_contour_list, new_text_block

    # 将垂直距离足够接近的轮廓合并
    def merge_text_block_vertical(self):
        contour_list, text_block = self.delete_contour_between_text_block()
        new_text_block = []
        labels = [False] * len(text_block)  # 用于标记该text block是否已经被合并
        for index1, text_block1 in enumerate(text_block):
            if labels[index1]:
                continue
            temp_text_block = {
                'x': text_block1['x'],
                'y': text_block1['y'],
                'w': text_block1['w'],
                'h': text_block1['h'],
                'container': [text_block1],
                'type': 'text'
            }
            labels[index1] = True
            original_y = text_block1['y']
            for index2, text_block2 in enumerate(text_block):
                if labels[index2]:
                    continue
                # 两个轮廓的垂直距离小于一个阀值且位于同一水平线上
                if abs(text_block2['y'] - (temp_text_block['y'] + temp_text_block['h'])) < 30 \
                        and abs(text_block2['x'] - temp_text_block['x']) <= 5:
                    temp_text_block['h'] = text_block2['y'] + text_block2['h'] - original_y
                    temp_text_block['w'] = max(temp_text_block['w'], text_block2['w'])
                    temp_text_block['container'].append(text_block2)
                    labels[index2] = True
            new_text_block.append(temp_text_block)
        return contour_list, self.filter_contour(new_text_block)

    # 将位于同一水平线上的轮廓合并进一个list
    # todo：如何控制距离阀值，将不应该出现的轮廓剔除
    def merge_contour_horizontal(self):
        _contour_list, _text_block = self.merge_text_block_vertical()
        contours = _contour_list + _text_block
        labels = [False] * len(contours)
        contour_list = []
        #print(self.original_image_width)
        for index1, contour1 in enumerate(contours):
            temp = []
            if labels[index1]:
                continue
            labels[index1] = True
            temp.append(contour1)
            for index2, contour2 in enumerate(contours):
                if not labels[index2] and abs(contour2['y'] - contour1['y']) < 30:
                    if (contour2['x'] < contour1['x']
                            and abs(contour1['x'] - (contour2['x'] + contour2['w'])) < self.original_image_width / 2) \
                            or (contour1['x'] <= contour2['x']
                                and abs(contour2['x'] - (contour1['x'] + contour1['w'])) < self.original_image_width / 2):
                        temp.append(contour2)
                        labels[index2] = True
            if len(temp) != 0:
                contour_list.append(temp)
        return contour_list

    # 根据排序后的轮廓列表得到列表项
    def get_list_item(self):
        result = []
        _contour_list = self.merge_contour_horizontal()
        #print(_contour_list)
        for temp_list in _contour_list:
            if len(temp_list) < 0:
                continue
            # 因为是排过序的list，list中的一项即为y坐标接近的多个轮廓
            temp = {
                'x': 0,
                'y': 0,
                'w': 0,
                'h': 0,
                'container': temp_list
            }
            min_x, min_y = temp_list[0]['x'], temp_list[0]['y']
            min_w, min_h = 0, 0
            for contour in temp_list:
                if contour['x'] < min_x:
                    min_x = contour['x']
                    min_w = max(min_w, (contour['x'] + contour['w'] - min_x))
                else:
                    min_w = max(min_w, (contour['x'] + contour['w'] - min_x))
                if contour['y'] < min_y:
                    min_y = contour['y']
                    min_h = max(min_h, (contour['y'] + contour['h'] - min_y))
                else:
                    min_h = max(min_h, (contour['y'] + contour['h'] - min_y))
            temp['x'] = min_x - 5
            temp['y'] = min_y - 5
            temp['w'] = min_w + 10
            temp['h'] = min_h + 10
            if temp not in result:
                result.append(temp)
        # 过滤那些只含非文本元素的item
        final_result = []
        for temp in result:
            for son in temp['container']:
                if son['type'] != 'non-text' and temp not in final_result:
                        final_result.append(temp)
        #print(final_result)
        return final_result

    # 定义列表
    def identify_list_view(self):
        list_item = self.get_list_item()
        #print(list_item)
        item_labels = [-1] * len(list_item)  # 用于标记结构相同的列表项
        for index1, contour1 in enumerate(list_item):
            if item_labels[index1] != -1:
                continue
            item_labels[index1] = index1
            for index2, contour2 in enumerate(list_item):
                if item_labels[index2] != -1:
                    continue
                if self.contour_structure_identical(contour1, contour2):
                    item_labels[index2] = index1
        #print(item_labels)
        for item in set(item_labels):
            if item_labels.count(item) >= len(list_item) / 2:
                list_item_result = [list_item[index] for index in range(len(item_labels)) if item_labels[index] == item]
                print(list_item_result)
                #self.draw_picture(list_item_result, self.original_image)
                return True, list_item_result
        return False, None

    # 判断两个item的结构是否相等
    # 处理到text block层次
    def contour_structure_identical(self, contour1, contour2):
        # step1: 如果有type，则看type是否相等
        if (('type' in contour1.keys()) and ('type' in contour2.keys()) and (contour1['type'] == contour2['type'])) or \
                (('type' not in contour1.keys()) and ('type' not in contour2.keys())):
            # step2: 再看两个contour是否含有container，如果含有再看container的长度是否相等
            if (('container' not in contour1.keys()) and ('container' not in contour2.keys())) or (
                        'container' in contour1.keys()) and ('container' in contour2.keys()) and \
                            len(contour1['container']) == len(contour2['container']):
                # step3: 递归看container的内容的结构是否相等
                if ('container' not in contour1.keys()) and ('container' not in contour2.keys()):
                    return True
                for index1, child1 in enumerate(contour1['container']):
                    if not self.contour_structure_identical(child1, contour2['container'][index1]):
                        return False
            else:
                return False
        else:
            return False
        return True

    # 去除重叠的轮廓
    def filter_contour(self, contour_list, rate=0.8):
        result = []
        for contour1 in contour_list:
            if contour1['y'] > 1800:
                continue
            fail = 1
            for contour2 in contour_list:
                if self.contour_is_covered(contour1, contour2, rate) \
                        and contour1['h'] * contour1['w'] < contour2['h'] * contour2['w'] and contour2['w']<0.3*self.original_image_width:
                    fail = 0
            if fail == 1:
                result.append(contour1)
        return result

    def getList(self):
        return self.get_text_block(),self.get_filtered_contour()

    # 判断两个轮廓是否有重叠
    @staticmethod
    def contour_is_covered(contour1, contour2, rate=0.8):
        x = max(contour1['x'], contour2['x'])
        x_ = min(contour1['x'] + contour1['w'], contour2['x'] + contour2['w'])
        y = max(contour1['y'], contour2['y'])
        y_ = min(contour1['y'] + contour1['h'], contour2['y'] + contour2['h'])
        area = min(contour1['w'] * contour1['h'], contour2['w'] * contour2['h'])
        if x_ > x and y_ > y and (x_ - x) * (y_ - y) > rate * area:
            return True
        return False

    # 用来查看轮廓提取结果
    @staticmethod
    def draw_picture(contour_list, image):
        for box in contour_list:
            p1 = (box['x'], box['y'])
            p2 = (box['x'] + box['w'], box['y'] + box['h'])
            image = cv2.rectangle(image, p1, p2, (255, 0, 0), 2)
        plt.subplot(121), plt.imshow(image, cmap='gray')
        plt.title('edge Image'), plt.xticks([]), plt.yticks([])
        plt.show()

    @staticmethod
    def filter_matches(kp1, kp2, matches, ratio=0.75):
        mkp1, mkp2 = [], []
        for m in matches:
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                m = m[0]
                mkp1.append(kp1[m.queryIdx])
                mkp2.append(kp2[m.trainIdx])
        p1 = np.float32([kp.pt for kp in mkp1])
        p2 = np.float32([kp.pt for kp in mkp2])
        kp_pairs = zip(mkp1, mkp2)
        return p1, p2, kp_pairs

    @staticmethod
    def explore_match(win, img1, img2, kp_pairs, initbox, status=None, H=None):
        similarPoints = []
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        vis = np.zeros((max(h1, h2), w1 + w2), np.uint8)
        vis[:h1, :w1] = img1
        vis[:h2, w1:w1 + w2] = img2
        vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

        if H is not None:
            corners = np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
            corners = np.int32(cv2.perspectiveTransform(corners.reshape(1, -1, 2), H).reshape(-1, 2) + (w1, 0))
            cv2.polylines(vis, [corners], True, (255, 255, 255))

        if status is None:
            status = np.ones(len(list(kp_pairs)), np.bool)

        p1 = np.int32([kpp[0].pt for kpp in kp_pairs])
        p2 = np.int32([kpp[1].pt for kpp in kp_pairs]) + (w1, 0)

        green = (0, 255, 0)
        red = (0, 0, 255)
        white = (255, 255, 255)
        kp_color = (51, 103, 236)
        for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
            if y1 > initbox['y'] and y1 < initbox['y'] + initbox['h'] and x1 > initbox['x'] and x1 < initbox['x'] + \
                    initbox[
                        'w'] and (y2 > 50 or h1<w1):

                if inlier:
                    similarPoints.append((x2 - w1, y2))
                    col = green
                    cv2.circle(vis, (x1, y1), 2, col, -1)
                    cv2.circle(vis, (x2, y2), 2, col, -1)
                else:
                    col = red
                    r = 2
                    thickness = 3
                    cv2.line(vis, (x1 - r, y1 - r), (x1 + r, y1 + r), col, thickness)
                    cv2.line(vis, (x1 - r, y1 + r), (x1 + r, y1 - r), col, thickness)
                    cv2.line(vis, (x2 - r, y2 - r), (x2 + r, y2 + r), col, thickness)
                    cv2.line(vis, (x2 - r, y2 + r), (x2 + r, y2 - r), col, thickness)
        vis0 = vis.copy()
        for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
            if y1 > initbox['y'] and y1 < initbox['y'] + initbox['h'] and x1 > initbox['x'] and x1 < initbox['x'] + \
                    initbox[
                        'w'] and inlier and (y2 > 50 or h1<w1):
                cv2.line(vis, (x1, y1), (x2, y2), green)
        # cv2.imwrite("12.png", vis)
        return similarPoints

    @staticmethod
    def getSift(image1, image2, initBox):
        img1 = cv2.imread(image1)
        img2 = cv2.imread(image2)

        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        sift = cv2.AKAZE_create()

        kp1, des1 = sift.detectAndCompute(img1_gray, None)
        kp2, des2 = sift.detectAndCompute(img2_gray, None)
        if des2 is None:
            print("image simple with none")
            return []
        # BFmatcher with default parms
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        matches = bf.knnMatch(des1, des2, k=2)
        p1, p2, kp_pairs = Image.filter_matches(kp1, kp2, matches, ratio=0.75)

        temp = list(kp_pairs)

        if len(temp) == 0:
            # print("no same element")
            return []
        similar = Image.explore_match('matches', img1_gray, img2_gray, temp, initBox)
        # img3 = cv2.drawMatchesKnn(img1_gray,kp1,img2_gray,kp2,good[:10],flag=2)

        return similar

def draw_picture1(image):
    p1 = (19, 286)
    p2 = (19 + 605, 286 + 500)
    image = cv2.rectangle(image, p1, p2, (255, 0, 0), 2)
    plt.subplot(121), plt.imshow(image, cmap='gray')
    plt.title('edge Image'), plt.xticks([]), plt.yticks([])
    plt.show()

if __name__ == '__main__':
    #Image.getSift('','')
    test = Image("img/sample1.png")
    #print(test.get_text_block())
    #text_block = test.get_text_block()
    #test.draw_picture(text_block, test.original_image)
    contour_list = test.get_filtered_contour()
    contour_list = test.get_filtered_contour_by_text()
    #contour_list = test.merge_contour_vertical()
    contour_list = test.get_text_block()
    print(contour_list)
    #test.draw_picture()
    #print contour_list[1]
    test.draw_picture(contour_list, test.original_image)
    #draw_picture1(test.original_image)