# PHASE 0 — KHÓA PHẠM VI

&#x20;

Trước khi code thêm bất cứ thứ gì:

## Giữ nguyên:

```
```

```
Video Upload
    ↓
DOLA API
    ↓
7 Dimension Scores
    ↓
Streamlit UI
```

Nếu cái này chưa chạy ổn định → không làm gì khác.

***

# PHASE 1 — BUILD SKILL FRAMEWORK (QUAN TRỌNG NHẤT)

Đừng làm cả 7 dimensions ngay.

## Chỉ làm Hook trước.

Tạo:

```
```

```
skills/
 └─ hook/
     ├─ curiosity_gap.py
     ├─ opening_text.py
     ├─ visual_shock.py
     └─ judge.py
```

***

## Hook Skill #1

Curiosity Gap Skill

Ví dụ đánh giá:

- &#x20;"Bạn sẽ không tin..."&#x20;
- &#x20;"Đợi đến cuối video..."&#x20;
- &#x20;"Đây là lý do..."&#x20;

Output:

```
```

```
{
  "score": 88,
  "reason": "Strong curiosity trigger"
}
```

***

## Hook Skill #2

Opening Text Skill

Đánh giá:

- &#x20;text xuất hiện sớm không&#x20;
- &#x20;text có rõ không&#x20;
- &#x20;text có mạnh không&#x20;

***

## Hook Skill #3

Visual Shock Skill

Đánh giá:

- &#x20;frame đầu có gây chú ý không&#x20;
- &#x20;chuyển động mạnh không&#x20;
- &#x20;có yếu tố bất ngờ không&#x20;

***

## Hook Judge

Nhận:

```
```

```
{
  "curiosity_gap": 88,
  "opening_text": 70,
  "visual_shock": 80
}
```

Trả:

```
```

```
{
  "hook_score": 81
}
```

***

# PHASE 2 — GẮN VÀO GUI

Đây là bước rất nhiều đội bỏ qua.

Hiện tại GUI của bạn có thể chỉ hiển thị:

```
```

```
Hook: 81
```

Sau bước này hiển thị:

```
```

```
Hook: 81

Breakdown:
✓ Curiosity Gap: 88
✓ Opening Text: 70
✓ Visual Shock: 80
```

***

# PHASE 3 — RETENTION SKILL PACK

Khi Hook chạy ổn mới làm tiếp.

Tạo:

```
```

```
skills/
 └─ retention/
```

Chỉ cần 2 skills đầu tiên:

### Pacing Skill

### Attention Decay Skill

***

# PHASE 4 — ENGAGEMENT SKILL PACK

Chỉ 2 skills:

### Emotion Skill

### Relatability Skill

***

# PHASE 5 — TREND SKILL PACK

Đây là lúc mới đụng tới trend.

Ban đầu chưa cần API trend.

Làm đơn giản:

### Trend Topic Skill

### Trend Format Skill

Dùng GPT đánh giá trước.

***

# PHASE 6 — VISUAL + AUDIO + SHAREABILITY

Mỗi dimension:

- &#x20;2 skills&#x20;
- &#x20;1 judge&#x20;

***

# KẾT QUẢ SAU PHASE 6

Bạn sẽ có:

```
```

```
7 Dimensions
    ↓
14 Skills
    ↓
7 Judges
    ↓
Fusion
    ↓
ViralScore
```

Đây đã là một kiến trúc rất thuyết phục cho hackathon.

***

# PHASE 7 — GROWTH COACH (ĂN ĐIỂM DEMO)

Sau khi có điểm.

Thêm:

```
```

```
Growth Coach
```

Ví dụ:

```
```

```
Current ViralScore: 72

Top Improvements:

1. Add stronger curiosity text in first second
2. Reduce dead time between scenes
3. Increase emotional intensity at 8–12s
```

Giám khảo thường thích phần này vì nó biến hệ từ "chấm điểm" thành "đưa ra hành động".

***

# PHASE 8 — TREND INTELLIGENCE THẬT

Lúc này mới:

- &#x20;TikTok Creative Center&#x20;
- &#x20;trending hashtags&#x20;
- &#x20;trending sounds&#x20;

và đưa vào Trend Skill Pack.

***

# Thứ tự chính xác mình khuyên

```
```

```
1. Hook Skill Pack
2. Hook Breakdown UI
3. Retention Skill Pack
4. Engagement Skill Pack
5. Trend Skill Pack
6. Visual Skill Pack
7. Audio Skill Pack
8. Shareability Skill Pack
9. Growth Coach
10. Trend Intelligence
```

