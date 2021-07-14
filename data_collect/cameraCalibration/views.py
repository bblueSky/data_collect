#encoding:utf-8
"""
一、确定现场要做的（实验）内容
    1、双目标定
    2、采图
    3、激光跟踪仪采基准板两侧数据（A板1、2、3以及B板1、2、3）（测两个指标，一个短时内多次测量，为求坐标转换精度；另一个是多日内单次测量）
    4、激光跟踪仪采筒上的孔数据及板上靶标数据（须有一定顺序，先A后B，易取标左孔顺时针为佳，之后POs、PHs、PWs）
二、确定需要转存的数据
    1、双目标定数据
    2、图像
    3、基准板一系列数据（粘过来就行）
    4、筒段孔上、靶标数据
三、软件要制作的功能
    1、相机通讯、拍照、保存（按照原本软件写的文件树存储）
    2、相机标定功能（按照原软件的标定存储模式写）
    3、手写导入并存储激光跟踪仪测基准板一系列数据（按照原本软件写的文件存储，以编号命名）
    4、手写导入并存储激光跟踪仪测筒段一系列数据（这是个新功能，在同一日志里，先切换好A、B，按顺序，点一下存一个点）
"""
#encoding:utf-8

from flask  import render_template, request
from data_collect.cameraCalibration import  cameraCalibration
import json
import cv2
import numpy as np
import time
import datetime
import signal
import threading
import os
from xml.dom import minidom
import data_collect.ksj.cam as  kcam

from  data_collect.cameraCalibration.utils  import  sig_calibration,stereo_Calibration
from  data_collect.cameraCalibration.utils  import  LTOrd2AOrd,LTside2VSide


os.environ['path'] += ';KSJApi.Bin\\x64';

@cameraCalibration.route('/')
def index():

    return render_template('camera_calibration/camera_calibration.html')


@cameraCalibration.route('/selectAorB/',methods=['POST','GET'])
def  selectAorB():
    AorB = request.args.get('mydata')
    #print("传数成功，选择了"+flager)

    img_path = os.path.realpath(__file__).replace("cameraCalibration/views.py","static/checkboard_img_dir/"+AorB)
    return  str(1)


@cameraCalibration.route('/imageDisplay/',methods=['POST','GET'])
def  imageDisplay():

    flag = request.args.get('mydata')


    img = "123"
    #return render_template('camera_calibration/calibration_output.html',img_path=img)
    return img



@cameraCalibration.route('/take_pic/', methods =['POST','GET'] )
def take_pic():
    flag = request.args.get('mydata')
    print("相机开始运行")
    #os.system('sh /home/cx/PycharmProjects/stereo_vision/stereo_vision/cameraCalibration/run.sh')
    exp_time = 150
    #exp_time =  request.get_date('exp_time')
    cam = kcam.Ksjcam()

    #TODO 软触发模式设置

    cam.SetExptime(0, exp_time)  # 设置曝光150MS
    cam.SetTriggerMode(0, 2)  # 设置成固定帧率模式

    cam.SetExptime(1, exp_time)  # 设置曝光150MS
    cam.SetTriggerMode(1, 2)  # 设置成固定帧率模式

    # cam.SetExptime(2, exp_time)  # 设置曝光150MS
    # cam.SetTriggerMode(2, 2)  # 设置成固定帧率模式
    #
    # cam.SetExptime(3, exp_time)  # 设置曝光150MS
    # cam.SetTriggerMode(3, 2)  # 设置成固定帧率模式

    cam.SetFixedFrameRateEx(0, 1)  # 设置固定帧率是5fs

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime( '%Y'+ '_' + '%m' + '_' + '%d' + '_' + '%H' + '_' + '%M' + '_' + '%S')
    ##默认A端0\1 B端2\3
    image_left = cam.read(0)  # 从相机0读取一个图像，这个image就是oenpcv的图像  # todo  需要找出哪个是相机0 哪个是相机1
    image_right = cam.read(1)
    frame_left = image_left[::-1,:]
    frame_right = image_right[::-1,:]
    # frame_left = image_left
    # frame_right = image_right
    # TODO  注释掉写入帧的操作
    dirPath = os.path.dirname(os.path.realpath(__file__)).replace('cameraCalibration', 'static/res_pictures/temp/')
    print(dirPath)
    print("标定的是"+flag+"端相机")


    img_left_save_path = os.path.join(dirPath, 'left.jpg')
    img_right_save_path = os.path.join(dirPath, 'right.jpg')

    cv2.imwrite(img_left_save_path, frame_left)
    cv2.imwrite(img_right_save_path, frame_right)


    return  json.dumps({"key":st})

