# NeMo Guardrails + Ollama デモ

NeMo Guardrails 0.24.1 から、ローカルの Ollama で動く `sileader/qwen3guard:0.6b` を呼び出して入力を検査します。会話を生成するデモではありません。

## 準備と実行

Python 3.12 と Ollama を用意します。初回は仮想環境とモデルをセットアップしてください。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
ollama pull sileader/qwen3guard:0.6b
```

```bash
cd ~/デスクトップ/nemo-guardrails-demo
.venv/bin/python demo.py
```

デバッグ時は1件だけ選び、必要なら Ollama の応答も表示できます。応答中の改行はエスケープして表示するため、各サンプルの結果に混ざりません。

```bash
.venv/bin/python demo.py --case 3 --verbose
```

`demo.py` は NeMo Guardrails を読み込む前に `NEMO_GUARDRAILS_NO_USAGE_STATS=1` を設定します。Ollama の接続先は `http://127.0.0.1:11434/api/chat` です。接続できない場合は Ollama のサービスが動いているか確認してください。


## Ollama のモデルが動いているか確認

次のコマンドは Ollama に直接「こんにちは」を判定させます。応答に `Safety: Safe` が含まれれば、モデルから返答を得られています。

```bash
curl -sS http://127.0.0.1:11434/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"model":"sileader/qwen3guard:0.6b","messages":[{"role":"user","content":"こんにちは"}],"stream":false}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["message"]["content"])'
ollama ps
```

`ollama ps` の `PROCESSOR` 列で CPU/GPU のどちらで動いているかも確認できます。`ollama list` はダウンロード済みモデルの一覧で、実行中かどうかは示しません。NeMo 経由の動作は、上の `demo.py` の出力で `rail=qwen guard input` の行を確認してください。

## 構成

- `config/config.yml`: 入出力の正規表現、Qwen3Guard の接続先、ブロック対象の判定ラベルを設定します。
- `config/rails.co`: Qwen3Guard がブロック判定を返したときに入力を拒否するフローです。
- `config/actions.py`: Ollama の API を呼び、応答の `Safety: Safe / Controversial / Unsafe` を読み取ります。
- `demo.py`: `check()` でサンプルの入力と出力を検査します。

入力は先に正規表現で調べ、その後 Qwen3Guard で意味に基づく判定をします。`API_KEY` は正規表現で、危険な依頼の例は Qwen3Guard の `Unsafe` 判定でブロックされます。出力側は正規表現だけで検査しています。そのため、デモにある assistant の「爆弾の作り方はxxxです」は通過します。

現在は `Unsafe` だけをブロックします。`Controversial` も止めるには `config/config.yml` の `block_labels` に追加します。小型の安全判定モデルなので、実運用では用途に合う評価が必要です。

モデルの配布元: [Ollama のモデルページ](https://ollama.com/sileader/qwen3guard:0.6b)。元モデルの仕様: [Qwen3Guard モデルカード](https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B)。
