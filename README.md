# 漆黒の遥藍地 (Hell High School)

JavaScriptで実装された対話型クイズゲームです。元々はStreamlitで作られたアプリケーションをJavaScriptに移植したものです。

## 概要

このゲームは、プレイヤーが「黒水校長」と対話しながら様々なクイズに答えていくインタラクティブなアドベンチャーゲームです。
2つのステージに分かれており、それぞれのステージでクイズに正解することで次のステージに進むことができます。

## 特徴

- 完全にクライアントサイドで動作するJavaScriptアプリケーション
- OpenAI GPT-4oまたはGoogle Geminiを使用した対話型AI
- テキスト読み上げ機能（OpenAI TTSまたはGoogle TTSを使用可能）
- 魅力的なビジュアルとサウンドエフェクト
- レスポンシブデザイン

## 使用方法

1. `API_KEYS`オブジェクト内の`openai`と`gemini`にそれぞれのAPIキーを設定してください。
   ```javascript
   const API_KEYS = {
       openai: 'your-openai-api-key',
       gemini: 'your-gemini-api-key'
   };
   ```

2. ローカルサーバーを起動して`3rd-stage.html`を開いてください。
   ```bash
   # Pythonを使用する場合
   python -m http.server 9000
   
   # Node.jsを使用する場合
   npx http-server
   ```

3. ブラウザで`http://localhost:9000/3rd-stage.html`にアクセスしてゲームを開始します。

## ファイル構成

- `3rd-stage.html`: メインのHTMLファイル
- `styles.css`: スタイルシート
- `app.js`: JavaScriptのメインコード
- `prompt.txt`: クイズ1のプロンプト
- `prompt2.txt`: クイズ2のプロンプト
- `src/images/`: 画像ファイル
- `src/audio/`: 音声ファイル

## 注意事項

- このアプリケーションはデモンストレーション目的で作成されています。
- 実際の運用では、APIキーをクライアントサイドに直接埋め込むのではなく、バックエンドサーバーを経由してAPIを呼び出すことをお勧めします。
- ブラウザのCORSポリシーにより、ローカルファイルシステムから直接HTMLを開くと一部機能が動作しない場合があります。ローカルサーバーを使用してアクセスしてください。

## ライセンス

このプロジェクトは個人的な使用のために作成されました。商用利用は禁止されています。 