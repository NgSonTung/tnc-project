from src.helper.converter_datetime import convert_datetime_to_timestamp


def sort_plug_date(list_plug):
    return sorted(list_plug, key=lambda obj: convert_datetime_to_timestamp(datetime_obj=obj.createdAt), reverse=True)
