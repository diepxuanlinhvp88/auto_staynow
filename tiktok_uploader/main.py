from tiktok_uploader.VideoEditor import VideoEditor
from tiktok_uploader.Video import Video
import requests
from pathlib import Path
import random
from tiktok_uploader import tiktok
import shutil
import time
from datetime import datetime

def get_rooms_from_api(limit=100):
    """
    Lấy danh sách phòng từ API
    :param limit: Số lượng phòng muốn lấy
    :return: Danh sách phòng hoặc None nếu có lỗi
    """
    try:
        url = f"https://staynow.id.vn/api/v1/rooms?limit={limit}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # API trả về trực tiếp danh sách phòng
        else:
            print(f"Lỗi khi gọi API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Lỗi kết nối API: {str(e)}")
        return None

def isVideoValid(url):
   if "/gr/" in url:
       return True
   else:
       return False

def downloadFromStayNow(id, address, price, url):
    try:
        # Đảm bảo thư mục VideoInputDirPath tồn tại
        input_dir = Path("VideoInputDirPath")
        input_dir.mkdir(exist_ok=True)
        
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"VideoInputDirPath/{id}_{address}_{price}.mp4", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded video from StayNow: {id}")
            return f"VideoInputDirPath/{id}.mp4"
        else:
            print(f"Failed to download video from StayNow: {id}")
            return False
    except Exception as e:
        print(f"Error downloading video from StayNow: {e}")
        return False


def downloadVideo(list_url, address, price, id):
    for url in list_url:
        if isVideoValid(url):
            result = downloadFromStayNow(id= id, address=address, price= price, url= url)
            if result:
                print(f"Download video: {url}")
                return True
            
        else:
            print(f"không phải video hợp lệ: {url}")
    return False

def downAllVideo(ListRoom, total):
    count = 0  # Số video đã tải thành công
    index = 0  # Vị trí hiện tại trong danh sách phòng
    total_rooms = len(ListRoom)
    
    while count < total and index < total_rooms:
        print(f"Đang xử lý phòng {index + 1}/{total_rooms}")
        result = downloadVideo(ListRoom[index].get("images"), ListRoom[index].get("address"), ListRoom[index].get("price"), ListRoom[index].get("id"))
        
        if result is True:
            count += 1
            print(f"Đã tải thành công {count}/{total} videos")
        else:
            print(f"Không tìm thấy video hợp lệ từ phòng {index + 1}")
            
        index += 1
        
    if count < total:
        print(f"Chỉ tải được {count}/{total} videos vì đã hết danh sách phòng")
    else:
        print(f"Đã tải đủ {total} videos thành công!")
    return True

def format_price(price_str):
    """Convert price from "3500000" format to "3m5" format"""
    try:
        price = int(price_str)
        millions = price // 1000000
        remainder = (price % 1000000) // 100000
        if remainder > 0:
            return f"{millions}m{remainder}"
        return f"{millions}m"
    except ValueError:
        return price_str

def get_random_music():
    """Get a random music file from MusicDirPath directory"""
    music_dir = Path("MusicDirPath")
    if not music_dir.exists():
        print("Thư mục MusicDirPath không tồn tại!")
        return "MusicDirPath/music.mp3"  # return default if directory doesn't exist
        
    music_files = list(music_dir.glob("*.mp3"))
    if not music_files:
        print("Không tìm thấy file nhạc nào trong MusicDirPath!")
        return "MusicDirPath/music.mp3"  # return default if no music files
        
    random_music = random.choice(music_files)
    return str(random_music)

