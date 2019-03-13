import Image1
import cv2
import os
from datetime import datetime


class Map(object):
    timeCostForMap = 0

    def __init__(self, image1, image2, initbox):
        self.image1 = image1
        self.image2 = image2

        # if not initbox.has_key('x'):
        if not 'x' in initbox.keys():
            initbox = {'x': 0, 'y': 0, 'w': 1, 'h': 1}
        self.initbox = initbox

        self.Image1 = Image1.Image(image1)
        self.Image2 = Image1.Image(image2)

    def setScreenProperty(self):
        self.heightScreen, self.widthSreen = self.getScreenSize(self.image1)
        self.textLineList1 = self.Image1.get_text_block()
        self.textLineList2 = self.Image2.get_text_block()
        self.contourList1 = self.Image1.get_filtered_contour_by_text()
        self.contourList2 = self.Image2.get_filtered_contour_by_text()
        self.type1 = self.popWindowRecognize(self.image1, self.contourList1)
        self.type2 = self.popWindowRecognize(self.image2, self.contourList2)
        self.isText = 0

    def getScreenSize(self, image):
        image = cv2.imread(image)
        widthScreen = image.shape[0]
        heightScreen = image.shape[1]
        return widthScreen, heightScreen

    # recognize specific widgets
    def popWindowRecognize(self, image_, contourList):
        image = cv2.imread(image_)
        for contour in contourList:
            if contour['x'] + 0.5 * contour['w'] > 0.45 * self.widthSreen and contour['x'] + 0.5 * contour[
                'w'] < 0.55 * self.widthSreen and contour['w'] > 0.75 * self.widthSreen and contour[
                'w'] < 0.95 * self.widthSreen and abs(
                contour['y'] + 0.5 * contour['h'] - 0.5 * self.heightScreen) < 0.33 * self.heightScreen and contour[
                'h'] > 0.08 * self.heightScreen:
                # image = cv2.imread(image_)
                # imageCut = image[contour['y']:contour['y'] + contour['h'], contour['x']:contour['x'] + contour['w']]
                # print widthScreen
                # print heightScreen
                brightList = []
                leftSeperate = 0
                rightSeperate = self.widthSreen
                for xi in range(0, self.widthSreen):
                    temp = 0
                    for xj in range(contour['y'] + int(contour['h'] / 4), contour['y'] + int(3 * contour['h'] / 4)):
                        # set the pixel value decrease to 20%
                        temp = temp + 0.3 * image[xj, xi, 0] + 0.6 * image[xj, xi, 1] + 0.1 * image[xj, xi, 2]
                    ##print 2*temp/contour['h']
                    brightList.append(2 * temp / contour['h'])
                for i in range(1, self.widthSreen):
                    if brightList[i - 1] - brightList[i] > 120:
                        rightSeperate = i
                    if brightList[i] - brightList[i - 1] > 120:
                        leftSeperate = i
                # print ("left seperate:%d right seperate:%d" % (leftSeperate, rightSeperate))
                # return seperate
                if (leftSeperate == 0 and rightSeperate == self.widthSreen) or leftSeperate > rightSeperate:
                    continue
                else:
                    return 2

        for contour in contourList:
            if contour['x'] + 0.5 * contour['w'] > 0.45 * self.widthSreen and contour['x'] + 0.5 * contour[
                'w'] < 0.55 * self.widthSreen and contour['w'] > 0.75 * self.widthSreen and contour[
                'w'] < 0.95 * self.widthSreen and abs(
                contour['y'] + 0.5 * contour['h'] - 0.5 * self.heightScreen) < 0.2 * self.heightScreen and contour[
                'h'] > 0.1 * self.heightScreen:
                # image = cv2.imread(image_)
                ##print widthScreen
                ##print heightScreen
                brightList = []
                leftSeperate = 0
                rightSeperate = self.widthSreen
                for xi in range(0, self.widthSreen):
                    temp = 0
                    for xj in range(contour['y'], contour['y'] + contour['h']):
                        # set the pixel value decrease to 20%
                        temp = temp + 0.3 * image[xj, xi, 0] + 0.6 * image[xj, xi, 1] + 0.1 * image[xj, xi, 2]
                    ##print temp/contour['h']
                    brightList.append(temp / contour['h'])
                for i in range(1, self.widthSreen):
                    if brightList[i - 1] - brightList[i] > 120:
                        rightSeperate = i
                    if brightList[i] - brightList[i - 1] > 120:
                        leftSeperate = i
                ##print ("left seperate:%d right seperate:%d"%(leftSeperate,rightSeperate))
                # return seperate
                if (leftSeperate == 0 and rightSeperate == self.widthSreen) or leftSeperate > rightSeperate:
                    return 0
                else:
                    return 3

        return 0

    def rectanCover(self, box1, box2, rate=0.8):
        x = max(box1['x'], box2['x'])
        x_ = min(box1['x'] + box1['w'], box2['x'] + box2['w'])
        y = max(box1['y'], box2['y'])
        y_ = min(box1['y'] + box1['h'], box2['y'] + box2['h'])
        area = min(box1['w'] * box1['h'], box2['w'] * box2['h'])
        if x_ > x and y_ > y and (x_ - x) * (y_ - y) > rate * area:
            return True
        return False

    def setInitText(self):
        for text in self.textLineList1:
            if self.rectanCover(text, self.initbox, 0.3):
                self.initText = text['text']
                self.isText = 1

    def calculatorMappingFeature(self):
        xBridge = []
        for word1 in self.textLineList1:
            temp = 0
            for x in xBridge:
                if abs(word1['x'] - x) < 15:
                    temp = 1
                    break
            if temp == 1:
                continue
            elif word1['x'] > 0.33 * self.widthSreen and word1['y'] < 0.9 * self.heightScreen and word1[
                'y'] > 0.1 * self.heightScreen:
                xBridge.append(word1['x'])

        rightPattern1 = []
        for x in xBridge:
            rightPatternTemp = []
            for word1 in self.textLineList1:
                if word1['x'] - x < 100 and word1['x'] - x > -20 and word1['y'] > 30:
                    rightPatternTemp.append(word1)
                elif abs(word1['x'] - x) < 100 and word1['y'] > 30 and word1['x'] - x > -100 and (
                        'E ' in word1['text'] or '= ' in word1['text'] or 'B ' in word1['text'] or '@ ' in word1[
                    'text']):
                    rightPatternTemp.append(word1)

            if len(rightPatternTemp) > len(rightPattern1):
                rightPattern1 = rightPatternTemp

        xBridge = []
        for word1 in self.textLineList2:
            temp = 0
            for x in xBridge:
                if abs(word1['x'] - x) < 15:
                    temp = 1
                    break
            if temp == 1:
                continue
            elif word1['x'] > 0.33 * self.widthSreen and word1['y'] < 0.9 * self.heightScreen and word1[
                'y'] > 0.1 * self.heightScreen:
                xBridge.append(word1['x'])

        rightPattern2 = []
        for x in xBridge:
            rightPatternTemp = []
            for word1 in self.textLineList2:
                if word1['x'] - x < 100 and word1['x'] - x > -20 and word1['y'] > 30:
                    rightPatternTemp.append(word1)
                elif abs(word1['x'] - x) < 100 and word1['y'] > 30 and word1['x'] - x > -100 and (
                        'E ' in word1['text'] or '= ' in word1['text'] or 'B ' in word1['text'] or '@ ' in word1[
                    'text']):
                    rightPatternTemp.append(word1)
            if len(rightPatternTemp) > len(rightPattern2):
                rightPattern2 = rightPatternTemp

                # leftPattern
        xBridge = []
        for word1 in self.textLineList1:
            temp = 0
            for x in xBridge:
                if abs(word1['x'] - x) < 15:
                    temp = 1
                    break
            if temp == 1:
                continue
            elif word1['x'] < 0.33 * self.widthSreen and word1['y'] < 0.9 * self.heightScreen and word1[
                'y'] > 0.06 * self.heightScreen:
                xBridge.append(word1['x'])

        leftPattern1 = []
        for x in xBridge:
            leftPatternTemp = []
            for word1 in self.textLineList1:
                if abs(word1['x'] - x) < 110 and word1['y'] > 40 and word1['x'] < self.widthSreen / 5:
                    leftPatternTemp.append(word1)
                elif abs(word1['x'] - x) < 110 and word1['y'] > 40 and word1['x'] < self.widthSreen / 3 and 'E ' not in \
                        word1['text'] and '= ' not in word1['text'] and 'B ' not in word1['text'] and '@ ' not in word1[
                    'text']:
                    leftPatternTemp.append(word1)
            if len(leftPatternTemp) > len(leftPattern1):
                leftPattern1 = leftPatternTemp

        xBridge = []
        for word1 in self.textLineList2:
            temp = 0
            for x in xBridge:
                if abs(word1['x'] - x) < 15:
                    temp = 1
                    break
            if temp == 1:
                continue
            elif word1['x'] < 0.33 * self.widthSreen and word1['y'] < 0.9 * self.heightScreen and word1[
                'y'] > 0.06 * self.heightScreen:
                xBridge.append(word1['x'])

        leftPattern2 = []
        for x in xBridge:
            leftPatternTemp = []
            for word1 in self.textLineList2:
                if abs(word1['x'] - x) < 110 and word1['y'] > 40 and word1['x'] < self.widthSreen / 5:
                    leftPatternTemp.append(word1)
                elif abs(word1['x'] - x) < 110 and word1['y'] > 40 and word1['x'] < self.widthSreen / 3 and 'E ' not in \
                        word1['text'] and '= ' not in word1['text'] and 'B ' not in word1['text'] and '@ ' not in word1[
                    'text']:
                    leftPatternTemp.append(word1)

            if len(leftPatternTemp) > len(leftPattern2):
                leftPattern2 = leftPatternTemp

        # topPattern
        yBridge = []
        for word1 in self.textLineList1:
            temp = 0
            for y in yBridge:
                if abs(word1['y'] - y) < 15:
                    temp = 1
                    break
            if temp == 1:
                continue
            elif word1['y'] < 0.1 * self.heightScreen and word1['y'] > 30:
                yBridge.append(word1['y'])

        topPattern1 = []
        for y in yBridge:
            leftPatternTemp = []
            for word1 in self.textLineList1:
                if abs(word1['y'] - y) < 20 and len(word1['text']) != 1:
                    leftPatternTemp.append(word1)
            if len(leftPatternTemp) > len(topPattern1):
                topPattern1 = leftPatternTemp

        yBridge = []
        for word1 in self.textLineList2:
            temp = 0
            for y in yBridge:
                if abs(word1['y'] - y) < 15:
                    temp = 1
                    break
            if temp == 1:
                continue
            elif word1['y'] < 0.1 * self.heightScreen and word1['y'] > 30:
                yBridge.append(word1['y'])

        topPattern2 = []
        for y in yBridge:
            leftPatternTemp = []
            for word1 in self.textLineList2:
                if abs(word1['y'] - y) < 20 and len(word1['text']) != 1:
                    leftPatternTemp.append(word1)
            if len(leftPatternTemp) > len(topPattern2):
                topPattern2 = leftPatternTemp

        right = 0
        for word1 in rightPattern1:
            for word2 in rightPattern2:
                if self.getTextSimilar(word1['text'], word2['text']):
                    right = right + 1
        if right != 0:
            right = right * 1.0 / max(len(rightPattern1), len(rightPattern2))
        # print("image1 %s type:%d; image2 %s type:%d right:%f" % (self.image1, self.type1, self.image2, self.type2, right)) #量化
        left = 0
        for word1 in leftPattern1:
            for word2 in leftPattern2:
                # if self.getTextSimilar(word1['text'], word2['text'])and not word2.has_key('isUsed'):
                if self.getTextSimilar(word1['text'], word2['text']) and not 'isUsed' in word2.keys():
                    left = left + 1
                    word2['isUsed'] = True
                    break
        if left != 0:
            left = left * 1.0 / max(len(leftPattern1), len(leftPattern2))
        # print("image1 %s type:%d; image2 %s type:%d left:%f" % (self.image1, self.type1, self.image2, self.type2, left))#量化
        top = 0
        for word1 in topPattern1:
            for word2 in topPattern2:
                if self.getTextSimilar(word1['text'], word2['text']):
                    top = top + 1
        if top != 0:
            top = top * 1.0 / len(topPattern1)

        if len(topPattern1) == 0 and len(topPattern2) == 0:
            top = 1.0

        if (left < 0.4 and max(len(leftPattern1), len(leftPattern2)) > 3) or (
                right < 0.4 and max(len(rightPattern1), len(rightPattern2)) > 3):
            print("image1 %s type:%d; image2 %s type:%d top:%f left:%f right:%f" % (
                self.image1, self.type1, self.image2, self.type2, top, left, right))  # 量化

        self.right = right
        self.left = left
        self.top = top
        # self.top = 1
        self.rightPattern1 = rightPattern1
        self.rightPattern2 = rightPattern2
        self.leftPattern1 = leftPattern1
        self.leftPattern2 = leftPattern2
        self.topPattern1 = topPattern1
        self.topPattern2 = topPattern2

    def getInitText(self):
        if self.isText == 0:
            return False, ""
        return True, self.initText

    def getDeltaTime(self, timeBefore, timeAfter):
        return (timeAfter - timeBefore).seconds + (timeAfter - timeBefore).microseconds / 1000000.0

    def judifyMap(self):
        timeBefore = datetime.now()

        # calculate some features of texts
        self.setScreenProperty()
        self.setInitText()
        self.calculatorMappingFeature()

        # windows type must be the same
        if self.type2 != self.type1:
            # print 'type1: {}, type2: {}'.format(self.type1,self.type2)
            return False, [], []

        returnBox = []

        # record diff elements between two screenshots
        tempUpdateList = self.getUpdatedElementList()

        # adjust the top feature according to the examples
        self.adjustTop()

        # check the two screenshots are mapped or not
        if self.initbox['x'] == -1 and self.initbox['y'] == -1:
            # print 'map for check:'
            return self.isCheckMap(timeBefore, self.type2, tempUpdateList, returnBox)

        if self.isText == 1:
            # print 'the original widget is text.'
            returnBox = self.getTextReturnBox()

            if self.widthSreen > self.heightScreen:
                for item in returnBox:
                    tempX, tempY, tempW, tempH = item['y'], self.heightScreen - item['x'] - item['w'], item['h'], item[
                        'w']
                    item['x'], item['y'], item['w'], item['h'] = tempX, tempY, tempW, tempH

            return self.isCheckMap(timeBefore, self.type2, tempUpdateList, returnBox)
        else:
            # print "the original widget is not text."
            returnBox = self.getNoneTextReturnBox()
            # returnBox.append(self.initbox)
            # showVisual(image2, outputPath + 'currentNPlusOne.png', textLineList2, contourList2, returnBox)
            return self.isCheckMap(timeBefore, self.type2, tempUpdateList, returnBox)

    def getMapTimeCost(self):
        return Map.timeCostForMap

    def getTextSimilar(self, text1, text2, isOCRFail=False):
        temp = 0
        tempList1 = []
        tempList2 = []
        textList1 = text1.strip('\n').split(' ')
        for word in textList1:
            if word != "spaceholder" and word != "Mode" and word != "mode" and word != "=" and word != "@":
                tempList1.append(word)

        textList1 = tempList1
        textList2 = text2.strip('\n').split(' ')
        for word in textList2:
            if word != "spaceholder" and word != "Mode" and word != "mode" and word != "=" and word != "@":
                tempList2.append(word)
        textList2 = tempList2

        if len(textList1) - len(textList2) > 3 or len(textList2) - len(textList1) > 3:
            return False
        else:
            for word1 in textList1:
                for word2 in textList2:
                    if word1.lower().strip('/') == word2.lower().strip('/') or word1.lower().strip('/')[
                                                                               0:-1] == word2.lower().strip(
                        '/') or word1.lower().strip('/') == word2.lower().strip('/')[0:-1] or word1.lower().strip(
                        '/') == word2.lower().strip('/')[1:] or word2.lower().strip('/') == word1.lower().strip(
                        '/')[1:] or word1.lower().strip('/')[0:-1] == word2.lower().strip('/')[0:-1]:
                        temp = temp + 1

            if isOCRFail and temp > 0:
                return True

            # print("similar word number is:%d"%(temp))
            # print("word1 number is %d\nword2 number is %d"%(len(textList1),len(textList2)))
            # print(textList1)
            # print(textList2)
            if min(len(textList1), len(textList2)) == 0:
                return False

            if temp * 2.0 / (len(textList1) + len(textList2)) > 0.45:
                return True
            else:
                return False

    def replaceNum(self, numberString):
        result = numberString
        for i in range(10):
            result = result.replace(str(i), 'x')
        return result

    def getSimilarImgElement(self, similarPoints, contourList, initbox):
        # returnBox = []
        repairBox = {}
        sumMax = 0
        initBoxNum = 0
        for (x, y) in similarPoints:
            if y > initbox['y'] and y < initbox['y'] + initbox['h'] and x > initbox['x'] and x < initbox['x'] + \
                    initbox[
                        'w']:
                initBoxNum = initBoxNum + 1
        if (initBoxNum > 0 and initbox['w'] < 55) or (initBoxNum > 1 and initbox['w'] < 70):
            return initbox

        for contour in contourList:
            # if 3*contour['w']<initbox['w'] or contour['w']>3*initbox['w']:
            # continue
            sum = 0
            for (x, y) in similarPoints:
                if y > contour['y'] and y < contour['y'] + contour['h'] and x > contour['x'] and x < contour['x'] + \
                        contour[
                            'w']:
                    sum = sum + 1
            if sum * 1.0 / contour['h'] / contour['w'] > sumMax and sum > 1:
                sumMax = sum * 1.0 / contour['h'] / contour['w']
                repairBox = contour
                # returnBox.append(repairBox)

        # if not repairBox.has_key('x') and len(similarPoints)>2:
        if not 'x' in repairBox.keys() and len(similarPoints) > 2:

            xList = []
            yList = []
            for tupleItem in similarPoints:
                xList.append(tupleItem[0])
                yList.append(tupleItem[1])

            xList.sort()
            yList.sort()
            if xList[-1] - xList[0] < 30 and yList[-1] - yList[0] < 30:
                return {'x': xList[0], 'y': yList[0], 'w': xList[-1] - xList[0], 'h': yList[-1] - yList[0]}

        # if not repairBox.has_key('x'):
        if not 'x' in repairBox.keys():
            initBoxNum = 0
            for (x, y) in similarPoints:
                if y > initbox['y'] and y < initbox['y'] + initbox['h'] and x > initbox['x'] and x < initbox['x'] + \
                        initbox[
                            'w']:
                    initBoxNum = initBoxNum + 1
            if (initBoxNum > 5 and initbox['w'] > 70 and initbox['w'] < 120):
                return initbox

        return repairBox

    def getUpdatedElementList(self):
        tempUpdateList = []

        for updateBox in self.leftPattern2:
            updateFlag = True
            for originalBox in self.leftPattern1:
                if self.getTextSimilar(updateBox['text'], originalBox['text']):
                    updateFlag = False
                    break
            if updateFlag:
                tempUpdateList.append(updateBox)
        for updateBox in self.rightPattern2:
            updateFlag = True
            for originalBox in self.rightPattern1:
                if self.getTextSimilar(updateBox['text'], originalBox['text']):
                    updateFlag = False
                    break
            if updateFlag:
                tempUpdateList.append(updateBox)

        for contourBox in self.contourList2:
            updateFlag = True
            for originalContourBox in self.contourList1:
                if self.rectanCover(contourBox, originalContourBox, 0.6):
                    updateFlag = False
                    break
            if updateFlag:
                tempUpdateList.append(contourBox)

        return tempUpdateList

    def adjustTop(self):
        shadowNum = 0
        if len(self.topPattern1) > 0 and self.top <= 0.5:
            for topItem in self.topPattern1:
                if topItem['x'] < 0.33 * self.widthSreen:
                    for textItem2 in self.leftPattern2:
                        if self.rectanCover(topItem, textItem2, 0.3):
                            for textItem1 in self.leftPattern1:
                                if self.getTextSimilar(textItem1['text'], textItem2['text']):
                                    shadowNum = shadowNum + 1
                                    break
                else:
                    for textItem2 in self.rightPattern2:
                        if self.rectanCover(topItem, textItem2, 0.3):
                            for textItem1 in self.rightPattern1:
                                if self.getTextSimilar(textItem1['text'], textItem2['text']):
                                    shadowNum = shadowNum + 1
                                    break

            if shadowNum / len(self.topPattern1) * 1.0 > 0.5:
                self.top = shadowNum / len(self.topPattern1) * 1.0

    def isCheckMap(self, timeBefore, type, updateElementList=None, returnBox=None):
        leftThresholdLarge = 0.3
        leftThresholdSmall = 0.05
        rightThresholdLarge = 0.75
        rightThresholdSmall = 0.6
        topThreshold = 0.5
        rightNumDiffThreshold = 5
        rightNumThreshold = 6
        leftNumThreshold = 6

        if type == 2 or type == 3:
            leftThresholdLarge = 0.05
            rightThresholdLarge = 0.05
            rightNumDiffThreshold = 6

        if (self.left > leftThresholdLarge or (
                self.left > leftThresholdSmall and self.right > rightThresholdLarge)) and (
                abs(len(self.rightPattern1) - len(
                    self.rightPattern2)) < rightNumDiffThreshold or self.right > rightThresholdSmall) and self.top > topThreshold:
            # if (initbox['x']<0.33*widthScreen and left>0.6 and locationSum>0.5) or (initbox['x']>0.33*widthScreen and right>0.6 and locationSum>0.5):
            Map.timeCostForMap = Map.timeCostForMap + self.getDeltaTime(timeBefore, datetime.now())
            return True, returnBox, updateElementList
        elif len(self.rightPattern1) < rightNumThreshold and len(self.leftPattern1) < leftNumThreshold and len(
                self.rightPattern2) < rightNumThreshold and len(
            self.leftPattern2) < leftNumThreshold and self.top > topThreshold and abs(len(self.rightPattern1) - len(
            self.rightPattern2)) < rightNumDiffThreshold:
            similarPoints = self.Image1.getSift(self.image1, self.image2,
                                                {'x': 0, 'y': 50, 'w': self.widthSreen, 'h': self.heightScreen})
            # print len(similarPoints)
            # print len(contourList2)
            # print len(similarPoints) / len(contourList2)
            if len(similarPoints) / (1.0 * max(len(self.contourList2), 1)) > 4 or (
                    len(similarPoints) / max(len(self.contourList2), 1) > 1 and len(similarPoints) > 1000):
                Map.timeCostForMap = Map.timeCostForMap + self.getDeltaTime(timeBefore, datetime.now())
                return True, returnBox, updateElementList
            else:
                return False, [], []
        else:
            Map.timeCostForMap = Map.timeCostForMap + self.getDeltaTime(timeBefore, datetime.now())
            return False, [], []

    def getTextReturnBox(self):
        returnBox = []
        if self.initbox['x'] < 0.33 * self.widthSreen:
            # print "left process"
            # print leftPattern1
            # print leftPattern2
            for word in self.leftPattern1:
                # #print word['text']
                if self.getTextSimilar(self.initText, word['text']):

                    for word2 in self.leftPattern2:
                        if self.getTextSimilar(word2['text'], word['text']) and (
                                (word2['y'] < 0.25 * self.heightScreen and self.initbox[
                                    'y'] < 0.25 * self.heightScreen) or (
                                        word2['y'] > 0.25 * self.heightScreen and self.initbox[
                                    'y'] > 0.25 * self.heightScreen)):
                            returnBox.append(word2)
                            # showVisual(image2, outputPath + 'currentNPlusOne.png', textLineList2, contourList2, returnBox)
        if self.initbox['x'] > 0.33 * self.widthSreen:
            # print "right process"
            for word in self.rightPattern1:
                if self.getTextSimilar(self.initText, word['text']):
                    for word2 in self.rightPattern2:
                        if self.getTextSimilar(word2['text'], word['text']) and (
                                (word2['y'] < 0.45 * self.heightScreen and self.initbox[
                                    'y'] < 0.45 * self.heightScreen) or (
                                        word2['y'] > 0.45 * self.heightScreen and self.initbox[
                                    'y'] > 0.45 * self.heightScreen)):
                            returnBox.append(word2)

            if 'cgeo' in self.image1:
                for word in self.textLineList2:
                    if self.rectanCover(self.initbox, word, 0.2) and self.getTextSimilar(word['text'], self.initText,
                                                                                         True):
                        returnBox = []
                        returnBox.append(self.initbox)
                        return returnBox

                        # showVisual(image2, outputPath + 'currentNPlusOne.png', textLineList2, contourList2, returnBox)
        if returnBox == [] or (len(returnBox) == 1 and returnBox[0]['text'] != self.initText):
            # print "text repair"
            for word3 in self.textLineList2:
                if (self.getTextSimilar(self.initText, word3['text']) or self.replaceNum(
                        self.initText) == self.replaceNum(word3['text'])) and word3 not in returnBox:
                    returnBox.append(word3)
                    # showVisual(image2, outputPath + 'currentNPlusOne.png', textLineList2, contourList2, returnBox)

        if returnBox != [] and returnBox[0]['text'] != self.initText:
            for boxIndex, returnBoxItem in enumerate(returnBox):
                if returnBoxItem['text'].lower() == self.initText.lower():
                    tempBox = returnBoxItem
                    returnBox[boxIndex] = returnBox[0]
                    returnBox[0] = tempBox
                    break

        repeatReturnBoxFlag = False
        for item in returnBox:
            if item['text'] == self.initText and not repeatReturnBoxFlag:
                repeatReturnBoxFlag = True
            if item['text'] == self.initText and repeatReturnBoxFlag:
                for boxIndex, item_ in enumerate(returnBox):
                    if item_['text'] == self.initText and self.rectanCover(item_, self.initbox, 0.01):
                        tempBox = item_
                        returnBox[boxIndex] = returnBox[0]
                        returnBox[0] = tempBox
                        break

        return returnBox

    def getNoneTextReturnBox(self):
        returnBox = []
        similarPointsInit = self.Image1.getSift(self.image1, self.image2, self.initbox)
        if self.getSimilarImgElement(similarPointsInit, self.contourList2, self.initbox) != {}:
            returnBox.append(self.getSimilarImgElement(similarPointsInit, self.contourList2, self.initbox))
            # print "found similar img element"
        if returnBox == []:
            # print "can not find similar pic "
            returnBox = []

        return returnBox


