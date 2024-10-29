from itertools import combinations

n = 8  # プレイヤー人数
m = 3  # コート数
l = 20  # ラウンド数


def convert_big_group_to_matches(big_group):
    """
    大グループから作られる3つの試合を生成
    """
    matches = {
        frozenset([frozenset(pair1), frozenset(pair2)])
        for pair1, pair2 in combinations(combinations(big_group, 2), 2)
        if len(set(pair1).union(pair2)) == 4
    }
    return matches


def get_free_players(is_free):
    """
    空いているプレイヤーの集合を返す
    """
    free_players = {player for player, value in is_free.items() if value}
    return free_players


def filter_candidate_matches_by_free_players(candidate_matches, free_players):
    """
    プレイヤーが空いているかどうかで試合候補を絞る
    """
    big_groups = frozenset(combinations(free_players, 4))
    new_candidate_matches = {
        pair for big_group in big_groups
        for pair in convert_big_group_to_matches(big_group)
    }
    new_candidate_matches &= candidate_matches
    return new_candidate_matches


def filter_candidate_matches_by_counts(candidate_matches, mode):
    """
    カウンタ値によって試合候補を絞る
    """
    new_candidate_matches = set()
    min_match_score = None
    for match_ in candidate_matches:
        match_score = get_match_score(match_, mode=mode)
        if min_match_score is None:
            min_match_score = match_score
            new_candidate_matches.add(match_)
        else:
            if match_score == min_match_score:
                new_candidate_matches.add(match_)
            elif match_score < min_match_score:
                min_match_score = match_score
                new_candidate_matches = {match_}
    new_candidate_matches &= candidate_matches
    return new_candidate_matches


def filter_candidate_matches_by_player_counts(candidate_matches):
    new_candidate_matches = filter_candidate_matches_by_counts(
        candidate_matches, "player")
    return new_candidate_matches


def filter_candidate_matches_by_match_counts(candidate_matches):
    new_candidate_matches = filter_candidate_matches_by_counts(
        candidate_matches, "match_")
    return new_candidate_matches


def filter_candidate_matches_by_pair_counts(candidate_matches):
    new_candidate_matches = filter_candidate_matches_by_counts(
        candidate_matches, "pair")
    return new_candidate_matches


def filter_candidate_matches_by_small_group_counts(candidate_matches):
    new_candidate_matches = filter_candidate_matches_by_counts(
        candidate_matches, "small_group")
    return new_candidate_matches


def update_counts(selected_match, step):
    """
    選ばれた試合の組み合わせによってカウンタをアップデート
    """
    global match_counts, player_counts, pair_counts, small_group_counts

    pairs = {pair for pair in selected_match}
    players = {player for pair in pairs for player in pair}
    selected_small_groups = {frozenset(small_group)
                             for small_group in combinations(players, 2)}

    match_counts[selected_match] += step

    for small_group in selected_small_groups:
        small_group_counts[small_group] += step

    for pair in pairs:
        pair_counts[pair] += step

    for player in players:
        player_counts[player] += step


def update_is_free(selected_match):
    global is_free

    pairs = {pair for pair in selected_match}
    players = {player for pair in pairs for player in pair}

    for player in players:
        is_free[player] = False


def get_match_score(match_, mode):
    global match_counts, player_counts, pair_counts, small_group_counts

    update_counts(match_, 1)

    if mode == "player":
        match_score = sorted(player_counts.values(), reverse=True)
    elif mode == "match_":
        match_score = sorted(match_counts.values(), reverse=True)
    elif mode == "pair":
        match_score = sorted(pair_counts.values(), reverse=True)
    elif mode == "small_group":
        match_score = sorted(small_group_counts.values(), reverse=True)

    update_counts(match_, -1)

    return match_score


if __name__ == "__main__":
    players = set(range(1, n + 1))  # プレイヤー一覧の作成
    player_counts = {player: 0 for player in players}  # 各プレイヤーの試合出場回数のカウンタ

    small_groups = {frozenset(small_group)
                    for small_group in combinations(players, 2)}  # 2人組の作成
    small_group_counts = {
        small_group: 0 for small_group in small_groups}  # 2人組のカウンタ

    pairs = small_groups.copy()
    pair_counts = {pair: 0 for pair in pairs}  # 各ペアの組んだ回数のカウンタ

    matches = set()
    match_counts = {}  # 試合の組み合わせのカウンタ
    big_groups = {frozenset(big_group)
                  for big_group in combinations(players, 4)}  # 2人組の作成
    for big_group in big_groups:
        temp_matches = convert_big_group_to_matches(big_group)
        for match_ in temp_matches:
            match_counts[match_] = 0
            matches.add(match_)

    # 保存用ファイルの初期化
    with open(f"schedule_{n}_{m}_{l}.csv", "w") as f:
        f.write(f"{n},{m},{l}\n")

    for round in range(1, l + 1):
        is_free = {player: True for player in players}  # プレイヤーが試合に出れるか表す

        for court in range(1, m + 1):
            # 試合候補の絞り込み
            candidate_matches = matches.copy()
            free_players = get_free_players(is_free)
            candidate_matches = filter_candidate_matches_by_free_players(
                candidate_matches, free_players)
            candidate_matches = filter_candidate_matches_by_player_counts(
                candidate_matches)
            candidate_matches = filter_candidate_matches_by_match_counts(
                candidate_matches)
            candidate_matches = filter_candidate_matches_by_pair_counts(
                candidate_matches)
            candidate_matches = filter_candidate_matches_by_small_group_counts(
                candidate_matches)

            sorted_match = "試合なし"
            if candidate_matches:
                sorted_matches = sorted(
                    [sorted([sorted(pair) for pair in match_])
                     for match_ in candidate_matches]
                )
                sorted_match = sorted_matches[0]
                selected_match = frozenset(
                    frozenset(pair) for pair in sorted_match
                )
                update_counts(selected_match, 1)
                update_is_free(selected_match)

            print(f"ラウンド{round}, コート{court}, {sorted_match}")
            with open(f"schedule_{n}_{m}_{l}.csv", "a") as f:
                if sorted_match == "試合なし":
                    f.write("-,-,-,-")
                else:
                    f.write(f"{sorted_match[0][0]},{sorted_match[0][1]},{
                            sorted_match[1][0]},{sorted_match[1][1]}")
                if court != m:
                    f.write(f",")

        with open(f"schedule_{n}_{m}_{l}.csv", "a") as f:
            f.write(f"\n")

print("end")
