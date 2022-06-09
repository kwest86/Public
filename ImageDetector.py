import cv2
from PIL import Image,ImageTk,ImageOps
import tkinter as tk
import time
import threading
import numpy as np

#######カスタイマイズ用#######
cam_no = 0 # 表示するカメラ番号
main_canvas_size = [640,480] # カメラ画像の表示サイズ設定
#############################

class GUI(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        master.title("画像検知")
        self.selecting_area = []
        self.tgt_img = np.empty(0)
        self.founded_pts = []

    def main_window(self,master):
        # 検索パラメータ用フレーム
        parameter_frame = tk.Frame(master)
        parameter_frame.grid(row=0,column=0,sticky=tk.N)
        # 検知したい画像を表示するキャンバス
        self.tgt_img_canvas = tk.Canvas(
            parameter_frame,
            width = 200,
            height = 200,
        )
        self.tgt_img_canvas.grid(row=0,column=0,sticky=tk.N)

        # 検査対象を指定するボタン
        capture_btn = tk.Button(
            parameter_frame,
            text="検査対象指定",
            command = self.register_image)
        capture_btn.grid(row=1,column=0)

        # カメラ表示用フレーム
        cam_frame = tk.Frame(master)
        cam_frame.grid(row=0,column=1,sticky=tk.N)

        # カメラ表示用キャンバス
        self.cam_canvas = tk.Canvas(
            cam_frame,
            width=main_canvas_size[0], 
            height=main_canvas_size[1],
            highlightthickness=0)
        self.cam_canvas.grid(row=0,column=0,sticky=tk.N)

        # 座標取得機能をバインド
        self.cam_canvas.bind('<ButtonPress-1>', self.start_pickup)
        self.cam_canvas.bind('<B1-Motion>', self.pickup_coordinate)
        self.cam_canvas.bind('<ButtonRelease-1>', self.stop_pickup)

    def register_image(self):
        if not self.selecting_area:
            print("対象物を囲んで下さい")
        else:
            global tgt_img_to_canvas
            # 選択範囲から画像を切り出す
            self.tgt_img = image.cut_image(cam.cap,self.selecting_area)
            # 切り出した画像をキャンバス用に変換して表示
            tgt_img_to_canvas = draw.convert_image_to_canvas(self.tgt_img_canvas ,self.tgt_img)
            self.tgt_img_canvas.create_image(0, 0, image=tgt_img_to_canvas, anchor=tk.NW, tag="img")

    def start_pickup(self,event): # カメラキャンバスから座標値を算出(スタート)
        self.selecting_area = []
        self.selecting_area.append(self.calc_coordinate(event.x,event.y))

    def pickup_coordinate(self,event): # カメラキャンバスから座標値を算出(ドラッグ中)
        # 座標値が１つ(点)の時は第二座標を追加、２つの時は第二座標を更新
        if len(self.selecting_area) == 1:
            self.selecting_area.append(self.calc_coordinate(event.x,event.y))
        if len(self.selecting_area) == 2:
            self.selecting_area[1] = self.calc_coordinate(event.x,event.y)

    def stop_pickup(self,event): # カメラキャンバスから座標値を算出(リリース)      
        if len(self.selecting_area) == 2:
            self.selecting_area[1] = (self.calc_coordinate(event.x,event.y))
            self.selecting_area_flag = False

    def calc_coordinate(self,x,y): # キャンバスサイズとカメラ解像度から座標値を補正
        # カメラ解像度とキャンバスサイズから比率を算出
        self.w_rate = cam.cam_size[0] / self.cam_canvas.winfo_width()
        self.h_rate = cam.cam_size[1] / self.cam_canvas.winfo_height()
        # キャンバスの座標値×比率(キャプチャサイズ/キャンバスサイズ)
        x_coodinate_value = int(x * self.w_rate)
        y_coodinate_value = int(y * self.h_rate)
        return([x_coodinate_value,y_coodinate_value])

class CAM():
    def __init__(self):
        self.cam_size = []
        #self.cap = []
        self.cap = np.empty(0)

        #カメラ解像度の設定
        # (W,Hで細かく設定可能だがカメラのスペックに依る為割愛)
        CAM_VALUE = 2000
        set_w = CAM_VALUE
        set_h = CAM_VALUE
        self.capture = cv2.VideoCapture(cam_no, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, set_w)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, set_h)

        # カメラの読み込みテスト
        ret,cap = self.capture.read()
        if ret:
            # 読み込みに成功したら解像度を記憶しておく
            configured_w = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            configured_h = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.cam_size = [int(configured_w), int(configured_h)]
            print('camera', cam_no, ' ON')
            print('w:' + str(configured_w) + 'px+h:' + str(configured_h) + 'px')
        else:
            messagebox.showerror('エラー', 'カメラが見つかりませんでした')
            global exit_flag
            exit_flag = True

    def read(self):
        global exit_flag
        while not exit_flag:
            ret, read_img = self.capture.read()
            if ret:
                self.cap = read_img
            else:
                messagebox.showerror('エラー', 'カメラとの接続に失敗しました')
                exit_flag = True
            time.sleep(1/30)

