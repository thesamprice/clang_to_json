#ifndef MESSAGES_H
#define MESSAGES_H
#include <stdint.h>
#include <stdint.h>

/*!
 *  @brief CCSDS Telemetry Header
 *  @TelemetryPacketHeader
 *
 */
typedef struct CCSDS_Telemetry_Header
{
    /*!
     * Primary header
     */

    /*!
     * @brief Destination address
     */
    char p_sp_dest;

    /*!
     * @brief Protocol ID
     * @default 0xf2
     */
    char p_sp_prot;
    /*!
    *@bitarray msbf
    *  @bits 3
    *    @name packet_version_number
    *    @brief Pacet Version Number
    *    @default 0
    *  @bits 1
    *    @name packet_type
    *    @brief Packet type
    *    @enum ENUM_PACKET_TYPE
    *  @bits 1
    *    @name secondary_header_present
    *    @brief Secondary Header flag
    *    @detailed The Secondary Header Flag shall indicate the presence or absence of the Packet Secondary Header within this Space Packet.
    *    It shall be 1 if a Packet Secondary Header is present; it shall be 0 if a Packet Secondary Header is not present.
    *    @enum CCSDS_Secondary_Header
    *  @bits 11
    *    @name apid
    *    @brief Application Process Identifier (APID)
    *    @detailed  via 135.0-b-1 application ID's 2040- 2047 are reserved and should not be used.
    *    The APID (possibly in conjunction with the optional APID Qualifier that
    *    identifies the naming domain for the APID) shall provide the naming mechanism for the LDP.
    */
    uint16_t p_ident;

   /*!
    *
    * @bitarray msbf
    *   @bits 2
    *     @name sequence_flags
    *     @enum CCSDS_Sequence_Flags
    *   @bits 14
    *     @name packet_count
    *     @brief  Packet Sequence Count or Packet Name
    */
    uint16_t p_seq_cont;

    /*!
     * @brief Packet data length. (Total number of octets in packet data field) -1
     * @units bytes
     */
    uint16_t p_data_len;

   /*!
    *@bitarray msbf
    *  @bits 1
    *    @name ccsds_standard_secondary_header
    *    @enum CCSDS_Standard_Secondary_header
    *  @bits 63
    *    @name time_stamp
    *    @brief It is the intent to have this data populated by C&DH to mark the S/C time at which the packet was received.
    */
    uint64_t s_time;
} CCSDS_Telemetry_Header;


/*!
 * @ingroup MESSAGES
 */
typedef struct KALMAN_FILTER_M
{
CCSDS_Telemetry_Header struct_inside_struct;
     int8_t   bits_8;
     uint8_t  ubits_8;
     int16_t   bits_16;
     uint16_t  ubits_16;
     int32_t  bits_32;
     uint32_t ubits_32;
     int64_t  bits_64;
     uint64_t ubits_64;
     float    float_type;
     double   double_type;
     long double long_double_type;

CCSDS_Telemetry_Header struct_array[2][5];
    double array_1[4];
    double array_2[3][5];

}KALMAN_FILTER_M;

int16_t blah;

#endif
