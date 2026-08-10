# Phiếu Phản Ánh - K3 Ngày 12

Họ và tên: Lê Mạnh Cương Mã học viên: 2A202601137

---

### Câu 1 - Fail fast (CP1)

Nếu deploy lên Render mà quên đặt AGENT_API_KEY, app phải lỗi ngay khi endpoint cần cấu hình được gọi thay vì âm thầm chạy với khóa mặc định như changeme. Trường hợp này cứu mình vì public URL đã mở ra Internet; nếu dùng khóa mặc định, người khác có thể đoán được key và gọi /ask, làm tốn quota và làm sai kết quả rate limit/cost guard. Fail fast buộc mình phát hiện thiếu secret trong log và sửa environment variable trước khi coi service là sẵn sàng.

---

### Câu 2 - Log cho máy đọc (CP1)

Một dòng log mình thu được khi gọi /ask:

{"event":"ask_completed","level":"info","timestamp":"2026-08-10T03:24:27+00:00","user_id":"local-test","tokens_in":48,"tokens_out":52,"cost_usd":0.0000384}

Với log JSON này mình có thể lọc theo event=ask_completed để đếm số request thành công, và có thể cộng cost_usd hoặc nhóm theo user_id để theo dõi chi phí từng user. Một dòng print("đã trả lời xong") không có cấu trúc nên máy khó lọc, khó cộng chi phí, và khó dựng cảnh báo.

---

### Câu 3 - Kích thước image (CP2)

| Bản                                  | Dung lượng      |
| ------------------------------------ | --------------- |
| 1 stage, dùng python:3.11 bản đầy đủ | khoảng hơn 1 GB |
| Multi-stage day12-agent:prod         | 353 MB          |

Phần chênh lệch chủ yếu đến từ base image đầy đủ của Python, các công cụ build, cache cài đặt, file không cần thiết và quyền root/runtime dư thừa. Bản multi-stage chỉ copy dependency đã cài và source cần chạy sang runtime python:3.11-slim, nên image nhỏ hơn và đạt yêu cầu dưới 500 MB.

---

### Câu 4 - Thứ tự lệnh trong Dockerfile (CP2)

Dockerfile hiện copy requirements.txt trước, chạy pip install, rồi mới copy app và utils. Khi sửa một ký tự trong app/main.py, các layer base image, WORKDIR, COPY requirements.txt, và RUN pip install vẫn dùng cache; chỉ các layer copy source và những layer sau đó cần chạy lại. Nếu đặt COPY . . trước RUN pip install, mỗi lần sửa code Docker sẽ xem context thay đổi và phải cài lại toàn bộ dependency, build chậm hơn nhiều dù requirements.txt không đổi.

---

### Câu 5 - Vì sao không chạy bằng root (CP2)

Nếu container chạy root và code Python có lỗ hổng cho phép ghi file hoặc chạy lệnh, kẻ tấn công có thể có quyền root bên trong container. Từ đó họ có thể sửa file hệ thống trong container, đọc nhiều thông tin hơn, hoặc lợi dụng cấu hình mount/socket sai để tác động ra host. Lệnh USER appuser cắt chuỗi này ở bước leo quyền: process Uvicorn chỉ chạy bằng user thường, nên kể cả app bị khai thác thì quyền trong container bị giới hạn hơn.

---

### Câu 6 - Cửa sổ trượt (CP3)

Nếu đếm theo phút đồng hồ với hạn mức 10/phút, user có thể gửi 20 request trong khoảng 2 giây: gửi 10 request ở 10:00:59, sau đó khi đồng hồ sang 10:01:00 bộ đếm reset và gửi thêm 10 request ở 10:01:01. Sliding window 60 giây tránh lỗ hổng này vì tại thời điểm 10:01:01, hệ thống vẫn nhìn lại 60 giây gần nhất và thấy 10 request cũ còn nằm trong cửa sổ.

---

### Câu 7 - Rate limit và cost guard (CP3)

Rate limit giới hạn số lượng request trong một khoảng thời gian, còn cost guard giới hạn tổng chi phí theo user trong tháng. Ví dụ rate limit cho qua nhưng cost guard chặn: user chỉ gửi 1 request nhưng request đó có prompt/history rất dài làm chi phí vượt ngân sách tháng. Ngược lại, cost guard có thể vẫn cho qua vì mỗi request rất rẻ, nhưng rate limit chặn vì user spam quá 10 request trong 60 giây.

---

### Câu 8 - /health khác /ready (CP4)

Nếu gộp /health và /ready rồi cho endpoint đó kiểm tra Redis, khi Redis mất kết nối 30 giây thì cả 3 container sẽ bắt đầu trả health check lỗi. Orchestrator tưởng process chết và restart các container, dù bản thân app vẫn sống. Các container restart đồng loạt làm mất request đang xử lý và tạo thêm nhiễu trong lúc Redis đang lỗi. Thiết kế đúng là /health chỉ kiểm tra process còn sống, còn /ready mới kiểm tra Redis để load balancer tạm ngừng gửi traffic vào instance chưa sẵn sàng.

---

### Câu 9 - Stateless (CP4)

Khi dùng Redis, nhiều instance agent cùng đọc/ghi một lịch sử nên gọi /ask nhiều lần với cùng X-User-Id sẽ thấy history_length tăng ổn định: 0, rồi 2, rồi 4... Nếu lưu trong một dict Python trong RAM, mỗi container có bộ nhớ riêng; request rơi vào instance khác sẽ thấy history rỗng hoặc số nhỏ hơn, làm agent lúc nhớ lúc quên. Redis giúp state sống ngoài process nên scale ngang vẫn nhất quán.

---

### Câu 10 - Deploy thật (CP5)

Lỗi mình gặp khi deploy Render là /health trả 200 nhưng /ready trả 503 {"status":"not ready","redis":false} hoặc trước đó /ask trả 500. Mình tìm nguyên nhân bằng cách gọi từng endpoint public: /health OK chứng tỏ app đã chạy, /ask thiếu key phải là 401, còn /ready fail chứng tỏ phần dependency/config Redis hoặc secret cloud chưa đúng. Cách sửa là đặt đúng AGENT_API_KEY trong Environment Variables của web service và dùng cặp Blueprint day12-agent + day12-redis để REDIS_URL trỏ tới Render Key Value/Valkey service. Sau khi redeploy, /ready trả {"status":"ready","redis":true} và CP5 pass.
