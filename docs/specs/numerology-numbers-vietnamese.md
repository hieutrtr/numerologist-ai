# Thông Số Kỹ Thuật: Các Con Số Thần Số Học
## Numerology Numbers Specification (Vietnamese)

**Phiên bản**: 1.0
**Ngày tạo**: 2025-11-21
**Dự án**: Numerologist AI

---

## Tổng Quan

Tài liệu này mô tả chi tiết về ba con số chính trong hệ thống Thần Số Học được sử dụng trong ứng dụng Numerologist AI:

1. **Life Path Number** (Số Đường Đời)
2. **Expression Number** (Số Biểu Hiện)
3. **Soul Urge Number** (Số Khát Khao Tâm Hồn)

Mỗi con số đại diện cho một khía cạnh khác nhau trong cuộc sống và tính cách của một người, cung cấp cái nhìn toàn diện về bản thân và hành trình sống.

---

## 1. Life Path Number (Số Đường Đời)

### 1.1. Định Nghĩa

**Life Path Number** là con số quan trọng nhất trong Thần Số Học, được tính từ ngày sinh của một người. Đây là con số đại diện cho hành trình cuộc đời, bài học chính, và mục đích sống của bạn.

### 1.2. Cách Tính

**Dữ liệu đầu vào**: Ngày sinh (birth_date) - Định dạng: YYYY-MM-DD

**Phương pháp**:
1. Cộng tất cả các chữ số trong ngày, tháng, và năm sinh
2. Rút gọn kết quả về một chữ số (1-9)
3. **Ngoại lệ**: Giữ nguyên số Chủ (Master Numbers): 11, 22, 33

**Ví dụ**:
```
Ngày sinh: 15/05/1990
→ Ngày: 1 + 5 = 6
→ Tháng: 0 + 5 = 5
→ Năm: 1 + 9 + 9 + 0 = 19 → 1 + 9 = 10 → 1 + 0 = 1
→ Tổng: 6 + 5 + 1 = 12 → 1 + 2 = 3
→ Life Path Number = 3
```

### 1.3. Khi Nào Cần Sử Dụng

**Tình huống phù hợp**:
- ✅ Khi người dùng muốn hiểu **hành trình cuộc đời** của họ
- ✅ Khi cần tư vấn về **định hướng nghề nghiệp** và sự nghiệp
- ✅ Khi tìm kiếm **mục đích sống** và ý nghĩa của cuộc đời
- ✅ Khi muốn hiểu về **thử thách và bài học chính** trong đời
- ✅ Khi cần lời khuyên về **con đường phát triển cá nhân**

**Câu hỏi thường gặp**:
- "Tôi sinh ra để làm gì?"
- "Con đường nào phù hợp với tôi nhất?"
- "Tại sao cuộc đời tôi có nhiều thử thách như vậy?"
- "Bài học lớn nhất tôi cần học trong đời là gì?"

### 1.4. Tại Sao Quan Trọng

**Ý nghĩa sâu sắc**:

1. **Bản Đồ Cuộc Đời**: Life Path Number như một GPS cho hành trình sống, chỉ ra con đường bạn được sinh ra để đi.

2. **Hiểu Về Bản Thân**: Giúp bạn nhận ra tại sao bạn có những xu hướng, sở thích, và thách thức nhất định.

3. **Định Hướng Quyết Định**: Cung cấp nguyên tắc chỉ dẫn để đưa ra các quyết định lớn trong cuộc sống (nghề nghiệp, quan hệ, nơi ở).

4. **Chấp Nhận Bản Thân**: Giúp bạn chấp nhận những điểm yếu và khai thác điểm mạnh một cách tự nhiên.

**Điểm khác biệt**: Không giống các con số khác có thể thay đổi theo tên (khi kết hôn, đổi tên), Life Path Number **KHÔNG BAO GIỜ THAY ĐỔI** - nó là dấu ấn định mệnh từ khi bạn sinh ra.

