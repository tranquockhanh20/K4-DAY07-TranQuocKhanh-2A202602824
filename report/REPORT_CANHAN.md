# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Quốc Khánh
**Nhóm:** G21
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có hướng gần nhau, cho thấy hai câu có nội dung hoặc ngữ nghĩa tương tự. Giá trị càng gần 1 thì mức tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Học phí chương trình chuẩn của HUST là 28 đến 40 triệu đồng mỗi năm.
- Câu B: Chương trình chuẩn HUST có mức học phí 28–40 triệu đồng/năm.
- Tại sao tương đồng: Hai câu cùng nói về mức học phí chương trình chuẩn HUST.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Học phí HUST được tính theo năm học.
- Câu B: Thư viện mở cửa từ tám giờ sáng.
- Tại sao khác: Một câu nói về học phí, câu còn lại nói về thời gian mở cửa thư viện.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, phù hợp để so sánh ngữ nghĩa và ít bị ảnh hưởng bởi độ dài hoặc độ lớn tuyệt đối của embedding.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Bước trượt là `500 - 50 = 450`. Số chunk = `ceil((10.000 - 50) / 450) = 23` chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk = `ceil((10.000 - 100) / (500 - 100)) = 25`. Overlap lớn hơn giữ được ngữ cảnh ở ranh giới chunk nhưng làm tăng số chunk và chi phí xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `[.!?]\s+` để tách câu, sau đó gom tối đa `max_sentences_per_chunk` câu vào một chunk. Chuỗi được `strip()` trước khi tách và số câu tối đa được bảo đảm ít nhất là 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử các separator theo thứ tự `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là ký tự đơn. Phần vượt `chunk_size` được đệ quy với separator tiếp theo, còn các phần nhỏ được ghép lại; base case là chuỗi không vượt kích thước hoặc không còn separator.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi tạo embedding cho từng document và lưu nội dung, metadata cùng vector trong bộ nhớ. Khi tìm kiếm, query được embedding rồi so sánh cosine với các vector đã lưu, sắp xếp giảm dần theo score và trả về tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata trước, yêu cầu tất cả cặp key-value khớp, rồi mới tìm kiếm trên tập ứng viên. `delete_document` loại mọi record có `metadata['doc_id']` trùng mã cần xóa và trả về `True` nếu có record bị loại.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` truy xuất `top_k` chunk, nối nội dung rồi đặt vào prompt theo cấu trúc `Context`, `Question`, `Answer`. Prompt được truyền cho `llm_fn`; demo hiện dùng LLM giả lập trả về phần xem trước prompt.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
# Chạy: .\.venv\Scripts\python.exe -m pytest tests/ -q
..........................................                               [100%]
42 passed in 0.06s
```
<!-- Chi tiết 42 test đều PASSED; kết quả được xác nhận lại trong môi trường .venv. -->
<!--
========================================= test session starts =========================================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0 -- D:\AI_in_action\lad\K4-DAY07-TranQuocKhanh-2A202602824\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\AI_in_action\lad\K4-DAY07-TranQuocKhanh-2A202602824
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED            [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                     [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED              [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED               [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                    [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED    [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED          [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED           [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED         [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                           [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED           [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                      [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                  [ 30%] 
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                            [ 33%] 
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED   [ 35%] 
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED       [ 38%] 
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%] 
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED       [ 42%] 
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                           [ 45%] 
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED             [ 47%] 
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED               [ 50%] 
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                     [ 52%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED          [ 54%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED            [ 57%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED             [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                      [ 64%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                     [ 66%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                [ 69%] 
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED            [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED       [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED            [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED       [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED           [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                 [ 78%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED            [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED       [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED           [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                 [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED           [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]          
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED      [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED     [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]       
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED    [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]     

========================================= 42 passed in 0.08s ==========================================
-->

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Học phí chuẩn HUST 28–40 triệu/năm. | Chương trình chuẩn HUST có mức 28–40 triệu/năm. | cao | -0.2728 | Không* |
| 2 | Sinh viên phải nộp học phí đúng hạn. | Người học cần thanh toán học phí theo thời hạn. | cao | -0.1016 | Không* |
| 3 | Học phí HUST tính theo năm học. | Thư viện mở cửa từ tám giờ sáng. | thấp | 0.0225 | Có |
| 4 | Học phí môn học dựa trên số tín chỉ. | Công thức tính học phí dựa trên số tín chỉ đăng ký. | cao | 0.2389 | Có |
| 5 | Elitech thu 35–68 triệu đồng/năm. | HUST có chương trình Elitech với mức 35–68 triệu/năm. | cao | 0.0453 | Không* |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là các cặp câu gần như đồng nghĩa vẫn có điểm âm hoặc rất thấp, đặc biệt cặp 1 và 2. Điều này cho thấy `_mock_embed` chỉ là embedding giả lập phục vụ kiểm thử, không phản ánh đầy đủ ngữ nghĩa tiếng Việt.

\* Kết quả được tính bằng mock embedder nên không hoàn toàn phản ánh dự đoán ngữ nghĩa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Học phí chuẩn HUST 2026–2027 dao động? | `hoc-phi-hust-2026`, chứa 28–40 triệu đồng/năm | 0.2506 | Có, top-1 | Trả về đúng khoảng 28–40 triệu đồng/năm |
| 2 | Học phí chương trình Elitech? | `hoc-phi-hust-2026` | 0.2633 | Có, top-1 | Đúng tài liệu nhưng chunk còn lẫn nội dung học bổng |
| 3 | Chương trình tài năng/quốc tế tính theo năm hay kỳ? | `hoc-phi-hust-2026` | 0.2161 | Có, top-1 | Gold là theo kỳ; cần chunk sạch hơn để trả lời rõ |
| 4 | Công thức học phí môn học ĐHKHTN? | `hus-quy-dinh-thu-hoc-phi` | 0.2281 | Có, top-1 | 165.000 đ/tín chỉ × số tín chỉ × hệ số môn học |
| 5 | HUST tăng tối đa bao nhiêu so với năm trước? | `vnua-thong-bao-thu-hoc-phi-2026` | 0.2914 | Không | Bị nhiễu, chưa trả đúng mức tăng tối đa của HUST |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Recursive chunking phù hợp hơn với tài liệu có heading và section rõ ràng, còn fixed-size dễ triển khai nhưng có thể cắt giữa ngữ cảnh. Metadata filter giúp giảm kết quả nhiễu giữa các trường.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
