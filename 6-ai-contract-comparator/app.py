import streamlit as st
from groq import Groq
from pypdf import PdfReader
import difflib
import os
from dotenv import load_dotenv

# .env dosyasındaki API anahtarını arka planda yükle
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Sayfa Yapısı Ayarları
st.set_page_config(page_title="AI Contract Comparator", layout="wide")

# ------------------ ÇOKLU DİL SÖZLÜĞÜ (DICTIONARY) ------------------
languages = {
    "TR": {
        "title": "Akıllı Evrak & Kontrat Karşılaştırıcı",
        "subtitle": "İki PDF belgesini yükleyin. Yapay zeka arka planda sizin için tüm farkları ve riskleri anında analiz etsin.",
        "ver1": "1. Versiyon (Orijinal Metin)",
        "ver2": "2. Versiyon (Güncellenmiş Metin)",
        "pdf_placeholder": "PDF seçin",
        "diff_title": "Kelime ve Satır Bazlı Değişiklikler",
        "diff_expander": "Metinsel Değişiklik Listesini Göster",
        "diff_same": "İki belge metinsel olarak birebir aynı.",
        "added": "[EKLENDİ]",
        "deleted": "[SİLİNDİ]",
        "ai_title": "Yapay Zeka Mantıksal Fark ve Risk Analizi",
        "ai_button": "AI Analiz Raporunu Oluştur",
        "error_api": "Sistem hatası: Arka planda Groq API anahtarı bulunamadı. Lütfen .env dosyasını kontrol edin.",
        "error_pdf": "Yüklediğiniz PDF'lerden metin ayıklanamadı. PDF'lerin taranmış bir resim değil, seçilebilir metin içerdiğinden emin olun.",
        "spinner": "Yapay zeka belgeleri karşılaştırıyor, lütfen bekleyin...",
        "ai_report_header": "### Yapay Zeka Değerlendirme Raporu",
        "prompt_instruction": "Analizini kesinlikle Türkçe ve maddeler halinde anlaşılır bir dille yap."
    },
    "EN ": {
        "title": "Smart Document & Contract Comparator",
        "subtitle": "Upload two PDF documents. AI will instantly analyze all differences and risks for you in the background.",
        "ver1": "Version 1 (Original Text)",
        "ver2": "Version 2 (Updated Text)",
        "pdf_placeholder": "Choose a PDF",
        "diff_title": "Word and Line-Based Differences",
        "diff_expander": "Show Textual Differences List",
        "diff_same": "The two documents are textually identical.",
        "added": "[ADDED]",
        "deleted": "[DELETED]",
        "ai_title": " AI Logical Difference & Risk Analysis",
        "ai_button": "Generate AI Analysis Report",
        "error_api": "System error: Groq API key not found in the background. Please check the .env file.",
        "error_pdf": "Could not extract text from the uploaded PDFs. Make sure the PDFs contain selectable text, not scanned images.",
        "spinner": "AI is comparing documents, please wait...",
        "ai_report_header": "### AI Evaluation Report",
        "prompt_instruction": "Provide your analysis strictly in English, clearly and in bullet points."
    },
    "DE ": {
        "title": "Intelligenter Dokumenten- & Vertragsvergleicher",
        "subtitle": "Laden Sie zwei PDF-Dokumente hoch. Die KI analysiert im Hintergrund sofort alle Unterschiede und Risiken für Sie.",
        "ver1": "Version 1 (Originaltext)",
        "ver2": "Version 2 (Aktualisierter Text)",
        "pdf_placeholder": "PDF auswählen",
        "diff_title": "Wort- und zeilenbasierte Unterschiede",
        "diff_expander": "Textuelle Änderungsliste anzeigen",
        "diff_same": "Die beiden Dokumente sind textlich identisch.",
        "added": "[GEFÜGT]",
        "deleted": "[GELÖSCHT]",
        "ai_title": " KI-Logikdifferenz- & Risikoanalyse",
        "ai_button": "KI-Analysebericht erstellen",
        "error_api": "Systemfehler: Groq-API-Schlüssel im Hintergrund nicht gefunden. Bitte überprüfen Sie die .env-Datei.",
        "error_pdf": "Text konnte nicht aus den PDFs extrahiert werden. Stellen Sie sicher, dass die PDFs auswählbaren Text und keine gescannten Bilder enthalten.",
        "spinner": "KI vergleicht Dokumente, bitte warten...",
        "ai_report_header": "###  KI-Bewertungsbericht",
        "prompt_instruction": "Erstellen Sie Ihre Analyse ausschließlich auf Deutsch, klar und in Stichpunkten."
    },
    "FR ": {
        "title": "Comparateur Intelligent de Documents & Contrats",
        "subtitle": "Téléchargez deux documents PDF. L'IA analysera instantanément toutes les différences et les risques pour vous en arrière-plan.",
        "ver1": "Version 1 (Texte Original)",
        "ver2": "Version 2 (Texte Mis à Jour)",
        "pdf_placeholder": "Choisir un PDF",
        "diff_title": "Différences par Mots et par Lignes",
        "diff_expander": "Afficher la Liste des Différences Textuelles",
        "diff_same": "Les deux documents sont textuellement identiques.",
        "added": "[AJOUTÉ]",
        "deleted": "[SUPPRIMÉ]",
        "ai_title": " Analyse Logique & Risques par l'IA",
        "ai_button": "Générer le Rapport d'Analyse IA",
        "error_api": "Erreur système : Clé API Groq introuvable. Veuillez vérifier le fichier .env.",
        "error_pdf": " Impossible d'extraire le texte des PDF. Assurez-vous que les PDF contiennent du texte sélectionnable et non des images numérisées.",
        "spinner": "L'IA compare les documents, veuillez patienter...",
        "ai_report_header": "###  Rapport d'Évaluation de l'IA",
        "prompt_instruction": "Rédigez votre analyse exclusivement en français, de manière claire et sous forme de puces."
    },
    "ES ": {
        "title": " Comparador Inteligente de Documentos y Contratos",
        "subtitle": "Suba dos documentos PDF. La IA analizará instantáneamente todas las diferencias y riesgos en segundo plano.",
        "ver1": "Versión 1 (Texto Original)",
        "ver2": "Versión 2 (Texto Actualizado)",
        "pdf_placeholder": "Elegir un PDF",
        "diff_title": " Diferencias por Palabras y Líneas",
        "diff_expander": "Mostrar Lista de Diferencias Textuales",
        "diff_same": "Los dos documentos son idénticos textualmente.",
        "added": "[AÑADIDO]",
        "deleted": "[ELIMINADO]",
        "ai_title": " Análisis de Riesgos y Diferencias Lógicas con IA",
        "ai_button": "Generar Reporte de Análisis de IA",
        "error_api": "Error del sistema: No se encontró la clave API de Groq. Por favor, verifique el archivo .env.",
        "error_pdf": "No se pudo extraer texto de los PDF. Asegúrese de que contengan texto seleccionable y no sean imágenes escaneadas.",
        "spinner": "La IA está comparando los documentos, por favor espere...",
        "ai_report_header": "### Reporte de Evaluación de la IA",
        "prompt_instruction": "Realice su análisis estrictamente en español, de forma clara y en puntos numerados o viñetas."
    },
    "RU ": {
        "title": " Умное сравнение документов и контрактов",
        "subtitle": "Загрузите два PDF-документа. ИИ мгновенно проанализирует все различия и риски для вас в фоновом режиме.",
        "ver1": "Версия 1 (Оригинальный текст)",
        "ver2": "Версия 2 (Обновленный текст)",
        "pdf_placeholder": "Выберите PDF",
        "diff_title": " Пословные и построчные изменения",
        "diff_expander": "Показать список текстовых изменений",
        "diff_same": "Оба документа текстово абсолютно идентичны.",
        "added": "[ДОБАВЛЕНО]",
        "deleted": "[УДАЛЕНО]",
        "ai_title": "Логический анализ различий и рисков с помощью ИИ",
        "ai_button": "Создать отчет аналитики ИИ",
        "error_api": "Системная ошибка: Ключ API Groq не найден. Пожалуйста, проверьте файл .env.",
        "error_pdf": "Не удалось извлечь текст из PDF. Убедитесь, что PDF содержит выделяемый текст, а не отсканированные изображения.",
        "spinner": "ИИ сравнивает документы, пожалуйста, подождите...",
        "ai_report_header": "###  Отчет об оценке ИИ",
        "prompt_instruction": "Сделайте свой анализ строго на русском языке, четко и по пунктам."
    }
}

