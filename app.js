// ゲームの状態管理
const gameState = {
    currentScreen: 'opening',
    quiz1Completed: false,
    quiz2Completed: false,
    currentQuiz: 'quiz1',
    modelChoice: 'gpt-4o',
    ttsEnabled: true,
    ttsProvider: 'openai',
    messages: [],
    openaiMessages: [],
    avatarImage: null
};

// プロンプト
const prompts = {
    quiz1: null,
    quiz2: null
};

// DOM要素の参照
const screens = {
    opening: document.getElementById('opening-screen'),
    opening2: document.getElementById('opening2-screen'),
    quizIntro: document.getElementById('quiz-intro-screen'),
    quiz: document.getElementById('quiz-screen'),
    middleSuccess: document.getElementById('middle-success-screen'),
    quiz2: document.getElementById('quiz2-screen'),
    finalSuccess: document.getElementById('final-success-screen'),
    ending: document.getElementById('ending-screen')
};

// 音声要素
const doorOpenSound = document.getElementById('door-open-sound');

// APIキー（本番環境では環境変数から取得するか、バックエンドを経由して安全に扱うべき）
const API_KEYS = {
    openai: '', // 実際のAPIキーを設定してください
    gemini: ''  // 実際のAPIキーを設定してください
};

// APIキーを設定するための関数
function setApiKey(provider, key) {
    if (provider && key) {
        API_KEYS[provider] = key;
        console.log(`${provider} APIキーが設定されました`);
        return true;
    }
    return false;
}

// 初期化
async function init() {
    // APIキーを読み込む
    await loadApiKeys();
    
    // プロンプトを読み込む
    await loadPrompts();
    
    // アバター画像を読み込む
    loadAvatarImage();
    
    // イベントリスナーを設定
    setupEventListeners();
    
    // 初期画面を表示
    showScreen('opening');
}

// プロンプトをファイルから読み込む
async function loadPrompts() {
    try {
        const quiz1Response = await fetch('prompt.txt');
        prompts.quiz1 = await quiz1Response.text();
        
        const quiz2Response = await fetch('prompt2.txt');
        prompts.quiz2 = await quiz2Response.text();
    } catch (error) {
        console.error('プロンプトの読み込みエラー:', error);
    }
}

// アバター画像を読み込む
function loadAvatarImage() {
    const img = new Image();
    img.src = 'src/images/opening.png';
    img.onload = () => {
        gameState.avatarImage = img;
    };
}

// APIキーをファイルから読み込む
async function loadApiKeys() {
    try {
        // OpenAI APIキーを読み込む
        const openaiKeyResponse = await fetch('.streamlit/secrets.toml');
        const openaiKeyText = await openaiKeyResponse.text();
        const openaiKeyMatch = openaiKeyText.match(/OPENAI_API_KEY\s*=\s*"([^"]+)"/);
        
        if (openaiKeyMatch && openaiKeyMatch[1]) {
            setApiKey('openai', openaiKeyMatch[1]);
        } else {
            console.error('OpenAI APIキーが見つかりませんでした');
            showApiKeyDialog();
            return;
        }
        
        // Gemini APIキーを読み込む
        const geminiKeyResponse = await fetch('src/credentials/gemini-api-key.txt');
        const geminiKey = await geminiKeyResponse.text();
        
        if (geminiKey && geminiKey.trim()) {
            setApiKey('gemini', geminiKey.trim());
        }
        
        console.log('APIキーの読み込みが完了しました');
    } catch (error) {
        console.error('APIキーの読み込みエラー:', error);
        // 読み込みに失敗した場合はダイアログを表示
        showApiKeyDialog();
    }
}

