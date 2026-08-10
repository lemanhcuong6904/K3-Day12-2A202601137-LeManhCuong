# Thông Tin Deploy - Checkpoint 5

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Lê Mạnh Cường |
| Mã học viên | 2A202601137 |
| Repo | https://github.com/lemanhcuong6904/K3-Day12-2A202601137-LeManhCuong |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://k3-day12-2a202601137-lemanhcuong-production.up.railway.app |
| Platform | Railway |
| Ngày deploy | 2026-08-10 |

## Biến Môi Trường Đã Set Trên Cloud

Chỉ liệt kê tên biến và nguồn giá trị, không ghi secret thật.

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | Có | Railway tự gán |
| `AGENT_API_KEY` | Có | Đặt trong Railway Variables, không nằm trong repo |
| `REDIS_URL` | Có | Reference từ Redis add-on trên Railway |
| `RATE_LIMIT_PER_MINUTE` | Có | 10 |
| `MONTHLY_BUDGET_USD` | Có | 10.0 |
| `LOG_LEVEL` | Có | INFO |

## Lệnh Kiểm Tra

```bash
curl -i https://k3-day12-2a202601137-lemanhcuong-production.up.railway.app/health
curl -i https://k3-day12-2a202601137-lemanhcuong-production.up.railway.app/ready
curl -i -X POST https://k3-day12-2a202601137-lemanhcuong-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```

## Kết Quả Chạy Thật

### Liveness

```text
HTTP/1.1 200 OK
{"status":"ok","service":"day12-agent","version":"1.0.0"}
```

### Readiness

```text
HTTP/1.1 200 OK
{"status":"ready","redis":true}
```

### Security

```text
POST /ask không có API key -> 401 Unauthorized
```

## Ảnh Chụp Màn Hình

Đặt ảnh minh chứng trong thư mục `screenshots/`:

- `screenshots/dashboard.png` - Railway dashboard service online
- `screenshots/health.png` - kết quả gọi `/health`
