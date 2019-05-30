# Script for converting the metadata in the PortIndex to
# a list of JSON objects.
# Written by Joshua Root <jmr@macports.org>, 2017
# Requires: tclsh with the tcllib 'json' package.
# Usage: tclsh portindex2json.tcl path/to/PortIndex

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
        if {[string first @ $entry] != -1} {
            set maintainer_array(github) [::json::write string [string trimleft $entry @]]
        } else {
            if {[string first : $entry] != -1} {
                set email_list [split $entry :]
                set email(name) [::json::write string [lindex $email_list 1]]
                set email(domain) [::json::write string [lindex $email_list 0]]
            } else {
                set email(name) [::json::write string $entry]
                set email(domain) [::json::write string "macports.org"]
            }
            set email_subobject [::json::write object {*}[array get email]]
            set maintainer_array(email) $email_subobject
        }
    }
    return [array get maintainer_array]
}

proc parse_maintainers {maintainers} {
    set maintainer_subobjects {}
    foreach maintainer $maintainers {
        if {$maintainer != "openmaintainer" && $maintainer != "nomaintainer"} {
            lappend maintainer_subobjects [::json::write object {*}[get_maintainer_array $maintainer]]
        }
    }
    set maintainers_list [::json::write array {*}$maintainer_subobjects]
    return $maintainers_list
}

proc is_closedmaintainer {maintainers} {
    foreach maintainer $maintainers {
        if {$maintainer == "openmaintainer" || $maintainer == "nomaintainer"} {
            return false
        }
    }
    return true
}

proc remove_extra_braces {text} {
    return [regsub -all {[\{\}]} $text ""]
}

set fd [open [lindex $argv 0] r]
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
        if {$key == "categories" || $key == "variants" || [string match "depends_*" $key]} {
            set json_portinfo($key) [tcl2json_list $portinfo($key)]
        } elseif {$key == "maintainers"} {
            set json_portinfo($key) [parse_maintainers $portinfo($key)]
            set json_portinfo(closedmaintainer) [is_closedmaintainer $portinfo($key)]
        } elseif {$key == "long_description"} {
            set json_portinfo($key) [::json::write string [remove_extra_braces $portinfo($key)]]
        } else {
            set json_portinfo($key) [::json::write string $portinfo($key)]
        }
    }
    lappend objects [::json::write object {*}[array get json_portinfo]]
}

chan configure stdout -encoding utf-8
puts [::json::write array {*}$objects]