def process_videos():
    """
    Xử lý tất cả video trong thư mục VideoInputDirPath và lưu kết quả vào VideosDirPath
    """
    # Đảm bảo cả hai thư mục đều tồn tại
    input_dir = Path("VideoInputDirPath")
    output_dir = Path("VideosDirPath")
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Lấy danh sách tất cả file .mp4 trong thư mục input
    input_videos = list(input_dir.glob("*.mp4"))
    if not input_videos:
        print("Không tìm thấy video nào trong VideoInputDirPath!")
        return False

    print(f"Tìm thấy {len(input_videos)} video cần xử lý")
    
    for video_path in input_videos:
        try:
            print(f"Đang xử lý video: {video_path.name}")
            
            address = video_path.stem.split('_')[1]
            price = format_price(video_path.stem.split('_')[2])
            video_text = f"{address}/{price}"

            video_editor = VideoEditor(video_path)
            video_editor.change_speed(1.2)
            video_editor
            video_editor.add_audio(get_random_music())
            video_editor.add_text(str(video_text))
            video_editor.save(f"VideosDirPath/{video_path.name}")
            
            print(f"Đã xử lý xong video: {video_path}")
        except Exception as e:
            print(f"Lỗi khi xử lý video {video_path.name}: {str(e)}")
            continue

    return True

def get_cookie_files():
    """Get list of cookie files from CookiesDir"""
    cookie_dir = Path("CookiesDir")
    if not cookie_dir.exists():
        print("Thư mục CookiesDir không tồn tại!")
        return []
    
    # Lấy danh sách file .cookie và chỉ lấy phần username (bỏ qua phần "tiktok_session-" và ".cookie")
    cookie_files = []
    for f in cookie_dir.glob("*.cookie"):
        if f.stem.startswith("tiktok_session-"):
            cookie_files.append(f.stem[len("tiktok_session-"):])
        else:
            cookie_files.append(f.stem)
    
    return cookie_files

def clean_directory(directory: Path):
    """Xóa tất cả các file trong thư mục"""
    if directory.exists():
        for file in directory.glob("*"):
            if file.is_file():
                file.unlink()
        print(f"Đã xóa tất cả file trong thư mục {directory}")

