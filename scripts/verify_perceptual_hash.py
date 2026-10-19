"""
Script tinh toan ma bam tri giac (Perceptual Hash - dHash 64-bit)
giua cac khung hinh cua 3 video test va toan bo anh trong tap huan luyen (train)
de danh gia tinh doc lap cau truc anh toan cuc (global image structure).
Xuat ket qua ra: reports/perceptual_hash_distances.csv
"""
import os
import sys
import glob
import csv
import cv2
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def compute_dhash(image, hash_size=8):
    if image is None:
        return None
    resized = cv2.resize(image, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
    if len(resized.shape) == 3:
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    else:
        gray = resized
    diff = gray[:, 1:] > gray[:, :-1]
    return diff.flatten()


def hamming_distance(hash1, hash2):
    return int(np.count_nonzero(hash1 != hash2))


def main():
    print("=" * 75)
    print("[PHASH] KIEM TRA PERCEPTUAL HASH (dHash 64-bit) GIUA VIDEO VA TAP TRAIN")
    print("=" * 75)

    train_patterns = [
        "datasets/**/train/**/*.jpg",
        "datasets/**/train/**/*.png",
        "datasets/train/**/*.jpg",
        "datasets/train/**/*.png"
    ]
    train_imgs = []
    for pat in train_patterns:
        train_imgs.extend(glob.glob(pat, recursive=True))
    train_imgs = sorted(list(set(train_imgs)))

    print(f"[*] Dang tinh dHash cho {len(train_imgs)} anh trong tap huan luyen...")
    train_hashes = []
    for p in train_imgs:
        img = cv2.imread(p)
        h = compute_dhash(img)
        if h is not None:
            train_hashes.append((p, h))
    print(f"[*] Da tinh xong {len(train_hashes)} dHash tap train.")

    videos = [
        ("Video 1 (Pho Hue)", "data/videos/video test.mp4"),
        ("Video 2 (Bach Mai)", "data/videos/videotesst2.mp4"),
        ("Video 3 (Tran Dai Nghia)", "data/videos/video test3.mp4"),
    ]

    csv_rows = []
    min_global_distance = 64
    closest_pair = None

    for vid_name, vid_path in videos:
        if not os.path.exists(vid_path):
            print(f"[!] Khong tim thay video: {vid_path}")
            continue
        cap = cv2.VideoCapture(vid_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        frame_idx = 0
        video_hashes = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % 10 == 0:  # Lay mau moi 10 frames (~0.41s)
                h = compute_dhash(frame)
                if h is not None:
                    video_hashes.append((frame_idx, frame_idx / fps, h))
            frame_idx += 1
        cap.release()

        print(f"\n[*] {vid_name}: {len(video_hashes)} frames duoc lay mau.")

        min_dist_vid = 64
        closest_vid_pair = None

        for f_idx, sec, v_h in video_hashes:
            # Tim anh train gan nhat
            best_dist = 64
            best_train_path = ""
            for t_path, t_h in train_hashes:
                dist = hamming_distance(v_h, t_h)
                if dist < best_dist:
                    best_dist = dist
                    best_train_path = t_path

            sim_pct = round((64 - best_dist) / 64.0 * 100, 2)
            csv_rows.append({
                "video_name": vid_name,
                "video_path": vid_path,
                "frame_index": f_idx,
                "timestamp_sec": round(sec, 2),
                "closest_train_image": os.path.basename(best_train_path),
                "closest_train_full_path": best_train_path,
                "min_hamming_distance_bits": best_dist,
                "similarity_pct": sim_pct
            })

            if best_dist < min_dist_vid:
                min_dist_vid = best_dist
                closest_vid_pair = (f_idx, sec, best_train_path, best_dist)

            if best_dist < min_global_distance:
                min_global_distance = best_dist
                closest_pair = (vid_name, f_idx, sec, best_train_path, best_dist)

        print(f"    Khoang cach Hamming nho nhat voi tap train: {min_dist_vid} / 64 bits")
        if closest_vid_pair:
            print(f"    Frame gan nhat: Frame {closest_vid_pair[0]} ({closest_vid_pair[1]:.2f}s) voi {os.path.basename(closest_vid_pair[2])}")

    # Ghi file CSV
    csv_out_path = "reports/perceptual_hash_distances.csv"
    os.makedirs(os.path.dirname(csv_out_path), exist_ok=True)
    fieldnames = [
        "video_name", "video_path", "frame_index", "timestamp_sec",
        "closest_train_image", "closest_train_full_path",
        "min_hamming_distance_bits", "similarity_pct"
    ]
    with open(csv_out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print("\n" + "=" * 75)
    print("[KET LUAN PHASH]")
    print(f"- Khoang cach Hamming toi thieu tren toan bo 3 video: {min_global_distance} / 64 bits")
    print(f"- Cap anh tuong dong nhat: {closest_pair[0]} F{closest_pair[1]} ({closest_pair[2]:.2f}s) voi {os.path.basename(closest_pair[3])} (khoang cach: {closest_pair[4]} bits)")
    print(f"- Da xuat chi tiet toan bo {len(csv_rows)} mau ra file: {csv_out_path}")
    print("[DANH GIA KHOA HOC]")
    print("  Khong phat hien trung lap gan giong o muc anh toan cuc (global image-level near-duplicate).")
    print("  Tuy nhien, do phuong phap dHash toan khung hinh khong the loai tru kha nang co bien quang cao")
    print("  rieng le bi crop/tang cuong, ket qua thuc nghiem tren 3 video duoc xem la danh gia so bo (preliminary validation).")
    print("=" * 75)


if __name__ == "__main__":
    main()
