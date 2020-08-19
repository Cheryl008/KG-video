import face_recognition
import cv2
import demo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

APPID = '5f30b54b'
APISECRET = '1b7cf0fac674c0eac7714bff3a1fc683'
APIKEY = 'ff5754aa9eb132498d8c2eaac05d10fa'

input_movie = cv2.VideoCapture("output_object.mp4")
length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

# Create an output movie file (make sure resolution/frame rate matches input video!)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_movie = cv2.VideoWriter('output_facial.avi', fourcc, 25, (1920, 1080))


known_faces_name = [
    "陈天佳",
    "刘欢",
    "那英",
    "孙燕姿",
    "孙悦",
    "王力宏",
    "老狼",
    "霍思燕"
]

# Initialize some variables
face_locations = []
face_names = []
frame_number = 0
name_times = []
frame_last_number = []
frame_left = []
frame_top = []
contents = []

for i in known_faces_name:
    content = []
    rec = open("face/" + i +".txt", "r+")
    lineInfos = rec.readlines()
    for row in lineInfos:
        content.append(row)

    lines = "".join(content)
    contents.append(lines)


for i in range(len(known_faces_name)):
    name_times.append(0)
    frame_last_number.append(0)
    frame_left.append(0)
    frame_top.append(0)

def cv2ImgAddText(img, text, left, top, textColor, textSize):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "font/simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


while True:
    # Grab a single frame of video
    ret, frame = input_movie.read()
    frame_number += 1

    # Quit when the input video file ends
    if not ret:
        break

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    #face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    i = 1
    name = ""
    face_names = []
    for (top, right, bottom, left) in face_locations:
        face = frame[top:bottom, left:right]
        face = cv2.resize(face, (512,512))
        if frame_number % 80 == 0:
            if i == 1:
                name = "img/" + str(frame_number) + '.jpg'
                cv2.imwrite(name, face)
            else:
                name = "img/" + str(frame_number)+'_' + str(i) + '.jpg'
                cv2.imwrite(name, face)
            i += 1

            score = 0
            index = 0
            for n in range(len(known_faces_name)):
                path = "face/" + known_faces_name[n] + ".png"
                score_new = demo.run(appid=APPID, apisecret=APISECRET, apikey=APIKEY, img1_path=path, img2_path=name)
                if (score < score_new) and (score_new > 0.5):
                    score = score_new
                    index = n
            face_names.append(known_faces_name[index])
        else:
            face_names.append("")

    for n in range(len(known_faces_name)):
        if frame_number <= frame_last_number[n]:
            frame = cv2ImgAddText(frame, known_faces_name[n], frame_left[n], frame_top[n], (255, 0, 0), 50)
            frame = cv2ImgAddText(frame, contents[n], frame_left[n], frame_top[n] + 100, (255, 0, 0), 25)

    c = 0
    # Label the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        if name == "":
            continue

        c += 1

        index = known_faces_name.index(name)

        name_times[index] += 1

        if name_times[index] > 1:
            continue
        
        frame = cv2ImgAddText(frame, name, 100*c, 100, (255, 0, 0), 50)

        index = known_faces_name.index(name)
        text = contents[index]
        frame = cv2ImgAddText(frame, text, 100*c, 200, (255, 0, 0), 25)
        frame_last_number[index] = frame_number + 80
        frame_left[index] = 100 * c
        frame_top[index] = 100

        

    # Write the resulting image to the output video file
    print("Writing frame {} / {}".format(frame_number, length))
    output_movie.write(frame)

# All done!
input_movie.release()
cv2.destroyAllWindows()

