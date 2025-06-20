# Audio Transcription with Gladia API

This backend now supports audio file transcription using the Gladia API v2. The transcription service follows the correct Gladia workflow: upload the audio file first, then transcribe it using the returned audio URL.

## Setup

### 1. Environment Variables

Add the following environment variable to your `.env` file:

```bash
GLADIA_API_KEY=your_gladia_api_key_here
```

You can get a free API key by signing up at [Gladia.io](https://www.gladia.io/).

### 2. Install Dependencies

The transcription service uses the `requests` package, which is already included in `requirements.txt`.

## How It Works

The transcription process follows the official Gladia API workflow:

1. **Upload Audio File** - Upload the audio file to Gladia's servers using `POST /v2/upload/`
2. **Start Transcription** - Send transcription request using `POST /v2/pre-recorded/` with the returned audio URL
3. **Poll for Results** - Continuously poll the result URL until transcription is complete
4. **Save Results** - Store transcription segments in the database

## API Endpoints

### Start Transcription

**POST** `/audio-files/{audio_file_id}/transcribe`

Start transcription for a downloaded audio file. This is a synchronous operation that may take several minutes.

**Response:**

```json
{
  "status": "success",
  "message": "Transcription started successfully",
  "audio_file_id": 1,
  "transcriptions_count": 15
}
```

### Get Transcription Status

**GET** `/audio-files/{audio_file_id}/transcription-status`

Get the current transcription status for an audio file.

**Response:**

```json
{
  "audio_file_id": 1,
  "status": "transcribed",
  "transcriptions_count": 15
}
```

### Get All Transcriptions

**GET** `/audio-files/{audio_file_id}/transcriptions`

Get all transcription segments for an audio file.

**Response:**

```json
[
  {
    "id": 1,
    "audio_file_id": 1,
    "language": "ja",
    "content_type": "transcription",
    "content": "こんにちは、皆さん。今日は基本的な挨拶について学びましょう。",
    "confidence_score": 0.95,
    "start_time_seconds": 0.0,
    "end_time_seconds": 5.2,
    "segment_order": 1,
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

### Get Transcriptions by Language

**GET** `/audio-files/{audio_file_id}/transcriptions/{language}`

Get transcription segments for a specific language (e.g., "ja", "en", "fr").

### Get Audio File with Transcriptions

**GET** `/audio-files/{audio_file_id}/with-transcriptions`

Get an audio file with all its transcription data included.

### Delete Transcriptions

**DELETE** `/audio-files/{audio_file_id}/transcriptions`

Delete all transcription data for an audio file.

## Audio File Status Values

The audio file status field now supports additional values for transcription:

- `not_downloaded` - File has not been downloaded yet
- `downloading` - File is currently being downloaded
- `downloaded` - File has been downloaded successfully
- `transcribing` - File is currently being transcribed
- `transcribed` - File has been transcribed successfully
- `transcription_failed` - Transcription failed
- `file_missing` - File was deleted from disk
- `download_failed` - Download failed

## Transcription Features

The transcription service includes the following features:

- **File Upload** - Automatically uploads audio files to Gladia's servers
- **Automatic Language Detection** - Detects the language of the audio content
- **Speaker Diarization** - Identifies different speakers (configured for 1-3 speakers)
- **Code Switching Support** - Handles mixed-language content
- **Confidence Scores** - Provides confidence scores for transcription accuracy
- **Time Stamps** - Includes start and end times for each transcription segment
- **Segment Ordering** - Maintains proper order of transcription segments
- **Polling Mechanism** - Automatically polls for results until completion

## Usage Example

1. **Download an audio file:**

   ```bash
   curl -X POST "http://localhost:8000/extract-audio" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://www.youtube.com/watch?v=example"}'
   ```

2. **Start transcription:**

   ```bash
   curl -X POST "http://localhost:8000/audio-files/1/transcribe"
   ```

   _Note: This will take several minutes to complete_

3. **Check transcription status:**

   ```bash
   curl "http://localhost:8000/audio-files/1/transcription-status"
   ```

4. **Get transcriptions:**
   ```bash
   curl "http://localhost:8000/audio-files/1/transcriptions"
   ```

## Error Handling

The transcription service includes comprehensive error handling:

- Validates that audio files exist and are downloaded before transcription
- Handles upload failures and provides detailed error messages
- Manages transcription request failures
- Implements timeout protection for long-running transcriptions
- Updates file status appropriately on failures
- Logs all operations for debugging

## Technical Details

### Upload Process

- Uses `multipart/form-data` to upload audio files
- Supports various audio formats (MP3, WAV, etc.)
- Returns an `audio_url` for use in transcription

### Transcription Process

- Sends JSON request with audio URL and configuration
- Configures diarization for 1-3 speakers
- Enables language detection and code switching
- Returns a `result_url` for polling

### Polling Process

- Polls the result URL every second
- Continues until status is "done" or "error"
- Times out after 5 minutes (300 attempts)
- Handles various status states

## Database Schema

The transcription data is stored in the `transcriptions` table with the following structure:

- `audio_file_id` - Reference to the audio file
- `language` - Language code (e.g., "ja", "en", "fr")
- `content_type` - Type of content ("transcription" or "translation")
- `content` - The transcribed text
- `confidence_score` - Confidence score (0.00 to 1.00)
- `start_time_seconds` - Start time of the segment
- `end_time_seconds` - End time of the segment
- `segment_order` - Order of the segment within the file

## Notes

- Transcription is a synchronous operation that may take several minutes for longer audio files
- The service automatically handles file upload and polling
- All transcription data is stored in the database for later retrieval
- The service is optimized for Japanese podcast content but works with any language
- The polling mechanism ensures reliable completion of transcription tasks

# Glada response format with utterances truncated

```json
{
    "id": "2a1b720f-ff90-448b-826f-1b508d46d7fe",
    "request_id": "G-2a1b720f",
    "version": 2,
    "status": "done",
    "created_at": "2025-06-22T15:04:37.431Z",
    "completed_at": "2025-06-22T15:05:25.841Z",
    "custom_metadata": null,
    "error_code": null,
    "kind": "pre-recorded",
    "file": {
        "id": "2d0a5e0b-22be-4aba-a7ce-921e11547cbc",
        "filename": "Japanese_podcast_for_beginners__Nihongo_con_Teppei__932etc....mp3",
        "source": null,
        "audio_duration": 275.04,
        "number_of_channels": 2
    },
    "request_params": {
        "audio_url": "https://api.gladia.io/file/2d0a5e0b-22be-4aba-a7ce-921e11547cbc",
        "sentences": false,
        "subtitles": true,
        "moderation": false,
        "diarization": true,
        "translation": true,
        "audio_to_llm": false,
        "display_mode": false,
        "summarization": false,
        "audio_enhancer": true,
        "chapterization": false,
        "custom_spelling": false,
        "detect_language": true,
        "language_config": {
            "languages": [],
            "code_switching": false
        },
        "name_consistency": false,
        "subtitles_config": {
            "style": "default",
            "formats": [
                "srt",
                "vtt"
            ]
        },
        "sentiment_analysis": false,
        "translation_config": {
            "model": "base",
            "context": "",
            "lipsync": true,
            "informal": false,
            "target_languages": [
                "fr",
                "en"
            ],
            "context_adaptation": true,
            "match_original_utterances": true
        },
        "diarization_enhanced": false,
        "punctuation_enhanced": false,
        "enable_code_switching": false,
        "named_entity_recognition": false,
        "speaker_reidentification": false,
        "accurate_words_timestamps": false,
        "skip_channel_deduplication": false,
        "structured_data_extraction": false
    },
    "result": {
        "metadata": {
            "audio_duration": 275.005542,
            "number_of_distinct_channels": 1,
            "billing_time": 275.005542,
            "transcription_time": 48.41
        },
        "transcription": {
            "utterances": [
                {
                    "words": [
                        {
                            "word": "日本",
                            "start": 1.916,
                            "end": 2.236,
                            "confidence": 0.72
                        },
                        {
                            "word": "語",
                            "start": 2.277,
                            "end": 2.397,
                            "confidence": 0.24
                        }
                    ],
                    "text": "日本語",
                    "language": "ja",
                    "start": 1.916,
                    "end": 2.397,
                    "speaker": 0,
                    "channel": 0,
                    "confidence": 0.48
                },
                {
                    "words": [
                        {
                            "word": "コン",
                            "start": 2.797,
                            "end": 2.977,
                            "confidence": 0.67
                        }
                    ],
                    "text": "コン",
                    "language": "ja",
                    "start": 2.797,
                    "end": 2.977,
                    "speaker": 0,
                    "channel": 0,
                    "confidence": 0.67
                }
            ],
            "full_transcript": "日本語 コン テッペイ。日本語学習者の皆さんを いつもいつも応援するポッドキャスト。 今日は アイスクリーム、 アイスキャンディー に ついて。 アイス。 アイスでいいかな? はい、 みなさんこんにちは。 日本語コンテッペンの時間ですね。 暑い。 毎日暑い。 暑すぎます。 暑い日は アイスクリームを 食べたいですね。 アイスクリーム とアイスキャンディー。 もしくは アイスキャンディー。 アイスキャンディー ですね。 アイスキャンディー と、 あとは アイス。 まあ日本語で アイスっていうと 色々な あの アイスのことですねあのシャーベットとかアイスクリームとか そういうのが全部 アイスまあソフトクリームも アイス ソフトクリームっていうと あのマクドナルドとかにあるような なんかこう まあぐるぐる巻いてある ちょっと 漫画のうんちみたいな 汚い話ですけど まあそういう形をしている ソフトクリーム ですね そしてアイスクリームアイスクリームはまあ やっぱりジェネラルな意味ですよね一般的な アイスアイスクリーム コンビニに行って あのいろいろなタイプの アイスがあります ハーゲンダッツみたいな バニラのアイスクリームとか チョコレートのアイスクリームもあるし シャーベット みたいなねシャーベットみたいなものもある 有名なのは ガリガリ君 ガリガリ君というアイスクリームは まあアイスクリーム まあそのシャーベット アイス はあの まあ ちょっと 変な味ですけど美味しいですね 変な味 なんかこう サイダーのような 味がしますね ちょっと砂糖のような ちょっと ちょっとだけシトラスのような味 あと スイカバースイカバーというのは ちょっとこうウォーター メロン みたいな味 ちょっとだけ ま あほとんどシャーベットですね 僕の子供は ガリガリ君とか スイカバー が 大好きです 僕はあんまりシャーベットは好きじゃない あの 手作りのシャーベットは大好きです レストランとかのシャーベットは大好き でも コンビニのシャーベットは全然好きじゃん 僕はコンビニ で普通は バニラアイス を買います だけど 美味しいバニラアイスと 美味しくない バニラアイスがありますね 僕が好きなのはもちろん 美味しいバニラアイスです 美味しくないバニラアイスは なんかこう薄くて甘すぎて 全然バニラの味がしなくて 全然ミルクの味がしない 全然おいしくないですね おいしいバニラアイスは バニラの味がして ミルクの味がして 牛乳の味がして 甘すぎない 僕はそういう バニラアイスが好きです ハーゲンダッツはちょっと甘すぎる 僕はちょっとハーゲンダッツは 好きだけど 一番好きじゃないですね 皆さんはどうですか アイスの話食べたくなってきましたね この後食べたいと思います それではチャオチャオアスタレーゴまたねまたね またね",
            "languages": [
                "ja"
            ],
            "subtitles": [
                {
                    "format": "srt",
                    "subtitles": "1\n00:00:01.916 --> 00:00:06.139\n日本 語 コン テッペイ。 日本 語 学習 者 の 皆 さん を\n\n2\n00:00:06.682 --> 00:00:09.022\nいつ も いつ も 応援 する ポッド キャスト。\n\n3\n00:00:10.725 --> 00:00:16.490\n今日 は アイス クリーム、 アイス キャンディー に つい て。\n\n4\n00:00:17.975 --> 00:00:18.675\nアイス。\n\n5\n00:00:20.740 --> 00:00:21.537\nアイス で いい か な?\n\n6\n00:00:26.424 --> 00:00:27.585\nはい、 みな さん こんにちは。\n\n7\n00:00:27.745 --> 00:00:29.427\n日本 語 コン テッペン の 時間 です ね。\n\n8\n00:00:31.630 --> 00:00:32.330\n暑い。\n\n9\n00:00:32.528 --> 00:00:33.571\n毎日 暑い。\n\n10\n00:00:33.751 --> 00:00:35.614\n暑 すぎ ます。\n\n11\n00:00:36.755 --> 00:00:40.177\n暑い 日 は アイス クリーム を 食べ たい です ね。\n\n12\n00:00:42.278 --> 00:00:45.536\nアイス クリーム と アイス キャンディー。\n\n13\n00:00:46.958 --> 00:00:49.614\nもしくは アイス キャンディー。\n\n14\n00:00:49.973 --> 00:00:50.802\nアイス キャンディー です ね。\n\n15\n00:00:50.864 --> 00:00:54.411\nアイス キャンディー と、 あと は アイス。\n\n16\n00:00:56.480 --> 00:01:02.782\nまあ 日本 語 で アイス って いう と 色々 な\n\n17\n00:01:03.521 --> 00:01:10.263\nあの アイス の こと です ね あの シャーベット と か アイス クリーム と\nか そう いう の が 全部\n\n18\n00:01:11.302 --> 00:01:17.052\nアイス ま あ ソフト クリーム も アイス ソフト クリーム って いう と\n\n19\n00:01:17.708 --> 00:01:24.058\nあの マクドナルド と か に ある よう な なんか こう まあ ぐるぐる 巻い\nて ある\n\n20\n00:01:24.939 --> 00:01:31.123\nちょっと 漫画 の うんち みたい な 汚い 話 です けど ま あ そう いう 形\nを し て いる\n\n21\n00:01:33.787 --> 00:01:38.412\nソフト クリーム です ね そして アイス クリーム アイス クリーム は まあ\n\n22\n00:01:39.130 --> 00:01:43.724\nやっぱり ジェネラル な 意味 です よ ね 一般 的 な アイス アイス クリーム\n\n23\n00:01:45.193 --> 00:01:50.396\nコンビニ に 行っ て あの いろいろ な タイプ の アイス が あり ます\n\n24\n00:01:51.648 --> 00:01:57.876\nハーゲンダッツ みたい な バニラ の アイス クリーム と か チョコレート の\nアイス クリーム も ある し\n\n25\n00:01:58.915 --> 00:02:04.845\nシャーベット みたい な ね シャーベット みたい な もの も ある 有名 な の\nは\n\n26\n00:02:05.321 --> 00:02:12.204\nガリガリ 君 ガリガリ 君 と いう アイス クリーム は ま あ アイス クリーム\nま あ その シャーベット アイス\n\n27\n00:02:13.454 --> 00:02:17.630\nは あの まあ ちょっと\n\n28\n00:02:19.171 --> 00:02:24.735\n変 な 味 です けど 美味しい です ね 変 な 味 なんか こう\n\n29\n00:02:26.157 --> 00:02:32.680\nサイダー の よう な 味 が し ます ね ちょっと 砂糖 の よう な ちょっと\n\n30\n00:02:35.212 --> 00:02:39.588\nちょっと だけ シトラス の よう な 味 あと\n\n31\n00:02:40.650 --> 00:02:46.416\nスイカバースイカバー と いう の は ちょっと こう ウォーター メロン みたい\nな 味\n\n32\n00:02:48.017 --> 00:02:53.642\nちょっと だけ ま あ ほとんど シャーベット です ね 僕 の 子供 は\n\n33\n00:02:54.181 --> 00:02:58.822\nガリガリ 君 と か スイ カバー が 大好き です\n\n34\n00:02:59.712 --> 00:03:04.684\n僕 は あんまり シャーベット は 好き じゃ ない あの\n\n35\n00:03:05.085 --> 00:03:11.632\n手作り の シャーベット は 大好き です レストラン と か の シャーベット は\n大好き で も\n\n36\n00:03:12.432 --> 00:03:18.761\nコンビニ の シャーベット は 全然 好き じゃん 僕 は コンビニ で 普通 は\n\n37\n00:03:20.120 --> 00:03:23.909\nバニラ アイス を 買い ます だ けど\n\n38\n00:03:25.696 --> 00:03:30.241\n美味しい バニラ アイス と 美味しく ない バニラ アイス が あり ます ね\n\n39\n00:03:31.284 --> 00:03:37.909\n僕 が 好き な の は もちろん 美味しい バニラ アイス です 美味しく ない\nバニラ アイス は\n\n40\n00:03:38.752 --> 00:03:43.580\nなん か こう 薄く て 甘 すぎ て\n\n41\n00:03:44.955 --> 00:03:47.424\n全然 バニラ の 味 が し なく て\n\n42\n00:03:49.968 --> 00:03:56.616\n全然 ミルク の 味 が し ない 全然 おいしく ない です ね おいしい バニラ\nアイス は\n\n43\n00:03:57.296 --> 00:04:03.382\nバニラ の 味 が し て ミルク の 味 が し て 牛乳 の 味 が し て\n\n44\n00:04:04.038 --> 00:04:08.944\n甘 すぎ ない 僕 は そう いう バニラ アイス が 好き です\n\n45\n00:04:09.569 --> 00:04:15.963\nハーゲンダッツ は ちょっと 甘 すぎる 僕 は ちょっと ハーゲンダッツ は 好き\nだ けど\n\n46\n00:04:16.665 --> 00:04:22.597\n一番 好き じゃ ない です ね 皆 さん は どう です か アイス の 話 食べ\nたく なっ て き まし た ね\n\n47\n00:04:23.616 --> 00:04:29.468\nこの 後 食べ たい と 思い ます それ で は チャオチャオアスタレーゴ また\nね また ね また ね\n"
                },
                {
                    "format": "vtt",
                    "subtitles": "WEBVTT\n\n1\n00:00:01.916 --> 00:00:06.139\n日本 語 コン テッペイ。 日本 語 学習 者 の 皆 さん を\n\n2\n00:00:06.682 --> 00:00:09.022\nいつ も いつ も 応援 する ポッド キャスト。\n\n3\n00:00:10.725 --> 00:00:16.490\n今日 は アイス クリーム、 アイス キャンディー に つい て。\n\n4\n00:00:17.975 --> 00:00:18.675\nアイス。\n\n5\n00:00:20.740 --> 00:00:21.537\nアイス で いい か な?\n\n6\n00:00:26.424 --> 00:00:27.585\nはい、 みな さん こんにちは。\n\n7\n00:00:27.745 --> 00:00:29.427\n日本 語 コン テッペン の 時間 です ね。\n\n8\n00:00:31.630 --> 00:00:32.330\n暑い。\n\n9\n00:00:32.528 --> 00:00:33.571\n毎日 暑い。\n\n10\n00:00:33.751 --> 00:00:35.614\n暑 すぎ ます。\n\n11\n00:00:36.755 --> 00:00:40.177\n暑い 日 は アイス クリーム を 食べ たい です ね。\n\n12\n00:00:42.278 --> 00:00:45.536\nアイス クリーム と アイス キャンディー。\n\n13\n00:00:46.958 --> 00:00:49.614\nもしくは アイス キャンディー。\n\n14\n00:00:49.973 --> 00:00:50.802\nアイス キャンディー です ね。\n\n15\n00:00:50.864 --> 00:00:54.411\nアイス キャンディー と、 あと は アイス。\n\n16\n00:00:56.480 --> 00:01:02.782\nまあ 日本 語 で アイス って いう と 色々 な\n\n17\n00:01:03.521 --> 00:01:10.263\nあの アイス の こと です ね あの シャーベット と か アイス クリーム と\nか そう いう の が 全部\n\n18\n00:01:11.302 --> 00:01:17.052\nアイス ま あ ソフト クリーム も アイス ソフト クリーム って いう と\n\n19\n00:01:17.708 --> 00:01:24.058\nあの マクドナルド と か に ある よう な なんか こう まあ ぐるぐる 巻い\nて ある\n\n20\n00:01:24.939 --> 00:01:31.123\nちょっと 漫画 の うんち みたい な 汚い 話 です けど ま あ そう いう 形\nを し て いる\n\n21\n00:01:33.787 --> 00:01:38.412\nソフト クリーム です ね そして アイス クリーム アイス クリーム は まあ\n\n22\n00:01:39.130 --> 00:01:43.724\nやっぱり ジェネラル な 意味 です よ ね 一般 的 な アイス アイス クリーム\n\n23\n00:01:45.193 --> 00:01:50.396\nコンビニ に 行っ て あの いろいろ な タイプ の アイス が あり ます\n\n24\n00:01:51.648 --> 00:01:57.876\nハーゲンダッツ みたい な バニラ の アイス クリーム と か チョコレート の\nアイス クリーム も ある し\n\n25\n00:01:58.915 --> 00:02:04.845\nシャーベット みたい な ね シャーベット みたい な もの も ある 有名 な の\nは\n\n26\n00:02:05.321 --> 00:02:12.204\nガリガリ 君 ガリガリ 君 と いう アイス クリーム は ま あ アイス クリーム\nま あ その シャーベット アイス\n\n27\n00:02:13.454 --> 00:02:17.630\nは あの まあ ちょっと\n\n28\n00:02:19.171 --> 00:02:24.735\n変 な 味 です けど 美味しい です ね 変 な 味 なんか こう\n\n29\n00:02:26.157 --> 00:02:32.680\nサイダー の よう な 味 が し ます ね ちょっと 砂糖 の よう な ちょっと\n\n30\n00:02:35.212 --> 00:02:39.588\nちょっと だけ シトラス の よう な 味 あと\n\n31\n00:02:40.650 --> 00:02:46.416\nスイカバースイカバー と いう の は ちょっと こう ウォーター メロン みたい\nな 味\n\n32\n00:02:48.017 --> 00:02:53.642\nちょっと だけ ま あ ほとんど シャーベット です ね 僕 の 子供 は\n\n33\n00:02:54.181 --> 00:02:58.822\nガリガリ 君 と か スイ カバー が 大好き です\n\n34\n00:02:59.712 --> 00:03:04.684\n僕 は あんまり シャーベット は 好き じゃ ない あの\n\n35\n00:03:05.085 --> 00:03:11.632\n手作り の シャーベット は 大好き です レストラン と か の シャーベット は\n大好き で も\n\n36\n00:03:12.432 --> 00:03:18.761\nコンビニ の シャーベット は 全然 好き じゃん 僕 は コンビニ で 普通 は\n\n37\n00:03:20.120 --> 00:03:23.909\nバニラ アイス を 買い ます だ けど\n\n38\n00:03:25.696 --> 00:03:30.241\n美味しい バニラ アイス と 美味しく ない バニラ アイス が あり ます ね\n\n39\n00:03:31.284 --> 00:03:37.909\n僕 が 好き な の は もちろん 美味しい バニラ アイス です 美味しく ない\nバニラ アイス は\n\n40\n00:03:38.752 --> 00:03:43.580\nなん か こう 薄く て 甘 すぎ て\n\n41\n00:03:44.955 --> 00:03:47.424\n全然 バニラ の 味 が し なく て\n\n42\n00:03:49.968 --> 00:03:56.616\n全然 ミルク の 味 が し ない 全然 おいしく ない です ね おいしい バニラ\nアイス は\n\n43\n00:03:57.296 --> 00:04:03.382\nバニラ の 味 が し て ミルク の 味 が し て 牛乳 の 味 が し て\n\n44\n00:04:04.038 --> 00:04:08.944\n甘 すぎ ない 僕 は そう いう バニラ アイス が 好き です\n\n45\n00:04:09.569 --> 00:04:15.963\nハーゲンダッツ は ちょっと 甘 すぎる 僕 は ちょっと ハーゲンダッツ は 好き\nだ けど\n\n46\n00:04:16.665 --> 00:04:22.597\n一番 好き じゃ ない です ね 皆 さん は どう です か アイス の 話 食べ\nたく なっ て き まし た ね\n\n47\n00:04:23.616 --> 00:04:29.468\nこの 後 食べ たい と 思い ます それ で は チャオチャオアスタレーゴ また\nね また ね また ね\n"
                }
            ]
        },
        "translation": {
            "success": true,
            "is_empty": false,
            "results": [
                {
                    "languages": [
                        "fr"
                    ],
                    "full_transcript": "日本語コンテッペイ。 Ce podcast soutient toujours les apprenants de japonais. Aujourd'hui, nous parlerons de crème glacée et de sucettes glacées. De la glace. Est-ce que de la glace ferait l'affaire ? Oui, bonjour à tous. C'est l'heure du sommet japonais, n'est-ce pas ? Il fait chaud. Il fait chaud tous les jours. Il fait trop chaud. Par cette chaleur, j'aimerais bien manger une glace, n'est-ce pas ? De la crème glacée et des glaces à l'eau. Ou bien, des glaces à l'eau. C'est une glace à l'eau, n'est-ce pas ? Des bâtonnets glacés, et puis de la glace. Eh bien, quand on dit « glace » en japonais, cela englobe divers types de glaces, n'est-ce pas ? Les sorbets, les crèmes glacées, tout cela est de la glace. Euh, les crèmes glacées à l'italienne aussi, comme celles que l'on trouve chez McDonald's, par exemple. Ainsi, eh bien, c'est enroulé, un peu comme des excréments de manga, c'est une histoire sale, mais c'est une forme de glace molle, n'est-ce pas ? Et la crème glacée, eh bien, c'est le sens général, n'est-ce pas, la crème glacée générale, les dépanneurs. Il y a là-bas divers types de glaces, comme des crèmes glacées à la vanille ou au chocolat, semblables à celles de Häagen-Dazs, et aussi des sorbets. Un produit célèbre est la glace appelée Garigari-kun. Euh, eh bien, la crème glacée, euh, ces glaces à l'eau, euh, ont un goût un peu étrange, mais elles sont délicieuses, n'est-ce pas ? Un goût étrange, comme celui du cidre, n'est-ce pas ? Un peu sucré, un peu d'agrumes, et puis... スイカバースイカバーというのはちょっとこうウォーターメロンみたいな味ちょっとだけまあほとんどシャーベットですね僕の子供はガリガリ君とかスイカバーが大好きです僕はあんまりシャーベットは好きじゃないあの手作りのシャーベットは大好きですレストランと. J'apprécie beaucoup ce sorbet, mais je n'aime pas du tout les sorbets des dépanneurs. J'achète généralement de la glace à la vanille dans les dépanneurs. Cependant, il y a de la glace à la vanille délicieuse et de la glace à la vanille qui ne l'est pas. Bien sûr, j'aime la glace à la vanille délicieuse. Une glace à la vanille qui n'est pas bonne, c'est un peu fade, trop sucrée, et n'a absolument pas le goût de vanille, ni celui du lait. Ce n'est vraiment pas bon. Une bonne glace à la vanille a le goût de vanille et de lait, comme le lait de vache. J'apprécie les glaces à la vanille qui ne sont pas trop sucrées. Häagen-Dazs est un peu trop sucré à mon goût, bien que je l'apprécie. Qu'en pensez-vous ? Cette discussion me donne envie de manger une glace. Je souhaiterais en manger après cela. Au revoir et à bientôt.",
                    "utterances": [
                        {
                            "words": [
                                {
                                    "word": "日 本",
                                    "start": 1.916,
                                    "end": 2.236,
                                    "confidence": 0.72
                                },
                                {
                                    "word": " ン",
                                    "start": 2.277,
                                    "end": 2.397,
                                    "confidence": 0.24
                                }
                            ],
                            "text": "日 本 ン",
                            "language": "fr",
                            "start": 1.916,
                            "end": 2.397,
                            "channel": 0,
                            "speaker": 0,
                            "confidence": 0.48
                        },
                        {
                            "words": [
                                {
                                    "word": " ッ",
                                    "start": 2.797,
                                    "end": 2.977,
                                    "confidence": 0.67
                                }
                            ],
                            "text": " ッ",
                            "language": "fr",
                            "start": 2.797,
                            "end": 2.977,
                            "channel": 0,
                            "speaker": 0,
                            "confidence": 0.67
                        }],
                    "error": null,
                    "subtitles": [
                        {
                            "format": "srt",
                            "subtitles": "1\n00:00:01.916 --> 00:00:05.580\n日 本 ン ッ ペ イ。 Ce podcast soutient\n\n2\n00:00:06.843 --> 00:00:09.022\nles apprenants de japonais.\n\n3\n00:00:10.725 --> 00:00:16.490\nAujourd'hui, nous parlerons de crème\nglacée et de sucettes glacées.\n\n4\n00:00:17.975 --> 00:00:18.675\nDe la glace.\n\n5\n00:00:20.740 --> 00:00:21.537\nEst-ce que de la glace ferait l'affaire ?\n\n6\n00:00:26.424 --> 00:00:27.585\nOui, bonjour à tous.\n\n7\n00:00:27.745 --> 00:00:29.427\nC'est l'heure du sommet japonais, n'est-ce\npas ?\n\n8\n00:00:31.630 --> 00:00:32.330\nIl fait chaud.\n\n9\n00:00:32.528 --> 00:00:33.571\nIl fait chaud tous les jours.\n\n10\n00:00:33.751 --> 00:00:35.614\nIl fait trop chaud.\n\n11\n00:00:36.755 --> 00:00:40.177\nPar cette chaleur, j'aimerais bien manger\nune glace, n'est-ce pas ?\n\n12\n00:00:42.278 --> 00:00:45.536\nDe la crème glacée et des glaces à l'eau.\n\n13\n00:00:46.958 --> 00:00:49.614\nOu bien, des glaces à l'eau.\n\n14\n00:00:49.973 --> 00:00:50.802\nC'est une glace à l'eau, n'est-ce pas ?\n\n15\n00:00:50.864 --> 00:00:54.411\nDes bâtonnets glacés, et puis de la glace.\n\n16\n00:00:56.480 --> 00:01:02.782\nEh bien, quand on dit « glace » en\njaponais,\n\n17\n00:01:03.521 --> 00:01:10.263\ncela englobe divers types de glaces,\nn'est-ce pas ? Les sorbets, les crèmes\n\n18\n00:01:10.263 --> 00:01:12.263\nglacées, tout cela est\n\n19\n00:01:12.263 --> 00:01:17.052\nde la glace. Euh, les crèmes glacées à\nl'italienne aussi,\n\n20\n00:01:17.708 --> 00:01:24.058\ncomme celles que l'on trouve chez\nMcDonald's, par exemple. Ainsi, eh bien,\n\n21\n00:01:24.058 --> 00:01:26.058\nc'est enroulé, un\n\n22\n00:01:26.058 --> 00:01:31.123\npeu comme des excréments de manga, c'est\nune histoire sale, mais c'est une forme de\n\n23\n00:01:31.123 --> 00:01:31.323\nglace\n\n24\n00:01:33.787 --> 00:01:35.209\nmolle, n'est-ce pas ?\n\n25\n00:01:35.966 --> 00:01:41.834\nEt la crème glacée, eh bien, c'est le sens\ngénéral, n'est-ce pas, la crème\n\n26\n00:01:42.396 --> 00:01:48.849\nglacée générale, les dépanneurs. Il y a\nlà-bas divers types\n\n27\n00:01:49.662 --> 00:01:55.292\nde glaces, comme des crèmes à la vanille\n\n28\n00:01:55.954 --> 00:02:02.861\nou au chocolat, semblables celles de\nHäagen-Dazs, et aussi des\n\n29\n00:02:04.040 --> 00:02:10.142\nsorbets. Un produit célèbre est la glace\nappelée Garigari-kun. Euh, eh bien, la\n\n30\n00:02:10.579 --> 00:02:16.168\ncrème glacée, euh, ces glaces à\n\n31\n00:02:16.869 --> 00:02:22.555\nl'eau, euh, ont un goût un peu étrange,\nmais elles sont\n\n32\n00:02:24.157 --> 00:02:28.298\ndélicieuses, n'est-ce pas ? Un étrange,\ncomme celui du\n\n33\n00:02:30.321 --> 00:02:37.243\ncidre, n'est-ce pas ? Un peu sucré, un peu\nd'agrumes, et\n\n34\n00:02:39.388 --> 00:02:40.088\npuis...\n\n35\n00:02:40.650 --> 00:02:46.416\nス イ カ バ ー ス イ カ バ ー う ょ っ と う ォ ー タ ー ロ\n\n36\n00:02:48.017 --> 00:02:53.642\nン た い ょ っ と け と ん ど ャ ー ベ ッ ト す 供 リ\n\n37\n00:02:54.181 --> 00:02:58.822\nガ リ イ バ ー 好 き す ん ま り ャ ー ベ\n\n38\n00:02:59.712 --> 00:03:04.684\nッ ト き ゃ い の 作 り ャ ー ベ ッ ト\n\n39\n00:03:05.085 --> 00:03:11.632\n好 き す ス ト ラ ン と. J'apprécie beaucoup ce\nsorbet, mais je n'aime pas\n\n40\n00:03:12.432 --> 00:03:18.761\ndu tout les sorbets des dépanneurs.\nJ'achète généralement de la glace à la\n\n41\n00:03:18.761 --> 00:03:19.039\nvanille\n\n42\n00:03:20.120 --> 00:03:23.909\ndans les dépanneurs. Cependant, il y a de\n\n43\n00:03:25.696 --> 00:03:30.241\nla glace à la vanille délicieuse et de la\nglace à la vanille qui\n\n44\n00:03:31.284 --> 00:03:35.362\nne l'est pas. Bien sûr, j'aime la glace à\nla vanille délicieuse.\n\n45\n00:03:36.330 --> 00:03:37.909\nUne glace à la vanille qui\n\n46\n00:03:38.752 --> 00:03:43.580\nn'est pas bonne, c'est un peu fade, trop\n\n47\n00:03:44.955 --> 00:03:47.424\nsucrée, et n'a absolument pas le goût de\n\n48\n00:03:49.968 --> 00:03:56.616\nvanille, ni celui du lait. Ce n'est\nvraiment pas bon. Une bonne glace à la\n\n49\n00:03:56.616 --> 00:03:56.953\nvanille\n\n50\n00:03:57.296 --> 00:04:03.241\na le goût de vanille et de lait, comme le\nlait de vache. J'apprécie les\n\n51\n00:04:04.460 --> 00:04:08.944\nà la vanille qui ne sont pas trop sucrées.\nHäagen-Dazs\n\n52\n00:04:09.569 --> 00:04:15.963\nest un peu trop sucré à mon goût, bien que\nje\n\n53\n00:04:16.665 --> 00:04:17.847\nl'apprécie. Qu'en pensez-vous ?\n\n54\n00:04:19.130 --> 00:04:25.116\ndiscussion me envie de manger une glace.\nJe souhaiterais en manger après cela.\n\n55\n00:04:25.561 --> 00:04:28.007\nAu revoir et à\n"
                        },
                        {
                            "format": "vtt",
                            "subtitles": "WEBVTT\n\n1\n00:00:01.916 --> 00:00:05.580\n日 本 ン ッ ペ イ。 Ce podcast soutient\n\n2\n00:00:06.843 --> 00:00:09.022\nles apprenants de japonais.\n\n3\n00:00:10.725 --> 00:00:16.490\nAujourd'hui, nous parlerons de crème\nglacée et de sucettes glacées.\n\n4\n00:00:17.975 --> 00:00:18.675\nDe la glace.\n\n5\n00:00:20.740 --> 00:00:21.537\nEst-ce que de la glace ferait l'affaire ?\n\n6\n00:00:26.424 --> 00:00:27.585\nOui, bonjour à tous.\n\n7\n00:00:27.745 --> 00:00:29.427\nC'est l'heure du sommet japonais, n'est-ce\npas ?\n\n8\n00:00:31.630 --> 00:00:32.330\nIl fait chaud.\n\n9\n00:00:32.528 --> 00:00:33.571\nIl fait chaud tous les jours.\n\n10\n00:00:33.751 --> 00:00:35.614\nIl fait trop chaud.\n\n11\n00:00:36.755 --> 00:00:40.177\nPar cette chaleur, j'aimerais bien manger\nune glace, n'est-ce pas ?\n\n12\n00:00:42.278 --> 00:00:45.536\nDe la crème glacée et des glaces à l'eau.\n\n13\n00:00:46.958 --> 00:00:49.614\nOu bien, des glaces à l'eau.\n\n14\n00:00:49.973 --> 00:00:50.802\nC'est une glace à l'eau, n'est-ce pas ?\n\n15\n00:00:50.864 --> 00:00:54.411\nDes bâtonnets glacés, et puis de la glace.\n\n16\n00:00:56.480 --> 00:01:02.782\nEh bien, quand on dit « glace » en\njaponais,\n\n17\n00:01:03.521 --> 00:01:10.263\ncela englobe divers types de glaces,\nn'est-ce pas ? Les sorbets, les crèmes\n\n18\n00:01:10.263 --> 00:01:12.263\nglacées, tout cela est\n\n19\n00:01:12.263 --> 00:01:17.052\nde la glace. Euh, les crèmes glacées à\nl'italienne aussi,\n\n20\n00:01:17.708 --> 00:01:24.058\ncomme celles que l'on trouve chez\nMcDonald's, par exemple. Ainsi, eh bien,\n\n21\n00:01:24.058 --> 00:01:26.058\nc'est enroulé, un\n\n22\n00:01:26.058 --> 00:01:31.123\npeu comme des excréments de manga, c'est\nune histoire sale, mais c'est une forme de\n\n23\n00:01:31.123 --> 00:01:31.323\nglace\n\n24\n00:01:33.787 --> 00:01:35.209\nmolle, n'est-ce pas ?\n\n25\n00:01:35.966 --> 00:01:41.834\nEt la crème glacée, eh bien, c'est le sens\ngénéral, n'est-ce pas, la crème\n\n26\n00:01:42.396 --> 00:01:48.849\nglacée générale, les dépanneurs. Il y a\nlà-bas divers types\n\n27\n00:01:49.662 --> 00:01:55.292\nde glaces, comme des crèmes à la vanille\n\n28\n00:01:55.954 --> 00:02:02.861\nou au chocolat, semblables celles de\nHäagen-Dazs, et aussi des\n\n29\n00:02:04.040 --> 00:02:10.142\nsorbets. Un produit célèbre est la glace\nappelée Garigari-kun. Euh, eh bien, la\n\n30\n00:02:10.579 --> 00:02:16.168\ncrème glacée, euh, ces glaces à\n\n31\n00:02:16.869 --> 00:02:22.555\nl'eau, euh, ont un goût un peu étrange,\nmais elles sont\n\n32\n00:02:24.157 --> 00:02:28.298\ndélicieuses, n'est-ce pas ? Un étrange,\ncomme celui du\n\n33\n00:02:30.321 --> 00:02:37.243\ncidre, n'est-ce pas ? Un peu sucré, un peu\nd'agrumes, et\n\n34\n00:02:39.388 --> 00:02:40.088\npuis...\n\n35\n00:02:40.650 --> 00:02:46.416\nス イ カ バ ー ス イ カ バ ー う ょ っ と う ォ ー タ ー ロ\n\n36\n00:02:48.017 --> 00:02:53.642\nン た い ょ っ と け と ん ど ャ ー ベ ッ ト す 供 リ\n\n37\n00:02:54.181 --> 00:02:58.822\nガ リ イ バ ー 好 き す ん ま り ャ ー ベ\n\n38\n00:02:59.712 --> 00:03:04.684\nッ ト き ゃ い の 作 り ャ ー ベ ッ ト\n\n39\n00:03:05.085 --> 00:03:11.632\n好 き す ス ト ラ ン と. J'apprécie beaucoup ce\nsorbet, mais je n'aime pas\n\n40\n00:03:12.432 --> 00:03:18.761\ndu tout les sorbets des dépanneurs.\nJ'achète généralement de la glace à la\n\n41\n00:03:18.761 --> 00:03:19.039\nvanille\n\n42\n00:03:20.120 --> 00:03:23.909\ndans les dépanneurs. Cependant, il y a de\n\n43\n00:03:25.696 --> 00:03:30.241\nla glace à la vanille délicieuse et de la\nglace à la vanille qui\n\n44\n00:03:31.284 --> 00:03:35.362\nne l'est pas. Bien sûr, j'aime la glace à\nla vanille délicieuse.\n\n45\n00:03:36.330 --> 00:03:37.909\nUne glace à la vanille qui\n\n46\n00:03:38.752 --> 00:03:43.580\nn'est pas bonne, c'est un peu fade, trop\n\n47\n00:03:44.955 --> 00:03:47.424\nsucrée, et n'a absolument pas le goût de\n\n48\n00:03:49.968 --> 00:03:56.616\nvanille, ni celui du lait. Ce n'est\nvraiment pas bon. Une bonne glace à la\n\n49\n00:03:56.616 --> 00:03:56.953\nvanille\n\n50\n00:03:57.296 --> 00:04:03.241\na le goût de vanille et de lait, comme le\nlait de vache. J'apprécie les\n\n51\n00:04:04.460 --> 00:04:08.944\nà la vanille qui ne sont pas trop sucrées.\nHäagen-Dazs\n\n52\n00:04:09.569 --> 00:04:15.963\nest un peu trop sucré à mon goût, bien que\nje\n\n53\n00:04:16.665 --> 00:04:17.847\nl'apprécie. Qu'en pensez-vous ?\n\n54\n00:04:19.130 --> 00:04:25.116\ndiscussion me envie de manger une glace.\nJe souhaiterais en manger après cela.\n\n55\n00:04:25.561 --> 00:04:28.007\nAu revoir et à\n"
                        }
                    ]
                },
                {
                    "languages": [
                        "en"
                    ],
                    "full_transcript": "Japanese Kon Teppei. A podcast that always supports Japanese language learners. Today, we are discussing ice cream and ice pops. Ice cream. Would ice cream be acceptable? Yes, everyone, hello. It is time for the pinnacle of enjoyment, is it not? It is hot. It is hot every day. It is excessively hot. On a hot day, I would like to eat ice cream, wouldn't I? Ice cream and ice pops. Or perhaps, ice pops. It is an ice pop, isn't it? Ice pops, and then, ice cream. Well, when we talk about ice in Japanese, it refers to various types of ice, such as sherbet and ice cream. All of these are considered ice, including soft serve ice cream, like the ones you find at McDonald's. Well, it's a soft serve ice cream that's swirled around, a bit like the shape of, well, a rather unpleasant thing from a comic, though it is a messy topic. And ice cream is, well, in the general sense, the typical ice cream from a convenience store. There are various types of ice cream available, such as vanilla ice cream and chocolate ice cream like Häagen-Dazs, as well as sorbet-like options; a well-known one is the ice pop called Garigari-kun. Well, ice cream, well, that sherbet ice, um, well, it has a slightly unusual flavor, but it is delicious, isn't it? The unusual flavor is like that of cider, isn't it? It has a slightly sugary, slightly citrus-like taste, and then... Regarding the Suika Bar and Suika Bar, the flavor is somewhat reminiscent of watermelon, and it is, to a degree, a sorbet. My children are very fond of Garigari-kun and Suika Bar. I am not particularly fond of sorbet, although I do enjoy handmade sorbet from restaurants. I greatly enjoy that sherbet, but I do not care for the sherbet from convenience stores at all. I usually purchase vanilla ice cream at convenience stores, however, there are delicious vanilla ice creams and vanilla ice creams that are not delicious. Of course, I prefer the delicious vanilla ice cream. Vanilla ice cream that is not delicious is, in a way, thin and too sweet, and it does not taste like vanilla at all, nor does it taste like milk at all; it is not delicious at all. Delicious vanilla ice cream tastes like vanilla and tastes like milk and like milk. I prefer vanilla ice cream that does not taste artificial and is not too sweet. Haagen-Dazs is a bit too sweet for me, although I do like it somewhat, but it is not my favorite. What about you all? This ice cream discussion is making me want to eat some. I see. I would like to eat something after this. Goodbye, and see you later.",
                    "utterances": [
                        {
                            "words": [
                                {
                                    "word": "Japanese",
                                    "start": 1.916,
                                    "end": 2.236,
                                    "confidence": 0.72
                                }
                            ],
                            "text": "Japanese",
                            "language": "en",
                            "start": 1.916,
                            "end": 2.397,
                            "channel": 0,
                            "speaker": 0,
                            "confidence": 0.48
                        },
                        {
                            "words": [],
                            "text": "",
                            "language": "en",
                            "start": 2.797,
                            "end": 2.977,
                            "channel": 0,
                            "speaker": 0,
                            "confidence": 0.67
                        }],
                    "error": null,
                    "subtitles": [
                        {
                            "format": "srt",
                            "subtitles": "1\n00:00:01.916 --> 00:00:05.580\nJapanese Teppei. A podcast that\n\n2\n00:00:06.843 --> 00:00:09.022\nsupports Japanese language learners.\n\n3\n00:00:10.725 --> 00:00:16.490\nToday, we are discussing ice cream and ice\npops.\n\n4\n00:00:17.975 --> 00:00:18.675\nIce cream.\n\n5\n00:00:20.740 --> 00:00:21.537\nWould ice cream be acceptable?\n\n6\n00:00:26.945 --> 00:00:27.645\neveryone, hello.\n\n7\n00:00:27.745 --> 00:00:29.427\nIt is time for the pinnacle of enjoyment,\nis it not?\n\n8\n00:00:31.630 --> 00:00:32.330\nIt is hot.\n\n9\n00:00:32.528 --> 00:00:33.571\nIt is hot every day.\n\n10\n00:00:33.751 --> 00:00:35.614\nIt is excessively hot.\n\n11\n00:00:36.755 --> 00:00:40.177\nOn a hot day, I would like to eat ice\ncream, wouldn't I?\n\n12\n00:00:42.278 --> 00:00:45.536\nIce cream and ice pops.\n\n13\n00:00:46.958 --> 00:00:49.614\nOr perhaps, ice pops.\n\n14\n00:00:49.973 --> 00:00:50.802\nIt is an ice pop, isn't it?\n\n15\n00:00:50.864 --> 00:00:54.411\nIce pops, and then, ice cream.\n\n16\n00:00:56.480 --> 00:01:02.782\nWell, when we talk about ice in Japanese,\nit refers\n\n17\n00:01:03.521 --> 00:01:10.263\nto various types of ice, such as sherbet\nand ice cream. All of\n\n18\n00:01:11.302 --> 00:01:17.052\nthese are considered ice, including soft\nserve ice cream,\n\n19\n00:01:17.708 --> 00:01:24.058\nlike the ones you find at McDonald's.\nWell, it's a soft serve ice cream\n\n20\n00:01:24.939 --> 00:01:31.123\nthat's swirled around, a bit like the\nshape of, well, a rather unpleasant thing\n\n21\n00:01:31.123 --> 00:01:33.123\nfrom a comic, though\n\n22\n00:01:33.787 --> 00:01:38.412\nit is a messy topic. And ice cream is,\nwell,\n\n23\n00:01:39.130 --> 00:01:45.974\nin the general sense, the typical ice\ncream from a convenience store. There\n\n24\n00:01:47.865 --> 00:01:52.689\nvarious types ice cream available, such\n\n25\n00:01:53.851 --> 00:01:57.653\nvanilla ice cream and chocolate ice cream\n\n26\n00:02:00.439 --> 00:02:06.040\nHäagen-Dazs, as well as sorbet-like\noptions; a well-known one is\n\n27\n00:02:06.861 --> 00:02:12.204\nthe ice pop called Garigari-kun. Well, ice\ncream, well, that sherbet ice, um,\n\n28\n00:02:13.454 --> 00:02:17.630\nwell, it has\n\n29\n00:02:19.171 --> 00:02:22.555\na slightly unusual flavor, but it is\ndelicious, isn't it?\n\n30\n00:02:24.157 --> 00:02:28.180\nThe unusual flavor is that of cider,\n\n31\n00:02:30.704 --> 00:02:37.243\nit? It has a slightly sugary, slightly\ncitrus-like taste, and\n\n32\n00:02:39.388 --> 00:02:40.088\nthen...\n\n33\n00:02:40.650 --> 00:02:46.416\nRegarding the Suika Bar and Suika Bar, the\nflavor is somewhat\n\n34\n00:02:48.017 --> 00:02:53.642\nreminiscent of watermelon, and it is, to a\ndegree, a sorbet.\n\n35\n00:02:54.181 --> 00:02:58.822\nMy children are very fond of Garigari-kun\nand Suika\n\n36\n00:02:59.712 --> 00:03:04.684\nBar. I am not particularly fond of sorbet,\n\n37\n00:03:05.085 --> 00:03:11.632\nalthough I do enjoy handmade sorbet from\nrestaurants. I greatly enjoy that sherbet,\n\n38\n00:03:11.632 --> 00:03:13.632\nbut I do\n\n39\n00:03:13.632 --> 00:03:17.073\nnot care for the sherbet from convenience\nstores at all.\n\n40\n00:03:17.636 --> 00:03:23.909\nI usually purchase vanilla ice cream at\nconvenience stores, however,\n\n41\n00:03:25.696 --> 00:03:30.241\nthere are delicious vanilla ice creams and\nvanilla ice creams that are\n\n42\n00:03:31.284 --> 00:03:35.362\nnot delicious. Of course, I prefer the\ndelicious vanilla ice cream.\n\n43\n00:03:36.330 --> 00:03:37.909\nVanilla ice cream that is not\n\n44\n00:03:38.752 --> 00:03:43.580\ndelicious is, in a way, thin and too\nsweet,\n\n45\n00:03:44.955 --> 00:03:47.424\nand it does not taste like vanilla at\n\n46\n00:03:49.968 --> 00:03:56.616\nall, nor does it taste like milk at all;\nit is not delicious at all. Delicious\n\n47\n00:03:57.296 --> 00:04:03.241\nvanilla ice cream tastes like vanilla and\ntastes like milk and like milk. I prefer\n\n48\n00:04:03.241 --> 00:04:03.402\nvanilla\n\n49\n00:04:04.460 --> 00:04:08.944\nthat does not taste artificial and is not\ntoo sweet. Haagen-Dazs is a bit\n\n50\n00:04:09.569 --> 00:04:15.963\ntoo sweet for me, although I do like it\nsomewhat, but it is not\n\n51\n00:04:16.665 --> 00:04:22.597\nmy favorite. What about you This ice\ndiscussion is making me want to eat some.\n\n52\n00:04:22.597 --> 00:04:24.597\nI see. I would\n\n53\n00:04:24.597 --> 00:04:28.007\nlike to eat something after this. Goodbye,\nand see you\n"
                        },
                        {
                            "format": "vtt",
                            "subtitles": "WEBVTT\n\n1\n00:00:01.916 --> 00:00:05.580\nJapanese Teppei. A podcast that\n\n2\n00:00:06.843 --> 00:00:09.022\nsupports Japanese language learners.\n\n3\n00:00:10.725 --> 00:00:16.490\nToday, we are discussing ice cream and ice\npops.\n\n4\n00:00:17.975 --> 00:00:18.675\nIce cream.\n\n5\n00:00:20.740 --> 00:00:21.537\nWould ice cream be acceptable?\n\n6\n00:00:27.145 --> 00:00:27.845\nhello.\n\n7\n00:00:27.845 --> 00:00:29.845\neveryone, hello.\n\n8\n00:00:29.845 --> 00:00:31.845\nIt is time for the pinnacle of enjoyment,\nis it not?\n\n9\n00:00:31.845 --> 00:00:32.330\nIt is hot.\n\n10\n00:00:32.528 --> 00:00:33.571\nIt is hot every day.\n\n11\n00:00:33.751 --> 00:00:35.614\nIt is excessively hot.\n\n12\n00:00:36.755 --> 00:00:40.177\nOn a hot day, I would like to eat ice\ncream, wouldn't I?\n\n13\n00:00:42.278 --> 00:00:45.536\nIce cream and ice pops.\n\n14\n00:00:46.958 --> 00:00:49.614\nOr perhaps, ice pops.\n\n15\n00:00:49.973 --> 00:00:50.802\nIt is an ice pop, isn't it?\n\n16\n00:00:50.864 --> 00:00:54.411\nIce pops, and then, ice cream.\n\n17\n00:00:56.480 --> 00:01:02.782\nWell, when we talk about ice in Japanese,\nit refers\n\n18\n00:01:03.521 --> 00:01:10.263\nto various types of ice, such as sherbet\nand ice cream. All of\n\n19\n00:01:11.302 --> 00:01:17.052\nthese are considered ice, including soft\nserve ice cream,\n\n20\n00:01:17.708 --> 00:01:24.058\nlike the ones you find at McDonald's.\nWell, it's a soft serve ice cream\n\n21\n00:01:24.939 --> 00:01:31.123\nthat's swirled around, a bit like the\nshape of, well, a rather unpleasant thing\n\n22\n00:01:31.123 --> 00:01:33.123\nfrom a comic, though\n\n23\n00:01:33.787 --> 00:01:38.412\nit is a messy topic. And ice cream is,\nwell,\n\n24\n00:01:39.130 --> 00:01:45.974\nin the general sense, the typical ice\ncream from a convenience store. There\n\n25\n00:01:47.865 --> 00:01:52.689\nvarious types ice cream available, such\n\n26\n00:01:53.851 --> 00:01:57.653\nvanilla ice cream and chocolate ice cream\n\n27\n00:02:00.439 --> 00:02:06.040\nHäagen-Dazs, as well as sorbet-like\noptions; a well-known one is\n\n28\n00:02:06.861 --> 00:02:12.204\nthe ice pop called Garigari-kun. Well, ice\ncream, well, that sherbet ice, um,\n\n29\n00:02:13.454 --> 00:02:17.630\nwell, it has\n\n30\n00:02:19.171 --> 00:02:22.555\na slightly unusual flavor, but it is\ndelicious, isn't it?\n\n31\n00:02:24.157 --> 00:02:28.180\nThe unusual flavor is that of cider,\n\n32\n00:02:30.704 --> 00:02:37.243\nit? It has a slightly sugary, slightly\ncitrus-like taste, and\n\n33\n00:02:39.388 --> 00:02:40.088\nthen...\n\n34\n00:02:40.650 --> 00:02:46.416\nRegarding the Suika Bar and Suika Bar, the\nflavor is somewhat\n\n35\n00:02:48.017 --> 00:02:53.642\nreminiscent of watermelon, and it is, to a\ndegree, a sorbet.\n\n36\n00:02:54.181 --> 00:02:58.822\nMy children are very fond of Garigari-kun\nand Suika\n\n37\n00:02:59.712 --> 00:03:04.684\nBar. I am not particularly fond of sorbet,\n\n38\n00:03:05.085 --> 00:03:11.632\nalthough I do enjoy handmade sorbet from\nrestaurants. I greatly enjoy that sherbet,\n\n39\n00:03:11.632 --> 00:03:13.632\nbut I do\n\n40\n00:03:13.632 --> 00:03:17.073\nnot care for the sherbet from convenience\nstores at all.\n\n41\n00:03:17.636 --> 00:03:23.909\nI usually purchase vanilla ice cream at\nconvenience stores, however,\n\n42\n00:03:25.696 --> 00:03:30.241\nthere are delicious vanilla ice creams and\nvanilla ice creams that are\n\n43\n00:03:31.284 --> 00:03:35.362\nnot delicious. Of course, I prefer the\ndelicious vanilla ice cream.\n\n44\n00:03:36.330 --> 00:03:37.909\nVanilla ice cream that is not\n\n45\n00:03:38.752 --> 00:03:43.580\ndelicious is, in a way, thin and too\nsweet,\n\n46\n00:03:44.955 --> 00:03:47.424\nand it does not taste like vanilla at\n\n47\n00:03:49.968 --> 00:03:56.616\nall, nor does it taste like milk at all;\nit is not delicious at all. Delicious\n\n48\n00:03:57.296 --> 00:04:03.241\nvanilla ice cream tastes like vanilla and\ntastes like milk and like milk. I prefer\n\n49\n00:04:03.241 --> 00:04:03.402\nvanilla\n\n50\n00:04:04.460 --> 00:04:08.944\nthat does not taste artificial and is not\ntoo sweet. Haagen-Dazs is a bit\n\n51\n00:04:09.569 --> 00:04:15.963\ntoo sweet for me, although I do like it\nsomewhat, but it is not\n\n52\n00:04:16.665 --> 00:04:22.597\nmy favorite. What about you This ice\ndiscussion is making me want to eat some.\n\n53\n00:04:22.597 --> 00:04:24.597\nI see. I would\n\n54\n00:04:24.597 --> 00:04:28.007\nlike to eat something after this. Goodbye,\nand see you\n"
                        }
                    ]
                }
            ],
            "exec_time": 8.881133247002959,
            "error": null
        }
    }
}
```