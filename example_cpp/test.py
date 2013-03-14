class CCSDS_Telemetry_Header_s_time(ctypes.LittleEndianStructure):
    """"""
    _fields_ = [ ("ccsds_standard_secondary_header" ,ctypes.c_ulonglong,1),
                 ("time_stamp"                      ,ctypes.c_ulonglong,63)]

class CCSDS_Telemetry_Header_p_seq_cont(ctypes.LittleEndianStructure):
    """"""
    _fields_ = [ ("sequence_flags" ,ctypes.c_ushort,2),
                 ("packet_count"   ,ctypes.c_ushort,14)]

class CCSDS_Telemetry_Header_p_ident(ctypes.LittleEndianStructure):
    """"""
    _fields_ = [ ("packet_version_number"    ,ctypes.c_ushort,3),
                 ("packet_type"              ,ctypes.c_ushort,1),
                 ("secondary_header_present" ,ctypes.c_ushort,1),
                 ("apid"                     ,ctypes.c_ushort,11)]

class CCSDS_Telemetry_Header(ctypes.LittleEndianStructure):
    """"""
    _fields_ = [ ("p_sp_dest"  , ctypes.c_char),
                 ("p_sp_prot"  , ctypes.c_char),
                 ("p_ident"    , CCSDS_Telemetry_Header_p_ident),
                 ("p_seq_cont" , CCSDS_Telemetry_Header_p_seq_cont),
                 ("p_data_len" , ctypes.c_ushort),
                 ("s_time"     , CCSDS_Telemetry_Header_s_time)]

class KALMAN_FILTER_M(ctypes.LittleEndianStructure):
    """"""
    _fields_ = [ ("struct_inside_struct" , CCSDS_Telemetry_Header),
                 ("bits_8"               , ctypes.c_char),
                 ("ubits_8"              , ctypes.c_ubyte),
                 ("bits_16"              , ctypes.c_short),
                 ("ubits_16"             , ctypes.c_ushort),
                 ("bits_32"              , ctypes.c_int),
                 ("ubits_32"             , ctypes.c_uint),
                 ("bits_64"              , ctypes.c_longlong),
                 ("ubits_64"             , ctypes.c_ulonglong),
                 ("float_type"           , ctypes.c_float),
                 ("double_type"          , ctypes.c_double),
                 ("long_double_type"     , ctypes.c_longdouble),
                 ("struct_array"         , (CCSDS_Telemetry_Header * 2) * 5),
                 ("array_1"              , ctypes.c_double * 4),
                 ("array_2"              , (ctypes.c_double * 3) * 5)]


