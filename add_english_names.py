#!/usr/bin/env python3
"""Add English translations to character names."""
import json

# English translations for Uma Musume characters
# Based on the official English release
TRANSLATIONS = {
    "スペシャルウィーク": "Special Week",
    "サイレンススズカ": "Silence Suzuka",
    "トウカイテイオー": "Tokai Teio",
    "マルゼンスキー": "Maruz ensky",
    "フジキセキ": "Fujikiseki",
    "オグリキャップ": "Oguri Cap",
    "ゴールドシップ": "Gold Ship",
    "ウオッカ": "Vodka",
    "ダイワスカーレット": "Daiwa Scarlet",
    "タイキシャトル": "Taiki Shuttle",
    "グラスワンダー": "Grass Wonder",
    "ヒシアマゾン": "Hishi Amazon",
    "メジロマックイーン": "Mejiro McQueen",
    "エルコンドルパサー": "El Condor Pasa",
    "テイエムオペラオー": "T.M. Opera O",
    "ナリタブライアン": "Narita Brian",
    "シンボリルドルフ": "Symboli Rudolf",
    "エアグルーヴ": "Air Groove",
    "アグネスデジタル": "Agnes Digital",
    "セイウンスカイ": "Seiun Sky",
    "タマモクロス": "Tamamo Cross",
    "ファインモーション": "Fine Motion",
    "ビワハヤヒデ": "Biwa Hayahide",
    "マチカネタンホイザ": "Matikane Tannhauser",
    "マヤノトップガン": "Mayano Top Gun",
    "マンハッタンカフェ": "Manhattan Cafe",
    "ミホノブルボン": "Mihono Bourbon",
    "メジロライアン": "Mejiro Ryan",
    "ヒシアケボノ": "Hishi Akebono",
    "ユキノビジン": "Yukino Bijin",
    "ライスシャワー": "Rice Shower",
    "アイネスフウジン": "Ines Fujin",
    "アグネスタキオン": "Agnes Tachyon",
    "アドマイヤベガ": "Admire Vega",
    "イナリワン": "Inari One",
    "ウイニングチケット": "Winning Ticket",
    "エアシャカール": "Air Shakur",
    "エイシンフラッシュ": "Eishin Flash",
    "カレンチャン": "Kare Chan",
    "カワカミプリンセス": "Kawakami Princess",
    "ゴールドシチー": "Gold City",
    "サクラバクシンオー": "Sakura Bakushin O",
    "シンコウウインディ": "Shinko Windy",
    "スイープトウショウ": "Sweep Tosho",
    "スーパークリーク": "Super Creek",
    "スマートファルコン": "Smart Falcon",
    "ゼンノロブロイ": "Zenno Rob Roy",
    "トーセンジョーダン": "Tosen Jordan",
    "ナリタタイシン": "Narita Taishin",
    "ナカヤマフェスタ": "Nakayama Festa",
    "ハッピーミーク": "Happy Meek",
    "バンブーメモリー": "Bamboo Memory",
    "ハルウララ": "Haru Urara",
    "ハクノイエロ": "Hakuno D'Or",
    "ビコーペガサス": "Biko Pegasus",
    "マーベラスサンデー": "Marvelous Sunday",
    "メジロパーマー": "Mejiro Palmer",
    "メジロドーベル": "Mejiro Dober",
    "ヤマニンゼファー": "Yamanin Zephyr",
    "ヤエノムテキ": "Yaeno Muteki",
    "ライクリー": "Like Lily",
    "ワン ダーアキュート": "Wonder Acute",
    "ニシノフラワー": "Nishino Flower",
    "ツインターボ": "Twin Turbo",
    "ツルマルツヨシ": "Tsurumaru Tsuyoshi",
    "ナイスネイチャ": "Nice Nature",
    "キングヘイロー": "King Halo",
    "マチカネフクキタル": "Matikane Fukukitaru",
    "サイレンススズカ": "Silence Suzuka",
    "ミスターシービー": "Mr. C.B.",
    "アストンマーチャン": "Aston Machan",
    "メジロブライト": "Mejiro Bright",
    "メジロアルダン": "Mejiro Ardan",
    "オグリキャップ": "Oguri Cap",
    "エイシンフラッシュ": "Eishin Flash",
    "サクラチヨノオー": "Sakura Chiyono O",
    "イクノディクタス": "Ikuno Dictus",
    "ゴッドアフェクシオン": "God Affection",
    "レベッカ": "Rebecca",
    "ドゥラメンテ": "Duramente",
    "キタサンブラック": "Kitasan Black",
    "サトノダイヤモンド": "Satono Diamond",
    "シリウスシンボリ": "Sirius Symboli",
    "ナリタトップロード": "Narita Top Road",
    "メジロラモーヌ": "Mejiro Ramonu",
    "トウカイテイオー": "Tokai Teio",
    "ツインターボ": "Twin Turbo",
    "アストンマーチャン": "Aston Machan",
    "ケイエスミラクル": "K.S. Miracle",
}

# Load characters
with open('./data/characters.json', 'r', encoding='utf-8') as f:
    characters = json.load(f)

# Add English translations
translated_count = 0
for char in characters:
    name_jp = char['name_jp']
    if name_jp in TRANSLATIONS:
        char['name_en'] = TRANSLATIONS[name_jp]
        translated_count += 1

# Save updated data
with open('./data/characters.json', 'w', encoding='utf-8') as f:
    json.dump(characters, f, indent=2, ensure_ascii=False)

print(f"✅ Added English names for {translated_count}/{len(characters)} characters")
print(f"❓ {len(characters) - translated_count} characters still need translation")

# Show untranslated
untranslated = [c for c in characters if not c['name_en']]
if untranslated:
    print("\nUntranslated characters:")
    for char in untranslated[:10]:
        print(f"  - {char['name_jp']}")
    if len(untranslated) > 10:
        print(f"  ... and {len(untranslated) - 10} more")