class DRAW():
    def __init__(self):
        # 描画用の線幅
        self.thick = 2

    def canvas(self):

        if gui.cam_canvas and cam.cap.any(): #キャンバス生成前に処理をするとエラーが出るので回避
            
            global cam_img_to_canvas
            cam_img_to_canvas = self.convert_image_to_canvas(gui.cam_canvas,cam.cap)
            # キャンバスへ描画
            gui.cam_canvas.create_image(0, 0, image=cam_img_to_canvas, anchor=tk.NW, tag="img")

            # 指定領域の描画
            gui.cam_canvas.delete("polygon")
            self.draw_area(gui.cam_canvas,gui.selecting_area,"yellow2")

            if search.result_pts: # サーチ結果があれば描画
                self.draw_area(gui.cam_canvas,search.result_pts,"green")

        # 終了フラグが立つまでループ
        if not exit_flag:
            win.after(100, self.canvas)

    def draw_area(self,tgt_canvas,tgt_area,color):
        draw_area = []
        for i in range(len(tgt_area)):
            draw_area.append(self.getCoordinate(tgt_area[i]))
        #検査領域の描画
        if len(draw_area) == 1:  # 要素が1つの時は点
            a = draw_area[0][0]
            b = draw_area[0][1]
            r = self.thick/2
            tgt_canvas.create_oval(a-r,b-r,a+r,b+r, fill=color)
        if len(draw_area) == 2:  # 要素が2つの時は長方形
            x1 = draw_area[0][0]
            y1 = draw_area[0][1]
            x2 = draw_area[1][0]
            y2 = draw_area[1][1]
            tgt_canvas.create_rectangle(x1,y1,x2,y2, outline=color)

    def getCoordinate(self,area): # キャンバス表示用座標からカメラ用座標へ変換
        x = int(area[0] / gui.w_rate)
        y = int(area[1] / gui.h_rate)
        return([x,y])  

    def convert_image_to_canvas(self,tgt_canvas,tgt_image):# キャンバスサイズに合わせてカメラ画像をリサイズ
        w = int(tgt_canvas["width"])
        h = int(tgt_canvas["height"])
        cv_image = cv2.cvtColor(tgt_image,cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image)
        pil_image = ImageOps.pad(pil_image,(w,h))
        img = ImageTk.PhotoImage(image=pil_image)
        return(img)

class IMAGE():
    def cut_image(self,img,roi):
        # 前処理の為、listからndarrayへ変換
        roi_array = np.array(roi)
        roi_min = roi_array.min(axis=0)
        roi_max = roi_array.max(axis=0)
        roi_img = img[roi_min[1]:roi_max[1], roi_min[0]:roi_max[0]]
        return(roi_img)

class IMAGE_SEARCH():
    def __init__(self):
        self.result_pts = []
    def search(self):
        if gui.tgt_img.any(): # 検査対象の画像があれば検査
            # matchTemplateはグレースケール画像しか使えない為変換
            image_gray = cv2.cvtColor(cam.cap,cv2.COLOR_BGR2GRAY)
            tgt_gray = cv2.cvtColor(gui.tgt_img,cv2.COLOR_BGR2GRAY)
            # matchTemplateで検索
            res = cv2.matchTemplate(image_gray,tgt_gray,cv2.TM_CCOEFF_NORMED)
            # 類似度の閾値
            threshold = 0.8
            loc = np.where(res >= threshold)

            # 発見した箇所を四角枠で囲う為に検査対象画像の大きさを取得
            h,w = tgt_gray.shape

            self.result_pts = []
            for pt in zip(*loc[::-1]):
                # 発見箇所の座標値を格納
                self.result_pts.append([pt[0],pt[1]])
                self.result_pts.append([pt[0] + w, pt[1] + h])
                # 今回は一番類似度が高い結果のみ表示する為break
                break
        if not exit_flag:
            win.after(100, self.search)

# 処理を停止するフラグ
exit_flag = False

win = tk.Tk()
gui = GUI(master=win)
gui.main_window(win)

cam = CAM()
cam_read = threading.Thread(target=cam.read)
cam_read.setDaemon(True)
cam_read.start()

search = IMAGE_SEARCH()
search_automation = threading.Thread(target=search.search)
search_automation.setDaemon(True)
search_automation.start()

draw = DRAW()
canvas_update = threading.Thread(target=draw.canvas)
canvas_update.setDaemon(True)
canvas_update.start()

image = IMAGE()

gui.mainloop()