// イベントリスナーを設定
function setupEventListeners() {
    // opening画面の廃墟のドア画像をクリックしたら次の画面へ
    document.querySelector('#opening-screen .scene-image').addEventListener('click', () => {
        showScreen('opening2');
        playDoorOpenSound();
        setTimeout(() => {
            showScreen('quizIntro');
        }, 2000);
    });
    
    // 隠しボタン（クイズ2へジャンプ）
    document.getElementById('jump-to-quiz2').addEventListener('click', () => {
        gameState.currentQuiz = 'quiz2';
        gameState.quiz1Completed = true;
        gameState.messages = [];
        gameState.openaiMessages = [
            { role: 'system', content: prompts.quiz2 }
        ];
        showScreen('quiz2');
    });
    
    // クイズイントロ画面
    document.getElementById('challenge-button').addEventListener('click', () => {
        gameState.messages = [];
        gameState.openaiMessages = [
            { role: 'system', content: prompts.quiz1 }
        ];
        showScreen('quiz');
    });
    
    // サイドバートグルボタンを追加
    addSidebarToggle('quiz');
    addSidebarToggle('quiz2');
    
    // クイズ1画面
    // 送信ボタンは削除されたのでエンターキーのみで送信
    document.getElementById('user-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSubmit('quiz');
        }
    });
    
    // モデル選択（クイズ1）
    document.getElementById('gpt-4o').addEventListener('change', () => {
        gameState.modelChoice = 'gpt-4o';
    });
    
    document.getElementById('gemini').addEventListener('change', () => {
        gameState.modelChoice = 'gemini';
    });
    
    // TTS設定（クイズ1）
    document.getElementById('tts-enabled').addEventListener('change', (e) => {
        gameState.ttsEnabled = e.target.checked;
    });
    
    document.getElementById('openai-tts').addEventListener('change', () => {
        gameState.ttsProvider = 'openai';
    });
    
    document.getElementById('google-tts').addEventListener('change', () => {
        gameState.ttsProvider = 'google';
    });
    
    // 中間成功画面
    document.getElementById('next-quiz-button').addEventListener('click', () => {
        gameState.currentQuiz = 'quiz2';
        gameState.messages = [];
        gameState.openaiMessages = [
            { role: 'system', content: prompts.quiz2 }
        ];
        showScreen('quiz2');
    });
    
    // クイズ2画面
    document.getElementById('send-button-2').addEventListener('click', () => {
        handleSubmit('quiz2');
    });
    
    document.getElementById('user-input-2').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSubmit('quiz2');
        }
    });
    
    // モデル選択（クイズ2）
    document.getElementById('gpt-4o-2').addEventListener('change', () => {
        gameState.modelChoice = 'gpt-4o';
    });
    
    document.getElementById('gemini-2').addEventListener('change', () => {
        gameState.modelChoice = 'gemini';
    });
    
    // TTS設定（クイズ2）
    document.getElementById('tts-enabled-2').addEventListener('change', (e) => {
        gameState.ttsEnabled = e.target.checked;
    });
    
    document.getElementById('openai-tts-2').addEventListener('change', () => {
        gameState.ttsProvider = 'openai';
    });
    
    document.getElementById('google-tts-2').addEventListener('change', () => {
        gameState.ttsProvider = 'google';
    });
    
    // 最終成功画面
    document.getElementById('next-button').addEventListener('click', () => {
        playDoorOpenSound();
        setTimeout(() => {
            showScreen('ending');
        }, 2000);
    });
}

// サイドバートグルボタンを追加する関数
function addSidebarToggle(screenId) {
    // トグルボタン要素を作成
    const toggleButton = document.createElement('button');
    toggleButton.className = 'sidebar-toggle';
    toggleButton.innerHTML = '⚙️';
    toggleButton.setAttribute('aria-label', '設定');
    
    // 対象の画面にトグルボタンを追加
    const targetScreen = document.getElementById(`${screenId}-screen`);
    if (targetScreen) {
        targetScreen.appendChild(toggleButton);
        
        // クリックイベントを追加
        toggleButton.addEventListener('click', () => {
            const sidebar = targetScreen.querySelector('.sidebar');
            const chatContainer = targetScreen.querySelector('.chat-container');
            const inputContainer = targetScreen.querySelector('.input-container');
            
            sidebar.classList.toggle('visible');
            
            // サイドバーの表示状態に応じてコンテナのクラスを切り替え
            if (sidebar.classList.contains('visible')) {
                chatContainer.classList.add('sidebar-visible');
                inputContainer.classList.add('sidebar-visible');
            } else {
                chatContainer.classList.remove('sidebar-visible');
                inputContainer.classList.remove('sidebar-visible');
            }
        });
    }
}

// 画面を表示する
function showScreen(screenName) {
    gameState.currentScreen = screenName;
    
    // すべての画面を非表示にする
    Object.values(screens).forEach(screen => {
        if (screen) screen.classList.add('hidden');
    });
    
    // 指定された画面を表示する
    if (screens[screenName]) {
        screens[screenName].classList.remove('hidden');
    }
}

