open_hw_manager
connect_hw_server -url localhost:3121 -allow_non_jtag
# Read IP
open_hw_target -xvc_url $ip:2542
set hw_target [get_hw_targets]

#close_hw_target hw_target
#open_hw_target -xvc_url $ip:2542
current_hw_device [get_hw_devices debug_bridge_0]
refresh_hw_device -update_hw_probes false [lindex [get_hw_devices debug_bridge_0] 0]

set xil_newLinks [list]
set hw_target [get_hw_targets]


set xil_newLink [create_hw_sio_link -description {Link 0} [lindex [get_hw_sio_txs $hw_target/0_1_0_0/IBERT/Quad_225/MGT_X0Y8/TX] 0] [lindex [get_hw_sio_rxs $hw_target/0_1_0_0/IBERT/Quad_225/MGT_X0Y8/RX] 0] ]
lappend xil_newLinks $xil_newLink
set xil_newLink [create_hw_sio_link -description {Link 1} [lindex [get_hw_sio_txs $hw_target/0_1_0_0/IBERT/Quad_225/MGT_X0Y10/TX] 0] [lindex [get_hw_sio_rxs $hw_target/0_1_0_0/IBERT/Quad_225/MGT_X0Y10/RX] 0] ]
lappend xil_newLinks $xil_newLink
set xil_newLink [create_hw_sio_link -description {Link 2} [lindex [get_hw_sio_txs $hw_target/0_1_0_0/IBERT/Quad_225/MGT_X0Y11/TX] 0] [lindex [get_hw_sio_rxs $hw_target/0_1_0_0/IBERT/Quad_225/MGT_X0Y11/RX] 0] ]
lappend xil_newLinks $xil_newLink
set xil_newLink [create_hw_sio_link -description {Link 3} [lindex [get_hw_sio_txs $hw_target/0_1_0_0/IBERT/Quad_227/MGT_X0Y18/TX] 0] [lindex [get_hw_sio_rxs $hw_target/0_1_0_0/IBERT/Quad_227/MGT_X0Y18/RX] 0] ]
lappend xil_newLinks $xil_newLink
set xil_newLink [create_hw_sio_link -description {Link 4} [lindex [get_hw_sio_txs $hw_target/0_1_0_0/IBERT/Quad_227/MGT_X0Y19/TX] 0] [lindex [get_hw_sio_rxs $hw_target/0_1_0_0/IBERT/Quad_227/MGT_X0Y19/RX] 0] ]
lappend xil_newLinks $xil_newLink
set xil_newLinkGroup [create_hw_sio_linkgroup -description {Link Group 0} [get_hw_sio_links $xil_newLinks]]
unset xil_newLinks

set_property RX_PATTERN   {PRBS 31-bit} [get_hw_sio_rxs *MGT_X0Y*];
set_property TX_PATTERN   {PRBS 31-bit} [get_hw_sio_txs *MGT_X0Y*];

set_property LOGIC.MGT_ERRCNT_RESET_CTRL 1 [get_hw_sio_links *];
commit_hw_sio                              [get_hw_sio_links *];
set_property LOGIC.MGT_ERRCNT_RESET_CTRL 0 [get_hw_sio_links *];
commit_hw_sio                              [get_hw_sio_links *];

# Wait for BER to go below 1E-
# if there is not sleep_time variable, set it to 10 seconds
if {[info exists sleep_time] == 0} {
    set sleep_time 210
}

puts [exec date] ; exec sleep $sleep_time ; puts [exec date]

set scans [get_hw_sio_scans]
foreach sc $scans {
    remove_hw_sio_scan $sc
}
unset -nocomplain ::env(PYTHONHOME)
unset -nocomplain ::env(PYTHONPATH)

set links [get_hw_sio_links]
variable i
variable ln
set i 0
foreach ln $links {
    # Extract Quad and MGT info from link name
    if {[regexp {Quad_(\d+)/MGT_X\d+Y(\d+)} $ln match quad mgt]} {
        set descr "Quad_${quad}_MGT_X0Y${mgt}"
        set fname "${descr}.csv"
        
        set xil_newScan [create_hw_sio_scan -description $descr 2d_full_eye [lindex [get_hw_sio_links $ln] 0]]
        set_property HORIZONTAL_INCREMENT {2} [get_hw_sio_scans $xil_newScan]
        set_property VERTICAL_INCREMENT {2} [get_hw_sio_scans $xil_newScan]
        set_property DWELL_BER 1e-7 [get_hw_sio_scans $xil_newScan]
        set_property RESET_RX_AFTER_APPLYING_SETTINGS 1 [get_hw_sio_scans $xil_newScan]
        run_hw_sio_scan [get_hw_sio_scans $xil_newScan]
        wait_on_hw_sio_scan [get_hw_sio_scans $xil_newScan]
        write_hw_sio_scan -force $fname [get_hw_sio_scans $xil_newScan]
        exec /usr/bin/python3 generate_plot.py $fname
    }
    incr i 1
}

# Low speed ILA
set_property PROBES.FILE {../top.ltx} [get_hw_devices debug_bridge_0]
set_property FULL_PROBES.FILE {../top.ltx} [get_hw_devices debug_bridge_0]
refresh_hw_device [lindex [get_hw_devices debug_bridge_0] 0]
display_hw_ila_data [ get_hw_ila_data hw_ila_data_1 -of_objects [get_hw_ilas -of_objects [get_hw_devices debug_bridge_0] -filter {CELL_NAME=~"loopback_ila_i"}]]
run_hw_ila [get_hw_ilas -of_objects [get_hw_devices debug_bridge_0] -filter {CELL_NAME=~"loopback_ila_i"}]
wait_on_hw_ila [get_hw_ilas -of_objects [get_hw_devices debug_bridge_0] -filter {CELL_NAME=~"loopback_ila_i"}]
display_hw_ila_data [upload_hw_ila_data [get_hw_ilas -of_objects [get_hw_devices debug_bridge_0] -filter {CELL_NAME=~"loopback_ila_i"}]]