### 1.5. Thông Tin Tiết Lộ

Life Path Number tiết lộ:
- ✨ Tài năng và khả năng tự nhiên
- ✨ Thử thách và bài học chính trong đời
- ✨ Phong cách làm việc và tương tác với người khác
- ✨ Loại nghề nghiệp và môi trường làm việc phù hợp
- ✨ Cách tiếp cận tình yêu và các mối quan hệ
- ✨ Mục đích sống và sứ mệnh tâm linh

---

## 2. Expression Number (Số Biểu Hiện)

### 2.1. Định Nghĩa

**Expression Number** (còn gọi là Destiny Number - Số Số Mệnh) được tính từ họ tên đầy đủ khi sinh. Con số này đại diện cho khả năng, tài năng tự nhiên, và cách bạn thể hiện bản thân với thế giới bên ngoài.

### 2.2. Cách Tính

**Dữ liệu đầu vào**: Họ tên đầy đủ (full_name) - Tên khai sinh chính thức

**Phương pháp**:
1. Gán giá trị số cho mỗi chữ cái (A=1, B=2, ... Z=26)
2. Cộng tất cả các giá trị số của TẤT CẢ các chữ cái trong tên
3. Rút gọn về một chữ số (1-9) hoặc số Chủ (11, 22, 33)

**Bảng chuyển đổi**:
```
A=1  B=2  C=3  D=4  E=5  F=6  G=7  H=8  I=9
J=1  K=2  L=3  M=4  N=5  O=6  P=7  Q=8  R=9
S=1  T=2  U=3  V=4  W=5  X=6  Y=7  Z=8
```

**Ví dụ**:
```
Họ tên: NGUYEN VAN ANH
→ N(5) + G(7) + U(3) + Y(7) + E(5) + N(5) = 32
→ V(4) + A(1) + N(5) = 10
→ A(1) + N(5) + H(8) = 14
→ Tổng: 32 + 10 + 14 = 56 → 5 + 6 = 11
→ Expression Number = 11 (Số Chủ, không rút gọn)
```

### 2.3. Khi Nào Cần Sử Dụng

**Tình huống phù hợp**:
- ✅ Khi người dùng muốn khám phá **tài năng thiên bẩm**
- ✅ Khi cần hiểu về **phong cách giao tiếp** và cách biểu đạt
- ✅ Khi tìm kiếm **điểm mạnh cá nhân** để phát triển
- ✅ Khi muốn biết **vai trò tự nhiên** trong nhóm/tổ chức
- ✅ Khi cần lời khuyên về **phát triển kỹ năng** và năng lực

**Câu hỏi thường gặp**:
- "Tôi giỏi về lĩnh vực nào?"
- "Tài năng tự nhiên của tôi là gì?"
- "Tôi nên phát triển kỹ năng nào?"
- "Làm thế nào để tôi tỏa sáng trong công việc?"
- "Tại sao người khác nhìn tôi theo cách đó?"

### 2.4. Tại Sao Quan Trọng

**Ý nghĩa sâu sắc**:

1. **Danh Tính Công Khai**: Expression Number thể hiện cách thế giới nhìn nhận bạn - "mặt nạ công khai" của bạn.

2. **Tài Năng Thiên Bẩm**: Chỉ ra những khả năng tự nhiên mà bạn được sinh ra để phát triển và sử dụng.

3. **Phong Cách Làm Việc**: Giúp hiểu cách bạn tiếp cận công việc, giải quyết vấn đề, và tương tác với đồng nghiệp.

4. **Sự Phù Hợp Nghề Nghiệp**: Chỉ dẫn về loại công việc, vai trò, và môi trường nơi bạn có thể phát huy tốt nhất.