// メッセージ送信を処理する
async function handleSubmit(quizType) {
    const inputId = quizType === 'quiz' ? 'user-input' : 'user-input-2';
    const messagesContainerId = quizType === 'quiz' ? 'chat-messages' : 'chat-messages-2';
    
    const inputElement = document.getElementById(inputId);
    const currentInput = inputElement.value.trim();
    
    if (currentInput) {
        // ユーザーメッセージを追加
        const userMessage = {
            role: 'user',
            content: currentInput
        };
        
        gameState.messages.push(userMessage);
        gameState.openaiMessages.push({
            role: 'user',
            content: currentInput
        });
        
        // ユーザーメッセージを表示
        displayMessage('user', currentInput, messagesContainerId);
        
        // 入力フィールドをクリア
        inputElement.value = '';
        
        // AIの応答を取得
        const aiResponse = await getChatResponse(gameState.openaiMessages);
        
        if (aiResponse) {
            // アシスタントメッセージを追加
            const assistantMessage = {
                role: 'assistant',
                content: aiResponse
            };
            
            gameState.messages.push(assistantMessage);
            gameState.openaiMessages.push({
                role: 'assistant',
                content: aiResponse
            });
            
            // アシスタントメッセージを表示
            displayMessage('assistant', aiResponse, messagesContainerId, true);
            
            // クイズ完了チェック
            if (quizType === 'quiz' && aiResponse.includes('これでクイズ1は終了だ')) {
                gameState.quiz1Completed = true;
                setTimeout(() => {
                    showScreen('middleSuccess');
                }, 2000);
            } else if (quizType === 'quiz2' && aiResponse.includes('これでクイズ2は終了だ') && gameState.messages.length > 3) {
                gameState.quiz2Completed = true;
                setTimeout(() => {
                    showScreen('finalSuccess');
                }, 2000);
            }
        }
    }
}

// メッセージを表示する
function displayMessage(role, content, containerId, isNewMessage = false) {
    const messagesContainer = document.getElementById(containerId);
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${role}-message`;
    
    if (role === 'assistant') {
        // アバター画像を追加
        if (gameState.avatarImage) {
            const avatarElement = document.createElement('img');
            avatarElement.className = 'avatar';
            avatarElement.src = 'src/images/opening.png';
            messageElement.appendChild(avatarElement);
        }
        
        // 音声を生成して再生（新しいメッセージの場合のみ）
        if (gameState.ttsEnabled && isNewMessage) {
            generateAndPlaySpeech(content);
        }
    }
    
    const contentElement = document.createElement('div');
    contentElement.className = 'message-content';
    contentElement.textContent = content;
    
    messageElement.appendChild(contentElement);
    messagesContainer.appendChild(messageElement);
    
    // スクロールを最下部に移動
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// AIの応答を取得する
async function getChatResponse(messages) {
    try {
        if (gameState.modelChoice === 'gpt-4o') {
            // OpenAI APIを使用
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${API_KEYS.openai}`
                },
                body: JSON.stringify({
                    model: 'gpt-4o',
                    messages: messages,
                    temperature: 0.7,
                    max_tokens: 1000
                })
            });
            
            const data = await response.json();
            return data.choices[0].message.content;
        } else if (gameState.modelChoice === 'gemini') {
            // Gemini APIを使用
            // 注意: このサンプルコードでは簡略化のため、フロントエンドからの直接APIコールを示していますが、
            // 実際の実装ではセキュリティ上の理由からバックエンドを経由すべきです
            
            // Gemini用にメッセージをフォーマット
            const geminiMessages = [];
            for (let i = 0; i < messages.length - 1; i++) {
                const msg = messages[i];
                if (msg.role === 'system') {
                    geminiMessages.push({
                        role: 'user',
                        parts: [{ text: msg.content }]
                    });
                } else {
                    geminiMessages.push({
                        role: msg.role === 'user' ? 'user' : 'model',
                        parts: [{ text: msg.content }]
                    });
                }
            }
            
            // 最後のメッセージを送信
            const lastMessage = messages[messages.length - 1];
            
            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${API_KEYS.gemini}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contents: [
                        {
                            role: lastMessage.role === 'user' ? 'user' : 'model',
                            parts: [{ text: lastMessage.content }]
                        }
                    ],
                    generationConfig: {
                        temperature: 0.7,
                        maxOutputTokens: 1000
                    }
                })
            });
            
            const data = await response.json();
            return data.candidates[0].content.parts[0].text;
        }
    } catch (error) {
        console.error('エラーが発生しました:', error);
        return null;
    }
}

