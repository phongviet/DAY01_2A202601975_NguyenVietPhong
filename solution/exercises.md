# K4 — Ngày 1: Bài Tập & Phản Ánh
## Khám Phá LLM API | Phiếu Thực Hành

**Thời lượng:** 14h00–18h00
**Cách làm:** Trả lời từng câu ngay sau khi hoàn thành block tương ứng —
đừng để dồn hết về cuối buổi. Thay dòng `*Câu trả lời của bạn*` bằng câu
trả lời thật (chấm tự động sẽ đếm số câu đã trả lời).

---

## Block 1 — API Cơ Bản (trả lời sau Checkpoint 1)

### Câu 1.1 — Độ nhạy của temperature
Gọi `call_openai` với temperature 0.0, 0.7, 1.2 và 1.8 dùng prompt
**"Hãy kể cho tôi một sự thật thú vị về Hà Nội."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi? Ở mức nào phản hồi bắt đầu
kém mạch lạc?** (2–3 câu)
> Khi tăng temperature từ 0.0 đến 1.8, phản hồi chuyển từ tính nhất quán và lặp lại cao (0.0) sang tự nhiên (0.7), rồi phong phú sáng tạo hơn (1.2). Khi temperature lên đến 1.8, phản hồi bắt đầu kém mạch lạc rõ rệt, xuất hiện các cụm từ vô nghĩa, sai ngữ pháp hoặc các ký tự hỗn loạn do mô hình chọn các token có xác suất rất thấp.

### Câu 1.2 — Chọn temperature cho sản phẩm
**Bạn sẽ đặt temperature bao nhiêu cho trợ lý soạn thảo hợp đồng pháp lý,
và bao nhiêu cho trợ lý viết slogan quảng cáo? Giải thích khác biệt.**
> Nên đặt temperature = 0.0 cho trợ lý soạn thảo hợp đồng pháp lý để đảm bảo phản hồi có tính chính xác tuyệt đối, nhất quán và không tự sáng tạo ra các điều khoản hư cấu. Ngược lại, nên đặt temperature = 0.8 – 1.0 cho trợ lý viết slogan quảng cáo để khuyến khích mô hình tạo ra các ý tưởng đột phá, đa dạng và giàu hình ảnh hơn.

### Câu 1.3 — Đánh đổi chi phí
Kịch bản: 20.000 người dùng hoạt động mỗi ngày, mỗi người gọi API 2 lần,
mỗi lần trung bình ~500 token đầu ra.

**Ước tính chi phí mỗi ngày của model lớn so với model nhỏ cho workload này
(dựa trên bảng giá trong template). Nêu một trường hợp model lớn xứng đáng
với chi phí và một trường hợp model nhỏ là lựa chọn đúng:**
> Với 40.000 lượt gọi/ngày và tổng 20 triệu token đầu ra/ngày: Chi phí output cho GPT-4o là 20.000 * $0.010 = $200/ngày, trong khi GPT-4o-mini là 20.000 * $0.0006 = $12/ngày (chênh lệch hơn 16 lần). Model lớn xứng đáng khi thực hiện các tác vụ suy luận phức tạp, phân tích hợp đồng pháp lý hoặc viết mã nguồn nâng cao. Model nhỏ là lựa chọn đúng cho các tác vụ như phân loại phản hồi khách hàng, tóm tắt nhanh hoặc trả lời các câu hỏi FAQ đơn giản.

---

## Block 2 — System Prompt & Token (trả lời sau Checkpoint 2)

### Câu 2.1 — Sức mạnh của persona
Gọi `chat_with_system_prompt` hai lần với cùng câu hỏi
**"Giải thích máy học (machine learning) là gì?"** nhưng hai system prompt
khác nhau:
- "Bạn là một nhà thơ, trả lời mọi thứ bằng hình ảnh ví von, tránh thuật ngữ."
- "Bạn là kỹ sư phần mềm senior, trả lời chính xác, có ví dụ code khi phù hợp."

**Hai phản hồi khác nhau như thế nào (giọng văn, độ dài, mức kỹ thuật)?
Từ đó rút ra system prompt điều khiển được những khía cạnh nào của phản hồi?**
(3–4 câu)
> Phản hồi của nhà thơ mang giọng văn bay bổng, sử dụng các hình ảnh ví von ẩn dụ (như việc một đứa trẻ tập đi hay mầm cây lớn lên) và hoàn toàn tránh các thuật ngữ kỹ thuật. Ngược lại, phản hồi của kỹ sư senior mang giọng văn chuẩn xác, cô đọng, đi trực tiếp vào bản chất bài toán (dữ liệu đầu vào, mô hình, hàm mất mát) và cung cấp ví dụ minh họa bằng mã nguồn Python ngắn gọn. Qua đó, system prompt cho thấy khả năng điều khiển mạnh mẽ về phong cách/tông giọng (tone of voice), mức độ chuyên sâu kỹ thuật, cấu trúc/định dạng đầu ra cũng như ranh giới tri thức và persona mà model phải đóng vai.

### Câu 2.2 — tiktoken vs đếm từ
Chọn một đoạn văn tiếng Việt ~150 từ. So sánh số token theo `count_tokens`
(tiktoken) với ước lượng `số từ / 0.75` mà Part 1 đã dùng.

