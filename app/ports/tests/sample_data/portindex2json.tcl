# Script for converting the metadata in the PortIndex to
# a list of JSON objects.
# Written by Joshua Root <jmr@macports.org>, 2017
# Requires: tclsh with the tcllib 'json' package.
#
# Usage:
#     tclsh portindex2json.tcl path/to/PortIndex [--info <key>=<value>]
#     tclsh portindex2json.tcl --help
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any
# warranty.
# <https://creativecommons.org/publicdomain/zero/1.0/>

package require json::write

proc tcl2json_list {tcl_list} {
    set new_tcl_list {}
    foreach element $tcl_list {
        lappend new_tcl_list [::json::write string $element]
    }
    return [::json::write array {*}$new_tcl_list]
}

proc get_maintainer_array {maintainer} {
    foreach entry $maintainer {
        set first_at [string first @ $entry]
        if {$first_at == 0} {
            # @foo = github handle 'foo'
            set maintainer_array(github) [::json::write string [string trimleft $entry @]]
        } elseif {$first_at != -1} {
            # unobfuscated email address
            set email_list [split $entry @]
            set email(name) [::json::write string [lindex $email_list 0]]
            set email(domain) [::json::write string [lindex $email_list 1]]
        } else {
            # obfuscated email address
            if {[string first : $entry] != -1} {
                set email_list [split $entry :]
                set email(name) [::json::write string [lindex $email_list 1]]
                set email(domain) [::json::write string [lindex $email_list 0]]
            } else {
                set email(name) [::json::write string $entry]
                set email(domain) [::json::write string "macports.org"]
            }
        }
    }
    if {[array exists email]} {
        set maintainer_array(email) [::json::write object {*}[array get email]]
    }
    return [array get maintainer_array]
}

proc parse_maintainers {maintainers} {
    set maintainer_subobjects {}
    foreach maintainer $maintainers {
        if {$maintainer ne "openmaintainer" && $maintainer ne "nomaintainer"} {
            lappend maintainer_subobjects [::json::write object {*}[get_maintainer_array $maintainer]]
        }
    }
    set maintainers_list [::json::write array {*}$maintainer_subobjects]
    return $maintainers_list
}

proc is_closedmaintainer {maintainers} {
    foreach maintainer $maintainers {
        if {$maintainer eq "openmaintainer" || $maintainer eq "nomaintainer"} {
            return false
        }
    }
    return true
}

proc print_usage {} {
    puts stdout ""
    puts stdout "Usage:"
    puts stdout "    /path/to/tclsh portindex2json.tcl \[--info <key>=<value>\] <path/to/PortIndex>"
    puts stdout "    /path/to/tclsh portindex2json.tcl --help"
    puts stdout ""
    puts stdout "Each '--info <key>=<value>' combinaton adds one key-value pair to the JSON output inside the parent key: \"info\""
    puts stdout "You may provide any number of '--info <key>=<value>' combinations."
    puts stdout ""
}

proc parse_options {} {
    global argc argv fd json_info
    for {set i 0} {$i < $argc} {incr i} {
        set arg [lindex $argv $i]
        switch -regex -- $arg {
            {^-.+} {
                if {$arg eq "--info"} {
                    incr i
                    set argument [split [lindex $argv $i] =]
                    if {[lindex $argument 1] eq ""} {
                        puts stderr "\nERROR: No value provided for the key: '[lindex $argument 0]'. The correct syntax is '--info <key>=<value>'.\n"
                        exit 1
                    } else {
                        set json_info([lindex $argument 0]) [::json::write string [lindex $argument 1]]
                    }
                } elseif {$arg eq "-help" || $arg eq "-h" || $arg eq "--help" } {
                    print_usage
                    exit 0
                } else {
                    puts stderr "\nERROR: '$arg' is an invalid argument (expecting '--help' or '--info').\n"
                    print_usage
                    exit 1
                }
            }
            default {
                if {[info exists fd]} {
                    puts stderr "\nERROR: No support for more than one argument for path to the PortIndex file.\n"
                    print_usage
                    exit 1
                } else {
                    if {[catch {set fd [open [lindex $argv $i] r]} fid]} {
                        puts stderr "\nERROR: Could not open file '[lindex $argv $i]'. Make sure the path to the PortIndex file is correct.\n"
                        exit 1
                    }
                }
            }
        }
    }

    if {![info exists fd]} {
        puts stderr "\nERROR: Path to the PortIndex file missing.\n"
        print_usage
        exit 1
    }
}

parse_options

chan configure $fd -encoding utf-8
while {[gets $fd line] >= 0} {
    if {[llength $line] != 2} {
        continue
    }
    set len [lindex $line 1]
    set line [read $fd $len]
    array unset portinfo
    array set portinfo $line
    array unset json_portinfo
    foreach key [array names portinfo] {
        if {$key eq "categories" || $key eq "variants" || [string match "depends_*" $key]} {
            set json_portinfo($key) [tcl2json_list $portinfo($key)]
        } elseif {$key eq "maintainers"} {
            set json_portinfo($key) [parse_maintainers $portinfo($key)]
            set json_portinfo(closedmaintainer) [is_closedmaintainer $portinfo($key)]
        } elseif {$key eq "description" || $key eq "long_description"} {
            set json_portinfo($key) [::json::write string [join $portinfo($key)]]
        } else {
            set json_portinfo($key) [::json::write string $portinfo($key)]
        }
    }
    lappend objects [::json::write object {*}[array get json_portinfo]]
}

set json_output [list]
if {[array exists json_info]} {
    lappend json_output info [::json::write object {*}[array get json_info]]
}

lappend json_output ports [::json::write array {*}$objects]

chan configure stdout -encoding utf-8
puts [::json::write object {*}$json_output]
