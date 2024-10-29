from itertools import combinations
import csv

csv1 = "schedule1.csv"  # ここを書き換える
csv2 = "schedule2.csv"  # ここを書き換える


class Score:
    def __init__(self, n, m, l, gametable, name):
        # Public
        self.name = name
        self.n = n
        self.m = m
        self.l = l
        self.gametable = gametable

        # Private
        __players = set(range(1, n + 1))
        self.__player_counts = {player: 0 for player in __players}

        __small_groups = {
            frozenset(small_group) for small_group in combinations(__players, 2)}
        self.__small_group_counts = {
            small_group: 0 for small_group in __small_groups}

        __pairs = __small_groups.copy()
        self.__pair_counts = {pair: 0 for pair in __pairs}

        self.__match_counts = {}
        __big_groups = {frozenset(big_group)
                        for big_group in combinations(__players, 4)}
        for big_group in __big_groups:
            temp_matches = self.__convert_big_group_to_matches(big_group)
            for match in temp_matches:
                self.__match_counts[match] = 0

        self.__score = {}

        # スコア計算
        for round_num, round_ in enumerate(gametable, start=1):
            for court in round_:
                self.__update_counts(court)
            round_score = self.__get_score()
            self.__score[round_num] = round_score

    def __convert_big_group_to_matches(self, big_group):
        matches = {
            frozenset([frozenset(pair1), frozenset(pair2)])
            for pair1, pair2 in combinations(combinations(big_group, 2), 2)
            if len(set(pair1).union(pair2)) == 4
        }
        return matches

    def __update_counts(self, match):
        pairs = {pair for pair in match}
        players = {player for pair in pairs for player in pair}
        small_groups = {frozenset(small_group)
                        for small_group in combinations(players, 2)}

        self.__match_counts[match] += 1

        for small_group in small_groups:
            self.__small_group_counts[small_group] += 1

        for pair in pairs:
            self.__pair_counts[pair] += 1

        for player in players:
            self.__player_counts[player] += 1

    def __get_score(self):
        match_score = (
            sorted(self.__player_counts.values(), reverse=True)
            + sorted(self.__match_counts.values(), reverse=True)
            + sorted(self.__pair_counts.values(), reverse=True)
            + sorted(self.__small_group_counts.values(), reverse=True)
        )

        return match_score

    def __getitem__(self, round_num):
        return self.__score.get(round_num, "Round not found")


def convert_csv_to_gametable(csv_path):
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        data = list(reader)

    n, m, l = map(int, data[0])

    gametable = []
    for round_data in data[1:]:
        players = list(map(int, round_data))
        round_matches = []

        for i in range(m):
            match = frozenset({
                frozenset(players[i * 4:i * 4 + 2]),
                frozenset(players[i * 4 + 2:i * 4 + 4])
            })
            round_matches.append(match)

        gametable.append(round_matches)

    return (n, m, l, gametable)


if __name__ == "__main__":
    n, m, l, gametable1 = convert_csv_to_gametable(csv1)
    n2, m2, l2, gametable2 = convert_csv_to_gametable(csv2)

    if n != n2 or m != m2 or l != l2:
        print("2つの試合表の形式が違います！")
        exit(1)

    score1 = Score(n, m, l, gametable1, csv1)
    score2 = Score(n, m, l, gametable2, csv2)

    for round_ in range(1, l + 1):
        if score1[round_] < score2[round_]:
            print(f"ラウンド{round_}: {score1.name}の方が良い試合表です")
        elif score1[round_] > score2[round_]:
            print(f"ラウンド{round_}: {score2.name}の方が良い試合表です")
        else:
            print(f"ラウンド{round_}: 同点です")
