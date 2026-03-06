import PyPDF2
import markovify
import re
import textwrap


def fix_spaced_out_words(match):
    return match.group(0).replace(" ", "")


def extract_and_clean_pdf(pdf_path):
    text = ""
    # Читання PDF-файлу
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "

    text = re.sub(r'[\u2022\u00B7\uF0D8\uF0A7]\s*', '', text)  # Видалення маркерів списку (Проблема: • ДТЕК)

    # Проблема: транс ‑ формації
    text = re.sub(r'([а-яА-ЯіІїЇєЄґҐ]+)(?:\s+[-‑]\s*|\s*[-‑]\s+)([а-яА-ЯіІїЇєЄґҐ]+)', r'\1\2', text)

    # Проблема: "д і л я н ц і", "Д Т Е К"
    text = re.sub(r'(?:\b[а-яА-ЯіІїЇєЄґҐA-Za-z]\s+){2,}[а-яА-ЯіІїЇєЄґҐA-Za-z]\b', fix_spaced_out_words, text)

    # Проблема: "Г рупи"
    safe_caps = "БГДЖКЛМНПРТФХЦЧШЩЬЮЇҐ"
    text = re.sub(rf'\b([{safe_caps}])\s+([а-яіїєґ]+)\b', r'\1\2', text)

    # Перенесення рядка -> пробіл
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    # Чистка пробілів перед розділовими знаками
    text = re.sub(r'\s+([.,!?:;%])', r'\1', text)
    return text.strip()


def evaluate_generation_quality(original_text, generated_text):
    print("\nМЕТРИКИ ЯКОСТІ ТЕКСТУ:\n")

    gen_words = re.findall(r'\b[а-яА-ЯіІїЇєЄґҐa-zA-Z]+\b', generated_text.lower())
    if gen_words:
        unique_words = len(set(gen_words))
        total_words = len(gen_words)
        ttr = unique_words / total_words
        print(f"1. Лексичне різноманіття (TTR): {ttr:.2f}")
        print(f"    (Унікальних слів: {unique_words} із {total_words})")
    else:
        print("1. Текст порожній.")

    orig_sentences = set([s.strip() for s in re.split(r'[.!?]', original_text) if len(s) > 15])
    gen_sentences = [s.strip() for s in re.split(r'[.!?]', generated_text) if len(s) > 15]
    if gen_sentences:
        copied_sentences = sum(1 for s in gen_sentences if s in orig_sentences)
        plagiarism_rate = (copied_sentences / len(gen_sentences)) * 100
        print(f"2. Плагіат: {plagiarism_rate:.1f}%")
        print(f"    ({copied_sentences} речень повністю скопійовано з {len(gen_sentences)} згенерованих)")


def main():
    file_name = "dtek_2020.pdf"
    dataset_text = extract_and_clean_pdf(file_name)
    text_model = markovify.Text(dataset_text, state_size=2)  # Навчання моделі Маркова

    print("\nЗГЕНЕРОВАНИЙ ЗВІТ ДТЕК:\n")
    full_generated_report = ""
    # Генерація 3 випадкових абзаців
    for _ in range(3):
        paragraph = ""
        for _ in range(4):  # 4 речення в кожному абзаці
            sentence = text_model.make_short_sentence(200, tries=100)
            if sentence:
                paragraph += sentence + " "

        if paragraph:
            full_generated_report += paragraph + "\n"
            formatted_paragraph = textwrap.fill(paragraph.strip(), width=100)
            print(formatted_paragraph)
            print()

    evaluate_generation_quality(dataset_text, full_generated_report)


if __name__ == "__main__":
    main()
