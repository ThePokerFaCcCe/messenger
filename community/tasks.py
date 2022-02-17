from celery import shared_task as task

from community.models import Member


@task
def create_member(community_id, user_id,
                  used_link_id=None,
                  used_guid: str = None,
                  rank=Member.RankChoices.NORMAL):
    join_data = {}
    if rank != Member.RankChoices.OWNER:
        _assert_err_fields = '`used_link_id` or `used_guid`'
        _fields = [used_link_id, used_guid]
        assert any(_fields), (
            f"You should set {_assert_err_fields}"
        )
        assert not all(_fields), (
            f"""You should set only one of 
            {_assert_err_fields} fields, not both!"""
        )

        if used_link_id:
            join_data['_used_link_id'] = used_link_id
        else:
            join_data['used_guid'] = used_guid

    Member.objects.create(
        community_id=community_id, user_id=user_id,
        rank=rank, **join_data)


@task
def delete_community_members(community_id) -> list[int]:
    mems = Member.objects.filter(community_id=community_id)
    uids = list(mems.values_list('user__id', flat=True))
    mems.delete()
    return uids