**Lưu ý đặc biệt**:
- Expression Number **CÓ THỂ THAY ĐỔI** nếu bạn đổi tên (kết hôn, pháp danh, nghệ danh)
- Tên mới sẽ tạo ra Expression Number mới, ảnh hưởng đến cách bạn biểu hiện trong giai đoạn mới
- Luôn sử dụng **TÊN KHAI SINH** để tính số gốc

### 2.5. Thông Tin Tiết Lộ

Expression Number tiết lộ:
- ✨ Tài năng và khả năng đặc biệt
- ✨ Phong cách giao tiếp và thể hiện
- ✨ Cách người khác cảm nhận về bạn
- ✨ Tiềm năng nghề nghiệp và vai trò phù hợp
- ✨ Phương thức làm việc hiệu quả nhất
- ✨ Kỹ năng cần phát triển để thành công

---

## 3. Soul Urge Number (Số Khát Khao Tâm Hồn)

### 3.1. Định Nghĩa

**Soul Urge Number** (còn gọi là Heart's Desire Number - Số Mong Muốn Trái Tim) được tính từ các **NGUYÊN ÂM** trong họ tên. Con số này đại diện cho khát vọng sâu thẳm, động lực nội tại, và những gì thực sự làm bạn hạnh phúc.

### 3.2. Cách Tính

**Dữ liệu đầu vào**: Họ tên đầy đủ (full_name) - Tên khai sinh chính thức

**Phương pháp**:
1. Chỉ lấy các NGUYÊN ÂM (A, E, I, O, U) trong tên
2. Gán giá trị số cho mỗi nguyên âm (A=1, E=5, I=9, O=6, U=3)
3. Cộng tất cả các giá trị
4. Rút gọn về một chữ số (1-9) hoặc số Chủ (11, 22, 33)

**Nguyên tắc đặc biệt**:
- Chữ **Y** được coi là nguyên âm nếu nó phát âm như nguyên âm (ví dụ: "Lynn" → Y là nguyên âm)
- Chữ **W** đôi khi là nguyên âm trong một số tên (ví dụ: "Gwen")

**Ví dụ**:
```
Họ tên: TRAN THI MAI
Nguyên âm: A (1) + I (9) + A (1) + I (9) = 20 → 2 + 0 = 2
→ Soul Urge Number = 2
```

### 3.3. Khi Nào Cần Sử Dụng

**Tình huống phù hợp**:
- ✅ Khi người dùng muốn hiểu **động lực thực sự** của mình
- ✅ Khi cảm thấy **mất phương hướng** hoặc không hạnh phúc
- ✅ Khi cần tìm kiếm **ý nghĩa và mục đích sâu sắc**
- ✅ Khi muốn biết **điều gì làm mình thỏa mãn** thực sự
- ✅ Khi tìm kiếm **sự cân bằng nội tâm** và hạnh phúc

**Câu hỏi thường gặp**:
- "Điều gì thực sự làm tôi hạnh phúc?"
- "Tại sao tôi cảm thấy trống rỗng dù đã có mọi thứ?"
- "Khát vọng sâu thẳm của tôi là gì?"
- "Làm thế nào để tôi sống đúng với bản thân?"
- "Tại sao tôi luôn cảm thấy có gì đó thiếu?"

### 3.4. Tại Sao Quan Trọng

**Ý nghĩa sâu sắc**:

1. **Giọng Nói Nội Tâm**: Soul Urge Number là tiếng nói của tâm hồn - những gì bạn thực sự mong muốn, không phải điều người khác kỳ vọng.

2. **Động Lực Thực Sự**: Giúp hiểu động lực sâu xa đằng sau hành động và quyết định của bạn.

3. **Hạnh Phúc Bền Vững**: Chỉ ra con đường dẫn đến sự thỏa mãn và hạnh phúc lâu dài, không chỉ thành công bề ngoài.

4. **Xung Đột Nội Tâm**: Giúp giải quyết mâu thuẫn giữa điều bạn làm (Expression) và điều bạn muốn (Soul Urge).

**Điểm đặc biệt**:
- Soul Urge Number thường là con số **RIÊNG TƯ NHẤT** - chỉ những người thân thiết mới thấy được
- Khi Expression và Soul Urge Number khác nhau nhiều → Có thể cảm thấy mâu thuẫn nội tâm
- Khi hai số này hài hòa → Cảm giác sống đúng với bản thân, hạnh phúc và thỏa mãn

### 3.5. Thông Tin Tiết Lộ

Soul Urge Number tiết lộ:
- ✨ Khát vọng và mong muốn sâu thẳm
- ✨ Động lực nội tại thực sự
- ✨ Điều gì mang lại hạnh phúc chân thật
- ✨ Giá trị cốt lõi và niềm tin
- ✨ Nhu cầu tình cảm và tinh thần
- ✨ Con đường đến sự thỏa mãn tâm hồn

---

## 4. So Sánh Ba Con Số

### 4.1. Bảng So Sánh Tổng Quan

| Tiêu Chí | Life Path | Expression | Soul Urge |
|----------|-----------|------------|-----------|
| **Tính từ** | Ngày sinh | Tất cả chữ cái | Chỉ nguyên âm |
| **Đại diện** | Hành trình đời | Tài năng & biểu hiện | Khát vọng nội tâm |
| **Câu hỏi** | "Tôi đến đây để làm gì?" | "Tôi có thể làm gì?" | "Tôi muốn gì?" |
| **Thay đổi** | KHÔNG | Có (khi đổi tên) | Có (khi đổi tên) |
| **Mức độ công khai** | Công khai | Rất công khai | Riêng tư |
| **Ưu tiên** | #1 Quan trọng nhất | #2 | #3 |

### 4.2. Mối Quan Hệ Giữa Ba Con Số

```
┌─────────────────────────────────────────┐
│         CUỘC ĐỜI CỦA BẠN               │
├─────────────────────────────────────────┤
│                                         │
│  Life Path (Số Đường Đời)              │
│  ↓                                      │
│  CON ĐƯỜNG → Hành trình bạn phải đi    │
│                                         │
│  Expression (Số Biểu Hiện)             │
│  ↓                                      │
│  CÔNG CỤ → Tài năng để đi con đường   │
│                                         │
│  Soul Urge (Số Khát Khao)              │
│  ↓                                      │
│  NHIÊN LIỆU → Động lực để tiếp tục    │
│                                         │
└─────────────────────────────────────────┘
```

**Ví dụ thực tế**:
- **Life Path 7**: Đường đời của nhà tư tưởng, nhà nghiên cứu
- **Expression 3**: Tài năng giao tiếp và sáng tạo
- **Soul Urge 9**: Khát khao giúp đỡ nhân loại

→ **Kết hợp**: Người này có thể trở thành một nhà giáo dục/nhà khoa học truyền thông, sử dụng tài năng giao tiếp để chia sẻ kiến thức sâu sắc, được thúc đẩy bởi mong muốn giúp đỡ người khác.

### 4.3. Khi Nào Nên Tính Số Nào?

**Trình tự khuyến nghị trong cuộc trò chuyện**:

1. **BẮT ĐẦU**: Life Path Number
   - Đây là nền tảng, quan trọng nhất
   - Cung cấp bức tranh tổng quan về cuộc đời

2. **TIẾP THEO**: Expression Number
   - Bổ sung thông tin về cách thực hiện Life Path
   - Chỉ ra công cụ và tài năng có sẵn

3. **CUỐI CÙNG**: Soul Urge Number
   - Giúp hiểu động lực nội tâm
   - Đảm bảo hành trình phù hợp với khát vọng

**Trường hợp đặc biệt**:
- Nếu người dùng cảm thấy **mất phương hướng** → Bắt đầu với Soul Urge để tìm lại động lực
- Nếu người dùng muốn **phát triển sự nghiệp** → Tập trung vào Expression + Life Path
- Nếu người dùng tìm kiếm **ý nghĩa cuộc sống** → Ưu tiên Life Path + Soul Urge

---

## 5. Số Chủ (Master Numbers)

### 5.1. Định Nghĩa

**Số Chủ** là các con số đặc biệt trong Thần Số Học: **11, 22, 33**. Chúng mang năng lượng mạnh mẽ và tiềm năng cao hơn, nhưng cũng đi kèm với thử thách lớn hơn.

### 5.2. Quy Tắc Xử Lý

**QUAN TRỌNG**: Khi tính toán, KHÔNG rút gọn các số sau:
- ✅ **11** (không rút thành 2)
- ✅ **22** (không rút thành 4)
- ✅ **33** (không rút thành 6)

**Lý do**: Số Chủ mang ý nghĩa và rung động khác biệt so với số rút gọn.

### 5.3. Ý Nghĩa Đặc Biệt

**Master Number 11** - Người Soi Đường
- Trực giác cao, nhạy cảm tâm linh
- Thử thách: Căng thẳng thần kinh, áp lực cao

**Master Number 22** - Kiến Trúc Sư Vĩ Đại
- Khả năng biến ý tưởng thành hiện thực
- Thử thách: Áp lực thành công, hoàn hảo chủ nghĩa

**Master Number 33** - Thầy Giáo Vĩ Đại
- Yêu thương vô điều kiện, chữa lành
- Thử thách: Hy sinh bản thân, kiệt sức

---

## 6. Hướng Dẫn Triển Khai

### 6.1. Flow Chart Quyết Định

```
Người dùng bắt đầu trò chuyện
         ↓
    Hỏi ngày sinh?
         ↓
    [Có] → Tính Life Path
         ↓
    Hỏi họ tên?
         ↓
    [Có] → Tính Expression + Soul Urge
         ↓
    Người dùng hỏi về tính cách?
         ↓
    → Lấy interpretation từ database
         ↓
    Trả lời với ngữ cảnh phù hợp
```

### 6.2. Validation Rules

**Life Path Number**:
- ✅ Ngày sinh phải hợp lệ (không phải tương lai)
- ✅ Định dạng: YYYY-MM-DD
- ✅ Năm hợp lý (1900 - năm hiện tại)

**Expression Number**:
- ✅ Tên không được rỗng
- ✅ Chứa ít nhất một chữ cái
- ✅ Sử dụng tên khai sinh chính thức

**Soul Urge Number**:
- ✅ Tên không được rỗng
- ✅ Chứa ít nhất một nguyên âm
- ✅ Sử dụng tên khai sinh chính thức

### 6.3. Error Handling

**Lỗi thường gặp**:

1. **InvalidDate**: Ngày sinh không hợp lệ
   - Message: "Định dạng ngày sinh không đúng. Vui lòng sử dụng YYYY-MM-DD (ví dụ: 1990-05-15)"

2. **InvalidName**: Tên không hợp lệ
   - Message: "Vui lòng cung cấp họ tên đầy đủ"

3. **CalculationError**: Lỗi tính toán
   - Message: "Không thể tính toán được. Vui lòng thử lại."

4. **DatabaseError**: Lỗi truy vấn dữ liệu
   - Message: "Không thể lấy thông tin giải nghĩa. Vui lòng thử lại."

---

## 7. Ví Dụ Thực Tế

### 7.1. Kịch Bản Hoàn Chỉnh

**Người dùng**: "Tôi sinh ngày 15/05/1990, tên là Nguyễn Văn Anh"

**Hệ thống xử lý**:

1. **Tính Life Path**:
   - Input: 1990-05-15
   - Calculation: 1+5+0+5+1+9+9+0 = 30 → 3
   - Result: Life Path = 3

2. **Tính Expression**:
   - Input: "NGUYEN VAN ANH"
   - Calculation: (5+7+3+7+5+5) + (4+1+5) + (1+5+8) = 56 → 11
   - Result: Expression = 11 (Master Number)

3. **Tính Soul Urge**:
   - Input: "NGUYEN VAN ANH"
   - Vowels: U(3) + E(5) + A(1) + A(1) = 10 → 1
   - Result: Soul Urge = 1

**Phân tích kết hợp**:
- **Life Path 3**: Người sáng tạo, giao tiếp tốt, nghệ sĩ
- **Expression 11**: Trực giác cao, có thể truyền cảm hứng cho người khác
- **Soul Urge 1**: Khát khao độc lập, lãnh đạo, đổi mới

→ **Tổng hợp**: Một nhà sáng tạo nội dung, diễn giả, hoặc nhà tư vấn có khả năng truyền cảm hứng mạnh mẽ, được thúc đẩy bởi mong muốn tạo ra tác động độc đáo và dẫn dắt người khác.

---

## 8. Best Practices

### 8.1. Thứ Tự Ưu Tiên

1. **Luôn tính Life Path trước tiên** - Đây là nền tảng
2. Nếu có tên → Tính cả Expression và Soul Urge cùng lúc
3. Chỉ lấy interpretation khi đã có số cụ thể
4. Giải thích ý nghĩa trong ngữ cảnh của câu hỏi người dùng

### 8.2. Giao Tiếp với Người Dùng

**NÊN**:
- ✅ Giải thích ý nghĩa bằng ngôn ngữ đời thường
- ✅ Kết nối các con số với tình huống thực tế
- ✅ Nhấn mạnh điểm mạnh trước, sau đó là thách thức
- ✅ Khuyến khích sự phát triển và tự nhận thức

**KHÔNG NÊN**:
- ❌ Sử dụng thuật ngữ kỹ thuật quá nhiều
- ❌ Đưa ra lời tiên đoán tuyệt đối
- ❌ Tạo áp lực hoặc lo lắng không cần thiết
- ❌ So sánh hoặc phán xét con số nào tốt/xấu hơn

### 8.3. Privacy & Security

**Dữ liệu nhạy cảm**:
- 🔒 Ngày sinh: Personal Identifiable Information (PII)
- 🔒 Họ tên: PII
- 🔒 Lưu trữ theo GDPR compliance
- 🔒 Không chia sẻ với bên thứ ba

**Logging**:
- ✅ Log số đã tính (Life Path, Expression, Soul Urge)
- ❌ KHÔNG log ngày sinh hoặc họ tên đầy đủ
- ✅ Chỉ log user_id và timestamp

---

## 9. Tài Liệu Tham Khảo

### 9.1. Implementation Files

- `backend/src/voice_pipeline/function_handlers.py`: Handler functions
- `backend/src/services/numerology_service.py`: Calculation logic
- `backend/src/models/numerology_interpretation.py`: Database model
- `backend/src/voice_pipeline/numerology_functions.py`: Function schemas

### 9.2. Database Schema

```sql
-- NumerologyInterpretation table structure
CREATE TABLE numerology_interpretation (
    id UUID PRIMARY KEY,
    number_type VARCHAR,  -- 'life_path', 'expression', 'soul_urge'
    number_value INTEGER, -- 1-9, 11, 22, 33
    category VARCHAR,     -- 'personality', 'strengths', 'challenges', etc.
    content TEXT,         -- Interpretation text
    language VARCHAR,     -- 'en', 'vi'
    version INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 9.3. API Endpoints

```
POST /api/v1/conversations/start
  → Bắt đầu session với Pipecat bot

GET /api/v1/numerology/profile
  → Lấy profile thần số học đầy đủ của user

POST /api/v1/numerology/calculate
  → Tính số cụ thể (life_path, expression, soul_urge)
```

---

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-21 | Tài liệu ban đầu - Đầy đủ 3 con số chính |

---

**Ghi chú**: Tài liệu này là living document và sẽ được cập nhật khi có thêm tính năng mới (Birthday Number, Personal Year, etc.)
