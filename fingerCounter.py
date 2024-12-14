import mysql.connector
import cv2
import time
import handTrackingModule as htm
import tkinter as tk
from tkinter import messagebox

# Database configuration
db_config = {
    'host': '127.0.0.1',  # Update with your database host
    'user': 'root',  # Update with your MySQL username
    'password': 'Vaibhav@2504',  # Update with your MySQL password
    'database': 'newdata',  # Update with your database name
}


class FingerMatters:
    def __init__(self):
        # Webcam settings
        self.wCam, self.hCam = 640, 480
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)

        # Initialize hand detector
        self.detector = htm.handDetector(detectionCon=0.75)
        self.tipIds = [4, 8, 12, 16, 20]

    def capture_photo(self, id):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return
        print("Press 'c' to capture the photo or 'q' to quit without capturing.")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read from camera.")
                break
            cv2.imshow("Capture", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                image_path = f'Images/{id}.jpg'
                cv2.imwrite(image_path, frame)
                print(f"Image saved at: {image_path}")
                break
            elif key == ord('q'):
                print("Exiting without capturing.")
                break
        cap.release()
        cv2.destroyAllWindows()

    def handle_login(self):
        name = self.name_input.get()
        global id
        id = self.id_input.get()
        major = self.major_input.get()
        starting_year = self.start_input.get()
        total_year = self.year_input.get()

        if name == '' or id == '' or major == '' or starting_year == '' or total_year == '':
            messagebox.showerror('Error', 'All fields are required!')
            return

        try:
            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Prepare the SQL query
            sql = """
            INSERT INTO Students (id, name, major, starting_year, total_attendance, year, last_attendance_time)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            # Insert data into the table
            cursor.execute(sql, (id, name, major, int(starting_year), 0, int(total_year)))
            conn.commit()

            messagebox.showinfo('Successful', 'Data saved to the database successfully!')

            # Capture the photo after the data is saved
            self.capture_photo(id)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            messagebox.showerror('Error', 'Failed to save data to the database.')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def if_not_found(self):
        root = tk.Tk()
        root.geometry('450x650')
        root.configure(background='#5F6F65')
        root.title("Detail Entry Form")

        text_label = tk.Label(root, text='Enter Details', fg='white', bg='#5F6F65')
        text_label.config(font=('bold', 24))
        text_label.pack()

        id_label = tk.Label(root, text='Enter ID', fg='white', bg='#5F6F65')
        id_label.config(font=('bold', 14))
        id_label.pack(pady=(20, 5))

        self.id_input = tk.Entry(root, width=50)
        self.id_input.pack(ipady=6, pady=(3, 15))

        name_label = tk.Label(root, text='Enter Name', fg='white', bg='#5F6F65')
        name_label.config(font=('bold', 14))
        name_label.pack(pady=(20, 5))

        self.name_input = tk.Entry(root, width=50)
        self.name_input.pack(ipady=6, pady=(3, 15))

        major_label = tk.Label(root, text='Enter Major', fg='white', bg='#5F6F65')
        major_label.config(font=('bold', 14))
        major_label.pack(pady=(20, 5))

        self.major_input = tk.Entry(root, width=50)
        self.major_input.pack(ipady=6, pady=(3, 15))

        start_label = tk.Label(root, text='Enter Starting Year', fg='white', bg='#5F6F65')
        start_label.config(font=('bold', 14))
        start_label.pack(pady=(20, 5))

        self.start_input = tk.Entry(root, width=50)
        self.start_input.pack(ipady=6, pady=(3, 15))

        year_label = tk.Label(root, text='Enter Total Year', fg='white', bg='#5F6F65')
        year_label.config(font=('bold', 14))
        year_label.pack(pady=(20, 5))

        self.year_input = tk.Entry(root, width=50)
        self.year_input.pack(ipady=6, pady=(3, 15))

        login_btn = tk.Button(root, text='Login Here', bg='white', fg='black', width=20, height=2,
                              command=self.handle_login)
        login_btn.pack(pady=(10, 20))
        login_btn.config(font=('bold', 10))

        root.mainloop()

    def detect_fingers(self):
        while True:
            success, img = self.cap.read()
            if not success:
                break

            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            if lmList:
                fingers = []

                # Thumb check
                fingers.append(lmList[self.tipIds[0]][1] > lmList[self.tipIds[0] - 1][1])

                # Other fingers check
                for id in range(1, 5):
                    fingers.append(lmList[self.tipIds[id]][2] < lmList[self.tipIds[id] - 2][2])

                # If index, middle, and ring fingers are raised, trigger the login screen
                if fingers[1] and fingers[2] and fingers[3] and not (fingers[0] or fingers[4]):
                    self.if_not_found()

            cv2.imshow("Image", img)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = FingerMatters()
    app.detect_fingers()