if __name__ == '__main__':
    '''
    Map has 3 parameters, the path for img1, the path for img2 amd the tested rectangle bound, which is {} if not neccessary.
    By invocating Map.judifyMap()[0], it returns whether the two imgs are mapped or not.
    '''
    folder_dir = '/Users/njutianyu/Desktop/imgMapApi 2/截图'
    count = 0
    data_folder = os.path.join(folder_dir)  # 文件路径
    video_list = [v for v in os.listdir(data_folder)]  # 文件名list
    video_list.sort()
    # path = os.path.join('/Users/njutianyu/Desktop/imgMapApi 2/截图',folder_dir)
    # print(video_list)#未排序
    # print(len(video_list)-1)
    for i in range(len(video_list) - 1):
        j = i + 1
        folder_dir = '/Users/njutianyu/Desktop/imgMapApi 2/截图/' + str(j)
        data_folder = os.path.join(folder_dir)
        video_list1 = [v for v in os.listdir(data_folder)]
        video_list1.sort()
        # path = os.path.join('/Users/njutianyu/Desktop/imgMapApi 2/截图/1', folder_dir)
        print(video_list1)
        for k in range(1, len(video_list1) - 1):
            a = video_list1[k]
            print("/Users/njutianyu/Desktop/imgMapApi 2/截图/" + str(i + 1) + "/" + a)
            b = video_list1[k + 1]
            print(b)
            map = Map("/Users/njutianyu/Desktop/imgMapApi 2/截图/" + str(i + 1) + "/" + a,
                      "/Users/njutianyu/Desktop/imgMapApi 2/截图/" + str(i + 1) + "/" + b
                      , {'x': 84, 'y': 322, 'w': 636, 'h': 76})
            # for m in range(len(video_list1) - 2):
            # for n in range(len(video_list1) - 1):
            # map = Map("img/sample1.png", b, {'x': 84, 'y': 322, 'w': 636, 'h': 76})  ##改这里应该就可以了
            # map = Map("/Users/njutianyu/Desktop/imgMapApi 2/截图/" + str(i) + str(video_list1[i+1]), "/Users/njutianyu/Desktop/imgMapApi 2/截图/" + str(i) + str(video_list1[i+2]), {'x': 84, 'y': 322, 'w': 636, 'h': 76})
            print(map.judifyMap()[0])
    # print(map.judifyMap()[0].top + map.judifyMap()[0].left + map.judifyMap()[0].right)