@cameraCalibration.route('/save_pic/',methods=['POST','GET'])
def save_pic():
    from_dirPath = os.path.dirname(os.path.realpath(__file__)).replace('cameraCalibration', "static\\res_pictures\\temp\\")
    to_dirPath = os.path.dirname(os.path.realpath(__file__)).replace('cameraCalibration', 'static\\res_pictures\\')
    flag = request.args.get('mydata')
    time = request.args.get('mydata1')
    from_img_left_path  = os.path.join(from_dirPath,'left.jpg')
    from_img_right_path = os.path.join(from_dirPath,'right.jpg')
    if flag=="cali_A":
        to_img_left_path = os.path.join(to_dirPath,"A_calibration_left\\"+time + "_left.jpg")
        to_img_right_path = os.path.join(to_dirPath,"A_calibration_right\\"+time + "_right.jpg")
    elif flag=="cali_B":
        to_img_left_path = os.path.join(to_dirPath,"B_calibration_left\\" + time + "_left.jpg")
        to_img_right_path = os.path.join(to_dirPath,"B_calibration_right\\" + time + "_right.jpg")
    else:
        to_img_left_path = os.path.join(to_dirPath,flag+"_left\\"+time+"_left.jpg")
        to_img_right_path = os.path.join(to_dirPath,flag+"_right\\"+time+"_right.jpg")
    command1 = "copy "+from_img_left_path+" "+to_img_left_path
    command2 = "copy " +from_img_right_path + " " + to_img_right_path
    print(command1)
    os.system(command1)
    os.system(command2)

    return str(1)


@cameraCalibration.route('/deleteAll/',methods=['POST','GET'])
def deletAll():
    flag = request.args.get('mydata')
    dirPath = os.path.dirname(os.path.realpath(__file__)).replace('cameraCalibration', 'static\\res_pictures\\')
    if flag=="cali_A":
        tarPath_left = dirPath+"A_calibration_left\\*"
        tarPath_right = dirPath+"A_calibration_right\\*"
    elif flag=="cali_B":
        tarPath_left = dirPath + "B_calibration_left\\*"
        tarPath_right = dirPath + "B_calibration_right\\*"
    else:
        tarPath_left = dirPath +flag+"_left\\*"
        tarPath_right = dirPath +flag+"_right\\*"


    command1 = "del /q "+tarPath_left
    command2 = "del /q "+tarPath_right
    os.system(command1)
    os.system(command2)
    return str(1)


@cameraCalibration.route('/stereoCalibration/',methods=['POST','GET'])
def  stereo_calibration():
    res = dict()
    flag = request.args.get('mydata')
    resultl = sig_calibration(flag,"left")
    resultr = sig_calibration(flag,"right")
    results = stereo_Calibration(flag)

    res["ltime"] = resultl[0]
    res["lmtx0"] = resultl[1]
    res["lmtx1"] = resultl[2]
    res["lmtx2"] = resultl[3]
    res["ldist"] = resultl[4]
    res["lterror"] = resultl[5]

    res["rtime"] = resultr[0]
    res["rmtx0"] = resultr[1]
    res["rmtx1"] = resultr[2]
    res["rmtx2"] = resultr[3]
    res["rdist"] = resultr[4]
    res["rterror"] = resultr[5]

    res["R0"] = results[0]
    res["R1"] = results[1]
    res["R2"] = results[2]
    res["T"] = results[3]
    res["stime"] = results[4]


    return res


