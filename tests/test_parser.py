import unittest

from bangumi.parser import Parser
from bangumi.entitiy import Episode


class TestRawParser(unittest.TestCase):

    def test_raw_parser(self):

        content = "【幻樱字幕组】【4月新番】【古见同学有交流障碍症 第二季 Komi-san wa, Komyushou Desu. S02】【22】【GB_MP4】【1920X1080】"
        info = Parser.parse_bangumi_name(content)

        self.assertEqual(info.title, "Komi-san wa, Komyushou Desu.")
        self.assertEqual(info.dpi, "1920X1080")
        self.assertEqual(info.ep_info.number, 22)
        self.assertEqual(info.season_info.number, 2)

        content = "[织梦字幕组] SPY×FAMILY S1.5 第10集【GB_MP4】【1920X1080】"
        info = Parser.parse_bangumi_name(content)

        self.assertEqual(info.title, "SPY×FAMILY")
        self.assertEqual(info.ep_info.number, 10)
        self.assertEqual(info.season_info.number, 1.5)

        content = "[百冬练习组&LoliHouse] BanG Dream! 少女乐团派对！☆PICO FEVER！ / Garupa Pico: Fever! - 26 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕][END] [101.69 MB]"
        info = Parser.parse_bangumi_name(content)

        self.assertEqual(info.group, "百冬练习组&LoliHouse")
        self.assertEqual(info.title, "BanG Dream! 少女乐团派对！☆PICO FEVER！")
        self.assertEqual(info.dpi, "1080p")
        self.assertEqual(info.ep_info.number, 26)
        self.assertEqual(info.season_info.number, 1)

        content = "【喵萌奶茶屋】★04月新番★[夏日重现/Summer Time Rendering][11][1080p][繁日双语][招募翻译] [539.4 MB]"
        info = Parser.parse_bangumi_name(content)
        self.assertEqual(info.group, "喵萌奶茶屋")
        self.assertEqual(info.title, "Summer Time Rendering")
        self.assertEqual(info.dpi, "1080p")
        self.assertEqual(info.ep_info.number, 11)
        self.assertEqual(info.season_info.number, 1)

        content = "【喵萌奶茶屋】★04月新番★夏日重现/Summer Time Rendering[11][1080p][繁日双语][招募翻译] [539.4 MB]"
        info = Parser.parse_bangumi_name(content)
        self.assertEqual(info.title, "Summer Time Rendering")

    def test_pre_process(self):
        content = "【幻樱字幕组】【4月新番】"
        expected_content = "[幻樱字幕组][4月新番]"
        self.assertEqual(Parser.pre_process(content), expected_content)

    def test_get_group(self):
        content = "【幻樱字幕组】【4月新番】【古见同学有交流障碍症 第二季 Komi-san wa, Komyushou Desu. S02】【22】【GB_MP4】【1920X1080】"

        content = Parser.pre_process(content)
        expected_content = "幻樱字幕组"

        self.assertEqual(Parser.get_group(content), expected_content)

    def test_find_tags(self):
        cases = [
            ("[GB_MP4] [1920X1080] [bilibili]", ["GB", "1920X1080", "bilibili"]),
            ("[GB_MP4] [1920X1080]", ["GB", "1920X1080", None]),
            ("[简_MP4] [Bilibili]", ["简", None, "Bilibili"]),
            ("[简_MP4] [Bilibili] [Web]", ["简", None, "Web"]),
            ("dfkajflkdaj dfkadjlkfa [Web]", [None, None, "Web"]),
            ("dfkajflkdaj dfkadjlkfa [Web] [Web]", [None, None, "Web"]),
        ]

        for content, expected in cases:
            ret = Parser.find_tags(content)
            self.assertEqual(len(ret), 3)
            for i in range(3):
                self.assertEqual(ret[i], expected[i])

    def test_episode(self):

        for epi in range(1, 100000, 100):
            content = f"【幻樱字幕组】【4月新番】【古见同学有交流障碍症 第一季 Komi-san wa, Komyushou Desu. S01】【{epi}】【GB_MP4】【4K】"
            info = Parser.parse_bangumi_name(content)
            self.assertEqual(info.ep_info.number, epi)

        for epi in range(1, 100000, 100):
            content = f"[Nekomoe kissaten][Summer Time Rendering - {epi} [1080p][JPTC].mp4"
            info = Parser.parse_bangumi_name(content)
            self.assertEqual(info.ep_info.number, epi)

    def test_season(self):
        chinese_number_arr = [
            "一",
            "二",
            "三",
            "四",
            "五",
            "六",
            "七",
            "八",
            "九",
            "十",
            "十一",
            "十二"]

        for i in range(1, 13):
            season = str(i).zfill(2)
            content = f"【幻樱字幕组】【古见同学有交流障碍症 第{chinese_number_arr[i - 1]}季 Komi-san wa, Komyushou Desu. S{season}】[1]"
            info = Parser.parse_bangumi_name(content)
            self.assertEqual(info.season_info.number, i)

    def test_formatted_title(self):
        cases = [
            ("【幻樱字幕组】【4月新番】【古见同学有交流障碍症 第二季 Komi-san wa, Komyushou Desu. S02】【22】【GB_MP4】【1920X1080】",
             "Komi-san wa, Komyushou Desu. S02E22"),
            ("[百冬练习组&LoliHouse] BanG Dream! 少女乐团派对！☆PICO FEVER！ / Garupa Pico: Fever! - 26 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕][END] [101.69 MB]",
             "BanG Dream! 少女乐团派对！☆PICO FEVER！ S01E26"),
            ("【喵萌奶茶屋】★04月新番★[夏日重现/Summer Time Rendering][11][1080p][繁日双语][招募翻译] [539.4 MB]",
             "Summer Time Rendering S01E11"),
            ("【喵萌奶茶屋】★04月新番★[夏日重现/Summer Time Rendering][01][1080p][繁日双语][招募翻译] [539.4 MB]",
             "Summer Time Rendering S01E01"),
            ("【喵萌奶茶屋】★04月新番★[夏日重现/Summer Time Rendering][29][1080p][繁日双语][招募翻译] [539.4 MB]",
             "Summer Time Rendering S01E29"),
            ("【幻樱字幕组】【4月新番】【古见同学有交流障碍症 第一季 Komi-san wa, Komyushou Desu. S01】【31】【GB_MP4】【1920X1080】",
             "Komi-san wa, Komyushou Desu. S01E31"),
        ]

        for raw, expected in cases:
            info = Parser.parse_bangumi_name(raw)
            self.assertEqual(info.formatted, expected)

    def test_large_data_set(self):
        data = [
            ("[Lilith-Raws] 勇者鬥惡龍 達伊的大冒險 / Dragon Quest - Dai no Daibouken (2020) - 84 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Dragon Quest - Dai no Daibouken (2020)", "Lilith-Raws", 84, 1),
            ("[NC-Raws] 勇者鬥惡龍 達伊的大冒險 / Dragon Quest - Dai no Daibouken - 84 (Baha 1920x1080 AVC AAC MP4)", "Dragon Quest - Dai no Daibouken", "NC-Raws", 84, 1),
            ("[ANi]  勇者鬥惡龍 達伊的大冒險 - 84 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "勇者鬥惡龍 達伊的大冒險", "ANi", 84, 1),
            ("[Lilith-Raws] 冰冰冰 冰淇淋君 / iii Icecrin S02 - 01 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "iii Icecrin", "Lilith-Raws", 1, 2),
            ("[Lilith-Raws] 神渣☆偶像 / Kami Kuzu☆Idol - 01 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Kami Kuzu☆Idol", "Lilith-Raws", 1, 1),
            ("[Lilith-Raws] 出租女友 / Kanojo, Okarishimasu S02 - 01 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Kanojo, Okarishimasu", "Lilith-Raws", 1, 2),
            ("[NC-Raws] 冰冰冰 冰淇淋君 第二季 / Iii Icecrin S2 - 01 (Baha 1920x1080 AVC AAC MP4)", "Iii Icecrin", "NC-Raws", 1, 2),
            ("[ANi]  神渣☆偶像 - 01 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "神渣☆偶像", "ANi", 1, 1),
            ("[ANi] RentaGirlfriend S2 -  出租女友 第二季 - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "RentaGirlfriend", "ANi", 13, 2),
            ("[Lilith-Raws] 杜鵑小鬧劇 / Kakkou no Iikagen - 10 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Kakkou no Iikagen", "Lilith-Raws", 10, 1),
            ("[熔岩动画Sub&MingY] 街角魔族 2丁目 / Machikado Mazoku S2 [12][1080p][简日内嵌]", "Machikado Mazoku", "熔岩动画Sub&MingY", 12, 2),
            ("[c.c動漫][4月新番][盾之勇者成名錄 第二季][13][BIG5][1080P][MP4][END]", "盾之勇者成名錄", "c.c動漫", 13, 2),
            ("[ANi]  杜鵑婚約 [特別篇] - 10 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "杜鵑婚約", "ANi", 10, 1),
            ("【喵萌奶茶屋】★04月新番★[相合之物/Deaimon][12][1080p][简体][招募翻译校对]", "Deaimon", "喵萌奶茶屋", 12, 1),
            ("[NC-Raws] 杜鵑婚約 [特別篇] / Kakkou no Iinazuke (A Couple of Cuckoos) - 10 (Baha 1920x1080 AVC AAC MP4)", "Kakkou no Iinazuke (A Couple of Cuckoos)", "NC-Raws", 10, 1),
            ("【幻櫻字幕組】【4月新番】【間諜過家家 / 間諜家家酒 SPY×FAMILY】【12】【END】【BIG5_MP4】【1280X720】", "間諜家家酒 SPY×FAMILY", "幻櫻字幕組", 12, 1),
            ("【幻樱字幕组】【4月新番】【间谍过家家 / 间谍家家酒 SPY×FAMILY】【12】【END】【GB_MP4】【1280X720】", "间谍家家酒 SPY×FAMILY", "幻樱字幕组", 12, 1),
            ("[GM-Team][国漫][完美世界][Perfect World][2021][65][AVC][GB][1080P]", "Perfect World", "GM-Team", 65, 1),
            ("[NC-Raws] 你真是个天才 / You're A Genius! - 21 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "You're A Genius!", "NC-Raws", 21, 1),
            ("【極影字幕社】★ CUE! 第24集 BIG5 AVC 720p MP4 (完)", "CUE!", "極影字幕社", 24, 1),
            ("[ANi] Onipan -  Onipan！（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "Onipan", "ANi", 12, 1),
            ("[NC-Raws] ONIPAN! - 12 (B-Global 1920x1080 HEVC AAC MKV)", "ONIPAN!", "NC-Raws", 12, 1),
            ("【喵萌奶茶屋】★04月新番★[夏日重現/Summer Time Rendering][12][1080p][繁日雙語][招募翻譯片源]", "Summer Time Rendering", "喵萌奶茶屋", 12, 1),
            ("[ANi] The Dawn of the Witch -  魔法使黎明期 - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "The Dawn of the Witch", "ANi", 12, 1),
            ("[ANi] Im Kodama Kawashiri -  川尻小玉的懶散生活 - 22 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Im Kodama Kawashiri", "ANi", 22, 1),
            ("[Lilith-Raws] 川尻小玉的懶散生活 / Atasha Kawajiri Kodama Da yo - 22 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Atasha Kawajiri Kodama Da yo", "Lilith-Raws", 22, 1),
            ("[Lilith-Raws] 魔法使黎明期 / Mahoutsukai Reimeiki - 12 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Mahoutsukai Reimeiki", "Lilith-Raws", 12, 1),
            ("[Lilith-Raws] 叫我對大哥 WEB版 / Ore, Tsushima Web ver. - 93 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Ore, Tsushima Web ver.", "Lilith-Raws", 93, 1),
            ("[千夏字幕组&LoliHouse] 约会大作战 IV / Date A Live IV - 08 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]", "Date A Live IV", "千夏字幕组&LoliHouse", 8, 1),
            ("[千夏字幕组&LoliHouse] 测不准的阿波连同学 / 不会拿捏距离的阿波连同学 / Aharen-san wa Hakarenai - 12 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕][End]", "Aharen-san wa Hakarenai", "千夏字幕组&LoliHouse", 12, 1),
            ("[GM-Team][国漫][凡人修仙传 再别天南][Fan Ren Xiu Xian Zhuan][2022][10][AVC][GB][1080P]", "Fan Ren Xiu Xian Zhuan", "GM-Team", 10, 1),
            ("[GM-Team][国漫][武动乾坤 第3季][Martial Universe 3rd Season][2022][2022][10][AVC][GB][1080P]", "Martial Universe 3rd Season", "GM-Team", 10, 3),
            ("[GM-Team][国漫][吞噬星空][Swallowed Star][2021][42][AVC][GB][1080P]", "Swallowed Star", "GM-Team", 42, 1),
            ("[GM-Team][国漫][斗罗大陆][Dou Luo Da Lu][Douro Mainland][2019][214][AVC][GB][1080P]", "Douro Mainland", "GM-Team", 214, 1),
            ("[NC-Raws] 最后的召唤师 / The Last Summoner - 11 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "The Last Summoner", "NC-Raws", 11, 1),
            ("[動漫萌][4月新番][間諜過家家/間諜家家酒/Spy X Family ][BIG5][10][1080P](字幕組招募內詳)", "Spy X Family", "動漫萌", 10, 1),
            ("[爱恋&漫猫字幕组][4月新番][间谍过家家][SPY × FAMILY][12][1080p][MP4][简中]", "SPY × FAMILY", "爱恋&漫猫字幕组", 12, 1),
            ("【千夏字幕組】【約會大作戰IV_Date A Live IV​】[第08話][1080p_AVC][繁體] ​", "Date A Live IV​", "千夏字幕組", 8, 1),
            ("[天月搬運組] 小鳥之翼 / Birdie Wing - Golf Girls Story - 13 [1080P][簡繁日外掛]", "Birdie Wing - Golf Girls Story", "天月搬運組", 13, 1),
            ("[天月搬運組] 盾之勇者成名錄 第二季 / Tate no Yuusha no Nariagari S02 - 13 [1080P][簡繁日外掛]", "Tate no Yuusha no Nariagari", "天月搬運組", 13, 2),
            ("[ANi] The Rising of the Shield Hero S2 -  盾之勇者成名錄 第二季 - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "The Rising of the Shield Hero", "ANi", 13, 2),
            ("[NC-Raws] 星际一游 / Interstellar Wanderer - 12 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "Interstellar Wanderer", "NC-Raws", 12, 1),
            ("[LoliHouse] 键等 / Kaginado - 24 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕][Fin]", "Kaginado", "LoliHouse", 24, 1),
            ("[悠哈璃羽字幕社] [式守同學不只是可愛而已/Kawaii dake ja Nai Shikimori-san] [09] [x264 1080p] [CHT]", "Kawaii dake ja Nai Shikimori-san", "悠哈璃羽字幕社", 9, 1),
            ("[酷漫404][輝夜姬想讓人告白 一超級浪漫一][11][1080P][WebRip][繁日雙語][AVC AAC][MP4][字幕組招人內詳]", "輝夜姬想讓人告白 一超級浪漫一", "酷漫404", 11, 1),
            ("[酷漫404][辉夜大小姐想让我告白 一终极浪漫一][11][1080P][WebRip][简日双语][AVC AAC][MP4][字幕组招人内详]", "辉夜大小姐想让我告白 一终极浪漫一", "酷漫404", 11, 1),
            ("[雪飄工作室][アイカツプラネット！ミララボ/Aikatsu_Planet!-Mirror_Labo/偶像活動星球！镜中练功房][S2E18（总第30集）][繁](檢索:偶活/愛活)", "Aikatsu_Planet!-Mirror_Labo", "雪飄工作室", 30, 2),
            ("[天月搬運組] 薔薇王的葬列 / Baraou no Souretsu - 24 [1080P][簡繁日外掛]", "Baraou no Souretsu", "天月搬運組", 24, 1),
            ("【極影字幕社】 ★4月新番 【SPY×FAMILY 間諜家家酒】【SPY×FAMILY】【09】BIG5 MP4_720P", "SPY×FAMILY 間諜家家酒", "極影字幕社", 9, 1),
            ("【极影字幕社】 ★4月新番 【间谍过家家】【SPY×FAMILY】【09】GB MP4_720P", "SPY×FAMILY", "极影字幕社", 9, 1),
            ("【悠哈璃羽字幕社】 [處刑少女的生存之道__Shokei-Shoujo-no-Virgin-Road] [12] [x264 1080p][CHT]", "Shokei-Shoujo-no-Virgin-Road", "悠哈璃羽字幕社", 12, 1),
            ("[ANi] Birdie Wing Golf Girls Story -  小鳥之翼 - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Birdie Wing Golf Girls Story", "ANi", 13, 1),
            ("[NC-Raws] 小鸟之翼 高尔夫少女 / Birdie Wing: Golf Girls' Story - 13 (B-Global 1920x1080 HEVC AAC MKV)", "Birdie Wing Golf Girls' Story", "NC-Raws", 13, 1),
            ("[爱恋&漫猫字幕组][4月新番][社畜小姐想被幼女幽灵治愈][Ms. Corporate Slave Wants to be Healed by a Loli Spirit, Shachisaretai][12][1080p][MP4][简中]", "Ms. Corporate Slave Wants to be Healed by a Loli Spirit, Shachisaretai", "爱恋&漫猫字幕组", 12, 1),
            ("【喵萌奶茶屋】★04月新番★[处刑少女的生存之道/処刑少女の生きる道/Shokei Shoujo no Virgin Road][10][WebRip 1080p HEVC-10bit AAC][简繁内封][招募翻译校对]", "Shokei Shoujo no Virgin Road", "喵萌奶茶屋", 10, 1),
            ("[桜都字幕組] 間諜家家酒 / Spy x Family [12v2][1080p][繁體內嵌]", "Spy x Family", "桜都字幕組", 12, 1),
            ("[ANi] KAGINADO S2 -  鍵等 第二季 - 24 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "KAGINADO", "ANi", 24, 2),
            ("[离谱Sub] 朋友遊戲 / トモダチゲーム / Tomodachi Game [12][AVC AAC][1080p][繁體內嵌]", "Tomodachi Game", "离谱Sub", 12, 1),
            ("[喵萌奶茶屋&LoliHouse] 杜鹃的婚约 / Kakkou no Iinazuke - 10 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]", "Kakkou no Iinazuke", "喵萌奶茶屋&LoliHouse", 10, 1),
            ("[NC-Raws] 不白吃话山海经 / Foodie Boy’s Classic of Mountains & Seas - 38 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "Foodie Boy’s Classic of Mountains & Seas", "NC-Raws", 38, 1),
            ("[NC-Raws] 凡人修仙传 / A Record Of Mortal's Journey To Immortality - 56 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "A Record Of Mortal's Journey To Immortality", "NC-Raws", 56, 1),
            ("[动漫国字幕组&LoliHouse] 夏日时光 / 夏日重现 / Summer Time Render - 10 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]", "Summer Time Render", "动漫国字幕组&LoliHouse", 10, 1),
            ("[丸子家族][樱桃小丸子第一期(Chibi Maruko-chan I)][060]令人向往的班级停课[数码画质版][简日内嵌][BDRip][1080P][MP4]", "樱桃小丸子(Chibi Maruko-chan I)", "丸子家族", 60, 1),
            ("[爱恋&漫猫字幕组][2006年4月] NANA/ナナ - 05 [1080p][BDRip yuv420p10le HEVC AAC][简日内封]", "NANA", "爱恋&漫猫字幕组", 5, 1),
            ("[动漫萌][4月新番][Spy  X Family ][BIG5][06][1080P](字幕组招募内详)", "X Family", "动漫萌", 6, 1),
            ("[Lilith-Raws] 境界戰機 / Kyoukai Senki S02 - 12 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Kyoukai Senki", "Lilith-Raws", 12, 2),
            ("[ANi] AMAIM Warrior at the Borderline S2 -  境界戰機 第二部 - 25 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "AMAIM Warrior at the Borderline", "ANi", 25, 2),
            ("【动漫国字幕组】★04月新番[SPY×FAMILY间谍家家酒 / 间谍过家家][11][1080P][简体][MP4]", "SPY×FAMILY间谍家家酒", "动漫国字幕组", 11, 1),
            ("【動漫國字幕組】★04月新番[SPY×FAMILY間諜家家酒 / 間諜過家家][11][1080P][繁體][MP4]", "SPY×FAMILY間諜家家酒", "動漫國字幕組", 11, 1),
            ("【动漫国字幕组】★04月新番[夏日时光 / 夏日重现][10][1080P][简体][MP4]", "夏日时光", "动漫国字幕组", 10, 1),
            ("【動漫國字幕組】★04月新番[夏日時光 / 夏日重現][10][1080P][繁體][MP4]", "夏日時光", "動漫國字幕組", 10, 1),
            ("[桜都字幕组] 社畜小姐想被幽灵幼女治愈。 / Shachiku-san wa Youjo Yuurei ni Iyasaretai. [12][1080p][简繁内封]", "Shachiku-san wa Youjo Yuurei ni Iyasaretai.", "桜都字幕组", 12, 1),
            ("【幻樱字幕组】【1月新番】【蔷薇王的葬礼/蔷薇王的葬列 Bara Ou no Souretsu】【22_V2】【BIG5_MP4】【1280X720】", "蔷薇王的葬列 Bara Ou no Souretsu", "幻樱字幕组", 22, 1),
            ("【幻樱字幕组】【4月新番】【社畜小姐想被幽灵幼女治愈。 Shachiku-san wa Youjo Yuurei ni Iyasaretai】【12】【GB_MP4】【1280X720】", "Shachiku-san wa Youjo Yuurei ni Iyasaretai", "幻樱字幕组", 12, 1),
            ("[NC-Raws] 暂停！让我查攻略 / Let Me Check the Walkthrough First - 07 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "Let Me Check the Walkthrough First", "NC-Raws", 7, 1),
            ("[NC-Raws] 小魔头暴露啦 / BUSTED! DARKLORD - 25 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "BUSTED! DARKLORD", "NC-Raws", 25, 1),
            ("[桜都字幕組] 式守同學不止可愛而已 / Kawaii Dake ja Nai Shikimori-san [10][1080p][繁體內嵌]", "Kawaii Dake ja Nai Shikimori-san", "桜都字幕組", 10, 1),
            ("[丸子家族][櫻桃小丸子第二期(Chibi Maruko-chan II)][1342]令人向往的熱褲&友藏不捨得得扔東西[2022.06.26][BIG5][1080P][MP4]", "櫻桃小丸子(Chibi Maruko-chan II)", "丸子家族", 1342, 2),
            ("[丸子家族][樱桃小丸子第二期(Chibi Maruko-chan II)][1342]令人向往的热裤&友藏不舍得扔东西[2022.06.26][GB][1080P][MP4]", "樱桃小丸子(Chibi Maruko-chan II)", "丸子家族", 1342, 2),
            ("【千夏字幕組】【測不準的阿波連同學 / 不會拿捏距離的阿波連同學_Aharen-san wa Hakarenai】[第12話][1080p_AVC][繁體][完]", "不會拿捏距離的阿波連同學_Aharen-san wa Hakarenai", "千夏字幕組", 12, 1),
            ("【千夏字幕组】【测不准的阿波连同学 / 不会拿捏距离的阿波连同学_Aharen-san wa Hakarenai】[第12话][1080p_AVC][简体][完]", "不会拿捏距离的阿波连同学_Aharen-san wa Hakarenai", "千夏字幕组", 12, 1),
            ("【悠哈璃羽字幕社】[青之蘆葦_Ao Ashi][12][x264 1080p][CHT]", "Ao Ashi", "悠哈璃羽字幕社", 12, 1),
            ("[桜都字幕组] 街角魔族 2丁目 / Machikado Mazoku: 2-choume  [11][1080P][简繁内封]", "Machikado Mazoku 2-choume", "桜都字幕组", 11, 1),
            ("[Skymoon-Raws] 這個僧侶有夠煩 / Kono Healer Mendokusai - 12 [ViuTV][WEB-DL][1080p][AVC AAC][繁體外掛][MP4+ASS](正式版本)", "Kono Healer Mendokusai", "Skymoon-Raws", 12, 1),
            ("[LoliHouse] 这个医师超麻烦 / 這個僧侶有夠煩 / Kono Healer, Mendokusai - 12 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕][End]", "Kono Healer, Mendokusai", "LoliHouse", 12, 1),
            ("[风车字幕组][名侦探柯南][1046][天谴降临生日派对（后篇）][1080P][简体][MP4]", "名侦探柯南", "风车字幕组", 1046, 1),
            ("[風車字幕組][名偵探柯南][1046][天譴降臨生日派對（後篇）][1080P][繁體][MP4]", "名偵探柯南", "風車字幕組", 1046, 1),
            ("[LoliHouse] 恋爱要在世界征服后 / Koi wa Sekai Seifuku no Ato de - 12 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕][End]", "Koi wa Sekai Seifuku no Ato de", "LoliHouse", 12, 1),
            ("[云光字幕组]辉夜大小姐想让我告白 -超级浪漫- Kaguya-sama wa Kokurasetai S3 [11][简体双语][1080p]招募后期", "辉夜大小姐想让我告白 -超级浪漫- Kaguya-sama wa Kokurasetai", "云光字幕组", 11, 3),
            ("[ANi] Requiem of the Rose King -  薔薇王的葬列 - 24 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Requiem of the Rose King", "ANi", 24, 1),
            ("[ANi] Dont Hurt Me My Healer -  這個僧侶有夠煩 - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Dont Hurt Me My Healer", "ANi", 12, 1),
            ("[NC-Raws] 时空之隙 / Rift - 12 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "Rift", "NC-Raws", 12, 1),
            ("[雪飘工作室][Delicious Party Precure/デリシャスパーティ プリキュア][WEBDL][1080p][16][简繁外挂](检索:光之美少女/Q娃) 偶活网番已交稿明后恢复", "Delicious Party Precure", "雪飘工作室", 16, 1),
            ("[雪飘工作室][ワッチャプリマジ！/Whatcha _Pri-maji!/哇恰美妙魔法！][36][简](检索:/美妙旋律/美妙天堂/美妙频道) 偶活网番已交稿明后恢复", "Whatcha _Pri-maji!", "雪飘工作室", 36, 1),
            ("[NC-Raws] 博人传之火影忍者次世代 / Boruto: Naruto Next Generations - 255 (B-Global 1920x1080 HEVC AAC MKV)", "Boruto Naruto Next Generations", "NC-Raws", 255, 1),
            ("[悠哈璃羽字幕社] [國王排名_Ousama Ranking] [23] [x264 1080p] [CHT]", "Ousama Ranking", "悠哈璃羽字幕社", 23, 1),
            ("[虹咲学园烤肉同好会][Love Live! 虹咲学园学园偶像同好会 第二季][13END][简日内嵌][特效歌词][WebRip][1080p][AVC AAC MP4]", "Love Live! 虹咲学园学园偶像同好会", "虹咲学园烤肉同好会", 13, 2),
            ("[桜都字幕组] 盾之勇者成名录 Season2 / Tate no Yuusha no Nariagari Season2 [12][1080P][简繁内封]", "Tate no Yuusha no Nariagari Season2", "桜都字幕组", 12, 1),
            ("【馴獸師聯盟】數碼寶貝/數碼暴龍/數碼獸幽靈遊戲[Digimon Ghost Game][31][1080p][繁日字幕]", "數碼獸幽靈遊戲 Digimon Ghost Game", "馴獸師聯盟", 31, 1),
            ("【驯兽师联盟】数码宝贝/数码暴龙/数码兽幽灵游戏[Digimon Ghost Game][31][1080p][简日字幕]", "数码兽幽灵游戏 Digimon Ghost Game", "驯兽师联盟", 31, 1),
            ("【喵萌奶茶屋】★04月新番★[间谍过家家/间谍家家酒/SPYxFAMILY][11][1080p][简日双语][招募翻译]", "SPYxFAMILY", "喵萌奶茶屋", 11, 1),
            ("[豌豆字幕组&LoliHouse] 王者天下 第四季 / Kingdom S4 - 12 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]", "Kingdom", "豌豆字幕组&LoliHouse", 12, 4),
            ("[MingY] 鬼裤衩 / Onipan! [11][1080p][简体内嵌]", "Onipan!", "MingY", 11, 1),
            ("【百冬練習組】【身為女主角 ～被討厭的女主角和秘密的工作～_Heroine Tarumono!】[12END][1080p AVC AAC][繁體]", "Heroine Tarumono!", "百冬練習組", 12, 1),
            ("[夜莺家族&YYQ字幕组]New Doraemon 哆啦A梦新番[712][2022.06.25][AVC][1080P][GB_JP]", "夜莺家族&YYQ字幕组 New Doraemon 哆啦A梦新番", "夜莺家族&YYQ字幕组", 712, 1),
            ("[LoliHouse] Love Live! 虹咲学园学园偶像同好会 第二季 / Love Live! Nijigasaki S2 - 13 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕][Fin]", "Love Live! Nijigasaki", "LoliHouse", 13, 2),
            ("【喵萌奶茶屋】★07月新番★[異世界舅舅/Isekai Ojisan][01][先行版][720p][繁體][招募翻譯]", "Isekai Ojisan", "喵萌奶茶屋", 1, 1),
            ("[天月搬運組] Love All Play - 13 [1080P][簡繁日外掛]", "Love All Play", "天月搬運組", 13, 1),
            ("【豌豆字幕组】[王者天下 第四季 / Kingdom_S4][12][简体][1080P][MP4]", "Kingdom_", "豌豆字幕组", 12, 4),
            ("[轻之国度字幕组][街角魔族 2丁目][11][720P][MP4]", "街角魔族 2丁目", "轻之国度字幕组", 11, 1),
            ("[Lilith-Raws] 女忍者椿的心事 / Kunoichi Tsubaki no Mune no Uchi - 12 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Kunoichi Tsubaki no Mune no Uchi", "Lilith-Raws", 12, 1),
            ("[Lilith-Raws] Build Divide - Code White - 12 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Build Divide", "Lilith-Raws", 12, 1),
            ("[Lilith-Raws] 群青的開幕曲 / Gunjou no Fanfare - 13 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Gunjou no Fanfare", "Lilith-Raws", 13, 1),
            ("[ANi] Shikimoris Not Just a Cutie -  式守同學不只可愛而已 - 10 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Shikimoris Not Just a Cutie", "ANi", 10, 1),
            ("[轻之国度字幕组][盾之勇者成名录 SEASON2][12][720P][MP4]", "SEASON2", "轻之国度字幕组", 12, 1),
            ("[NC-Raws] BUILD-DIVIDE -#FFFFFF- CODE WHITE - 12 (B-Global 1920x1080 HEVC AAC MKV)", "BUILD-DIVIDE -#FFFFFF- CODE WHITE", "NC-Raws", 12, 1),
            ("[ANi] A Couple of Cuckoos -  杜鵑婚約 - 10 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "A Couple of Cuckoos", "ANi", 10, 1),
            ("[ANi] In the Heart of Kunoichi Tsubaki -  女忍者椿的心事 - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "In the Heart of Kunoichi Tsubaki", "ANi", 12, 1),
            ("[ANi] Fanfare of Adolescence -  群青的開幕曲 - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Fanfare of Adolescence", "ANi", 13, 1),
            ("[ANi]  Love Live！虹咲學園 學園偶像同好會 第二季 - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Love Live！虹咲學園 學園偶像同好會", "ANi", 13, 2),
            ("[c.c動漫][4月新番][街角的魔族女孩 第二季][11][BIG5][1080P][MP4]", "街角的魔族女孩", "c.c動漫", 11, 2),
            ("[NC-Raws] Love Live！虹咲学园学园偶像同好会 第二季 / Nijigasaki S2 - 13 (B-Global 1920x1080 HEVC AAC MKV)", "Nijigasaki", "NC-Raws", 13, 2),
            ("[NC-Raws] 君有云 / Word of Honor - 11 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "Word of Honor", "NC-Raws", 11, 1),
            ("[NC-Raws] 谎颜 / Face on Lie - 12 (B-Global Donghua 1920x1080 HEVC AAC MKV)", "Face on Lie", "NC-Raws", 12, 1),
            ("[NC-Raws] 名侦探柯南 / Detective Conan - 1105 (B-Global 1920x1080 HEVC AAC MKV)", "Detective Conan", "NC-Raws", 1105, 1),
            ("【極影字幕社】LoveLive！ 虹咲學園學園偶像同好會 第2期 第12集 BIG5 AVC 1080p", "LoveLive！ 虹咲學園學園偶像同好會", "極影字幕社", 12, 2),
            ("[梦蓝字幕组]Crayonshinchan 蜡笔小新[1136][2022.06.18][AVC][1080P][GB_JP]V2", "Crayonshinchan 蜡笔小新", "梦蓝字幕组", 1136, 1),
            ("[梦蓝字幕组]New Doraemon 哆啦A梦新番[711][2022.06.18][AVC][1080P][GB_JP]", "New Doraemon", "梦蓝字幕组", 711, 1),
            ("[ANi]  街角的魔族女孩 第二季（僅限港澳台地區） - 11 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "街角的魔族女孩 （僅限港澳台地區）", "ANi", 11, 2),
            ("【喵萌Production】★04月新番★[歌愈少女/Healer Girl][12][1080p][简日双语][招募翻译]", "Healer Girl", "喵萌Production", 12, 1),
            ("[Skymoon-Raws] 輝夜姬想讓人告白 一超級浪漫一 / Kaguya-sama wa Kokurasetai S03 - 13 [ViuTV][WEB-DL][1080p][AVC AAC][繁體外掛][MP4+ASS](正式版本)", "Kaguya-sama wa Kokurasetai", "Skymoon-Raws", 13, 3),
            ("[ANi] CUE -  CUE!（僅限港澳台地區） - 24 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "CUE", "ANi", 24, 1),
            ("[NC-Raws] 辉夜大小姐想让我告白？～天才们的恋爱头脑战～第3季 / Kaguya-sama S3 - 13 (B-Global 1920x1080 HEVC AAC MKV)", "Kaguya-sama", "NC-Raws", 13, 3),
            ("[ANi] Kaguyasama Love is War -  輝夜姬想讓人告白 ー超級浪漫ー - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Kaguyasama Love is War", "ANi", 13, 1),
            ("[冷番补完][明日之丈2剧场版][あしたのジョー２][Ashita no joe 2 Movie][1981][BDRip][1080P]", "Ashita no joe 2 Movie", "冷番补完", 1981, 1),
            ("[LoliHouse] 雀魂 PONG / Jongtama PONG - 11 [WebRip 1080p HEVC-10bit AAC]", "Jongtama PONG", "LoliHouse", 11, 1),
            ("[c.c動漫][4月新番][約會大作戰 第四季][12][BIG5][1080P][MP4][END]", "約會大作戰", "c.c動漫", 12, 4),
            ("[ANi]  約會大作戰 DATE A LIVE 第四季（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "DATE A LIVE", "ANi", 12, 4),
            ("[NC-Raws] 约会大作战 第四季 / Date A Live S4 - 12 (B-Global 1920x1080 HEVC AAC MKV)", "Date A Live", "NC-Raws", 12, 4),
            ("[ANi] Love After World Domination -  愛在征服世界後 - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Love After World Domination", "ANi", 12, 1),
            ("【悠哈璃羽字幕社】[86 -不存在的戰區- / Eighty Six][23][x264 1080p][CHT]", "Eighty Six", "悠哈璃羽字幕社", 23, 1),
            (r"[波洛咖啡厅\PCSUB][相合之物\Deaimon][04][简日\CHS_JP][1080P][MP4_AAC][网盘][招翻译]", r"相合之物 Deaimon", r"波洛咖啡厅\PCSUB", 4, 1),
            ("[酷漫404][間諜家家酒][11][1080P][WebRip][繁日雙語][AVC AAC][MP4][字幕組招人內詳]", "間諜家家酒", "酷漫404", 11, 1),
            ("[酷漫404][间谍过家家][11][1080P][WebRip][简日双语][AVC AAC][MP4][字幕组招人内详]", "间谍过家家", "酷漫404", 11, 1),
            ("[NC-Raws] 假面騎士劇場版 對決！超越新世代 [電影] / Kamen Rider: Beyond Generations - 01 (Baha 1920x1080 AVC AAC MP4)", "Kamen Rider Beyond Generations", "NC-Raws", 1, 1),
            ("[桜都字幕组] RPG不动产 / RPG Fudousan [12][1080P][简繁内封]", "RPG Fudousan", "桜都字幕组", 12, 1),
            ("[c.c動漫][4月新番][成為女主角！~被討厭的女主角和秘密的工作~][12][BIG5][1080P][MP4][END]", "成為女主角！~被討厭的女主角和秘密的工作~", "c.c動漫", 12, 1),
            ("[Lilith-Raws] 骸骨騎士大人異世界冒險中 / Gaikotsu Kishi-sama - 12 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Gaikotsu Kishi-sama", "Lilith-Raws", 12, 1),
            ("[ANi] Skeleton Knight in Another World -  骸骨騎士大人異世界冒險中 - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Skeleton Knight in Another World", "ANi", 12, 1),
            ("[c.c動漫][4月新番][社畜想被幼女幽靈療癒。][12][BIG5][1080P][MP4][END]", "社畜想被幼女幽靈療癒。", "c.c動漫", 12, 1),
            ("[ANi]  成為女主角！~被討厭的女主角和秘密的工作~（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "成為女主角！~被討厭的女主角和秘密的工作~（僅限港澳台地區）", "ANi", 12, 1),
            ("[ANi]  社畜想被幼女幽靈療癒。（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "社畜想被幼女幽靈療癒。（僅限港澳台地區）", "ANi", 12, 1),
            ("[NC-Raws] 社畜小姐想被幽灵幼女治愈。 / Shachiku-san wa Youjo Yuurei - 12 (B-Global 3840x2160 HEVC AAC MKV)", "Shachiku-san wa Youjo Yuurei", "NC-Raws", 12, 1),
            ("[c.c動漫][4月新番][RPG不動產][12][BIG5][1080P][MP4][END]", "RPG不動產", "c.c動漫", 12, 1),
            ("[喵萌奶茶屋&LoliHouse] 舞动不止 / Dance Dance Danseur - 11 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]", "Dance Dance Danseur", "喵萌奶茶屋&LoliHouse", 11, 1),
            ("[ANi] Deaimon Recipe for Happiness -  相合之物 - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Deaimon Recipe for Happiness", "ANi", 12, 1),
            ("【幻櫻字幕組】【4月新番】【古見同學有交流障礙症 Komi-san wa, Komyushou Desu.】【24v2】【BIG5_MP4】【1920X1080】【END】", "Komi-san wa, Komyushou Desu.", "幻櫻字幕組", 24, 1),
            ("【极影字幕社】★4月新番 街角魔族 第二季 第09话 GB 1080P MP4（字幕社招人内详）", "街角魔族", "极影字幕社", 9, 2),
            ("[LoliHouse] 史上最强大魔王重生为村民A / Shijou Saikyou no Daimaou, Murabito A ni Tensei suru - 12 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]", "Shijou Saikyou no Daimaou, Murabito A ni Tensei suru", "LoliHouse", 12, 1),
            ("【极影字幕社】LoveLive! 虹咲学园学园偶像同好会 第2期 第12集 GB_CN HEVC_opus 1080p", "LoveLive! 虹咲学园学园偶像同好会", "极影字幕社", 12, 2),
            ("[ANi] RPG Real Estate -  RPG 不動產（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "RPG Real Estate", "ANi", 12, 1),
            ("[Lilith-Raws] 史上最強大魔王轉生為村民 A / Shijou Saikyou no Daimaou - 12 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Shijou Saikyou no Daimaou", "Lilith-Raws", 12, 1),
            ("[ANi]  史上最強大魔王轉生為村民 A - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "史上最強大魔王轉生為村民 A", "ANi", 12, 1),
            ("[Skymoon-Raws] 勇者、辭職不幹了 / Yuusha, Yamemasu - 12 [ViuTV][WEB-DL][1080p][AVC AAC][繁體外掛][MP4+ASS](正式版本)", "Yuusha, Yamemasu", "Skymoon-Raws", 12, 1),
            ("[c.c動漫][4月新番][勇者、辭職不幹了][12][簡繁內掛][AVC_AAC][1080P][MKV][END]", "勇者、辭職不幹了", "c.c動漫", 12, 1),
            ("[ANi] Im Quitting Heroing -  勇者、辭職不幹了 - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "Im Quitting Heroing", "ANi", 12, 1),
            ("[酷漫404][夏日重现][10][1080P][WebRip][简日双语][AVC AAC][MP4][字幕组招人内详]", "夏日重现", "酷漫404", 10, 1),
            ("[LoliHouse] 理科生坠入情网故尝试证明[r=1-sinθ ] - 12 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕][Fin]", "r=1-sin", "LoliHouse", 12, 1),
            ("[黑岩射手吧字幕组] Black Rock Shooter - Dawn Fall [12 END][1080p][简繁内挂]", "Black Rock Shooter", "黑岩射手吧字幕组", 12, 1),
            ("[ANi]  Healer Girls 歌愈少女（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "Healer Girls 歌愈少女（僅限港澳台地區）", "ANi", 12, 1),
            ("【中肯字幕組】【1月新番】【川尻小玉的懒散生活】【18】【BIG5_MP4】【1920X1080】", "川尻小玉的懒散生活", "中肯字幕組", 18, 1),
            ("【喵萌Production】★07月新番★[聯盟空軍航空魔法音樂隊 光輝魔女/Luminous Witches][01][先行版][1080p][繁體][招募翻譯]", "Luminous Witches", "喵萌Production", 1, 1),
            ("[c.c動漫][4月新番][女性向遊戲世界對路人角色很不友好][12][BIG5][1080P][MP4][END]", "女性向遊戲世界對路人角色很不友好", "c.c動漫", 12, 1),
            ("[Skymoon-Raws][One Piece 海賊王][1022][ViuTV][WEB-DL][1080p][AVC AAC][CHT][MP4+ASS](正式版本)", "One Piece 海賊王", "Skymoon-Raws", 1022, 1),
            ("[NC-Raws] 女性向遊戲世界對路人角色很不友好 / Otome Game Sekai - 12 (Baha 1920x1080 AVC AAC MP4)", "Otome Game Sekai", "NC-Raws", 12, 1),
            ("[ANi]  女性向遊戲世界對路人角色很不友好（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "女性向遊戲世界對路人角色很不友好（僅限港澳台地區）", "ANi", 12, 1),
            ("[NC-Raws] 海贼王 / One Piece - 1022 (B-Global 3840x2160 HEVC AAC MKV)", "One Piece", "NC-Raws", 1022, 1),
            ("【极影字幕社+辉夜汉化组】辉夜大小姐想让我告白 究极浪漫 第11集 GB_CN HEVC opus 1080p", "辉夜大小姐想让我告白 究极浪漫", "极影字幕社+辉夜汉化组", 11, 1),
            ("[桜都字幕組] 雀魂 PONG☆ / Jantama Pong [11][1080p][繁體內嵌]", "Jantama Pong", "桜都字幕組", 11, 1),
            ("[c.c動漫][4月新番][理科生墜入情網，故嘗試證明。r=1-sinθ][12][BIG5][1080P][MP4][END]", "理科生墜入情網，故嘗試證明。r=1-sinθ", "c.c動漫", 12, 1),
            ("【枫叶字幕组】[宠物小精灵 / 宝可梦 旅途][115][简体][1080P][MP4]", "宠物小精灵", "枫叶字幕组", 115, 1),
            ("【楓葉字幕組】[寵物小精靈 / 寶可夢 旅途][115][繁體][1080P][MP4]", "寵物小精靈", "楓葉字幕組", 115, 1),
            ("[ANi]  不會拿捏距離的阿波連同學（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "不會拿捏距離的阿波連同學（僅限港澳台地區）", "ANi", 12, 1),
            ("[ANi]  理科生墜入情網，故嘗試證明。r=1-sinθ（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "理科生墜入情網，故嘗試證明。r=1-sinθ（僅限港澳台地區）", "ANi", 12, 1),
            ("[ANi] The Executioner and Her Way of Life -  處刑少女的生存之道 - 12 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "The Executioner and Her Way of Life", "ANi", 12, 1),
            ("[NC-Raws] 理科生坠入情网，故尝试证明。第二季 / Rikei ga Koi ni Ochita S2 - 12 (B-Global 1920x1080 HEVC AAC MKV)", "Rikei ga Koi ni Ochita", "NC-Raws", 12, 2),
            ("[c.c動漫][4月新番][派對咖孔明][12][BIG5][1080P][MP4][END]", "派對咖孔明", "c.c動漫", 12, 1),
            ("【悠哈璃羽字幕社】 [夏日重现__Summer-Time-Rendering] [09] [x264 1080p][CHS]", "Summer-Time-Rendering", "悠哈璃羽字幕社", 9, 1),
            ("【熔岩动画搬运】派对浪客诸葛孔明 / 派对咖孔明 / Paripi Koumei [12 END][简体内嵌][1080P][AVC AAC][MP4]", "Paripi Koumei", "熔岩动画搬运", 12, 1),
            ("[ANi] Ya Boy Kongming -  派對咖孔明（僅限港澳台地區） - 12 [1080P][Bilibili][WEB-DL][AAC AVC][CHT CHS][MP4]", "Ya Boy Kongming", "ANi", 12, 1),
            ("[NC-Raws] 派对浪客诸葛孔明 / Paripi Koumei (Ya Boy Kongming!) - 12 (B-Global 1920x1080 HEVC AAC MKV)", "Paripi Koumei (Ya Boy Kongming!)", "NC-Raws", 12, 1),
            ("【YWCN字幕组】[妖怪手表♪Youkai Watch♪][36][GB][1920X1080][MP4]", "妖怪手表♪Youkai Watch♪", "YWCN字幕组", 36, 1),
            ("【悠哈璃羽字幕社】[小林家的龍女僕S_Kobayashi-san Chi no Maid Dragon S][13][x264 1080p][CHT]", "Kobayashi-san Chi no Maid Dragon S", "悠哈璃羽字幕社", 13, 1),
            ("[Lilith-Raws] 小書痴的下剋上：為了成為圖書管理員不擇手段！/ Honzuki no Gekokujou - 36 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]", "Honzuki no Gekokujou", "Lilith-Raws", 36, 1),
            ("[ANi]  小書痴的下剋上：為了成為圖書管理員不擇手段！第三季 - 36 [1080P][Baha][WEB-DL][AAC AVC][CHT][MP4]", "小書痴的下剋上 為了成為圖書管理員不擇手段！", "ANi", 36, 3),
            ("[桜都字幕组] 3秒后，野兽。～坐在联谊会角落的他是个肉食系 / 3 Byou Go, Yajuu. Goukon de Sumi ni Ita Kare wa Midara na Nikushoku Deshita [08][1080p][简繁内封]", "3 Byou Go, Yajuu. Goukon de Sumi ni Ita Kare wa Midara na Nikushoku Deshita", "桜都字幕组", 8, 1),
            ("[PoInSu] 间谍家家酒 & SPY×FAMILY [09] [2160P] [HEVC 10bit] [英内封]", "& SPY×FAMILY", "PoInSu", 9, 1),
            ("【熔岩动画Sub】街角魔族 2丁目 (第二季) / Machikado Mazoku 2-Choume [09][简日内嵌][1080P][AVC AAC][MP4]", "Machikado Mazoku 2-Choume", "熔岩动画Sub", 9, 2),
            ("[澄空学园&华盟字幕社] Date A Live IV 约会大作战IV 第09话 MP4 720p", "Date A Live IV 约会大作战IV", "澄空学园&华盟字幕社", 9, 1),
            ("【极影字幕社】★4月新番 小书痴的下克上 第三季 第06话 GB 1080P MP4（字幕社招人内详）", "小书痴的下克上", "极影字幕社", 6, 3),
            ("【極影字幕社】★4月新番 小書癡的下克上 第三季 第06話 BIG5 1080P MP4（字幕社招人內詳）", "小書癡的下克上", "極影字幕社", 6, 3)
        ]



        for raw, title, group, epi, season in data:
            info = Parser.parse_bangumi_name(raw)
            self.assertEqual(info.title, title)
            self.assertEqual(info.group, group)
            self.assertEqual(info.ep_info.number, epi)
            self.assertEqual(info.season_info.number, season)

    def test_title(self):
        epi = Episode()
        epi.title = "测试/测试"
        self.assertEqual(epi.title, "测试 测试")

        epi.title = "测试：测试"
        self.assertEqual(epi.title, "测试 测试")

        epi.title = "测试：/、、\测试"
        self.assertEqual(epi.title, "测试 、、 测试")

        epi.title = ":"
        self.assertEqual(epi.title, "")