// 音声を生成して再生する
async function generateAndPlaySpeech(text) {
    try {
        // 読み方ガイドを適用
        const modifiedText = applyPronunciationGuides(text);
        
        let audioData = null;
        
        if (gameState.ttsProvider === 'openai') {
            // OpenAI TTSを使用
            const response = await fetch('https://api.openai.com/v1/audio/speech', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${API_KEYS.openai}`
                },
                body: JSON.stringify({
                    model: 'tts-1',
                    voice: 'ash',
                    input: modifiedText,
                    speed: 1.0
                })
            });
            
            audioData = await response.blob();
        } else {
            // Google TTSを使用
            // 注意: このサンプルコードでは簡略化のため、フロントエンドからの直接APIコールを示していますが、
            // 実際の実装ではセキュリティ上の理由からバックエンドを経由すべきです
            
            // Google Cloud Text-to-Speech APIの実装はここに追加
            // 実際の実装では、バックエンドを経由してGoogle Cloud APIを呼び出す必要があります
        }
        
        if (audioData) {
            const audioUrl = URL.createObjectURL(audioData);
            const audioElement = new Audio(audioUrl);
            audioElement.play();
        }
    } catch (error) {
        console.error('音声生成エラー:', error);
    }
}

// 読み方ガイドを適用する
function applyPronunciationGuides(text) {
    // 読み方マッピング辞書
    const pronunciationMap = {
        "源頼朝": "源頼朝みなもとのよりとも",
        "征夷大将軍": "せいいたいしょうぐん",
        "趣":"おもむき",
        "浪人生":"ろうにんせい",
        "板垣政参": "いたがきまさみつ",
        "瑞宝中綬章": "ずいほうちゅうじゅしょう",
        "裏店": "うらみせ",
        "肉飯": "にくめし",
        "男く祭": "おとこくさい",
        "芙蓉": "ふよう",
        "西鉄": "にしてつ",
        "久留米":"くるめ",
        "チーム1":"チームいち",
        "チーム2":"チームに",
        "チーム3":"チームさん",
        "チーム4":"チームよん",
        "チーム5":"チームご",
        "1192":"せんひゃくきゅうじゅうに",
        "2005":"にせんご",
        "1968":"せんきゅうひゃくろうじゅうはち",
        "吉川敦": "よしかわあつし",
        "黒水": "くろうず",
        "七福神":"しちふくじん", 
        "満々":"まんまん",
        "松下由依":"まつしたゆい",
        "勝連":"かつれん",
        "小林":"こばやし",
        "松雪":"まつゆき",
        "中島":"なかじま",
        "山本":"やまもと",
        "上坂元":"かみさかもと",
        "秋本":"あきもと",
        "松浦":"まつうら",
        "田中":"たなか",
        "吉開":"よしかい",
        "年": "ねん",
        "織田信長":"おだのぶなが",
        "町田": "まちだ",
        "情け": "なさけ",
        "三権分立":"さんけんぶんりつ",
        "県花":"けんか",
    };
    
    // 辞書内の各項目に対して読み方を追加
    for (const [word, reading] of Object.entries(pronunciationMap)) {
        if (text.includes(word) && word !== reading) {
            text = text.replace(new RegExp(word, 'g'), reading);
        }
    }
    
    return text;
}

// ドアが開く音を再生する
function playDoorOpenSound() {
    doorOpenSound.currentTime = 0;
    doorOpenSound.play().catch(error => {
        console.error('音声再生エラー:', error);
    });
}

// APIキー設定ダイアログを表示
function showApiKeyDialog() {
    const apiKeyDialog = document.createElement('div');
    apiKeyDialog.className = 'api-key-dialog';
    apiKeyDialog.innerHTML = `
        <div class="api-key-dialog-content">
            <h2>APIキーの設定</h2>
            <p>ゲームを開始するにはAPIキーを設定してください。</p>
            <div class="api-key-input">
                <label for="openai-api-key">OpenAI APIキー:</label>
                <input type="password" id="openai-api-key" placeholder="sk-..." />
            </div>
            <div class="api-key-input">
                <label for="gemini-api-key">Gemini APIキー (任意):</label>
                <input type="password" id="gemini-api-key" placeholder="..." />
            </div>
            <button id="save-api-keys">保存して開始</button>
        </div>
    `;
    
    document.body.appendChild(apiKeyDialog);
    
    // 保存ボタンのイベントリスナー
    document.getElementById('save-api-keys').addEventListener('click', () => {
        const openaiKey = document.getElementById('openai-api-key').value.trim();
        const geminiKey = document.getElementById('gemini-api-key').value.trim();
        
        if (setApiKey('openai', openaiKey)) {
            setApiKey('gemini', geminiKey);
            apiKeyDialog.remove();
        } else {
            alert('OpenAI APIキーを入力してください。');
        }
    });
}

// 初期化を実行
document.addEventListener('DOMContentLoaded', init); 