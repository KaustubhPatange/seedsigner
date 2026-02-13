from threading import Thread
import time
import cv2

def resize_and_center_crop_240(frame_bgr: np.ndarray) -> np.ndarray:
    target = 240
    h, w = frame_bgr.shape[:2]

    # resize to 240
    if w < h:
        scale = target / w
    else:
        scale = target / h

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(frame_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # center crop
    x1 = (new_w - target) // 2
    y1 = (new_h - target) // 2

    cropped = resized[y1:y1 + target, x1:x1 + target]

    return cropped

class WebcamVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32, format="bgr", **kwargs):
        # initialize the camera
        self.camera = cv2.VideoCapture(0)
        self.set_resolution(resolution)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.should_stop = False
        self.is_stopped = True

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        self.is_stopped = False
        return self

    def update(self):
        if self.camera.isOpened():
            # keep looping infinitely until the thread is stopped
            while not self.should_stop:
                # grab the frame from the stream and clear the stream in
                # preparation for the next frame
                ret, stream = self.camera.read()
                stream = cv2.resize(stream, (240, 240))
                stream = cv2.cvtColor(stream, cv2.COLOR_BGR2RGB)
                time.sleep(0.05)
                self.frame = stream
        self.is_stopped = True
        self.should_stop = False

    def read(self):
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.should_stop = True

        # Block in this thread until stopped
        while not self.is_stopped:
            pass

    def set_resolution(self, resolution):
        self.camera.set(3, resolution[0])
        self.camera.set(4, resolution[1])

    @staticmethod
    def single_frame():
       cap = cv2.VideoCapture(0)

       # Warm-up, let auto-exposure settle in
       for _ in range(30):
          cap.read()
          time.sleep(0.01)

       ret, frame = cap.read()
       cap.release()

       if not ret:
          raise RuntimeError("Camera capture failed")

       frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
       frame = resize_and_center_crop_240(frame)
       return frame
