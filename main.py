import cv2 
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

running = False

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
smileCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

FRAME_WIDTH, FRAME_HEIGHT = 640, 480

output_dir = r'F:/TGMT/Selfie-capture/res'

def detect_smile(cap, label_image, reliability_threshold, consecutive_photos):
    global running
    true_positives = 0
    false_positives = 0
    count = 1
    accuracy = 0

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    while running:
        ret, img = cap.read()
        if not ret:
            print("Không thể đọc khung hình từ video.")
            break
        original_img = img.copy()
        grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        grayImg = cv2.GaussianBlur(grayImg, (5, 5), 0)

        faces = faceCascade.detectMultiScale(grayImg, 1.3, 3)
        smile_ratio = 0  
        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
            smiles = smileCascade.detectMultiScale(grayImg[y:y+h, x:x+w], 1.9, 20)
            smile_detected = False
            if len(faces) > 0 and len(smiles) > 0:
                    # Tính tỷ lệ nụ cười trên tổng số khuôn mặt
                        smile_ratio = len(smiles) / len(faces) * 100

                        # Kiểm tra xem tỷ lệ nụ cười có đạt ngưỡng độ tin cậy không
                        if smile_ratio >= reliability_threshold:
                            for sx, sy, sw, sh in smiles:
                                cv2.rectangle(img, (x + sx, y + sy), (x + sx + sw, y + sy + sh), (0, 0, 255), 5)

                            # Lưu ảnh khi tỷ lệ nụ cười >= độ tin cậy người dùng nhập vào
                            for _ in range(consecutive_photos):
                                now = datetime.now()
                                time_only = now.strftime("%H-%M-%S")

                                path = os.path.join(output_dir, f'img_{time_only}_{count}.jpg')
                                if cv2.imwrite(path, original_img):
                                    # Cập nhật thông báo
                                    label_notification.config(text=f"Đã chụp ảnh! Ảnh đã được lưu thành công tại: {path}")
                                    
        # Hiển thị ảnh đã chụp (giảm kích thước ảnh để không che video)
                                    img_captured = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
                                    img_pil_captured = Image.fromarray(img_captured)
                                    
                                    # Chỉnh kích thước ảnh đã chụp
                                    img_pil_captured = img_pil_captured.resize((200, 150))  # Resize ảnh đã chụp nhỏ lại
                                    img_tk_captured = ImageTk.PhotoImage(image=img_pil_captured)
                                    label_captured_image.imgtk = img_tk_captured
                                    label_captured_image.configure(image=img_tk_captured)
                                else:
                                   label_notification.config(text=f"Lỗi: Không thể lưu ảnh tại: {path}", fg="red")
                                count += 1
                            smile_detected = True
                        else:
                         # Nếu không phát hiện nụ cười, đặt giá trị mặc định
                            smile_ratio = 0

                            print("Không phát hiện nụ cười.")
            if smile_detected:
                            true_positives += 1  
            else:
                            false_positives += 1  

            if true_positives + false_positives > 0:
                            accuracy = true_positives / (true_positives + false_positives)
            else:
                            accuracy = 0

        # Hiển thị độ chính xác lên khung vẽ
        cv2.putText(img, f"ACCURACY: {accuracy:.2f}%", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        # Hiển thị độ tin cậy hiện tại lên giao diện
        cv2.putText(img, f"Smile Ratio: {smile_ratio:.2f}% (Threshold: {reliability_threshold}%)", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # Hiển thị ảnh trong giao diện
        img_resized = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        label_image.imgtk = img_tk
        label_image.configure(image=img_tk)

        window.update()
    cap.release()
def open_video_file(label_image):
    global running
    file_path = filedialog.askopenfilename(title="Chọn file video", filetypes=[("Video files", "*.mp4;*.avi")])
    if file_path:
        running = True
        btn_stop.pack(pady=5)
        btn_open_folder.pack(pady=5)
        cap = cv2.VideoCapture(file_path)
        # accuracy_threshold = int(entry_accuracy.get())
        try:
            reliability_threshold = int(entry_reliability.get())  # Chuyển đổi thành số nguyên
        except ValueError:
            print("Độ tin cậy phải là một số nguyên.")
            return  # Nếu nhập không hợp lệ, dừng hàm
        consecutive_photos = int(entry_photos.get())
        detect_smile(cap, label_image,reliability_threshold,  consecutive_photos)

def open_webcam(label_image):
    global running
    running = True
    btn_stop.pack(pady=5)
    btn_open_folder.pack(pady=5)
    cap = cv2.VideoCapture(0)
    try:
        reliability_threshold = int(entry_reliability.get())  # Chuyển đổi thành số nguyên
    except ValueError:
        print("Độ tin cậy phải là một số nguyên.")
        return  # Nếu nhập không hợp lệ, dừng hàm
    # accuracy_threshold = int(entry_accuracy.get())
    consecutive_photos = int(entry_photos.get())
    detect_smile(cap, label_image,reliability_threshold,  consecutive_photos)

def stop_camera():
    global running
    running = False
    btn_stop.pack_forget()

def open_output_folder():
    if os.path.exists(output_dir):
        os.startfile(output_dir)
    else:
        print("Thư mục không tồn tại.")


window = tk.Tk()
window.title("Smile Detection")
# Label thông báo lưu ảnh
label_notification = tk.Label(window, text="", font=("Arial", 10), fg="green")
label_notification.pack(pady=5)

# Khung chứa ảnh đã chụp
label_captured_image = tk.Label(window, text="Hình ảnh đã chụp sẽ hiển thị ở đây.", font=("Arial", 12))
label_captured_image.pack(pady=10,)

frame_input = tk.Frame(window)
frame_input.pack(pady=10)

label_reliability = tk.Label(frame_input, text="Nhập độ tin cậy (%):", font=("Arial", 12))
label_reliability.pack(side=tk.LEFT, padx=5)
entry_reliability = tk.Entry(frame_input, width=5)
entry_reliability.insert(0, "70")
entry_reliability.pack(side=tk.LEFT, padx=5)
# entry_accuracy = tk.Entry(frame_input, width=5)
# entry_accuracy.insert(0, "70")
# entry_accuracy.pack(side=tk.LEFT, padx=5)

label_photos = tk.Label(frame_input, text="Số ảnh liên tiếp:", font=("Arial", 12))
label_photos.pack(side=tk.LEFT, padx=5)
entry_photos = tk.Entry(frame_input, width=5)
entry_photos.insert(0, "1")
entry_photos.pack(side=tk.LEFT, padx=5)

frame_load = tk.Frame(window)
frame_load.pack(padx=20, pady=20)
label_load = tk.Label(
    frame_load, 
    text="NHẬN DIỆN QUA VIDEO", 
    font=("Arial", 16, "bold"),  
    fg="red"  
)
label_load.pack()
btn_load = tk.Button(
    frame_load, 
    text="Chọn tệp file video", 
    command=lambda: open_video_file(label_image),
    font=("Arial", 10, "bold"),
    bg="#4CAF50", 
    fg="white",
    relief="raised",
    bd=2,
    activebackground="#45a049",
    activeforeground="white",
    width=16,
    height=1
)
btn_load.pack(pady=5)

frame_smile = tk.Frame(window)
frame_smile.pack(pady=5)
label_smile = tk.Label(
    frame_smile, 
    text="NHẬN DIỆN TRỰC TIẾP BẰNG WEBCAM", 
    font=("Arial", 12, "bold"),
    fg="red"
)
label_smile.pack()
btn_smile = tk.Button(
    frame_smile, text="Mở Camera", 
    command=lambda: open_webcam(label_image),
    font=("Arial", 10, "bold"),
    bg="#4CAF50",
    fg="white",
    relief="raised",
    bd=2,
    activebackground="#45a049",
    activeforeground="white",
    width=15,
    height=1
)
btn_smile.pack(pady=5)

label_image = tk.Label(window, width=FRAME_WIDTH, height=FRAME_HEIGHT)
label_image.pack(padx=20, pady=20)

frame_controls = tk.Frame(window)
frame_controls.pack(pady=10)

btn_stop = tk.Button(
    frame_smile, text="Tạm Dừng",
    command=stop_camera,
    font=("Arial", 10, "bold"),
    bg="#FF0000",  
    fg="white", 
    relief="raised", 
    bd=2,  
    activebackground="#FF4D4D",  
    activeforeground="white", 
    width=15, 
    height=1  
)
btn_stop.pack(pady=5) 
btn_stop.pack_forget() 

btn_open_folder = tk.Button(
    frame_controls, text="Xem ảnh đã được chụp", 
    command=open_output_folder,
    font=("Arial", 10, "bold"),
    bg="#4CAF50",
    fg="white",
    relief="raised",
    bd=2,
    activebackground="#1C86EE",
    activeforeground="white",
    width=20,
    height=1
)
btn_open_folder.pack(side=tk.LEFT, padx=10)  
btn_open_folder.pack_forget()

label_accuracy = tk.Label(window, text="Độ chính xác: 0%", font=("Arial", 12, "bold"), fg="blue")
label_accuracy.pack(pady=2)
window.geometry("800x700")
window.mainloop()
