# 出典と検証対象

確認日: 2026-09-06。公式英語ドキュメントの表示バージョン: MoonBit v0.10.11。
本教材は公式教材ではありません。説明と例題は本教材用に作成し、公式ドキュメントの本文・画像は転載していません。

| 場面 | 主な根拠 |
|---|---|
| 01–03 | [公式サイト](https://www.moonbitlang.com/)、[Introduction](https://docs.moonbitlang.com/en/latest/language/introduction.html) |
| 04–20 | [Fundamentals](https://docs.moonbitlang.com/en/latest/language/fundamentals.html)：型、let、関数、制御構文、配列、構造体、enum、Option、型パラメーター |
| 21–24 | [Method and Trait](https://docs.moonbitlang.com/en/latest/language/methods.html)：型に関連する関数、明示的impl、型制約、extend |
| 24 | [Deriving traits](https://docs.moonbitlang.com/en/latest/language/derive.html)：derive(Eq) |
| 25–27 | [Error handling](https://docs.moonbitlang.com/en/latest/language/error-handling.html)、Fundamentals：Result、suberror、raise、try/catch |
| 28 | [Writing Tests](https://docs.moonbitlang.com/en/latest/language/tests.html)：test、assert_eq、moon test |
| 29 | [Managing Projects with Packages](https://docs.moonbitlang.com/en/latest/language/packages.html)：package/module、moon.pkg、公開範囲 |
| 30–32 | 上記の概念を用いた独自の設計演習・まとめ |

実行方法: [Running .mbtx Scripts](https://docs.moonbitlang.com/en/latest/toolchain/moon/script-mode.html)。
ツールチェーン入手元: [公式ダウンロード](https://www.moonbitlang.com/download/)。

## 検証環境

- Windows x86_64、Wasm GCターゲット
- moon 0.1.20260827 (d0aaa07 2026-08-27)
- moonc v0.10.11+6ff76a5f9 (2026-08-28)
- moonrun 0.1.20260827 (d0aaa07 2026-08-27)
- ツールチェーンZIPのSHA256: `f08e1d54efff3a99319f686b11ceb1a1454288e460e7f20a77219f8d4e08f538`。公式配布のチェックサムと照合済み。

`latest`は変わります。将来の再生成ではコンパイラーバージョンを記録し直し、例題も再検証してください。
本教材は言語仕様の全項目を網羅しません。非同期、FFI、形式検証、全演算子、詳細なアクセス制御などは範囲外です。

## 検証結果の読み方

`VALIDATION.json`は25個の例題の標準出力比較と7件のテスト結果です。
一部の短い例には、説明のために宣言だけを示す未使用フィールド・コンストラクターの警告があります。
非推奨のタプル表示は修正済みです。未使用の警告と実行失敗は区別しています。
構文が受理されたことだけではなく、表示する結果も期待値と比較しています。
独立したテスト群では、値なし、エラー回復、全状態分岐、元配列が保存されることも確認します。