**Hai con số chênh nhau bao nhiêu phần trăm? Nếu dùng ước lượng thô để dự
toán ngân sách API cho ứng dụng tiếng Việt, bạn sẽ dự toán thiếu hay thừa —
và vì sao?**
> Với đoạn văn tiếng Việt ~150 từ, ước lượng thô theo công thức `150 / 0.75` cho ra khoảng 200 token. Tuy nhiên, khi dùng `tiktoken`, số token thực tế thường dao động khoảng 230–270 token tùy theo bộ mã hóa (chênh lệch cao hơn khoảng 15% – 35%). Do đó, nếu dùng công thức ước lượng thô cho tiếng Việt, bạn sẽ bị **dự toán thiếu** ngân sách. Nguyên nhân là các thuật toán tokenizer (như BPE của OpenAI) được tối ưu hóa chủ yếu cho tiếng Anh; các từ và ký tự có dấu trong tiếng Việt thường bị tách thành nhiều subword hoặc byte token hơn.

---

## Block 3 — Streaming & Độ Bền (trả lời sau Checkpoint 3)

### Câu 3.1 — Trải nghiệm người dùng với streaming
**Xét ba ứng dụng: (a) chatbot văn bản, (b) trợ lý giọng nói đọc to phản hồi,
(c) pipeline dịch tài liệu chạy ngầm ban đêm. Ứng dụng nào hưởng lợi nhiều
nhất từ streaming, ứng dụng nào không cần — và tại sao?** (1 đoạn văn)
> Chatbot văn bản (a) hưởng lợi nhiều nhất từ streaming vì giúp hiển thị ngay những ký tự đầu tiên cho người dùng, giảm thiểu cảm giác chờ đợi (TTFT - Time to First Token) và tạo trải nghiệm tương tác tự nhiên. Trợ lý giọng nói (b) cũng hưởng lợi vì có thể bắt đầu đọc từng cụm từ được stream về thay vì chờ xong cả câu. Ngược lại, pipeline dịch tài liệu ngầm ban đêm (c) không cần streaming vì đây là tác vụ xử lý hàng loạt (batch job) không tương tác trực tiếp với người dùng, việc chờ toàn bộ tài liệu hoàn thành trước khi ghi file sẽ đơn giản và hiệu quả hơn.

### Câu 3.2 — Vì sao backoff theo cấp số nhân?
**Khi API quá tải và hàng nghìn client cùng retry, exponential backoff giúp
gì so với delay cố định? Tra cứu thêm: kỹ thuật "jitter" (thêm độ trễ ngẫu
nhiên) giải quyết vấn đề gì còn sót lại?**
> Exponential backoff giúp giảm áp lực dồn dập lên máy chủ bằng cách tăng thời gian chờ theo cấp số nhân sau mỗi lần thất bại, cho phép hệ thống phía server có đủ thời gian phục hồi. Kỹ thuật "jitter" (thêm độ trễ ngẫu nhiên vào khoảng thời gian chờ) giải quyết vấn đề "Thundering Herd" — hiện tượng hàng loạt client bị lỗi cùng lúc sẽ retry vào đúng các mốc thời gian giống nhau, tạo ra các đỉnh lưu lượng đột biến lặp đi lặp lại khiến server tiếp tục bị quá tải.

---

## Block 4 — Mini-Project (trả lời sau Checkpoint 4)

### Câu 4.1 — Thiết kế persona
**Viết lại system prompt bạn dùng cho trợ lý của mình. Chỉ ra 2 chỗ trong
prompt mà nếu xóa đi, hành vi trợ lý sẽ thay đổi rõ rệt — và mô tả thay đổi
đó:**
> System prompt: *"Bạn là trợ giảng AI thân thiện của khóa học, luôn trả lời ngắn gọn dưới 3 câu và giải thích bằng tiếng Việt."*
> 1. Nếu xóa *"luôn trả lời ngắn gọn dưới 3 câu"*: Trợ lý sẽ trả lời dông dài, trình bày nhiều đoạn văn chi tiết và phân tích sâu thay vì cô đọng thông tin.
> 2. Nếu xóa *"và giải thích bằng tiếng Việt"*: Trợ lý có thể phản hồi bằng tiếng Anh hoặc tự động nhại lại ngôn ngữ mà người dùng gõ vào trong ô chat.

### Câu 4.2 — Hạn chế & cải thiện
**Trợ lý của bạn giữ history 4 lượt cuối. Hãy mô tả một tình huống hội thoại
cụ thể mà giới hạn này khiến trợ lý trả lời sai/mất ngữ cảnh, và đề xuất một
cách khắc phục (ví dụ: tóm tắt các lượt cũ, tăng giới hạn có chọn lọc...):**
> **Tình huống:** Người dùng khai báo tên hoặc bối cảnh ở lượt 1 (ví dụ: "Tôi tên là Nam, đang học lập trình Python"). Sau đó, hai bên tiếp tục trao đổi 4 lượt câu hỏi khác về các chủ đề khác nhau. Đến lượt 6, Nam hỏi "Hãy nhắc lại tên tôi là gì?". Vì history bị giới hạn trong 4 lượt gần nhất (lượt 2–5), thông tin tên ở lượt 1 đã bị cắt xả, khiến trợ lý không còn ngữ cảnh và trả lời "Tôi không biết tên bạn". **Cách khắc phục:** Áp dụng kỹ thuật tóm tắt hội thoại (conversation summarization), trong đó một mô hình nhỏ chạy ngầm tóm tắt các thông tin quan trọng từ các lượt cũ đã bị cắt và chèn bản tóm tắt đó vào đầu danh sách message/system prompt.

---

## Danh Sách Kiểm Tra Nộp Bài

- [x] `python grade.py` — xem điểm tự động, mục tiêu ≥ 75/100
- [x] Cả 4 checkpoint pytest đều pass
- [x] Tất cả 9 câu trong file này đã được trả lời
- [x] Đã copy bài làm vào folder `solution/`, push lên GitHub cá nhân và nộp link repo vào vlearn (theo hướng dẫn README)

