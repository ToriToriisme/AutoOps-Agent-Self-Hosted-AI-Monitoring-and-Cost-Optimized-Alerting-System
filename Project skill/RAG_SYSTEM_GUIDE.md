# Kiến thức cốt lõi về Hệ thống RAG (Retrieval-Augmented Generation)

Tài liệu này tổng hợp các kiến thức nền tảng và kiến trúc của hệ thống RAG, dựa trên bài báo cáo "Simple RAG System" để phục vụ cho dự án AutoOps Agent.

## 1. Dẫn nhập về RAG
Các mô hình ngôn ngữ lớn (LLMs) dù vô cùng mạnh mẽ nhưng vẫn luôn đối mặt với 3 điểm yếu lớn: 
- Bị giới hạn tri thức tại một thời điểm huấn luyện nhất định (Knowledge cutoff).
- Hay sinh ra hiện tượng ảo giác (Hallucination) khi gặp các câu hỏi nằm ngoài vùng kiến thức.
- Không thể truy cập vào dữ liệu riêng tư/nội bộ của cá nhân hay doanh nghiệp.

**Giải pháp:** RAG (Retrieval-Augmented Generation) ra đời cho phép LLM tiếp cận nguồn dữ liệu bên ngoài theo thời gian thực để trả lời câu hỏi, mà không cần tốn kém chi phí để fine-tuning (huấn luyện lại).

## 2. Kiến trúc RAG hiện đại (In-Context RAG)
Hệ thống RAG hiện đại chủ yếu sử dụng hướng tiếp cận **"Retrieve and Prompt"** (Tìm kiếm và Đưa vào ngữ cảnh), thay vì cập nhật trọng số của mô hình. Quy trình cơ bản gồm 3 giai đoạn chính:

### Giai đoạn 1: Indexing (Tạo chỉ mục)
Đây là quy trình chuẩn bị và xử lý dữ liệu đầu vào:
- **Document Loading:** Trích xuất văn bản thuần túy và các siêu dữ liệu (metadata như tác giả, thời gian...) từ các nguồn (PDF, TXT, Web...).
- **Text Splitting (Chunking):** Do LLM bị giới hạn số lượng token đầu vào (Context Window), ta cần cắt văn bản dài thành các đoạn nhỏ (chunks). Phương pháp tối ưu hiện nay là **Recursive Chunking** kết hợp **Chunk Overlap** (giữ lại một phần ký tự nối tiếp giữa các chunk) để không làm mất ngữ cảnh.
- **Embedding:** Sử dụng mô hình Embedding để chuyển đổi các chunk văn bản thành các vector số thực trong không gian đa chiều. Các đoạn văn có ý nghĩa tương đương sẽ có vector nằm gần nhau.
- **Vector Store:** Lưu trữ các vector và metadata vào cơ sở dữ liệu chuyên dụng (ChromaDB, FAISS, Qdrant...).

### Giai đoạn 2: Retrieval (Truy xuất dữ liệu)
Đây là bước quyết định độ chính xác của RAG:
- **Query Processing:** Mã hóa câu hỏi của người dùng thành vector truy vấn. Có thể dùng các kỹ thuật mở rộng như **Multi-Query** hoặc **HyDE** (Hypothetical Document Embeddings) để truy xuất tốt hơn dù câu hỏi ngắn hoặc lủng củng.
- **Similarity Search:** Dùng thuật toán tìm kiếm lân cận gần đúng (như HNSW) đo lường Cosine Similarity để tìm các tài liệu liên quan nhất.
- **Hybrid Search & RRF:** Kết hợp tìm kiếm theo ngữ nghĩa (Vector/Dense Search) và tìm kiếm từ khóa chính xác (Keyword/Sparse Search như BM25). Sau đó dùng thuật toán **RRF (Reciprocal Rank Fusion)** để xếp hạng lại kết quả chung.
- **Re-ranking (Lọc lại):** Dùng mô hình Cross-Encoder để chấm điểm và xếp hạng lại tập ứng viên một cách kỹ lưỡng nhất (Chiến lược cái phễu: Lấy nhiều bằng Bi-Encoder, Lọc lại ít bằng Cross-Encoder).

### Giai đoạn 3: Generation (Sinh câu trả lời)
- **Context Preparation:** Tổng hợp thông tin từ các tài liệu tìm được. Để khắc phục hiện tượng LLM hay quên khúc giữa (Lost in the Middle), ta có thể áp dụng **Context Reordering** (sắp xếp tài liệu quan trọng ra 2 đầu) hoặc **Context Compression** (nén tóm tắt).
- **Prompt Engineering:** Sử dụng kỹ thuật Zero-shot, Few-shot hoặc Chain-of-Thought (CoT - Yêu cầu LLM suy nghĩ từng bước) để định hướng câu trả lời.
- **Generation & Attribution:** LLM sinh câu trả lời dựa trên context. Điểm mạnh của RAG là có thể yêu cầu LLM trích dẫn nguồn cụ thể (Citation) để minh bạch hóa thông tin.

## 3. Vai trò của từng thành phần
Nếu thử tháo rời các module, hệ thống sẽ gặp các hạn chế sau:
- Thiếu **Embedding Model**: Hệ thống chỉ có thể tìm kiếm theo mặt chữ (Lexical Retrieval), dễ bỏ sót thông tin đồng nghĩa và cách diễn đạt tương đương.
- Thiếu **Vector Store**: Hệ thống không thể mở rộng (Unscalable Prototype), quá trình tìm kiếm sẽ cực kỳ chậm chạp và tốn tài nguyên khi dữ liệu lớn dần.
- Thiếu **LLM**: Hệ thống chỉ là một máy tìm kiếm ngữ nghĩa thông thường (Semantic Search), chỉ có thể trả về các đoạn trích dẫn chứ không thể suy luận và đối đáp linh hoạt được.

## 4. Xây dựng RAG với LangChain Framework
LangChain là "chất keo" liên kết mọi module của hệ thống RAG:
- **Document Loaders:** Hỗ trợ nạp hàng trăm định dạng file (VD: `PyPDFLoader`).
- **Text Splitters:** Tiện ích cắt nhỏ đoạn văn thông minh (VD: `RecursiveCharacterTextSplitter`).
- **Embeddings:** Giao tiếp với các nhà cung cấp mô hình (VD: `OpenAIEmbeddings`).
- **Vector Store:** Cung cấp API chuẩn cho các DB (VD: `Chroma`, `InMemoryVectorStore`).
- **Retrievers:** Bộ máy đóng gói logic tìm kiếm để dễ dàng chèn vào chuỗi xử lý (chains) của LangChain.
