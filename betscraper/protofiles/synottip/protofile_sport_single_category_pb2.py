# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protofile_sport_single_category.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%protofile_sport_single_category.proto\"*\n\x0bSportRoot_s\x12\x1b\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\r.sport_data_s\"7\n\x0csport_data_s\x12\'\n\ndata_sport\x18\x01 \x01(\x0b\x32\x13.sport_data_sport_s\"o\n\x12sport_data_sport_s\x12\x1d\n\x05sport\x18\x01 \x01(\x0b\x32\x0e.sport_sport_s\x12\x0e\n\x06number\x18\x03 \x01(\x05\x12*\n\x08\x63\x61tegory\x18\x04 \x03(\x0b\x32\x18.sport_category_events_s\"5\n\rsport_sport_s\x12\x10\n\x08sport_id\x18\x01 \x01(\t\x12\x12\n\nsport_name\x18\x02 \x01(\t\"D\n\x17sport_category_events_s\x12)\n\x0b\x65vents_info\x18\x01 \x01(\x0b\x32\x14.sport_events_info_s\"s\n\x13sport_events_info_s\x12\x11\n\tevents_xx\x18\x01 \x01(\t\x12\x17\n\x0f\x65vents_category\x18\x02 \x01(\t\x12\x10\n\x08\x65vents_x\x18\x03 \x01(\t\x12\x1e\n\x06\x65vents\x18\x05 \x03(\x0b\x32\x0e.sport_event_s\"\xd3\x01\n\rsport_event_s\x12\x10\n\x08\x65vent_id\x18\x01 \x01(\x03\x12\x12\n\nevent_name\x18\x02 \x01(\t\x12\'\n\nevent_time\x18\x04 \x01(\x0b\x32\x13.sport_event_time_s\x12\x10\n\x08number_5\x18\x05 \x01(\t\x12)\n\x0b\x62\x65t_details\x18\x06 \x01(\x0b\x32\x14.sport_bet_details_s\x12\x10\n\x08\x65vent_xx\x18\x07 \x01(\t\x12\x11\n\tnumber_10\x18\n \x01(\x05\x12\x11\n\tnumber_12\x18\x0c \x01(\x05\"&\n\x12sport_event_time_s\x12\x10\n\x08\x64\x61tetime\x18\x01 \x01(\x03\"a\n\x13sport_bet_details_s\x12\x14\n\x0c\x62\x65t_category\x18\x01 \x01(\x05\x12\x19\n\x11\x62\x65t_category_name\x18\x02 \x01(\t\x12\x19\n\x03\x62\x65t\x18\x03 \x01(\x0b\x32\x0c.sport_bet_s\"~\n\x0bsport_bet_s\x12\x0f\n\x07\x62\x65ts_id\x18\x01 \x01(\t\x12\x11\n\tbets_name\x18\x02 \x01(\t\x12%\n\tbets_info\x18\x06 \x01(\x0b\x32\x12.sport_bets_info_s\x12\x11\n\tnumber_11\x18\x0b \x01(\x05\x12\x11\n\tnumber_12\x18\x0c \x01(\x05\"e\n\x11sport_bets_info_s\x12\x0e\n\x06\x62\x65t_id\x18\x01 \x01(\x03\x12\x10\n\x08\x62\x65t_name\x18\x02 \x01(\t\x12\x12\n\nbet_number\x18\x03 \x01(\x05\x12\x1a\n\x04odds\x18\x04 \x03(\x0b\x32\x0c.sport_odd_s\"C\n\x0bsport_odd_s\x12\x0e\n\x06odd_id\x18\x01 \x01(\t\x12\x10\n\x08odd_name\x18\x02 \x01(\t\x12\x12\n\nodd_number\x18\x03 \x01(\x02\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protofile_sport_single_category_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SPORTROOT_S._serialized_start=41
  _SPORTROOT_S._serialized_end=83
  _SPORT_DATA_S._serialized_start=85
  _SPORT_DATA_S._serialized_end=140
  _SPORT_DATA_SPORT_S._serialized_start=142
  _SPORT_DATA_SPORT_S._serialized_end=253
  _SPORT_SPORT_S._serialized_start=255
  _SPORT_SPORT_S._serialized_end=308
  _SPORT_CATEGORY_EVENTS_S._serialized_start=310
  _SPORT_CATEGORY_EVENTS_S._serialized_end=378
  _SPORT_EVENTS_INFO_S._serialized_start=380
  _SPORT_EVENTS_INFO_S._serialized_end=495
  _SPORT_EVENT_S._serialized_start=498
  _SPORT_EVENT_S._serialized_end=709
  _SPORT_EVENT_TIME_S._serialized_start=711
  _SPORT_EVENT_TIME_S._serialized_end=749
  _SPORT_BET_DETAILS_S._serialized_start=751
  _SPORT_BET_DETAILS_S._serialized_end=848
  _SPORT_BET_S._serialized_start=850
  _SPORT_BET_S._serialized_end=976
  _SPORT_BETS_INFO_S._serialized_start=978
  _SPORT_BETS_INFO_S._serialized_end=1079
  _SPORT_ODD_S._serialized_start=1081
  _SPORT_ODD_S._serialized_end=1148
# @@protoc_insertion_point(module_scope)
