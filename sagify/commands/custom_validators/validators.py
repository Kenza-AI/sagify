import click


def validate_tags(ctx, param, value):
    """
    Validates provided tags from the command-line of the form k1=v2;k2=v2;...

    :param ctx: [click.Context], Click context (not used)
    :param param: [str], parameter value (not used)
    :param value: [str], value of parameter
    :return: [list[dict[str, str]]], tags in the AWS friendly format. Example:

        [
            {
                'Key': 'key_name_1',
                'Value': key_value_1,
            },
            {
                'Key': 'key_name_2',
                'Value': key_value_2,
            },
            ...
        ]

    """
    if value is None:
        return None

    key_value_pairs = value.strip().split(";")
    tags_dict = dict()
    for kv in key_value_pairs:
        kv_list = kv.strip().split("=")

        if len(kv_list) != 2:
            raise click.BadParameter('Malformed provided tags')

        key = kv_list[0].strip()
        value = kv_list[1].strip()

        if key in tags_dict:
            raise click.BadParameter('Duplicate key in provided tags')

        tags_dict[key] = value

    sorted_keys = list(tags_dict.keys())
    sorted_keys.sort()

    return [{'Key': k, 'Value': tags_dict[k]} for k in sorted_keys]
