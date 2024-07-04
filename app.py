from flask import Flask, request, jsonify
from pytube import YouTube
import ffmpeg
import requests
import subprocess
import time

# تعریف برنامه Flask
app = Flask(__name__)

def get_most_replayed_time(id):
    try:
        # URL API با آیدی ویدیو
        api_url = f'https://yt.lemnoslife.com/videos?part=mostReplayed&id={id}'
    
        # ارسال درخواست به API
        response = requests.get(api_url)
    
        # بررسی وضعیت درخواست
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}")
    
        data = response.json()
    
        # استخراج داده‌های 'mostReplayed' از جیسون
        markers = data['items'][0]['mostReplayed']['markers']
    
        # پیدا کردن بیشترین intensityScoreNormalized از ثانیه 6 به بعد
        max_intensity = 0
        max_start_millis = 0
    
        for marker in markers:
            if marker['startMillis'] >= 6000 and marker['startMillis'] <= 45000 and marker['intensityScoreNormalized'] > max_intensity:
                max_intensity = marker['intensityScoreNormalized']
                max_start_millis = marker['startMillis']
    
        # تبدیل startMillis به فرمت HH:MM:SS
        seconds = max_start_millis // 1000
        minutes = seconds // 60
        hours = minutes // 60
        formatted_time = f"{int(hours):02}:{int(minutes % 60):02}:{int(seconds % 60):02}"
    
        return formatted_time
    except Exception as e:
        print(f"Error occurred while fetching the most replayed time: {e}")
        # مقدار پیش‌فرض در صورت بروز خطا
        return "00:00:00"



def cut_and_crop_video(input_path, output_path, start_time, duration, width, height):
    command = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-ss', start_time,
        '-t', duration,
        '-vf', f'crop={width}:{height}',
        '-c:a', 'copy',
        output_path
    ]
    subprocess.run(command)


def sendVideoNote():
    # اطلاعات ربات و چت آیدی
    bot_token = '7069807990:AAGudnd8tpTMBfQ_I_6F9nBb26hxz-KZR8E'
    chat_id = '@proxy_tunes'
    
    # فایل ویدیو برای ارسال
    files = {'video_note': open('final_video_with_audio.mp4', 'rb')}
    
    # ارسال درخواست POST به API تلگرام
    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendVideoNote', data={'chat_id': chat_id}, files=files)
    
    # بررسی پاسخ سرور
    if response.status_code == 200:
        print('Video sent successfully!')
    else:
        print(f'Failed to send video. Status code: {response.status_code}')


def main(id):
    # فراخوانی تابع و دریافت زمان پربازدید
    most_replayed_time = get_most_replayed_time(id)
    print(f"Most replayed time: {most_replayed_time}")

    time.sleep(2)

    # ویدیو را دانلود کنید
    yt = YouTube('https://www.youtube.com/watch?v=' + id)
    stream = yt.streams.filter(file_extension='mp4').first()
    stream.download(filename='downloaded_video.mp4')

    cut_start_time = most_replayed_time  # زمان شروع برش به فرمت HH:MM:SS
    cut_duration = '00:01:00'  # مدت زمان برش به فرمت HH:MM:SS
    crop_width = 360
    crop_height = 360
    cropped_video_path = 'final_video_with_audio.mp4'

    cut_and_crop_video('downloaded_video.mp4', cropped_video_path, cut_start_time, cut_duration, crop_width, crop_height)

    # ارسال ویدیو به تلگرام
    sendVideoNote()

@app.route('/')
def hi():
    return 'Hi'

# تعریف مسیر API برای دریافت URL
@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        data = request.json
        id = data.get('id')
        if not id:
            return jsonify({'error': 'ID is required'}), 400
        main(id)
        return jsonify({'status': 'success', 'message': 'Video processed and sent to Telegram'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
# اجرای برنامه Flask
if __name__ == '__main__':
    app.run(debug=True)