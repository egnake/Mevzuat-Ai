# 🏛️ Mevzuat-AI | Türk Hukuku Asistanı

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-active-success)

**Mevzuat-AI**, hukukçular, öğrenciler ve vatandaşlar için geliştirilmiş, **%100 yerel çalışan**, gizlilik odaklı ve yapay zeka destekli bir hukuk asistanıdır. Kullanıcıların yüklediği karmaşık hukuki belgeleri (Kanunlar, İçtihatlar, Sözleşmeler) analiz eder ve RAG (Retrieval-Augmented Generation) teknolojisi ile sorularınıza **kaynaklı ve gerekçeli** yanıtlar verir.

---

## 🚀 Özellikler

*   **🔒 Tamamen Yerel ve Gizli:** Verileriniz asla cihazınızdan çıkmaz. İnternet bağlantısı gerektirmez.
*   **🧠 RAG Teknolojisi:** Belgelerinizi akıllıca parçalar, vektörel olarak saklar ve sorunuzla en alakalı kısımları bularak cevaplar.
*   **🔎 Kaynak Gösterme:** Her cevabın altında, bilginin belgenin hangi sayfasından ve hangi maddesinden alındığını gösterir.
*   **📄 Çoklu Belge Analizi:** Aynı anda birden fazla PDF dosyasını yükleyip analiz edebilirsiniz.
*   **🎨 Profesyonel Arayüz:** Modern, kullanıcı dostu ve göz yormayan "Kurumsal" tasarım.
*   **🇹🇷 Türkçe Dil Desteği:** Türkçe hukuk terminolojisine uygun prompt mühendisliği.

## 🛠️ Teknoloji Yığını

Bu proje aşağıdaki açık kaynak teknolojiler kullanılarak geliştirilmiştir:

*   **Backend:** Python, Flask
*   **AI & LLM:** LangChain, Ollama (Llama 3 / Jarvis / Mistral modelleri ile uyumlu)
*   **Vektör Veritabanı:** ChromaDB
*   **Embedding:** HuggingFace (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
*   **Frontend:** HTML5, CSS3 (Modern/Clean UI), JavaScript (Vanilla)

## ⚙️ Kurulum ve Çalıştırma

### 1. Gereksinimler

*   **Python 3.10+**: [İndir](https://www.python.org/downloads/)
*   **Ollama**: [İndir](https://ollama.com/)
    *   Kurulumdan sonra terminalden bir model çekin (Örn: `ollama pull jarvis:latest` veya `ollama pull llama3`)

### 2. Projeyi Klonlayın

```bash
git clone https://github.com/egnake/Mevzuat-Ai.git
cd Mevzuat-Ai
```

### 3. Sanal Ortam ve Bağımlılıklar

```bash
# Sanal ortam oluşturma
python -m venv .venv

# Aktif etme (Windows)
.\.venv\Scripts\Activate

# Bağımlılıkları yükleme
pip install -r requirements.txt
```

### 4. Uygulamayı Başlatın

```bash
python app.py
```

Tarayıcınızda **http://localhost:5000** adresine gidin.

## 🤝 Katkıda Bulunma

Katkılarınız memnuniyetle karşılanır! Lütfen önce bir "Issue" açarak neyi değiştirmek istediğinizi tartışın.

1.  Bu repoyu Forklayın
2.  Yeni bir Branch oluşturun (`git checkout -b feature/YeniOzellik`)
3.  Değişikliklerinizi Commit yapın (`git commit -m 'Yeni özellik eklendi'`)
4.  Branch'i Pushlayın (`git push origin feature/YeniOzellik`)
5.  Pull Request açın

## 👤 Yazar

**Ege Parlak (egnake)**

*   GitHub: [@egnake](https://github.com/egnake)
*   LinkedIn: [Ege Parlak](https://www.linkedin.com/in/ege-parlak-7b860b332/)

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
