NET_C_FE_NO_ROUTE 	= 0x12			#no arg
NET_C_FE_SENT_MSG	= 0x20			#:app. send       :msg uid, origin, next_hop
NET_C_FE_RCV_MSG 	= 0x21			#:next hop receive:msg uid, origin, last_hop
NET_C_FE_FWD_MSG 	= 0x22			#:fwd msg         :msg uid, origin, next_hop
NET_C_FE_DST_MSG 	= 0x23			#:base app. recv  :msg_uid, origin, last_hop 
NET_DC_REPORT 		= 0x60			#duty cycle report :uint16_t dutyCycle, uint16_t time
NET_LL_DUPLICATE 	= 0x61			#dropped duplicate packet seen in cache:dsn, source, accept
NET_LPL_SENDDONE 	= 0x62			#report duration of send duty cycle
#Filters a dict by only permitting certain keys.
NET_APP_SENT 		= 0x70			#app. send       :msg uid, origin
NET_C_DIE 			= 0x71
NET_SNOOP_RCV		= 0x72
NET_DC_REPORT		= 0x60

NET_C_FE_SEND_QUEUE_FULL = 0x11
NET_C_FE_SENDDONE_FAIL = 0x24
NET_C_FE_SENDDONE_WAITACK = 0x25
NET_C_FE_SENDDONE_FAIL_ACK_SEND = 0x26
NET_C_FE_SENDDONE_FAIL_ACK_FWD  = 0x27

#CTP beacons
NET_C_TREE_NO_ROUTE   = 0x30   #:        :no args
NET_C_TREE_NEW_PARENT = 0x31   #:        :parent_id, hopcount, metric
NET_C_TREE_ROUTE_INFO = 0x32   #:periodic:parent_id, hopcount, metric
NET_C_TREE_SENT_BEACON = 0x33
NET_C_TREE_RCV_BEACON = 0x34
