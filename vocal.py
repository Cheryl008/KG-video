# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下，您可自行逐一或者复制到一个新的txt文件利用pip一次性安装：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#
#  语音听写流式 WebAPI 接口调用示例 接口文档（必看）：https://doc.xfyun.cn/rest_api/语音听写（流式版）.html
#  webapi 听写服务参考帖子（必看）：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=38947&extra=
#  语音听写流式WebAPI 服务，热词使用方式：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--个性化热词，
#  设置热词
#  注意：热词只能在识别的时候会增加热词的识别权重，需要注意的是增加相应词条的识别率，但并不是绝对的，具体效果以您测试为准。
#  语音听写流式WebAPI 服务，方言试用方法：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--识别语种列表
#  可添加语种或方言，添加后会显示该方言的参数值
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import subprocess
from moviepy.editor import *
from pydub import AudioSegment
from pydub.utils import make_chunks
import os
import numpy as np
import re
import cv2
from PIL import Image, ImageDraw, ImageFont
import imageio

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

MOVIENAME = "testing.mp4"
INPUT = "output_facial.avi"
FILENAME = "歌词.txt"
APPID = '5f155048'
APIKey = '2a32db2bf2ad933e6f1655b14a78719c'
APISecret = '55158771e4cbf261277391d777f790cc'
INTERVAL = 6000  #6s
OUTPUT = "output.avi"


fo = open(FILENAME, "w")
known_lyrics_name = ["北京欢迎你", "父亲", "同桌的你"]

contents = []

for i in known_lyrics_name:
    content = []
    rec = open(i+".txt", "r+")
    lineInfos = rec.readlines()
    for row in lineInfos:
        line = re.findall('[\u4e00-\u9fa5]',row.strip())
        line = "".join(line)
        content.append(line)

    lines = "".join(content)
    contents.append(lines)


name_set = []
class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1,"vad_eos":10000}

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


# 收到websocket消息的处理
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            #print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # print(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            #print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
            a = re.findall('[\u4e00-\u9fa5]',result)
            a = "".join(a)
            if len(a) >= 5:
                for i in range(len(contents)):
                    if contents[i].find(a) != -1:
                        print("%s存在于%s"%(a, known_lyrics_name[i]))
                        #print(known_lyrics_name[i])
                        name_set.append(known_lyrics_name[i])
                        break
            #print(a)
            fo.write(a + "\n")
    except Exception as e:
        print("receive msg,but parse exception:", e)




# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    name_set.append("flag")
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        frameSize = 1000  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:

                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    # 测试时候在此处正确填写相关信息即可运行

    video = VideoFileClip(MOVIENAME)
    audio = video.audio
    audio.write_audiofile('Music.mp3')

    subprocess.call(["spleeter separate -i Music.mp3 -p spleeter:2stems -o {}".format("sound")], shell=True)
    subprocess.call(["mv {} .".format("sound/Music/vocals.wav")], shell=True)
    #subprocess.call(["rm -r {}".format("sound")], shell=True)
    #subprocess.call(["rm {}".format("Music.mp3")], shell=True)

    audio = AudioSegment.from_file("vocals.wav", "wav")

    size = INTERVAL

    chunks = make_chunks(audio, size) 

    length = len(chunks)

    for i, chunk in enumerate(chunks):
        chunk_name = "sound/vocal-{0}".format(i)
        old_name = "{}.wav".format(chunk_name)
        new_name = "{}_New.wav".format(chunk_name)
        chunk.export(old_name, format="wav")
        subprocess.call(["sox {} -r 16000 -b 16 -c 1 {}".format(old_name, new_name)], shell=True)
        subprocess.call(["rm {}".format(old_name)], shell=True)
        f = open(new_name, "rb")
        f.seek(0)
        f.read(44)
        data = np.fromfile(f, dtype=np.int16)
        data.tofile("{}.pcm".format(chunk_name))
        #subprocess.call(["rm {}".format(new_name)], shell=True)

    #subprocess.call(["rm {}".format("vocals.wav")], shell=True)


    for i in range(length):
        name = "sound/vocal-{0}.pcm".format(i)
        time1 = datetime.now()
        wsParam = Ws_Param(APPID=APPID, APIKey=APIKey,
                           APISecret=APISecret,
                           AudioFile=name)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        time2 = datetime.now()
        #print(time2-time1)
    fo.close()

    time = INTERVAL / 1000
    input_movie = cv2.VideoCapture(INPUT)
    rate = input_movie.get(5)
    flag_number = 0
    song = ""
    song_name = []
    song_nameNew = []
    frame_number = 0
    length = int(input_movie.get(7))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_movie = cv2.VideoWriter(OUTPUT, fourcc, rate, (1920, 1080))

    def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
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


    for i in range(len(name_set)):
        if name_set[i] == "flag":
            flag_number += 1
            if (i != 0) and (name_set[i-1] != "flag"):
                song = name_set[i-1]
            else:
                song = ""
            bottom = int((flag_number - 1) * time * rate)
            up = int(flag_number * time * rate)
            for n in range(bottom, up):
                song_name.append(song)


    frame_total = int(input_movie.get(7))

    for i in range(frame_total):
        song_nameNew.append(song_name[i])

    print(song_nameNew)

    while True:
        ret, frame = input_movie.read()
        if not ret:
            break
        name = song_nameNew[frame_number]
        frame = cv2ImgAddText(frame, name, 1200, 950, (0, 255, 0), 100)
        frame_number += 1

        print("Writing frame {} / {}".format(frame_number, length))
        output_movie.write(frame)

    input_movie.release()
    cv2.destroyAllWindows()

    '''def video_add_mp3(file_name, mp3_file):
        outfile_name = file_name.split('.')[0] + '-new.avi'
        subprocess.call('ffmpeg -i ' + file_name
                        + ' -i ' + mp3_file + ' -strict -2 -f avi '
                        + outfile_name, shell=True)

    video_add_mp3(OUTPUT, "Music.mp3")'''






    