def archive_videos(source_dir: Path, archive_dir: Path):
    """Di chuyển video đã xử lý vào thư mục archive với xử lý trùng tên"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = archive_dir / timestamp
        archive_path.mkdir(parents=True, exist_ok=True)
        
        for file in source_dir.glob("*.mp4"):
            target_path = archive_path / file.name
            # Xử lý trường hợp file đã tồn tại
            if target_path.exists():
                base = target_path.stem
                suffix = target_path.suffix
                counter = 1
                while target_path.exists():
                    target_path = archive_path / f"{base}_{counter}{suffix}"
                    counter += 1
            shutil.move(str(file), str(target_path))
        print(f"Đã di chuyển các file từ {source_dir} vào {archive_path}")
        return True
    except Exception as e:
        print(f"Lỗi khi archive video: {str(e)}")
        return False

def cleanup_after_upload(should_archive=True):
    """Dọn dẹp sau khi upload xong"""
    try:
        input_dir = Path("VideoInputDirPath")
        output_dir = Path("VideosDirPath")
        
        if should_archive:
            print("\n=== Đang lưu trữ video đã xử lý ===")
            # Chỉ lưu trữ video từ VideosDirPath
            archive_videos(output_dir, Path("ArchivedVideos"))
            # Xóa file trong VideoInputDirPath
            if input_dir.exists():
                clean_directory(input_dir)
        else:
            print("\n=== Đang xóa video đã xử lý ===")
            clean_directory(input_dir)
            clean_directory(output_dir)
            
        return True
    except Exception as e:
        print(f"Lỗi khi dọn dẹp: {str(e)}")
        return False

def get_random_hashtags(count=5):  # Đổi mặc định xuống 5 hashtag
    """Trả về danh sách hashtag ngẫu nhiên"""
    all_hashtags = [
        "xuhuong",
        "phongtro",
        "phongtrohanoi",
        "nhatro",
        "nhatrohanoi",
        "trothanhlap",
        "trosinhvien",
        "trogiare",
        "timmaiamhanoi",
        "phongtrodep",
        "nhatrodep",
        "thuetro",
        "timtro",
        "timphongtro",
        "nhatrogiare",
        "dichvuphongtro",
        "phongtrosinhvien",
        "viral"
    ]
    # Giới hạn số lượng hashtag để tránh tiêu đề quá dài
    max_hashtags = min(count, 5)  # Giới hạn tối đa 5 hashtag
    selected = random.sample(all_hashtags, min(max_hashtags, len(all_hashtags)))
    return " ".join([f"#{tag}" for tag in selected])

def format_video_title(video_path: Path, include_hashtags=True):
    """Format tiêu đề video với hashtag"""
    # Lấy thông tin từ tên file
    room_id = video_path.stem.split('_')[0]
    address = video_path.stem.split('_')[1]
    price = format_price(video_path.stem.split('_')[2])
    
    # Tạo tiêu đề cơ bản
    title = f"Mã phòng {room_id} - {address} - {price}"
    
    # Thêm hashtag nếu được yêu cầu
    if include_hashtags:
        hashtags = get_random_hashtags()
        title = f"{title} {hashtags}"
    
    return title

def upload_videos_to_tiktok():
    """Upload videos to TikTok with increasing schedule time"""
    try:
        # Kiểm tra thư mục VideosDirPath
        videos_dir = Path("VideosDirPath")
        if not videos_dir.exists():
            print("Thư mục VideosDirPath không tồn tại!")
            return False

        # Lấy danh sách video cần upload
        videos = list(videos_dir.glob("*.mp4"))
        if not videos:
            print("Không tìm thấy video nào trong VideosDirPath!")
            return False

        # Lấy danh sách cookie files
        cookie_files = get_cookie_files()
        if not cookie_files:
            print("Không tìm thấy file cookie nào!")
            return False

        total_videos = len(videos)
        successful_uploads = 0
        failed_uploads = 0
        
        print(f"Tìm thấy {total_videos} video và {len(cookie_files)} tài khoản")
        print("Danh sách tài khoản:", cookie_files)
        
        # Tính số nhóm upload (mỗi nhóm có số video = số cookie)
        cookies_count = len(cookie_files)
        total_groups = (len(videos) + cookies_count - 1) // cookies_count  # Làm tròn lên
        
        start_time = time.time()
        
        # Xử lý từng nhóm video
        for group in range(total_groups):
            print(f"\n=== Đang xử lý nhóm {group + 1}/{total_groups} ===")
            
            # Tính thời gian còn lại ước tính
            if group > 0:
                elapsed_time = time.time() - start_time
                avg_time_per_group = elapsed_time / group
                remaining_groups = total_groups - group
                estimated_remaining = avg_time_per_group * remaining_groups
                print(f"Ước tính thời gian còn lại: {int(estimated_remaining/60)} phút {int(estimated_remaining%60)} giây")
            
            # Lấy các video cho nhóm hiện tại
            start_idx = group * cookies_count
            end_idx = min(start_idx + cookies_count, len(videos))
            group_videos = videos[start_idx:end_idx]
            
            # Upload từng video trong nhóm với một cookie khác nhau
            for i, video in enumerate(group_videos):
                max_retries = 3
                retry_count = 0
                upload_success = False
                
                while retry_count < max_retries and not upload_success:
                    try:
                        # Format tiêu đề video với hashtag
                        title = format_video_title(video)
                        
                        # Lấy cookie tương ứng
                        current_cookie = cookie_files[i]
                        print(f"\nĐang upload video {video.name} với tài khoản {current_cookie}")
                        print(f"Tiến độ: {successful_uploads + failed_uploads + 1}/{total_videos}")
                        print(f"Tiêu đề: {title}")
                        
                        # Upload video - không dùng schedule_time nữa
                        result = tiktok.upload_video(
                            session_user=current_cookie,
                            video=str(video.name),
                            title=title,
                            schedule_time=0,  # Luôn đăng ngay lập tức
                            allow_comment=1,
                            allow_duet=0,
                            allow_stitch=0,
                            visibility_type=0
                        )
                        
                        # In ra giá trị trả về để debug
                        print(f"Giá trị trả về từ upload_video: {result}")
                        
                        # Kiểm tra kết quả upload
                        if result is None:  # Nếu hàm trả về None là thành công (vì đã in "Published successfully")
                            print(f"Upload thành công video {video.name}")
                            upload_success = True
                            successful_uploads += 1
                            break
                        else:
                            print(f"Upload thất bại video {video.name}")
                            if isinstance(result, str) and "invalid parameters" in result.lower():
                                print("Lỗi tham số không hợp lệ, có thể do tiêu đề quá dài")
                                # Thử lại với ít hashtag hơn
                                title = format_video_title(video, include_hashtags=False)
                                print(f"Thử lại với tiêu đề không có hashtag: {title}")
                            
                            # Tính thời gian chờ tăng dần
                            retry_delay = (retry_count + 1) * 10  # 10s, 20s, 30s
                            retry_count += 1
                            if retry_count < max_retries:
                                print(f"Thử lại lần {retry_count + 1} sau {retry_delay} giây...")
                                time.sleep(retry_delay)
                            
                    except Exception as e:
                        error_msg = str(e).lower()
                        print(f"Lỗi khi upload video {video.name}: {error_msg}")
                        
                        # Tính thời gian chờ tăng dần cho cả lỗi kết nối
                        retry_delay = (retry_count + 1) * 10
                        if "connection" in error_msg or "timeout" in error_msg:
                            print("Lỗi kết nối, đợi lâu hơn trước khi thử lại...")
                            retry_delay *= 2  # Tăng gấp đôi thời gian chờ cho lỗi kết nối (20s, 40s, 60s)
                        
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"Thử lại lần {retry_count + 1} sau {retry_delay} giây...")
                            time.sleep(retry_delay)
                        continue
                
                if not upload_success:
                    print(f"Đã thử {max_retries} lần nhưng không thành công với video {video.name}")
                    failed_uploads += 1
        
        # Sau khi upload hoàn tất tất cả video
        total_time = int(time.time() - start_time)
        print(f"\n=== Upload hoàn tất sau {total_time//60} phút {total_time%60} giây ===")
        print(f"Tổng số video: {total_videos}")
        print(f"Upload thành công: {successful_uploads}")
        print(f"Upload thất bại: {failed_uploads}")
        
        cleanup_after_upload(should_archive=True)  # True để archive, False để xóa
        return True
        
    except Exception as e:
        print(f"Lỗi trong quá trình upload: {str(e)}")
        return False

def count_cookies_files():
    """
    Đếm số file trong thư mục CookiesDir
    """
    cookies_dir = Path("CookiesDir")
    if not cookies_dir.exists():
        print("Thư mục CookiesDir không tồn tại!")
        return 0
    
    # Đếm tất cả các file (không tính thư mục)
    count = len([f for f in cookies_dir.iterdir() if f.is_file()])
    print(f"Số file cookies: {count}")
    return count

if __name__ == "__main__":
    # Bước 1: Tải video từ API
    cookies_count = count_cookies_files()
    if cookies_count == 0:
        print("Không có file cookies nào!")
        exit(1)
        
    total = 3 * cookies_count  
    ListRoom = get_rooms_from_api()
    
    if not ListRoom:
        print("Không thể lấy danh sách phòng từ API")
        exit(1)

    if not downAllVideo(ListRoom, total):
        print("Lỗi khi tải video từ API")
        exit(1)

    # Bước 2: Xử lý video
    print("\n=== Bắt đầu xử lý video ===")
    if not process_videos():
        print("Lỗi khi xử lý video")
        exit(1)

    # Bước 3: Upload lên TikTok
    print("\n=== Bắt đầu upload lên TikTok ===")
    if not upload_videos_to_tiktok():
        print("Lỗi khi upload lên TikTok")
        exit(1)

    print("\nHoàn thành tất cả các bước!")

    