# ------------------ DİL SEÇİM ARAYÜZÜ (SAĞ ÜST / SIDEBAR) ------------------
st.sidebar.markdown("### Language / Dil")
selected_lang = st.sidebar.selectbox("Select Language", list(languages.keys()))
t = languages[selected_lang] # Aktif dil paketini yükle

# Başlık ve Açıklamalar (Seçilen dile göre dinamikleşti)
st.title(t["title"])
st.write(t["subtitle"])

# PDF'ten Metin Çıkarma Fonksiyonu
def extract_text_from_pdf(pdf_file):
    if pdf_file is not None:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    return ""

# Yan Yana Belge Yükleme Alanları
col1, col2 = st.columns(2)

with col1:
    st.subheader(t["ver1"])
    file1 = st.file_uploader(t["pdf_placeholder"], type=["pdf"], key="pdf1")

with col2:
    st.subheader(t["ver2"])
    file2 = st.file_uploader(t["pdf_placeholder"], type=["pdf"], key="pdf2")

# Her iki dosya da yüklendiğinde çalışacak kısım
if file1 and file2:
    text1 = extract_text_from_pdf(file1)
    text2 = extract_text_from_pdf(file2)
    
    # ------------------ 1. BÖLÜM: GÖRSEL VE KELİME BAZLI DEĞİŞİKLİKLER ------------------
    st.markdown("---")
    st.header(t["diff_title"])
    
    diff = list(difflib.ndiff(text1.splitlines(), text2.splitlines()))
    changes = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]
    
    if changes:
        with st.expander(t["diff_expander"], expanded=True):
            for line in changes:
                if line.startswith('+ '):
                    st.success(f"**{t['added']}** {line[2:]}")
                elif line.startswith('- '):
                    st.error(f"**{t['deleted']}** {line[2:]}")
    else:
        st.info(t["diff_same"])

    # ------------------ 2. BÖLÜM: ARKA PLANDAKİ GROQ AI ANALİZİ ------------------
    st.markdown("---")
    st.header(t["ai_title"])
    
    if not GROQ_API_KEY:
        st.error(t["error_api"])
    else:
        if st.button(t["ai_button"], type="primary"):
            if len(text1.strip()) == 0 or len(text2.strip()) == 0:
                st.error(t["error_pdf"])
            else:
                with st.spinner(t["spinner"]):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        
                        # Yapay zekaya seçilen dilde cevap vermesini söyleyen dinamik prompt
                        prompt = f"""
                        GÖREV: Aşağıdaki iki metнi (sözleşmeyi) birbiriyle kıyasla ve analiz et. 
                        Doğrudan bu yüklenen gerçek metinler üzerinden konuş.

                        --- ESKİ VERSİYON (METİN 1) ---
                        {text1[:4000]}

                        --- YENİ VERSİYON (METİN 2) ---
                        {text2[:4000]}
                        ---
                        
                        Lütfen yukarıdaki verilere göre şu 3 maddeyi doldur:
                        1. Maddi veya yükümlülük getiren kritik değişiklikler nelerdir?
                        2. İkinci versiyonda gözden kaçabilecek riskli veya gizlenmiş bir ekleme/çıkarma var mı?
                        3. Değişikliklerin genel özeti nedir?

                        DİL KURALI: {t['prompt_instruction']}
                        """
                        
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile",
                            temperature=0.2,
                        )
                        
                        st.balloons()
                        st.markdown(t["ai_report_header"])
                        st.write(chat_completion.choices[0].message.content)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")