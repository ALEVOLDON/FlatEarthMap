import os
import sys
import time
import subprocess
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY", "")
WORKDIR = r"C:\Users\alevo\.gemini\antigravity\scratch\femap_presentation"
AUDIO_DIR = os.path.join(WORKDIR, "audio_gemini")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE_NAME = "Charon"  # Deep, engaging documentary narrator
MODEL_NAME = "gemini-3.8-flash-tts"

SCENES = [
    {
        "id": 1,
        "text": (
            "Всем привет! Сегодня мы детально разберём один из самых любопытных и технически проработанных интерактивных проектов — Flat Earth Map версии 6.4.2. "
            "На первый взгляд это классическая дисковая карта мира, но под капотом здесь скрывается мощнейший математический движок, "
            "объединяющий библиотеку D3, реальные астрономические расчёты и орбитальную механику. Давайте посмотрим, как это устроено!"
        )
    },
    {
        "id": 2,
        "text": (
            "Начнём с самого главного — с геометрии. В основе сайта лежит азимутальная эквидистантная проекция. "
            "Обычно её центрируют на Северном полюсе — так получается знаменитая карта Глисона. "
            "Но смотрите, что произойдёт, если мы переключим центр на Южный полюс: Антарктида мгновенно становится центром мира, "
            "а Евразия и Америка растягиваются в циклопические кольца на горизонте! "
            "Можно выбрать экватор или ввести координаты любого города, например Москвы — и сразу увидеть, как плоскость неизбежно искажает реальные формы континентов."
        )
    },
    {
        "id": 3,
        "text": (
            "Интерфейс спроектирован очень гибко. Мы можем в один клик включить координатную сетку с шагом 30 градусов, "
            "подписи параллелей и меридианов, а также метки крупнейших мировых столиц и полярных станций Антарктиды — от станции Восток до Амундсен-Скотт. "
            "Более того, вы можете добавить на карту абсолютно любую свою точку: вводим координаты, название — и новый маркер тут же появляется на интерактивном холсте."
        )
    },
    {
        "id": 4,
        "text": (
            "А вот этот инструмент — настоящий математический детектор правды. Это интерактивная линейка. "
            "Когда мы соединяем две точки, система на лету считает два расстояния: реальное сферическое по дуге большого круга и плоское расстояние на карте. "
            "Посмотрите на маршрут между Сиднеем и Сантьяго: на сфере это 11 тысяч километров, а на плоской карте — больше 25 тысяч! "
            "Разница колоссальная — более чем в два раза, что наглядно доказывает масштаб искажений на плоской модели."
        )
    },
    {
        "id": 5,
        "text": (
            "И здесь мы подходим к главному аргументу картографии — реальным авиарейсам. Включаем отображение маршрутов. "
            "Обратите внимание на регулярные перелёты через океан в южном полушарии, такие как Сидней — Сантьяго авиакомпании Qantas или Йоханнесбург — Перт. "
            "Лайнеры преодолевают этот путь за 12–14 часов со стандартной скоростью. "
            "На плоской карте такой полет потребовал бы нереальной сверхзвуковой скорости, ведь самолёту пришлось бы лететь через весь край карты."
        )
    },
    {
        "id": 6,
        "text": (
            "Перейдём к астрономии. Проект оснащён передовым движком Astronomy Engine. Включаем Солнце, Луну и тень терминатора. "
            "Карта в реальном времени рассчитывает подсолнечную точку, границы освещённости и точные фазы Луны. "
            "Но самая крутая фишка — это кнопки предсказания затмений. "
            "Нажимаем «следующее затмение» — и система автоматически переносит нас в будущее, прямо в момент схождения светил на траектории затмения!"
        )
    },
    {
        "id": 7,
        "text": (
            "Теперь взглянем на небосвод. Включаем планеты — от Меркурия до Сатурна, линии эклиптики, тропиков и небесного экватора. "
            "Приложение загружает официальные границы тринадцати зодиакальных созвездий, звёзды до пятой величины и даже рукава нашей галактики Млечный Путь. "
            "Причём система в реальном времени отслеживает и пишет в панели, в каком именно знаке и созвездии сейчас находится каждая планета."
        )
    },
    {
        "id": 8,
        "text": (
            "Космическая баллистика здесь тоже на высоте. Включаем слой МКС. "
            "Сервис подключается напрямую к серверам CelesTrak и скачивает свежайшие параметры NORAD TLE. "
            "По модели SGP4 рассчитывается живое положение станции: высота около 420 километров и первая космическая скорость — почти 28 тысяч километров в час! "
            "Мы можем ускорить время в двадцать или сто раз и наблюдать, как станция виток за витком облетает планету."
        )
    },
    {
        "id": 9,
        "text": (
            "Один из самых красивых визуальных режимов — хвосты траекторий. Включаем следы светил и запускаем симуляцию времени с шагом в 24 часа. "
            "Посмотрите, как подсолнечная точка день за днём вычерчивает завораживающую спираль между Северным и Южным тропиками, наглядно иллюстрируя смену сезонов года. "
            "А Луна и спутники оставляют эффектные переплетающиеся узоры."
        )
    },
    {
        "id": 10,
        "text": (
            "Подводя итог: перед нами потрясающий пример качественной инженерной разработки. "
            "Никаких тяжёлых фреймворков — только чистый JavaScript, D3, строгая математика и открытые научные данные. "
            "Проект поддерживает три языка: русский, английский и немецкий, и служит превосходным наглядным пособием по картографии и астрономии. "
            "Обязательно протестируйте его сами по ссылке в описании!"
        )
    }
]

def get_duration(audio_file):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return float(res.stdout.strip())

def generate_scene(client, idx, text):
    out_file = os.path.join(AUDIO_DIR, f"scene_{idx}.wav")
    
    if os.path.exists(out_file) and os.path.getsize(out_file) > 100000:
        dur = get_duration(out_file)
        print(f"Scene {idx} already exists ({dur:.2f} s, {os.path.getsize(out_file)} bytes). Skipping.")
        return dur

    print(f"Generating Scene {idx}/10 with {MODEL_NAME} ({VOICE_NAME})...")
    max_retries = 6
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_NAME)
                        )
                    )
                )
            )
            for cand in resp.candidates:
                for part in cand.content.parts:
                    if part.inline_data:
                        with open(out_file, "wb") as f:
                            f.write(part.inline_data.data)
                        dur = get_duration(out_file)
                        print(f"  -> [OK] Scene {idx} saved: {dur:.2f} s ({os.path.getsize(out_file)} bytes)")
                        return dur
            print(f"  -> Warning: No inline audio in response for Scene {idx}")
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                wait_time = 32
                print(f"  -> Rate limit hit (attempt {attempt+1}/{max_retries}). Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"  -> Unexpected error: {e}. Retrying in 15s...")
                time.sleep(15)
    raise RuntimeError(f"Failed to generate Scene {idx} after {max_retries} attempts.")

def main():
    print("=" * 60)
    print(f"Generating Presentation Voiceover using {MODEL_NAME}")
    print("=" * 60)
    client = genai.Client(api_key=API_KEY)

    durations = {}
    for item in SCENES:
        idx = item["id"]
        dur = generate_scene(client, idx, item["text"])
        durations[idx] = dur
        time.sleep(22)  # Respect 3 RPM Free Tier quota limit

    print("\n[ALL SCENES GENERATED SUCCESSFULLY]")
    for idx, dur in durations.items():
        print(f"Scene {idx}: {dur:.2f} s")

if __name__ == "__main__":
    main()
