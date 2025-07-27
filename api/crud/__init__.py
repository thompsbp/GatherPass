# ==============================================================================
# FILE: api/crud/__init__.py
# ==============================================================================

from .items import create_item, delete_item, get_item_by_id, get_items, update_item
from .prizes import (
    create_prize,
    delete_prize,
    get_prize_by_id,
    get_prizes,
    update_prize,
)
from .ranks import create_rank, delete_rank, get_rank_by_id, get_ranks, update_rank
from .season_items import (
    add_item_to_season,
    get_items_for_season,
    get_season_item_by_ids,
    remove_item_from_season,
    update_season_item,
)
from .season_prizes import (
    add_prize_to_season_rank,
    get_prizes_for_season_rank,
    get_season_prize_by_ids,
    remove_prize_from_season_rank,
)
from .season_ranks import (
    add_rank_to_season,
    get_ranks_for_season,
    get_season_rank_by_ids,
    remove_rank_from_season,
    update_season_rank,
)
from .season_user_ranks import award_rank_to_user, get_user_ranks_for_season
from .season_users import (
    get_all_users_for_season,
    get_user_progress_in_season,
    register_user_for_season,
)
from .seasons import (
    create_season,
    delete_season,
    get_season_by_id,
    get_seasons,
    update_season,
)
from .user_prize_awards import (
    create_user_prize_award,
    get_awards_for_user,
    get_user_prize_award_by_id,
    update_user_prize_award,
)
from .users import (
    ban_user,
    create_user,
    get_user_by_discord_id,
    get_user_by_id,
    get_user_by_uuid,
    get_users,
    update_user,
)
