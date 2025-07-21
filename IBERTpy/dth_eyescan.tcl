open_hw_manager

current_hw_target [get_hw_targets */xilinx_tcf/Xilinx/00001ee7fd5e01]
set_property PARAM.FREQUENCY 6000000 [get_hw_targets */xilinx_tcf/Xilinx/00001ee7fd5e01]
open_hw_target

set_property PROBES.FILE {} [get_hw_devices xcku15p_0]
set_property FULL_PROBES.FILE {} [get_hw_devices xcku15p_0]
set_property PROGRAM.FILE {/home/ablaizot/dth_ibert.bit} [get_hw_devices xcku15p_0]
program_hw_devices [get_hw_devices xcku15p_0]

current_hw_device [get_hw_devices xcku15p_0]
refresh_hw_device -update_hw_probes false [lindex [get_hw_devices xcku15p_0] 0]
detect_hw_sio_links

set scans [get_hw_sio_scans]
foreach sc $scans {
    remove_hw_sio_scan $sc
}

set sweeps [get_hw_sio_sweeps]
foreach sw $sweeps {
    remove_hw_sio_sweep $sw
}
unset -nocomplain ::env(PYTHONHOME)
unset -nocomplain ::env(PYTHONPATH)

# Read slot number from file
if {[catch {set fp [open "slot_number.dat" r]} err]} {
    puts "Error: Could not open slot_number.dat: $err"
    puts "Using default slot number 0"
    set slot_number 0
} else {
    gets $fp slot_number
    close $fp
    puts "Using slot number: $slot_number"
}

set hw_target [get_hw_targets]
set links [get_hw_sio_links]
variable i
variable ln
set i 0
foreach ln $links {
    # Extract Quad and MGT info from link name
    if {[regexp {Quad_(\d+)/MGT_X\d+Y(\d+)} $ln match quad mgt]} {
        set descr "Slot${slot_number}_Quad_${quad}_MGT_X0Y${mgt}"

        set xil_newSweep [create_hw_sio_sweep -description {Sweep 0} -iteration_settings [list  [list "TXDIFFSWING" "330 mV (00110)" ] [list "TXDIFFSWING" "396 mV (01000)" ] [list "TXDIFFSWING" "460 mV (01010)" ] [list "TXDIFFSWING" "523 mV (01100)" ] [list "TXDIFFSWING" "587 mV (01110)" ] [list "TXDIFFSWING" "647 mV (10000)" ] [list "TXDIFFSWING" "707 mV (10010)" ] [list "TXDIFFSWING" "765 mV (10100)" ] [list "TXDIFFSWING" "822 mV (10110)" ] [list "TXDIFFSWING" "873 mV (11000)" ]] 2d_full_eye  [lindex [get_hw_sio_links] 0 ]]
        set_property HORIZONTAL_INCREMENT {2} [get_hw_sio_sweeps $xil_newSweep]
        set_property VERTICAL_INCREMENT {2} [get_hw_sio_sweeps $xil_newSweep]
        run_hw_sio_sweep [get_hw_sio_sweeps $xil_newSweep]
        wait_on_hw_sio_sweep [get_hw_sio_sweeps $xil_newSweep]

        set max_oa 0
        set best_scan ""
        set best_swing ""
        set scans [get_hw_sio_scans]
        foreach sc $scans {
            set oa [get_property OPEN_AREA [get_hw_sio_scans $sc]]
            set swing [get_property LINK_SETTINGS [get_hw_sio_scans $sc]]

                puts "Open Area for $sc $swing: $oa"
                if {$oa > $max_oa} {
                    set max_oa $oa
                    set best_swing $swing
                    set best_scan $sc
                    puts "New best scan found: $sc with Open Area $oa"
            }
        }
                
        # Save the best result
        set fname "${descr}_best.csv"
        write_hw_sio_scan -force $fname $best_scan
        exec /usr/bin/python3 generate_plot.py $fname
        
        puts "Best TXDIFFSWING for $descr: $best_swing"
        puts "Maximum Open Area: $max_oa"
    }
    incr i 1
}
