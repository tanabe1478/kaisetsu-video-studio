"""Author the lesson, transcript, and independently runnable code examples."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
scenes=[]
def add(chapter, heading, lines, *, code=None, points=None, setup='', check='', expression='normal', pose='point', pause=.8):
    replacements={'MoonBit':'ムーンビット','VOICEVOX':'ボイスボックス','let mut':'レット ミュート','let':'レット','Int':'イント','Double':'ダブル','Bool':'ブール','String':'ストリング','Unit':'ユニット','Array':'アレイ','FixedArray':'フィックストアレイ','Option':'オプション','Some':'サム','None':'ナン','Result':'リザルト','Ok':'オーケー','Err':'エラー','struct':'ストラクト','enum':'イーナム','match':'マッチ','trait':'トレイト','impl':'インプル','derive':'ディライブ','Debug':'デバッグ','Eq':'イーク','raise':'レイズ','suberror':'サブエラー','try':'トライ','catch':'キャッチ','fn':'エフエヌ','pub':'パブ','mut':'ミュート','main':'メイン','test':'テスト','return':'リターン','Self':'セルフ','nobreak':'ノーブレイク','while':'ワイル','for':'フォー','if':'イフ','else':'エルス','map':'マップ','push':'プッシュ','extend':'エクステンド','T?':'ティー、クエスチョン','T':'ティー','API':'エーピーアイ','FFI':'エフエフアイ','GC':'ジーシー','JavaScript':'ジャバスクリプト','WebAssembly':'ウェブアセンブリ'}
    narration=[]
    for line in lines:
        speech=line
        for a,b in sorted(replacements.items(),key=lambda x:-len(x[0])):
            speech=re.sub(r'(?<![A-Za-z])'+re.escape(a)+r'(?![A-Za-z])',lambda _:b,speech)
        narration.append({'text':line,'speech':speech})
    scene={'chapter':chapter,'heading':heading,'narration':narration,'expression':expression,'pose':pose,'pause':pause}
    if code:
        scene['code']=code
        number=len(scenes)+1
        (ROOT/'examples').mkdir(exist_ok=True)
        source=setup+'\n'+code+'\n'+check+'\n'
        (ROOT/'examples'/f'{number:02d}.mbtx').write_text(source.strip()+'\n',encoding='utf-8')
    else:scene['points']=points or []
    scenes.append(scene)

add('01 はじめに','型と式から読むMoonBit',[
'こんにちは、ずんだもんなのだ。今回はMoonBitの言語仕様を、短いコードで学ぶのだ。',
'変数と関数を少し知っている人向けに、型、分岐、データの表現を順番に説明するのだ。',
'途中で結果を予想する小問も出すのだ。コードは一時停止して読んでほしいのだ。',
'これは公式教材ではなく、公式ドキュメントと実行確認に基づく入門動画なのだ。'],
points=['対象：変数と関数を少し知っている人','短い例で、型・式・データ設計を学ぶ','独自の解説教材 / 2026-09-06確認'],expression='happy',pose='wave')
add('01 はじめに','今回の範囲とバージョン',[
'MoonBitは静的に型を検査する言語なのだ。実行する前に、値の種類の不整合を見つけるのだ。',
'今回はコンパイラーのバージョン、ゼロ点十点十一でコード例を確認するのだ。',
'言語とツールは更新されるので、古い記事の構文と違うことがあるのだ。',
'非同期処理、外部言語との連携、形式検証は、今回の入門の範囲には含めないのだ。'],
points=['検証：moonc v0.10.11（2026-08-28）','公式英語ドキュメントのlatestを参照','非同期・FFI・形式検証は別の発展テーマ'])
add('02 変数と型','最小のプログラム',[
'最初は画面に文字を出すだけなのだ。fn mainという特別な入口に処理を書くのだ。',
'丸括弧を付けた普通の関数宣言とは、入口の書き方が少し違うのだ。',
'printlnは改行付きで表示する関数なのだ。この例では、ハロー、ムーンビットと表示するのだ。',
'以降のコードも、補足が必要な定義を添えて実行できる形で保存しておくのだ。'],code='fn main {\n  println("Hello, MoonBit!")\n}')
add('02 変数と型','let：名前と値を結び付ける',[
'letで値に名前を付けるのだ。ここでは、二十七という整数に、ポイントという名前を付けるのだ。',
'型を書かなくても、この値からIntという整数型が推論されるのだ。',
'次の行は、二倍した結果を別の名前に結び付けているのだ。表示される値は五十四なのだ。',
'型を省略できることと、型が存在しないことは違うのだ。型推論は静的な検査の一部なのだ。'],code='fn main {\n  let points = 27\n  let doubled : Int = points * 2\n  println(doubled) // 54\n}')
add('02 変数と型','再代入にはlet mut',[
'普通のletで作った名前には、別の値を再代入できないのだ。',
'あとで数を更新したいときは、let mutと書くのだ。この例の結果は四なのだ。',
'変えなくてよい名前は、そのままにしておくと、後の処理を読みやすくできるのだ。',
'ただし、名前を再代入できないことと、中身を変更できないことは別なのだ。配列で後ほど確認するのだ。'],code='fn main {\n  let mut count = 1\n  count = count + 3\n  println(count) // 4\n}')
add('02 変数と型','型は値の使い方を決める',[
'整数のInt、小数のDouble、真偽値のBool、文字列のStringを見てみるのだ。',
'型を書く場合は、名前のあとにコロンと型名を置くのだ。',
'整数を持つ変数と小数を計算するなら、変換を明示して意図を伝えるのだ。',
'この例は整数の八を小数へ変換してから、零点五を足すので、八点五になるのだ。'],code='fn main {\n  let n : Int = 8\n  let ratio : Double = 0.5\n  let ready : Bool = true\n  let label : String = "score"\n  println(n.to_double() + ratio) // 8.5\n  println(ready)\n  println(label)\n}')
add('02 変数と型','文字列に値を埋め込む',[
'文章の中へ計算結果を入れるには、文字列補間を使えるのだ。',
'画面のように、バックスラッシュに続く波括弧の中へ式を書くのだ。',
'この例では、計算した九が文章の中に入るのだ。文字列と整数を無理に足す必要はないのだ。',
'丸括弧で値を並べたタプルと、角括弧で要素を並べた配列も、ここで見分けておくのだ。'],code='fn main {\n  let score = 3 * 3\n  println("score = \\{score}")\n  let pair : (String, Int) = ("zunda", 9)\n  println(pair.1) // 9\n}')
add('03 関数と制御構文','関数は最後の式を返す',[
'トップレベルの関数は、引数と戻り値の型を明示して定義するのだ。',
'矢印の右にあるIntが戻り値の型なのだ。関数の最後に置いた式が結果になるのだ。',
'このadd関数へ六と七を渡すと、十三が返るのだ。毎回returnと書く必要はないのだ。',
'早く関数から抜けるときはreturnも使えるのだ。値を返さない処理ではUnitが登場するのだ。'],code='fn add(a : Int, b : Int) -> Int {\n  a + b\n}\nfn main {\n  println(add(6, 7)) // 13\n}')
add('03 関数と制御構文','ifも値を作る式',[
'MoonBitでは、ifを使って値を選ぶこともできるのだ。',
'この例では、温度が二十以上ならワーム、それ以外ならクールという文字列を作るのだ。',
'両方の枝が同じ種類の値を返すので、結果を一つの名前に受け取れるのだ。',
'片方が文字列でもう片方が整数では、この使い方は型が合わないのだ。式として読むことが大切なのだ。'],code='fn main {\n  let temperature = 24\n  let label = if temperature >= 20 {\n    "warm"\n  } else {\n    "cool"\n  }\n  println(label) // warm\n}')
add('03 関数と制御構文','小問：最後に表示する数は？',[
'ここで一度、自分で結果を予想してほしいのだ。最初の値は五なのだ。',
'条件は、三より大きいかどうかなのだ。条件が成立した枝の値が、answerに入るのだ。',
'どちらの枝を通るか、最後に何が表示されるかを考えるのだ。必要なら一時停止してほしいのだ。'],code='fn main {\n  let n = 5\n  let answer = if n > 3 { n * 2 } else { n + 2 }\n  println(answer)\n}',expression='thinking',pose='think',pause=3)
add('03 関数と制御構文','答えは10：式を順番に読む',[
'答えは十なのだ。五は三より大きいので、二倍する枝が選ばれるのだ。',
'大切なのは、条件分岐そのものが値を返し、その値に名前が付くという流れなのだ。',
'この考え方は、あとで出てくるmatchにも、そのままつながるのだ。',
'型がそろった枝から一つの結果を作る、と捉えると複雑な分岐も整理しやすいのだ。'],points=['5 > 3 は true','選ばれる式：5 * 2','if全体の値がanswerになる'],expression='happy',pose='wave')
add('03 関数と制御構文','繰り返しと範囲',[
'配列などの要素を順番に取り出すには、forとinを使うのだ。',
'この範囲は、零以上四未満なのだ。取り出す値は、零、一、二、三になるのだ。',
'合計すると六になるのだ。終点を含むかどうかを、記号で確認してほしいのだ。',
'条件が成立する間だけ繰り返すwhileや、途中で抜けるbreakも使えるのだ。'],code='fn main {\n  let mut total = 0\n  for n in 0..<4 {\n    total = total + n\n  }\n  println(total) // 6\n}')
add('04 コレクション','Arrayと名前の変更は別',[
'配列のArrayは、同じ型の要素をまとめて扱うのだ。',
'この例ではletで名前を作っているけれど、配列の要素は変更できるのだ。',
'零番目を九にして、最後に四を追加するのだ。配列の長さは四になるのだ。',
'letが禁止するのは名前への再代入なのだ。配列や可変フィールドの変更とは区別するのだ。'],code='fn main {\n  let values : Array[Int] = [1, 2, 3]\n  values[0] = 9\n  values.push(4)\n  println(values[0]) // 9\n  println(values.length()) // 4\n}')
add('04 コレクション','関数を渡して変換する',[
'関数は、別の関数へ引数として渡すこともできるのだ。',
'mapに、受け取った数を二倍する小さな関数を渡してみるのだ。',
'四、五、六から、八、十、十二という新しい配列ができるのだ。元の配列を書き換える処理ではないのだ。',
'矢印で書く短い関数の構文なのだ。繰り返しの細部より、要素をどう変えるかに集中できるのだ。'],code='fn main {\n  let source = [4, 5, 6]\n  let doubled = source.map(x => x * 2)\n  println(doubled[1]) // 10\n  println(source[1]) // 5\n}')
add('05 データを設計する','structで関連する値をまとめる',[
'構造体のstructは、関連する情報を名前付きのフィールドにまとめるのだ。',
'この例のCardは、名前とポイントを持っているのだ。',
'型名を付けた構造体リテラルで値を作り、ドットに続けてフィールド名を書くと取り出せるのだ。',
'同じ整数でも何の数字か分かるように、データの意味を構造で示せるのだ。'],code='struct Card {\n  name : String\n  points : Int\n}\nfn main {\n  let card = Card::{ name: "zunda", points: 12 }\n  println(card.points) // 12\n}')
add('05 データを設計する','変更できるフィールドを指定',[
'構造体のフィールドは、変更できるものをmutで明示するのだ。',
'このCounterは、valueだけを更新できるように定義しているのだ。',
'名前のcounterは再代入していないけれど、その中の値を一から二へ更新しているのだ。',
'配列と同じで、名前の可変性とデータの可変性を、二つに分けて考えるのだ。'],code='struct Counter {\n  mut value : Int\n}\nfn main {\n  let counter = Counter::{ value: 1 }\n  counter.value = counter.value + 1\n  println(counter.value) // 2\n}')
add('05 データを設計する','enumで状態を選択肢にする',[
'enumは、いくつかの選択肢を持つ型を定義するのだ。',
'待機中、読み込み中、完了という状態を、それぞれ別の選択肢として書けるのだ。',
'完了の状態だけに文字列を持たせることもできるのだ。状態と必要なデータを一緒に表現するのだ。',
'文字列で状態名を管理するよりも、選択肢を型で示せる点が学習のポイントなのだ。'],code='enum LoadState {\n  Idle\n  Loading\n  Ready(String)\n}\nfn main {\n  let state : LoadState = Ready("done")\n  ignore(state)\n}')
add('05 データを設計する','matchで状態を分けて扱う',[
'enumの中身を扱うときに、パターンマッチが役立つのだ。',
'Readyに入っている文字列を、textという名前で取り出して返しているのだ。',
'ほかの二つの状態にも、それぞれ返す文字列を用意しているのだ。',
'matchは選択肢の網羅性も検査するのだ。状態を追加したときの処理漏れを見つける助けになるのだ。'],code='fn message(state : LoadState) -> String {\n  match state {\n    Idle => "waiting"\n    Loading => "loading"\n    Ready(text) => text\n  }\n}\nfn main { println(message(Ready("done"))) }',setup='enum LoadState { Idle; Loading; Ready(String) }')
add('05 データを設計する','Option：値がない場合も型にする',[
'値が存在しない可能性は、Optionで表せるのだ。',
'Someには値が入り、Noneは値がないことを表すのだ。T?はOptionの省略表記なのだ。',
'この例では、見つかった数を返し、見つからなければ零を返すのだ。',
'値があるはずだと決め付ける前に、存在しない側の処理を考えられるのだ。'],code='fn or_zero(value : Int?) -> Int {\n  match value {\n    Some(n) => n\n    None => 0\n  }\n}\nfn main { println(or_zero(None)) }')
add('05 データを設計する','ジェネリクス：型を引数にする',[
'同じ処理を複数の型に使いたいときは、型パラメーターを使うのだ。',
'この関数のTは、呼び出すときに決まる型を表しているのだ。',
'整数を渡せば整数が返り、文字列を渡せば文字列が返るのだ。型の対応は保たれるのだ。',
'何でもできる型という意味ではないのだ。比較などの操作が必要なら、次の章の制約が必要になるのだ。'],code='fn[T] identity(value : T) -> T {\n  value\n}\nfn main {\n  println(identity(21))\n  println(identity("hello"))\n}')
add('06 メソッドとトレイト','メソッドは型に関連付いた関数',[
'メソッドは、型と関連付けた関数として定義できるのだ。',
'Counterという型名に続けて、二つのコロンと関数名を書くのだ。',
'最初の引数で対象の値を受け取り、ドットを使って呼び出せるのだ。',
'クラスの中にすべて書く必要はないのだ。データの定義と、関連する操作を分けて読めるのだ。'],code='fn Counter::next(self : Counter) -> Int {\n  self.value + 1\n}\nfn main {\n  let counter = Counter::{ value: 8 }\n  println(counter.next()) // 9\n}',setup='struct Counter { value : Int }')
add('06 メソッドとトレイト','trait：必要な操作を宣言',[
'トレイトは、その型に何ができてほしいかを宣言する仕組みなのだ。',
'このNamedは、表示用の名前を返す操作を一つ要求しているのだ。',
'Selfは、そのトレイトを実装する型を指すのだ。ここでは特定の型名に固定しないのだ。',
'単に同じ名前の関数があるだけではなく、実装を明示して契約を満たすのだ。'],code='trait Named {\n  title(Self) -> String\n}',check='struct Badge { text : String }\nimpl Named for Badge with title(self) { self.text }\nfn main { println(Named::title(Badge::{ text: "learner" })) }')
add('06 メソッドとトレイト','implで操作の実体を書く',[
'implで、Badgeという型に対するNamedの実装を書いているのだ。',
'今回は中に持つ文字列を、そのまま返しているのだ。',
'呼び出しではトレイト名を明記して、どの操作を使うかを分かりやすくしているのだ。',
'最新版では、トレイトのメソッドをドットで公開するためのextendもあるのだ。暗黙の挙動に頼らないのが安心なのだ。'],code='struct Badge { text : String }\nimpl Named for Badge with title(self) {\n  self.text\n}\nfn main {\n  let badge = Badge::{ text: "learner" }\n  println(Named::title(badge))\n}',setup='trait Named { title(Self) -> String }')
add('06 メソッドとトレイト','制約とderiveを組み合わせる',[
'型パラメーターにEqという制約を付けると、等しいかどうかを比較できるのだ。',
'同じ関数を、整数にも文字列にも使えるのだ。ただし必要な比較を提供する型に限られるのだ。',
'構造体などでは、deriveで対応するトレイトの実装を自動生成できる場合があるのだ。',
'型を一般化するときは、どんな操作が必要かを一緒に明示するのだ。'],code='fn[T : Eq] same(a : T, b : T) -> Bool {\n  a == b\n}\nstruct Pair { x : Int; y : Int } derive(Eq)\nfn main {\n  println(same(3, 3)) // true\n  println(same("a", "b")) // false\n}')
add('07 エラー処理','Result：成功と失敗を値にする',[
'Optionが存在するかどうかを表すのに対し、Resultは成功か失敗かを表せるのだ。',
'Okには成功した結果、Errには失敗の情報を入れるのだ。',
'この例では、負の数なら失敗の文字列を返しているのだ。',
'返ってきた値をmatchで処理できるので、失敗もデータとして保持したい設計に使えるのだ。'],code='fn accept(n : Int) -> Result[Int, String] {\n  if n >= 0 { Ok(n) } else { Err("negative") }\n}\nfn main {\n  match accept(-1) {\n    Ok(n) => println(n)\n    Err(reason) => println(reason)\n  }\n}')
add('07 エラー処理','raise：失敗する可能性を型に書く',[
'MoonBitには、Resultを返す方法に加えて、raiseによるエラー処理もあるのだ。',
'まずsuberrorで、エラーの種類を定義するのだ。',
'関数の戻り値のあとには、起こり得るエラーを宣言しているのだ。負の数なら、そのエラーを送出するのだ。',
'正常な結果の型と、失敗する可能性を、関数の宣言から読み取れるのだ。'],code='suberror Negative\nfn checked(n : Int) -> Int raise Negative {\n  if n < 0 { raise Negative }\n  n\n}',check='fn main {\n  let n = try checked(-2) catch { Negative => 0 }\n  println(n)\n}')
add('07 エラー処理','try / catchで回復する',[
'送出されたエラーは、tryとcatchで受け取れるのだ。',
'この例では、負の値を渡したときにNegativeが発生し、代わりの零を選ぶのだ。',
'いつも零にすればよいわけではないのだ。表示する、再試行する、呼び出し元へ伝えるなど、目的に合わせて設計するのだ。',
'失敗を値として残すResultと、送出して扱うraiseを混同しないことが大切なのだ。'],code='fn main {\n  let value = try checked(-2) catch {\n    Negative => 0\n  }\n  println(value) // 0\n}',setup='suberror Negative\nfn checked(n : Int) -> Int raise Negative {\n  if n < 0 { raise Negative }\n  n\n}')
add('08 テストと設計','テストで理解を確かめる',[
'ここまでの予想を、テストとして残してみるのだ。',
'testブロックの中で、実際の結果と期待する値をassert_eqで比較するのだ。',
'一致しなければテストが失敗するので、仕様の理解や変更の影響を確かめられるのだ。',
'テストはmoon testで実行するのだ。この教材でも、表示例とは別に期待値を検証するテストを用意するのだ。'],code='test "addition and fallback" {\n  assert_eq(add(6, 7), 13)\n  assert_eq(or_zero(None), 0)\n  assert_eq(or_zero(Some(9)), 9)\n}',setup='fn add(a : Int, b : Int) -> Int { a + b }\nfn or_zero(x : Int?) -> Int { match x { Some(n) => n; None => 0 } }',check='fn main { println(add(6, 7)) }')
add('08 テストと設計','コードはパッケージにまとめる',[
'実際のプロジェクトでは、複数のソースファイルをパッケージとして整理するのだ。',
'パッケージ設定はmoon.pkgに書き、モジュール全体の設定とは役割を分けるのだ。',
'ほかのパッケージから使う関数はpubで公開し、利用側ではインポートした別名を使うのだ。',
'型の公開方法には、構築や実装をどこまで許すかの違いがあるので、公開APIを作る段階で詳しく確認するのだ。'],points=['package：ソースとmoon.pkgの単位','module：パッケージを束ねる配布単位','pubとインポートで外部との境界を作る'])
add('08 テストと設計','小問：値なしと失敗をどう分ける？',[
'最後の小問なのだ。検索したけれど見つからなかった場合と、通信そのものに失敗した場合を考えるのだ。',
'この二つを、同じ意味として処理してよいかを考えてほしいのだ。',
'値がないことが通常の結果ならOption、失敗の理由も必要ならResultなどで表現できるのだ。',
'型を選ぶことは、利用者へどんな状況を伝えるかを決めることでもあるのだ。'],points=['見つからない：通常の「値なし」？','通信失敗：理由を伝えたい「失敗」？','状況の違いを型で表現する'],expression='thinking',pose='think',pause=2)
add('09 まとめと学習資料','覚えておきたい四つの視点',[
'今回の要点を整理するのだ。一つ目は、型推論があっても静的に型を検査することなのだ。',
'二つ目は、関数や分岐を、値を作る式として読むことなのだ。',
'三つ目は、struct、enum、Optionなどでデータの意味を表現することなのだ。',
'四つ目は、トレイトとエラーの宣言で、操作の条件や失敗の可能性を伝えることなのだ。'],points=['型と式で、コードの意味を読む','データの状態を型で表す','操作の条件と失敗を明示する'],expression='happy',pose='wave')
add('09 まとめと学習資料','次は自分で値を変えてみる',[
'添付するコード例で、入力の数やenumの選択肢を変えて試してほしいのだ。',
'テストの期待値も変えながら、成功する場合と失敗する場合を比べると理解が深まるのだ。',
'詳しい仕様は、公式ドキュメントの基礎、メソッドとトレイト、エラー処理、テストの各章を参照してほしいのだ。',
'台本、出典、検証記録はリポジトリに残すのだ。ずんだもんと学ぶMoonBit入門は、ここまでなのだ。'],points=['公式：docs.moonbitlang.com','台本・コード例・出典を同梱','音声：VOICEVOX:ずんだもん'],expression='happy',pose='wave')

project={'title':'MoonBit 言語仕様入門','series':'KAISETSU VIDEO STUDIO  /  MOONBIT 0.10.11','speaker':'ずんだもん','style':'ノーマル','speed':1.02,'scenes':scenes}
(ROOT/'lesson.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
transcript=['# MoonBit 言語仕様入門\n','2026-09-06 / 対象コンパイラー: moonc v0.10.11\n']
for i,s in enumerate(scenes,1):
    transcript.append(f'## {i:02d} {s["chapter"]} — {s["heading"]}\n')
    if 'code' in s:transcript.append('```moonbit\n'+s['code']+'\n```\n')
    transcript.extend(x['text']+'\n' for x in s['narration'])
(ROOT/'TRANSCRIPT.md').write_text('\n'.join(transcript),encoding='utf-8')
print(f'{len(scenes)} scenes; {sum(len(x["text"]) for s in scenes for x in s["narration"])} Japanese characters')