@cameraCalibration.route('/insertComplete/',methods=['POST','GET'])
def insertComplete():
    ##先生成相关文件

    p_doc = minidom.Document()
    save_dir = os.path.dirname(os.path.realpath(__file__)).replace("cameraCalibration",'static\\res_pictures\\result\\global_info\\')
    numOfglob = 0
    dirList = os.listdir(save_dir)
    for i in dirList:
        if i.endswith(".xml"):
            numOfglob += 1
    numOfglob = numOfglob//2
    savepath = save_dir+"global_info_"+str(numOfglob)+".xml"
    root = p_doc.createElement('global_info')
    ## root
    p_doc.appendChild(root)
    ## time of calibration
    A_calibration_time = p_doc.createElement('A_calibration_time')
    A_calibration_time.appendChild(p_doc.createElement('time'))
    root.appendChild(A_calibration_time)

    B_calibration_time = p_doc.createElement('B_calibration_time')
    B_calibration_time.appendChild(p_doc.createElement('time'))
    root.appendChild(B_calibration_time)

    ## time of global
    global_time = p_doc.createElement('global_time')
    global_time.appendChild(p_doc.createElement('time'))
    root.appendChild(global_time)
    ## origin coordi
    origin = p_doc.createElement('origin')
    AP1 = p_doc.createElement('AP1')
    AP2 = p_doc.createElement('AP2')
    AP3 = p_doc.createElement('AP3')
    BP1 = p_doc.createElement('BP1')
    BP2 = p_doc.createElement('BP2')
    BP3 = p_doc.createElement('BP3')
    root.appendChild(origin)
    origin.appendChild(AP1)
    origin.appendChild(AP2)
    origin.appendChild(AP3)
    origin.appendChild(BP1)
    origin.appendChild(BP2)
    origin.appendChild(BP3)
    ## T2A coordi
    T2A = p_doc.createElement('T2A')
    APO = p_doc.createElement('APO')
    APH = p_doc.createElement('APH')
    APW = p_doc.createElement('APW')
    BPO = p_doc.createElement('BPO')
    BPH = p_doc.createElement('BPH')
    BPW = p_doc.createElement('BPW')
    R_T2A = p_doc.createElement('R_T2A')
    T_T2A = p_doc.createElement('T_T2A')
    root.appendChild(T2A)
    T2A.appendChild(APO)
    T2A.appendChild(APH)
    T2A.appendChild(APW)
    T2A.appendChild(BPO)
    T2A.appendChild(BPH)
    T2A.appendChild(BPW)
    T2A.appendChild(R_T2A)
    T2A.appendChild(T_T2A)
    ## S2S coordi
    S2S = p_doc.createElement('S2S')
    APOs = p_doc.createElement('APOs')
    APHs = p_doc.createElement('APHs')
    APWs = p_doc.createElement('APWs')
    BPOs = p_doc.createElement('BPOs')
    BPHs = p_doc.createElement('BPHs')
    BPWs = p_doc.createElement('BPWs')
    T_AS2S = p_doc.createElement('T_AS2S')
    T_BS2S = p_doc.createElement('T_BS2S')
    root.appendChild(S2S)
    S2S.appendChild(APOs)
    S2S.appendChild(APHs)
    S2S.appendChild(APWs)
    S2S.appendChild(BPOs)
    S2S.appendChild(BPHs)
    S2S.appendChild(BPWs)
    S2S.appendChild(T_AS2S)
    S2S.appendChild(T_BS2S)

    with open(savepath, 'w') as fp:
        p_doc.writexml(fp)

    ###################################################多生成一个记录LT数据的文件###############################

    p_doc = minidom.Document()
    save_dir = os.path.dirname(os.path.realpath(__file__)).replace("cameraCalibration",
                                                                   'static\\res_pictures\\result\\global_info\\')
    numOfglob = 0
    dirList = os.listdir(save_dir)
    for i in dirList:
        if i.endswith(".xml"):
            numOfglob += 1
    numOfglob = numOfglob // 2
    savepath1 = save_dir + "LT_info_" + str(numOfglob) + ".xml"
    root = p_doc.createElement('LT_info')
    ## root
    p_doc.appendChild(root)
    ## time of calibration
    A_calibration_time = p_doc.createElement('A_calibration_time')
    A_calibration_time.appendChild(p_doc.createElement('time'))
    root.appendChild(A_calibration_time)

    B_calibration_time = p_doc.createElement('B_calibration_time')
    B_calibration_time.appendChild(p_doc.createElement('time'))
    root.appendChild(B_calibration_time)

    ## time of global
    global_time = p_doc.createElement('global_time')
    global_time.appendChild(p_doc.createElement('time'))
    root.appendChild(global_time)
    ## origin coordi
    origin = p_doc.createElement('origin')
    AP1 = p_doc.createElement('AP1')
    AP2 = p_doc.createElement('AP2')
    AP3 = p_doc.createElement('AP3')
    BP1 = p_doc.createElement('BP1')
    BP2 = p_doc.createElement('BP2')
    BP3 = p_doc.createElement('BP3')
    root.appendChild(origin)
    origin.appendChild(AP1)
    origin.appendChild(AP2)
    origin.appendChild(AP3)
    origin.appendChild(BP1)
    origin.appendChild(BP2)
    origin.appendChild(BP3)
    ## T2A coordi
    T2A = p_doc.createElement('T2A')
    APO = p_doc.createElement('APO')
    APH = p_doc.createElement('APH')
    APW = p_doc.createElement('APW')
    BPO = p_doc.createElement('BPO')
    BPH = p_doc.createElement('BPH')
    BPW = p_doc.createElement('BPW')
    R_T2A = p_doc.createElement('R_T2A')
    T_T2A = p_doc.createElement('T_T2A')
    root.appendChild(T2A)
    T2A.appendChild(APO)
    T2A.appendChild(APH)
    T2A.appendChild(APW)
    T2A.appendChild(BPO)
    T2A.appendChild(BPH)
    T2A.appendChild(BPW)
    T2A.appendChild(R_T2A)
    T2A.appendChild(T_T2A)
    ## S2S coordi
    S2S = p_doc.createElement('S2S')
    APOs = p_doc.createElement('APOs')
    APHs = p_doc.createElement('APHs')
    APWs = p_doc.createElement('APWs')
    BPOs = p_doc.createElement('BPOs')
    BPHs = p_doc.createElement('BPHs')
    BPWs = p_doc.createElement('BPWs')
    T_AS2S = p_doc.createElement('T_AS2S')
    T_BS2S = p_doc.createElement('T_BS2S')
    root.appendChild(S2S)
    S2S.appendChild(APOs)
    S2S.appendChild(APHs)
    S2S.appendChild(APWs)
    S2S.appendChild(BPOs)
    S2S.appendChild(BPHs)
    S2S.appendChild(BPWs)
    S2S.appendChild(T_AS2S)
    S2S.appendChild(T_BS2S)

    with open(savepath1, 'w') as fp:
        p_doc.writexml(fp)



    ##########################################################################################################
    A1X = request.args.get('A1X')
    A1Y = request.args.get('A1Y')
    A1Z = request.args.get('A1Z')
    A2X = request.args.get('A2X')
    A2Y = request.args.get('A2Y')
    A2Z = request.args.get('A2Z')
    A3X = request.args.get('A3X')
    A3Y = request.args.get('A3Y')
    A3Z = request.args.get('A3Z')
    B1X = request.args.get('B1X')
    B1Y = request.args.get('B1Y')
    B1Z = request.args.get('B1Z')
    B2X = request.args.get('B2X')
    B2Y = request.args.get('B2Y')
    B2Z = request.args.get('B2Z')
    B3X = request.args.get('B3X')
    B3Y = request.args.get('B3Y')
    B3Z = request.args.get('B3Z')

    rAOX = request.args.get('AOX')
    rAOY = request.args.get('AOY')
    rAOZ = request.args.get('AOZ')
    rAHX = request.args.get('AHX')
    rAHY = request.args.get('AHY')
    rAHZ = request.args.get('AHZ')
    rAWX = request.args.get('AWX')
    rAWY = request.args.get('AWY')
    rAWZ = request.args.get('AWZ')
    rBOX = request.args.get('BOX')
    rBOY = request.args.get('BOY')
    rBOZ = request.args.get('BOZ')
    rBHX = request.args.get('BHX')
    rBHY = request.args.get('BHY')
    rBHZ = request.args.get('BHZ')
    rBWX = request.args.get('BWX')
    rBWY = request.args.get('BWY')
    rBWZ = request.args.get('BWZ')


    AP1 = np.mat([float(A1X),float(A1Y),float(A1Z)])
    AP2 = np.mat([float(A2X),float(A2Y),float(A2Z)])
    AP3 = np.mat([float(A3X),float(A3Y),float(A3Z)])
    BP1 = np.mat([float(B1X),float(B1Y),float(B1Z)])
    BP2 = np.mat([float(B2X),float(B2Y),float(B2Z)])
    BP3 = np.mat([float(B3X),float(B3Y),float(B3Z)])
    APO,APH,APW,BPO,BPH,BPW,R_T2A,T_T2A = LTOrd2AOrd(AP1,AP2,AP3,BP1,BP2,BP3)  ##激光跟踪仪下的六点坐标转移到A基准板坐标系下；APO默认（0,0,0），APH与APO同Height，APW与APO同Width
    result = dict()
    AOX = APO[0, 0]
    AOY = APO[0, 1]
    AOZ = APO[0, 2]
    result["APOX"] = AOX
    result["APOY"] = AOY
    result["APOZ"] = AOZ
    AHX = APH[0, 0]
    AHY = APH[0, 1]
    AHZ = APH[0, 2]
    result["APHX"] = AHX
    result["APHY"] = AHY
    result["APHZ"] = AHZ
    AWX = APW[0, 0]
    AWY = APW[0, 1]
    AWZ = APW[0, 2]
    result["APWX"] = AWX
    result["APWY"] = AWY
    result["APWZ"] = AWZ
    BOX = BPO[0, 0]
    BOY = BPO[0, 1]
    BOZ = BPO[0, 2]
    result["BPOX"] = BOX
    result["BPOY"] = BOY
    result["BPOZ"] = BOZ
    BHX = BPH[0, 0]
    BHY = BPH[0, 1]
    BHZ = BPH[0, 2]
    result["BPHX"] = BHX
    result["BPHY"] = BHY
    result["BPHZ"] = BHZ
    BWX = BPW[0, 0]
    BWY = BPW[0, 1]
    BWZ = BPW[0, 2]
    result["BPWX"] = BWX
    result["BPWY"] = BWY
    result["BPWZ"] = BWZ

    APOs,APHs,APWs,BPOs,BPHs,BPWs,T_AS2S,T_BS2S = LTside2VSide(APO,APH,APW,BPO,BPH,BPW)  ##靶球一侧向视觉靶标一侧转换，坐标系仍然是A基准板，解出的六点是视觉靶标在A板坐标系下的坐标
    AOsX = APOs[0, 0]
    AOsY = APOs[0, 1]
    AOsZ = APOs[0, 2]
    AHsX = APHs[0, 0]
    AHsY = APHs[0, 1]
    AHsZ = APHs[0, 2]
    AWsX = APWs[0, 0]
    AWsY = APWs[0, 1]
    AWsZ = APWs[0, 2]
    BOsX = BPOs[0, 0]
    BOsY = BPOs[0, 1]
    BOsZ = BPOs[0, 2]
    BHsX = BPHs[0, 0]
    BHsY = BPHs[0, 1]
    BHsZ = BPHs[0, 2]
    BWsX = BPWs[0, 0]
    BWsY = BPWs[0, 1]
    BWsZ = BPWs[0, 2]
    ATX = T_AS2S[0, 0]
    ATY = T_AS2S[0, 1]
    ATZ = T_AS2S[0, 2]
    BTX = T_BS2S[0, 0]
    BTY = T_BS2S[0, 1]
    BTZ = T_BS2S[0, 2]

    ## 数据存入global_ord.xml


    savePath = savepath
    dom = minidom.parse(savePath)
    root = dom.documentElement
    root.removeChild(root.getElementsByTagName("origin")[0])
    root.removeChild(root.getElementsByTagName("T2A")[0])
    root.removeChild(root.getElementsByTagName("S2S")[0])
    root.appendChild(dom.createElement("origin"))
    root.appendChild(dom.createElement("T2A"))
    root.appendChild(dom.createElement("S2S"))
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y' + '_' + '%m' + '_' + '%d' + '_' + '%H' + '_' + '%M' + '_' + '%S')
    calibration_time = root.getElementsByTagName("global_time")[0]
    calibration_time.removeChild(root.getElementsByTagName("time")[2])
    time1 = dom.createElement("time")
    calibration_time.appendChild(time1)
    time1.appendChild(dom.createTextNode(st))
    origin = root.getElementsByTagName("origin")[0]
    AP1 = dom.createElement('AP1')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(A1X))
    AP1.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(A1Y))
    AP1.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(A1Z))
    AP1.appendChild(Z)
    AP2 = dom.createElement('AP2')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(A2X))
    AP2.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(A2Y))
    AP2.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(A2Z))
    AP2.appendChild(Z)
    AP3 = dom.createElement('AP3')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(A3X))
    AP3.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(A3Y))
    AP3.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(A3Z))
    AP3.appendChild(Z)
    BP1 = dom.createElement('BP1')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(B1X))
    BP1.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(B1Y))
    BP1.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(B1Z))
    BP1.appendChild(Z)
    BP2 = dom.createElement('BP2')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(B2X))
    BP2.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(B2Y))
    BP2.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(B2Z))
    BP2.appendChild(Z)
    BP3 = dom.createElement('BP3')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(B3X))
    BP3.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(B3Y))
    BP3.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(B3Z))
    BP3.appendChild(Z)
    origin.appendChild(AP1)
    origin.appendChild(AP2)
    origin.appendChild(AP3)
    origin.appendChild(BP1)
    origin.appendChild(BP2)
    origin.appendChild(BP3)




    T2A = root.getElementsByTagName("T2A")[0]
    APO = dom.createElement('APO')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(AOX)))
    APO.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(AOY)))
    APO.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(AOZ)))
    APO.appendChild(Z)
    APH = dom.createElement('APH')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(AHX)))
    APH.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(AHY)))
    APH.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(AHZ)))
    APH.appendChild(Z)
    APW = dom.createElement('APW')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(AWX)))
    APW.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(AWY)))
    APW.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(AWZ)))
    APW.appendChild(Z)
    BPO = dom.createElement('BPO')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(BOX)))
    BPO.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(BOY)))
    BPO.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(BOZ)))
    BPO.appendChild(Z)
    BPH = dom.createElement('BPH')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(BHX)))
    BPH.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(BHY)))
    BPH.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(BHZ)))
    BPH.appendChild(Z)
    BPW = dom.createElement('BPW')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(BWX)))
    BPW.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(BWY)))
    BPW.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(BWZ)))
    BPW.appendChild(Z)
    T2A.appendChild(APO)
    T2A.appendChild(APH)
    T2A.appendChild(APW)
    T2A.appendChild(BPO)
    T2A.appendChild(BPH)
    T2A.appendChild(BPW)



    S2S = root.getElementsByTagName("S2S")[0]
    APOs = dom.createElement('APOs')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(AOsX)))
    APOs.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(AOsY)))
    APOs.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(AOsZ)))
    APOs.appendChild(Z)
    APHs = dom.createElement('APHs')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(AHsX)))
    APHs.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(AHsY)))
    APHs.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(AHsZ)))
    APHs.appendChild(Z)
    APWs = dom.createElement('APWs')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(AWsX)))
    APWs.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(AWsY)))
    APWs.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(AWsZ)))
    APWs.appendChild(Z)
    BPOs = dom.createElement('BPOs')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(BOsX)))
    BPOs.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(BOsY)))
    BPOs.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(BOsZ)))
    BPOs.appendChild(Z)
    BPHs = dom.createElement('BPHs')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(BHsX)))
    BPHs.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(BHsY)))
    BPHs.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(BHsZ)))
    BPHs.appendChild(Z)
    BPWs = dom.createElement('BPWs')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(BWsX)))
    BPWs.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(BWsY)))
    BPWs.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(BWsZ)))
    BPWs.appendChild(Z)
    T_AS2S = dom.createElement('T_AS2S')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(ATX)))
    T_AS2S.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(ATY)))
    T_AS2S.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(ATZ)))
    T_AS2S.appendChild(Z)
    T_BS2S = dom.createElement('T_BS2S')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(BTX)))
    T_BS2S.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(BTY)))
    T_BS2S.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(BTZ)))
    T_BS2S.appendChild(Z)
    S2S.appendChild(T_AS2S)
    S2S.appendChild(T_BS2S)
    S2S.appendChild(APOs)
    S2S.appendChild(APHs)
    S2S.appendChild(APWs)
    S2S.appendChild(BPOs)
    S2S.appendChild(BPHs)
    S2S.appendChild(BPWs)
    with open(savePath, 'w') as fp:
        dom.writexml(fp)


    ##数据存入LT_info.xml
    savePath = savepath1
    dom = minidom.parse(savePath)
    root = dom.documentElement
    root.removeChild(root.getElementsByTagName("origin")[0])
    root.removeChild(root.getElementsByTagName("T2A")[0])
    root.removeChild(root.getElementsByTagName("S2S")[0])
    root.appendChild(dom.createElement("origin"))
    root.appendChild(dom.createElement("T2A"))
    root.appendChild(dom.createElement("S2S"))
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime(
        '%Y' + '_' + '%m' + '_' + '%d' + '_' + '%H' + '_' + '%M' + '_' + '%S')
    calibration_time = root.getElementsByTagName("global_time")[0]
    calibration_time.removeChild(root.getElementsByTagName("time")[2])
    time1 = dom.createElement("time")
    calibration_time.appendChild(time1)
    time1.appendChild(dom.createTextNode(st))
    T2A = root.getElementsByTagName("T2A")[0]
    APO = dom.createElement('APO')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(rAOX)))
    APO.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(rAOY)))
    APO.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(rAOZ)))
    APO.appendChild(Z)
    APH = dom.createElement('APH')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(rAHX)))
    APH.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(rAHY)))
    APH.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(rAHZ)))
    APH.appendChild(Z)
    APW = dom.createElement('APW')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(rAWX)))
    APW.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(rAWY)))
    APW.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(rAWZ)))
    APW.appendChild(Z)
    BPO = dom.createElement('BPO')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(rBOX)))
    BPO.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(rBOY)))
    BPO.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(rBOZ)))
    BPO.appendChild(Z)
    BPH = dom.createElement('BPH')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(rBHX)))
    BPH.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(rBHY)))
    BPH.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(rBHZ)))
    BPH.appendChild(Z)
    BPW = dom.createElement('BPW')
    X = dom.createElement('X')
    X.appendChild(dom.createTextNode(str(rBWX)))
    BPW.appendChild(X)
    Y = dom.createElement('Y')
    Y.appendChild(dom.createTextNode(str(rBWY)))
    BPW.appendChild(Y)
    Z = dom.createElement('Z')
    Z.appendChild(dom.createTextNode(str(rBWZ)))
    BPW.appendChild(Z)
    T2A.appendChild(APO)
    T2A.appendChild(APH)
    T2A.appendChild(APW)
    T2A.appendChild(BPO)
    T2A.appendChild(BPH)
    T2A.appendChild(BPW)
    with open(savePath, 'w') as fp:
        dom.writexml(fp)
    return result


@cameraCalibration.route('/constructMeasureField/',methods=['POST','GET'])
def constructMeasureField():
    filePath = os.path.dirname(os.path.realpath(__file__)).replace("cameraCalibration","static/global_info.xml")
    doc = minidom.parse(filePath)
    root = doc.documentElement
    AcameraTime = root.getElementsByTagName("time")[0].childNodes[0].data
    BcameraTime = root.getElementsByTagName("time")[1].childNodes[0].data
    globalTime = root.getElementsByTagName("time")[2].childNodes[0].data
    res = dict()
    res["AcameraTime"] = AcameraTime
    res["BcameraTime"] = BcameraTime
    res["globalTime"] = globalTime
    return res





